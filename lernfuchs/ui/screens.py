"""Startseite, Fachübersicht, Ergebnis, Sticker-Album und Begrüßung."""

import random

import customtkinter as ctk

from .. import adaptive
from .. import theme as T
from ..content import topics as TP
from ..emoji import emoji_image, gray_image
from ..storage import STARS_PER_STICKER, STICKERS, today
from .widgets import (Card, Confetti, anim_emoji, big_button, count_up, darker, emoji_label, level_dots,
                      soft_button)

FOX_TIPS = [
    "Profis lesen die Aufgabe zweimal – dann erst antworten.",
    "Fehler zeigen dir, wo du als Nächstes stärker wirst.",
    "Schnell UND richtig bringt Blitz-Bonus.",
    "Ab Stufe 6 wird es PROFI – Stoff der nächsten Klasse.",
    "Am Ende jeder Runde wartet eine Boss-Aufgabe.",
    "Kurze Pausen machen dein Gehirn schneller.",
    "Knobel-Sonderaufgaben bringen +3 XP extra.",
]


def make_clickable(widget, command, hover_widget=None, normal=None, hover=None):
    def enter(*_):
        if hover_widget is not None and hover:
            hover_widget.configure(fg_color=hover)

    def leave(*_):
        if hover_widget is not None and normal:
            hover_widget.configure(fg_color=normal)

    def bind(w):
        w.bind("<Button-1>", lambda *_: command())
        w.bind("<Enter>", enter)
        w.bind("<Leave>", leave)
        try:
            w.configure(cursor="hand2")
        except Exception:
            pass
        for ch in w.winfo_children():
            bind(ch)
    bind(widget)


def header(master, app, title, emoji, color=None, back=None):
    color = color or T.TEXT
    bar = ctk.CTkFrame(master, fg_color="transparent")
    bar.pack(fill="x", padx=28, pady=(18, 6))
    ctk.CTkButton(bar, text="", image=emoji_image("⬅️", 26), width=56, height=52, corner_radius=26,
                  fg_color=T.NEUTRAL_BTN, hover_color=T.NEUTRAL_HOVER,
                  command=back or app.go_home).pack(side="left")
    ctk.CTkLabel(bar, text=f"  {title}", image=emoji_image(emoji, 44), compound="left", font=T.f(32),
                 text_color=color).pack(side="left", padx=12)
    return bar


# --- Startseite ----------------------------------------------------------------

