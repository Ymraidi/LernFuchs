"""Konzentrationsspiele (Tablet): Fehlerbild, Zahlen-Jagd, Zahlen merken, Memory, Buchstaben-Detektiv, Farben-Falle."""

import random
import time

from kivy.clock import Clock
from kivy.graphics import Color, Line
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from lernfuchs import adaptive
from lernfuchs import theme as T
from lernfuchs.content.deutsch_data import NOMEN
from lernfuchs.storage import today
from .screens import BaseScreen
from .ui import AnimImg, Box, C, EmojiImg, NumPad, RButton, Txt, emoji_src, pil_texture

KC = lambda: T.SUBJECTS["konz"][0]  # noqa: E731
KL = lambda: T.SUBJECTS["konz"][1]  # noqa: E731


class GameScreen(BaseScreen):
    TITLE, EMOJI, ID, INTRO = "", "🧠", "", ""

    def __init__(self, app, topic=None, **kw):
        super().__init__(app, **kw)
        self.topic = topic
        self.profile = app.profile
        self.skill = f"konz.{self.ID}"
        self.raw_level = adaptive.level_for(self.profile, "konz", self.skill)
        self.level = min(5, self.raw_level)
        self._ev = []
        self.header(self.TITLE, self.EMOJI, color=KC())
        self.card = Box(bg=T.CARD, border=T.CARD_BORDER, radius=24, orientation="vertical", padding=dp(16),
                        spacing=dp(10))
        self.col.add_widget(self.card)
        a = AnchorLayout(size_hint_y=None, height=dp(130))
        a.add_widget(EmojiImg(self.EMOJI, 110))
        self.card.add_widget(Widget())
        self.card.add_widget(a)
        self.card.add_widget(Txt(self.INTRO, fs=24, size_hint_y=None, height=dp(100)))
        self.card.add_widget(Txt(f"Stufe {self.raw_level}" + (" · PROFI" if self.raw_level >= 6 else ""), fs=20,
                                 color=KC(), bold=True, size_hint_y=None, height=dp(34)))
        b = AnchorLayout(size_hint_y=None, height=dp(70))
        b.add_widget(RButton("Start", on_press=self._start, bg=KC(), icon="▶️", fs=24, size_hint=(None, None),
                             size=(dp(220), dp(66))))
        self.card.add_widget(b)
        self.card.add_widget(Widget())
        app.speaker.say(self.INTRO)

    def later(self, sec, fn):
        ev = Clock.schedule_once(lambda *_: fn(), sec)
        self._ev.append(ev)
        return ev

    def on_leave(self, *_):
        for e in self._ev:
            e.cancel()

    def _start(self):
        self.app.speaker.stop()
        self.card.clear_widgets()
        self.t0 = time.monotonic()
        self.play()

    def finish(self, success, stars, detail, record_key=None, value=None, better=min):
        secs = int(time.monotonic() - self.t0)
        adaptive.record(self.profile, self.skill, success)
        if record_key:
            recs = self.profile.data["records"]
            old = recs.get(record_key)
            if old is None or better(old, value) == value:
                recs[record_key] = value
        new_sticker = self.profile.add_stars(stars)
        self.profile.touch_streak()
        self.profile.log_session({"date": today(), "subject": "konz", "topic": self.ID, "title": self.TITLE,
                                  "correct": 1 if success else 0, "total": 1, "seconds": secs, "stars": stars})
        self.profile.save()
        self.app.show_result(subject="konz", topic=None, correct=1 if success else 0, total=1, xp=stars, seconds=secs,
                             new_sticker=new_sticker, detail=detail, game=self.topic)


