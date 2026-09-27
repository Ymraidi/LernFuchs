"""Startseite, Fachseite, Ergebnis, Sammlung, Begrüßung und Elternbereich (Tablet)."""

import random

from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.slider import Slider
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from lernfuchs import adaptive
from lernfuchs import theme as T
from lernfuchs.content import topics as TP
from lernfuchs.storage import STARS_PER_STICKER, STICKERS, today
from .ui import AnimImg, Box, C, EmojiImg, NumPad, Progress, RButton, Txt, toast

TIPS = ["Profis lesen die Aufgabe zweimal – dann erst antworten.", "Schnell UND richtig bringt Blitz-Bonus.",
        "Ab Stufe 6 wird es PROFI – Stoff der nächsten Klasse.", "Am Ende jeder Runde wartet eine Boss-Aufgabe.",
        "Knobel-Sonderaufgaben bringen +3 XP extra.", "Kurze Pausen machen dein Gehirn schneller."]


class BaseScreen(Screen):
    def __init__(self, app, **kw):
        super().__init__(**kw)
        self.app = app
        self.root = FloatLayout()
        with self.root.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*C(T.BG))
            self._bg = Rectangle(pos=self.root.pos, size=self.root.size)
        self.root.bind(size=lambda *_: setattr(self._bg, "size", self.root.size))
        self.add_widget(self.root)
        self.col = BoxLayout(orientation="vertical", padding=(dp(22), dp(14)), spacing=dp(12))
        self.root.add_widget(self.col)

    def header(self, title, emoji, color=None, back=None, right=None):
        bar = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(64), spacing=dp(12))
        bar.add_widget(RButton("", on_press=back or self.app.go_home, bg=T.NEUTRAL_BTN, icon="⬅️", icon_size=26,
                               size_hint=(None, None), size=(dp(62), dp(58)), pos_hint={"center_y": 0.5}))
        bar.add_widget(EmojiImg(emoji, 44, pos_hint={"center_y": 0.5}))
        bar.add_widget(Txt(title, fs=30, color=color or T.TEXT, bold=True, halign="left"))
        if right:
            bar.add_widget(right)
        self.col.add_widget(bar)
        return bar


def level_dots(level, color):
    row = BoxLayout(orientation="horizontal", size_hint=(None, None), size=(dp(8 * 14 + 8), dp(12)), spacing=dp(4))
    for i in range(8):
        on = i < level
        d = Box(bg=(T.GOLD if i >= 5 else color) if on else T.DOT_OFF, radius=6, size_hint=(None, None),
                size=(dp(10), dp(10)))
        row.add_widget(d)
    return row


class HomeScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        p = app.profile
        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(84), spacing=dp(14))
        top.add_widget(AnimImg("Fox", 78))
        hello = BoxLayout(orientation="vertical")
        hello.add_widget(Txt(f"Hallo {p.data['name'] or 'du'}!", fs=34, bold=True, halign="left"))
        hello.add_widget(Txt(random.choice(TIPS), fs=16, color=T.MUTED, halign="left"))
        top.add_widget(hello)
        for icon, text, cb, w in [("🔥", str(p.streak_days()), None, 90), ("⭐", f"{p.data['stars']} XP",
                                  lambda: app.open("collection"), 150), ("🏅", "Sammlung", lambda: app.open("collection"), 170),
                                  ("🔒", "", lambda: app.open("gate"), 64)]:
            top.add_widget(RButton(text, on_press=cb, bg=T.NEUTRAL_BTN, fg=T.TEXT, icon=icon, icon_size=28, fs=19,
                                   size_hint=(None, None), size=(dp(w), dp(58)), pos_hint={"center_y": 0.5}))
        self.col.add_widget(top)
        # Rang & Tagesziel
        stats = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(70), spacing=dp(12))
        rname, remo, rlo, rhi = T.rank_for(p.data["stars"])
        rc = Box(bg=T.CARD, border=T.CARD_BORDER, radius=18, orientation="horizontal", padding=(dp(14), dp(8)),
                 spacing=dp(10))
        rc.add_widget(EmojiImg(remo, 40, pos_hint={"center_y": 0.5}))
        rv = BoxLayout(orientation="vertical", spacing=dp(3))
        rv.add_widget(Txt(f"Rang: {rname}", fs=18, color=T.GOLD, bold=True, halign="left"))
        pr = Progress(color=T.GOLD, size_hint_y=None, height=dp(9))
        pr.value = 1 if rhi is None else (p.data["stars"] - rlo) / (rhi - rlo)
        rv.add_widget(pr)
        rv.add_widget(Txt("Höchster Rang!" if rhi is None else f"Noch {rhi - p.data['stars']} XP bis zum nächsten Rang",
                          fs=13, color=T.MUTED, halign="left"))
        rc.add_widget(rv)
        stats.add_widget(rc)
        done_today = sum(s["total"] for s in p.data["sessions"] if s["date"] == today())
        goal = int(p.settings.get("daily_goal", 20))
        gc = Box(bg=T.CARD, border=T.CARD_BORDER, radius=18, orientation="horizontal", padding=(dp(14), dp(8)),
                 spacing=dp(10))
        gc.add_widget(EmojiImg("🎯", 34, pos_hint={"center_y": 0.5}))
        gv = BoxLayout(orientation="vertical")
        gv.add_widget(Txt(f"Tagesziel: {done_today} / {goal}", fs=18, bold=True, halign="left"))
        gp = Progress(color=T.GOOD, size_hint_y=None, height=dp(12))
        gp.value = min(1, done_today / max(1, goal))
        gv.add_widget(gp)
        gc.add_widget(gv)
        stats.add_widget(gc)
        self.col.add_widget(stats)
        self.col.add_widget(RButton("Tagesmix  ·  alle Fächer, mit Boss-Aufgabe", on_press=lambda: app.start_session("mix"),
                                    bg=T.SUBJECTS["mix"][0], icon="🎲", icon_size=48, fs=26, radius=26,
                                    size_hint_y=None, height=dp(86)))
        grid = GridLayout(cols=2, spacing=dp(14))
        for subj in ("deutsch", "mathe", "sach", "konz"):
            c, light, _ = T.SUBJECTS[subj]
            topics = TP.topics_for(subj, p.grade)
            levels = [adaptive.level_for(p, subj, t.skill) for t in topics if t.kind == "tasks"]
            avg = round(sum(levels) / len(levels)) if levels else 1
            card = RButton("", on_press=lambda s=subj: app.open_subject(s), bg=light, radius=26)
            card.border = C(c)
            card.padding = (dp(24), dp(12))
            card.spacing = dp(18)
            card.add_widget(EmojiImg(T.SUBJECT_EMOJI[subj], 76, pos_hint={"center_y": 0.5}))
            v = BoxLayout(orientation="vertical", spacing=dp(4), padding=(0, dp(20)))
            v.add_widget(Txt(T.SUBJECT_NAMES[subj], fs=28, color=c, bold=True, halign="left"))
            v.add_widget(Txt(f"{len(topics)} Themen · Ø Stufe {avg}" + (" · PROFI" if avg >= 6 else ""), fs=16,
                             color=T.MUTED, halign="left"))
            v.add_widget(level_dots(avg, c))
            card.add_widget(v)
            grid.add_widget(card)
        self.col.add_widget(grid)
        due = adaptive.due_entries(p)
        if due:
            self.col.add_widget(RButton(f"Fehler-Training: {len(due)} Aufgabe{'n' if len(due) != 1 else ''} zum Wiederholen",
                                        on_press=lambda: app.start_session("mix", review_only=True), bg=T.GOLD,
                                        fg="#1D2438", icon="🔁", fs=20, size_hint_y=None, height=dp(58)))


