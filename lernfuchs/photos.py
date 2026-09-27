"""Echte Fotos (aus dem Klexikon / Wikimedia Commons) für Such- und Unterschiedsaufgaben.

Die Fotos werden beim ersten Start im Hintergrund geladen und im Ordner daten/fotos gespeichert,
danach funktioniert alles auch offline.
"""

import colorsys
import json
import os
import random
import threading
import urllib.parse
import urllib.request

from PIL import Image, ImageEnhance, ImageFilter, ImageOps, ImageStat

from .storage import DATA_DIR

PHOTO_DIR = os.path.join(DATA_DIR, "fotos")
INDEX = os.path.join(PHOTO_DIR, "index.json")
API = "https://klexikon.zum.de/api.php"
UA = {"User-Agent": "LernFuchs/1.0 (Lern-App fuer Grundschulkinder; privat)"}

THEMEN = [
    "Fuchs", "Elefanten", "Giraffen", "Zebras", "Tiger", "Papageien", "Pinguine", "Eisbären", "Flamingos",
    "Pfau", "Chamäleons", "Koalas", "Delfine", "Frösche", "Marienkäfer", "Schmetterlinge", "Eichhörnchen",
    "Pferde", "Kühe", "Leuchtturm", "Hafen", "Bauernhof", "Markt", "Eisenbahn", "Feuerwehr", "Schloss Neuschwanstein",
    "Alpen", "Wald", "Obst", "Gemüse", "Blumen", "Tulpen", "Sonnenblumen", "Brücke", "Segelschiff", "Traktor",
    "Heißluftballon", "Riesenrad", "Burg", "Venedig", "Korallenriff", "Tukan", "Erdbeeren", "Kürbis",
]

_lock = threading.Lock()
_loading = False


def _load_index():
    try:
        with open(INDEX, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def available() -> list:
    idx = _load_index()
    return [os.path.join(PHOTO_DIR, v["file"]) for v in idx.values()
            if v.get("file") and os.path.isfile(os.path.join(PHOTO_DIR, v["file"]))]


def random_photo(exclude=()):
    lst = [p for p in available() if p not in exclude] or available()
    return random.choice(lst) if lst else None


def prefetch(max_photos=40):
    """Lädt fehlende Fotos im Hintergrund (nur einmal gleichzeitig)."""
    global _loading
    with _lock:
        if _loading:
            return
        _loading = True

    def work():
        global _loading
        try:
            os.makedirs(PHOTO_DIR, exist_ok=True)
            idx = _load_index()
            for title in random.sample(THEMEN, len(THEMEN)):
                if sum(1 for v in idx.values() if v.get("file")) >= max_photos:
                    break
                if title in idx:
                    continue
                try:
                    url = API + "?" + urllib.parse.urlencode({
                        "action": "query", "generator": "search", "gsrsearch": title, "gsrlimit": 1,
                        "prop": "pageimages", "pithumbsize": 800, "format": "json"})
                    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=8) as r:
                        d = json.loads(r.read().decode("utf-8"))
                    page = next(iter(d["query"]["pages"].values()))
                    th = page.get("thumbnail")
                    if not th or th.get("width", 0) < 500 or not (1.15 < th["width"] / max(1, th["height"]) < 1.9):
                        idx[title] = {"file": "", "skip": True}
                        continue
                    with urllib.request.urlopen(urllib.request.Request(th["source"], headers=UA), timeout=10) as r:
                        data = r.read()
                    fn = "".join(ch if ch.isalnum() else "_" for ch in title) + ".jpg"
                    path = os.path.join(PHOTO_DIR, fn)
                    im = Image.open(__import__("io").BytesIO(data)).convert("RGB")
                    im.thumbnail((800, 600))
                    im.save(path, quality=88)
                    idx[title] = {"file": fn, "title": page["title"]}
                    with open(INDEX, "w", encoding="utf-8") as fh:
                        json.dump(idx, fh, ensure_ascii=False)
                except Exception:
                    continue
        finally:
            with _lock:
                _loading = False
    threading.Thread(target=work, daemon=True).start()


# --- Bildbearbeitung ------------------------------------------------------------

