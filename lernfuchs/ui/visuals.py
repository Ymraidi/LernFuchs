"""Zeichnet die Bild-Hilfen zu Aufgaben: Uhr, Münzen, Zahlenmauer, Lineal, Formen, Emojis …"""

import math
import random
import tkinter as tk

import customtkinter as ctk

from .. import theme as T
from ..emoji import emoji_image, emoji_photo
from .widgets import emoji_label, scaling


def render(master, visual: dict, bg=None, on_replay=None):
    bg = bg or T.CARD
    if not visual:
        return None
    kind = visual.get("kind")
    fn = {
        "emoji": _emoji, "emoji_row": _emoji_row, "emoji_groups": _emoji_groups, "emoji_array": _emoji_array,
        "emoji_grid": _emoji_grid, "pattern": _pattern, "clock": _clock, "coins": _coins, "wall": _wall,
        "ruler": _ruler, "shape": _shape, "shapes": _shapes, "column": _column, "rect": _rect, "text": _text,
        "listen": _listen, "equations": _equations, "numgrid": _numgrid, "code": _code,
    }.get(kind)
    if fn is None:
        return None
    if kind == "listen":
        return fn(master, visual, bg, on_replay)
    return fn(master, visual, bg)


# --- Emojis ------------------------------------------------------------------

def _emoji(master, v, bg):
    if not v.get("e"):
        return None
    return emoji_label(master, v["e"], 96, fg_color="transparent")


def _emoji_row(master, v, bg):
    items = [e for e in v.get("items", []) if e]
    if not items:
        return None
    f = ctk.CTkFrame(master, fg_color="transparent")
    for e in items:
        emoji_label(f, e, 64, fg_color="transparent").pack(side="left", padx=8)
    return f


