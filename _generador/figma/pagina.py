# -*- coding: utf-8 -*-
"""Arma una página completa (un solo HTML) a partir de los frames de Figma:
frame de escritorio + frame móvil + capas superpuestas + variantes, con el motor de interacciones,
la capa de la guía (formulario.html) y el formulario conectado al endpoint de Apiworking.
"""
import html, json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.dirname(HERE))
import figapi, build_fig
from fig2html import Converter, px

esc = lambda s: html.escape(s, quote=True)

FORM_ENDPOINT = "https://api-centralizador.apiworking.pe/api/Administrativo/sendFormContact"
FORM_DEST = ["danielaapiworking@gmail.com", "alo.midocto@gmail.com", "rexlobo45699@gmail.com", "josephchamorrotv@gmail.com"]
FIELD_KEYS = {"nombre": "nombre", "whatsapp": "whatsapp", "negocio": "negocio", "locales": "locales",
              "especialidad": "especialidad", "necesidad": "necesidad"}
# Textos del diseño que decían que el formulario no envía datos (ahora sí envía)
TEXT_FIX = {
    "Formulario de demostración. Los campos muestran ejemplos y aún no capturan datos.": "Déjanos tus datos y un asesor te contactará por WhatsApp.",
    "Vista de demostración. El envío se conectará al canal comercial.": "Al enviar, un asesor de Apiworking te contactará por WhatsApp.",
    "Vista demostrativa: el formulario aún no guarda ni envía datos.": "Al enviar, un asesor de Apiworking te contactará por WhatsApp.",
    "Vista de demostración: los campos muestran ejemplos. No guarda ni envía información; el canal comercial está pendiente de conexión.": "Al enviar, un asesor de Apiworking te contactará por WhatsApp para coordinar tu demo.",
    "Revisa tus datos y prioridades con el equipo comercial. Esta vista es demostrativa: no se ha enviado una solicitud ni reservado una cita.": "Recibimos tu consulta. Un asesor de Apiworking te escribirá por WhatsApp para coordinar tu demo.",
    "Revisa tus datos y prioridades con el equipo comercial. Esta vista no guarda ni envía información.": "Revisa tus datos antes de enviar.",
}


# Botones que disparaban animaciones: ahora son automáticas y el botón se oculta (conserva su espacio)
AUTO_BUTTONS = {"Control de movimiento de cabecera", "Ver crecer", "Ver entrada escalonada", "Ver giro"}


# Botones y etiquetas de movimiento: se ocultan (pedido del usuario, 2026-11-23)
MOTION_BUTTONS = {"Sin movimiento", "Activar movimiento", "Reproducir"}
MOTION_LABELS = {"VISTA SIN MOVIMIENTO", "ENTRADA ESCALONADA · MOVIMIENTO BREVE"}


def n_is_button(node):
    """Solo los botones visibles de movimiento alternan la animación (no los temporizadores ni variantes)."""
    return node["name"] in ("Sin movimiento", "Cambiar movimiento") or "movimiento" in node["name"].lower()


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


