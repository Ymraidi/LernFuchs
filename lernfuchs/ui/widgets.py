"""Wiederverwendbare Bausteine: Sanduhr, Karten, Knöpfe, Konfetti, Hinweise."""

import math
from functools import lru_cache
import random
import threading
import time
import tkinter as tk

import customtkinter as ctk

from .. import theme as T
from ..emoji import emoji_image, emoji_photo
from PIL import ImageTk


def scaling(widget) -> float:
    try:
        return ctk.ScalingTracker.get_widget_scaling(widget)
    except Exception:
        return 1.0


def darker(hex_color: str, factor: float = 0.85) -> str:
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * factor), int(g * factor), int(b * factor))


class Card(ctk.CTkFrame):
    def __init__(self, master, color=None, radius=24, border=True, **kw):
        color = color or T.CARD
        super().__init__(master, fg_color=color, corner_radius=radius,
                         border_width=2 if border else 0, border_color=T.CARD_BORDER, **kw)


def big_button(master, text, command, color=None, hover=None, emoji=None, size=22, height=64,
               text_color=None, width=0, radius=20, emoji_size=None, **kw):
    color = color or T.PRIMARY
    img = emoji_image(emoji, emoji_size or int(size * 1.4)) if emoji else None
    return ctk.CTkButton(master, text=text, command=command, fg_color=color, hover_color=hover or darker(color),
                         text_color=text_color or T.ON_ACCENT, font=T.f(size), height=height, width=width, corner_radius=radius,
                         image=img, compound="left", **kw)


def soft_button(master, text, command, size=18, height=46, emoji=None, **kw):
    img = emoji_image(emoji, int(size * 1.3)) if emoji else None
    return ctk.CTkButton(master, text=text, command=command, fg_color=T.NEUTRAL_BTN, hover_color=T.NEUTRAL_HOVER,
                         text_color=T.TEXT, font=T.f(size), height=height, corner_radius=16, image=img,
                         compound="left", **kw)


def emoji_label(master, e: str, size: int, **kw):
    return ctk.CTkLabel(master, text="", image=emoji_image(e, size), **kw)


class Hourglass(tk.Canvas):
    """Animierte Sanduhr. start(sekunden, bei_ablauf) – pause() – resume() – stop()."""

    W, H = 74, 118

    def __init__(self, master, bg=None):
        bg = bg or T.BG
        self.s = scaling(master)
        super().__init__(master, width=int(self.W * self.s), height=int(self.H * self.s), bg=bg,
                         highlightthickness=0)
        self.total = 0
        self.elapsed_before = 0.0
        self.t0 = None
        self.on_timeout = None
        self._job = None
        self._draw(1.0, False)

    # Steuerung ---------------------------------------------------------------
    def start(self, seconds: float, on_timeout=None):
        self.stop()
        self.total = seconds
        self.elapsed_before = 0.0
        self.on_timeout = on_timeout
        if seconds <= 0:
            self._draw(1.0, False, idle=True)
            return
        self.t0 = time.monotonic()
        self._tick()

    def elapsed(self) -> float:
        run = (time.monotonic() - self.t0) if self.t0 is not None else 0
        return self.elapsed_before + run

    def ratio(self):
        return None if self.total <= 0 else min(1.0, self.elapsed() / self.total)

    def pause(self):
        if self.t0 is not None:
            self.elapsed_before += time.monotonic() - self.t0
            self.t0 = None
        if self._job:
            self.after_cancel(self._job)
            self._job = None

    def resume(self):
        if self.total > 0 and self.t0 is None and self.elapsed_before < self.total:
            self.t0 = time.monotonic()
            self._tick()

    def stop(self):
        self.pause()

    def destroy(self):
        self.stop()
        super().destroy()

    def _tick(self):
        el = self.elapsed()
        rem = max(0.0, 1 - el / self.total)
        self._draw(rem, True)
        if rem <= 0:
            self.pause()
            cb, self.on_timeout = self.on_timeout, None
            if cb:
                cb()
            return
        self._job = self.after(80, self._tick)

    # Zeichnen ----------------------------------------------------------------
    def _draw(self, rem: float, running: bool, idle=False):
        s = self.s
        self.delete("all")
        w, h = self.W * s, self.H * s
        top, bot, neck = 12 * s, 96 * s, 54 * s
        left, right, cx = 12 * s, w - 12 * s, w / 2
        nw = 3 * s
        wood = "#B07A4E"
        # Glas
        glass = [left, top, right, top, cx + nw, neck, right, bot, left, bot, cx - nw, neck]
        self.create_polygon(glass, fill=T.GLASS, outline=T.GLASS_LINE, width=2 * s, smooth=False)
        if not idle:
            if rem > 0.3:
                sand = T.GOLD
            elif rem > 0.15:
                sand = "#FF9F43"
            else:
                sand = T.BAD if int(time.monotonic() * 4) % 2 == 0 else "#FF8A8E"

            def xw(y, y0, y1, w0, w1):
                t = (y - y0) / (y1 - y0)
                return w0 + (w1 - w0) * t
            # oberer Sand
            if rem > 0.001:
                ly = neck - (neck - top - 4 * s) * rem
                half = xw(ly, top, neck, (right - left) / 2, nw) - 2 * s
                self.create_polygon(cx - half, ly, cx + half, ly, cx + nw, neck - 1, cx - nw, neck - 1,
                                    fill=sand, outline="")
            # unterer Sandhügel
            done = 1 - rem
            if done > 0.001:
                hy = bot - (bot - neck - 10 * s) * done
                half = (right - left) / 2 - 3 * s
                self.create_polygon(cx - half, bot - 1, cx + half, bot - 1, cx + half * 0.7, hy + 6 * s,
                                    cx, hy, cx - half * 0.7, hy + 6 * s, fill=sand, outline="", smooth=True)
            if running and rem > 0.001:
                self.create_line(cx, neck, cx, bot - 3 * s - (bot - neck - 10 * s) * done, fill=sand,
                                 width=2 * s, dash=(3, 2))
        # Holzrahmen
        self.create_rectangle(4 * s, 4 * s, w - 4 * s, top, fill=wood, outline="")
        self.create_rectangle(4 * s, bot, w - 4 * s, bot + 8 * s, fill=wood, outline="")
        if self.total > 0 and not idle:
            left_s = max(0, math.ceil(self.total - self.elapsed()))
            self.create_text(cx, h - 7 * s, text=f"{left_s} s", fill=T.MUTED, font=(T.FONT, int(11), "bold"))
        elif idle:
            self.create_text(cx, h - 7 * s, text="∞", fill=T.MUTED, font=(T.FONT, 12, "bold"))


