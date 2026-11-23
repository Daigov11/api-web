# -*- coding: utf-8 -*-
"""Convierte un frame de Figma (JSON de la API) en HTML con estilos en línea.

Reglas:
- Frames con diseño automático -> flexbox (gap, padding, alineación, tamaños FIXED/HUG/FILL).
- Frames sin diseño automático y grupos -> hijos con posición absoluta.
- Vectores, texto en curva, nodos rotados, máscaras y grupos solo-decorativos -> imagen
  renderizada por Figma (SVG en línea si es pequeño; PNG @2x subido a S3 si no).
- Rellenos de imagen -> imagen original subida a S3.
El resultado se escala con `zoom` desde JS (diseño fijo de 1440 / 390 px).
"""
import html, math, re

VECTORISH = {"VECTOR", "BOOLEAN_OPERATION", "STAR", "LINE", "REGULAR_POLYGON", "TEXT_PATH"}
CONTAINERS = {"FRAME", "GROUP", "INSTANCE", "COMPONENT", "COMPONENT_SET", "SECTION"}


def px(v):
    v = round(float(v), 2)
    return ("%g" % v) + "px"


def rgba(c, op=1.0):
    a = round(c.get("a", 1) * op, 3)
    r, g, b = (round(c[k] * 255) for k in "rgb")
    if a >= 1:
        return "#%02x%02x%02x" % (r, g, b)
    return "rgba(%d,%d,%d,%g)" % (r, g, b, a)


def esc(s):
    return html.escape(s, quote=True)


