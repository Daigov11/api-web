# -*- coding: utf-8 -*-
"""Acceso a la API de Figma y a la API de imágenes de Apiworking, con caché local.

- Token de Figma: ~/.figma_token (solo lectura). Nunca se guarda en el repo.
- Caché de JSON de Figma: _generador/figma/cache/ (ignorado por git).
- assets.json: mapa recurso -> URL definitiva en S3 (se versiona, evita re-subir).
"""
import hashlib, json, os, re, subprocess, time, urllib.parse, urllib.request

FILE_KEY = "FOlwySZnBYyLc0rKWgWWI4"
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "cache")
ASSETS_PATH = os.path.join(HERE, "assets.json")
UPLOAD_URL = "https://api-centralizador.apiworking.pe/api/Data/images"
os.makedirs(CACHE, exist_ok=True)


def _token():
    with open(os.path.expanduser("~/.figma_token")) as f:
        return f.read().strip()


def _get(url, raw=False, tries=6):
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"X-Figma-Token": _token()} if "api.figma.com" in url else {})
            with urllib.request.urlopen(req, timeout=180) as r:
                data = r.read()
            return data if raw else json.loads(data)
        except urllib.error.HTTPError as e:
            if e.code == 429 and i < tries - 1:
                wait = int(e.headers.get("Retry-After") or 0) or 30 * (i + 1)
                print(f"Figma 429: esperando {wait}s", flush=True)
                time.sleep(min(wait, 300)); continue
            raise
        except Exception:
            if i < tries - 1:
                time.sleep(3); continue
            raise


_FULL = {}


def _full_index():
    """Índice id -> nodo de todo el archivo (descargado una vez en cache/full_file.json)."""
    if not _FULL:
        with open(os.path.join(CACHE, "full_file.json")) as f:
            doc = json.load(f)["document"]
        stack = [doc]
        while stack:
            n = stack.pop()
            _FULL[n["id"]] = n
            stack.extend(n.get("children", []))
    return _FULL


def node_tree(node_id, refresh=False):
    """Árbol completo de un nodo. Sale de la copia local del archivo (no gasta cupo de la API)."""
    path = os.path.join(CACHE, "node_" + re.sub(r"[^\w-]", "_", node_id.replace(":", "-")) + ".json")
    if os.path.exists(path) and not refresh:
        with open(path) as f:
            return json.load(f)
    return _full_index()[node_id]


def find(pred, root=None):
    out, stack = [], [root] if root else [ _full_index()[k] for k in list(_full_index())[:1] ]
    while stack:
        n = stack.pop()
        if pred(n):
            out.append(n)
        stack.extend(reversed(n.get("children", [])))
    return out


def image_fill_urls():
    path = os.path.join(CACHE, "image_fills.json")
    if os.path.exists(path) and time.time() - os.path.getmtime(path) < 3 * 86400:
        with open(path) as f:
            return json.load(f)
    d = _get(f"https://api.figma.com/v1/files/{FILE_KEY}/images")
    m = d["meta"]["images"]
    with open(path, "w") as f:
        json.dump(m, f)
    return m


def render_urls(ids, fmt="png", scale=2):
    out = {}
    ids = list(ids)
    for i in range(0, len(ids), 40):
        chunk = ids[i:i + 40]
        q = urllib.parse.urlencode({"ids": ",".join(chunk), "format": fmt, "scale": scale,
                                    "svg_include_id": "false", "svg_simplify_stroke": "true"})
        d = _get(f"https://api.figma.com/v1/images/{FILE_KEY}?{q}")
        out.update({k: v for k, v in d["images"].items() if v})
    return out


def download(url):
    return _get(url, raw=True)


LIMIT = 1_900_000


def _sips(args):
    subprocess.run(["sips"] + args, capture_output=True, check=True)


def optimize(data, ext, max_dim=2000):
    """Reduce peso: fotos opacas -> JPG 82; con transparencia -> PNG reducido. Usa sips (macOS)."""
    if ext not in ("png", "jpg"):
        return data, ext
    tmp = os.path.join(CACHE, "opt_" + hashlib.sha1(data).hexdigest())
    src = tmp + "." + ext
    with open(src, "wb") as f:
        f.write(data)
    try:
        info = subprocess.run(["sips", "-g", "hasAlpha", "-g", "pixelWidth", "-g", "pixelHeight", src], capture_output=True, text=True).stdout
        alpha = "hasAlpha: yes" in info
        w = int(re.search(r"pixelWidth: (\d+)", info).group(1)); h = int(re.search(r"pixelHeight: (\d+)", info).group(1))
        dim = max_dim
        for _ in range(4):
            out = tmp + ("_o.png" if alpha else "_o.jpg")
            args = ["-Z", str(min(dim, max(w, h)))]
            if alpha:
                _sips(args + [src, "--out", out])
            else:
                _sips(args + ["-s", "format", "jpeg", "-s", "formatOptions", "82", src, "--out", out])
            with open(out, "rb") as f:
                res = f.read()
            os.remove(out)
            if len(res) <= LIMIT and (alpha or len(res) < len(data) or ext == "png"):
                return res, ("png" if alpha else "jpg")
            if len(res) <= LIMIT:
                return (data, ext) if len(data) <= LIMIT else (res, "png" if alpha else "jpg")
            dim = int(dim * 0.75)
        return res, ("png" if alpha else "jpg")
    finally:
        os.remove(src)


class Assets:
    """Mapa persistente clave -> URL en S3 de Apiworking."""

    def __init__(self):
        self.map = {}
        if os.path.exists(ASSETS_PATH):
            with open(ASSETS_PATH) as f:
                self.map = json.load(f)

    def save(self):
        with open(ASSETS_PATH, "w") as f:
            json.dump(self.map, f, indent=1, sort_keys=True)

    def upload_bytes(self, key, data, ext, max_dim=2000):
        if key in self.map:
            return self.map[key]
        data, ext = optimize(data, ext, max_dim)
        digest = hashlib.sha1(data).hexdigest()
        if "sha1:" + digest in self.map:          # mismo archivo ya subido con otra clave
            self.map[key] = self.map["sha1:" + digest]; return self.map[key]
        tmp = os.path.join(CACHE, "up_" + digest + "." + ext)
        with open(tmp, "wb") as f:
            f.write(data)
        res = subprocess.run(["curl", "-s", "--max-time", "180", "-X", "POST", UPLOAD_URL,
                              "-H", "accept: */*", "-F", "image=@" + tmp], capture_output=True, text=True)
        os.remove(tmp)
        url = json.loads(res.stdout)["url"]
        self.map[key] = url
        self.map["sha1:" + digest] = url
        self.save()
        return url