class SubjectScreen(BaseScreen):
    def __init__(self, app, subject, **kw):
        super().__init__(app, **kw)
        c, light, _ = T.SUBJECTS[subject]
        mix = RButton("Konzentrations-Mix" if subject == "konz" else "Alles gemischt",
                      on_press=lambda: app.start_session(subject), bg=c, icon="🎲", fs=19,
                      size_hint=(None, None), size=(dp(270), dp(56)), pos_hint={"center_y": 0.5})
        self.header(T.SUBJECT_NAMES[subject], T.SUBJECT_EMOJI[subject], color=c, right=mix)
        p = app.profile
        topics = TP.topics_for(subject, p.grade, ("tasks", "game"))
        sv = ScrollView(do_scroll_x=False, bar_width=dp(6))
        g = GridLayout(cols=3, spacing=dp(12), size_hint_y=None, row_default_height=dp(104), row_force_default=True)
        g.bind(minimum_height=g.setter("height"))
        for t in topics:
            card = RButton("", on_press=lambda t=t: app.open_topic(t), bg=T.CARD, radius=20)
            card.border = C(T.CARD_BORDER)
            card.padding = (dp(14), dp(10))
            card.spacing = dp(12)
            card.add_widget(EmojiImg(t.emoji, 50, pos_hint={"center_y": 0.5}))
            v = BoxLayout(orientation="vertical", spacing=dp(2))
            v.add_widget(Txt(t.title, fs=19, bold=True, halign="left"))
            if t.desc:
                v.add_widget(Txt(t.desc, fs=13, color=T.MUTED, halign="left"))
            if t.kind == "tasks":
                v.add_widget(level_dots(adaptive.level_for(p, subject, t.skill), c))
            else:
                v.add_widget(Txt("Spiel", fs=13, color=c, bold=True, halign="left"))
            card.add_widget(v)
            g.add_widget(card)
        sv.add_widget(g)
        self.col.add_widget(sv)


