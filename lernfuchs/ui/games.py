"""Konzentrationsspiele: Zahlen-Jagd, Zahlen merken, Memory, Buchstaben-Detektiv, Farben-Falle."""

import random
import time
import tkinter as tk

import customtkinter as ctk

from .. import adaptive
from .. import theme as T
from ..content.deutsch_data import NOMEN
from ..emoji import emoji_image
from ..storage import today
from .screens import ResultScreen, header
from .widgets import Card, NumPad, big_button, darker, emoji_label

def _k(i):
    return T.SUBJECTS["konz"][i]


class GameScreen(ctk.CTkFrame):
    TITLE = ""
    EMOJI = "🧠"
    INTRO = ""
    ID = ""

    def __init__(self, app, topic=None):
        super().__init__(app.container, fg_color=T.BG)
        self.app = app
        self.profile = app.profile
        self.skill = f"konz.{self.ID}"
        self.raw_level = adaptive.level_for(self.profile, "konz", self.skill)
        self.level = min(5, self.raw_level)
        self.jobs = []
        header(self, app, self.TITLE, self.EMOJI, color=_k(0))
        self.card = Card(self)
        self.card.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        self._intro()

    def later(self, ms, fn):
        job = self.after(ms, fn)
        self.jobs.append(job)
        return job

    def destroy(self):
        for j in self.jobs:
            try:
                self.after_cancel(j)
            except Exception:
                pass
        self.app.unbind_key()
        super().destroy()

    def clear(self):
        for w in self.card.winfo_children():
            w.destroy()

    def _intro(self):
        box = ctk.CTkFrame(self.card, fg_color="transparent")
        box.pack(expand=True)
        emoji_label(box, self.EMOJI, 110, fg_color="transparent").pack(pady=6)
        ctk.CTkLabel(box, text=self.INTRO, font=(T.FONT, 24), text_color=T.TEXT, wraplength=760).pack(pady=10)
        ctk.CTkLabel(box, text=f"Stufe {self.raw_level}" + (" · PROFI" if self.raw_level >= 6 else ""), font=T.f(20), fg_color=_k(1), corner_radius=12,
                     text_color=_k(0), width=190, height=36).pack(pady=6)
        big_button(box, "  Start", self._start, color=_k(0), emoji="▶️", width=220, height=66).pack(pady=16)
        self.app.speaker.say(self.INTRO)
        self.app.bind_key(lambda e: self._start() if e.keysym == "Return" and not getattr(self, "_started", 0) else None)

    def _start(self):
        if getattr(self, "_started", False):
            return
        self._started = True
        self.app.unbind_key()
        self.app.speaker.stop()
        self.clear()
        self.t0 = time.monotonic()
        self.play()

    def play(self):
        raise NotImplementedError

    def finish(self, success: bool, stars: int, detail: str, record_key=None, record_value=None, better=min,
               record_text=None):
        secs = int(time.monotonic() - self.t0)
        adaptive.record(self.profile, self.skill, success)
        recs = self.profile.data["records"]
        new_record = False
        if record_key is not None and record_value is not None:
            old = recs.get(record_key)
            if old is None or better(old, record_value) == record_value and old != record_value:
                recs[record_key] = record_value
                recs[self.ID] = record_text or str(record_value)
                new_record = old is not None
        new_sticker = self.profile.add_stars(stars)
        self.profile.touch_streak()
        self.profile.log_session({"date": today(), "subject": "konz", "topic": self.ID, "title": self.TITLE,
                                  "correct": 1 if success else 0, "total": 1, "seconds": secs, "stars": stars})
        self.profile.save()
        if new_record:
            detail += "  –  Neuer Rekord! 🏅"
        self.app.show(ResultScreen, subject="konz", topic=None, correct=1 if success else 0, total=1, stars=stars,
                      seconds=secs, new_sticker=new_sticker, game_title=self.TITLE, detail=detail)


# --- Zahlen-Jagd (Schulte-Tabelle) -------------------------------------------

