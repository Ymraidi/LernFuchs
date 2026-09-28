"""Übungsrunde auf dem Tablet – gleiche Logik wie am PC (Stufen, Fehlerbox, Boss-, Sonder- und Fokus-Aufgaben)."""

import random
import time

from kivy.animation import Animation
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import Screen
from kivy.uix.widget import Widget

from lernfuchs import adaptive
from lernfuchs import theme as T
from lernfuchs.content import topics as TP
from lernfuchs.storage import today
from .taskview import TaskView
from .ui import MY_BEYS, AnimImg, BeyTop, Box, C, EmojiImg, Hourglass, Progress, RButton, Txt, fly_up, toast

PRAISE = ["Richtig!", "Stark gelöst!", "Präzise!", "Sauber!", "Genau so!", "Treffer!", "Top!", "Klar erkannt!",
          "Souverän!"]
SPOKEN_PRAISE = ["Richtig!", "Stark gelöst!", "Genau so!", "Sauber!", "Treffer!", "Super, das stimmt!",
                 "Klasse gemacht!", "Perfekt!", "Ja, genau!"]
SPOKEN_FAST = ["Blitzschnell!", "Das ging ja schnell!", "Wow, schnell und richtig!"]
ENCOURAGE = ["Knapp daneben.", "Nicht ganz.", "Guter Versuch.", "Das holen wir uns noch!"]
CORRECT_ANIMS = ["Party Popper", "Clapping Hands Light Skin Tone", "Star-Struck", "Glowing Star", "Hundred Points",
                 "Smiling Face with Sunglasses"]
WRONG_ANIMS = ["Thinking Face", "Face with Monocle"]
BREAKS = [("🤸", "Aktiv-Pause", "Mach 10 Hampelmänner – so schnell du kannst."),
          ("🦩", "Flamingo-Pause", "Stehe auf einem Bein und zähle bis 15. Dann das andere Bein!"),
          ("🎈", "Luftballon-Atmen", "Atme tief ein wie ein Luftballon … und langsam wieder aus. 5 Mal!"),
          ("🙆", "Streck dich!", "Strecke dich ganz groß zur Decke – und mach dich dann ganz klein. 3 Mal!"),
          ("👀", "Augen-Pause", "Schau aus dem Fenster in die Ferne und zähle bis 20.")]
MIX_SUBJECTS = ["deutsch", "mathe", "sach", "mathe", "deutsch", "konz"]