class Confetti(tk.Canvas):
    """Konfetti-Regen als Belohnung (läuft ein paar Sekunden und räumt sich auf)."""

    COLORS = ["#FF6B6B", "#4D96FF", "#2EB872", "#FFC93C", "#9B5DE5", "#FF8C42"]

    def __init__(self, master, width, height, bg=None, duration=2.8):
        bg = bg or T.BG
        super().__init__(master, width=width, height=height, bg=bg, highlightthickness=0)
        self.pieces = []
        for _ in range(90):
            x = random.uniform(0, width)
            y = random.uniform(-height, 0)
            size = random.uniform(6, 12)
            color = random.choice(self.COLORS)
            pid = self.create_rectangle(x, y, x + size, y + size * 0.6, fill=color, outline="")
            self.pieces.append([pid, random.uniform(3, 8), random.uniform(-1.5, 1.5)])
        self.end = time.monotonic() + duration
        self._step()

    def _step(self):
        if not self.winfo_exists():
            return
        for pid, vy, vx in self.pieces:
            self.move(pid, vx, vy)
        if time.monotonic() < self.end:
            self.after(30, self._step)


class Toast:
    """Kurzer Hinweis oben im Fenster (z. B. 'Neue Stufe!')."""

    def __init__(self, root, text, emoji=None, color=None, text_color=None, ms=2200, anim=None):
        color = color or T.GOLD
        text_color = text_color or "#1D2438"
        frame = ctk.CTkFrame(root, fg_color=color, corner_radius=22)
        if anim:
            AnimEmoji(frame, anim, 40, still=emoji).pack(side="left", padx=(16, 4), pady=6)
        elif emoji:
            emoji_label(frame, emoji, 36, fg_color="transparent").pack(side="left", padx=(16, 4), pady=8)
        ctk.CTkLabel(frame, text=text, font=T.f(22), text_color=text_color).pack(side="left", padx=(4, 20), pady=8)
        frame.place(relx=0.5, y=18, anchor="n")
        frame.lift()
        root.after(ms, frame.destroy)


