"""Eine Übungsrunde: Aufgaben, Sanduhr, Rückmeldung, Pausen, Wiederholungen."""

import random
import time

import customtkinter as ctk

from .. import adaptive
from .. import theme as T
from ..content import topics as TP
from ..emoji import emoji_image
from ..storage import today
from .task_view import TaskView
from .widgets import (CORRECT_ANIMS, WRONG_ANIMS, Card, Hourglass, Pads, Toast, anim_emoji, big_button,
                      count_up, darker, emoji_label, fly_up, shake, slide_in)

PRAISE = ["Richtig!", "Stark gelöst!", "Präzise!", "Sauber!", "Genau so!", "Treffer!", "Top!",
          "Klar erkannt!", "Souverän!", "Messerscharf!"]
PRAISE_EMOJI = ["✅", "🎯", "⚡", "🔥", "💎", "🏅", "🚀"]
ENCOURAGE = ["Knapp daneben.", "Nicht ganz.", "Guter Versuch.", "Das holen wir uns noch!"]

BREAKS = [
    ("🤸", "Aktiv-Pause", "Mach 10 Hampelmänner – so schnell du kannst."),
    ("🦩", "Flamingo-Pause!", "Stehe auf einem Bein und zähle bis 15. Dann das andere Bein!"),
    ("🎈", "Luftballon-Atmen", "Atme ganz tief ein wie ein Luftballon … und langsam wieder aus. 5 Mal!"),
    ("🐸", "Frosch-Pause!", "Mache 5 Froschsprünge durchs Zimmer."),
    ("🙆", "Streck dich!", "Strecke dich ganz groß zur Decke – und dann mach dich ganz klein. 3 Mal!"),
    ("👀", "Augen-Pause", "Schau aus dem Fenster in die Ferne und zähle bis 20."),
    ("🧘", "Stille-Pause", "Schließe die Augen und horche: Welche Geräusche hörst du?"),
    ("🦉", "Eulen-Pause", "Drehe deinen Kopf langsam nach links und rechts wie eine Eule. 5 Mal!"),
    ("✊", "Fäuste-Pause", "Mache 10 Mal ganz feste Fäuste und öffne die Hände wieder weit."),
]

MIX_SUBJECTS = ["deutsch", "mathe", "sach", "mathe", "deutsch", "konz"]

SPOKEN_PRAISE = ["Richtig!", "Stark gelöst!", "Genau so!", "Sauber!", "Treffer!", "Super, das stimmt!",
                 "Klasse gemacht!", "Perfekt!", "Ja, genau!", "Richtig gut!"]
SPOKEN_FAST = ["Blitzschnell!", "Das ging ja schnell!", "Wow, schnell und richtig!"]


