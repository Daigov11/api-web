# -*- coding: utf-8 -*-
"""Dibuja como SVG un subárbol de Figma usando su geometría (fillGeometry/strokeGeometry).

Sustituye al renderizado de la API de Figma (que tiene un cupo muy bajo en cuentas de lectura).
Cubre: vectores, elipses, rectángulos, frames con relleno/recorte, máscaras simples,
degradados lineales/radiales, opacidad y texto en curva (aproximado sobre una elipse).
"""
import html, math

_uid = [0]


def _id(p):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def _col(c, op=1.0):
    a = c.get("a", 1) * op
    r, g, b = (round(c[k] * 255) for k in "rgb")
    return "#%02x%02x%02x" % (r, g, b), round(a, 4)


def _matrix(n):
    """Transformación local->absoluta (sin traslación de la raíz) usando rotación de relativeTransform
    y la caja absoluta para la posición (robusto ante grupos)."""
    rt = n.get("relativeTransform") or [[1, 0, 0], [0, 1, 0]]
    a, c_, b, d = rt[0][0], rt[0][1], rt[1][0], rt[1][1]
    sz = n.get("size") or {}
    bb = n.get("absoluteBoundingBox") or {"x": 0, "y": 0, "width": 0, "height": 0}
    w, h = sz.get("x", bb["width"]), sz.get("y", bb["height"])
    xs = [a * x + c_ * y for x, y in ((0, 0), (w, 0), (0, h), (w, h))]
    ys = [b * x + d * y for x, y in ((0, 0), (w, 0), (0, h), (w, h))]
    tx, ty = bb["x"] - min(xs), bb["y"] - min(ys)
    return (a, b, c_, d, tx, ty), w, h


