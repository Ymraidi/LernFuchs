"""Bild-Hilfen zu Aufgaben (Kivy): Uhr, Münzen, Lineal, Formen, Zahlenmauer, Gitter, Code, Lesetext …"""

import math
import random

from kivy.graphics import Color, Ellipse, Line, Mesh, Rectangle, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget

from lernfuchs import theme as T
from .ui import Box, C, EmojiImg, RButton, Txt, emoji_row, split_emojis


def _wrap(w, width, height):
    w.size_hint = (None, None)
    w.size = (dp(width), dp(height))
    return w


def render(visual, on_replay=None):
    if not visual:
        return None
    kind = visual.get("kind")
    fn = {"emoji": _emoji, "emoji_row": _emoji_row, "emoji_groups": _groups, "emoji_array": _array,
          "emoji_grid": _grid, "pattern": _pattern, "clock": _clock, "coins": _coins, "wall": _wall,
          "ruler": _ruler, "shape": _shape, "shapes": _shapes, "column": _column, "rect": _rect, "text": _text,
          "equations": _equations, "numgrid": _numgrid, "code": _code, "code_line": _code_line}.get(kind)
    if kind == "listen":
        return _listen(visual, on_replay)
    return fn(visual) if fn else None


def _emoji(v):
    return EmojiImg(v["e"], 96) if v.get("e") else None


def _emoji_row(v):
    items = [e for e in v.get("items", []) if e]
    return emoji_row("".join(items), 60, 12) if items else None


def _groups(v):
    total = sum(n for _, n in v["groups"])
    size = 44 if total <= 8 else 34 if total <= 14 else 28
    row = BoxLayout(orientation="horizontal", size_hint=(None, None), spacing=dp(10))
    width, height = 0, 0
    for gi, (e, n) in enumerate(v["groups"]):
        if gi:
            lab = Txt(v.get("sep", "+"), fs=34, color=T.MUTED, wrap=False, size_hint=(None, 1), width=dp(36))
            row.add_widget(lab)
            width += dp(46)
        cols = min(5, n)
        rows = math.ceil(n / cols)
        g = GridLayout(cols=cols, spacing=dp(3), size_hint=(None, None),
                       size=(cols * dp(size + 3), rows * dp(size + 3)))
        for _ in range(n):
            g.add_widget(EmojiImg(e, size))
        row.add_widget(g)
        width += g.width + dp(10)
        height = max(height, g.height)
    row.size = (width, height)
    return row


def _array(v):
    n = v["rows"] * v["cols"]
    size = 38 if n <= 24 else 30
    g = GridLayout(cols=v["cols"], spacing=dp(4), size_hint=(None, None))
    for _ in range(n):
        g.add_widget(EmojiImg(v["emoji"], size))
    g.size = (v["cols"] * dp(size + 4), v["rows"] * dp(size + 4))
    return g


def _grid(v):
    n = len(v["items"])
    cols = v.get("cols", 6)
    size = 42 if n <= 20 else 36 if n <= 30 else 30
    g = GridLayout(cols=cols, spacing=dp(6), size_hint=(None, None))
    for e in v["items"]:
        g.add_widget(EmojiImg(e, size))
    rows = math.ceil(n / cols)
    g.size = (cols * dp(size + 6), rows * dp(size + 6))
    return g


def _pattern(v):
    row = BoxLayout(orientation="horizontal", size_hint=(None, None), spacing=dp(8), height=dp(56))
    for e in v["seq"]:
        if e == "?":
            b = Box(bg=T.GOLD_LIGHT, radius=12, size_hint=(None, None), size=(dp(56), dp(56)))
            b.add_widget(Txt("?", fs=30, color=T.PRIMARY, bold=True))
            row.add_widget(b)
        else:
            row.add_widget(EmojiImg(e, 50))
    row.width = len(v["seq"]) * dp(64)
    return row