def fit(im: Image.Image, w: int, h: int) -> Image.Image:
    return ImageOps.fit(im, (w, h), Image.LANCZOS)


def _hue_shift(region: Image.Image, deg: float) -> Image.Image:
    hsv = region.convert("HSV")
    hch, s, v = hsv.split()
    shift = int(deg / 360 * 255)
    hch = hch.point(lambda x: (x + shift) % 256)
    return Image.merge("HSV", (hch, s, v)).convert("RGB")


def _region_diff(a: Image.Image, b: Image.Image) -> float:
    from PIL import ImageChops
    return sum(ImageStat.Stat(ImageChops.difference(a, b)).mean) / 3


def _strength(level: int) -> dict:
    """Wie deutlich die Veränderungen sind – je höher die Stufe, desto feiner."""
    lv = max(1, min(8, level))
    return {
        "hue": {1: (60, 95), 2: (50, 80), 3: (42, 65), 4: (36, 55), 5: (32, 48), 6: (28, 42), 7: (25, 38),
                8: (22, 34)}[lv],
        "bright": {1: 0.35, 2: 0.3, 3: 0.28, 4: 0.22, 5: 0.18, 6: 0.15, 7: 0.13, 8: 0.11}[lv],
        "min_diff": {1: 24, 2: 20, 3: 16, 4: 13, 5: 11, 6: 9, 7: 8, 8: 7}[lv],
        "feather": 4 + lv,
    }


def _change(base, r, meth, st, W):
    """Liefert den veränderten Bildausschnitt für Rechteck r."""
    orig = base.crop(r)
    bw, bh = orig.size
    if meth == "farbe":
        lo, hi = st["hue"]
        return _hue_shift(orig, random.choice([-1, 1]) * random.uniform(lo, hi) % 360)
    if meth == "hell":
        d = st["bright"]
        return ImageEnhance.Brightness(orig).enhance(random.choice([1 - d, 1 + d]))
    if meth == "spiegeln":
        return ImageOps.mirror(orig) if random.random() < 0.7 else ImageOps.flip(orig)
    if meth == "verschieben":  # Inhalt ein Stück versetzt – „etwas ist verrutscht“
        dx, dy = int(bw * random.uniform(0.25, 0.4)) * random.choice([-1, 1]), int(bh * random.uniform(0, 0.25))
        sx = min(max(0, r[0] + dx), W - bw)
        sy = min(max(0, r[1] + dy), base.size[1] - bh)
        return base.crop((sx, sy, sx + bw, sy + bh))
    # „weg“: Bereich durch benachbarten Hintergrund ersetzen
    dx = random.choice([-1, 1]) * bw
    sx = min(max(0, r[0] + dx), W - bw)
    return base.crop((sx, r[1], sx + bw, r[1] + bh))


def make_difference_pair(path: str, n: int, size=(560, 420), box=(70, 100), level: int = 1):
    """Erzeugt (Original, Fehlerbild, [Rechtecke]) mit n Unterschieden. Stufe steuert, wie fein sie sind."""
    st = _strength(level)
    base = fit(Image.open(path).convert("RGB"), *size)
    mod = base.copy()
    W, H = size
    gray = base.convert("L")
    cands = []
    for _ in range(320):
        bw, bh = random.randint(*box), random.randint(*box)
        x, y = random.randint(8, W - bw - 8), random.randint(8, H - bh - 8)
        detail = ImageStat.Stat(gray.crop((x, y, x + bw, y + bh))).stddev[0]
        cands.append((detail, (x, y, x + bw, y + bh)))
    cands.sort(reverse=True)
    top = [c[1] for c in cands[:160]]
    random.shuffle(top)
    chosen = []
    for r in top:
        if len(chosen) >= n:
            break
        if any(not (r[2] + 14 < c[0] or c[2] + 14 < r[0] or r[3] + 14 < c[1] or c[3] + 14 < r[1]) for c in chosen):
            continue
        orig = base.crop(r)
        mask = Image.new("L", orig.size, 0)
        m = st["feather"]
        mask.paste(255, (m, m, orig.size[0] - m, orig.size[1] - m))
        mask = mask.filter(ImageFilter.GaussianBlur(m * 0.8))
        sat = ImageStat.Stat(orig.convert("HSV").split()[1]).mean[0]
        methods = ["weg", "verschieben", "spiegeln", "hell"] + (["farbe", "farbe"] if sat > 40 else [])
        random.shuffle(methods)
        for meth in methods:
            new = _change(base, r, meth, st, W)
            diff = _region_diff(orig, new)
            if st["min_diff"] <= diff:
                mod.paste(new, r[:2], mask)
                chosen.append(r)
                break
    return base, mod, chosen