class SVG:
    def __init__(self, root):
        self.root = root
        bb = root["absoluteBoundingBox"]
        self.ox, self.oy, self.w, self.h = bb["x"], bb["y"], bb["width"], bb["height"]
        self.defs = []
        self.body = []

    def tf(self, n):
        (a, b, c, d, tx, ty), w, h = _matrix(n)
        tx -= self.ox; ty -= self.oy
        if abs(a - 1) < 1e-6 and abs(d - 1) < 1e-6 and abs(b) < 1e-6 and abs(c) < 1e-6:
            return f'transform="translate({tx:.2f} {ty:.2f})"', w, h
        return f'transform="matrix({a:.5f} {b:.5f} {c:.5f} {d:.5f} {tx:.2f} {ty:.2f})"', w, h

    def paint(self, paints, w, h):
        """Devuelve lista de (fill, opacity) para cada relleno visible (de abajo a arriba)."""
        out = []
        for p in paints or []:
            if not p.get("visible", True):
                continue
            op = p.get("opacity", 1)
            t = p["type"]
            if t == "SOLID":
                c, a = _col(p["color"], op)
                out.append((c, a))
            elif t in ("GRADIENT_LINEAR", "GRADIENT_RADIAL", "GRADIENT_DIAMOND", "GRADIENT_ANGULAR"):
                gid = _id("g")
                h0, h1, h2 = (p["gradientHandlePositions"] + [{"x": 0, "y": 0}] * 3)[:3]
                stops = "".join(
                    '<stop offset="%g" stop-color="%s" stop-opacity="%g"/>' % ((s["position"],) + _col(s["color"], op))
                    for s in p["gradientStops"])
                if t == "GRADIENT_LINEAR":
                    self.defs.append(f'<linearGradient id="{gid}" gradientUnits="userSpaceOnUse" x1="{h0["x"]*w:.2f}" y1="{h0["y"]*h:.2f}" x2="{h1["x"]*w:.2f}" y2="{h1["y"]*h:.2f}">{stops}</linearGradient>')
                else:
                    rx = math.hypot((h1["x"] - h0["x"]) * w, (h1["y"] - h0["y"]) * h)
                    ry = math.hypot((h2["x"] - h0["x"]) * w, (h2["y"] - h0["y"]) * h)
                    ang = math.degrees(math.atan2((h1["y"] - h0["y"]) * h, (h1["x"] - h0["x"]) * w))
                    sy = ry / rx if rx else 1
                    self.defs.append(f'<radialGradient id="{gid}" gradientUnits="userSpaceOnUse" cx="0" cy="0" r="{rx:.2f}" gradientTransform="translate({h0["x"]*w:.2f} {h0["y"]*h:.2f}) rotate({ang:.2f}) scale(1 {sy:.4f})">{stops}</radialGradient>')
                out.append((f"url(#{gid})", 1))
        return out

    def shape(self, n, opacity):
        t = n["type"]
        tr, w, h = self.tf(n)
        op = opacity * n.get("opacity", 1)
        parts = []
        fills = self.paint(n.get("fills"), w, h)
        strokes = self.paint(n.get("strokes"), w, h)
        geo = n.get("fillGeometry") or []
        if t == "ELLIPSE" and not n.get("arcData", {}).get("innerRadius") and \
                abs(n.get("arcData", {}).get("endingAngle", 6.2832) - n.get("arcData", {}).get("startingAngle", 0)) >= 6.28:
            for f, a in fills:
                parts.append(f'<ellipse cx="{w/2:.2f}" cy="{h/2:.2f}" rx="{w/2:.2f}" ry="{h/2:.2f}" fill="{f}"' + (f' fill-opacity="{a}"' if a < 1 else "") + "/>")
        elif t in ("RECTANGLE", "FRAME", "INSTANCE", "COMPONENT") and not geo:
            r = n.get("cornerRadius", 0) or 0
            for f, a in fills:
                parts.append(f'<rect width="{w:.2f}" height="{h:.2f}" rx="{r}" fill="{f}"' + (f' fill-opacity="{a}"' if a < 1 else "") + "/>")
        else:
            for g in geo:
                rule = "evenodd" if g.get("windingRule") == "EVENODD" else "nonzero"
                for f, a in fills:
                    parts.append(f'<path d="{g["path"]}" fill-rule="{rule}" fill="{f}"' + (f' fill-opacity="{a}"' if a < 1 else "") + "/>")
        for g in n.get("strokeGeometry") or []:
            for f, a in strokes:
                parts.append(f'<path d="{g["path"]}" fill="{f}"' + (f' fill-opacity="{a}"' if a < 1 else "") + "/>")
        if not n.get("strokeGeometry") and strokes and n.get("strokeWeight") and t in ("ELLIPSE", "RECTANGLE", "FRAME"):
            sw = n["strokeWeight"]
            dash = f' stroke-dasharray="{" ".join(str(x) for x in n["strokeDashes"])}"' if n.get("strokeDashes") else ""
            for f, a in strokes:
                if t == "ELLIPSE":
                    parts.append(f'<ellipse cx="{w/2:.2f}" cy="{h/2:.2f}" rx="{w/2:.2f}" ry="{h/2:.2f}" fill="none" stroke="{f}" stroke-width="{sw}"{dash}/>')
                else:
                    parts.append(f'<rect width="{w:.2f}" height="{h:.2f}" rx="{n.get("cornerRadius",0) or 0}" fill="none" stroke="{f}" stroke-width="{sw}"{dash}/>')
        if not parts:
            return ""
        o = f' opacity="{op:.3f}"' if op < 0.999 else ""
        return f'<g {tr}{o}>{"".join(parts)}</g>'

    def text_path(self, n, opacity):
        tr, w, h = self.tf(n)
        st = n.get("style", {})
        fills = self.paint(n.get("fills"), w, h)
        col = fills[-1][0] if fills else "#000"
        pid = _id("tp")
        vn = n.get("vectorNetwork") or {}
        V, S = vn.get("vertices") or [], vn.get("segments") or []
        start_frac = 0
        if V and S:
            d, cur = [], None
            for sg in S:
                p0, p1 = V[sg["start"]]["position"], V[sg["end"]]["position"]
                t0, t1 = sg.get("startTangent", {"x": 0, "y": 0}), sg.get("endTangent", {"x": 0, "y": 0})
                if cur != sg["start"]:
                    d.append(f'M {p0["x"]:.2f},{p0["y"]:.2f}')
                d.append(f'C {p0["x"]+t0["x"]:.2f},{p0["y"]+t0["y"]:.2f} {p1["x"]+t1["x"]:.2f},{p1["y"]+t1["y"]:.2f} {p1["x"]:.2f},{p1["y"]:.2f}')
                cur = sg["end"]
            sd = n.get("textPathStartData") or {}
            start_frac = (sd.get("segment", 0) + sd.get("position", 0)) / len(S)
            self.defs.append(f'<path id="{pid}" d="{" ".join(d)}"/>')
        else:
            rx, ry = w / 2, h / 2
            self.defs.append(f'<path id="{pid}" d="M {rx:.2f},0 A {rx:.2f},{ry:.2f} 0 1,1 {rx-0.01:.2f},0 Z"/>')
        fs = st.get("fontSize", 14)
        ls = st.get("letterSpacing", 0)
        txt = html.escape(n.get("characters", ""))
        tc = st.get("textCase")
        if tc == "UPPER":
            txt = txt.upper()
        return (f'<g {tr}><text font-family="Inter,system-ui,sans-serif" font-size="{fs}" font-weight="{st.get("fontWeight",400)}" '
                f'letter-spacing="{ls}" fill="{col}"><textPath href="#{pid}" startOffset="{start_frac*100:.3f}%">{txt}</textPath></text></g>')

    def walk(self, n, opacity=1.0):
        if not n.get("visible", True):
            return ""
        t = n["type"]
        if t == "TEXT_PATH":
            return self.text_path(n, opacity)
        if t == "TEXT":
            return ""
        out = []
        kids = [c for c in n.get("children", []) if c.get("visible", True)]
        if n is not self.root or t not in ("GROUP",):
            if t not in ("GROUP", "BOOLEAN_OPERATION") or t == "BOOLEAN_OPERATION":
                out.append(self.shape(n, opacity))
        if t == "BOOLEAN_OPERATION":
            return "".join(out)          # la geometría booleana ya está resuelta
        child_op = opacity * (n.get("opacity", 1) if t in ("GROUP", "FRAME", "INSTANCE", "COMPONENT", "SECTION") else 1)
        inner = []
        mask_id = None
        for c in kids:
            if c.get("isMask"):
                mask_id = _id("m")
                self.defs.append(f'<clipPath id="{mask_id}">{self.shape(dict(c, fills=[{"type":"SOLID","color":{"r":0,"g":0,"b":0,"a":1}}], strokes=[]), 1)}</clipPath>')
                continue
            s = self.walk(c, child_op)
            if s:
                inner.append(f'<g clip-path="url(#{mask_id})">{s}</g>' if mask_id else s)
        body = "".join(inner)
        if body and n.get("clipsContent") and t in ("FRAME", "INSTANCE", "COMPONENT") and n is not self.root:
            cid = _id("c")
            tr, w, h = self.tf(n)
            self.defs.append(f'<clipPath id="{cid}"><rect {tr} width="{w:.2f}" height="{h:.2f}" rx="{n.get("cornerRadius",0) or 0}"/></clipPath>')
            body = f'<g clip-path="url(#{cid})">{body}</g>'
        out.append(body)
        return "".join(out)

    def render(self):
        # la raíz se dibuja como cualquier nodo (sus rellenos), salvo opacidad que va en el contenedor HTML
        body = self.walk(self.root, 1.0)
        defs = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg width="{self.w:.2f}" height="{self.h:.2f}" viewBox="0 0 {self.w:.2f} {self.h:.2f}" fill="none" '
                f'xmlns="http://www.w3.org/2000/svg">{defs}{body}</svg>')


def render(node):
    return SVG(node).render()