def _emoji_groups(master, v, bg):
    groups = v["groups"]
    total = sum(n for _, n in groups)
    size = 46 if total <= 8 else 36 if total <= 14 else 28
    f = ctk.CTkFrame(master, fg_color="transparent")
    for gi, (e, n) in enumerate(groups):
        if gi:
            ctk.CTkLabel(f, text=v.get("sep", "+"), font=T.f(40), text_color=T.MUTED).pack(side="left", padx=10)
        box = ctk.CTkFrame(f, fg_color=T.SURFACE, corner_radius=16)
        box.pack(side="left", padx=4)
        for i in range(n):
            emoji_label(box, e, size, fg_color="transparent").grid(row=i // 5, column=i % 5, padx=2, pady=2)
    return f


def _canvas_grid(master, items, cols, px, bg, gap=6):
    s = scaling(master)
    p = int(px * s)
    g = int(gap * s)
    rows = math.ceil(len(items) / cols)
    c = tk.Canvas(master, width=cols * (p + g) + g, height=rows * (p + g) + g, bg=bg, highlightthickness=0)
    c._imgs = []
    for i, e in enumerate(items):
        r, col = divmod(i, cols)
        img = emoji_photo(e, p)
        c._imgs.append(img)
        c.create_image(g + col * (p + g) + p // 2, g + r * (p + g) + p // 2, image=img)
    return c


def _emoji_array(master, v, bg):
    items = [v["emoji"]] * (v["rows"] * v["cols"])
    px = 40 if v["rows"] * v["cols"] <= 24 else 30
    return _canvas_grid(master, items, v["cols"], px, bg)


def _emoji_grid(master, v, bg):
    n = len(v["items"])
    px = 44 if n <= 20 else 38 if n <= 30 else 32
    return _canvas_grid(master, v["items"], v.get("cols", 6), px, bg, gap=8)


def _pattern(master, v, bg):
    f = ctk.CTkFrame(master, fg_color="transparent")
    for e in v["seq"]:
        if e == "?":
            ctk.CTkLabel(f, text="?", width=56, height=56, corner_radius=14, fg_color=T.GOLD_LIGHT,
                         font=T.f(32), text_color=T.PRIMARY).pack(side="left", padx=4)
        else:
            emoji_label(f, e, 48, fg_color="transparent").pack(side="left", padx=4)
    return f


# --- Uhr ---------------------------------------------------------------------

def _clock(master, v, bg):
    s = scaling(master)
    size = int(230 * s)
    c = tk.Canvas(master, width=size, height=size, bg=bg, highlightthickness=0)
    cx = cy = size / 2
    r = size / 2 - 8 * s
    c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=T.CLOCK_FACE, outline=T.PRIMARY, width=7 * s)
    for i in range(60):
        a = math.radians(i * 6 - 90)
        inner = r - (14 if i % 5 == 0 else 7) * s
        c.create_line(cx + inner * math.cos(a), cy + inner * math.sin(a), cx + (r - 4 * s) * math.cos(a),
                      cy + (r - 4 * s) * math.sin(a), width=(3 if i % 5 == 0 else 1) * s, fill=T.CLOCK_TEXT)
    for n in range(1, 13):
        a = math.radians(n * 30 - 90)
        rr = r - 32 * s
        c.create_text(cx + rr * math.cos(a), cy + rr * math.sin(a), text=str(n), font=(T.FONT, 16, "bold"),
                      fill=T.CLOCK_TEXT)
    h, m = v["h"] % 12, v["m"]
    ah = math.radians((h + m / 60) * 30 - 90)
    am = math.radians(m * 6 - 90)
    c.create_line(cx, cy, cx + r * 0.5 * math.cos(ah), cy + r * 0.5 * math.sin(ah), width=10 * s,
                  fill="#E63946", capstyle="round")
    c.create_line(cx, cy, cx + r * 0.8 * math.cos(am), cy + r * 0.8 * math.sin(am), width=6 * s,
                  fill="#1D6FE0", capstyle="round")
    c.create_oval(cx - 8 * s, cy - 8 * s, cx + 8 * s, cy + 8 * s, fill=T.CLOCK_TEXT, outline="")
    return c


# --- Geld --------------------------------------------------------------------

def _coins(master, v, bg):
    s = scaling(master)
    vals = v["values"]
    pos, x, y, row_h = [], 10 * s, 10 * s, 0
    maxw = 640 * s
    for val in vals:
        w, h = ((150, 78) if val >= 500 else (2 * _coin_r(val), 2 * _coin_r(val)))
        w, h = w * s, h * s
        if x + w > maxw:
            x, y = 10 * s, y + row_h + 10 * s
            row_h = 0
        pos.append((val, x, y, w, h))
        x += w + 12 * s
        row_h = max(row_h, h)
    width = max(p[1] + p[3] for p in pos) + 10 * s
    height = y + row_h + 10 * s
    c = tk.Canvas(master, width=width, height=height, bg=bg, highlightthickness=0)
    for val, x, y, w, h in pos:
        if val >= 500:
            col = {500: "#A9B7A4", 1000: "#E58A7A", 2000: "#7EA6E0", 5000: "#F2A65A"}.get(val, "#CCCCCC")
            c.create_rectangle(x, y, x + w, y + h, fill=col, outline=_dark(col), width=2 * s)
            c.create_rectangle(x + 8 * s, y + 8 * s, x + w - 8 * s, y + h - 8 * s, outline="white", width=1)
            c.create_text(x + w / 2, y + h / 2, text=f"{val // 100} €", font=(T.FONT, 20, "bold"), fill="white")
            continue
        r = w / 2
        cx, cy = x + r, y + r
        if val in (100, 200):
            outer, inner = ("#E3B341", "#C9CDD2") if val == 100 else ("#C9CDD2", "#E3B341")
            c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=outer, outline=_dark(outer), width=2)
            c.create_oval(cx - r * 0.68, cy - r * 0.68, cx + r * 0.68, cy + r * 0.68, fill=inner, outline="")
            label = f"{val // 100} €"
        else:
            col = "#C8703C" if val <= 5 else "#E3B341"
            c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=col, outline=_dark(col), width=2)
            c.create_oval(cx - r * 0.82, cy - r * 0.82, cx + r * 0.82, cy + r * 0.82, outline=_dark(col, 0.92))
            label = f"{val} ct"
        c.create_text(cx, cy, text=label, font=(T.FONT, 13 if val < 10 else 14, "bold"), fill=T.TEXT)
    return c


