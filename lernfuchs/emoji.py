"""Emojis als Bilder: realistische 3D-Emojis (Microsoft Fluent) und animierte 3D-Emojis.

- 3D-Standbilder und Animationen werden einmalig im Hintergrund geladen und lokal gespeichert.
- Solange ein 3D-Bild noch fehlt, wird das farbige Windows-Emoji (Segoe UI Emoji) gezeichnet.
"""

import json
import os
import re
import threading
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

from PIL import Image, ImageDraw, ImageFont, ImageTk
import customtkinter as ctk

from .storage import DATA_DIR

_RENDER_PX = 128
DIR_3D = os.path.join(DATA_DIR, "emoji3d")
DIR_ANIM = os.path.join(DATA_DIR, "animation")
URL_3D = "https://raw.githubusercontent.com/microsoft/fluentui-emoji/main/"
URL_ANIM = "https://raw.githubusercontent.com/Tarikul-Islam-Anik/Animated-Fluent-Emojis/master/"
UA = {"User-Agent": "LernFuchs/2.0"}

_FONT_CANDIDATES = [
    os.path.join(os.environ.get("WINDIR", r"C:\Windows"), "Fonts", "seguiemj.ttf"),
    "seguiemj.ttf",
]


# --- Index & Namen ---------------------------------------------------------------

@lru_cache(maxsize=1)
def _index():
    try:
        with open(os.path.join(os.path.dirname(__file__), "emoji_index.json"), encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {"3d": {}, "anim": {}}


def _norm(s: str) -> str:
    return re.sub(r"[^a-z0-9 ]", "", s.lower().replace("_", " ").replace("-", " ")).strip()


@lru_cache(maxsize=4096)
def emoji_name(ch: str) -> str:
    try:
        import emoji as emj
        return _norm(emj.demojize(ch).strip(":"))
    except Exception:
        return ""


@lru_cache(maxsize=4096)
def split_emojis(text: str) -> tuple:
    try:
        import emoji as emj
        found = [e["emoji"] for e in emj.emoji_list(text)]
        if found and "".join(found) == text.replace("\ufe0f", "") or "".join(found) == text:
            return tuple(found)
    except Exception:
        pass
    return (text,)


def _path_3d(ch):
    return os.path.join(DIR_3D, emoji_name(ch).replace(" ", "_") + ".png")


def _path_anim(name):
    return os.path.join(DIR_ANIM, name.replace(" ", "_") + ".png")


# --- Downloads im Hintergrund ---------------------------------------------------------

_pool = ThreadPoolExecutor(max_workers=3)
_pending = set()
_lock = threading.Lock()
online = True


def _download(url, path):
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=12) as r:
            data = r.read()
        if len(data) > 200:
            tmp = path + ".part"
            with open(tmp, "wb") as fh:
                fh.write(data)
            os.replace(tmp, path)
    except Exception:
        pass
    finally:
        with _lock:
            _pending.discard(path)


def _queue(url, path):
    with _lock:
        if path in _pending or os.path.exists(path):
            return
        _pending.add(path)
    _pool.submit(_download, url, path)


def prewarm(texts):
    """Lädt fehlende 3D-Bilder für alle übergebenen Emojis im Hintergrund."""
    if not online:
        return
    os.makedirs(DIR_3D, exist_ok=True)
    idx = _index()["3d"]
    for t in texts:
        for ch in split_emojis(t):
            name = emoji_name(ch)
            if name in idx:
                _queue(URL_3D + urllib.parse.quote(idx[name]), _path_3d(ch))


def prefetch_anims(names):
    if not online:
        return
    os.makedirs(DIR_ANIM, exist_ok=True)
    idx = _index()["anim"]
    for n in names:
        key = _norm(n) if n in idx or _norm(n) in idx else emoji_name(n)
        if key in idx:
            _queue(URL_ANIM + urllib.parse.quote(idx[key]), _path_anim(key))


# --- Rendern ---------------------------------------------------------------------

@lru_cache(maxsize=1)
def _font():
    for path in _FONT_CANDIDATES:
        try:
            return ImageFont.truetype(path, _RENDER_PX)
        except OSError:
            continue
    return None