class SchulteGame(GameScreen):
    TITLE, EMOJI, ID = "Zahlen-Jagd", "🎯", "schulte"
    INTRO = "Tippe die Zahlen der Reihe nach an – so schnell du kannst! Fang bei 1 an."

    def play(self):
        self.n = {1: 3, 2: 4, 3: 5, 4: 5, 5: 6}[self.level]
        total = self.n * self.n
        self.target, self.errors = 1, 0
        top = ctk.CTkFrame(self.card, fg_color="transparent")
        top.pack(pady=(16, 6))
        self.find_lbl = ctk.CTkLabel(top, text="Suche: 1", font=T.f(34), text_color=_k(0))
        self.find_lbl.pack(side="left", padx=30)
        self.time_lbl = ctk.CTkLabel(top, text="0.0 s", font=T.f(28), text_color=T.MUTED)
        self.time_lbl.pack(side="left", padx=30)
        grid = ctk.CTkFrame(self.card, fg_color="transparent")
        grid.pack(expand=True)
        nums = list(range(1, total + 1))
        random.shuffle(nums)
        size = {3: 110, 4: 94, 5: 82, 6: 70}[self.n]
        colors = [c[1] for c in T.SUBJECTS.values()]
        self.btns = {}
        for i, num in enumerate(nums):
            bg = random.choice(colors) if self.level >= 4 else _k(1)
            b = ctk.CTkButton(grid, text=str(num), width=size, height=size, corner_radius=14,
                              font=T.f(int(size * 0.38)), fg_color=bg, hover_color=darker(bg, 0.95),
                              text_color=T.TEXT, command=lambda num=num: self._click(num))
            b.grid(row=i // self.n, column=i % self.n, padx=4, pady=4)
            self.btns[num] = (b, bg)
        self._tick()

    def _tick(self):
        if not self.winfo_exists():
            return
        self.time_lbl.configure(text=f"{time.monotonic() - self.t0:.1f} s")
        self.later(100, self._tick)

    def _click(self, num):
        b, bg = self.btns[num]
        if num == self.target:
            b.configure(fg_color=T.GOOD_LIGHT, text_color=T.GOOD, state="disabled")
            self.app.sounds.play("klick")
            self.target += 1
            if self.target > self.n * self.n:
                return self._done()
            self.find_lbl.configure(text=f"Suche: {self.target}")
        elif num > self.target:
            self.errors += 1
            b.configure(fg_color=T.BAD_LIGHT)
            self.later(250, lambda: b.winfo_exists() and b.configure(fg_color=bg))

    def _done(self):
        t = time.monotonic() - self.t0
        target = self.n * self.n * 1.6
        stars = 3 if (t < target and self.errors <= 1) else 2 if t < target * 1.6 else 1
        ok = t < target * 1.2 and self.errors <= 2
        self.finish(ok, stars, f"{self.n}×{self.n} in {t:.1f} Sekunden, {self.errors} Fehlklicks",
                    record_key=f"schulte_{self.n}", record_value=round(t, 1), better=min,
                    record_text=f"{t:.1f} s")


# --- Zahlen merken -------------------------------------------------------------

class ZahlenMerkenGame(GameScreen):
    TITLE, EMOJI, ID = "Zahlen merken", "🧠", "zahlenmerken"
    INTRO = "Gleich erscheinen Zahlen – eine nach der anderen. Merke sie dir gut und tippe sie danach ein!"

    def play(self):
        self.length = 2 + self.level
        self.lives, self.round, self.best, self.stars = 2, 0, 0, 0
        self.status = ctk.CTkLabel(self.card, text="", font=T.f(22), text_color=T.MUTED)
        self.status.pack(pady=(18, 0))
        self.big = ctk.CTkLabel(self.card, text="", font=(T.FONT, 150, "bold"), text_color=_k(0))
        self.big.pack(expand=True)
        self.input_box = ctk.CTkFrame(self.card, fg_color="transparent")
        self.input_box.pack(pady=10)
        self._next_round()

    def _next_round(self):
        if self.lives <= 0 or self.round >= 8:
            return self._done()
        self.round += 1
        for w in self.input_box.winfo_children():
            w.destroy()
        self.seq = [random.randint(0, 9) for _ in range(self.length)]
        for i in range(1, len(self.seq)):
            while self.seq[i] == self.seq[i - 1]:
                self.seq[i] = random.randint(0, 9)
        self.status.configure(text=f"Runde {self.round}  ·  {self.length} Zahlen  ·  Leben: {'❤️' * self.lives}")
        self.big.configure(text="👀", font=(T.FONT, 90))
        speed = max(650, 1000 - self.level * 60)
        self.later(1000, lambda: self._show(0, speed))

    def _show(self, i, speed):
        if i >= len(self.seq):
            self.big.configure(text="?")
            return self._ask()
        self.big.configure(text=str(self.seq[i]), font=(T.FONT, 150, "bold"))
        self.later(speed, lambda: (self.big.configure(text=""), self.later(250, lambda: self._show(i + 1, speed))))

    def _ask(self):
        row = ctk.CTkFrame(self.input_box, fg_color="transparent")
        row.pack()
        self.entry = ctk.CTkEntry(row, width=300, height=66, font=T.f(36), justify="center", corner_radius=16,
                                  border_color=_k(0), border_width=3)
        self.entry.pack(side="left", padx=6)
        big_button(row, "Prüfen", self._check, color=_k(0), emoji="✅", width=150, height=66).pack(side="left", padx=6)
        NumPad(self.input_box, self.entry, self._check).pack(pady=8)
        self.entry.focus_set()
        self.app.bind_key(lambda e: self._check() if e.keysym in ("Return", "KP_Enter") else None)

    def _check(self):
        given = "".join(ch for ch in self.entry.get() if ch.isdigit())
        if not given:
            return
        self.app.unbind_key()
        right = "".join(map(str, self.seq))
        if given == right:
            self.app.sounds.play("richtig")
            self.best = max(self.best, self.length)
            self.stars += 1
            self.big.configure(text="✔", text_color=T.GOOD, font=(T.FONT, 120))
            self.length += 1
        else:
            self.app.sounds.play("falsch")
            self.lives -= 1
            self.big.configure(text=right, text_color=T.BAD, font=(T.FONT, 80, "bold"))
        self.later(1400, lambda: (self.big.configure(text_color=_k(0)), self._next_round()))

    def _done(self):
        ok = self.best >= 3 + self.level
        self.finish(ok, max(1, self.stars), f"Du hast dir bis zu {self.best} Zahlen gemerkt",
                    record_key="zahlenmerken_n", record_value=self.best, better=max,
                    record_text=f"{self.best} Zahlen")


# --- Memory ----------------------------------------------------------------------

MATH_PAIRS = [("3 × 4", "12"), ("5 × 5", "25"), ("7 + 8", "15"), ("2 × 9", "18"), ("6 × 6", "36"),
              ("20 − 7", "13"), ("4 × 8", "32"), ("8 × 3", "24")]


class MemoryGame(GameScreen):
    TITLE, EMOJI, ID = "Memory", "🃏", "memory"
    INTRO = "Decke immer zwei Karten auf. Findest du alle Paare? Merke dir gut, wo welche Karte liegt!"

    def play(self):
        n_pairs = {1: 4, 2: 6, 3: 6, 4: 8, 5: 10}[self.level]
        uniq = {}
        for n in NOMEN:  # jedes Bild nur einmal, sonst sehen zwei Paare gleich aus
            if n["e"] and n["e"] not in uniq:
                uniq[n["e"]] = n
        pool_e = random.sample(list(uniq.values()), n_pairs)
        pairs = []
        if self.level <= 2:
            pairs = [(n["e"], n["e"]) for n in pool_e]
        else:
            k_math = 0 if self.level == 3 else n_pairs // 3
            pairs = [(n["e"], n["w"]) for n in pool_e[:n_pairs - k_math]]
            pairs += random.sample(MATH_PAIRS, k_math)
        cards = []
        for pid, (a, b) in enumerate(pairs):
            cards += [(pid, a), (pid, b)]
        random.shuffle(cards)
        self.cards = cards
        self.open, self.matched, self.moves, self.busy = [], set(), 0, False
        self.info = ctk.CTkLabel(self.card, text="Züge: 0", font=T.f(24), text_color=T.MUTED)
        self.info.pack(pady=(14, 4))
        grid = ctk.CTkFrame(self.card, fg_color="transparent")
        grid.pack(expand=True)
        cols = 4 if len(cards) <= 16 else 5
        size = 112 if len(cards) <= 12 else 98
        self.back_img = emoji_image("🦊", 46)
        self.btns = []
        for i, (pid, content) in enumerate(cards):
            b = ctk.CTkButton(grid, text="", image=self.back_img, width=size + 30, height=size, corner_radius=16,
                              fg_color=_k(0), hover_color=_k(2), font=T.f(22), text_color=T.TEXT,
                              command=lambda i=i: self._flip(i))
            b.grid(row=i // cols, column=i % cols, padx=5, pady=5)
            self.btns.append(b)

    def _face(self, i):
        content = self.cards[i][1]
        b = self.btns[i]
        from .task_view import is_emoji
        if is_emoji(content):
            b.configure(image=emoji_image(content, 60), text="", fg_color=T.SURFACE)
        else:
            b.configure(image=None, text=content.strip(), fg_color=T.SURFACE)

    def _hide(self, i):
        self.btns[i].configure(image=self.back_img, text="", fg_color=_k(0))

    def _flip(self, i):
        if self.busy or i in self.open or i in self.matched:
            return
        self._face(i)
        self.open.append(i)
        self.app.sounds.play("klick")
        if len(self.open) == 2:
            self.moves += 1
            self.info.configure(text=f"Züge: {self.moves}")
            a, b = self.open
            if self.cards[a][0] == self.cards[b][0] or self.cards[a][1] == self.cards[b][1]:
                self.matched |= {a, b}
                for j in (a, b):
                    self.btns[j].configure(fg_color=T.GOOD_LIGHT, border_width=3, border_color=T.GOOD)
                self.open = []
                self.app.sounds.play("richtig")
                if len(self.matched) == len(self.cards):
                    self.later(700, self._done)
            else:
                self.busy = True
                self.later(950, self._unflip)

    def _unflip(self):
        for j in self.open:
            self._hide(j)
        self.open, self.busy = [], False

    def _done(self):
        pairs = len(self.cards) // 2
        stars = 3 if self.moves <= pairs * 1.5 else 2 if self.moves <= pairs * 2.2 else 1
        self.finish(self.moves <= pairs * 2, stars, f"{pairs} Paare in {self.moves} Zügen",
                    record_key=f"memory_{pairs}", record_value=self.moves, better=min,
                    record_text=f"{self.moves} Züge")


# --- Buchstaben-Detektiv ------------------------------------------------------

class DetektivGame(GameScreen):
    TITLE, EMOJI, ID = "Buchstaben-Detektiv", "🔍", "detektiv"
    CONF = {1: ("b", ["d"], 5, 8), 2: ("b", ["d", "p"], 6, 8), 3: ("d", ["b", "p", "q"], 6, 9),
            4: ("ei", ["ie", "ai", "eu"], 6, 8), 5: ("die", ["dei", "eid", "ide", "dir"], 6, 7)}

    def __init__(self, app, topic=None):
        lvl = min(5, adaptive.level_for(app.profile, "konz", "konz.detektiv"))
        self.target = self.CONF[lvl][0]
        self.INTRO = f"Finde alle „{self.target}“ und tippe sie an! Aber Vorsicht: Lass dich nicht von " \
                     f"ähnlichen Zeichen reinlegen."
        super().__init__(app, topic)

    def play(self):
        target, others, rows, cols = self.CONF[self.level]
        total = rows * cols
        n_t = max(5, total // 4)
        cells = [target] * n_t + [random.choice(others) for _ in range(total - n_t)]
        random.shuffle(cells)
        self.left, self.errors = n_t, 0
        top = ctk.CTkFrame(self.card, fg_color="transparent")
        top.pack(pady=(14, 4))
        ctk.CTkLabel(top, text=f"Finde:  {target}", font=T.f(34), text_color=_k(0)).pack(side="left", padx=26)
        self.left_lbl = ctk.CTkLabel(top, text=f"Noch {n_t}", font=T.f(26), text_color=T.MUTED)
        self.left_lbl.pack(side="left", padx=26)
        grid = ctk.CTkFrame(self.card, fg_color="transparent")
        grid.pack(expand=True)
        w = 72 if len(target) == 1 else 92
        for i, ch in enumerate(cells):
            b = ctk.CTkButton(grid, text=ch, width=w, height=64, corner_radius=12, font=(T.FONT, 32),
                              fg_color=T.BG, hover_color=_k(1), text_color=T.TEXT)
            b.configure(command=lambda b=b, ch=ch: self._click(b, ch))
            b.grid(row=i // cols, column=i % cols, padx=3, pady=3)

    def _click(self, b, ch):
        if ch == self.target:
            b.configure(fg_color=T.GOOD_LIGHT, text_color=T.GOOD, state="disabled")
            self.app.sounds.play("klick")
            self.left -= 1
            self.left_lbl.configure(text=f"Noch {self.left}")
            if self.left == 0:
                self._done()
        else:
            self.errors += 1
            self.app.sounds.play("falsch")
            b.configure(fg_color=T.BAD_LIGHT)
            self.later(400, lambda: b.winfo_exists() and b.configure(fg_color=T.BG))

    def _done(self):
        t = time.monotonic() - self.t0
        stars = 3 if self.errors == 0 else 2 if self.errors <= 2 else 1
        self.finish(self.errors <= 1, stars, f"Alle gefunden in {t:.0f} Sekunden, {self.errors} Fehler",
                    record_key=f"detektiv_{self.level}", record_value=round(t, 1), better=min,
                    record_text=f"{t:.0f} s")


# --- Farben-Falle (Stroop) ------------------------------------------------------

COLORS = [("ROT", "#E63946"), ("BLAU", "#1D6FE0"), ("GRÜN", "#2A9D5C"), ("GELB", "#E0A800"), ("LILA", "#8E44AD")]


class FarbenGame(GameScreen):
    TITLE, EMOJI, ID = "Farben-Falle", "🎨", "farben"
    INTRO = "Ein Farbwort erscheint in einer Farbe. Tippe auf die FARBE, in der das Wort geschrieben ist – " \
            "nicht auf das, was da steht!"

    def play(self):
        self.colors = COLORS[:4] if self.level < 4 else COLORS
        self.trials = 12 if self.level <= 2 else 16
        self.incong = {1: 0.3, 2: 0.5, 3: 0.7, 4: 0.8, 5: 0.9}[self.level]
        self.limit = {1: 0, 2: 0, 3: 4.0, 4: 3.0, 5: 2.5}[self.level]
        self.i, self.hits, self.rts = 0, 0, []
        self.status = ctk.CTkLabel(self.card, text="", font=T.f(20), text_color=T.MUTED)
        self.status.pack(pady=(16, 0))
        self.word = ctk.CTkLabel(self.card, text="", font=(T.FONT, 110, "bold"))
        self.word.pack(expand=True)
        self.bar = ctk.CTkProgressBar(self.card, width=400, height=12, progress_color=_k(0))
        if self.limit:
            self.bar.pack(pady=4)
        row = ctk.CTkFrame(self.card, fg_color="transparent")
        row.pack(pady=(10, 30))
        for name, col in self.colors:
            ctk.CTkButton(row, text=name.capitalize(), width=150, height=74, corner_radius=18, font=T.f(24),
                          fg_color=col, hover_color=darker(col), command=lambda col=col: self._answer(col)
                          ).pack(side="left", padx=8)
        self.app.bind_key(self._key)
        self.later(600, self._next)

    def _key(self, e):
        if e.char and e.char in "12345":
            k = int(e.char) - 1
            if k < len(self.colors):
                self._answer(self.colors[k][1])

    def _next(self):
        if self.i >= self.trials:
            return self._done()
        self.i += 1
        name, col = random.choice(self.colors)
        ink = col
        if random.random() < self.incong:
            ink = random.choice([c for n, c in self.colors if c != col])
        self.ink = ink
        self.word.configure(text=name, text_color=ink)
        self.status.configure(text=f"{self.i} / {self.trials}")
        self.shown_at = time.monotonic()
        self.waiting = True
        if self.limit:
            self._countdown()

    def _countdown(self):
        if not self.waiting or not self.winfo_exists():
            return
        left = 1 - (time.monotonic() - self.shown_at) / self.limit
        self.bar.set(max(0, left))
        if left <= 0:
            self.waiting = False
            self.word.configure(text="Zu langsam!", text_color=T.MUTED)
            self.later(600, self._next)
            return
        self.later(50, self._countdown)

    def _answer(self, col):
        if not getattr(self, "waiting", False):
            return
        self.waiting = False
        rt = time.monotonic() - self.shown_at
        if col == self.ink:
            self.hits += 1
            self.rts.append(rt)
            self.app.sounds.play("klick")
            self.word.configure(text="✔", text_color=T.GOOD)
        else:
            self.app.sounds.play("falsch")
            self.word.configure(text="✘", text_color=T.BAD)
        self.later(450, self._next)

    def _done(self):
        pct = self.hits / self.trials
        avg = sum(self.rts) / len(self.rts) if self.rts else 0
        stars = 3 if pct >= 0.9 else 2 if pct >= 0.7 else 1
        self.finish(pct >= 0.8, stars, f"{self.hits} von {self.trials} richtig · Ø {avg:.1f} s",
                    record_key=f"farben_{self.level}", record_value=self.hits, better=max,
                    record_text=f"{self.hits}/{self.trials}")




# --- Fehlerbild (echte Fotos) ---------------------------------------------------

class FehlerbildGame(GameScreen):
    TITLE, EMOJI, ID = "Fehlerbild", "🔎", "fehlerbild"
    INTRO = "Zwei echte Fotos – im rechten wurde heimlich etwas verändert. Finde alle Unterschiede und tippe " \
            "sie an. Je weniger Fehlklicks und Tipps, desto mehr Punkte!"

    def play(self):
        from .. import photos
        from PIL import ImageTk
        from .widgets import scaling
        path = photos.random_photo(exclude=self.profile.data.get("last_photos", []))
        if not path:
            photos.prefetch()
            box = ctk.CTkFrame(self.card, fg_color="transparent")
            box.pack(expand=True)
            emoji_label(box, "📡", 90, fg_color="transparent").pack(pady=8)
            ctk.CTkLabel(box, text="Die Fotos werden gerade aus dem Internet geladen.\nBitte in einer Minute nochmal "
                                   "versuchen.", font=T.f(22), text_color=T.MUTED).pack()
            return
        self.profile.data["last_photos"] = (self.profile.data.get("last_photos", []) + [path])[-8:]
        lv = self.raw_level
        n = {1: 4, 2: 5, 3: 5, 4: 6, 5: 7, 6: 7, 7: 8, 8: 9}[lv]
        bmin, bmax = {1: (80, 110), 2: (70, 95), 3: (60, 85), 4: (52, 75), 5: (46, 66), 6: (40, 58),
                      7: (36, 52), 8: (32, 46)}[lv]
        s = scaling(self)
        W, H, gap = int(545 * s), int(409 * s), int(18 * s)
        self.s, self.W, self.gap = s, W, gap
        base, mod, regs = photos.make_difference_pair(path, n, (W, H), (int(bmin * s), int(bmax * s)), level=lv)
        self.regs, self.found, self.errors, self.hints = regs, set(), 0, 0
        top = ctk.CTkFrame(self.card, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(14, 6))
        self.count_lbl = ctk.CTkLabel(top, text=f"Gefunden: 0 / {len(regs)}", font=T.f(24), text_color=_k(0))
        self.count_lbl.pack(side="left")
        self.time_lbl = ctk.CTkLabel(top, text="0 s", font=T.f(22), text_color=T.MUTED)
        self.time_lbl.pack(side="left", padx=30)
        big_button(top, "  Tipp", self._hint, color=T.GOLD, text_color="#1D2438", emoji="💡", size=18,
                   height=46, width=120).pack(side="right")
        labels = ctk.CTkFrame(self.card, fg_color="transparent")
        labels.pack()
        ctk.CTkLabel(labels, text="Original", font=T.f(16), text_color=T.MUTED, width=int(W / s)).pack(side="left")
        ctk.CTkLabel(labels, text="Fehlerbild", font=T.f(16), text_color=T.MUTED, width=int(W / s)
                     ).pack(side="left", padx=(int(gap / s), 0))
        self.cv = tk.Canvas(self.card, width=2 * W + gap, height=H, bg=T.CARD, highlightthickness=0, cursor="hand2")
        self.cv.pack(pady=(4, 16))
        self._imgs = [ImageTk.PhotoImage(base), ImageTk.PhotoImage(mod)]
        self.cv.create_image(0, 0, image=self._imgs[0], anchor="nw")
        self.cv.create_image(W + gap, 0, image=self._imgs[1], anchor="nw")
        self.cv.bind("<Button-1>", self._click)
        self._tick()

    def _tick(self):
        if not self.winfo_exists():
            return
        self.time_lbl.configure(text=f"{int(time.monotonic() - self.t0)} s")
        self.later(500, self._tick)

    def _mark(self, r, color, tag=None, dash=None):
        pad = 6 * self.s
        for off in (0, self.W + self.gap):
            self.cv.create_oval(r[0] + off - pad, r[1] - pad, r[2] + off + pad, r[3] + pad, outline=color,
                                width=4 * self.s, tags=tag, dash=dash)

    def _click(self, e):
        x, y = e.x, e.y
        if x > self.W + self.gap:
            x -= self.W + self.gap
        elif x > self.W:
            return
        tol = 14 * self.s
        for i, r in enumerate(self.regs):
            if i not in self.found and r[0] - tol <= x <= r[2] + tol and r[1] - tol <= y <= r[3] + tol:
                self.found.add(i)
                self._mark(r, T.GOOD)
                self.app.sounds.play("richtig")
                self.count_lbl.configure(text=f"Gefunden: {len(self.found)} / {len(self.regs)}")
                if len(self.found) == len(self.regs):
                    self.later(700, self._done)
                return
        self.errors += 1
        self.app.sounds.play("falsch")
        d = 12 * self.s
        for off in (0, self.W + self.gap):
            cx = x + off
            self.cv.create_line(cx - d, y - d, cx + d, y + d, fill=T.BAD, width=4, tags="miss")
            self.cv.create_line(cx - d, y + d, cx + d, y - d, fill=T.BAD, width=4, tags="miss")
        self.later(600, lambda: self.cv.winfo_exists() and self.cv.delete("miss"))

    def _hint(self):
        left = [r for i, r in enumerate(self.regs) if i not in self.found]
        if not left:
            return
        self.hints += 1
        self._mark(random.choice(left), T.GOLD, tag="hint", dash=(6, 4))
        self.later(1300, lambda: self.cv.winfo_exists() and self.cv.delete("hint"))

    def _done(self):
        t = time.monotonic() - self.t0
        n = len(self.regs)
        stars = 3 if (self.errors <= 2 and self.hints == 0 and t < n * 14) else 2 if self.hints <= 1 else 1
        stars += 1 if self.raw_level >= 6 else 0
        self.finish(self.errors <= n and self.hints <= 1, stars,
                    f"{n} Unterschiede in {t:.0f} s · {self.errors} Fehlklicks · {self.hints} Tipps",
                    record_key=f"fehlerbild_{n}", record_value=round(t, 1), better=min, record_text=f"{t:.0f} s")


GAMES = {"fehlerbild": FehlerbildGame, "schulte": SchulteGame, "zahlenmerken": ZahlenMerkenGame, "memory": MemoryGame,
         "detektiv": DetektivGame, "farben": FarbenGame}