class Page:
    def __init__(self, routes, frame_route, rubro_name):
        self.routes = routes                  # nombre de frame (sin sufijo) -> URL
        self.frame_route = frame_route        # función nombre_frame -> URL o None
        self.rubro = rubro_name
        self.idx = figapi._full_index()
        self.assets = figapi.Assets()
        self.table = []                       # acciones por elemento
        self.anchor_ids = set()
        self.overlays = {}                    # id frame -> html
        self.templates = {}                   # id componente -> html
        self.pending_ov, self.pending_tpl = [], []
        self.auto = {}                        # conjunto de variantes -> secuencia automática
        self.parent = {}
        for n in list(self.idx.values()):
            for c in n.get("children", []):
                self.parent[c["id"]] = n["id"]

    # ---------- análisis de interacciones ----------
    def set_of(self, comp_id):
        p = self.parent.get(comp_id)
        return self.idx.get(p) if p else None

    def variant_dest(self, dest_id):
        """Normaliza variantes de movimiento: siempre la versión 'Quieto' (el movimiento lo pone CSS)."""
        d = self.idx.get(dest_id)
        s = self.set_of(dest_id)
        if not d or not s or s["type"] != "COMPONENT_SET":
            return dest_id
        if "Movimiento=" in d["name"]:
            want = re.sub(r"Movimiento=[^,]+", "Movimiento=Quieto", d["name"])
            for c in s["children"]:
                if c["name"] == want:
                    return c["id"]
        return dest_id

    def actions(self, node):
        """Traduce las interacciones de Figma a acciones simples del motor JS."""
        out = []
        name = node["name"].lower()
        for it in node.get("interactions") or []:
            trig = it["trigger"]["type"]
            if trig not in ("ON_CLICK", "AFTER_TIMEOUT"):
                continue
            acts = []
            for a in self.flatten(it.get("actions") or ([it["action"]] if it.get("action") else [])):
                t, nav, dest = a.get("type"), a.get("navigation"), a.get("destinationId")
                if t == "URL":
                    acts.append({"k": "url", "u": a["url"], "b": 1 if a.get("openInNewTab") else 0})
                elif t in ("CLOSE",) or (t == "BACK"):
                    acts.append({"k": "close"})
                elif t == "NODE" and dest in self.idx:
                    dn = self.idx[dest]
                    if nav == "NAVIGATE":
                        url = self.frame_route(dn["name"])
                        if url:
                            acts.append({"k": "go", "u": url})
                    elif nav == "SCROLL_TO":
                        self.anchor_ids.add(dest)
                        acts.append({"k": "scroll", "id": "fz-" + slug(dest)})
                    elif nav in ("OVERLAY", "SWAP"):
                        if dest not in self.overlays and dest not in self.pending_ov:
                            self.pending_ov.append(dest)
                        acts.append({"k": "ov" if nav == "OVERLAY" else "swapov", "id": dest})
                    elif nav == "CHANGE_TO":
                        s = self.set_of(dest)
                        sname = (s or {}).get("name", "")
                        if "movimiento" in name or sname.startswith(("Cabecera 360", "Espigas")) or "Fase=" in dn["name"]:
                            if trig == "ON_CLICK" and n_is_button(node):
                                acts.append({"k": "motion"})
                            continue
                        if trig == "AFTER_TIMEOUT" and s and len(s.get("children", [])) > 8:
                            continue        # bucles de animación largos: los reemplaza CSS
                        d2 = self.variant_dest(dest)
                        if d2 not in self.templates and d2 not in self.pending_tpl:
                            self.pending_tpl.append(d2)
                        acts.append({"k": "change", "id": d2, "set": (s or {}).get("id", "")})
            if acts:
                e = {"t": "time" if trig == "AFTER_TIMEOUT" else "click", "a": acts}
                if trig == "AFTER_TIMEOUT":
                    e["ms"] = int(1000 * (it["trigger"].get("timeout") or 0.8))
                out.append(e)
        # tarjetas de función: el modal muestra la función pulsada
        if any(a["k"] == "ov" for e in out for a in e["a"]) and node["name"].startswith("Función · "):
            for e in out:
                e["fn"] = node["name"][len("Función · "):]
        return out

    def flatten(self, acts):
        res = []
        for a in acts:
            if not a:
                continue
            if a.get("type") == "CONDITIONAL":
                blocks = a.get("conditionalBlocks") or []
                # sin evaluar variables: se toma el bloque por defecto (el último)
                if blocks:
                    res.extend(self.flatten(blocks[-1].get("actions") or []))
            elif a.get("type") != "SET_VARIABLE":
                res.append(a)
        return res

    # ---------- conversión ----------
    def setup(self, conv, root):
        for n in figapi.find(lambda x: True, root):
            acts = self.actions(n) if n.get("interactions") else []
            if acts:
                self.table.append(acts)
                conv.hooks.setdefault(n["id"], {})["data-fz"] = len(self.table) - 1
            if n["type"] == "INSTANCE":
                comp = self.idx.get(n.get("componentId"))
                s = self.set_of(n.get("componentId")) if comp else None
                if s and s["type"] == "COMPONENT_SET":
                    conv.hooks.setdefault(n["id"], {})["data-set"] = s["id"]
                    if s["name"].startswith("Cabecera 360"):
                        conv.hooks[n["id"]]["data-spin"] = "1"
            if n["type"] in ("FRAME", "INSTANCE") and re.match(r"Entrada( de demostración)? · ", n["name"]):
                conv.replace[n["id"]] = self.field_html(conv, n)
            if n["name"] == "Preparar mi consulta" and n["type"] in ("FRAME", "INSTANCE"):
                h = conv.hooks.setdefault(n["id"], {})
                h["data-send"] = str(h.pop("data-fz")) if "data-fz" in h else "x"
            if n["name"].startswith(("Anillo exterior", "Anillo interior", "Espigas exteriores", "Espigas interiores")):
                conv.hooks.setdefault(n["id"], {})["data-ring"] = "out" if "exterior" in n["name"] else "in"
            if n["name"].startswith("Función · ") and n["type"] != "TEXT":
                conv.hooks.setdefault(n["id"], {})["data-card"] = "1"
            if n["type"] == "TEXT_PATH" and n.get("characters") and not n.get("_ring"):
                items = []
                for w in n["characters"].split("•"):
                    w = w.strip()
                    if w and w not in items:
                        items.append(w)
                if any(n["name"] == "Texto circular editable" and self.idx.get(self.parent.get(n["id"], ""), {}).get("name", "").startswith("Anillo exterior") for _ in [0]):
                    for extra in ("Logística", "Luka IA"):
                        if extra not in items:
                            items.append(extra)
                one = "".join(w + "  •  " for w in items)
                fs = (n.get("style") or {}).get("fontSize", 16)
                est = len(one) * fs * (0.62 if one.upper() == one else 0.55)
                circ = 3.1416 * (n.get("size") or {}).get("x", n["absoluteBoundingBox"]["width"])
                n["characters"] = one * max(1, round(circ * 0.985 / est))
                n["_ring"] = True
            if n["name"] in AUTO_BUTTONS or (n["type"] == "TEXT" and n.get("characters") in AUTO_BUTTONS and self.idx.get(self.parent.get(n["id"], ""), {}).get("type") == "INSTANCE"):
                conv.hooks.setdefault(n["id"], {})["data-hide"] = "1"
            if n["type"] == "INSTANCE":
                s0 = self.set_of(n.get("componentId") or "")
                if s0 and s0["type"] == "COMPONENT_SET" and s0["name"].startswith("Quinua"):
                    seq = [c["id"] for c in s0["children"] if c["name"] in ("Estado=Semilla", "Estado=Brote", "Estado=Creciendo", "Estado=Plena")]
                    for c in seq:
                        if c not in self.templates and c not in self.pending_tpl:
                            self.pending_tpl.append(c)
                    self.auto[s0["id"]] = {"seq": seq, "ms": [700, 700, 800, 2600]}
                if s0 and s0["type"] == "COMPONENT_SET" and s0["name"].startswith("Explorador"):
                    conv.hooks.setdefault(n["id"], {})["data-enter"] = "1"
            if n["type"] == "TEXT" and n.get("characters", "").strip() in MOTION_BUTTONS:
                par = self.idx.get(self.parent.get(n["id"], ""), {})
                target = par["id"] if par.get("type") in ("FRAME", "INSTANCE") and par["absoluteBoundingBox"]["width"] < 400 else n["id"]
                conv.hooks.setdefault(target, {})["data-hide"] = "1"
            if n["type"] == "TEXT" and n.get("characters", "").strip() in MOTION_LABELS:
                conv.hooks.setdefault(n["id"], {})["data-hide"] = "1"
            if n["type"] in ("FRAME", "INSTANCE") and n["name"] in ("Sin movimiento", "Cambiar movimiento", "Reproducir", "Activar movimiento"):
                conv.hooks.setdefault(n["id"], {})["data-hide"] = "1"
            if n["type"] == "TEXT" and n.get("characters") in TEXT_FIX:
                n["characters"] = TEXT_FIX[n["characters"]]
                n["characterStyleOverrides"] = []
            if n["type"] == "TEXT" and "characters" in (n.get("boundVariables") or {}):
                conv.hooks.setdefault(n["id"], {})["data-var"] = n["boundVariables"]["characters"]["id"]
            if n.get("scrollBehavior") == "FIXED" and n is not root:
                conv.hooks.setdefault(n["id"], {})["data-fixed"] = "1"
        for i in list(self.anchor_ids):
            conv.hooks.setdefault(i, {})["data-anchor"] = "fz-" + slug(i)

    def field_html(self, conv, n):
        key = FIELD_KEYS.get(slug(n["name"].split("·")[-1]).split("-")[0], slug(n["name"].split("·")[-1]))
        label = n["name"].split("·")[-1].strip()
        texts = [c for c in figapi.find(lambda x: x["type"] == "TEXT", n)]
        ph = texts[0]["characters"] if texts else ""
        tst = conv.text_style(texts[0]["style"], texts[0].get("fills")) if texts else {}

        def make(node, st):
            box = dict(st)
            conv.fills_css(node, box); conv.strokes_css(node, box); conv.radius_css(node, box)
            pad = [node.get("paddingTop", 0), node.get("paddingRight", 0), node.get("paddingBottom", 0), node.get("paddingLeft", 0)]
            box["padding"] = " ".join(px(p) for p in pad)
            box.update(tst)
            box["display"] = "block"; box["outline"] = "none"; box["resize"] = "none"
            box["height"] = px(node["absoluteBoundingBox"]["height"])
            box["-webkit-text-fill-color"] = box.get("color", "inherit")
            css = conv.css(box)
            multi = key == "necesidad"
            tag = "textarea" if multi else "input"
            attrs = {"name": key, "placeholder": ph, "data-label": label, "aria-label": label, "style": css}
            if key == "whatsapp":
                attrs.update({"inputmode": "numeric", "autocomplete": "tel"})
            if key == "nombre":
                attrs["autocomplete"] = "name"
            if key == "locales":
                attrs["inputmode"] = "numeric"
            a = "".join(f' {k}="{esc(str(v))}"' for k, v in attrs.items())
            return f"<textarea{a}></textarea>" if multi else f"<input type=\"text\"{a}>"
        return make

    def convert(self, root, parent=None):
        conv = Converter(None, None)
        self.setup(conv, root)
        return build_fig.build(root, self.assets, setup=lambda c: (c.hooks.update(conv.hooks), c.replace.update(conv.replace)))

    def build_frame(self, frame_id):
        return self.convert(self.idx[frame_id])

    def drain(self):
        while self.pending_ov or self.pending_tpl:
            if self.pending_ov:
                i = self.pending_ov.pop(0)
                self.overlays[i] = (self.convert(self.idx[i]), int(self.idx[i]["absoluteBoundingBox"]["width"]))
            else:
                i = self.pending_tpl.pop(0)
                self.templates[i] = self.convert(self.idx[i])


def build_page(desk_id, mob_id, rubro, title, desc, frame_route):
    pg = Page({}, frame_route, rubro)
    desk = pg.build_frame(desk_id)
    mob = pg.build_frame(mob_id) if mob_id else ""
    pg.drain()
    pg.assets.save()
    root = pg.idx[desk_id]
    bgf = [f for f in root.get("fills", []) if f.get("visible", True) and f["type"] == "SOLID"]
    from fig2html import rgba
    bg = rgba(bgf[-1]["color"]) if bgf else "#ffffff"
    import shell
    return shell.page(title, desc, bg, desk, mob, pg.overlays, pg.templates, pg.table, rubro, pg.auto)
