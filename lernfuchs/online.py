"""Online-Inhalte aus dem Klexikon (Kinderlexikon, klexikon.zum.de) – mit Offline-Zwischenspeicher."""

import io
import json
import os
import random
import re
import threading
import urllib.parse
import urllib.request

from .storage import DATA_DIR

API = "https://klexikon.zum.de/api.php"
UA = {"User-Agent": "LernFuchs/1.0 (Lern-App fuer Grundschulkinder; privat)"}
CACHE_FILE = os.path.join(DATA_DIR, "klexikon_cache.json")
IMG_DIR = os.path.join(DATA_DIR, "bilder")

# Kindgerechte, zum Sachunterricht passende Themen
THEMEN = [
    "Igel", "Eichhörnchen", "Fuchs", "Honigbiene", "Pinguine", "Delfine", "Elefant", "Löwe", "Dinosaurier",
    "Wal", "Regenbogen", "Gewitter", "Vulkan", "Mond", "Sonne", "Mars", "Erde", "Schnee", "Wald", "Bauernhof",
    "Kuh", "Pferd", "Feuerwehr", "Ritter", "Burg", "Pyramide", "Eisbär", "Schmetterling", "Marienkäfer",
    "Ameisen", "Kartoffel", "Apfel", "Schokolade", "Fahrrad", "Eisenbahn", "Flugzeug", "Rakete", "Bayern",
    "München", "Alpen", "Donau", "Zugspitze", "Zahn", "Herz", "Skelett", "Magnet", "Wasser", "Wolke",
    "Maulwurf", "Frosch", "Eule", "Specht", "Hase", "Reh", "Schnecke", "Spinne", "Regenwurm", "Kastanie",
    "Eiche", "Sonnenblume", "Tulpe", "Biber", "Fledermaus", "Hai", "Krake", "Giraffe", "Zebra", "Känguru",
]


def _get(params, timeout=6):
    url = API + "?" + urllib.parse.urlencode({**params, "format": "json"})
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def _load_cache():
    try:
        with open(CACHE_FILE, encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def _save_cache(cache):
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(CACHE_FILE, "w", encoding="utf-8") as fh:
        json.dump(cache, fh, ensure_ascii=False)


def _short(text, max_sent=5):
    text = re.sub(r"\s+", " ", text).strip()
    sents = re.split(r"(?<=[.!?])\s+", text)
    out = []
    for s in sents:
        out.append(s)
        if len(out) >= max_sent or sum(len(x) for x in out) > 520:
            break
    return " ".join(out)


def fetch_article(title: str) -> dict:
    d = _get({"action": "query", "generator": "search", "gsrsearch": title, "gsrlimit": 1,
              "prop": "extracts|pageimages", "exintro": 1, "explaintext": 1, "pithumbsize": 420,
              "redirects": 1})
    page = next(iter(d["query"]["pages"].values()))
    art = {"title": page["title"], "text": _short(page.get("extract", "")), "img": ""}
    thumb = page.get("thumbnail", {}).get("source")
    if thumb:
        try:
            req = urllib.request.Request(thumb, headers=UA)
            with urllib.request.urlopen(req, timeout=6) as r:
                data = r.read()
            os.makedirs(IMG_DIR, exist_ok=True)
            fn = re.sub(r"[^A-Za-z0-9]+", "_", page["title"]) + ".img"
            path = os.path.join(IMG_DIR, fn)
            with open(path, "wb") as fh:
                fh.write(data)
            art["img"] = path
        except Exception:
            pass
    return art


def load_random(callback, exclude=()):
    """Lädt einen zufälligen Artikel im Hintergrund; callback(article or None, offline: bool)."""
    def work():
        cache = _load_cache()
        titles = [t for t in THEMEN if t not in exclude] or THEMEN
        title = random.choice(titles)
        try:
            art = fetch_article(title)
            if len(art["text"]) < 60:
                raise ValueError("zu kurz")
            cache[title] = art
            _save_cache(cache)
            callback(art, False, title)
        except Exception:
            if cache:
                key = random.choice(list(cache))
                callback(cache[key], True, key)
            else:
                callback(None, True, title)
    threading.Thread(target=work, daemon=True).start()


def make_quiz(art: dict):
    """Lückentext-Frage aus dem Artikel: ein wichtiges Nomen fehlt."""
    sents = re.split(r"(?<=[.!?])\s+", art["text"])
    words_all = set()
    for s in sents:
        for i, w in enumerate(re.findall(r"[A-ZÄÖÜ][a-zäöüß]{4,}", s)):
            words_all.add(w)
    candidates = []
    for s in sents:
        ws = re.findall(r"(?<!^)(?<=\s)([A-ZÄÖÜ][a-zäöüß]{4,})", s)
        for w in ws:
            if w.lower() not in art["title"].lower() and len(s) < 180:
                candidates.append((s, w))
    if not candidates:
        return None
    s, w = random.choice(candidates)
    wrong = [x for x in words_all if x != w and x.lower() not in art["title"].lower()]
    if len(wrong) < 2:
        return None
    opts = random.sample(wrong, 2) + [w]
    random.shuffle(opts)
    return {"sentence": s.replace(w, "_____", 1), "answer": w, "options": opts}


def load_image(path, max_w=380, max_h=280):
    from PIL import Image
    im = Image.open(path)
    im.thumbnail((max_w, max_h))
    return im