class FehlerbildGame(GameScreen):
    TITLE, EMOJI, ID = "Fehlerbild", "🔎", "fehlerbild"
    INTRO = "Zwei echte Fotos – im rechten wurde heimlich etwas verändert. Tippe alle Unterschiede an!"

    def play(self):
        from lernfuchs import photos
        path = photos.random_photo()
        lv = self.raw_level
        n = {1: 4, 2: 5, 3: 5, 4: 6, 5: 7, 6: 7, 7: 8, 8: 9}[lv]
        bmin, bmax = {1: (80, 110), 2: (70, 95), 3: (60, 85), 4: (52, 75), 5: (46, 66), 6: (40, 58), 7: (36, 52),
                      8: (32, 46)}[lv]
        W, H = 540, 405
        base, mod, regs = photos.make_difference_pair(path, n, (W, H), (bmin, bmax), level=lv)
        self.regs, self.found, self.errors, self.hints, self.W = regs, set(), 0, 0, W
        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(52), spacing=dp(14))
        self.count = Txt(f"Gefunden: 0 / {len(regs)}", fs=22, color=KC(), bold=True, halign="left")
        top.add_widget(self.count)
        top.add_widget(RButton("Tipp", on_press=self._hint, bg=T.GOLD, fg="#1D2438", icon="💡", fs=18,
                               size_hint=(None, 1), width=dp(130)))
        self.card.add_widget(top)
        row = BoxLayout(orientation="horizontal", spacing=dp(16))
        self.imgs = []
        for im in (base, mod):
            img = Image(texture=pil_texture(im), fit_mode="contain")
            img.bind(on_touch_down=self._touch)
            self.imgs.append(img)
            row.add_widget(img)
        self.card.add_widget(row)

    def _img_coords(self, img, touch):
        """Tippposition → Bildkoordinaten (Bild ist eingepasst)."""
        iw, ih = img.norm_image_size
        x0 = img.center_x - iw / 2
        y0 = img.center_y - ih / 2
        if not (x0 <= touch.x <= x0 + iw and y0 <= touch.y <= y0 + ih):
            return None
        sx = (touch.x - x0) / iw * self.W
        sy = (1 - (touch.y - y0) / ih) * (self.W * 3 / 4)
        return sx, sy, x0, y0, iw / self.W

    def _mark(self, r, color):
        for img in self.imgs:
            iw, ih = img.norm_image_size
            x0, y0 = img.center_x - iw / 2, img.center_y - ih / 2
            k = iw / self.W
            with img.canvas.after:
                Color(*C(color))
                Line(ellipse=(x0 + r[0] * k - dp(6), y0 + ih - r[3] * k - dp(6), (r[2] - r[0]) * k + dp(12),
                              (r[3] - r[1]) * k + dp(12)), width=dp(3))

    def _touch(self, img, touch):
        res = self._img_coords(img, touch)
        if not res:
            return False
        x, y = res[0], res[1]
        tol = 14
        for i, r in enumerate(self.regs):
            if i not in self.found and r[0] - tol <= x <= r[2] + tol and r[1] - tol <= y <= r[3] + tol:
                self.found.add(i)
                self._mark(r, T.GOOD)
                self.app.sounds.play("richtig")
                self.count.text = f"Gefunden: {len(self.found)} / {len(self.regs)}"
                if len(self.found) == len(self.regs):
                    self.later(0.8, self._done)
                return True
        self.errors += 1
        self.app.sounds.play("falsch")
        return True

    def _hint(self):
        left = [r for i, r in enumerate(self.regs) if i not in self.found]
        if left:
            self.hints += 1
            self._mark(random.choice(left), T.GOLD)

    def _done(self):
        t = time.monotonic() - self.t0
        n = len(self.regs)
        stars = (3 if (self.errors <= 2 and self.hints == 0 and t < n * 14) else 2 if self.hints <= 1 else 1) + \
            (1 if self.raw_level >= 6 else 0)
        self.finish(self.errors <= n and self.hints <= 1, stars,
                    f"{n} Unterschiede in {t:.0f} s · {self.errors} Fehlklicks · {self.hints} Tipps",
                    f"fehlerbild_{n}", round(t, 1))


class SchulteGame(GameScreen):
    TITLE, EMOJI, ID = "Zahlen-Jagd", "🎯", "schulte"
    INTRO = "Tippe die Zahlen der Reihe nach an – so schnell du kannst! Fang bei 1 an."

    def play(self):
        self.n = {1: 3, 2: 4, 3: 5, 4: 5, 5: 6}[self.level]
        self.target, self.errors = 1, 0
        self.find = Txt("Suche: 1", fs=32, color=KC(), bold=True, size_hint_y=None, height=dp(50))
        self.card.add_widget(self.find)
        nums = list(range(1, self.n * self.n + 1))
        random.shuffle(nums)
        size = {3: 120, 4: 100, 5: 86, 6: 72}[self.n]
        g = GridLayout(cols=self.n, spacing=dp(8), size_hint=(None, None),
                       size=(self.n * dp(size + 8), self.n * dp(size + 8)))
        cols = [c[1] for c in T.SUBJECTS.values()]
        self.btns = {}
        for num in nums:
            bg = random.choice(cols) if self.level >= 4 else KL()
            b = RButton(str(num), on_press=lambda num=num: self._click(num), bg=bg, fg=T.TEXT, fs=int(size * 0.32))
            self.btns[num] = b
            g.add_widget(b)
        a = AnchorLayout()
        a.add_widget(g)
        self.card.add_widget(a)

    def _click(self, num):
        b = self.btns[num]
        if num == self.target:
            b.disable(T.GOOD_LIGHT)
            self.app.sounds.play("klick")
            self.target += 1
            if self.target > self.n * self.n:
                return self._done()
            self.find.text = f"Suche: {self.target}"
        elif num > self.target:
            self.errors += 1

    def _done(self):
        t = time.monotonic() - self.t0
        target = self.n * self.n * 1.6
        stars = 3 if (t < target and self.errors <= 1) else 2 if t < target * 1.6 else 1
        self.finish(t < target * 1.2 and self.errors <= 2, stars,
                    f"{self.n}×{self.n} in {t:.1f} Sekunden, {self.errors} Fehlklicks", f"schulte_{self.n}", round(t, 1))