class HomeScreen(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app.container, fg_color=T.BG)
        self.app = app
        p = app.profile
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=32, pady=(22, 8))
        anim_emoji(top, "Fox", 80).pack(side="left")
        hello = ctk.CTkFrame(top, fg_color="transparent")
        hello.pack(side="left", padx=14)
        ctk.CTkLabel(hello, text=f"Hallo {p.data['name'] or 'du'}!", font=T.f(36), text_color=T.TEXT).pack(anchor="w")
        ctk.CTkLabel(hello, text=random.choice(FOX_TIPS), font=(T.FONT, 17),
                     text_color=T.MUTED, wraplength=560, justify="left").pack(anchor="w")

        right = ctk.CTkFrame(top, fg_color="transparent")
        right.pack(side="right")
        ctk.CTkButton(right, text="", image=emoji_image("🔒", 26), width=52, height=52, corner_radius=26,
                      fg_color=T.NEUTRAL_BTN, hover_color=T.NEUTRAL_HOVER,
                      command=lambda: app.show_parent()).pack(side="right", padx=(10, 0))
        soft_button(right, f" {p.data['stars']} XP", lambda: app.show(StickerScreen), size=20, height=52,
                    emoji="⭐", width=130).pack(side="right", padx=5)
        soft_button(right, f" {p.streak_days()}", lambda: None, size=22, height=52, emoji="🔥",
                    width=90).pack(side="right", padx=5)
        soft_button(right, " Sammlung", lambda: app.show(StickerScreen), size=19, height=52, emoji="🏅",
                    width=140).pack(side="right", padx=5)

        # Tagesziel
        done_today = sum(s["total"] for s in p.data["sessions"] if s["date"] == today())
        goal = int(p.settings.get("daily_goal", 20))
        stats_row = ctk.CTkFrame(self, fg_color="transparent")
        stats_row.pack(fill="x", padx=32, pady=(6, 8))
        rname, remo, rlo, rhi = T.rank_for(p.data["stars"])
        rank_card = Card(stats_row, radius=20)
        rank_card.pack(side="left", fill="x", expand=True, padx=(0, 6))
        emoji_label(rank_card, remo, 34, fg_color="transparent").pack(side="left", padx=(16, 8), pady=10)
        rc = ctk.CTkFrame(rank_card, fg_color="transparent")
        rc.pack(side="left", fill="x", expand=True, padx=(0, 16))
        ctk.CTkLabel(rc, text=f"Rang: {rname}", font=T.f(19), text_color=T.GOLD).pack(anchor="w")
        rbar = ctk.CTkProgressBar(rc, height=10, corner_radius=5, progress_color=T.GOLD, fg_color=T.TRACK)
        rbar.pack(fill="x", pady=(2, 0))
        rbar.set(1 if rhi is None else (p.data["stars"] - rlo) / (rhi - rlo))
        ctk.CTkLabel(rc, text="Höchster Rang erreicht!" if rhi is None else
                     f"Noch {rhi - p.data['stars']} XP bis zum nächsten Rang", font=(T.FONT, 13),
                     text_color=T.MUTED).pack(anchor="w")
        goal_card = Card(stats_row, radius=20)
        goal_card.pack(side="left", fill="x", expand=True, padx=(6, 0))
        ctk.CTkLabel(goal_card, text=" Tagesziel", image=emoji_image("🎯", 26), compound="left", font=T.f(19),
                     text_color=T.TEXT).pack(side="left", padx=(18, 10), pady=12)
        bar = ctk.CTkProgressBar(goal_card, height=14, corner_radius=7, progress_color=T.GOOD, fg_color=T.TRACK)
        bar.pack(side="left", fill="x", expand=True, padx=8)
        bar.set(min(1, done_today / max(1, goal)))
        txt = f"{done_today}/{goal}" + ("  ✓" if done_today >= goal else "")
        ctk.CTkLabel(goal_card, text=txt, font=T.f(17), text_color=T.MUTED).pack(side="left", padx=18)

        # Tagesmix
        mc, ml, mh = T.SUBJECTS["mix"]
        mix = big_button(self, "  Tagesmix  ·  alle Fächer, mit Boss-Aufgabe", lambda: app.start_session("mix"), color=mc,
                         emoji="🎲", size=28, height=86, emoji_size=52, radius=26)
        mix.pack(fill="x", padx=32, pady=(8, 10))

        # Fächer
        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="both", expand=True, padx=26, pady=4)
        for i, subj in enumerate(["deutsch", "mathe", "sach", "konz"]):
            c, light, hv = T.SUBJECTS[subj]
            topics = TP.topics_for(subj, p.grade)
            levels = [adaptive.level_for(p, subj, t.skill) for t in topics if t.kind == "tasks"]
            avg = round(sum(levels) / len(levels)) if levels else 1
            card = ctk.CTkFrame(grid, fg_color=light, corner_radius=26, border_width=3, border_color=c)
            card.grid(row=i // 2, column=i % 2, padx=8, pady=8, sticky="nsew")
            emoji_label(card, T.SUBJECT_EMOJI[subj], 72, fg_color="transparent").pack(side="left", padx=(24, 12),
                                                                                     pady=16)
            col = ctk.CTkFrame(card, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True, padx=(0, 18))
            ctk.CTkLabel(col, text=T.SUBJECT_NAMES[subj], font=T.f(28), text_color=c).pack(anchor="w")
            ctk.CTkLabel(col, text=f"{len(topics)} Themen  ·  Ø Stufe {avg}" + ("  ·  PROFI" if avg >= 6 else ""),
                         font=(T.FONT, 16), text_color=T.MUTED).pack(anchor="w")
            level_dots(col, avg, c).pack(anchor="w", pady=4)
            make_clickable(card, lambda s=subj: app.show(SubjectScreen, subject=s), card, light,
                           darker(light, 0.95))
        grid.grid_columnconfigure((0, 1), weight=1, uniform="a")
        grid.grid_rowconfigure((0, 1), weight=1, uniform="b")

        due = adaptive.due_entries(p)
        if due:
            big_button(self, f"  Fehler-Training: {len(due)} Aufgabe{'n' if len(due) != 1 else ''} zum Wiederholen",
                       lambda: app.start_session("mix", review_only=True), color=T.GOLD, text_color="#1D2438",
                       emoji="🔁", size=20, height=56).pack(fill="x", padx=32, pady=(4, 18))
        else:
            ctk.CTkFrame(self, height=14, fg_color="transparent").pack()


# --- Fachübersicht --------------------------------------------------------------

class SubjectScreen(ctk.CTkFrame):
    def __init__(self, app, subject):
        super().__init__(app.container, fg_color=T.BG)
        self.app = app
        c, light, _ = T.SUBJECTS[subject]
        bar = header(self, app, T.SUBJECT_NAMES[subject], T.SUBJECT_EMOJI[subject], color=c)
        if subject != "konz":
            big_button(bar, "  Alles gemischt", lambda: app.start_session(subject), color=c, emoji="🎲",
                       size=20, height=52).pack(side="right")
        else:
            big_button(bar, "  Konzentrations-Mix", lambda: app.start_session("konz"), color=c, emoji="🎲",
                       size=20, height=52).pack(side="right")
        area = ctk.CTkFrame(self, fg_color="transparent")
        area.pack(fill="both", expand=True, padx=22, pady=(4, 16))
        p = app.profile
        topics = TP.topics_for(subject, p.grade)
        for i, t in enumerate(topics):
            card = ctk.CTkFrame(area, fg_color=T.CARD, corner_radius=20, border_width=2, border_color=T.CARD_BORDER,
                                height=96)
            card.grid(row=i // 3, column=i % 3, padx=8, pady=8, sticky="nsew")
            emoji_label(card, t.emoji, 44, fg_color="transparent").pack(side="left", padx=(14, 8), pady=10)
            col = ctk.CTkFrame(card, fg_color="transparent")
            col.pack(side="left", fill="x", expand=True, padx=(0, 10))
            ctk.CTkLabel(col, text=t.title, font=T.f(20), text_color=T.TEXT, anchor="w", wraplength=210,
                         justify="left").pack(anchor="w")
            if t.desc:
                ctk.CTkLabel(col, text=t.desc, font=(T.FONT, 14), text_color=T.MUTED, anchor="w", wraplength=210,
                             justify="left").pack(anchor="w")
            if t.kind == "tasks":
                lv = adaptive.level_for(p, subject, t.skill)
                lrow = ctk.CTkFrame(col, fg_color="transparent")
                lrow.pack(anchor="w", pady=(4, 0))
                level_dots(lrow, lv, c, size=9).pack(side="left")
                if t.special or t.fokus:
                    ctk.CTkLabel(lrow, text=" KNOBELN " if t.special else " FOKUS ", font=T.f(11),
                                 fg_color=T.GOLD if t.special else T.SUBJECTS["konz"][0],
                                 text_color="#1D2438" if t.special else "white",
                                 corner_radius=6, height=20).pack(side="left", padx=6)
            else:
                tag = "Spiel" if t.kind == "game" else "Internet"
                rec = p.data["records"].get(t.id)
                if rec:
                    tag += f" · Rekord: {rec}"
                ctk.CTkLabel(col, text=tag, font=T.f(13), fg_color=light, corner_radius=8, text_color=c
                             ).pack(anchor="w", pady=(4, 0))
            make_clickable(card, lambda t=t: app.open_topic(t), card, T.CARD, light)
        area.grid_columnconfigure((0, 1, 2), weight=1, uniform="a")


# --- Ergebnis -----------------------------------------------------------------

class ResultScreen(ctk.CTkFrame):
    def __init__(self, app, subject, topic, correct, total, stars, seconds, levelups=(), new_sticker=False,
                 has_mistakes=False, review_only=False, game_title=None, detail=None, speech=None, extras=None):
        super().__init__(app.container, fg_color=T.BG)
        self.app = app
        pct = correct / total if total else 0
        emo, title = ("Trophy", "Überragend!") if pct >= 0.9 else ("Rocket", "Starke Runde!") if pct >= 0.7 else \
            ("Flexed Biceps Light Skin Tone", "Gut trainiert!") if pct >= 0.4 else ("Brain", "Harte Runde – dranbleiben!")
        if total == 0:
            emo, title = "Fox", "Nichts zu wiederholen!"
        card = Card(self)
        card.pack(expand=True, padx=60, pady=30, fill="both")
        conf_w = 900
        if pct >= 0.7 and total:
            conf = Confetti(card, conf_w, 200, bg=T.CARD)
            conf.place(relx=0.5, y=10, anchor="n")
            self.after(3000, conf.destroy)
            app.sounds.play("fertig")
        anim_emoji(card, emo, 130).pack(pady=(26, 4))
        ctk.CTkLabel(card, text=title, font=T.f(40), text_color=T.TEXT).pack()
        if detail:
            ctk.CTkLabel(card, text=detail, font=T.f(24), text_color=T.MUTED).pack(pady=4)
        elif total:
            ctk.CTkLabel(card, text=f"{correct} von {total} richtig", font=T.f(28), text_color=T.MUTED).pack(pady=4)
        stats = ctk.CTkFrame(card, fg_color="transparent")
        stats.pack(pady=14)
        xp_lbl = ctk.CTkLabel(stats, text="  +0 XP", image=emoji_image("⭐", 40), compound="left", font=T.f(32),
                              text_color=T.TEXT)
        xp_lbl.pack(side="left", padx=26)
        self.after(400, lambda: count_up(xp_lbl, 0, stars, "  +{} XP", 900))
        ex = extras or {}
        chips = [t for t in [("💥", "Boss besiegt") if ex.get("boss") else None,
                             ("🔥", f"Beste Serie: {ex.get('combo')}") if ex.get("combo", 0) >= 3 else None,
                             ("⚡", f"{ex.get('blitz')}× Blitz") if ex.get("blitz", 0) else None] if t]
        if chips:
            crow = ctk.CTkFrame(card, fg_color="transparent")
            crow.pack(pady=(0, 6))
            for e, txt in chips:
                ctk.CTkLabel(crow, text=f" {txt}", image=emoji_image(e, 22), compound="left", font=T.f(16),
                             fg_color=T.SURFACE, corner_radius=12, height=34, text_color=T.TEXT
                             ).pack(side="left", padx=5, ipadx=6)
        m, s = divmod(seconds, 60)
        ctk.CTkLabel(stats, text=f"  {m}:{s:02d} min", image=emoji_image("⏱️", 36), compound="left", font=T.f(28),
                     text_color=T.TEXT).pack(side="left", padx=26)
        best = {}
        for name, lvl in levelups:  # pro Thema nur die höchste neue Stufe
            best[name] = max(lvl, best.get(name, 0))
        for name, lvl in best.items():
            ctk.CTkLabel(card, text=f"  Neue Stufe {lvl}: {name}", image=emoji_image("🚀", 28), compound="left",
                         font=T.f(20), text_color=T.PRIMARY).pack()
        if new_sticker:
            n = app.profile.data["stickers"]
            st = STICKERS[min(n, len(STICKERS)) - 1]
            ctk.CTkLabel(card, text="  Neues Abzeichen für deine Sammlung!", image=emoji_image(st, 44), compound="left",
                         font=T.f(22), text_color=T.GOOD).pack(pady=6)
            app.sounds.play("sticker")
        btns = ctk.CTkFrame(card, fg_color="transparent")
        btns.pack(pady=(18, 28))
        color = T.SUBJECTS.get(subject, T.SUBJECTS["mix"])[0]
        if not review_only and not game_title:
            big_button(btns, "  Nochmal", lambda: app.start_session(subject, topic), color=color, emoji="🔄",
                       width=200).pack(side="left", padx=8)
        if has_mistakes and adaptive.due_entries(app.profile):
            big_button(btns, "  Fehler üben", lambda: app.start_session("mix", review_only=True), color=T.GOLD,
                       text_color="#1D2438", emoji="🔁", width=220).pack(side="left", padx=8)
        big_button(btns, "  Übersicht", app.go_home, color=T.GOOD, emoji="🏠", width=200).pack(side="left", padx=8)
        if speech:
            app.speaker.say(speech)
        elif total:
            app.speaker.say(f"{title} {detail}." if detail else f"{title}")


# --- Sticker-Album ------------------------------------------------------------

class StickerScreen(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app.container, fg_color=T.BG)
        p = app.profile
        header(self, app, "Meine Sammlung", "🏅", color=T.PRIMARY)
        rname, remo, rlo, rhi = T.rank_for(p.data["stars"])
        ranks = ctk.CTkFrame(self, fg_color="transparent")
        ranks.pack(pady=(0, 8))
        for lo, name, emo in T.RANKS:
            got = p.data["stars"] >= lo
            chip = ctk.CTkFrame(ranks, fg_color=T.GOLD_LIGHT if got else T.LOCKED, corner_radius=14)
            chip.pack(side="left", padx=4)
            ctk.CTkLabel(chip, text=f" {name}", image=emoji_image(emo, 22) if got else gray_image(emo, 22),
                         compound="left", font=T.f(14), text_color=T.TEXT if got else T.MUTED
                         ).pack(padx=8, pady=6)
        n = p.data["stickers"]
        to_next = STARS_PER_STICKER - p.data["stars"] % STARS_PER_STICKER
        ctk.CTkLabel(self, text=f"{n} von {len(STICKERS)} Abzeichen  ·  noch {to_next} XP bis zum nächsten",
                     font=T.f(18), text_color=T.MUTED).pack(pady=(0, 8))
        card = Card(self)
        card.pack(expand=True, fill="both", padx=32, pady=(0, 24))
        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(expand=True)
        for i, st in enumerate(STICKERS):
            owned = i < n
            img = emoji_image(st, 54) if owned else gray_image(st, 54)
            cell = ctk.CTkLabel(grid, text="", image=img, width=86, height=80, corner_radius=16,
                                fg_color=T.GOLD_LIGHT if owned else T.LOCKED)
            cell.grid(row=i // 10, column=i % 10, padx=5, pady=5)


# --- Begrüßung (erster Start) -------------------------------------------------

class WelcomeScreen(ctk.CTkFrame):
    def __init__(self, app):
        super().__init__(app.container, fg_color=T.BG)
        self.app = app
        card = Card(self)
        card.pack(expand=True, padx=120, pady=50)
        emoji_label(card, "🦊", 130, fg_color="transparent").pack(pady=(36, 6))
        ctk.CTkLabel(card, text="Willkommen bei LernFuchs!", font=T.f(38), text_color=T.PRIMARY).pack()
        ctk.CTkLabel(card, text="Wie heißt du?", font=T.f(24), text_color=T.TEXT).pack(pady=(24, 6))
        self.name = ctk.CTkEntry(card, width=360, height=60, font=T.f(28), justify="center", corner_radius=16,
                                 border_color=T.PRIMARY, border_width=3)
        self.name.pack()
        ctk.CTkLabel(card, text="In welche Klasse gehst du?", font=T.f(22), text_color=T.TEXT).pack(pady=(22, 6))
        self.grade = ctk.CTkSegmentedButton(card, values=["2. Klasse", "3. Klasse", "4. Klasse"], font=T.f(20),
                                            height=52, selected_color=T.PRIMARY,
                                            selected_hover_color=T.PRIMARY_HOVER, fg_color=T.NEUTRAL_BTN,
                                            unselected_color=T.NEUTRAL_BTN, unselected_hover_color=T.NEUTRAL_HOVER,
                                            text_color=T.TEXT)
        self.grade.set(f"{app.profile.grade}. Klasse")
        self.grade.pack()
        big_button(card, "  Los geht's!", self._go, emoji="🚀", width=260, height=66).pack(pady=(30, 14))
        ctk.CTkLabel(card, text="Für Eltern: Im Elternbereich (🔒 oben rechts) stellt ihr Schwierigkeit, "
                                "Sanduhr-Zeit und mehr ein.", font=(T.FONT, 15), text_color=T.MUTED,
                     wraplength=560).pack(pady=(0, 28), padx=30)
        self.after(100, self.name.focus_set)
        app.bind_key(lambda e: self._go() if e.keysym == "Return" else None)

    def _go(self):
        name = self.name.get().strip()
        if not name:
            self.name.configure(border_color=T.BAD)
            return
        p = self.app.profile
        p.data["name"] = name
        p.settings["grade"] = int(self.grade.get()[0])
        p.save()
        self.app.speaker.say(f"Hallo {name}! Schön, dass du da bist. Los geht's!", force=True)
        self.app.go_home()

    def destroy(self):
        self.app.unbind_key()
        super().destroy()


ZAHLWORT = ["null", "eine", "zwei", "drei", "vier", "fünf", "sechs", "sieben", "acht", "neun", "zehn", "elf",
            "zwölf", "dreizehn", "vierzehn", "fünfzehn", "sechzehn", "siebzehn", "achtzehn", "neunzehn", "zwanzig"]


def _zw(n):
    return ZAHLWORT[n] if 0 <= n < len(ZAHLWORT) else str(n)


def result_speech(profile, correct, total, xp, levelups, boss_won, best_combo, blitz, rank_before) -> str:
    """Persönliche, abwechslungsreiche Rückmeldung zum Rundenende (statt immer derselben Floskel)."""
    name = profile.data.get("name") or ""
    pct = correct / total if total else 0
    if pct == 1:
        opener = random.choice([f"{name}, fehlerfrei! Alle {_zw(total)} Aufgaben richtig.",
                                f"Perfekte Runde, {name}! Keine einzige falsch.",
                                f"Wahnsinn, {name}: {_zw(total)} von {_zw(total)}!"])
    elif pct >= 0.8:
        opener = random.choice([f"Richtig stark, {name}! {_zw(correct)} von {_zw(total)}.",
                                f"{_zw(correct).capitalize()} von {_zw(total)} richtig – das kann sich sehen lassen.",
                                f"Sehr gute Runde, {name}!"])
    elif pct >= 0.5:
        opener = random.choice([f"Gut gekämpft, {name}! {_zw(correct)} von {_zw(total)}.",
                                f"Mehr als die Hälfte geschafft. Die Fehler üben wir noch.",
                                f"Solide Runde, {name}. Da geht noch mehr!"])
    else:
        opener = random.choice([f"Das war eine harte Runde, {name}. Genau so wird man besser!",
                                f"Nicht aufgeben, {name}! Schwierige Aufgaben machen dein Gehirn stärker."])
    parts = [opener]
    if boss_won:
        parts.append(random.choice(["Und den Boss hast du auch besiegt!", "Die Boss-Aufgabe hast du geknackt!"]))
    if levelups:
        topic_name, lvl = levelups[-1]
        parts.append(f"Neue Stufe {lvl} in {topic_name}" + ("– das ist schon Profi-Niveau!" if lvl >= 6 else "!"))
    if best_combo >= 5:
        parts.append(f"Deine beste Serie: {_zw(best_combo)} richtige hintereinander.")
    elif blitz >= 3:
        parts.append(f"{_zw(blitz).capitalize()}-mal warst du blitzschnell.")
    rname, _, _, nxt = T.rank_for(profile.data["stars"])
    if rname != rank_before:
        parts.append(f"Neuer Rang: {rname}!")
    elif nxt:
        parts.append(f"Noch {nxt - profile.data['stars']} X P bis zum nächsten Rang.")
    if random.random() < 0.35:
        from ..content.sach_data import FRAGEN
        facts = [f["x"] for f in FRAGEN["forscher"] if f.get("x") and len(f["x"]) < 110]
        if facts:
            parts.append("Übrigens: " + random.choice(facts))
    return " ".join(parts)