class Converter:
    def __init__(self, image_fill_url, render_req, can_png=lambda n: False):
        """image_fill_url(ref)->url ; render_req(node, kind)->placeholder url (kind: svg|png)."""
        self.image_fill_url = image_fill_url
        self.render_req = render_req
        self.can_png = can_png
        self.hooks = {}          # id figma -> atributos extra (data-*, id)
        self.skip = set()        # ids a omitir
        self.replace = {}        # id figma -> html que sustituye al nodo (con mismo posicionamiento)
        self.inline_svg = {}     # se llena luego

    # ---------- utilidades de análisis ----------
    def visible(self, n):
        return n.get("visible", True) and n["id"] not in self.skip

    def has_text(self, n):
        if n["type"] == "TEXT":
            return True
        return any(self.has_text(c) for c in n.get("children", []) if self.visible(c))

    def has_hook(self, n):
        if n["id"] in self.hooks or n["id"] in self.replace:
            return True
        return any(self.has_hook(c) for c in n.get("children", []) if self.visible(c))

    def has_vectorish(self, n):
        if n["type"] in VECTORISH or n.get("isMask"):
            return True
        return any(self.has_vectorish(c) for c in n.get("children", []) if self.visible(c))

    def has_image(self, n):
        if any(f.get("type") == "IMAGE" and f.get("visible", True) for f in n.get("fills", []) or []):
            return True
        return any(self.has_image(c) for c in n.get("children", []) if self.visible(c))

    def rotated(self, n):
        if abs(n.get("rotation") or 0) > 1e-3:
            return True
        rt = n.get("relativeTransform")
        if not rt:
            return False
        return abs(rt[0][1]) > 1e-3 or abs(rt[1][0]) > 1e-3 or rt[0][0] < 0 or rt[1][1] < 0

    def count(self, n):
        return 1 + sum(self.count(c) for c in n.get("children", []))

    def should_raster(self, n):
        t = n["type"]
        if n["id"] in self.hooks or n["id"] in self.replace:
            return False
        # con fotos dentro solo se rasteriza si ya existe un render PNG de Figma; si no, se convierte en HTML
        if self.has_image(n) and not self.can_png(n):
            return False
        if t in VECTORISH:
            return True
        if self.rotated(n) and t != "TEXT":
            return True
        if t == "ELLIPSE" and n.get("arcData") and abs(n["arcData"].get("endingAngle", 6.283) - n["arcData"].get("startingAngle", 0)) < 6.28:
            return True
        if t in CONTAINERS and not self.has_text(n) and not self.has_hook(n):
            kids = [c for c in n.get("children", []) if self.visible(c)]
            if kids and (self.has_vectorish(n) or self.count(n) > 12 or any(c.get("isMask") for c in kids)):
                return True
        if any(f.get("type") == "IMAGE" and f.get("scaleMode") == "CROP" for f in n.get("fills", []) or []) and not n.get("children"):
            return True
        return False

    # ---------- estilos ----------
    def fills_css(self, n, st):
        layers = []
        for f in reversed([f for f in (n.get("fills") or []) if f.get("visible", True)]):
            op = f.get("opacity", 1)
            t = f["type"]
            if t == "SOLID":
                c = rgba(f["color"], op)
                layers.append(f"linear-gradient({c},{c})")
            elif t == "GRADIENT_LINEAR":
                layers.append(self.linear(f, n))
            elif t in ("GRADIENT_RADIAL", "GRADIENT_DIAMOND"):
                layers.append(self.radial(f, n))
            elif t == "GRADIENT_ANGULAR":
                stops = ",".join(f"{rgba(s['color'], op)} {round(s['position']*360,1)}deg" for s in f["gradientStops"])
                layers.append(f"conic-gradient({stops})")
            elif t == "IMAGE":
                url = self.image_fill_url(f.get("imageRef"))
                if not url:
                    continue
                mode = f.get("scaleMode", "FILL")
                if mode == "FIT":
                    layers.append(f"url({url}) center/contain no-repeat")
                elif mode == "TILE":
                    layers.append(f"url({url}) 0 0/{round(f.get('scalingFactor',1)*100)}% repeat")
                else:
                    layers.append(f"url({url}) center/cover no-repeat")
        if not layers:
            return
        # color sólido único -> background-color (más limpio)
        solids = [f for f in (n.get("fills") or []) if f.get("visible", True)]
        if len(solids) == 1 and solids[0]["type"] == "SOLID":
            st["background-color"] = rgba(solids[0]["color"], solids[0].get("opacity", 1))
        else:
            st["background"] = ",".join(layers)

    def linear(self, f, n):
        w, h = n["size"]["x"] if "size" in n else 1, n["size"]["y"] if "size" in n else 1
        p0, p1 = f["gradientHandlePositions"][0], f["gradientHandlePositions"][1]
        dx, dy = (p1["x"] - p0["x"]) * w, (p1["y"] - p0["y"]) * h
        ang = math.degrees(math.atan2(dx, -dy))
        # longitud del gradiente CSS para ese ángulo
        a = math.radians(ang)
        L = abs(w * math.sin(a)) + abs(h * math.cos(a))
        glen = math.hypot(dx, dy) or 1
        # proyección del punto inicial respecto al inicio CSS
        cx, cy = w / 2, h / 2
        ux, uy = math.sin(a), -math.cos(a)
        start_css = (cx - ux * L / 2, cy - uy * L / 2)
        off = ((p0["x"] * w - start_css[0]) * ux + (p0["y"] * h - start_css[1]) * uy)
        op = f.get("opacity", 1)
        stops = []
        for s in f["gradientStops"]:
            pos = (off + s["position"] * glen) / (L or 1) * 100
            stops.append(f"{rgba(s['color'], op)} {round(pos, 2)}%")
        return f"linear-gradient({round(ang, 2)}deg,{','.join(stops)})"

    def radial(self, f, n):
        w, h = n["size"]["x"], n["size"]["y"]
        p0, p1, p2 = f["gradientHandlePositions"][:3]
        rx = math.hypot((p1["x"] - p0["x"]) * w, (p1["y"] - p0["y"]) * h)
        ry = math.hypot((p2["x"] - p0["x"]) * w, (p2["y"] - p0["y"]) * h)
        op = f.get("opacity", 1)
        stops = ",".join(f"{rgba(s['color'], op)} {round(s['position']*100, 2)}%" for s in f["gradientStops"])
        return f"radial-gradient({px(rx)} {px(ry)} at {round(p0['x']*100,2)}% {round(p0['y']*100,2)}%,{stops})"

    def strokes_css(self, n, st):
        strokes = [s for s in (n.get("strokes") or []) if s.get("visible", True) and s["type"] == "SOLID"]
        if not strokes:
            return
        c = rgba(strokes[-1]["color"], strokes[-1].get("opacity", 1))
        style = "dashed" if n.get("strokeDashes") else "solid"
        isw = n.get("individualStrokeWeights")
        align = n.get("strokeAlign", "INSIDE")
        if isw:
            for side in ("top", "right", "bottom", "left"):
                wv = isw.get(side, 0)
                if wv:
                    st[f"border-{side}"] = f"{px(wv)} {style} {c}"
            return
        w = n.get("strokeWeight", 1)
        if not w:
            return
        if align == "INSIDE" or n["type"] == "TEXT":
            st["border"] = f"{px(w)} {style} {c}"
        elif align == "OUTSIDE":
            st["outline"] = f"{px(w)} {style} {c}"
        else:
            st["outline"] = f"{px(w)} {style} {c}"
            st["outline-offset"] = px(-w / 2)

    def effects_css(self, n, st, is_text=False):
        shadows, inner, filt = [], [], []
        has_fill = any(f.get("visible", True) for f in (n.get("fills") or []))
        for e in n.get("effects") or []:
            if not e.get("visible", True):
                continue
            t = e["type"]
            if t in ("DROP_SHADOW", "INNER_SHADOW"):
                o = e.get("offset", {"x": 0, "y": 0})
                c = rgba(e["color"])
                if t == "INNER_SHADOW":
                    inner.append(f"inset {px(o['x'])} {px(o['y'])} {px(e['radius'])} {px(e.get('spread',0))} {c}")
                elif is_text:
                    shadows.append(f"{px(o['x'])} {px(o['y'])} {px(e['radius'])} {c}")
                elif has_fill or n.get("strokes"):
                    shadows.append(f"{px(o['x'])} {px(o['y'])} {px(e['radius'])} {px(e.get('spread',0))} {c}")
                else:
                    filt.append(f"drop-shadow({px(o['x'])} {px(o['y'])} {px(e['radius']/2)} {c})")
            elif t == "LAYER_BLUR":
                filt.append(f"blur({px(e['radius']/2)})")
            elif t == "BACKGROUND_BLUR":
                st["backdrop-filter"] = st["-webkit-backdrop-filter"] = f"blur({px(e['radius']/2)})"
        if is_text and shadows:
            st["text-shadow"] = ",".join(shadows)
        elif shadows or inner:
            st["box-shadow"] = ",".join(shadows + inner)
        if filt:
            st["filter"] = " ".join(filt)

    def radius_css(self, n, st):
        if n["type"] == "ELLIPSE":
            st["border-radius"] = "50%"
            return
        rr = n.get("rectangleCornerRadii")
        if rr and any(rr):
            st["border-radius"] = " ".join(px(v) for v in rr)
        elif n.get("cornerRadius"):
            st["border-radius"] = px(n["cornerRadius"])

    def common_css(self, n, st):
        if n.get("opacity", 1) < 1:
            st["opacity"] = round(n["opacity"], 3)
        bm = n.get("blendMode", "PASS_THROUGH")
        if bm not in ("PASS_THROUGH", "NORMAL"):
            st["mix-blend-mode"] = bm.lower().replace("_", "-").replace("linear-burn", "color-burn").replace("linear-dodge", "color-dodge")

    # ---------- posición y tamaño ----------
    def place(self, n, parent, st):
        bb = n.get("absoluteBoundingBox") or {"x": 0, "y": 0, "width": 0, "height": 0}
        if parent is None:
            st["position"] = "relative"
            st["width"] = px(bb["width"])
            st["min-height"] = px(bb["height"])
            return
        playout = parent.get("layoutMode") if parent["type"] != "GROUP" else None
        if playout in ("HORIZONTAL", "VERTICAL") and n.get("layoutPositioning") != "ABSOLUTE":
            st["position"] = "relative"
            sh = n.get("layoutSizingHorizontal") or ("FILL" if (playout == "VERTICAL" and n.get("layoutAlign") == "STRETCH") or (playout == "HORIZONTAL" and n.get("layoutGrow")) else "FIXED")
            sv = n.get("layoutSizingVertical") or ("FILL" if (playout == "HORIZONTAL" and n.get("layoutAlign") == "STRETCH") or (playout == "VERTICAL" and n.get("layoutGrow")) else "FIXED")
            W, H = n.get("size", {}).get("x", bb["width"]), n.get("size", {}).get("y", bb["height"])
            for axis, mode, val in (("width", sh, W), ("height", sv, H)):
                primary = (axis == "width") == (playout == "HORIZONTAL")
                if mode == "FIXED":
                    st[axis] = px(val)
                    if primary:
                        st["flex-shrink"] = 0
                elif mode == "FILL":
                    if primary:
                        st["flex"] = "1 1 0"
                        st["min-" + axis] = "0"
                    else:
                        st["align-self"] = "stretch"
            for k, css in (("minWidth", "min-width"), ("maxWidth", "max-width"), ("minHeight", "min-height"), ("maxHeight", "max-height")):
                if n.get(k) is not None:
                    st[css] = px(n[k])
            if n["type"] == "TEXT" and sh == "HUG":
                st["white-space"] = "pre"
        else:
            pbb = parent.get("absoluteBoundingBox")
            st["position"] = "absolute"
            st["left"] = px(bb["x"] - pbb["x"])
            st["top"] = px(bb["y"] - pbb["y"])
            st["width"] = px(bb["width"])
            st["height"] = px(bb["height"])

    def layout_css(self, n, st):
        lm = n.get("layoutMode")
        if lm not in ("HORIZONTAL", "VERTICAL") or n["type"] == "GROUP":
            return
        st["display"] = "flex"
        st["flex-direction"] = "row" if lm == "HORIZONTAL" else "column"
        pa = n.get("primaryAxisAlignItems", "MIN")
        ca = n.get("counterAxisAlignItems", "MIN")
        jm = {"MIN": "flex-start", "CENTER": "center", "MAX": "flex-end", "SPACE_BETWEEN": "space-between"}
        am = {"MIN": "flex-start", "CENTER": "center", "MAX": "flex-end", "BASELINE": "baseline"}
        if pa != "MIN":
            st["justify-content"] = jm.get(pa, "flex-start")
        st["align-items"] = am.get(ca, "flex-start")
        if n.get("itemSpacing") and pa != "SPACE_BETWEEN":
            st["gap"] = px(n["itemSpacing"])
        if n.get("layoutWrap") == "WRAP":
            st["flex-wrap"] = "wrap"
            if n.get("counterAxisSpacing"):
                st["row-gap" if lm == "HORIZONTAL" else "column-gap"] = px(n["counterAxisSpacing"])
                st["column-gap" if lm == "HORIZONTAL" else "row-gap"] = px(n.get("itemSpacing", 0))
                st.pop("gap", None)
        pad = [n.get("paddingTop", 0), n.get("paddingRight", 0), n.get("paddingBottom", 0), n.get("paddingLeft", 0)]
        if any(pad):
            st["padding"] = " ".join(px(p) for p in pad)

    # ---------- texto ----------
    def text_style(self, s, fills):
        st = {}
        if s.get("fontFamily"):
            st["font-family"] = f"{s['fontFamily']},system-ui,sans-serif"
        if s.get("fontWeight"):
            st["font-weight"] = int(s["fontWeight"])
        if s.get("fontSize"):
            st["font-size"] = px(s["fontSize"])
        if s.get("italic"):
            st["font-style"] = "italic"
        lu = s.get("lineHeightUnit")
        if lu == "PIXELS" and s.get("lineHeightPx"):
            st["line-height"] = px(s["lineHeightPx"])
        elif lu == "FONT_SIZE_%" and s.get("lineHeightPercentFontSize"):
            st["line-height"] = round(s["lineHeightPercentFontSize"] / 100, 4)
        elif lu == "INTRINSIC_%":
            st["line-height"] = "normal"
        if s.get("letterSpacing"):
            st["letter-spacing"] = px(s["letterSpacing"])
        tc = s.get("textCase")
        if tc:
            st["text-transform"] = {"UPPER": "uppercase", "LOWER": "lowercase", "TITLE": "capitalize"}.get(tc, "none")
            if tc in ("SMALL_CAPS", "SMALL_CAPS_FORCED"):
                st["font-variant"] = "small-caps"
        td = s.get("textDecoration")
        if td:
            st["text-decoration"] = {"UNDERLINE": "underline", "STRIKETHROUGH": "line-through"}.get(td, "none")
        if fills is not None:
            vis = [f for f in fills if f.get("visible", True)]
            if vis and vis[-1]["type"] == "SOLID":
                st["color"] = rgba(vis[-1]["color"], vis[-1].get("opacity", 1))
        return st

    def text_html(self, n, st):
        s = n.get("style", {})
        st.update(self.text_style(s, n.get("fills")))
        ta = s.get("textAlignHorizontal", "LEFT")
        if ta != "LEFT":
            st["text-align"] = {"CENTER": "center", "RIGHT": "right", "JUSTIFIED": "justify"}[ta]
        st.setdefault("white-space", "pre-wrap")
        if s.get("textAutoResize") == "WIDTH_AND_HEIGHT":
            st["white-space"] = "pre"
            st.pop("width", None)
        elif s.get("textAutoResize") == "HEIGHT":
            st.pop("height", None)
        va = s.get("textAlignVertical", "TOP")
        if va != "TOP" and "height" in st:
            st["display"] = "flex"; st["flex-direction"] = "column"
            st["justify-content"] = "center" if va == "CENTER" else "flex-end"
        if n.get("style", {}).get("maxLines"):
            st["display"] = "-webkit-box"; st["-webkit-line-clamp"] = n["style"]["maxLines"]
            st["-webkit-box-orient"] = "vertical"; st["overflow"] = "hidden"
        chars = n.get("characters", "")
        ov = n.get("characterStyleOverrides") or []
        table = n.get("styleOverrideTable") or {}
        if not ov:
            body = esc(chars)
        else:
            runs, cur, buf = [], None, ""
            for i, ch in enumerate(chars):
                k = ov[i] if i < len(ov) else 0
                if k != cur and buf:
                    runs.append((cur, buf)); buf = ""
                cur = k; buf += ch
            if buf:
                runs.append((cur, buf))
            parts = []
            for k, txt in runs:
                o = table.get(str(k)) if k else None
                if not o:
                    parts.append(esc(txt)); continue
                sst = self.text_style(o, o.get("fills"))
                link = o.get("hyperlink", {}).get("url") if o.get("hyperlink") else None
                tag = "a" if link else "span"
                attr = f' href="{esc(link)}" target="_blank" rel="noopener"' if link else ""
                parts.append(f'<{tag}{attr} style="{self.css(sst)}">{esc(txt)}</{tag}>')
            body = "".join(parts)
        if st.get("display") == "flex":
            body = f"<span>{body}</span>"
        return body

    # ---------- salida ----------
    @staticmethod
    def css(st):
        return ";".join(f"{k}:{v}" for k, v in st.items())

    def attrs(self, n):
        h = self.hooks.get(n["id"], {})
        return "".join(f' {k}="{esc(str(v))}"' for k, v in h.items())

    def convert(self, n, parent=None):
        if not self.visible(n):
            return ""
        st = {}
        self.place(n, parent, st)
        if n["id"] in self.replace:
            return self.replace[n["id"]](n, st)
        t = n["type"]
        if self.should_raster(n):
            has_img = self.has_image(n)
            kind = "png" if has_img else "svg"
            url = self.render_req(n, kind)
            st["display"] = "block"
            img_st = {"display": "block", "width": "100%", "height": "100%", "pointer-events": "none"}
            return f'<div{self.attrs(n)} style="{self.css(st)}"><img src="{url}" alt="" style="{self.css(img_st)}" loading="lazy" decoding="async"></div>'
        if t == "TEXT":
            self.common_css(n, st)
            self.effects_css(n, st, is_text=True)
            body = self.text_html(n, st)
            return f'<div{self.attrs(n)} style="{self.css(st)}">{body}</div>'
        # caja (frame, grupo, rectángulo, elipse)
        self.layout_css(n, st)
        if t != "GROUP":
            self.fills_css(n, st)
            self.strokes_css(n, st)
            self.radius_css(n, st)
        self.effects_css(n, st)
        self.common_css(n, st)
        if n.get("clipsContent") and t != "GROUP":
            st["overflow"] = "hidden"
        kids = "".join(self.convert(c, n) for c in n.get("children", []))
        return f'<div{self.attrs(n)} style="{self.css(st)}">{kids}</div>'