class ResultScreen(BaseScreen):
    def __init__(self, app, subject, topic, correct, total, xp, seconds, levelups=(), new_sticker=False, boss=False,
                 combo=0, blitz=0, rank_before="", review_only=False, detail=None, game=None, **kw):
        super().__init__(app, **kw)
        pct = correct / total if total else 0
        anim, title = ("Trophy", "Überragend!") if pct >= 0.9 else ("Rocket", "Starke Runde!") if pct >= 0.7 else \
            ("Flexed Biceps Light Skin Tone", "Gut trainiert!") if pct >= 0.4 else ("Brain", "Harte Runde – dranbleiben!")
        card = Box(bg=T.CARD, border=T.CARD_BORDER, radius=26, orientation="vertical", padding=dp(24), spacing=dp(10))
        a = AnchorLayout(size_hint_y=None, height=dp(140))
        a.add_widget(AnimImg(anim, 130))
        card.add_widget(a)
        card.add_widget(Txt(title, fs=38, bold=True, size_hint_y=None, height=dp(52)))
        card.add_widget(Txt(detail or f"{correct} von {total} richtig", fs=26, color=T.MUTED, size_hint_y=None,
                            height=dp(40)))
        self.xp_lbl = Txt("+0 XP", fs=32, bold=True, size_hint_y=None, height=dp(46))
        card.add_widget(self.xp_lbl)
        m, s = divmod(seconds, 60)
        card.add_widget(Txt(f"Zeit: {m}:{s:02d} min", fs=20, color=T.MUTED, size_hint_y=None, height=dp(30)))
        chips = [x for x in [("Boss besiegt" if boss else None), (f"Beste Serie: {combo}" if combo >= 3 else None),
                             (f"{blitz}× Blitz" if blitz else None)] if x]
        if chips:
            card.add_widget(Txt("  ·  ".join(chips), fs=18, color=T.GOLD, bold=True, size_hint_y=None, height=dp(30)))
        best = {}
        for name, lvl in levelups:
            best[name] = max(lvl, best.get(name, 0))
        for name, lvl in best.items():
            card.add_widget(Txt(f"Neue Stufe {lvl}: {name}", fs=18, color=T.PRIMARY, bold=True, size_hint_y=None,
                                height=dp(28)))
        if new_sticker:
            card.add_widget(Txt("Neues Abzeichen für deine Sammlung!", fs=20, color=T.GOOD, bold=True,
                                size_hint_y=None, height=dp(30)))
            app.sounds.play("sticker")
        btns = BoxLayout(orientation="horizontal", size_hint=(None, None), height=dp(68), spacing=dp(14),
                         pos_hint={"center_x": 0.5})
        w = 0
        color = T.SUBJECTS.get(subject, T.SUBJECTS["mix"])[0]
        if not review_only and not game:
            btns.add_widget(RButton("Nochmal", on_press=lambda: app.start_session(subject, topic), bg=color, icon="🔄",
                                    fs=22, size_hint=(None, None), size=(dp(210), dp(64))))
            w += dp(224)
        if game:
            btns.add_widget(RButton("Nochmal", on_press=lambda: app.open_topic(game), bg=color, icon="🔄",
                                    fs=22, size_hint=(None, None), size=(dp(210), dp(64))))
            w += dp(224)
        btns.add_widget(RButton("Übersicht", on_press=app.go_home, bg=T.GOOD, icon="🏠", fs=22,
                                size_hint=(None, None), size=(dp(210), dp(64))))
        btns.width = w + dp(210)
        card.add_widget(Widget())
        card.add_widget(btns)
        wrap = AnchorLayout(padding=(dp(120), dp(20)))
        wrap.add_widget(card)
        self.col.add_widget(wrap)
        if pct >= 0.7 and total:
            app.sounds.play("fertig")
        self._xp, self._shown = xp, 0
        Clock.schedule_interval(self._count, 0.04)
        if total:
            app.speaker.say(result_speech(app.profile, correct, total, levelups, boss, combo, blitz, rank_before)
                            if not detail else f"{title} {detail}.")

    def _count(self, dt):
        self._shown = min(self._xp, self._shown + max(1, self._xp // 20))
        self.xp_lbl.text = f"+{self._shown} XP"
        return self._shown < self._xp


ZAHLWORT = ["null", "eine", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf", "zwölf"]


def _zw(n):
    return ZAHLWORT[n] if 0 <= n < len(ZAHLWORT) else str(n)


def result_speech(profile, correct, total, levelups, boss, combo, blitz, rank_before):
    name = profile.data.get("name") or ""
    pct = correct / total if total else 0
    if pct == 1:
        parts = [random.choice([f"{name}, fehlerfrei! Alle {_zw(total)} Aufgaben richtig.",
                                f"Perfekte Runde, {name}! Keine einzige falsch."])]
    elif pct >= 0.8:
        parts = [random.choice([f"Richtig stark, {name}! {_zw(correct)} von {_zw(total)}.", "Sehr gute Runde!"])]
    elif pct >= 0.5:
        parts = [random.choice([f"Gut gekämpft, {name}! {_zw(correct)} von {_zw(total)}.",
                                "Mehr als die Hälfte geschafft. Die Fehler üben wir noch."])]
    else:
        parts = [f"Das war eine harte Runde, {name}. Genau so wird man besser!"]
    if boss:
        parts.append("Und den Boss hast du auch besiegt!")
    if levelups:
        n, lvl = levelups[-1]
        parts.append(f"Neue Stufe {lvl} in {n}" + (" – das ist schon Profi-Niveau!" if lvl >= 6 else "!"))
    if combo >= 5:
        parts.append(f"Deine beste Serie: {_zw(combo)} richtige hintereinander.")
    rname, _, _, nxt = T.rank_for(profile.data["stars"])
    if rname != rank_before:
        parts.append(f"Neuer Rang: {rname}!")
    elif nxt:
        parts.append(f"Noch {nxt - profile.data['stars']} X P bis zum nächsten Rang.")
    return " ".join(parts)


class CollectionScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        p = app.profile
        self.header("Meine Sammlung", "🏅", color=T.PRIMARY)
        n = p.data["stickers"]
        to_next = STARS_PER_STICKER - p.data["stars"] % STARS_PER_STICKER
        self.col.add_widget(Txt(f"{n} von {len(STICKERS)} Abzeichen  ·  noch {to_next} XP bis zum nächsten",
                                fs=18, color=T.MUTED, size_hint_y=None, height=dp(28)))
        g = GridLayout(cols=10, spacing=dp(10), padding=dp(20))
        for i, st in enumerate(STICKERS):
            cell = Box(bg=T.GOLD_LIGHT if i < n else T.LOCKED, radius=16)
            img = EmojiImg(st, 54, pos_hint={"center_x": 0.5, "center_y": 0.5})
            img.opacity = 1 if i < n else 0.18
            a = AnchorLayout()
            a.add_widget(img)
            cell.add_widget(a)
            g.add_widget(cell)
        self.col.add_widget(g)


class WelcomeScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        card = Box(bg=T.CARD, border=T.CARD_BORDER, radius=26, orientation="vertical", padding=dp(30), spacing=dp(14))
        a = AnchorLayout(size_hint_y=None, height=dp(140))
        a.add_widget(AnimImg("Fox", 130))
        card.add_widget(a)
        card.add_widget(Txt("Willkommen bei LernFuchs!", fs=36, color=T.PRIMARY, bold=True, size_hint_y=None,
                            height=dp(50)))
        card.add_widget(Txt("Wie heißt du?", fs=24, bold=True, size_hint_y=None, height=dp(36)))
        self.name_in = TextInput(multiline=False, font_size=dp(28), halign="center", size_hint=(None, None),
                              size=(dp(380), dp(60)), pos_hint={"center_x": 0.5}, background_color=C(T.INPUT_BG),
                              foreground_color=C(T.TEXT), cursor_color=C(T.TEXT))
        card.add_widget(self.name_in)
        card.add_widget(Txt("In welche Klasse gehst du?", fs=22, bold=True, size_hint_y=None, height=dp(34)))
        row = BoxLayout(orientation="horizontal", size_hint=(None, None), size=(dp(560), dp(58)), spacing=dp(12),
                        pos_hint={"center_x": 0.5})
        self.grade = app.profile.grade
        self.gbtns = {}
        for g in (2, 3, 4):
            b = RButton(f"{g}. Klasse", on_press=lambda g=g: self._pick(g), bg=T.PRIMARY if g == self.grade else
                        T.NEUTRAL_BTN, fg=T.ON_ACCENT if g == self.grade else T.TEXT, fs=20)
            self.gbtns[g] = b
            row.add_widget(b)
        card.add_widget(row)
        card.add_widget(RButton("Los geht's!", on_press=self._go, bg=T.PRIMARY, icon="🚀", fs=24,
                                size_hint=(None, None), size=(dp(280), dp(66)), pos_hint={"center_x": 0.5}))
        wrap = AnchorLayout(padding=(dp(160), dp(30)))
        wrap.add_widget(card)
        self.col.add_widget(wrap)

    def _pick(self, g):
        self.grade = g
        for k, b in self.gbtns.items():
            b.set_bg(T.PRIMARY if k == g else T.NEUTRAL_BTN)
            b.set_fg(T.ON_ACCENT if k == g else T.TEXT)

    def _go(self):
        name = self.name_in.text.strip()
        if not name:
            self.name_in.background_color = C(T.BAD_LIGHT)
            return
        p = self.app.profile
        p.data["name"] = name
        p.settings["grade"] = self.grade
        p.save()
        self.app.speaker.say(f"Hallo {name}! Schön, dass du da bist. Los geht's!", force=True)
        self.app.go_home()


class GateScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        self.header("Elternbereich", "🔒")
        self.a, self.b = random.randint(6, 9), random.randint(12, 19)
        card = Box(bg=T.CARD, border=T.CARD_BORDER, radius=24, orientation="vertical", padding=dp(24), spacing=dp(12),
                   size_hint=(None, None), size=(dp(460), dp(560)), pos_hint={"center_x": 0.5})
        card.add_widget(Txt("Nur für Erwachsene", fs=26, bold=True, size_hint_y=None, height=dp(40)))
        card.add_widget(Txt(f"Bitte löse:  {self.a} × {self.b} = ?", fs=24, color=T.MUTED, size_hint_y=None,
                            height=dp(36)))
        self.entry = TextInput(multiline=False, readonly=True, font_size=dp(28), halign="center",
                               size_hint=(None, None), size=(dp(220), dp(60)), pos_hint={"center_x": 0.5},
                               background_color=C(T.INPUT_BG), foreground_color=C(T.TEXT))
        card.add_widget(self.entry)
        pad = NumPad(self.entry, pos_hint={"center_x": 0.5})
        card.add_widget(pad)
        card.add_widget(RButton("Öffnen", on_press=self._check, bg=T.PRIMARY, icon="🔓", fs=22,
                                size_hint=(None, None), size=(dp(220), dp(60)), pos_hint={"center_x": 0.5}))
        a = AnchorLayout()
        a.add_widget(card)
        self.col.add_widget(a)

    def _check(self):
        if self.entry.text.strip() == str(self.a * self.b):
            self.app.open("parent")
        else:
            self.entry.text = ""
            self.entry.background_color = C(T.BAD_LIGHT)


class ParentScreen(BaseScreen):
    def __init__(self, app, **kw):
        super().__init__(app, **kw)
        self.p = app.profile
        st = self.p.settings
        save = RButton("Speichern", on_press=self._save, bg=T.GOOD, icon="💾", fs=20, size_hint=(None, None),
                       size=(dp(200), dp(56)), pos_hint={"center_y": 0.5})
        self.header("Elternbereich", "🔓", right=save)
        sv = ScrollView(do_scroll_x=False, bar_width=dp(6))
        box = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(12), padding=(dp(10), dp(6)))
        box.bind(minimum_height=box.setter("height"))
        self.w = {}

        def seg(key, values, current, labels=None, width=70):
            row = BoxLayout(orientation="horizontal", size_hint=(None, None), height=dp(48), spacing=dp(6))
            btns = {}

            def pick(v):
                self.w[key] = v
                for k, b in btns.items():
                    b.set_bg(T.PRIMARY if k == v else T.NEUTRAL_BTN)
                    b.set_fg(T.ON_ACCENT if k == v else T.TEXT)
            for i, v in enumerate(values):
                b = RButton((labels or values)[i] if labels else str(v), on_press=lambda v=v: pick(v), bg=T.NEUTRAL_BTN,
                            fg=T.TEXT, fs=16, size_hint=(None, 1), width=dp(width), radius=12)
                btns[v] = b
                row.add_widget(b)
            row.width = len(values) * dp(width + 6)
            pick(current)
            return row

        def line(label, widget, hint=""):
            r = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(62), spacing=dp(14))
            lv = BoxLayout(orientation="vertical", size_hint=(None, 1), width=dp(320))
            lv.add_widget(Txt(label, fs=18, bold=True, halign="left"))
            if hint:
                lv.add_widget(Txt(hint, fs=12, color=T.MUTED, halign="left"))
            r.add_widget(lv)
            r.add_widget(widget)
            r.add_widget(Widget())
            box.add_widget(r)

        self.name_in = TextInput(text=self.p.data["name"], multiline=False, font_size=dp(20), size_hint=(None, None),
                              size=(dp(300), dp(48)), background_color=C(T.INPUT_BG), foreground_color=C(T.TEXT))
        line("Name des Kindes", self.name_in)
        line("Klasse", seg("grade", [2, 3, 4], self.p.grade), "Bestimmt Zahlenraum, Themen und Wortschatz.")
        box.add_widget(Txt("Mindeststufe & Sanduhr je Fach (die Stufe passt sich immer an; 6–8 = PROFI)", fs=17,
                           color=T.PRIMARY, bold=True, halign="left", size_hint_y=None, height=dp(30)))
        for subj in ("deutsch", "mathe", "sach", "konz"):
            d = int(st["difficulty"].get(subj, 1) or 1)
            line(f"{T.SUBJECT_NAMES[subj]} – ab Stufe", seg(f"diff_{subj}", list(range(1, 9)), d, width=52))
            t = int(st["timer"].get(subj, 0) or 0)
            opts = [0, 20, 30, 45, 60, 90]
            line(f"{T.SUBJECT_NAMES[subj]} – Sanduhr", seg(f"timer_{subj}", opts, t if t in opts else 30,
                                                              labels=["Aus", "20 s", "30 s", "45 s", "60 s", "90 s"]))
        line("Aufgaben pro Runde", seg("tasks", [5, 10, 15, 20], int(st["tasks_per_round"])))
        line("Bewegungspause", seg("break", [0, 5, 8, 12], int(st.get("break_every", 8)),
                                   labels=["Aus", "alle 5", "alle 8", "alle 12"], width=90))
        line("Sonder- & Boss-Aufgaben", seg("specials", [True, False], bool(st.get("specials", True)),
                                            labels=["An", "Aus"]))
        line("Aufgaben vorlesen", seg("tts", [True, False], bool(st.get("tts", True)), labels=["An", "Aus"]))
        self.rate = Slider(min=0.6, max=1.3, value=float(st.get("tablet_rate", 0.95)), size_hint=(None, None),
                           size=(dp(300), dp(40)))
        line("Sprechtempo", self.rate)
        sess = self.p.data["sessions"]
        tasks = sum(s["total"] for s in sess)
        ok = sum(s["correct"] for s in sess)
        box.add_widget(Txt(f"Fortschritt: {len(sess)} Runden · {tasks} Aufgaben · "
                           f"{round(100 * ok / tasks) if tasks else 0} % richtig · {self.p.data['stars']} XP",
                           fs=17, color=T.MUTED, halign="left", size_hint_y=None, height=dp(32)))
        for subj in ("deutsch", "mathe", "sach", "konz"):
            parts = []
            for t in TP.topics_for(subj, self.p.grade, ("tasks",)):
                sk = self.p.data["skills"].get(t.skill)
                if sk:
                    parts.append(f"{t.title} {sk['level']:.1f}")
            if parts:
                box.add_widget(Txt(f"{T.SUBJECT_NAMES[subj]}: " + " · ".join(parts), fs=14, halign="left",
                                   size_hint_y=None, height=dp(44)))
        sv.add_widget(box)
        self.col.add_widget(sv)

    def _save(self):
        st = self.p.settings
        w = self.w
        if self.name_in.text.strip():
            self.p.data["name"] = self.name_in.text.strip()
        st["grade"] = w["grade"]
        for subj in ("deutsch", "mathe", "sach", "konz"):
            st["difficulty"][subj] = w[f"diff_{subj}"]
            st["timer"][subj] = w[f"timer_{subj}"]
            for key, sk in self.p.data["skills"].items():
                if key.startswith(subj + ".") and sk["level"] < w[f"diff_{subj}"]:
                    sk["level"] = float(w[f"diff_{subj}"])
        st["tasks_per_round"] = w["tasks"]
        st["break_every"] = w["break"]
        st["specials"] = w["specials"]
        st["tts"] = w["tts"]
        st["tablet_rate"] = round(self.rate.value, 2)
        self.p.save()
        self.app.apply_settings()
        toast(self.root, "Gespeichert!", "Gem Stone", color=T.GOOD_LIGHT)
        self.app.speaker.say("Einstellungen gespeichert.", force=True)