class _Canvas(Widget):
    def __init__(self, draw, w, h, **kw):
        super().__init__(size_hint=(None, None), size=(dp(w), dp(h)), **kw)
        self._draw_fn = draw
        self.bind(pos=lambda *_: self._redraw(), size=lambda *_: self._redraw())

    def _redraw(self):
        self.canvas.clear()
        for ch in list(self.children):
            self.remove_widget(ch)
        self._draw_fn(self)

    def label(self, text, cx, cy, size=16, color=None, bold=True):
        lab = Label(text=text, font_size=sp(size), color=C(color or T.TEXT), bold=bold, size_hint=(None, None))
        lab.texture_update()
        lab.size = lab.texture_size
        lab.center = (cx, cy)
        self.add_widget(lab)


def _clock(v):
    def draw(w):
        cx, cy = w.center
        r = min(w.width, w.height) / 2 - dp(6)
        with w.canvas:
            Color(*C(T.PRIMARY))
            Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))
            Color(*C(T.CLOCK_FACE))
            Ellipse(pos=(cx - r + dp(6), cy - r + dp(6)), size=(2 * r - dp(12), 2 * r - dp(12)))
            Color(*C(T.CLOCK_TEXT))
            for i in range(60):
                a = math.radians(90 - i * 6)
                inner = r - dp(16 if i % 5 == 0 else 11)
                Line(points=[cx + inner * math.cos(a), cy + inner * math.sin(a),
                             cx + (r - dp(8)) * math.cos(a), cy + (r - dp(8)) * math.sin(a)],
                     width=dp(1.6 if i % 5 == 0 else 0.8))
            h, m = v["h"] % 12, v["m"]
            ah = math.radians(90 - (h + m / 60) * 30)
            am = math.radians(90 - m * 6)
            Color(*C("#E63946"))
            Line(points=[cx, cy, cx + r * 0.5 * math.cos(ah), cy + r * 0.5 * math.sin(ah)], width=dp(5), cap="round")
            Color(*C("#1D6FE0"))
            Line(points=[cx, cy, cx + r * 0.78 * math.cos(am), cy + r * 0.78 * math.sin(am)], width=dp(3),
                 cap="round")
            Color(*C(T.CLOCK_TEXT))
            Ellipse(pos=(cx - dp(7), cy - dp(7)), size=(dp(14), dp(14)))
        for n in range(1, 13):
            a = math.radians(90 - n * 30)
            w.label(str(n), cx + (r - dp(32)) * math.cos(a), cy + (r - dp(32)) * math.sin(a), 17, T.CLOCK_TEXT)
    return _Canvas(draw, 230, 230)


def _coin_r(val):
    return {1: 24, 2: 27, 5: 30, 10: 29, 20: 32, 50: 35, 100: 34, 200: 38}.get(val, 30)


def _coins(v):
    vals = v["values"]
    width = sum((150 if x >= 500 else 2 * _coin_r(x)) + 12 for x in vals) + 10

    def draw(w):
        x = w.x + dp(6)
        cy = w.center_y
        for val in vals:
            if val >= 500:
                col = {500: "#A9B7A4", 1000: "#E58A7A", 2000: "#7EA6E0", 5000: "#F2A65A"}.get(val, "#CCCCCC")
                with w.canvas:
                    Color(*C(col))
                    RoundedRectangle(pos=(x, cy - dp(38)), size=(dp(150), dp(76)), radius=[dp(6)])
                w.label(f"{val // 100} €", x + dp(75), cy, 22, "#FFFFFF")
                x += dp(162)
                continue
            r = dp(_coin_r(val))
            if val in (100, 200):
                outer, inner = ("#E3B341", "#C9CDD2") if val == 100 else ("#C9CDD2", "#E3B341")
            else:
                outer = inner = "#C8703C" if val <= 5 else "#E3B341"
            with w.canvas:
                Color(*C(outer))
                Ellipse(pos=(x, cy - r), size=(2 * r, 2 * r))
                Color(*C(inner))
                Ellipse(pos=(x + r * 0.3, cy - r * 0.7), size=(r * 1.4, r * 1.4))
            w.label(f"{val // 100} €" if val >= 100 else f"{val} ct", x + r, cy, 13, "#1D2438")
            x += 2 * r + dp(12)
    return _Canvas(draw, width, 90)


