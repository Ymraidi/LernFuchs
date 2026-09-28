"""Kivy-Bausteine für die Tablet-Version: Farben, Karten, Knöpfe, 3D-Emojis, Animationen, Sanduhr, Zahlenfeld."""

import io
import json
import math
import os
import time

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Ellipse, Line, Mesh, Rectangle, RoundedRectangle
from kivy.graphics.texture import Texture
from kivy.metrics import dp, sp
from kivy.properties import ListProperty, NumericProperty, StringProperty
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

from lernfuchs import theme as T

APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ASSETS = os.path.join(APP_DIR, "assets")
T.apply("bey")


def C(hex_color, alpha=1.0):
    c = get_color_from_hex(hex_color)
    c[3] = alpha
    return c


# --- Emoji-Bilder -------------------------------------------------------------------

_EMOJI_MAP = None


def _emap():
    global _EMOJI_MAP
    if _EMOJI_MAP is None:
        try:
            with open(os.path.join(ASSETS, "emoji_map.json"), encoding="utf-8") as fh:
                raw = json.load(fh)
        except (OSError, ValueError):
            raw = {}
        _EMOJI_MAP = {k.replace("️", ""): v for k, v in raw.items()}
    return _EMOJI_MAP


def split_emojis(text):
    try:
        import emoji as emj
        found = [e["emoji"] for e in emj.emoji_list(text)]
        if found:
            return found
    except Exception:
        pass
    return [text]


def emoji_src(ch, fallback=True):
    name = _emap().get((ch or "").replace("️", ""))
    if name:
        p = os.path.join(ASSETS, "emoji3d", name + ".png")
        if os.path.exists(p):
            return p
    return emoji_src("⭐", False) if fallback and ch != "⭐" else ""


def has_emoji(ch):
    return bool(emoji_src(ch, False))


class EmojiImg(Image):
    """3D-Emoji als Bild (quadratisch)."""

    def __init__(self, ch, size=48, **kw):
        kw.setdefault("size_hint", (None, None))
        super().__init__(source=emoji_src(ch), size=(dp(size), dp(size)), fit_mode="contain", **kw)


def emoji_row(text, size=48, spacing=6):
    box = BoxLayout(orientation="horizontal", size_hint=(None, None), spacing=dp(spacing), height=dp(size))
    parts = [p for p in split_emojis(text) if has_emoji(p)]
    for p in parts:
        box.add_widget(EmojiImg(p, size))
    box.width = len(parts) * dp(size) + max(0, len(parts) - 1) * dp(spacing)
    return box


class AnimImg(Image):
    """Animiertes 3D-Emoji (ZIP-Bildfolge); sonst Standbild."""

    STILL = {"Party_Popper": "🎉", "Clapping_Hands_Light_Skin_Tone": "👏", "StarStruck": "🤩",
             "Sparkles": "✨", "Glowing_Star": "🌟", "Hundred_Points": "💯", "Smiling_Face_with_Sunglasses": "😎",
             "Thinking_Face": "🤔", "Face_with_Monocle": "🧐", "Hourglass_Done": "⌛", "Collision": "💥",
             "Rocket": "🚀", "Fire": "🔥", "Trophy": "🏆", "Fox": "🦊", "Flexed_Biceps_Light_Skin_Tone": "💪",
             "Brain": "🧠", "Light_Bulb": "💡", "Gem_Stone": "💎"}

    def __init__(self, name, size=64, **kw):
        key = _alnum(name)
        path = ""
        folder = os.path.join(ASSETS, "anim")
        if os.path.isdir(folder):
            for fn in os.listdir(folder):
                if _alnum(fn[:-4]) == key:
                    path = os.path.join(folder, fn)
        kw.setdefault("size_hint", (None, None))
        if path:
            super().__init__(source=path, anim_delay=0.09, anim_loop=0, size=(dp(size), dp(size)),
                             fit_mode="contain", **kw)
        else:
            still = next((v for k, v in self.STILL.items() if _alnum(k) == key), "⭐")
            super().__init__(source=emoji_src(still), size=(dp(size), dp(size)), fit_mode="contain", **kw)