def tile(path: str, crop: tuple, fx: str, px: int, patch=None) -> Image.Image:
    """Quadratischer Bildausschnitt, optional verändert (für „Was ist anders?“)."""
    im = Image.open(path).convert("RGB").crop(tuple(crop))
    if fx == "mirror":
        im = ImageOps.mirror(im)
    elif fx == "rotate":
        im = im.rotate(180)
    elif fx == "color":
        im = _hue_shift(im, 150)
    elif fx == "patch" and patch:
        w, h = im.size
        x0, y0, x1, y1, meth, lvl = patch
        r = (int(x0 * w), int(y0 * h), int(x1 * w), int(y1 * h))
        random.seed(hash((path, tuple(crop), tuple(patch[:4]))) & 0xFFFF)  # gleiche Veränderung bei jedem Zeichnen
        new = _change(im, r, meth, _strength(lvl), w)
        random.seed()
        mask = Image.new("L", new.size, 0)
        m = 3
        mask.paste(255, (m, m, new.size[0] - m, new.size[1] - m))
        im.paste(new, r[:2], mask.filter(ImageFilter.GaussianBlur(2)))
    return im.resize((px, px), Image.LANCZOS)


def odd_tile_spec(path: str, lvl: int):
    """Wählt Ausschnitt + Veränderung. Ab Stufe 2 nur ein kleiner Teil des Fotos → genau hinsehen!"""
    im = Image.open(path).convert("RGB")
    w, h = im.size
    side = int(min(w, h) * random.uniform(0.55, 0.8))
    x, y = random.randint(0, w - side), random.randint(0, h - side)
    crop = (x, y, x + side, y + side)
    if lvl <= 1:
        return crop, random.choice(["mirror", "rotate", "color"]), None
    base = tile(path, crop, None, 128)
    size = {2: 0.42, 3: 0.35, 4: 0.3, 5: 0.26}.get(lvl, 0.24)
    gray = base.convert("L")
    best = None
    for _ in range(40):  # Stelle mit vielen Details suchen, damit die Änderung sichtbar bleibt
        x0, y0 = random.uniform(0.05, 0.95 - size), random.uniform(0.05, 0.95 - size)
        box = (int(x0 * 128), int(y0 * 128), int((x0 + size) * 128), int((y0 + size) * 128))
        d = ImageStat.Stat(gray.crop(box)).stddev[0]
        if best is None or d > best[0]:
            best = (d, x0, y0)
    _, x0, y0 = best
    for meth in random.sample(["weg", "verschieben", "spiegeln", "farbe", "hell"], 5):
        patch = [x0, y0, x0 + size, y0 + size, meth, lvl + 1]
        if _region_diff(base, tile(path, crop, "patch", 128, patch)) > 1.2:
            return crop, "patch", patch
    return crop, "patch", [x0, y0, x0 + size, y0 + size, "weg", lvl]


def random_photos(n: int) -> list:
    """n verschiedene Fotos mit Titel: [(pfad, titel), …]."""
    idx = _load_index()
    lst = [(os.path.join(PHOTO_DIR, v["file"]), v.get("title", k)) for k, v in idx.items()
           if v.get("file") and os.path.isfile(os.path.join(PHOTO_DIR, v["file"]))]
    seen, out = set(), []
    for p, t in random.sample(lst, len(lst)):
        if t not in seen:
            seen.add(t)
            out.append((p, t))
        if len(out) >= n:
            break
    return out


def square_thumb(path: str, px: int) -> Image.Image:
    im = Image.open(path).convert("RGB")
    return ImageOps.fit(im, (px, px), Image.LANCZOS)