class SessionScreen(Screen):
    def __init__(self, app, subject, topic=None, review_only=False, **kw):
        super().__init__(**kw)
        self.app, self.subject, self.topic, self.review_only = app, subject, topic, review_only
        self.profile = app.profile
        self.color = T.SUBJECTS.get(subject, T.SUBJECTS["mix"])[0]
        self.n_target = int(self.profile.settings["tasks_per_round"])
        self.queue, self.done, self.correct, self.xp, self.combo, self.extra = [], 0, 0, 0, 0, 0
        self.levelups, self.mistakes = [], []
        self.mix_i = random.randrange(len(MIX_SUBJECTS))
        self.specials_done, self.boss_done, self.boss_won, self.best_combo, self.blitz = 0, False, False, 0, 0
        self.rank_before = T.rank_for(self.profile.data["stars"])[0]
        self.t_start = time.monotonic()
        self.view = self.current = None
        self.feedback_visible = False
        self._auto = None
        self._build_reviews()
        self._build_ui()
        Clock.schedule_once(lambda *_: self._countdown(), 0.3)

    def _countdown(self):
        """„3 – 2 – 1 – Let it rip!“ vor dem Start."""
        lbl = Txt("3", fs=110, color=T.GOLD, bold=True, wrap=False)
        self.body.add_widget(lbl)
        self.app.speaker.say("Drei, zwei, eins – Let it rip!", force=True)
        seq = ["3", "2", "1", "LET IT RIP!"]

        def show(i):
            if i >= len(seq):
                self.body.remove_widget(lbl)
                self.my_bey.boost(to=1400, back=540)
                self.rival_bey.boost(to=1400, back=540)
                return self._next()
            lbl.text = seq[i]
            lbl.font_size = dp(110 if i < 3 else 80)
            lbl.opacity = 0
            Animation(opacity=1, d=0.15).start(lbl)
            self.app.sounds.play("klick" if i < 3 else "stufe")
            Clock.schedule_once(lambda *_: show(i + 1), 0.6 if i < 3 else 0.8)
        show(0)

    # --- Aufbau ---------------------------------------------------------------------------
    def _build_reviews(self):
        due = adaptive.due_entries(self.profile, self.subject, skill=self.topic.skill if self.topic else None)
        random.shuffle(due)
        limit = self.n_target if self.review_only else max(1, int(self.n_target * 0.3))
        reviews = []
        for e in due[:limit]:
            t = adaptive.task_from_entry(e)
            if t:
                t._meta = {"review_key": e["key"]}
                reviews.append(t)
        if self.review_only:
            self.queue, self.n_target = reviews, len(reviews)
            self._pending_reviews, self._review_slots = [], []
        else:
            self._pending_reviews = reviews
            self._review_slots = sorted(random.sample(range(1, max(2, self.n_target)),
                                                      min(len(reviews), max(1, self.n_target - 1))))

    def _build_ui(self):
        root = FloatLayout()
        with root.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*C(T.BG))
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(size=lambda *_: setattr(self._bg, "size", root.size))
        col = BoxLayout(orientation="vertical", padding=(dp(18), dp(10)), spacing=dp(8))
        top = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(96), spacing=dp(12))
        top.add_widget(RButton("", on_press=self._quit, bg=T.NEUTRAL_BTN, icon="✖️", icon_size=24,
                               size_hint=(None, None), size=(dp(58), dp(58)), pos_hint={"center_y": 0.5}))
        title = self.topic.title if self.topic else ("Fehler-Training" if self.review_only
                                                      else T.SUBJECT_NAMES.get(self.subject, ""))
        emo = self.topic.emoji if self.topic else T.SUBJECT_EMOJI.get(self.subject, "🎲")
        top.add_widget(EmojiImg(emo, 40, pos_hint={"center_y": 0.5}))
        top.add_widget(Txt(title, fs=24, bold=True, halign="left"))
        self.level_lbl = Txt("", fs=15, color=T.MUTED, wrap=False, size_hint=(None, 1), width=dp(150))
        top.add_widget(self.level_lbl)
        self.combo_lbl = Txt("", fs=20, color=T.PRIMARY, bold=True, wrap=False, size_hint=(None, 1), width=dp(70))
        top.add_widget(self.combo_lbl)
        top.add_widget(EmojiImg("⭐", 34, pos_hint={"center_y": 0.5}))
        self.xp_lbl = Txt("0", fs=24, bold=True, wrap=False, size_hint=(None, 1), width=dp(60))
        top.add_widget(self.xp_lbl)
        self.hourglass = Hourglass(pos_hint={"center_y": 0.5})
        top.add_widget(self.hourglass)
        col.add_widget(top)
        prow = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(18), spacing=dp(10))
        self.progress = Progress(color=self.color, size_hint_y=None, height=dp(14), pos_hint={"center_y": 0.5})
        prow.add_widget(self.progress)
        self.count_lbl = Txt("", fs=15, color=T.MUTED, wrap=False, size_hint=(None, 1), width=dp(70))
        prow.add_widget(self.count_lbl)
        col.add_widget(prow)
        # Arena: dein Kreisel gegen den Rivalen – Ausdauerbalken
        my = int(self.profile.settings.get("my_bey", 0))
        rival = random.choice([i for i in range(len(MY_BEYS)) if i != my])
        self.rival_name = MY_BEYS[rival][0]
        arena = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(58), spacing=dp(10))
        self.my_bey = BeyTop(54, my, glow=True, pos_hint={"center_y": 0.5})
        arena.add_widget(self.my_bey)
        mcol = BoxLayout(orientation="vertical", spacing=dp(2))
        mcol.add_widget(Txt(f"{MY_BEYS[my][0]} ({self.profile.data.get('name') or 'Du'})", fs=13, color=T.ELECTRIC,
                            bold=True, halign="left"))
        self.my_bar = Progress(color=T.ELECTRIC, size_hint_y=None, height=dp(12))
        self.my_bar.value = 1
        mcol.add_widget(self.my_bar)
        arena.add_widget(mcol)
        arena.add_widget(Txt("VS", fs=22, color=T.GOLD, bold=True, wrap=False, size_hint=(None, 1), width=dp(50)))
        rcol = BoxLayout(orientation="vertical", spacing=dp(2))
        rcol.add_widget(Txt(f"Rivale: {self.rival_name}", fs=13, color=T.PRIMARY, bold=True, halign="right"))
        self.rival_bar = Progress(color=T.PRIMARY, size_hint_y=None, height=dp(12))
        self.rival_bar.value = 1
        rcol.add_widget(self.rival_bar)
        arena.add_widget(rcol)
        self.rival_bey = BeyTop(54, rival, glow=True, pos_hint={"center_y": 0.5})
        arena.add_widget(self.rival_bey)
        col.add_widget(arena)
        self.my_hp, self.rival_hp = 1.0, 1.0
        self.card = Box(bg=T.CARD, border=T.CARD_BORDER, radius=24, orientation="vertical", padding=dp(14))
        tools = BoxLayout(orientation="horizontal", size_hint_y=None, height=dp(50), spacing=dp(8))
        tools.add_widget(Widget())
        tools.add_widget(RButton("", on_press=lambda: self.view and self.view.speak(), bg=self.light, icon="🔊",
                                 icon_size=28, size_hint=(None, None), size=(dp(60), dp(50))))
        self.hint_btn = RButton("", on_press=self._hint, bg=T.GOLD_LIGHT, icon="💡", icon_size=28,
                                size_hint=(None, None), size=(dp(60), dp(50)))
        tools.add_widget(self.hint_btn)
        self.card.add_widget(tools)
        self.body = FloatLayout()
        self.card.add_widget(self.body)
        col.add_widget(self.card)
        self.fb = Box(bg=T.GOOD_LIGHT, radius=22, orientation="horizontal", size_hint_y=None, height=dp(96),
                      padding=(dp(16), dp(8)), spacing=dp(12))
        self.fb_anim = AnchorLayout(size_hint=(None, 1), width=dp(70))
        self.fb.add_widget(self.fb_anim)
        txt = BoxLayout(orientation="vertical")
        self.fb_title = Txt("", fs=24, bold=True, halign="left")
        self.fb_text = Txt("", fs=17, halign="left")
        txt.add_widget(self.fb_title)
        txt.add_widget(self.fb_text)
        self.fb.add_widget(txt)
        self.next_btn = RButton("Weiter", on_press=self._next, bg=T.GOOD, icon="➡️", fs=22,
                                size_hint=(None, None), size=(dp(180), dp(64)), pos_hint={"center_y": 0.5})
        self.fb.add_widget(self.next_btn)
        self._col = col
        root.add_widget(col)
        self.root = root
        self.add_widget(root)

    @property
    def light(self):
        return T.SUBJECTS.get(self.subject, T.SUBJECTS["mix"])[1]

    # --- Ablauf -------------------------------------------------------------------------
    def _total(self):
        return max(self.n_target + self.extra, self.done + len(self.queue) + (1 if self.current else 0))

    def _generate(self, ahead=0):
        if self.subject == "mix":
            subj = MIX_SUBJECTS[self.mix_i % len(MIX_SUBJECTS)]
            self.mix_i += 1
            topic = TP.random_topic(subj, self.profile.grade)
        elif self.topic:
            topic = self.topic
        else:
            topic = TP.random_topic(self.subject, self.profile.grade)
        lvl = adaptive.level_for(self.profile, topic.subject, topic.skill)
        badge, bonus = None, 0
        remaining = self.n_target + self.extra - self.done - ahead
        pos = self.done + ahead
        specials = self.profile.settings.get("specials", True)
        if remaining == 1 and not self.boss_done and self.n_target >= 5:
            self.boss_done = True
            lvl = min(8, lvl + 2)
            badge, bonus = "BOSS-AUFGABE · +2 Bonus", 2
        elif specials and self.done >= 2 and self.specials_done < 2 and not (self.topic and self.topic.special) \
                and random.random() < 0.2:
            self.specials_done += 1
            topic = TP.special_topic(self.subject if self.subject != "mix" else "mathe")
            lvl = adaptive.level_for(self.profile, topic.subject, topic.skill)
            badge, bonus = "SONDERAUFGABE · +3 Bonus", 3
        elif specials and pos % 4 == 2 and not (self.topic and (self.topic.fokus or self.topic.subject == "konz")):
            topic = TP.fokus_topic(topic.subject)
            lvl = adaptive.level_for(self.profile, topic.subject, topic.skill)
            badge, bonus = "FOKUS-AUFGABE · +1 Bonus", 1
        tasks = TP.generate(topic, self.profile.grade, lvl)
        for t in tasks:
            t._meta, t._level, t._badge, t._bonus = {}, lvl, badge, bonus
        return tasks

    def _next(self):
        if self._auto:
            self._auto.cancel()
            self._auto = None
        if self.feedback_visible or self.fb.parent:
            self._hide_feedback()
        self.feedback_visible = False
        if self.current is not None:
            self.done += 1
            self.current = None
            if self._maybe_break():
                return
        if self.view:
            self.view.cleanup()
            self.body.remove_widget(self.view)
            self.view = None
        task = None
        if self.queue:
            task = self.queue.pop(0)
        elif self.done < self.n_target + self.extra:
            if self._pending_reviews and self._review_slots and self.done >= self._review_slots[0]:
                self._review_slots.pop(0)
                task = self._pending_reviews.pop(0)
            else:
                tasks = self._generate()
                if tasks:
                    task, rest = tasks[0], tasks[1:]
                    self.queue = rest + self.queue
        if task is None:
            return self._finish()
        self.current = task
        Animation(value=self.done / max(1, self._total()), d=0.4, t="out_quad").start(self.progress)
        self.count_lbl.text = f"{self.done + 1} / {self._total()}"
        lv = getattr(task, "_level", None)
        self.level_lbl.text = (f"Stufe {lv}" + (" · PROFI" if lv and lv >= 6 else "")) if lv else "Wiederholung"
        self.level_lbl.color = C(T.GOLD if lv and lv >= 6 else T.MUTED)
        color = T.SUBJECTS.get(task.subject, T.SUBJECTS["mix"])[0]
        self.view = TaskView(self.app, task, color, self._on_answer, self._on_ready, size_hint=(1, 1),
                             pos_hint={"x": 0.08, "y": 0})
        self.view.opacity = 0
        self.body.add_widget(self.view)
        Animation(pos_hint={"x": 0, "y": 0}, opacity=1, d=0.25, t="out_cubic").start(self.view)
        self.hint_btn.opacity = 1 if task.hint else 0

    def _on_ready(self):
        t = self.current
        if t is None:
            return
        base = int(self.profile.settings["timer"].get(t.subject, 0) or 0)
        self.hourglass.start(round(base * t.time_factor) if base else 0, self._timeout)

    def _timeout(self):
        if self.view and not self.view.locked and not self.feedback_visible:
            self.view.locked = True
            self.view.attempts = max(1, self.view.attempts)
            self.app.sounds.play("zeit")
            self._on_answer(False, None, timeout=True)

    def _on_answer(self, correct, given, timeout=False):
        view, task = self.view, self.current
        if view is None or task is None:
            return
        self.hourglass.pause()
        ratio = self.hourglass.ratio()
        if not correct and not timeout and self.profile.settings.get("retry", True) and view.can_retry():
            self.app.sounds.play("falsch")
            view.allow_retry(given)
            self._shake()
            self._feedback(False, "Noch ein Versuch!", "Prüf die Aufgabe nochmal ganz genau.", "Face with Monocle",
                           retry=True)
            self.hourglass.resume()
            return
        view.show_result(correct, given)
        second = view.attempts > 1
        old, new = adaptive.record(self.profile, task.skill, correct, ratio, timeout, second, task.subject)
        if new != old:
            self.queue = [t for t in self.queue if not (getattr(t, "_pre", False) and t.skill == task.skill)]
        if new > old:
            topic = TP.BY_SKILL.get(task.skill)
            name = topic.title if topic else ""
            self.levelups.append((name, new))
            txt = f"Level up! Stufe {new} in „{name}“" + (" – PROFI!" if new >= 6 else "")
            Clock.schedule_once(lambda *_: (self.app.sounds.play("stufe"), toast(self.root, txt, "Rocket")), 0.4)
        meta = getattr(task, "_meta", {}) or {}
        if meta.get("review_key"):
            adaptive.review_result(self.profile, meta["review_key"], correct and not second, task.type)
        elif not correct or second:
            adaptive.add_mistake(self.profile, task)
        if not correct and not meta.get("repeat") and task.concept and self.extra < 4:
            rv = TP.review(task.concept, task.type)
            if rv:
                rv.skill, rv.subject = task.skill, task.subject
                rv._meta = {"repeat": True}
                self.queue.insert(min(2, len(self.queue)), rv)
                self.extra += 1
        if correct:
            self.correct += 1
            gained = 0 if second else 1
            extras = []
            fast = not second and ratio is not None and ratio < 0.35
            if fast:
                gained += 1
                self.blitz += 1
                extras.append("Blitz-Bonus")
            bonus = getattr(task, "_bonus", 0)
            if not second and bonus:
                gained += bonus
                extras.append({2: "Boss besiegt", 3: "Sonderaufgabe gelöst", 1: "Fokus-Bonus"}[bonus])
                self.boss_won = self.boss_won or bonus == 2
            self.combo = self.combo + 1 if not second else 0
            self.best_combo = max(self.best_combo, self.combo)
            if self.combo and self.combo % 5 == 0:
                gained += 3
                toast(self.root, f"{self.combo}er-Serie! +3 XP", "Fire")
            self.xp += gained
            self.xp_lbl.text = str(self.xp)
            self.combo_lbl.text = f"{self.combo}x" if self.combo >= 2 else ""
            if gained:
                fly_up(self.root, f"+{gained} XP", self.card.center)
            hit = (1.0 / max(1, self.n_target)) * (1.0 if not second else 0.5) * (1.6 if bonus == 2 else 1.1)
            self.rival_hp = max(0.0, self.rival_hp - hit)
            Animation(value=self.rival_hp, d=0.5, t="out_quad").start(self.rival_bar)
            self.my_bey.boost()
            self.rival_bey.wobble()
            if self.rival_hp <= 0.001 and not getattr(self, "_burst", False):
                self._burst = True
                toast(self.root, "BURST FINISH!", "Collision", seconds=2.5)
            self.app.sounds.play("richtig")
            text = "Im zweiten Versuch geschafft." if second else \
                (f"+{gained} XP" + (f"  ·  {', '.join(extras)}" if extras else ""))
            self._feedback(True, random.choice(PRAISE), text, "Collision" if bonus == 2 else random.choice(CORRECT_ANIMS))
            if self.profile.settings.get("tts") and not task.listen:
                self.app.speaker.say("Boss besiegt! Stark!" if bonus == 2 else
                                     random.choice(SPOKEN_FAST if fast else SPOKEN_PRAISE))
            if not task.explain or not second:
                self._advance_when_quiet(1.3)
        else:
            self.combo = 0
            self.combo_lbl.text = ""
            self.mistakes.append(task)
            self.my_hp = max(0.15, self.my_hp - 0.08)
            Animation(value=self.my_hp, d=0.5, t="out_quad").start(self.my_bar)
            self.my_bey.wobble()
            self.rival_bey.boost(to=1100)
            if not timeout:
                self.app.sounds.play("falsch")
            sol = self._solution(task)
            title = "Die Zeit ist um!" if timeout else random.choice(ENCOURAGE)
            self._feedback(False, title, sol, "Hourglass Done" if timeout else random.choice(WRONG_ANIMS))
            self._shake()
            if self.profile.settings.get("tts"):
                self.app.speaker.say(f"{title} {sol.splitlines()[0]}")
        self.profile.save()
        Clock.schedule_once(lambda *_: self._lookahead(), 0.3)

    def _lookahead(self):
        """Nächste Aufgabe vorbereiten, damit es ohne Pause weitergeht."""
        if self.queue or self.review_only or self.done + 1 >= self.n_target + self.extra:
            return
        if self._pending_reviews and self._review_slots and self.done + 1 >= self._review_slots[0]:
            return
        for t in self._generate(ahead=1):
            t._pre = True
            self.queue.append(t)

    def _advance_when_quiet(self, min_s, max_s=8.0):
        start = time.monotonic()

        def check(*_):
            if not self.feedback_visible:
                return
            waited = time.monotonic() - start
            if waited >= max_s or (waited >= min_s and not self.app.speaker.is_speaking()):
                self._auto = Clock.schedule_once(lambda *_: self._next(), 0.25)
                return
            self._auto = Clock.schedule_once(check, 0.12)
        self._auto = Clock.schedule_once(check, 0.4)

    def _solution(self, t):
        if t.type == "sort":
            return "Grün umrandet = richtige Gruppe."
        if t.type == "order":
            return "Richtig: " + (" – ".join(t.answer) if not all(len(x) <= 2 for x in t.answer) else "".join(t.answer))
        if t.type == "grid_click":
            return t.explain or "Das grüne Bild ist die Lösung."
        if t.type == "multi_click":
            return t.explain
        ans = f"Richtig: {t.answer}{(' ' + t.unit) if t.unit else ''}"
        return ans + (f"\n{t.explain}" if t.explain and t.explain not in ans else "")

    def _feedback(self, good, title, text, anim, retry=False):
        self.fb.bg = C(T.GOOD_LIGHT if good else (T.GOLD_LIGHT if retry else T.BAD_LIGHT))
        self.fb_anim.clear_widgets()
        self.fb_anim.add_widget(AnimImg(anim, 58))
        self.fb_title.text, self.fb_text.text = title, text
        self.next_btn.opacity = 0 if retry else 1
        self.next_btn.enabled = not retry
        self.next_btn.set_bg(T.GOOD if good else T.PRIMARY)
        if not self.fb.parent:
            self._col.add_widget(self.fb)
        self.fb.opacity = 0
        Animation(opacity=1, d=0.2).start(self.fb)
        if retry:
            Clock.schedule_once(lambda *_: (not self.feedback_visible) and self._hide_feedback(), 1.6)
        else:
            self.feedback_visible = True

    def _hide_feedback(self):
        if self.fb.parent:
            self._col.remove_widget(self.fb)

    def _shake(self):
        if not self.view:
            return
        v = self.view
        a = Animation(pos_hint={"x": -0.015, "y": 0}, d=0.05)
        for x in (0.015, -0.01, 0.01, -0.005, 0):
            a += Animation(pos_hint={"x": x, "y": 0}, d=0.05)
        a.start(v)

    def _hint(self):
        if self.current and self.current.hint:
            toast(self.root, self.current.hint, "Light Bulb", seconds=3.5)
            self.app.speaker.say(self.current.hint, force=True)

    def _maybe_break(self):
        every = int(self.profile.settings.get("break_every", 0) or 0)
        if not every or self.done % every != 0 or self._total() - self.done <= 1:
            return False
        if self.view:
            self.view.cleanup()
            self.body.remove_widget(self.view)
            self.view = None
        emo, title, text = random.choice(BREAKS)
        box = BoxLayout(orientation="vertical", spacing=dp(12), padding=dp(30))
        a = AnchorLayout(size_hint_y=None, height=dp(130))
        a.add_widget(EmojiImg(emo, 120))
        box.add_widget(a)
        box.add_widget(Txt(title, fs=34, color=self.color, bold=True, size_hint_y=None, height=dp(50)))
        box.add_widget(Txt(text, fs=24, size_hint_y=None, height=dp(90)))
        b = AnchorLayout(size_hint_y=None, height=dp(70))
        b.add_widget(RButton("Weiter geht's", on_press=lambda: (self.body.remove_widget(box), self._next()),
                             bg=T.GOOD, icon="💪", fs=22, size_hint=(None, None), size=(dp(280), dp(66))))
        box.add_widget(b)
        box.add_widget(Widget())
        self.body.add_widget(box)
        self.app.speaker.say(f"{title}. {text}", force=True)
        self.hourglass.start(20, None)
        self.count_lbl.text = "Pause"
        return True

    def _finish(self):
        self.hourglass.stop()
        secs = int(time.monotonic() - self.t_start)
        total = self.done
        self.xp += 2 if total >= 5 else 0
        new_sticker = self.profile.add_stars(self.xp) if self.xp else False
        self.profile.touch_streak()
        self.profile.log_session({"date": today(), "subject": self.subject,
                                  "topic": self.topic.id if self.topic else "",
                                  "title": self.topic.title if self.topic else T.SUBJECT_NAMES.get(self.subject, ""),
                                  "correct": self.correct, "total": total, "seconds": secs, "stars": self.xp})
        self.profile.save()
        self.app.show_result(subject=self.subject, topic=self.topic, correct=self.correct, total=total, xp=self.xp,
                             seconds=secs, levelups=self.levelups, new_sticker=new_sticker,
                             boss=self.boss_won, combo=self.best_combo, blitz=self.blitz, rank_before=self.rank_before,
                             review_only=self.review_only)

    def _quit(self):
        self.hourglass.stop()
        self.app.speaker.stop()
        if self.xp:
            self.profile.add_stars(self.xp)
        self.profile.save()
        self.app.go_home()

    def on_leave(self, *_):
        self.hourglass.stop()
        if self.view:
            self.view.cleanup()