def _alnum(s):
    return "".join(ch for ch in s.lower() if ch.isalnum())


def pil_texture(im):
    """PIL-Bild → Kivy-Textur (für Fotos)."""
    im = im.convert("RGBA")
    tex = Texture.create(size=im.size, colorfmt="rgba")
    from PIL import Image as _PIL
    tex.blit_buffer(im.transpose(_PIL.Transpose.FLIP_TOP_BOTTOM).tobytes(), colorfmt="rgba", bufferfmt="ubyte")
    return tex


# --- Flächen & Knöpfe ------------------------------------------------------------------

class Box(BoxLayout):
    bg = ListProperty([0, 0, 0, 0])
    radius = NumericProperty(dp(18))
    border = ListProperty([0, 0, 0, 0])

    def __init__(self, bg=None, radius=18, border=None, **kw):
        super().__init__(**kw)
        if bg:
            self.bg = C(bg) if isinstance(bg, str) else bg
        if border:
            self.border = C(border)
        self.radius = dp(radius)
        with self.canvas.before:
            self._c = Color(*self.bg)
            self._r = RoundedRectangle(pos=self.pos, size=self.size, radius=[self.radius])
            self._bc = Color(*self.border)
            self._bl = Line(rounded_rectangle=(self.x, self.y, self.width, self.height, self.radius), width=dp(1.3))
        self.bind(pos=self._upd, size=self._upd, bg=self._upd, border=self._upd)

    def _upd(self, *_):
        self._c.rgba = self.bg
        self._r.pos, self._r.size = self.pos, self.size
        self._r.radius = [self.radius]
        self._bc.rgba = self.border
        self._bl.rounded_rectangle = (self.x, self.y, self.width, self.height, self.radius)


# Zeichen, die die Tablet-Schrift (Roboto) nicht enthält → passende Ersatzzeichen
GLYPHS = {"→": "–", "←": "–", "↔": "–", "─": "-", "✔": "", "✘": "", "✓ ": "", "✗ ": "", "○": "?", "⌫": ""}


def clean(text):
    for a, b in GLYPHS.items():
        text = text.replace(a, b)
    return text


class Txt(Label):
    def __init__(self, text="", fs=20, color=None, bold=False, halign="center", wrap=True, **kw):
        super().__init__(text=clean(text), font_size=sp(fs), color=C(color or T.TEXT), bold=bold, halign=halign,
                         valign="middle", **kw)
        self.bind(text=self._clean_text)
        if wrap:
            self.bind(width=lambda *_: setattr(self, "text_size", (self.width, None)))
            self.bind(texture_size=lambda *_: setattr(self, "height", self.texture_size[1]) if self.size_hint_y is None else None)


    def _clean_text(self, *_):
        t = clean(self.text)
        if t != self.text:
            self.text = t


class RButton(ButtonBehavior, Box):
    """Abgerundeter Knopf mit optionalem 3D-Emoji."""

    def __init__(self, text="", on_press=None, bg=None, fg=None, fs=22, icon=None, icon_size=None,
                 radius=16, **kw):
        self._bg_hex = bg or T.PRIMARY
        super().__init__(bg=self._bg_hex, radius=radius, orientation="horizontal", padding=(dp(12), dp(4)),
                         spacing=dp(8), **kw)
        self._cb = on_press
        self.enabled = True
        if icon and has_emoji(icon):
            self.add_widget(EmojiImg(icon, icon_size or fs * 1.3, pos_hint={"center_y": 0.5}))
        if text:
            self.label = Txt(text, fs=fs, color=fg or T.ON_ACCENT, bold=True)
            self.add_widget(self.label)
        else:
            self.label = None

    def set_bg(self, hex_color):
        self._bg_hex = hex_color
        self.bg = C(hex_color)

    def set_fg(self, hex_color):
        if self.label:
            self.label.color = C(hex_color)

    def on_press(self):
        if self.enabled:
            self.bg = C(self._bg_hex, 0.75)

    def on_release(self):
        self.bg = C(self._bg_hex)
        if self.enabled and self._cb:
            self._cb()

    def disable(self, hex_color=None):
        self.enabled = False
        if hex_color:
            self.set_bg(hex_color)