def _wall(v):
    rows = v["rows"]
    maxlen = max(len(str(x)) for row in rows for x in row if x is not None)
    cw = max(80, 20 * maxlen + 30)
    box = BoxLayout(orientation="vertical", spacing=dp(4), size_hint=(None, None))
    for row in reversed(rows):
        line = BoxLayout(orientation="horizontal", spacing=dp(4), size_hint=(None, None),
                         size=(len(row) * dp(cw + 4), dp(48)), pos_hint={"center_x": 0.5})
        for val in row:
            hidden = val is None
            b = Box(bg=T.GOLD if hidden else "#F4A988", radius=8, size_hint=(None, None), size=(dp(cw), dp(48)))
            b.add_widget(Txt("?" if hidden else str(val), fs=24, color="#1D2438" if hidden else "#FFFFFF", bold=True))
            line.add_widget(b)
        box.add_widget(line)
    box.size = (len(rows[0]) * dp(cw + 4), len(rows) * dp(52))
    return box


def _ruler(v):
    L = v["length"]

    def draw(w):
        cm = dp(36)
        x0, yp = w.x + dp(20), w.top - dp(30)
        with w.canvas:
            Color(*C("#FFC93C"))
            Rectangle(pos=(x0, yp - dp(10)), size=(max(dp(6), (L - 0.6) * cm), dp(20)))
            Color(*C("#F5D7B0"))
            Mesh(vertices=[x0 + (L - 0.6) * cm, yp - dp(10), 0, 0, x0 + L * cm, yp, 0, 0,
                           x0 + (L - 0.6) * cm, yp + dp(10), 0, 0], indices=[0, 1, 2], mode="triangles")
            Color(*C(T.GLASS))
            top = yp - dp(30)
            Rectangle(pos=(x0 - dp(10), top - dp(54)), size=(12.6 * cm, dp(54)))
            Color(*C(T.TEXT))
            for mm in range(0, 125):
                x = x0 + mm * cm / 10
                ln = 20 if mm % 10 == 0 else 13 if mm % 5 == 0 else 7
                Line(points=[x, top, x, top - dp(ln)], width=1)
        for c in range(13):
            w.label(str(c), x0 + c * cm, yp - dp(30) - dp(34), 12)
    return _Canvas(draw, 36 * 13 + 40, 130)


SHAPE_COLORS = ["#FF6B6B", "#4D96FF", "#2EB872", "#FFC93C", "#9B5DE5", "#FF8C42"]


def _poly(cx, cy, r, n, rot=-90):
    pts = []
    for i in range(n):
        a = math.radians(rot + i * 360 / n)
        pts += [cx + r * math.cos(a), cy - r * math.sin(a)]
    return pts