class NumPad(ctk.CTkFrame):
    """Zahlenfeld zum Tippen mit der Maus. Kann per bind() für neue Eingabefelder wiederverwendet werden."""

    def __init__(self, master, entry, on_enter=None, comma=False, extra=None):
        super().__init__(master, fg_color="transparent")
        self.entry = entry
        keys = ["7", "8", "9", "4", "5", "6", "1", "2", "3", "⌫", "0"]
        for i, k in enumerate(keys):
            ctk.CTkButton(self, text=k, width=64, height=52, corner_radius=14, font=T.f(24),
                          fg_color=T.NEUTRAL_BTN, hover_color=T.NEUTRAL_HOVER, text_color=T.TEXT,
                          command=lambda k=k: self._press(k)).grid(row=i // 3, column=i % 3, padx=4, pady=4)
        self.extra_btn = ctk.CTkButton(self, text="", width=64, height=52, corner_radius=14, font=T.f(24),
                                       fg_color=T.NEUTRAL_BTN, hover_color=T.NEUTRAL_HOVER, text_color=T.TEXT,
                                       command=lambda: self._press(self.extra_btn.cget("text")))
        self.bind_entry(entry, "," if comma else (extra or ""))

    def bind_entry(self, entry, extra=""):
        self.entry = entry
        if extra:
            self.extra_btn.configure(text=extra)
            self.extra_btn.grid(row=3, column=2, padx=4, pady=4)
        else:
            self.extra_btn.grid_remove()

    def _press(self, k):
        if self.entry is None or not self.entry.winfo_exists() or str(self.entry.cget("state")) == "disabled":
            return
        if k == "⌫":
            cur = self.entry.get()
            self.entry.delete(0, "end")
            self.entry.insert(0, cur[:-1])
        else:
            self.entry.insert("end", k)
        self.entry.focus_set()


class LetterPad(ctk.CTkFrame):
    """Umlaut-Tasten für die Texteingabe."""

    def __init__(self, master, entry):
        super().__init__(master, fg_color="transparent")
        self.entry = entry
        for i, k in enumerate(["ä", "ö", "ü", "ß", "Ä", "Ö", "Ü"]):
            ctk.CTkButton(self, text=k, width=48, height=44, corner_radius=12, font=T.f(20),
                          fg_color=T.NEUTRAL_BTN, hover_color=T.NEUTRAL_HOVER, text_color=T.TEXT,
                          command=lambda k=k: self._press(k)).grid(row=0, column=i, padx=3)

    def bind_entry(self, entry, extra=""):
        self.entry = entry

    def _press(self, k):
        if self.entry is not None and self.entry.winfo_exists():
            self.entry.insert("insert", k)
            self.entry.focus_set()


class Pads:
    """Hält Zahlen- und Umlautfeld für eine ganze Runde – spart den Neuaufbau bei jeder Aufgabe."""

    def __init__(self, parent):
        self.parent = parent
        self._num = None
        self._let = None

    def show(self, container, entry, numeric=True, extra=""):
        self.hide()
        if numeric:
            if self._num is None:
                self._num = NumPad(self.parent, entry)
            pad = self._num
        else:
            if self._let is None:
                self._let = LetterPad(self.parent, entry)
            pad = self._let
        pad.bind_entry(entry, extra)
        pad.pack(in_=container)
        pad.lift()

    def hide(self):
        for p in (self._num, self._let):
            if p is not None and p.winfo_exists():
                p.pack_forget()


# --- Animationen -----------------------------------------------------------------

def ease_out(t: float) -> float:
    return 1 - (1 - t) ** 3


def tween(widget, duration_ms, step_fn, done=None, fps=60):
    """Ruft step_fn(fortschritt 0..1, geglättet) über duration_ms auf."""
    start = time.monotonic()

    def tick():
        if not widget.winfo_exists():
            return
        t = min(1.0, (time.monotonic() - start) * 1000 / duration_ms)
        step_fn(ease_out(t))
        if t < 1.0:
            widget.after(int(1000 / fps), tick)
        elif done:
            done()
    tick()


def slide_in(widget, dx=80, duration=220):
    """Neue Aufgabe gleitet von rechts herein (place-basiert)."""
    def step(p):
        widget.place_configure(x=int(dx * (1 - p)))
    tween(widget, duration, step)


def shake(widget, amplitude=14, duration=380):
    """Kopfschütteln bei falscher Antwort."""
    def step(p):
        off = int(amplitude * (1 - p) * math.sin(p * math.pi * 6))
        widget.place_configure(x=off)
    tween(widget, duration, step, done=lambda: widget.winfo_exists() and widget.place_configure(x=0))


def count_up(label, start, end, fmt="{}", duration=600):
    def step(p):
        label.configure(text=fmt.format(int(round(start + (end - start) * p))))
    tween(label, duration, step)


def fly_up(root, text, x, y, color=None, duration=900):
    """„+2 XP“ steigt nach oben und verblasst."""
    lbl = ctk.CTkLabel(root, text=text, font=T.f(26), text_color=color or T.GOLD, fg_color="transparent")
    lbl.place(x=x, y=y, anchor="center")

    def step(p):
        lbl.place_configure(y=int(y - 90 * p))
        if p > 0.7:
            lbl.configure(text_color=T.MUTED)
    tween(lbl, duration, step, done=lbl.destroy)


def resolve_bg(widget) -> str:
    """Tatsächliche Hintergrundfarbe (CTk-„transparent“ wird bis zum Elternelement aufgelöst)."""
    w = widget
    while w is not None:
        try:
            col = w.cget("fg_color")
        except Exception:
            try:
                return w.cget("bg")
            except Exception:
                return T.BG
        if isinstance(col, (list, tuple)):
            col = col[1] if T.CURRENT == "modern" else col[0]
        if col and col != "transparent":
            return col
        w = w.master
    return T.BG


class AnimEmoji(tk.Label):
    """Animiertes 3D-Emoji. Leichtgewichtig (reines Tk-Label, vorberechnete Bilder); pausiert, wenn unsichtbar."""

    def __init__(self, master, emoji_or_name, size, loop=True, still=None, **kw):
        from ..emoji import anim_available
        self._px = int(size * scaling(master))
        super().__init__(master, bd=0, highlightthickness=0, bg=resolve_bg(master))
        self._still = emoji_photo(still or emoji_or_name, self._px)
        self.configure(image=self._still)
        self._loop, self._job, self._imgs, self._i, self._dur = loop, None, [], 0, 80
        if anim_available(emoji_or_name):
            box = []
            threading.Thread(target=lambda: box.append(_decode(emoji_or_name, self._px)), daemon=True).start()
            self._wait(box)

    def _wait(self, box):
        if not self.winfo_exists():
            return
        if not box:
            self._job = self.after(40, lambda: self._wait(box))
            return
        res = box[0]
        if not res:
            return
        frames, self._dur = res
        self._frames = frames
        self._step()

    def _step(self):
        if not self.winfo_exists():
            return
        if not self.winfo_viewable():  # verdeckt → kaum Rechenzeit verbrauchen
            self._job = self.after(400, self._step)
            return
        if self._i >= len(self._imgs):  # Bild erst bei Bedarf erzeugen (verteilt die Arbeit)
            self._imgs.append(ImageTk.PhotoImage(self._frames[self._i]))
        self.configure(image=self._imgs[self._i])
        self._i += 1
        if self._i >= len(self._frames):
            if not self._loop:
                return
            self._i = 0
        self._job = self.after(self._dur, self._step)

    def destroy(self):
        if self._job:
            try:
                self.after_cancel(self._job)
            except Exception:
                pass
        super().destroy()


def _decode(name, px):
    from ..emoji import load_anim_frames
    return load_anim_frames(name, px, step=3)


def level_dots(master, level: int, color: str, maximum=8, size=11):
    """Stufen als EIN Bild (schnell): 1–5 in Fachfarbe, 6–8 (Profi) in Gold."""
    return ctk.CTkLabel(master, text="", image=_dots_image(level, color, T.GOLD, T.DOT_OFF, maximum, size),
                        fg_color="transparent")


@lru_cache(maxsize=256)
def _dots_image(level, color, gold, off, maximum, size):
    from PIL import Image, ImageDraw
    k = 3
    gap, extra = 4, 6
    w = maximum * size + (maximum - 1) * gap + extra
    im = Image.new("RGBA", (w * k, size * k), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    x = 0
    for i in range(maximum):
        if i == 5:
            x += extra
        col = (gold if i >= 5 else color) if i < level else off
        d.ellipse((x * k, 0, (x + size) * k - 1, size * k - 1), fill=col)
        x += size + gap
    return ctk.CTkImage(im, im, size=(w, size))


# Animierte 3D-Emojis (Name im Animations-Set → Standbild als Ersatz)
ANIM_STILL = {
    "Party Popper": "🎉", "Clapping Hands Light Skin Tone": "👏", "Star-Struck": "🤩", "Sparkles": "✨",
    "Glowing Star": "🌟", "Hundred Points": "💯", "Smiling Face with Sunglasses": "😎", "Thinking Face": "🤔",
    "Face with Monocle": "🧐", "Hourglass Done": "⌛", "Collision": "💥", "Rocket": "🚀", "Fire": "🔥",
    "Trophy": "🏆", "Fox": "🦊", "Flexed Biceps Light Skin Tone": "💪", "Brain": "🧠", "High Voltage": "⚡",
    "Light Bulb": "💡", "Crown": "👑", "Confetti Ball": "🎊", "Gem Stone": "💎", "1st Place Medal": "🥇",
    "Nerd Face": "🤓", "Magnifying Glass Tilted Left": "🔍", "Fireworks": "🎆", "Direct Hit": "🎯",
}
CORRECT_ANIMS = ["Party Popper", "Clapping Hands Light Skin Tone", "Star-Struck", "Sparkles", "Glowing Star",
                 "Hundred Points", "Smiling Face with Sunglasses", "Gem Stone"]
WRONG_ANIMS = ["Thinking Face", "Face with Monocle", "Light Bulb"]


def anim_emoji(master, name, size, loop=True):
    return AnimEmoji(master, name, size, loop=loop, still=ANIM_STILL.get(name, "⭐"))