class Progress(Widget):
    value = NumericProperty(0)

    def __init__(self, color=None, **kw):
        super().__init__(**kw)
        self._col = C(color or T.PRIMARY)
        with self.canvas:
            Color(*C(T.TRACK))
            self._bgr = RoundedRectangle(radius=[dp(6)])
            self._fc = Color(*self._col)
            self._fr = RoundedRectangle(radius=[dp(6)])
        self.bind(pos=self._upd, size=self._upd, value=self._upd)

    def _upd(self, *_):
        self._bgr.pos, self._bgr.size = self.pos, self.size
        self._fr.pos = self.pos
        self._fr.size = (max(self.height, self.width * max(0, min(1, self.value))), self.height)

    def set_color(self, hex_color):
        self._fc.rgba = C(hex_color)


# --- Sanduhr ----------------------------------------------------------------------------

class Hourglass(Widget):
    def __init__(self, **kw):
        kw.setdefault("size_hint", (None, None))
        kw.setdefault("size", (dp(60), dp(96)))
        super().__init__(**kw)
        self.total, self.t0, self.before, self.cb, self._ev = 0, None, 0.0, None, None
        self.lbl = Label(font_size=sp(12), color=C(T.MUTED), size_hint=(None, None))
        self.add_widget(self.lbl)
        self.bind(pos=lambda *_: self._draw(), size=lambda *_: self._draw())
        self._draw()

    def start(self, seconds, cb=None):
        self.stop()
        self.total, self.before, self.cb = seconds, 0.0, cb
        if seconds > 0:
            self.t0 = time.monotonic()
            self._ev = Clock.schedule_interval(self._tick, 0.1)
        self._draw()

    def elapsed(self):
        return self.before + ((time.monotonic() - self.t0) if self.t0 else 0)

    def ratio(self):
        return None if self.total <= 0 else min(1.0, self.elapsed() / self.total)

    def pause(self):
        if self.t0:
            self.before += time.monotonic() - self.t0
            self.t0 = None
        if self._ev:
            self._ev.cancel()
            self._ev = None

    def resume(self):
        if self.total > 0 and not self.t0 and self.before < self.total:
            self.t0 = time.monotonic()
            self._ev = Clock.schedule_interval(self._tick, 0.1)

    stop = pause

    def _tick(self, dt):
        self._draw()
        if self.total and self.elapsed() >= self.total:
            self.pause()
            cb, self.cb = self.cb, None
            if cb:
                cb()

    def _draw(self):
        x, y, w, h = self.x, self.y + dp(14), self.width, self.height - dp(14)
        rem = 1.0 if self.total <= 0 else max(0.0, 1 - self.elapsed() / self.total)
        self.canvas.clear()
        top, bot, neck = y + h - dp(8), y + dp(8), y + h / 2
        if top - neck < dp(4):  # noch nicht fertig angeordnet
            return
        l, r, cx = x + dp(8), x + w - dp(8), x + w / 2
        with self.canvas:
            Color(*C(T.GLASS))
            Mesh(vertices=[l, top, 0, 0, r, top, 0, 0, cx, neck, 0, 0], indices=[0, 1, 2], mode="triangles")
            Mesh(vertices=[l, bot, 0, 0, r, bot, 0, 0, cx, neck, 0, 0], indices=[0, 1, 2], mode="triangles")
            sand = T.GOLD if rem > 0.3 else ("#FF9F43" if rem > 0.15 else T.BAD)
            Color(*C(sand))
            if self.total > 0 and rem > 0.01:
                ly = neck + (top - neck - dp(4)) * rem
                half = (r - l) / 2 * (ly - neck) / max(top - neck, 1e-3)
                Mesh(vertices=[cx - half, ly, 0, 0, cx + half, ly, 0, 0, cx, neck, 0, 0], indices=[0, 1, 2],
                     mode="triangles")
            done = 1 - rem if self.total > 0 else 0
            if done > 0.01:
                hy = bot + (neck - bot - dp(6)) * done
                Mesh(vertices=[l + dp(3), bot, 0, 0, r - dp(3), bot, 0, 0, cx, hy, 0, 0], indices=[0, 1, 2],
                     mode="triangles")
            Color(*C("#B07A4E"))
            Rectangle(pos=(x + dp(3), top), size=(w - dp(6), dp(6)))
            Rectangle(pos=(x + dp(3), bot - dp(6)), size=(w - dp(6), dp(6)))
        self.lbl.text = "∞" if self.total <= 0 else f"{max(0, math.ceil(self.total - self.elapsed()))} s"
        self.lbl.texture_update()
        self.lbl.size = self.lbl.texture_size
        self.lbl.pos = (cx - self.lbl.width / 2, self.y)