class SessionScreen(ctk.CTkFrame):
    def __init__(self, app, subject: str, topic=None, review_only=False):
        super().__init__(app.container, fg_color=T.BG)
        self.app, self.subject, self.topic = app, subject, topic
        self.review_only = review_only
        self.profile = app.profile
        st = self.profile.settings
        self.color, self.light, _ = T.SUBJECTS.get(subject, T.SUBJECTS["mix"])
        self.n_target = int(st["tasks_per_round"])
        self.queue = []
        self.done = 0
        self.correct = 0
        self.stars = 0
        self.combo = 0
        self.extra = 0
        self.levelups = []
        self.mistakes = []
        self.mix_i = random.randrange(len(MIX_SUBJECTS))
        self.specials_done = 0
        self.boss_done = False
        self.best_combo = 0
        self.blitz = 0
        self.boss_won = False
        self.rank_before = T.rank_for(self.profile.data["stars"])[0]
        self.t_start = time.monotonic()
        self.view = None
        self.current = None
        self.feedback_visible = False
        self._auto_job = None
        self._build_reviews()
        self._build_ui()
        self.app.bind_key(self._on_key)
        self.after(50, self._next)

    # --- Aufbau ---------------------------------------------------------------
    def _build_reviews(self):
        due = adaptive.due_entries(self.profile, self.subject,
                                   skill=self.topic.skill if self.topic else None)
        random.shuffle(due)
        limit = self.n_target if self.review_only else max(1, int(self.n_target * 0.3))
        reviews = []
        for e in due[:limit]:
            task = adaptive.task_from_entry(e)
            if task:
                task._meta = {"review_key": e["key"]}
                reviews.append(task)
        if self.review_only:
            self.queue = reviews
            self.n_target = len(reviews)
        else:
            self._pending_reviews = reviews
            # Wiederholungen verteilt in die Runde einstreuen
            self._review_slots = sorted(random.sample(range(1, max(2, self.n_target)), min(len(reviews),
                                                                                         max(1, self.n_target - 1))))

    def _build_ui(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(14, 4))
        ctk.CTkButton(top, text="", image=emoji_image("✖️", 22), width=52, height=52, corner_radius=26,
                      fg_color=T.NEUTRAL_BTN, hover_color=T.NEUTRAL_HOVER, command=self._quit).pack(side="left")
        title = (self.topic.title if self.topic else
                 ("Fehler-Training" if self.review_only else T.SUBJECT_NAMES.get(self.subject, "")))
        emo = self.topic.emoji if self.topic else ("🔁" if self.review_only else T.SUBJECT_EMOJI.get(self.subject))
        ctk.CTkLabel(top, text=f"  {title}", image=emoji_image(emo, 34), compound="left", font=T.f(24),
                     text_color=T.TEXT).pack(side="left", padx=12)
        self.hourglass = Hourglass(top, bg=T.BG)
        self.hourglass.pack(side="right")
        self.star_lbl = ctk.CTkLabel(top, text=" 0", image=emoji_image("⭐", 30), compound="left", font=T.f(26),
                                     text_color=T.TEXT)
        self.star_lbl.pack(side="right", padx=18)
        self.combo_lbl = ctk.CTkLabel(top, text="", font=T.f(22), text_color=T.PRIMARY)
        self.combo_lbl.pack(side="right", padx=6)
        self.level_lbl = ctk.CTkLabel(top, text="", font=T.f(16), corner_radius=12, height=34, width=120,
                                      fg_color=T.SURFACE, text_color=T.MUTED)
        self.level_lbl.pack(side="right", padx=10)

        pb_row = ctk.CTkFrame(self, fg_color="transparent")
        pb_row.pack(fill="x", padx=30)
        self.progress = ctk.CTkProgressBar(pb_row, height=16, corner_radius=8, progress_color=self.color,
                                           fg_color=T.TRACK)
        self.progress.pack(side="left", fill="x", expand=True)
        self.progress.set(0)
        self.count_lbl = ctk.CTkLabel(pb_row, text="", font=T.f(16), text_color=T.MUTED, width=70)
        self.count_lbl.pack(side="left", padx=8)

        self.card = Card(self)
        self.card.pack(fill="both", expand=True, padx=24, pady=10)
        tools = ctk.CTkFrame(self.card, fg_color="transparent")
        tools.place(relx=1.0, x=-14, y=12, anchor="ne")
        self.speak_btn = ctk.CTkButton(tools, text="", image=emoji_image("🔊", 28), width=54, height=50,
                                       corner_radius=16, fg_color=self.light, hover_color=darker(self.light, 0.93),
                                       command=lambda: self.view and self.view.speak())
        self.speak_btn.pack(side="left", padx=4)
        self.hint_btn = ctk.CTkButton(tools, text="", image=emoji_image("💡", 28), width=54, height=50,
                                      corner_radius=16, fg_color=T.GOLD_LIGHT, hover_color=darker(T.GOLD_LIGHT, 0.9),
                                      command=self._hint)
        self.body = ctk.CTkFrame(self.card, fg_color="transparent")
        self.body.pack(fill="both", expand=True, padx=20, pady=(18, 10))
        self.pads = Pads(self.body)
        tools.lift()

        self.fb = ctk.CTkFrame(self, fg_color=T.GOOD_LIGHT, corner_radius=22, height=96)
        self.fb_emoji = ctk.CTkFrame(self.fb, fg_color="transparent", width=60, height=60)
        self.fb_emoji.pack(side="left", padx=(22, 8), pady=8)
        txt = ctk.CTkFrame(self.fb, fg_color="transparent")
        txt.pack(side="left", fill="x", expand=True, pady=8)
        self.fb_title = ctk.CTkLabel(txt, text="", font=T.f(26), text_color=T.TEXT, anchor="w")
        self.fb_title.pack(anchor="w")
        self.fb_text = ctk.CTkLabel(txt, text="", font=(T.FONT, 19), text_color=T.TEXT, anchor="w", justify="left",
                                    wraplength=700)
        self.fb_text.pack(anchor="w")
        self.next_btn = big_button(self.fb, "Weiter", self._next, color=T.GOOD, emoji="➡️", width=170, height=62)
        self.next_btn.pack(side="right", padx=18)

    # --- Ablauf ----------------------------------------------------------------
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
        if remaining == 1 and not self.boss_done and self.n_target >= 5:
            self.boss_done = True
            lvl = min(8, lvl + 2)
            badge, bonus = "⚡ BOSS-AUFGABE · +2 Bonus", 2
        elif (self.profile.settings.get("specials", True) and self.done >= 2 and self.specials_done < 2
              and not (self.topic and self.topic.special) and random.random() < 0.2):
            self.specials_done += 1
            topic = TP.special_topic(self.subject if self.subject != "mix" else "mathe")
            lvl = adaptive.level_for(self.profile, topic.subject, topic.skill)
            badge, bonus = "★ SONDERAUFGABE · +3 Bonus", 3
        elif (self.profile.settings.get("specials", True) and pos % 4 == 2
              and not (self.topic and (self.topic.fokus or self.topic.subject == "konz"))):
            topic = TP.fokus_topic(topic.subject)
            lvl = adaptive.level_for(self.profile, topic.subject, topic.skill)
            badge, bonus = "🎯 FOKUS-AUFGABE · +1 Bonus", 1
        tasks = TP.generate(topic, self.profile.grade, lvl)
        for t in tasks:
            t._meta = {}
            t._level = lvl
            t._badge = badge
            t._bonus = bonus
        self.app.speaker.prefetch([t.speak or t.prompt for t in tasks])
        return tasks

    def _lookahead(self):
        """Nächste Aufgabe schon vorbereiten (inkl. Sprachausgabe) – damit es ohne Wartezeit weitergeht."""
        if not self.winfo_exists() or self.queue or self.review_only:
            return
        if self.done + 1 >= self.n_target + self.extra:
            return
        if self._pending_reviews and self._review_slots and self.done + 1 >= self._review_slots[0]:
            return
        tasks = self._generate(ahead=1)
        for t in tasks:
            t._pre = True
        self.queue.extend(tasks)

    def _next(self):
        if self._auto_job:
            self.after_cancel(self._auto_job)
            self._auto_job = None
        self.fb.pack_forget()
        self.feedback_visible = False
        if self.current is not None:
            self.done += 1
            self.current = None
            if self._maybe_break():
                return
        if self.view:
            self.view.destroy()
            self.view = None
        task = None
        if self.queue:
            task = self.queue.pop(0)
        elif self.done < self.n_target + self.extra:
            if not self.review_only and self._pending_reviews and self._review_slots and \
                    self.done >= self._review_slots[0]:
                self._review_slots.pop(0)
                task = self._pending_reviews.pop(0)
            else:
                tasks = self._generate()
                if tasks:
                    task, rest = tasks[0], tasks[1:]
                    self.queue = rest + self.queue
        if task is None:
            self._finish()
            return
        self.current = task
        self.progress.set(self.done / max(1, self._total()))
        self.count_lbl.configure(text=f"{self.done + 1} / {self._total()}")
        subject_color = T.SUBJECTS.get(task.subject, T.SUBJECTS["mix"])[0]
        lv = getattr(task, "_level", None)
        if lv:
            self.level_lbl.configure(text=f"Stufe {lv}" + (" · PROFI" if lv >= 6 else ""),
                                     text_color=T.GOLD if lv >= 6 else T.MUTED)
        else:
            self.level_lbl.configure(text="Wiederholung", text_color=T.MUTED)
        self.view = TaskView(self.body, self.app, task, subject_color, self._on_answer, self._on_ready,
                             pads=self.pads)
        self.view.place(x=0, y=0, relwidth=1, relheight=1)
        slide_in(self.view)
        self.after(350, self._lookahead)
        if task.hint:
            self.hint_btn.pack(side="left", padx=4)
        else:
            self.hint_btn.pack_forget()

    def _on_ready(self):
        t = self.current
        if t is None:
            return
        base = int(self.profile.settings["timer"].get(t.subject, 0) or 0)
        secs = round(base * t.time_factor) if base else 0
        self.hourglass.start(secs, self._timeout)

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
        # Zweiter Versuch?
        if not correct and not timeout and self.profile.settings.get("retry", True) and view.can_retry():
            self.app.sounds.play("falsch")
            view.allow_retry(given)
            self._show_feedback(False, "Noch ein Versuch!", "Prüf die Aufgabe nochmal ganz genau.", "🧐",
                                retry=True)
            self.hourglass.resume()
            return
        view.show_result(correct, given)
        second = view.attempts > 1
        old, new = adaptive.record(self.profile, task.skill, correct, ratio, timeout, second, task.subject)
        if new != old:  # vorbereitete Aufgabe passt nicht mehr zur neuen Stufe
            keep = []
            for t in self.queue:
                if getattr(t, "_pre", False) and t.skill == task.skill:
                    if getattr(t, "_bonus", 0) == 2:
                        self.boss_done = False
                    elif getattr(t, "_bonus", 0) == 3:
                        self.specials_done -= 1
                    continue
                keep.append(t)
            self.queue = keep
        if new > old and adaptive.is_auto(self.profile, task.subject):
            topic = TP.BY_SKILL.get(task.skill)
            name = topic.title if topic else ""
            self.levelups.append((name, new))
            txt = f"Level up! Stufe {new} in „{name}“" + (" – PROFI-Modus!" if new >= 6 else "")
            self.after(400, lambda: (self.app.sounds.play("stufe"), Toast(self.app, txt, "🚀", anim="Rocket",
                                                                           ms=2600)))
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
        # Punkte
        if correct:
            self.correct += 1
            gained = 0 if second else 1
            extras = []
            fast = not second and ratio is not None and ratio < 0.35
            if fast:
                gained += 1
                self.blitz += 1
                extras.append("Blitz-Bonus")
            if not second and getattr(task, "_bonus", 0):
                gained += task._bonus
                extras.append({2: "Boss besiegt", 3: "Sonderaufgabe gelöst", 1: "Fokus-Bonus"}[task._bonus])
                if task._bonus == 2:
                    self.boss_won = True
            self.combo = self.combo + 1 if not second else 0
            self.best_combo = max(self.best_combo, self.combo)
            if self.combo and self.combo % 5 == 0:
                gained += 3
                Toast(self.app, f"{self.combo}er-Serie! +3 XP", "🔥", ms=1800, anim="Fire")
            count_up(self.star_lbl, self.stars, self.stars + gained, " {}", 500)
            if gained:
                try:
                    x = view.winfo_rootx() - self.winfo_rootx() + view.winfo_width() // 2
                    y = view.winfo_rooty() - self.winfo_rooty() + view.winfo_height() // 2
                    fly_up(self, f"+{gained} XP", x, y)
                except Exception:
                    pass
            self.stars += gained
            self.combo_lbl.configure(text=f"🔥 {self.combo}" if self.combo >= 2 else "")
            self.app.sounds.play("richtig")
            title = random.choice(PRAISE)
            text = "Im zweiten Versuch geschafft." if second else \
                (f"+{gained} XP" + (f"  ·  {', '.join(extras)}" if extras else ""))
            anim = "Collision" if getattr(task, "_bonus", 0) == 2 else random.choice(CORRECT_ANIMS)
            self._show_feedback(True, title, text, anim)
            if self.profile.settings.get("tts") and not task.listen:
                if getattr(task, "_bonus", 0) == 2:
                    self.app.speaker.say("Boss besiegt! Stark!")
                elif self.combo and self.combo % 5 == 0:
                    self.app.speaker.say(f"{self.combo} richtige in Folge!")
                else:
                    self.app.speaker.say(random.choice(SPOKEN_FAST if fast else SPOKEN_PRAISE))
            if not task.explain or not second:
                self._advance_when_quiet(1300)
        else:
            self.combo = 0
            self.combo_lbl.configure(text="")
            self.mistakes.append(task)
            if not timeout:
                self.app.sounds.play("falsch")
            solution = self._solution_text(task)
            title = "Die Zeit ist um!" if timeout else random.choice(ENCOURAGE)
            self._show_feedback(False, title, solution, "Hourglass Done" if timeout else random.choice(WRONG_ANIMS))
            try:
                shake(view)
            except Exception:
                pass
            if self.profile.settings.get("tts"):
                self.app.speaker.say(f"{title} {solution.splitlines()[0]}", force=False)
        self.profile.save()

    def _advance_when_quiet(self, min_ms, max_ms=8000):
        """Erst weiter, wenn die Stimme fertig gesprochen hat (höchstens max_ms)."""
        start = time.monotonic()

        def check():
            self._auto_job = None
            if not self.winfo_exists() or not self.feedback_visible:
                return
            waited = (time.monotonic() - start) * 1000
            if waited >= max_ms or (waited >= min_ms and not self.app.speaker.is_speaking()):
                self._auto_job = self.after(250, self._next)  # kurze Atempause
                return
            self._auto_job = self.after(120, check)
        self._auto_job = self.after(min(min_ms, 400), check)

    def _solution_text(self, t):
        if t.type == "sort":
            return "Grün = richtige Gruppe. " + (t.explain or "")
        if t.type == "order":
            return "Richtig: " + (" – ".join(t.answer) if not all(len(x) <= 2 for x in t.answer)
                                  else "".join(t.answer))
        if t.type == "grid_click":
            return "Das grüne Bild ist anders."
        ans = f"Richtig: {t.answer}{(' ' + t.unit) if t.unit else ''}"
        return ans + (f"\n{t.explain}" if t.explain and t.explain not in ans else "")

    def _show_feedback(self, good, title, text, emoji, retry=False):
        self.fb.configure(fg_color=T.GOOD_LIGHT if good else (T.GOLD_LIGHT if retry else T.BAD_LIGHT))
        for w in self.fb_emoji.winfo_children():
            w.destroy()
        if emoji and emoji[0].isascii():
            anim_emoji(self.fb_emoji, emoji, 56).pack()
        else:
            ctk.CTkLabel(self.fb_emoji, text="", image=emoji_image(emoji, 52)).pack()
        self.fb_title.configure(text=title)
        self.fb_text.configure(text=text)
        if retry:
            self.next_btn.pack_forget()
            self.after(1600, lambda: self.fb.winfo_exists() and not self.feedback_visible and self.fb.pack_forget())
        else:
            self.next_btn.pack(side="right", padx=18)
            self.next_btn.configure(fg_color=T.GOOD if good else T.PRIMARY,
                                    hover_color=darker(T.GOOD if good else T.PRIMARY))
            self.feedback_visible = True
        self.fb.pack(side="bottom", fill="x", padx=24, pady=(0, 16), before=self.card)

    def _hint(self):
        if self.current and self.current.hint:
            Toast(self.app, self.current.hint, "💡", ms=3500)
            self.app.speaker.say(self.current.hint, force=True)

    # --- Bewegungspause --------------------------------------------------------
    def _maybe_break(self) -> bool:
        every = int(self.profile.settings.get("break_every", 0) or 0)
        remaining = self._total() - self.done
        if not every or self.done % every != 0 or remaining <= 1:
            return False
        if self.view:
            self.view.destroy()
            self.view = None
        emo, title, text = random.choice(BREAKS)
        box = ctk.CTkFrame(self.body, fg_color="transparent")
        box.pack(expand=True)
        emoji_label(box, emo, 120, fg_color="transparent").pack(pady=(10, 6))
        ctk.CTkLabel(box, text=title, font=T.f(36), text_color=self.color).pack()
        ctk.CTkLabel(box, text=text, font=(T.FONT, 26), text_color=T.TEXT, wraplength=760).pack(pady=12)
        btn = big_button(box, "Weiter geht's", lambda: (box.destroy(), self._next()), color=T.GOOD, emoji="💪",
                         width=260)
        btn.pack(pady=14)
        self.app.speaker.say(f"{title} {text}", force=True)
        self.hourglass.start(20, lambda: None)
        self.count_lbl.configure(text="Pause")
        self._in_break = box
        return True

    # --- Ende ------------------------------------------------------------------
    def _finish(self):
        self.hourglass.stop()
        secs = int(time.monotonic() - self.t_start)
        total = self.done
        bonus = 2 if total >= 5 else 0
        self.stars += bonus
        new_sticker = self.profile.add_stars(self.stars) if self.stars else False
        self.profile.touch_streak()
        self.profile.log_session({
            "date": today(), "subject": self.subject, "topic": self.topic.id if self.topic else "",
            "title": self.topic.title if self.topic else T.SUBJECT_NAMES.get(self.subject, "Fehler-Training"),
            "correct": self.correct, "total": total, "seconds": secs, "stars": self.stars})
        self.profile.save()
        from .screens import ResultScreen, result_speech
        speech = result_speech(self.profile, self.correct, total, self.stars, self.levelups, self.boss_won,
                               self.best_combo, self.blitz, self.rank_before)
        self.app.show(ResultScreen, subject=self.subject, topic=self.topic, correct=self.correct, total=total,
                      stars=self.stars, seconds=secs, levelups=self.levelups, new_sticker=new_sticker,
                      has_mistakes=bool(self.mistakes), review_only=self.review_only, speech=speech,
                      extras={"boss": self.boss_won, "combo": self.best_combo, "blitz": self.blitz})

    def _quit(self):
        self.hourglass.stop()
        self.app.speaker.stop()
        if self.stars:
            self.profile.add_stars(self.stars)
        self.profile.save()
        self.app.go_home()

    def _on_key(self, event):
        if event.keysym in ("Return", "KP_Enter"):
            if self.feedback_visible:
                self._next()
            elif self.view and self.current and self.current.type == "input" and self.view.entry:
                self.view.submit(self.view.entry.get())
        elif event.char and event.char in "123456" and self.view:
            self.view.key(event.char)

    def destroy(self):
        self.app.unbind_key()
        if self._auto_job:
            self.after_cancel(self._auto_job)
        super().destroy()
