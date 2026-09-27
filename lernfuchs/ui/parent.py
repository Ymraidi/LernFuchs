"""Elternbereich: Einstellungen, Fortschritt, Fehlerbox (geschützt durch eine Rechenaufgabe)."""

import random

import customtkinter as ctk

from .. import adaptive
from .. import theme as T
from ..content import topics as TP
from ..emoji import emoji_image
from .screens import header
from .widgets import Card, Toast, big_button, level_dots

TIMER_OPTS = ["Aus", "15 s", "20 s", "30 s", "45 s", "60 s", "90 s", "120 s"]
DIFF_OPTS = ["1", "2", "3", "4", "5", "6", "7", "8"]
DESIGN_OPTS = {"Modern (dunkel)": "modern", "Hell (freundlich)": "hell"}
BREAK_OPTS = {"Aus": 0, "alle 5": 5, "alle 8": 8, "alle 12": 12}


class ParentGate(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app.container, fg_color=T.BG)
        self.app = app
        self.a, self.b = random.randint(6, 9), random.randint(12, 19)
        header(self, app, "Elternbereich", "🔒")
        card = Card(self)
        card.pack(expand=True, padx=200, pady=60)
        ctk.CTkLabel(card, text="Nur für Erwachsene", font=T.f(28), text_color=T.TEXT).pack(pady=(40, 6))
        ctk.CTkLabel(card, text=f"Bitte löse:  {self.a} × {self.b} = ?", font=T.f(26), text_color=T.MUTED).pack(pady=6)
        self.entry = ctk.CTkEntry(card, width=220, height=60, font=T.f(28), justify="center", corner_radius=14)
        self.entry.pack(pady=10)
        big_button(card, "Öffnen", self._check, emoji="🔓", width=200).pack(pady=(6, 40))
        self.after(100, self.entry.focus_set)
        app.bind_key(lambda e: self._check() if e.keysym == "Return" else None)

    def _check(self):
        if self.entry.get().strip() == str(self.a * self.b):
            self.app.show(ParentScreen)
        else:
            self.entry.delete(0, "end")
            self.entry.configure(border_color=T.BAD)

    def destroy(self):
        self.app.unbind_key()
        super().destroy()