class MemoryGame(GameScreen):
    TITLE, EMOJI, ID = "Memory", "🃏", "memory"
    INTRO = "Decke immer zwei Karten auf. Findest du alle Paare? Merke dir gut, wo welche Karte liegt!"

    def play(self):
        n_pairs = {1: 4, 2: 6, 3: 6, 4: 8, 5: 10}[self.level]
        uniq = {}
        for n in NOMEN:
            if n["e"] and n["e"] not in uniq and emoji_src(n["e"], False):
                uniq[n["e"]] = n
        pool = random.sample(list(uniq.values()), n_pairs)
        pairs = [(n["e"], n["e"]) for n in pool] if self.level <= 2 else [(n["e"], n["w"]) for n in pool]
        cards = []
        for pid, (a, b) in enumerate(pairs):
            cards += [(pid, a), (pid, b)]
        random.shuffle(cards)
        self.cards, self.open, self.matched, self.moves, self.busy = cards, [], set(), 0, False
        self.info = Txt("Züge: 0", fs=22, color=T.MUTED, size_hint_y=None, height=dp(36))
        self.card.add_widget(self.info)
        cols = 4 if len(cards) <= 16 else 5
        g = GridLayout(cols=cols, spacing=dp(10), size_hint=(None, None),
                       size=(cols * dp(150), ((len(cards) + cols - 1) // cols) * dp(118)))
        self.btns = []
        for i, (pid, content) in enumerate(cards):
            b = RButton("", on_press=lambda i=i: self._flip(i), bg=KC())
            b._img = Image(source=emoji_src("🦊"), fit_mode="contain")
            b._lbl = Txt("", fs=20, color="#1D2438", bold=True)
            b.add_widget(b._img)
            self.btns.append(b)
            g.add_widget(b)
        a = AnchorLayout()
        a.add_widget(g)
        self.card.add_widget(a)

    def _face(self, i, show):
        b, content = self.btns[i], self.cards[i][1]
        b.clear_widgets()
        if show:
            b.set_bg("#FFFFFF")
            if emoji_src(content, False):
                b._img.source = emoji_src(content)
                b.add_widget(b._img)
            else:
                b._lbl.text = content
                b.add_widget(b._lbl)
        else:
            b.set_bg(KC())
            b._img.source = emoji_src("🦊")
            b.add_widget(b._img)

    def _flip(self, i):
        if self.busy or i in self.open or i in self.matched:
            return
        self._face(i, True)
        self.open.append(i)
        self.app.sounds.play("klick")
        if len(self.open) == 2:
            self.moves += 1
            self.info.text = f"Züge: {self.moves}"
            a, b = self.open
            if self.cards[a][0] == self.cards[b][0] or self.cards[a][1] == self.cards[b][1]:
                self.matched |= {a, b}
                for j in (a, b):
                    self.btns[j].set_bg(T.GOOD_LIGHT)
                self.open = []
                self.app.sounds.play("richtig")
                if len(self.matched) == len(self.cards):
                    self.later(0.7, self._done)
            else:
                self.busy = True
                self.later(0.95, self._unflip)

    def _unflip(self):
        for j in self.open:
            self._face(j, False)
        self.open, self.busy = [], False

    def _done(self):
        pairs = len(self.cards) // 2
        stars = 3 if self.moves <= pairs * 1.5 else 2 if self.moves <= pairs * 2.2 else 1
        self.finish(self.moves <= pairs * 2, stars, f"{pairs} Paare in {self.moves} Zügen", f"memory_{pairs}",
                    self.moves)


class FarbenGame(GameScreen):
    TITLE, EMOJI, ID = "Farben-Falle", "🎨", "farben"
    INTRO = "Ein Farbwort erscheint in einer Farbe. Tippe auf die FARBE, in der das Wort geschrieben ist – " \
            "nicht auf das, was da steht!"
    COLORS = [("ROT", "#E63946"), ("BLAU", "#1D6FE0"), ("GRÜN", "#2A9D5C"), ("GELB", "#E0A800"), ("LILA", "#8E44AD")]

    def play(self):
        self.colors = self.COLORS[:4] if self.level < 4 else self.COLORS
        self.trials = 12 if self.level <= 2 else 16
        self.incong = {1: 0.3, 2: 0.5, 3: 0.7, 4: 0.8, 5: 0.9}[self.level]
        self.i, self.hits, self.waiting = 0, 0, False
        self.status = Txt("", fs=18, color=T.MUTED, size_hint_y=None, height=dp(30))
        self.word = Txt("", fs=100, bold=True)
        self.card.add_widget(self.status)
        self.card.add_widget(self.word)
        row = BoxLayout(orientation="horizontal", size_hint=(None, None), height=dp(80), spacing=dp(12),
                        pos_hint={"center_x": 0.5}, width=len(self.colors) * dp(172))
        for name, col in self.colors:
            row.add_widget(RButton(name.capitalize(), on_press=lambda col=col: self._answer(col), bg=col, fs=24))
        self.card.add_widget(row)
        self.later(0.6, self._next)

    def _next(self):
        if self.i >= self.trials:
            return self._done()
        self.i += 1
        name, col = random.choice(self.colors)
        ink = col if random.random() >= self.incong else random.choice([c for _, c in self.colors if c != col])
        self.ink, self.waiting = ink, True
        self.word.text = name
        self.word.color = C(ink)
        self.status.text = f"{self.i} / {self.trials}"

    def _answer(self, col):
        if not self.waiting:
            return
        self.waiting = False
        if col == self.ink:
            self.hits += 1
            self.app.sounds.play("klick")
            self.word.text, self.word.color = "Richtig!", C(T.GOOD)
        else:
            self.app.sounds.play("falsch")
            self.word.text, self.word.color = "Falsch", C(T.BAD)
        self.later(0.45, self._next)

    def _done(self):
        pct = self.hits / self.trials
        self.finish(pct >= 0.8, 3 if pct >= 0.9 else 2 if pct >= 0.7 else 1, f"{self.hits} von {self.trials} richtig",
                    f"farben_{self.level}", self.hits, max)


class DetektivGame(GameScreen):
    TITLE, EMOJI, ID = "Buchstaben-Detektiv", "🔍", "detektiv"
    INTRO = "Finde alle gesuchten Zeichen und tippe sie an – aber lass dich nicht von ähnlichen reinlegen!"
    CONF = {1: ("b", ["d"], 5, 8), 2: ("b", ["d", "p"], 6, 8), 3: ("d", ["b", "p", "q"], 6, 9),
            4: ("ei", ["ie", "ai", "eu"], 6, 8), 5: ("die", ["dei", "eid", "ide", "dir"], 6, 7)}

    def play(self):
        target, others, rows, cols = self.CONF[self.level]
        total = rows * cols
        n_t = max(5, total // 4)
        cells = [target] * n_t + [random.choice(others) for _ in range(total - n_t)]
        random.shuffle(cells)
        self.target, self.left, self.errors = target, n_t, 0
        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50))
        top.add_widget(Txt(f"Finde:  {target}", fs=30, color=KC(), bold=True))
        self.left_lbl = Txt(f"Noch {n_t}", fs=24, color=T.MUTED)
        top.add_widget(self.left_lbl)
        self.card.add_widget(top)
        w = 78 if len(target) == 1 else 96
        g = GridLayout(cols=cols, spacing=dp(6), size_hint=(None, None), size=(cols * dp(w + 6), rows * dp(70)))
        for ch in cells:
            b = RButton(ch, bg=T.SURFACE, fg=T.TEXT, fs=30)
            b._cb = lambda b=b, ch=ch: self._click(b, ch)
            g.add_widget(b)
        a = AnchorLayout()
        a.add_widget(g)
        self.card.add_widget(a)

    def _click(self, b, ch):
        if not b.enabled:
            return
        if ch == self.target:
            b.disable(T.GOOD_LIGHT)
            self.app.sounds.play("klick")
            self.left -= 1
            self.left_lbl.text = f"Noch {self.left}"
            if self.left == 0:
                self._done()
        else:
            self.errors += 1
            self.app.sounds.play("falsch")
            b.set_bg(T.BAD_LIGHT)
            self.later(0.4, lambda: b.set_bg(T.SURFACE))

    def _done(self):
        t = time.monotonic() - self.t0
        stars = 3 if self.errors == 0 else 2 if self.errors <= 2 else 1
        self.finish(self.errors <= 1, stars, f"Alle gefunden in {t:.0f} Sekunden, {self.errors} Fehler",
                    f"detektiv_{self.level}", round(t, 1))


class ZahlenMerkenGame(GameScreen):
    TITLE, EMOJI, ID = "Zahlen merken", "🧠", "zahlenmerken"
    INTRO = "Gleich erscheinen Zahlen – eine nach der anderen. Merke sie dir und tippe sie danach ein!"

    def play(self):
        self.length, self.lives, self.round, self.best, self.stars = 2 + self.level, 2, 0, 0, 0
        self.status = Txt("", fs=20, color=T.MUTED, size_hint_y=None, height=dp(32))
        self.big = Txt("", fs=130, color=KC(), bold=True)
        self.inbox = BoxLayout(orientation="vertical", size_hint_y=None, height=dp(0), spacing=dp(8))
        for w in (self.status, self.big, self.inbox):
            self.card.add_widget(w)
        self._round()

    def _round(self):
        if self.lives <= 0 or self.round >= 8:
            return self._done()
        self.round += 1
        self.inbox.clear_widgets()
        self.inbox.height = 0
        self.big.opacity = 1
        self.seq = [random.randint(0, 9) for _ in range(self.length)]
        self.status.text = f"Runde {self.round} · {self.length} Zahlen · Leben: {self.lives}"
        self.big.text = "…"
        speed = max(0.65, 1.0 - self.level * 0.06)
        self.later(1.0, lambda: self._show(0, speed))

    def _show(self, i, speed):
        if i >= len(self.seq):
            self.big.text = "?"
            return self._ask()
        self.big.text = str(self.seq[i])
        self.later(speed, lambda: (setattr(self.big, "text", ""), self.later(0.25, lambda: self._show(i + 1, speed))))

    def _ask(self):
        self.entry = TextInput(multiline=False, readonly=True, font_size=dp(34), halign="center",
                               size_hint=(None, None), size=(dp(300), dp(62)), pos_hint={"center_x": 0.5},
                               background_color=C(T.INPUT_BG), foreground_color=C(T.TEXT))
        pad = NumPad(self.entry, pos_hint={"center_x": 0.5})
        btn = RButton("Prüfen", on_press=self._check, bg=KC(), icon="✅", fs=22, size_hint=(None, None),
                      size=(dp(200), dp(60)), pos_hint={"center_x": 0.5})
        for w in (self.entry, pad, btn):
            self.inbox.add_widget(w)
        self.inbox.height = dp(62) + pad.height + dp(60) + dp(24)
        self.big.opacity = 0.25

    def _check(self):
        given = "".join(ch for ch in self.entry.text if ch.isdigit())
        if not given:
            return
        right = "".join(map(str, self.seq))
        self.big.opacity = 1
        if given == right:
            self.app.sounds.play("richtig")
            self.best, self.stars = max(self.best, self.length), self.stars + 1
            self.big.text, self.big.color = "Richtig!", C(T.GOOD)
            self.length += 1
        else:
            self.app.sounds.play("falsch")
            self.lives -= 1
            self.big.text, self.big.color = right, C(T.BAD)
        self.inbox.clear_widgets()
        self.inbox.height = 0
        self.later(1.4, lambda: (setattr(self.big, "color", C(KC())), self._round()))

    def _done(self):
        self.finish(self.best >= 3 + self.level, max(1, self.stars), f"Du hast dir bis zu {self.best} Zahlen gemerkt",
                    "zahlenmerken_n", self.best, max)


GAMES = {"fehlerbild": FehlerbildGame, "schulte": SchulteGame, "memory": MemoryGame, "farben": FarbenGame,
         "detektiv": DetektivGame, "zahlenmerken": ZahlenMerkenGame}