def _draw_shape(w, name, cx, cy, r, color):
    with w.canvas:
        Color(*C(color))
        if name == "Kreis":
            Ellipse(pos=(cx - r, cy - r), size=(2 * r, 2 * r))
        elif name == "Quadrat":
            Rectangle(pos=(cx - r * 0.85, cy - r * 0.85), size=(r * 1.7, r * 1.7))
        elif name == "Rechteck":
            Rectangle(pos=(cx - r * 1.2, cy - r * 0.6), size=(r * 2.4, r * 1.2))
        else:
            n = {"Dreieck": 3, "Fünfeck": 5, "Sechseck": 6}[name]
            pts = _poly(cx, cy - (r * 0.15 if n == 3 else 0), r, n, rot=90)
            verts, idx = [], []
            for i in range(0, len(pts), 2):
                verts += [pts[i], pts[i + 1], 0, 0]
                idx.append(i // 2)
            Mesh(vertices=verts, indices=idx, mode="triangle_fan")


def _shape(v):
    col = random.choice(SHAPE_COLORS)
    return _Canvas(lambda w: _draw_shape(w, v["name"], w.center_x, w.center_y, dp(78), col), 260, 200)


def _shapes(v):
    lst = v["list"]
    cols = 8 if len(lst) > 12 else 6
    rows = math.ceil(len(lst) / cols)
    cols_ = [random.choice(SHAPE_COLORS) for _ in lst]
    offs = [(random.uniform(-5, 5), random.uniform(-5, 5)) for _ in lst]

    def draw(w):
        cell = dp(68)
        for i, name in enumerate(lst):
            r, c = divmod(i, cols)
            cx = w.x + c * cell + cell / 2 + dp(offs[i][0])
            cy = w.top - (r * cell + cell / 2) + dp(offs[i][1])
            _draw_shape(w, name, cx, cy, dp(23), cols_[i])
    return _Canvas(draw, cols * 68, rows * 68)


def _rect(v):
    wc, hc = v["w"], v["h"]

    def draw(w):
        cell = dp(34)
        x0, y0 = w.x + dp(46), w.y + dp(40)
        with w.canvas:
            Color(*C(T.SUBJECTS["mathe"][1]))
            Rectangle(pos=(x0, y0), size=(wc * cell, hc * cell))
            Color(*C(T.SUBJECTS["mathe"][0]))
            Line(rectangle=(x0, y0, wc * cell, hc * cell), width=dp(2))
            if v["mode"] == "flaeche":
                Color(*C(T.GLASS_LINE))
                for i in range(1, wc):
                    Line(points=[x0 + i * cell, y0, x0 + i * cell, y0 + hc * cell])
                for j in range(1, hc):
                    Line(points=[x0, y0 + j * cell, x0 + wc * cell, y0 + j * cell])
        if v["mode"] != "flaeche":
            w.label(f"{wc} cm", x0 + wc * cell / 2, y0 + hc * cell + dp(16))
            w.label(f"{hc} cm", x0 + wc * cell + dp(30), y0 + hc * cell / 2)
    return _Canvas(draw, wc * 34 + 110, hc * 34 + 80)


def _column(v):
    lines = v["lines"]
    width = max(len(x) for x in lines)
    text = "\n".join(lines) + "\n" + "─" * width
    lab = Label(text=text, font_name="RobotoMono-Regular", font_size=sp(38), color=C(T.TEXT), halign="right",
                size_hint=(None, None))
    lab.texture_update()
    lab.size = lab.texture_size
    return lab


def _text(v):
    b = Box(bg=T.READ_BG, border=T.READ_BORDER, radius=16, orientation="vertical", size_hint=(None, None),
            width=dp(900), padding=(dp(20), dp(12)), spacing=dp(6))
    t1 = Txt(v.get("title", ""), fs=22, color=T.PRIMARY, bold=True, halign="left", size_hint_y=None)
    t2 = Txt(v["text"], fs=20, halign="left", size_hint_y=None)
    b.add_widget(t1)
    b.add_widget(t2)
    t1.text_size = (dp(860), None)
    t2.text_size = (dp(860), None)
    t1.texture_update()
    t2.texture_update()
    t1.height, t2.height = t1.texture_size[1], t2.texture_size[1]
    b.height = t1.height + t2.height + dp(34)
    return b


def _listen(v, on_replay):
    row = BoxLayout(orientation="horizontal", size_hint=(None, None), size=(dp(420), dp(80)), spacing=dp(14))
    row.add_widget(EmojiImg("🎧", 70))
    col = BoxLayout(orientation="vertical", spacing=dp(4))
    if v.get("title"):
        col.add_widget(Txt(v["title"], fs=20, bold=True, halign="left"))
    if on_replay:
        col.add_widget(RButton("Nochmal anhören", on_press=on_replay, icon="🔊", fs=18, size_hint=(None, None),
                               size=(dp(250), dp(46))))
    row.add_widget(col)
    return row


def _equations(v):
    box = Box(bg=T.SURFACE, radius=18, orientation="vertical", size_hint=(None, None), padding=dp(12), spacing=dp(6))
    maxw = 0
    for line in v["lines"]:
        row = BoxLayout(orientation="horizontal", size_hint=(None, None), height=dp(52), spacing=dp(8),
                        pos_hint={"center_x": 0.5})
        w = 0
        for tok in line:
            if tok == "?":
                b = Box(bg=T.GOLD, radius=10, size_hint=(None, None), size=(dp(50), dp(48)))
                b.add_widget(Txt("?", fs=28, color="#1D2438", bold=True))
                row.add_widget(b)
                w += dp(58)
            elif split_emojis(tok) != [tok] or (len(tok) <= 2 and ord(tok[0]) > 0x2000 and tok not in "×−→?"):
                row.add_widget(EmojiImg(tok, 44))
                w += dp(52)
            else:
                lab = Txt(tok, fs=28 if len(tok) <= 4 else 19, bold=True, wrap=False, size_hint=(None, 1))
                lab.texture_update()
                lab.width = lab.texture_size[0] + dp(6)
                row.add_widget(lab)
                w += lab.width + dp(8)
        row.width = w
        maxw = max(maxw, w)
        box.add_widget(row)
    box.size = (maxw + dp(40), len(v["lines"]) * dp(58) + dp(24))
    return box


def _numgrid(v):
    rows = v["rows"]
    n = len(rows)
    cell = 66 if n <= 3 else 58 if n <= 4 else 52
    box = Box(bg=T.CARD_BORDER, radius=12, size_hint=(None, None), padding=dp(6))
    g = GridLayout(cols=n, spacing=dp(4))
    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            ask = val == "?"
            b = Box(bg=T.GOLD if ask else T.SURFACE, radius=8)
            b.add_widget(Txt("" if val is None else str(val), fs=26, color="#1D2438" if ask else T.TEXT, bold=True))
            g.add_widget(b)
    box.add_widget(g)
    box.size = (n * dp(cell + 4) + dp(12), n * dp(cell + 4) + dp(12))
    return box


def _code(v):
    col = BoxLayout(orientation="vertical", size_hint=(None, None), spacing=dp(10))
    row = BoxLayout(orientation="horizontal", size_hint=(None, None), height=dp(62), spacing=dp(6),
                    pos_hint={"center_x": 0.5})
    for ch in v["text"]:
        b = Box(bg=T.SURFACE, radius=10, size_hint=(None, None), size=(dp(50), dp(62)))
        b.add_widget(Label(text=ch, font_name="RobotoMono-Regular", font_size=sp(32), color=C(T.PRIMARY), bold=True))
        row.add_widget(b)
    row.width = len(v["text"]) * dp(56)
    col.add_widget(row)
    width, height = row.width, dp(62)
    if v.get("table"):
        abc = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        k = v["shift"]
        t = Label(text="Code:     " + " ".join(abc[(i + k) % 26] for i in range(26)) + "\nKlartext: " + " ".join(abc),
                  font_name="RobotoMono-Regular", font_size=sp(15), color=C(T.TEXT), size_hint=(None, None))
        t.texture_update()
        t.size = t.texture_size
        t.pos_hint = {"center_x": 0.5}
        col.add_widget(t)
        width, height = max(width, t.width), height + t.height + dp(10)
    col.size = (width, height)
    return col


def _code_line(v):
    b = Box(bg=T.READ_BG, radius=14, size_hint=(None, None), padding=(dp(20), dp(10)))
    lab = Txt(v["text"], fs=28, bold=True, wrap=False)
    lab.texture_update()
    b.add_widget(lab)
    b.size = (min(dp(1000), lab.texture_size[0] + dp(50)), lab.texture_size[1] + dp(24))
    return b