class ParentScreen(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app.container, fg_color=T.BG)
        self.app = app
        self.p = app.profile
        bar = header(self, app, "Elternbereich", "🔓")
        big_button(bar, "  Speichern", self._save, color=T.GOOD, emoji="💾", size=20, height=52).pack(side="right")
        tabs = ctk.CTkTabview(self, fg_color=T.CARD, segmented_button_selected_color=T.PRIMARY,
                              segmented_button_selected_hover_color=T.PRIMARY_HOVER, corner_radius=20,
                              border_width=2, border_color=T.CARD_BORDER)
        tabs._segmented_button.configure(font=T.f(18), height=44)
        tabs.pack(fill="both", expand=True, padx=24, pady=(0, 20))
        self._builders = {"Einstellungen": self._settings, "Fortschritt": self._progress,
                          "Fehlerbox": self._reviews, "So funktioniert's": self._info}
        self._built = set()
        self.tabs = tabs
        for name in self._builders:
            tabs.add(name)
        tabs.configure(command=self._on_tab)
        self._on_tab()

    def _on_tab(self):
        name = self.tabs.get()
        if name not in self._built:
            self._built.add(name)
            self._builders[name](self.tabs.tab(name))

    # --- Einstellungen ---------------------------------------------------------
    def _row(self, parent, label, widget_fn, hint=""):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=7, padx=10)
        lab = ctk.CTkFrame(row, fg_color="transparent", width=300)
        lab.pack(side="left")
        ctk.CTkLabel(lab, text=label, font=T.f(18), text_color=T.TEXT, anchor="w", width=300).pack(anchor="w")
        if hint:
            ctk.CTkLabel(lab, text=hint, font=(T.FONT, 13), text_color=T.MUTED, anchor="w", width=300,
                         wraplength=290, justify="left").pack(anchor="w")
        w = widget_fn(row)
        w.pack(side="left", padx=10)
        return w

    def _seg(self, parent, values, current):
        s = ctk.CTkSegmentedButton(parent, values=values, font=T.f(16), height=40, selected_color=T.PRIMARY,
                                   selected_hover_color=T.PRIMARY_HOVER, fg_color=T.NEUTRAL_BTN,
                                   unselected_color=T.NEUTRAL_BTN, unselected_hover_color=T.NEUTRAL_HOVER,
                                   text_color=T.TEXT)
        s.set(current)
        return s

    def _settings(self, tab):
        st = self.p.settings
        area = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        area.pack(fill="both", expand=True)
        self.w = {}
        self.w["name"] = self._row(area, "Name des Kindes", lambda r: ctk.CTkEntry(r, width=260, height=40,
                                                                                   font=T.f(18)))
        self.w["name"].insert(0, self.p.data["name"])
        self.w["grade"] = self._row(area, "Klasse", lambda r: self._seg(r, ["2", "3", "4"], str(st["grade"])),
                                    "Bestimmt Zahlenraum, Themen und Wortschatz.")
        ctk.CTkLabel(area, text="Mindeststufe & Sanduhr je Fach", font=T.f(22), text_color=T.PRIMARY
                     ).pack(anchor="w", padx=10, pady=(18, 2))
        ctk.CTkLabel(area, text="Die Stufe passt sich IMMER dem Lernerfolg an: richtige und schnelle Antworten "
                                "heben sie, Fehler senken sie. Hier wählt ihr nur die Mindeststufe – darunter fällt "
                                "es nie. Stufen 1–5 = Stoff der eingestellten Klasse, 6–8 = PROFI (Stoff der "
                                "nächsten Klasse). Die Sanduhr-Zeit gilt pro Aufgabe und verlängert sich bei "
                                "langen Aufgaben automatisch.",
                     font=(T.FONT, 14), text_color=T.MUTED, wraplength=900, justify="left").pack(anchor="w", padx=10)
        for subj in ("deutsch", "mathe", "sach", "konz"):
            c = T.SUBJECTS[subj][0]
            box = ctk.CTkFrame(area, fg_color=T.SUBJECTS[subj][1], corner_radius=16)
            box.pack(fill="x", padx=10, pady=6)
            ctk.CTkLabel(box, text=f"  {T.SUBJECT_NAMES[subj]}", image=emoji_image(T.SUBJECT_EMOJI[subj], 28),
                         compound="left", font=T.f(19), text_color=c, width=260, anchor="w"
                         ).pack(side="left", padx=12, pady=10)
            d = int(st["difficulty"].get(subj, 1) or 1)
            ctk.CTkLabel(box, text="ab Stufe", font=T.f(14), text_color=T.MUTED).pack(side="left")
            seg = self._seg(box, DIFF_OPTS, str(d))
            seg.pack(side="left", padx=8)
            t = int(st["timer"].get(subj, 0) or 0)
            opt = ctk.CTkOptionMenu(box, values=TIMER_OPTS, width=120, height=38, font=T.f(16),
                                    fg_color=c, button_color=c)
            opt.set("Aus" if t == 0 else f"{t} s")
            ctk.CTkLabel(box, text="", image=emoji_image("⏳", 26)).pack(side="left", padx=(20, 4))
            opt.pack(side="left", padx=4)
            self.w[f"diff_{subj}"], self.w[f"timer_{subj}"] = seg, opt
        ctk.CTkLabel(area, text="Runde & Motivation", font=T.f(22), text_color=T.PRIMARY
                     ).pack(anchor="w", padx=10, pady=(18, 2))
        self.w["tasks"] = self._row(area, "Aufgaben pro Runde", lambda r: self._seg(
            r, ["5", "10", "15", "20"], str(st["tasks_per_round"])))
        self.w["goal"] = self._row(area, "Tagesziel (Aufgaben)", lambda r: self._seg(
            r, ["10", "20", "30", "40"], str(st.get("daily_goal", 20))))
        cur_break = next((k for k, v in BREAK_OPTS.items() if v == st["break_every"]), "alle 8")
        self.w["break"] = self._row(area, "Bewegungspause", lambda r: self._seg(r, list(BREAK_OPTS), cur_break),
                                    "Kurze Bewegungs- und Atemübungen fördern die Konzentration.")
        self.w["retry"] = self._row(area, "Zweiter Versuch", lambda r: self._switch(r, st.get("retry", True)),
                                    "Bei falscher Antwort darf nochmal probiert werden.")
        self.w["specials"] = self._row(area, "Sonder- & Boss-Aufgaben",
                                       lambda r: self._switch(r, st.get("specials", True)),
                                       "Knobelaufgaben zwischendurch und eine schwere Boss-Aufgabe am Rundenende.")
        cur_design = next((k for k, v in DESIGN_OPTS.items() if v == st.get("design", "modern")), "Modern (dunkel)")
        self.w["design"] = self._row(area, "Design", lambda r: self._seg(r, list(DESIGN_OPTS), cur_design))
        ctk.CTkLabel(area, text="Ton & Internet", font=T.f(22), text_color=T.PRIMARY
                     ).pack(anchor="w", padx=10, pady=(18, 2))
        self.w["tts"] = self._row(area, "Aufgaben vorlesen", lambda r: self._switch(r, st["tts"]),
                                  "Höraufgaben und Diktate werden immer vorgelesen.")
        from ..speech import VOICE_LABELS
        self._voice_map = {v: k for k, v in VOICE_LABELS.items()}
        self.w["voice"] = self._row(area, "Stimme", lambda r: ctk.CTkOptionMenu(
            r, values=list(VOICE_LABELS.values()), width=340, height=38, font=T.f(15), fg_color=T.PRIMARY,
            button_color=T.PRIMARY_HOVER), "Online-Stimmen klingen natürlich; ohne Internet spricht automatisch Stefan.")
        self.w["voice"].set(VOICE_LABELS.get(st.get("voice", "conrad"), VOICE_LABELS["conrad"]))
        ctk.CTkButton(area, text="Stimme testen", width=160, height=36, font=T.f(15), fg_color=T.NEUTRAL_BTN,
                      hover_color=T.NEUTRAL_HOVER, text_color=T.TEXT, command=self._test_voice
                      ).pack(anchor="w", padx=320)
        self.w["rate"] = self._row(area, "Sprechtempo", lambda r: ctk.CTkSlider(r, from_=-5, to=3, number_of_steps=8,
                                                                              width=260, button_color=T.PRIMARY))
        self.w["rate"].set(st.get("tts_rate", -1))
        self.w["sound"] = self._row(area, "Klänge", lambda r: self._switch(r, st.get("sound", True)))
        self.w["online"] = self._row(area, "Internet (Entdecken)", lambda r: self._switch(r, st.get("online", True)),
                                     "Lädt kindgerechte Artikel aus dem Klexikon.")
        ctk.CTkButton(area, text="Fortschritt komplett zurücksetzen …", fg_color="transparent", text_color=T.BAD,
                      hover_color=T.BAD_LIGHT, font=T.f(15), command=self._reset).pack(anchor="w", padx=10, pady=20)
        if not self.app.speaker.available:
            ctk.CTkLabel(area, text="Hinweis: Keine Sprachausgabe gefunden – Vorlesen ist nicht verfügbar.",
                         font=T.f(14), text_color=T.BAD).pack(anchor="w", padx=10)

    def _switch(self, parent, value):
        sw = ctk.CTkSwitch(parent, text="", progress_color=T.PRIMARY, switch_width=54, switch_height=28)
        if value:
            sw.select()
        return sw

    def _save(self):
        st = self.p.settings
        w = self.w
        name = w["name"].get().strip()
        if name:
            self.p.data["name"] = name
        st["grade"] = int(w["grade"].get())
        for subj in ("deutsch", "mathe", "sach", "konz"):
            d = int(w[f"diff_{subj}"].get())
            st["difficulty"][subj] = d
            for key, sk in self.p.data["skills"].items():  # Mindeststufe sofort anwenden
                if key.startswith(subj + ".") and sk["level"] < d:
                    sk["level"] = float(d)
            t = w[f"timer_{subj}"].get()
            st["timer"][subj] = 0 if t == "Aus" else int(t.split()[0])
        st["tasks_per_round"] = int(w["tasks"].get())
        st["daily_goal"] = int(w["goal"].get())
        st["break_every"] = BREAK_OPTS[w["break"].get()]
        st["retry"] = bool(w["retry"].get())
        st["tts"] = bool(w["tts"].get())
        st["tts_rate"] = int(round(w["rate"].get()))
        st["sound"] = bool(w["sound"].get())
        st["online"] = bool(w["online"].get())
        st["specials"] = bool(w["specials"].get())
        st["voice"] = self._voice_map.get(w["voice"].get(), "conrad")
        new_design = DESIGN_OPTS[w["design"].get()]
        design_changed = new_design != st.get("design", "modern")
        st["design"] = new_design
        self.p.save()
        self.app.apply_settings()
        if design_changed:
            self.app.show(ParentScreen)
        self.app.speaker.say("Einstellungen gespeichert.", force=True)
        Toast(self.app, "Gespeichert!", "💾", color=T.GOOD_LIGHT)

    def _test_voice(self):
        from ..speech import VOICE_LABELS
        voice = self._voice_map.get(self.w["voice"].get(), "conrad")
        old = self.app.speaker.voice
        self.app.speaker.set_voice(voice)
        self.app.speaker.set_rate(int(round(self.w["rate"].get())))
        self.app.speaker.say("Hallo! So klinge ich. Wie viel ist sieben mal acht?", force=True)

    def _reset(self):
        dlg = ctk.CTkInputDialog(text="Wirklich ALLES zurücksetzen (Stufen, Sterne, Statistik)?\n"
                                      "Zum Bestätigen JA eintippen:", title="Zurücksetzen")
        if (dlg.get_input() or "").strip().upper() == "JA":
            name, settings = self.p.data["name"], self.p.settings
            from ..storage import DEFAULT
            import copy
            self.p.data = copy.deepcopy(DEFAULT)
            self.p.data["name"], self.p.data["settings"] = name, settings
            self.p.save()
            Toast(self.app, "Fortschritt zurückgesetzt", "🧹")
            self.app.show(ParentScreen)

    # --- Fortschritt -------------------------------------------------------------
    def _progress(self, tab):
        area = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        area.pack(fill="both", expand=True)
        sess = self.p.data["sessions"]
        total_tasks = sum(s["total"] for s in sess)
        total_ok = sum(s["correct"] for s in sess)
        minutes = sum(s["seconds"] for s in sess) // 60
        tiles = ctk.CTkFrame(area, fg_color="transparent")
        tiles.pack(fill="x", pady=6)
        for emo, val, lab in [("📚", len(sess), "Runden"), ("✏️", total_tasks, "Aufgaben"),
                              ("🎯", f"{round(100 * total_ok / total_tasks) if total_tasks else 0} %", "richtig"),
                              ("⏱️", minutes, "Minuten"), ("⭐", self.p.data["stars"], "Sterne"),
                              ("🔥", self.p.streak_days(), "Tage in Folge")]:
            t = ctk.CTkFrame(tiles, fg_color=T.BG, corner_radius=16)
            t.pack(side="left", padx=6, expand=True, fill="x")
            ctk.CTkLabel(t, text=f" {val}", image=emoji_image(emo, 26), compound="left", font=T.f(24),
                         text_color=T.TEXT).pack(pady=(10, 0))
            ctk.CTkLabel(t, text=lab, font=(T.FONT, 14), text_color=T.MUTED).pack(pady=(0, 10))

        for subj in ("deutsch", "mathe", "sach", "konz"):
            c = T.SUBJECTS[subj][0]
            ctk.CTkLabel(area, text=f"  {T.SUBJECT_NAMES[subj]}", image=emoji_image(T.SUBJECT_EMOJI[subj], 26),
                         compound="left", font=T.f(20), text_color=c).pack(anchor="w", padx=8, pady=(14, 4))
            for t in TP.topics_for(subj, self.p.grade):
                sk = self.p.data["skills"].get(t.skill)
                row = ctk.CTkFrame(area, fg_color=T.BG, corner_radius=12)
                row.pack(fill="x", padx=8, pady=2)
                ctk.CTkLabel(row, text="", image=emoji_image(t.emoji, 22)).pack(side="left", padx=(10, 4), pady=6)
                ctk.CTkLabel(row, text=t.title, font=T.f(15), text_color=T.TEXT, width=230, anchor="w"
                             ).pack(side="left")
                if not sk:
                    ctk.CTkLabel(row, text="noch nicht geübt", font=(T.FONT, 14), text_color=T.MUTED
                                 ).pack(side="left", padx=10)
                    continue
                level_dots(row, int(sk["level"]), c).pack(side="left", padx=10)
                acc = adaptive.accuracy(self.p, t.skill)
                ctk.CTkLabel(row, text=f"Stufe {sk['level']:.1f}", font=(T.FONT, 14), text_color=T.TEXT, width=90
                             ).pack(side="left")
                ctk.CTkLabel(row, text=f"zuletzt {round(100 * acc)} % richtig" if acc is not None else "",
                             font=(T.FONT, 14), text_color=T.GOOD if (acc or 0) >= 0.7 else T.BAD, width=170
                             ).pack(side="left")
                ctk.CTkLabel(row, text=f"{sk['seen']}× geübt", font=(T.FONT, 14), text_color=T.MUTED
                             ).pack(side="left", padx=10)

        ctk.CTkLabel(area, text="Letzte Runden", font=T.f(20), text_color=T.PRIMARY).pack(anchor="w", padx=8,
                                                                                          pady=(18, 4))
        for s in reversed(sess[-15:]):
            m, sec = divmod(s["seconds"], 60)
            txt = f"{s['date']}   ·   {s.get('title', '')}   ·   {s['correct']}/{s['total']} richtig   ·   " \
                  f"{m}:{sec:02d} min   ·   +{s['stars']} ⭐"
            ctk.CTkLabel(area, text=txt, font=(T.FONT, 14), text_color=T.TEXT, anchor="w").pack(anchor="w", padx=14)
        if not sess:
            ctk.CTkLabel(area, text="Noch keine Runden gespielt.", font=(T.FONT, 14), text_color=T.MUTED
                         ).pack(anchor="w", padx=14)

    # --- Fehlerbox ---------------------------------------------------------------
    def _reviews(self, tab):
        area = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        area.pack(fill="both", expand=True)
        box = self.p.data["review"]
        ctk.CTkLabel(area, text="Falsch beantwortete Aufgaben kommen in die Fehlerbox und werden später in einer "
                                "ANDEREN Form wiederholt (z. B. Diktat → Buchstaben-Puzzle, Rechnung → "
                                "Umkehraufgabe). Nach 4 richtigen Wiederholungen im Abstand von 1, 3 und 7 Tagen "
                                "gilt eine Aufgabe als gelernt.", font=(T.FONT, 14), text_color=T.MUTED,
                     wraplength=900, justify="left").pack(anchor="w", padx=8, pady=(4, 10))
        if not box:
            ctk.CTkLabel(area, text="Die Fehlerbox ist leer. 🎉", font=T.f(18), text_color=T.GOOD).pack(anchor="w",
                                                                                                    padx=8)
        for e in sorted(box, key=lambda e: e["due"])[:120]:
            topic = TP.BY_SKILL.get(e["skill"])
            txt = f"{topic.title if topic else e['skill']}:  {e.get('label', '')}"
            row = ctk.CTkFrame(area, fg_color=T.BG, corner_radius=10)
            row.pack(fill="x", padx=8, pady=2)
            ctk.CTkLabel(row, text=txt, font=(T.FONT, 14), text_color=T.TEXT, anchor="w", width=620
                         ).pack(side="left", padx=10, pady=4)
            ctk.CTkLabel(row, text=f"Fach {e['box']}/4  ·  fällig {e['due']}", font=(T.FONT, 13),
                         text_color=T.MUTED).pack(side="left")

    def _info(self, tab):
        txt = (
            "• Anpassung: Jedes Thema hat 8 Stufen und passt sich immer an. Richtige, schnelle Antworten und "
            "Serien heben die Stufe, Fehler senken sie. In den ersten Aufgaben eines Themas steigt die Stufe "
            "besonders schnell (Einstufung). Stufen 6–8 sind PROFI-Stufen mit Stoff der nächsten Klasse – so "
            "bleibt es auch für schnelle Lerner spannend. Im Einstellungs-Tab legt ihr nur eine Mindeststufe fest.\n\n"
            "• Sonderaufgaben & Boss: Zwischendurch erscheinen Knobel-Sonderaufgaben (Logik, Geheimschrift, "
            "Forscherfragen), am Ende jeder Runde eine Boss-Aufgabe zwei Stufen über dem aktuellen Niveau.\n\n"
            "• Sanduhr: Die Zeit pro Aufgabe trainiert konzentriertes Arbeiten. Läuft sie ab, wird die Lösung "
            "gezeigt und die Aufgabe kommt in die Fehlerbox – ohne Strafe.\n\n"
            "• Wiederholung in anderer Form: Fehler werden in derselben Runde und an späteren Tagen in "
            "anderer Form erneut geübt (Leitner-System).\n\n"
            "• Konzentration: Zahlen-Jagd (Schulte-Tabelle), Zahlen merken, Memory, Buchstaben-Detektiv (b/d), "
            "Farben-Falle (Stroop), Rechenketten hören und Bilder merken trainieren Aufmerksamkeit, "
            "Arbeitsgedächtnis und Impulskontrolle.\n\n"
            "• Empfehlung für Klasse 2: täglich 10–20 Minuten, lieber kurz und regelmäßig. Tastatur: Ziffern 1–4 "
            "wählen Antworten, Enter prüft bzw. geht weiter.\n\n"
            "• Erweitern: Neue Fragen für Heimat- und Sachkunde (z. B. zu eurem Wohnort) lassen sich in "
            "lernfuchs/content/sach_data.py als neue Zeile ergänzen, neue Lesetexte in deutsch_data.py.\n\n"
            "• Daten: Alles wird lokal im Ordner „daten“ gespeichert. Internet wird nur für „Entdecken“ genutzt."
        )
        ctk.CTkLabel(tab, text=txt, font=(T.FONT, 16), text_color=T.TEXT, wraplength=960, justify="left"
                     ).pack(anchor="w", padx=16, pady=12)
