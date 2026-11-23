# -*- coding: utf-8 -*-
"""Convierte frames de Figma en fragmentos HTML con recursos alojados en S3 de Apiworking."""
import re, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import figapi
import svgrender
from fig2html import Converter

INLINE_SVG_MAX = 60_000
_svg_n = [0]


def _uniq_svg(svg):
    _svg_n[0] += 1
    p = f"s{_svg_n[0]}_"
    ids = set(re.findall(r'id="([^"]+)"', svg))
    for i in sorted(ids, key=len, reverse=True):
        svg = svg.replace(f'id="{i}"', f'id="{p}{i}"').replace(f'url(#{i})', f'url(#{p}{i})').replace(f'href="#{i}"', f'href="#{p}{i}"')
    svg = re.sub(r'<\?xml[^>]*>\s*', '', svg)
    return svg


def build(root, assets, setup=None, figma_svg_cache=False):
    """root: nodo Figma. setup(conv): permite registrar hooks/replace. Devuelve html."""
    fills = None
    req = {}

    def fill_url(ref):
        nonlocal fills
        if not ref:
            return None
        key = "fill:" + ref
        if key not in assets.map:
            if fills is None:
                fills = figapi.image_fill_urls()
            if ref not in fills:
                return None
            data = figapi.download(fills[ref])
            ext = "jpg" if data[:3] == b"\xff\xd8\xff" else "png"
            assets.upload_bytes(key, data, ext)
        return assets.map[key]

    meta = {}
    meta_nodes = {}

    def render_req(n, kind):
        meta_nodes[n["id"]] = n
        req[n["id"]] = kind
        meta[n["id"]] = (n.get("absoluteBoundingBox"), n.get("absoluteRenderBounds"))
        return f"@@R:{n['id']}|{kind}@@"

    conv = Converter(fill_url, render_req, can_png=lambda n: f"png:{n['id']}" in assets.map)
    if setup:
        setup(conv)
    out = conv.convert(root)

    # --- resolver renders: SVG propio desde la geometría (o el SVG de Figma si ya está en caché) ---
    svg_cache_dir = os.path.join(figapi.CACHE, "svg")
    os.makedirs(svg_cache_dir, exist_ok=True)
    inline = {}
    nodes_by_id = meta_nodes
    for i, k in req.items():
        if k != "svg":
            continue
        path = os.path.join(svg_cache_dir, re.sub(r"[^\w-]", "_", i) + ".svg")
        if figma_svg_cache and os.path.exists(path):
            inline[i] = open(path, encoding="utf-8").read()
        else:
            inline[i] = svgrender.render(nodes_by_id[i])
    png_ids = [i for i, k in req.items() if k == "png" and f"png:{i}" not in assets.map]
    assert not png_ids, f"faltan renders PNG: {png_ids[:5]}"
    for i, k in req.items():                       # dimensiones de PNG ya subidos (sin volver a renderizar)
        if i not in inline and f"png:{i}" in assets.map and f"dim:{i}" not in assets.map:
            data = figapi.download(assets.map[f"png:{i}"])
            if data[:4] == b"\x89PNG":
                assets.map[f"dim:{i}"] = [int.from_bytes(data[16:20], "big") / 2, int.from_bytes(data[20:24], "big") / 2]

    def place(i, w, h, style):
        bb, rb = meta[i]
        if not bb or (abs(w - bb["width"]) < 2 and abs(h - bb["height"]) < 2):
            return style
        if rb and abs(w - rb["width"]) < 2 and abs(h - rb["height"]) < 2:
            x, y = rb["x"] - bb["x"], rb["y"] - bb["y"]
        else:
            x, y = (bb["width"] - w) / 2, (bb["height"] - h) / 2
        return f"position:absolute;left:{x:.2f}px;top:{y:.2f}px;width:{w:.2f}px;height:{h:.2f}px;max-width:none;pointer-events:none"

    def sub(m):
        i, kind, style = m.group(1), m.group(2), m.group(3)
        if i in inline:
            mw = re.search(r'<svg[^>]*\bwidth="([\d.]+)"[^>]*\bheight="([\d.]+)"', inline[i])
            if mw:
                style = place(i, float(mw.group(1)), float(mw.group(2)), style)
            svg = _uniq_svg(inline[i])
            return re.sub(r"<svg\b", f'<svg aria-hidden="true" style="{style}"', svg, count=1)
        url = assets.map.get(f"png:{i}", "")
        dims = assets.map.get(f"dim:{i}")
        if dims:
            bb = meta[i][0]
            # el PNG pudo reducirse al optimizar: se compara por proporción y se escala al ancho de la caja
            if bb and dims[0] and abs(dims[0] / dims[1] - bb["width"] / max(bb["height"], .01)) > .02:
                k = max(dims[0] / bb["width"], dims[1] / bb["height"]) if dims[0] > bb["width"] * 1.02 or dims[1] > bb["height"] * 1.02 else 1
                style = place(i, dims[0] / k if k > 1.5 else dims[0], dims[1] / k if k > 1.5 else dims[1], style)
        return f'<img src="{url}" alt="" style="{style}" loading="lazy" decoding="async">'
    out = re.sub(r'<img src="@@R:([^|"]+)\|(svg|png)@@" alt="" style="([^"]*)"[^>]*>', sub, out)
    assert "@@R:" not in out, "quedaron recursos sin resolver"
    return out
