# -*- coding: utf-8 -*-
"""Genera las 12 páginas del proyecto desde la copia local del Figma.
Uso: python3 _generador/figma/build_all.py [clave ...]   (sin claves = todas)
"""
import os, re, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import figapi, pagina
from data import NAMES, ROUTES, BASE_URL, TAGLINES

FRAMES = {}
for i, n in figapi.json.load(open(os.path.join(figapi.CACHE, "index.json"))).items():
    m = re.match(r"Apiworking · (.+?)(?: · (Desktop|Mobile))?$", n["name"])
    if m and n["type"] == "FRAME":
        FRAMES[(m.group(1), m.group(2) or "Desktop")] = i


def route(fname):
    m = re.match(r"Apiworking · (.+?)(?: · (Desktop|Mobile))?$", fname)
    if not m:
        return None
    nm = m.group(1)
    if nm == "Inicio":
        return BASE_URL + "/"
    for k, v in NAMES.items():
        if v == nm:
            return BASE_URL + "/" + ROUTES[k].strip("/") + "/"
    return None


# Ajustes de contenido sobre el Figma (pedidos del usuario)
# 2026-11-24: en Inicio se quitan "Confianza · hechos del ecosistema" (11 / 264) y "Cómo funciona"
#             y en su lugar va la cabecera (Hero) de Tiendas.
EDITS = {
    "inicio": [("10:2", ["10:5", "10:6"], "10:64"), ("54:2464", ["54:2467", "54:2468"], "10:76")],
}


def apply_edits(key):
    import copy
    idx = figapi._full_index()
    for frame, remove, insert in EDITS.get(key, []):
        kids = idx[frame]["children"]
        pos = min(i for i, c in enumerate(kids) if c["id"] in remove)
        kids[:] = [c for c in kids if c["id"] not in remove]
        node = copy.deepcopy(idx[insert])
        node["layoutSizingHorizontal"] = "FILL"
        kids.insert(pos, node)


def build(key):
    apply_edits(key)
    name = "Inicio" if key == "inicio" else NAMES[key]
    desk = FRAMES[(name, "Desktop")]
    mob = FRAMES.get((name, "Mobile"))
    title = "Apiworking" if key == "inicio" else f"Apiworking · {name}"
    desc = "Hecho para tu negocio. Pensado para que vuelvan." if key == "inicio" else f"Sistema para {name.lower()}: {TAGLINES.get(key, '')}"
    html = pagina.build_page(desk, mob, "" if key == "inicio" else name, title, desc, route)
    out = os.path.join(PROJECT, key, ("index" if key == "inicio" else key) + ".html")
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    return out, len(html)


if __name__ == "__main__":
    keys = sys.argv[1:] or ["inicio"] + list(NAMES)
    for k in keys:
        t = time.time()
        out, size = build(k)
        print(f"{os.path.relpath(out, PROJECT)}: {size//1024} KB ({time.time()-t:.0f}s)", flush=True)