# --- Zahlenfeld --------------------------------------------------------------------------

class NumPad(GridLayout):
    def __init__(self, target_label, extra="", on_enter=None, **kw):
        super().__init__(cols=3, spacing=dp(8), size_hint=(None, None), **kw)
        self.target = target_label
        keys = ["7", "8", "9", "4", "5", "6", "1", "2", "3", "DEL", "0", extra or ""]
        for k in keys:
            if not k:
                self.add_widget(Widget())
                continue
            self.add_widget(RButton("" if k == "DEL" else k, on_press=lambda k=k: self._press(k), bg=T.NEUTRAL_BTN,
                                    fg=T.TEXT, fs=26, icon="⬅️" if k == "DEL" else None, icon_size=30,
                                    size_hint=(None, None), size=(dp(76), dp(58)), radius=14))
        self.width = dp(76) * 3 + dp(16)
        self.height = dp(58) * 4 + dp(24)

    def _press(self, k):
        if k == "DEL":
            self.target.text = self.target.text[:-1]
        elif len(self.target.text) < 12:
            self.target.text += k


# --- Hinweis-Einblendung -----------------------------------------------------------------

def toast(root, text, anim=None, color=None, seconds=2.2):
    box = Box(bg=color or T.GOLD, radius=22, orientation="horizontal", size_hint=(None, None),
              height=dp(58), padding=(dp(14), dp(6)), spacing=dp(10))
    if anim:
        box.add_widget(AnimImg(anim, 42))
    lbl = Txt(text, fs=19, color="#1D2438", bold=True, wrap=False)
    lbl.texture_update()
    lbl.size_hint = (None, 1)
    lbl.width = lbl.texture_size[0] + dp(10)
    box.add_widget(lbl)
    box.width = lbl.width + (dp(56) if anim else 0) + dp(34)
    box.pos = (root.width / 2 - box.width / 2, root.height)
    root.add_widget(box)
    Animation(y=root.height - box.height - dp(16), d=0.35, t="out_back").start(box)
    Clock.schedule_once(lambda *_: (Animation(opacity=0, d=0.3).start(box),
                                    Clock.schedule_once(lambda *_: root.remove_widget(box), 0.35)), seconds)


def fly_up(root, text, center):
    lbl = Txt(f"[b]{text}[/b]", fs=26, color=T.GOLD, wrap=False, markup=True, size_hint=(None, None))
    lbl.texture_update()
    lbl.size = lbl.texture_size
    lbl.center = center
    root.add_widget(lbl)
    Animation(y=lbl.y + dp(110), opacity=0, d=1.0, t="out_quad").start(lbl)
    Clock.schedule_once(lambda *_: root.remove_widget(lbl), 1.05)


# --- Battle-Kreisel (eigene Grafik, animiert) ----------------------------------------

from kivy.graphics import PopMatrix, PushMatrix, Rotate  # noqa: E402
from kivy.properties import NumericProperty as _Num  # noqa: E402