def _flat(text: str) -> Image.Image:
    font = _font()
    size = _RENDER_PX * (len(text) + 2)
    im = Image.new("RGBA", (size * 2, _RENDER_PX * 3), (0, 0, 0, 0))
    draw = ImageDraw.Draw(im)
    if font is None:
        draw.text((10, 10), text, fill="black")
    else:
        draw.text((size, int(_RENDER_PX * 1.5)), text, font=font, anchor="mm", embedded_color=True)
    bbox = im.getbbox()
    if not bbox:
        return Image.new("RGBA", (_RENDER_PX, _RENDER_PX), (0, 0, 0, 0))
    return im.crop(bbox)


def _square(im: Image.Image) -> Image.Image:
    w, h = im.size
    side = max(w, h, int(_RENDER_PX * 0.9))
    if w <= _RENDER_PX * 1.3 * max(1, h / _RENDER_PX):
        sq = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        sq.paste(im, ((side - w) // 2, (side - h) // 2), im)
        return sq
    return im


def _single(ch: str) -> Image.Image:
    p = _path_3d(ch)
    if emoji_name(ch) and os.path.exists(p):
        try:
            im = Image.open(p).convert("RGBA")
            im.thumbnail((_RENDER_PX, _RENDER_PX), Image.LANCZOS)
            return im
        except Exception:
            pass
    return _square(_flat(ch))


@lru_cache(maxsize=2048)
def _render(text: str) -> Image.Image:
    parts = split_emojis(text)
    if len(parts) == 1:
        return _single(parts[0])
    ims = [_single(p) for p in parts]
    w = sum(i.size[0] for i in ims) + 8 * (len(ims) - 1)
    h = max(i.size[1] for i in ims)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    x = 0
    for i in ims:
        out.paste(i, (x, (h - i.size[1]) // 2), i)
        x += i.size[0] + 8
    return out


def emoji_image(text: str, size: int) -> ctk.CTkImage:
    """CTkImage für Labels/Buttons; `size` = Höhe in (logischen) Pixeln."""
    return _ctk_image(text, int(size))


@lru_cache(maxsize=2048)
def _ctk_image(text: str, size: int) -> ctk.CTkImage:
    im = _render(text)
    w, h = im.size
    return ctk.CTkImage(light_image=im, dark_image=im, size=(max(1, int(w * size / h)), size))


_photo_cache: dict = {}


def emoji_photo(text: str, px: int, gray: bool = False) -> ImageTk.PhotoImage:
    """PhotoImage für tk.Canvas (px = echte Bildschirmpixel)."""
    key = (text, px, gray)
    if key not in _photo_cache:
        im = _render(text)
        w, h = im.size
        im = im.resize((max(1, int(w * px / h)), px), Image.LANCZOS)
        if gray:
            alpha = im.getchannel("A")
            im = im.convert("L").convert("RGBA")
            im.putalpha(alpha.point(lambda a: a * 0.35))
        _photo_cache[key] = ImageTk.PhotoImage(im)
    return _photo_cache[key]


def gray_image(text: str, size: int) -> ctk.CTkImage:
    im = _render(text)
    alpha = im.getchannel("A")
    g = im.convert("L").convert("RGBA")
    g.putalpha(alpha.point(lambda a: a * 0.3))
    w, h = g.size
    return ctk.CTkImage(light_image=g, dark_image=g, size=(max(1, int(w * size / h)), size))


# --- Animationen ---------------------------------------------------------------------

_anim_frames: dict = {}


def anim_key(name_or_emoji: str) -> str:
    idx = _index()["anim"]
    n = _norm(name_or_emoji)
    if n in idx:
        return n
    return emoji_name(name_or_emoji)


def anim_available(name_or_emoji: str) -> bool:
    return os.path.exists(_path_anim(anim_key(name_or_emoji)))


def load_anim_frames(name_or_emoji: str, px: int, step: int = 2):
    """Liefert (Liste PIL-Frames, Dauer ms) oder None. Ergebnis wird zwischengespeichert."""
    key = (anim_key(name_or_emoji), px, step)
    if key in _anim_frames:
        return _anim_frames[key]
    path = _path_anim(key[0])
    if not os.path.exists(path):
        return None
    try:
        im = Image.open(path)
        frames = []
        dur = im.info.get("duration", 40) or 40
        for i in range(0, getattr(im, "n_frames", 1), step):
            im.seek(i)
            fr = im.convert("RGBA").resize((px, px), Image.BILINEAR)
            frames.append(fr)
        res = (frames, int(dur * step))
        _anim_frames[key] = res
        return res
    except Exception:
        return None
