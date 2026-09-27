"""Entdecken: kindgerechte Artikel aus dem Klexikon lesen/hören und ein kleines Quiz lösen."""

import customtkinter as ctk

from .. import online
from .. import theme as T
from ..emoji import emoji_image
from .screens import header
from .widgets import Card, Toast, big_button, darker, emoji_label, soft_button

def _s(i):
    return T.SUBJECTS["sach"][i]


class DiscoverScreen(ctk.CTkFrame):
    def __init__(self, app, topic=None):
        super().__init__(app.container, fg_color=T.BG)
        self.app = app
        self.seen = []
        self.art = None
        bar = header(self, app, "Entdecken", "🔭", color=_s(0))
        big_button(bar, "  Neues Thema", self.load, color=_s(0), emoji="🎲", size=20, height=52).pack(side="right")
        self.card = Card(self)
        self.card.pack(fill="both", expand=True, padx=24, pady=(4, 20))
        if not app.profile.settings.get("online", True):
            self._message("🔌", "Das Internet ist im Elternbereich ausgeschaltet.")
            return
        self.load()

    def _message(self, emo, text):
        for w in self.card.winfo_children():
            w.destroy()
        box = ctk.CTkFrame(self.card, fg_color="transparent")
        box.pack(expand=True)
        emoji_label(box, emo, 90, fg_color="transparent").pack(pady=8)
        ctk.CTkLabel(box, text=text, font=T.f(24), text_color=T.MUTED, wraplength=700).pack()

    def load(self):
        self._message("🔭", "Ich suche etwas Spannendes für dich …")
        box = []
        online.load_random(lambda a, off, key: box.append((a, off, key)), exclude=self.seen)

        def poll():  # Ergebnis aus dem Hintergrund-Thread im Hauptthread abholen
            if not self.winfo_exists():
                return
            if box:
                self._show(*box[0])
            else:
                self.after(100, poll)
        poll()

    def _show(self, art, offline, key):
        if not self.winfo_exists():
            return
        if art is None:
            self._message("📡", "Keine Internetverbindung – versuche es später noch einmal.")
            return
        self.seen.append(key)
        self.art = art
        for w in self.card.winfo_children():
            w.destroy()
        top = ctk.CTkFrame(self.card, fg_color="transparent")
        top.pack(fill="both", expand=True, padx=26, pady=(20, 6))
        if art.get("img"):
            try:
                im = online.load_image(art["img"])
                img = ctk.CTkImage(light_image=im, dark_image=im, size=im.size)
                ctk.CTkLabel(top, text="", image=img, corner_radius=16).pack(side="left", padx=(0, 22), anchor="n")
            except Exception:
                pass
        col = ctk.CTkFrame(top, fg_color="transparent")
        col.pack(side="left", fill="both", expand=True)
        ctk.CTkLabel(col, text=art["title"], font=T.f(34), text_color=_s(0), anchor="w").pack(anchor="w")
        ctk.CTkLabel(col, text=art["text"], font=(T.FONT, 20), text_color=T.TEXT, justify="left",
                     wraplength=560 if art.get("img") else 980, anchor="w").pack(anchor="w", pady=8)
        src = "Quelle: Klexikon – das Kinderlexikon (klexikon.zum.de)" + (" · offline gespeichert" if offline else "")
        ctk.CTkLabel(col, text=src, font=(T.FONT, 13), text_color=T.MUTED).pack(anchor="w")
        btns = ctk.CTkFrame(self.card, fg_color="transparent")
        btns.pack(pady=(4, 8))
        soft_button(btns, "  Vorlesen", lambda: self.app.speaker.say(f"{art['title']}. {art['text']}", force=True),
                    emoji="🔊", size=20, height=54).pack(side="left", padx=8)
        big_button(btns, "  Quiz dazu", self._quiz, color=_s(0), emoji="❓", size=20, height=54).pack(side="left", padx=8)
        self.quiz_box = ctk.CTkFrame(self.card, fg_color="transparent")
        self.quiz_box.pack(pady=(0, 16))

    def _quiz(self):
        for w in self.quiz_box.winfo_children():
            w.destroy()
        q = online.make_quiz(self.art) if self.art else None
        if not q:
            ctk.CTkLabel(self.quiz_box, text="Zu diesem Text gibt es kein Quiz – probier ein neues Thema!",
                         font=T.f(18), text_color=T.MUTED).pack()
            return
        ctk.CTkLabel(self.quiz_box, text="Welches Wort fehlt?", font=T.f(22), text_color=T.TEXT).pack()
        ctk.CTkLabel(self.quiz_box, text=q["sentence"], font=(T.FONT, 20), text_color=T.TEXT, wraplength=900
                     ).pack(pady=6)
        row = ctk.CTkFrame(self.quiz_box, fg_color="transparent")
        row.pack()
        btns = {}

        def pick(o):
            ok = o == q["answer"]
            for opt, b in btns.items():
                b.configure(state="disabled", fg_color=T.GOOD if opt == q["answer"] else
                            (T.BAD_LIGHT if opt == o else _s(1)))
            if ok:
                self.app.sounds.play("richtig")
                self.app.profile.add_stars(1)
                self.app.profile.save()
                Toast(self.app, "Richtig gelesen! +1 Stern", "⭐")
            else:
                self.app.sounds.play("falsch")

        for o in q["options"]:
            b = ctk.CTkButton(row, text=o, width=210, height=58, corner_radius=16, font=T.f(20), fg_color=_s(1),
                              hover_color=darker(_s(1), 0.93), text_color=T.TEXT, command=lambda o=o: pick(o))
            b.pack(side="left", padx=6)
            btns[o] = b