def _coin_r(val):
    return {1: 26, 2: 29, 5: 32, 10: 31, 20: 34, 50: 37, 100: 36, 200: 40}.get(val, 30)


def _dark(hx, f=0.75):
    h = hx.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


# --- Zahlenmauer -------------------------------------------------------------

def _wall(master, v, bg):
    f = ctk.CTkFrame(master, fg_color="transparent")
    rows = v["rows"]
    maxlen = max(len(str(x)) for row in rows for x in row if x is not None)
    w = max(84, 22 * maxlen + 30)
    for r_i, row in enumerate(reversed(rows)):
        line = ctk.CTkFrame(f, fg_color="transparent")
        line.pack(pady=2)
        for val in row:
            hidden = val is None
            ctk.CTkLabel(line, text="?" if hidden else str(val), width=w, height=48, corner_radius=8,
                         fg_color=T.GOLD if hidden else "#F4A988", text_color="#1D2438" if hidden else "white",
                         font=T.f(24)).pack(side="left", padx=2)
    return f


# --- Lineal ------------------------------------------------------------------

def _ruler(master, v, bg):
    s = scaling(master)
    cm = 38 * s
    L = v["length"]
    x0, y_pen = 24 * s, 34 * s
    width = int(x0 * 2 + 13 * cm)
    c = tk.Canvas(master, width=width, height=int(130 * s), bg=bg, highlightthickness=0)
    # Stift
    body_end = x0 + (L - 0.6) * cm if L > 1 else x0 + L * cm * 0.6
    c.create_rectangle(x0, y_pen - 11 * s, body_end, y_pen + 11 * s, fill="#FFC93C", outline="#D9A21B", width=2)
    c.create_rectangle(x0, y_pen - 11 * s, x0 + 10 * s, y_pen + 11 * s, fill="#FF8FA3", outline="")
    c.create_polygon(body_end, y_pen - 11 * s, x0 + L * cm, y_pen, body_end, y_pen + 11 * s, fill="#F5D7B0",
                     outline="#D9A21B")
    c.create_line(x0, y_pen + 16 * s, x0, 62 * s, dash=(3, 3), fill=T.MUTED)
    c.create_line(x0 + L * cm, y_pen + 4 * s, x0 + L * cm, 62 * s, dash=(3, 3), fill=T.MUTED)
    # Lineal
    top = 62 * s
    c.create_rectangle(x0 - 12 * s, top, x0 + 12.5 * cm, top + 58 * s, fill=T.GLASS, outline=T.GLASS_LINE, width=2)
    for mm in range(0, 125):
        x = x0 + mm * cm / 10
        ln = 20 if mm % 10 == 0 else 13 if mm % 5 == 0 else 7
        c.create_line(x, top, x, top + ln * s, fill=T.TEXT)
        if mm % 10 == 0:
            c.create_text(x, top + 34 * s, text=str(mm // 10), font=(T.FONT, 12, "bold"), fill=T.TEXT)
    c.create_text(x0 + 12.2 * cm, top + 48 * s, text="cm", font=(T.FONT, 10), fill=T.MUTED)
    return c


# --- Formen ------------------------------------------------------------------

SHAPE_COLORS = ["#FF6B6B", "#4D96FF", "#2EB872", "#FFC93C", "#9B5DE5", "#FF8C42"]


def _draw_shape(c, name, cx, cy, r, color, s):
    if name == "Kreis":
        c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=color, outline=_dark(color), width=3 * s)
    elif name == "Quadrat":
        c.create_rectangle(cx - r * 0.85, cy - r * 0.85, cx + r * 0.85, cy + r * 0.85, fill=color,
                           outline=_dark(color), width=3 * s)
    elif name == "Rechteck":
        c.create_rectangle(cx - r * 1.2, cy - r * 0.6, cx + r * 1.2, cy + r * 0.6, fill=color,
                           outline=_dark(color), width=3 * s)
    else:
        n = {"Dreieck": 3, "Fünfeck": 5, "Sechseck": 6}[name]
        pts = []
        for i in range(n):
            a = math.radians(-90 + i * 360 / n)
            pts += [cx + r * math.cos(a), cy + r * math.sin(a) + (r * 0.15 if n == 3 else 0)]
        c.create_polygon(pts, fill=color, outline=_dark(color), width=3 * s)


def _shape(master, v, bg):
    s = scaling(master)
    size = int(200 * s)
    c = tk.Canvas(master, width=size + 80 * s, height=size, bg=bg, highlightthickness=0)
    _draw_shape(c, v["name"], (size + 80 * s) / 2, size / 2, 80 * s, random.choice(SHAPE_COLORS), s)
    return c


def _shapes(master, v, bg):
    s = scaling(master)
    lst = v["list"]
    cols = 8 if len(lst) > 12 else 6
    cell = 70 * s
    rows = math.ceil(len(lst) / cols)
    c = tk.Canvas(master, width=cols * cell + 10 * s, height=rows * cell + 10 * s, bg=bg, highlightthickness=0)
    for i, name in enumerate(lst):
        r, col = divmod(i, cols)
        cx = 5 * s + col * cell + cell / 2 + random.uniform(-5, 5) * s
        cy = 5 * s + r * cell + cell / 2 + random.uniform(-5, 5) * s
        _draw_shape(c, name, cx, cy, 24 * s, random.choice(SHAPE_COLORS), s)
    return c


def _rect(master, v, bg):
    s = scaling(master)
    cell = 36 * s
    w, h = v["w"], v["h"]
    pad = 50 * s
    c = tk.Canvas(master, width=w * cell + 2 * pad, height=h * cell + 2 * pad, bg=bg, highlightthickness=0)
    x0, y0 = pad, pad
    c.create_rectangle(x0, y0, x0 + w * cell, y0 + h * cell, fill=T.SUBJECTS["mathe"][1], outline=T.SUBJECTS["mathe"][0], width=4 * s)
    if v["mode"] == "flaeche":
        for i in range(1, w):
            c.create_line(x0 + i * cell, y0, x0 + i * cell, y0 + h * cell, fill=T.GLASS_LINE)
        for j in range(1, h):
            c.create_line(x0, y0 + j * cell, x0 + w * cell, y0 + j * cell, fill=T.GLASS_LINE)
    else:
        c.create_text(x0 + w * cell / 2, y0 - 18 * s, text=f"{w} cm", font=(T.FONT, 16, "bold"), fill=T.TEXT)
        c.create_text(x0 + w * cell + 30 * s, y0 + h * cell / 2, text=f"{h} cm", font=(T.FONT, 16, "bold"),
                      fill=T.CLOCK_TEXT)
    return c


def _column(master, v, bg):
    lines = v["lines"]
    width = max(len(x) for x in lines)
    text = "\n".join(lines) + "\n" + "─" * width
    return ctk.CTkLabel(master, text=text, font=("Consolas", 40, "bold"), text_color=T.TEXT, justify="right")


# --- Lesetext & Hören --------------------------------------------------------

def _text(master, v, bg):
    f = ctk.CTkFrame(master, fg_color=T.READ_BG, corner_radius=16, border_width=2, border_color=T.READ_BORDER)
    ctk.CTkLabel(f, text=v.get("title", ""), font=T.f(22), text_color=T.PRIMARY).pack(anchor="w", padx=20,
                                                                                         pady=(12, 2))
    ctk.CTkLabel(f, text=v["text"], font=(T.FONT, 20), text_color=T.TEXT, justify="left",
                 wraplength=860).pack(anchor="w", padx=20, pady=(0, 14))
    return f


def _listen(master, v, bg, on_replay):
    f = ctk.CTkFrame(master, fg_color="transparent")
    emoji_label(f, "🎧", 72, fg_color="transparent").pack(side="left", padx=10)
    col = ctk.CTkFrame(f, fg_color="transparent")
    col.pack(side="left", padx=10)
    if v.get("title"):
        ctk.CTkLabel(col, text=v["title"], font=T.f(22), text_color=T.TEXT).pack(anchor="w")
    if on_replay:
        ctk.CTkButton(col, text="  Nochmal anhören", image=emoji_image("🔊", 26), compound="left",
                      command=on_replay, font=T.f(20), height=50, corner_radius=16, fg_color=T.PRIMARY,
                      hover_color=T.PRIMARY_HOVER).pack(anchor="w", pady=6)
    return f


# --- Knobel-Visuals ------------------------------------------------------------

def _is_emo(tok):
    return bool(tok) and ord(tok[0]) > 0x2000 and tok not in ("×", "−", "→", "?")


def _equations(master, v, bg):
    f = ctk.CTkFrame(master, fg_color=T.SURFACE, corner_radius=18)
    for line in v["lines"]:
        row = ctk.CTkFrame(f, fg_color="transparent")
        row.pack(anchor="center", padx=24, pady=5)
        for tok in line:
            if tok == "?":
                ctk.CTkLabel(row, text="?", width=54, height=50, corner_radius=12, fg_color=T.GOLD,
                             text_color="#1D2438", font=T.f(28)).pack(side="left", padx=4)
            elif _is_emo(tok):
                emoji_label(row, tok, 44, fg_color="transparent").pack(side="left", padx=3)
            else:
                ctk.CTkLabel(row, text=tok, font=T.f(30 if len(tok) <= 4 else 20), text_color=T.TEXT
                             ).pack(side="left", padx=6)
    return f


def _numgrid(master, v, bg):
    rows = v["rows"]
    n = len(rows)
    box = v.get("box", 0)
    cell = 70 if n <= 3 else 62
    outer = ctk.CTkFrame(master, fg_color=T.CARD_BORDER, corner_radius=12)
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            ask = val == "?"
            padx = (6 if c == 0 else (6 if box and c % box == 0 else 2), 6 if c == n - 1 else 0)
            pady = (6 if r == 0 else (6 if box and r % box == 0 else 2), 6 if r == n - 1 else 0)
            ctk.CTkLabel(outer, text="" if val is None else str(val), width=cell, height=cell, corner_radius=8,
                         fg_color=T.GOLD if ask else T.SURFACE, text_color="#1D2438" if ask else T.TEXT,
                         font=T.f(30)).grid(row=r, column=c, padx=padx, pady=pady)
    return outer


def _code(master, v, bg):
    f = ctk.CTkFrame(master, fg_color="transparent")
    row = ctk.CTkFrame(f, fg_color="transparent")
    row.pack()
    for ch in v["text"]:
        ctk.CTkLabel(row, text=ch, width=52, height=62, corner_radius=10, fg_color=T.SURFACE,
                     text_color=T.PRIMARY, font=("Consolas", 34, "bold")).pack(side="left", padx=3)
    if v.get("table"):
        abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        k = v["shift"]
        tab = ctk.CTkFrame(f, fg_color=T.SURFACE, corner_radius=12)
        tab.pack(pady=(12, 0))
        ctk.CTkLabel(tab, text="Code:     " + " ".join(abc[(i + k) % 26] for i in range(26)),
                     font=("Consolas", 15), text_color=T.PRIMARY).pack(padx=14, pady=(8, 0), anchor="w")
        ctk.CTkLabel(tab, text="Klartext: " + " ".join(abc), font=("Consolas", 15), text_color=T.TEXT
                     ).pack(padx=14, pady=(0, 8), anchor="w")
    return f