# (Name, Hauptfarbe, Ringfarbe, Juwel)
MY_BEYS = [("Sturmfalke", "#1EA7FF", "#E8EEF8", "#FFD23F"), ("Feuerdrache", "#FF3B3B", "#FFB020", "#FFE08A"),
           ("Eiswolf", "#7FE3FF", "#3A6CFF", "#FFFFFF"), ("Donnerlöwe", "#FFD23F", "#FF7A1A", "#FF3B3B"),
           ("Nebelkobra", "#9B5CFF", "#23E5A0", "#E8EEF8"), ("Titanbär", "#8C96AA", "#3B4660", "#FF3B3B")]


class BeyTop(Widget):
    """Selbst gezeichneter Battle-Kreisel mit Energie-Ring. speed = Grad pro Sekunde."""
    speed = _Num(540)

    def __init__(self, size=120, bey=0, glow=True, **kw):
        kw.setdefault("size_hint", (None, None))
        super().__init__(size=(dp(size), dp(size)), **kw)
        self.name_, self.c1, self.c2, self.c3 = MY_BEYS[bey % len(MY_BEYS)]
        self.glow = glow
        self._t = 0.0
        self.bind(pos=lambda *_: self._build(), size=lambda *_: self._build())
        self._build()
        self._ev = Clock.schedule_interval(self._tick, 1 / 40)

    def _build(self):
        self.canvas.clear()
        cx, cy = self.center
        r = min(self.width, self.height) / 2
        with self.canvas:
            self._glow_c = Color(*C(T.ELECTRIC if hasattr(T, "ELECTRIC") else "#1EA7FF", 0.18))
            self._glow = Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))
            PushMatrix()
            self._rot = Rotate(angle=0, origin=(cx, cy))
            # drei Klingen (Angriffsring)
            Color(*C(self.c1))
            for i in range(3):
                base = i * 120
                verts, idx = [], []
                steps = 10
                for s in range(steps + 1):
                    a = math.radians(base + s * 80 / steps)
                    ro = r * (0.95 - 0.12 * (s / steps) ** 2)
                    ri = r * 0.52
                    verts += [cx + ro * math.cos(a), cy + ro * math.sin(a), 0, 0,
                              cx + ri * math.cos(a), cy + ri * math.sin(a), 0, 0]
                    idx += [2 * s, 2 * s + 1]
                Mesh(vertices=verts, indices=idx, mode="triangle_strip")
            # Metallring
            Color(*C(self.c2))
            Line(circle=(cx, cy, r * 0.62), width=max(1.5, r * 0.06))
            Color(*C("#9AA7C0"))
            Ellipse(pos=(cx - r * 0.5, cy - r * 0.5), size=(r, r))
            Color(*C("#5B6680"))
            for i in range(6):
                a = math.radians(i * 60 + 30)
                Line(points=[cx + r * 0.22 * math.cos(a), cy + r * 0.22 * math.sin(a),
                             cx + r * 0.48 * math.cos(a), cy + r * 0.48 * math.sin(a)], width=max(1, r * 0.025))
            # Energie-Kern
            Color(*C(self.c1))
            Ellipse(pos=(cx - r * 0.24, cy - r * 0.24), size=(r * 0.48, r * 0.48))
            Color(*C(self.c3))
            Mesh(vertices=[cx, cy + r * 0.17, 0, 0, cx - r * 0.15, cy - r * 0.1, 0, 0, cx + r * 0.15, cy - r * 0.1, 0, 0],
                 indices=[0, 1, 2], mode="triangles")
            PopMatrix()

    def _tick(self, dt):
        if not self.get_root_window():
            return
        self._t += dt
        self._rot.angle = (self._rot.angle - self.speed * dt) % 360
        if self.glow:
            pulse = 0.14 + 0.1 * (0.5 + 0.5 * math.sin(self._t * 5))
            self._glow_c.a = pulse * min(1.5, self.speed / 540)

    def boost(self, to=1800, back=540, d=0.25, hold=0.8):
        Animation(speed=to, d=d).start(self)
        Clock.schedule_once(lambda *_: Animation(speed=back, d=0.8).start(self), d + hold)

    def wobble(self):
        a = Animation(speed=120, d=0.3) + Animation(speed=540, d=1.0)
        a.start(self)

    def on_parent(self, *_):
        if self.parent is None and self._ev:
            self._ev.cancel()
