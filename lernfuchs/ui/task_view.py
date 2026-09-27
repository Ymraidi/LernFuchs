"""Stellt eine einzelne Aufgabe dar (alle Aufgabentypen) und meldet die Antwort zurück."""

import re

import customtkinter as ctk

from .. import theme as T
from ..emoji import emoji_image
from ..tasks import Task, check
from . import visuals
from .widgets import LetterPad, NumPad, darker, emoji_label

EMOJI_RE = re.compile(r"^[\U0001F000-\U0001FAFF☀-➿⬀-⯿️‍\U0001F1E6-\U0001F1FF]+$")
EMOJI_IN_TEXT = re.compile(r"[\U0001F000-\U0001FAFF☀-➿][️‍\U0001F000-\U0001FAFF]*")


def is_emoji(s: str) -> bool:
    return bool(EMOJI_RE.match(s or ""))


class TaskView(ctk.CTkFrame):
    def __init__(self, master, app, task: Task, color: str, on_answer, on_ready, pads=None):
        super().__init__(master, fg_color="transparent")
        self.app, self.task, self.color = app, task, color
        self.light = T.SUBJECTS.get(task.subject, T.SUBJECTS["mix"])[1]
        self.on_answer, self.on_ready = on_answer, on_ready
        self.pads = pads
        self.attempts = 0
        self.locked = False
        self.buttons = {}
        self.entry = None
        self.selected = set()

        prompt = task.prompt
        found = EMOJI_IN_TEXT.findall(prompt)
        img = None
        if found:  # Tk zeigt Emojis nur schwarz-weiß → farbig als Bild daneben
            prompt = re.sub(r"\s+", " ", EMOJI_IN_TEXT.sub("", prompt)).replace(" ?", "?").strip()
            img = emoji_image(found[0], 44)
        badge = getattr(task, "_badge", None)
        if badge:
            ctk.CTkLabel(self, text=f"  {badge}  ", font=T.f(16), fg_color=T.GOLD, text_color="#1D2438",
                         corner_radius=12, height=32).pack(pady=(0, 6))
        self.prompt_lbl = ctk.CTkLabel(self, text=prompt + ("  " if img else ""), image=img, compound="right",
                                       font=T.f(30 if len(prompt) < 60 else 24),
                                       text_color=T.TEXT, wraplength=900, justify="center")
        self.prompt_lbl.pack(pady=(4, 10))

        self.visual_box = ctk.CTkFrame(self, fg_color="transparent", height=1)
        self.visual_box.pack()
        self.answer_box = ctk.CTkFrame(self, fg_color="transparent", height=1)
        self.answer_box.pack(pady=(12, 0), fill="x")

        replay = self.speak if task.listen else None
        vis = task.visual or ({"kind": "listen"} if task.listen else None)
        kind = (vis or {}).get("kind")
        if kind in ("flash", "flash_text", "flash_photos"):
            self._flash(vis)
            return
        if kind == "flash_grid":
            self._build_grid(flash=vis["seconds"])
            return
        w = visuals.render(self.visual_box, vis, bg=T.CARD, on_replay=replay)
        if w is not None:
            w.pack(pady=4)
        self._build_answers()
        self.after(10, self._ready)

    # --- Vorlesen ------------------------------------------------------------
    def speak(self):
        t = self.task
        self.app.speaker.say(t.listen_text if t.listen else (t.speak or t.prompt), force=True)

    def _ready(self):
        if self.task.listen:
            self.app.speaker.say(self.task.speak or self.task.listen_text, force=True)
        elif self.app.profile.settings.get("tts"):
            self.app.speaker.say(self.task.speak or self.task.prompt)
        self.on_ready()

    # --- Kurz zeigen, dann verdecken (Merk- und Blitzaufgaben) -----------------
    def _flash(self, vis):
        kind = vis["kind"]
        box = ctk.CTkFrame(self.visual_box, fg_color=T.SURFACE, corner_radius=18)
        box.pack(pady=6, ipadx=10, ipady=6)
        info = ctk.CTkLabel(self.visual_box, text="", font=T.f(18), text_color=T.MUTED)
        info.pack(pady=(4, 0))
        self.app.speaker.say("Gut aufpassen!" if kind != "flash" else "Merke dir die Bilder!", force=True)
        widgets = []
        if kind == "flash":
            for e in vis["items"]:
                lbl = emoji_label(box, e, 64, fg_color=T.CARD, corner_radius=16, width=84, height=84)
                lbl.pack(side="left", padx=5, pady=5)
                widgets.append(lbl)
        elif kind == "flash_photos":
            from .. import photos
            size = 128 if len(vis["items"]) <= 5 else 104
            for i, it in enumerate(vis["items"]):
                cell = ctk.CTkFrame(box, fg_color="transparent")
                cell.grid(row=i // 5, column=i % 5, padx=5, pady=5)
                im = photos.square_thumb(it["photo"], size * 2)
                ctk.CTkLabel(cell, text="", image=ctk.CTkImage(im, im, size=(size, size)), corner_radius=10).pack()
                ctk.CTkLabel(cell, text=it["label"], font=T.f(14), text_color=T.TEXT).pack()
            widgets.append(box)
        elif vis.get("seq"):
            lbl = ctk.CTkLabel(box, text="", font=(T.FONT, 96, "bold"), text_color=self.color, width=320, height=150)
            lbl.pack(padx=30, pady=10)
            widgets.append(lbl)
        elif vis.get("list"):
            for i, w in enumerate(vis["items"]):
                ctk.CTkLabel(box, text=w, font=T.f(26), fg_color=T.CARD, corner_radius=12, height=48,
                             text_color=T.TEXT).grid(row=i // 4, column=i % 4, padx=6, pady=6, ipadx=10)
            widgets.append(box)
        else:
            small = vis.get("small")
            ctk.CTkLabel(box, text=vis["items"][0], font=T.f(26 if small else 60), text_color=T.TEXT if small else
                         self.color, wraplength=820, justify="center").pack(padx=30, pady=18)
            widgets.append(box)

        def finish():
            if not self.winfo_exists():
                return
            info.configure(text="")
            if kind == "flash":
                q = emoji_image("❓", 56)
                for lbl in widgets:
                    lbl.configure(image=q)
            else:
                for w in box.winfo_children():
                    w.destroy()
                ctk.CTkLabel(box, text="", image=emoji_image("🙈", 64)).pack(padx=40, pady=10)
            self._build_answers()
            if self.app.profile.settings.get("tts"):
                self.app.speaker.say(self.task.speak or self.task.prompt)
            self.on_ready()

        if vis.get("seq"):
            items = list(vis["items"])
            per = int(vis["seconds"] * 1000)

            def show(i):
                if not self.winfo_exists():
                    return
                if i >= len(items):
                    return finish()
                widgets[0].configure(text=items[i])
                info.configure(text=f"Zahl {i + 1} von {len(items)}")
                self.after(per, lambda: (widgets[0].winfo_exists() and widgets[0].configure(text=""),
                                         self.after(180, lambda: show(i + 1))))
            self.after(500, lambda: show(0))
            return
        total = float(vis["seconds"])
        t_end = [total]

        def tick():
            if not self.winfo_exists():
                return
            if t_end[0] <= 0.01:
                return finish()
            info.configure(text=f"Gut merken … {t_end[0]:.0f} s" if total >= 2 else "Gut hinsehen!")
            step = min(1.0, t_end[0])
            t_end[0] -= step
            self.after(int(step * 1000), tick)
        tick()

    # --- Antwortbereich --------------------------------------------------------
    def _build_answers(self):
        t = self.task
        if t.type in ("choice", "truefalse"):
            self._build_choice()
        elif t.type == "input":
            self._build_input()
        elif t.type == "order":
            self._build_order()
        elif t.type == "sort":
            self._build_sort()
        elif t.type == "grid_click":
            self._build_grid()
        elif t.type == "multi_click":
            self._build_multi()

    def _build_choice(self):
        t = self.task
        opts = t.options
        emoji_opts = all(is_emoji(o) for o in opts)
        longest = max(len(o) for o in opts)
        box = ctk.CTkFrame(self.answer_box, fg_color="transparent")
        box.pack()
        if t.type == "truefalse":
            cols = 2
        elif emoji_opts or longest <= 6:
            cols = min(len(opts), 6)
        elif longest <= 26:
            cols = 2 if len(opts) <= 4 else 3
        else:
            cols = 1
        for i, o in enumerate(opts):
            img = None
            text = o
            if emoji_opts:
                img, text = emoji_image(o, 56), ""
            elif o in t.emojis and t.emojis[o]:
                img = emoji_image(t.emojis[o], 32)
            if t.type == "truefalse":
                img = emoji_image("👍" if i == 0 else "👎", 30)
            width = 130 if (emoji_opts or longest <= 6) else (430 if cols == 2 else 290 if cols == 3 else 820)
            b = ctk.CTkButton(box, text=f"  {text}" if img and text else text, image=img, compound="left",
                              width=width, height=78 if emoji_opts else 66, corner_radius=18,
                              font=T.f(26 if longest <= 14 else 21), fg_color=self.light,
                              hover_color=darker(self.light, 0.93), text_color=T.TEXT, border_width=3,
                              border_color=self.light, command=lambda o=o: self.submit(o))
            b.grid(row=i // cols, column=i % cols, padx=8, pady=7)
            self.buttons[o] = b

    def _build_input(self):
        t = self.task
        row = ctk.CTkFrame(self.answer_box, fg_color="transparent")
        row.pack()
        is_num = t.input_kind == "number"
        width = 200 if is_num else (520 if len(str(t.answer)) > 12 else 360)
        self.entry = ctk.CTkEntry(row, width=width, height=68, font=T.f(34), justify="center", corner_radius=16,
                                  border_width=3, border_color=self.color, fg_color=T.INPUT_BG, text_color=T.TEXT)
        self.entry.pack(side="left", padx=6)
        if t.unit:
            ctk.CTkLabel(row, text=t.unit, font=T.f(28), text_color=T.MUTED).pack(side="left", padx=4)
        self.check_btn = ctk.CTkButton(row, text="Prüfen", image=emoji_image("✅", 28), compound="left",
                                       width=150, height=68, corner_radius=16, font=T.f(24), fg_color=self.color,
                                       hover_color=darker(self.color), command=lambda: self.submit(self.entry.get()))
        self.check_btn.pack(side="left", padx=10)
        pad_row = ctk.CTkFrame(self.answer_box, fg_color="transparent", height=1)
        pad_row.pack(pady=(8, 0))
        extra = "," if ("," in str(t.answer) or t.unit in ("€", "cm")) else ("R" if "R" in str(t.answer) else "")
        if self.pads is not None:  # wiederverwendbares Zahlenfeld (schneller)
            self.pads.show(pad_row, self.entry, numeric=is_num, extra=extra)
        elif is_num:
            NumPad(pad_row, self.entry, None, comma=extra == ",", extra=extra if extra != "," else None).pack()
        else:
            LetterPad(pad_row, self.entry).pack()
        self.after(60, lambda: self.entry.winfo_exists() and self.entry.focus_set())

    # Reihenfolge / Buchstaben legen
    def _build_order(self):
        t = self.task
        self.placed = []
        letters = all(len(x) <= 2 for x in t.items)
        per_row = 9 if letters else 4
        tile_w = 64 if letters else 190
        self.slot_box = ctk.CTkFrame(self.answer_box, fg_color=self.light, corner_radius=18, height=88)
        self.slot_box.pack(fill="x", padx=40, pady=(0, 10))
        self.slot_hint = ctk.CTkLabel(self.slot_box, text="Tippe die Teile in der richtigen Reihenfolge an",
                                      font=(T.FONT, 18), text_color=T.MUTED)
        self.slot_hint.pack(pady=26)
        self.slot_inner = ctk.CTkFrame(self.slot_box, fg_color="transparent")
        pool = ctk.CTkFrame(self.answer_box, fg_color="transparent")
        pool.pack()
        self.pool_btns = []
        for i, it in enumerate(t.items):
            img = emoji_image(t.emojis[it], 28) if t.emojis.get(it) else None
            b = ctk.CTkButton(pool, text=it, image=img, compound="left", width=tile_w, height=64, corner_radius=14,
                              font=T.f(28 if letters else 20), fg_color=T.SURFACE, text_color=T.TEXT,
                              border_width=3, border_color=self.color, hover_color=self.light,
                              command=lambda i=i: self._place(i))
            b.grid(row=i // per_row, column=i % per_row, padx=5, pady=5)
            self.pool_btns.append(b)
        self._tile_w, self._letters = tile_w, letters
        self.check_btn = ctk.CTkButton(self.answer_box, text="Fertig", image=emoji_image("✅", 28), compound="left",
                                       width=180, height=60, corner_radius=16, font=T.f(24), fg_color=self.color,
                                       hover_color=darker(self.color), state="disabled",
                                       command=lambda: self.submit([self.task.items[i] for i in self.placed]))
        self.check_btn.pack(pady=12)

    def _place(self, i):
        if self.locked or i in self.placed:
            return
        self.placed.append(i)
        self.pool_btns[i].configure(state="disabled", fg_color=T.NEUTRAL_BTN, border_color=T.NEUTRAL_BTN,
                                    text_color=T.DISABLED_TEXT)
        self.app.sounds.play("klick")
        self._redraw_slots()

    def _unplace(self, i):
        if self.locked:
            return
        self.placed.remove(i)
        self.pool_btns[i].configure(state="normal", fg_color=T.SURFACE, border_color=self.color, text_color=T.TEXT)
        self._redraw_slots()

    def _redraw_slots(self):
        for w in self.slot_inner.winfo_children():
            w.destroy()
        if self.placed:
            self.slot_hint.pack_forget()
            self.slot_inner.pack(pady=10)
        else:
            self.slot_inner.pack_forget()
            self.slot_hint.pack(pady=26)
        for n, i in enumerate(self.placed):
            it = self.task.items[i]
            ctk.CTkButton(self.slot_inner, text=it, width=self._tile_w if not self._letters else 56, height=58,
                          corner_radius=12, font=T.f(28 if self._letters else 19), fg_color=self.color,
                          hover_color=darker(self.color), text_color=T.ON_ACCENT,
                          command=lambda i=i: self._unplace(i)).grid(row=n // 9 if self._letters else n // 4,
                                                                     column=n % 9 if self._letters else n % 4,
                                                                     padx=3, pady=3)
        full = len(self.placed) == len(self.task.items)
        self.check_btn.configure(state="normal" if full else "disabled")

    # Sortieren in Gruppen
    def _build_sort(self):
        t = self.task
        self.sort_idx = 0
        self.sort_errors = 0
        self.sort_given = {}
        top = ctk.CTkFrame(self.answer_box, fg_color=self.light, corner_radius=20)
        top.pack(pady=(0, 10))
        self.sort_emoji = ctk.CTkLabel(top, text="", fg_color="transparent")
        self.sort_emoji.pack(side="left", padx=(20, 6), pady=10)
        self.sort_word = ctk.CTkLabel(top, text="", font=T.f(30), text_color=T.TEXT)
        self.sort_word.pack(side="left", padx=(6, 24), pady=10)
        self.sort_count = ctk.CTkLabel(self.answer_box, text="", font=(T.FONT, 16), text_color=T.MUTED)
        self.sort_count.pack()
        cols = ctk.CTkFrame(self.answer_box, fg_color="transparent")
        cols.pack(pady=6)
        self.bucket_btns, self.bucket_lists = {}, {}
        palette = ["#4D96FF", "#2EB872", "#FF8C42", "#9B5DE5", "#FF6B6B"]
        width = 200 if len(t.buckets) <= 3 else 170
        for i, bkt in enumerate(t.buckets):
            col = ctk.CTkFrame(cols, fg_color="transparent")
            col.grid(row=0, column=i, padx=6, sticky="n")
            b = ctk.CTkButton(col, text=bkt, width=width, height=62, corner_radius=16, font=T.f(20),
                              fg_color=palette[i % 5], hover_color=darker(palette[i % 5]),
                              command=lambda bkt=bkt: self._sort_pick(bkt))
            b.pack()
            lst = ctk.CTkFrame(col, fg_color="transparent")
            lst.pack(pady=4)
            self.bucket_btns[bkt], self.bucket_lists[bkt] = b, lst
        self._sort_show()

    def _sort_show(self):
        t = self.task
        it = t.items[self.sort_idx]
        e = t.emojis.get(it)
        self.sort_emoji.configure(image=emoji_image(e, 56) if e else emoji_image("❔", 1))
        self.sort_word.configure(text=it)
        self.sort_count.configure(text=f"Begriff {self.sort_idx + 1} von {len(t.items)}")

    def _sort_pick(self, bkt):
        if self.locked:
            return
        t = self.task
        it = t.items[self.sort_idx]
        right = t.answer[it]
        self.sort_given[it] = bkt
        ok = bkt == right
        chip_col = T.GOOD_LIGHT if ok else T.BAD_LIGHT
        ctk.CTkLabel(self.bucket_lists[right], text=("✓ " if ok else "✗ ") + it, font=(T.FONT, 15),
                     fg_color=chip_col, corner_radius=10, text_color=T.TEXT).pack(pady=2, fill="x")
        if not ok:
            self.sort_errors += 1
            self.app.sounds.play("falsch")
            self.locked = True
            self.bucket_btns[right].configure(border_width=4, border_color=T.GOOD)
            self.after(900, lambda: (self.bucket_btns[right].configure(border_width=0), self._sort_next()))
        else:
            self.app.sounds.play("klick")
            self._sort_next()

    def _sort_next(self):
        self.locked = False
        self.sort_idx += 1
        if self.sort_idx >= len(self.task.items):
            self.attempts = 1
            self.locked = True
            self.on_answer(self.sort_errors == 0, self.sort_given)
        else:
            self._sort_show()

    # Bild anklicken (auch: Fotos merken → verdeckt)
    def _build_grid(self, flash=None):
        t = self.task
        n = len(t.items)
        cols = 3 if n <= 9 else 4 if n <= 16 else 5
        size = 54 if n <= 16 else 46
        box = ctk.CTkFrame(self.answer_box, fg_color="transparent")
        box.pack()
        self.grid_btns = []
        photo = isinstance(t.items[0], dict)
        cache = {}
        self._photo_imgs = []
        if photo:
            from .. import photos
            size = 118 if n <= 9 else 100 if n <= 12 else 86
            cols = 3 if n <= 9 else 4

            def img_for(it):
                key = (it["photo"], it["fx"]) if flash else (it["fx"], str(it.get("patch")))
                if key not in cache:
                    im = photos.tile(it["photo"], it["crop"], it["fx"], size * 2, it.get("patch"))
                    cache[key] = ctk.CTkImage(light_image=im, dark_image=im, size=(size, size))
                return cache[key]
        for i, e in enumerate(t.items):
            img = img_for(e) if photo else emoji_image(e, size)
            self._photo_imgs.append(img)
            cell = ctk.CTkFrame(box, fg_color="transparent")
            cell.grid(row=i // cols, column=i % cols, padx=4, pady=4)
            b = ctk.CTkButton(cell, text="", image=img, width=size + (10 if photo else 26),
                              height=size + (10 if photo else 20),
                              fg_color=T.SURFACE, hover_color=self.light, corner_radius=10 if photo else 14,
                              command=lambda i=i: self.submit(i))
            b.pack()
            if flash and photo:
                lbl = ctk.CTkLabel(cell, text=e.get("label", ""), font=T.f(13), text_color=T.MUTED, height=18)
                lbl.pack()
            self.grid_btns.append(b)
        if not flash:
            return
        self.locked = True
        info = ctk.CTkLabel(self.visual_box, text="", font=T.f(18), text_color=T.MUTED)
        info.pack()
        self.app.speaker.say("Merk dir, wo welches Bild liegt!", force=True)
        left = [int(flash)]

        def tick():
            if not self.winfo_exists():
                return
            if left[0] <= 0:
                q = emoji_image("❓", int(size * 0.6))
                for b in self.grid_btns:
                    b.configure(image=q)
                for cell in box.winfo_children():
                    for w in cell.winfo_children()[1:]:
                        w.configure(text="")
                info.configure(text="")
                self.locked = False
                if self.app.profile.settings.get("tts"):
                    self.app.speaker.say(self.task.prompt.split("\n")[-1])
                self.on_ready()
                return
            info.configure(text=f"Gut merken … {left[0]} s")
            left[0] -= 1
            self.after(1000, tick)
        tick()

    # Mehrere anklicken
    def _build_multi(self):
        t = self.task
        n = len(t.items)
        cols = 4 if n <= 16 else 5
        box = ctk.CTkFrame(self.answer_box, fg_color="transparent")
        box.pack()
        self.grid_btns = []
        for i, it in enumerate(t.items):
            b = ctk.CTkButton(box, text=it, width=96, height=62, corner_radius=14, font=T.f(26),
                              fg_color=T.SURFACE, hover_color=self.light, text_color=T.TEXT, border_width=3,
                              border_color=T.SURFACE, command=lambda i=i: self._toggle(i))
            b.grid(row=i // cols, column=i % cols, padx=5, pady=5)
            self.grid_btns.append(b)
        self.check_btn = ctk.CTkButton(self.answer_box, text="Fertig", image=emoji_image("✅", 28), compound="left",
                                       width=180, height=58, corner_radius=16, font=T.f(22), fg_color=self.color,
                                       hover_color=darker(self.color),
                                       command=lambda: self.submit(sorted(self.selected)))
        self.check_btn.pack(pady=12)

    def _toggle(self, i):
        if self.locked:
            return
        b = self.grid_btns[i]
        if i in self.selected:
            self.selected.discard(i)
            b.configure(fg_color=T.SURFACE, border_color=T.SURFACE, text_color=T.TEXT)
        else:
            self.selected.add(i)
            b.configure(fg_color=self.color, border_color=self.color, text_color=T.ON_ACCENT)
        self.app.sounds.play("klick")

    # --- Auswertung -----------------------------------------------------------
    def submit(self, given):
        if self.locked:
            return
        if self.task.type == "input" and not str(given).strip():
            return
        self.attempts += 1
        self.locked = True
        self.on_answer(check(self.task, given), given)

    def show_result(self, correct: bool, given):
        """Färbt die Antwort grün/rot und zeigt die richtige Lösung."""
        t = self.task
        self.locked = True
        if t.type in ("choice", "truefalse"):
            for o, b in self.buttons.items():
                if o == t.answer:
                    b.configure(fg_color=T.GOOD, text_color=T.ON_ACCENT, border_color=T.GOOD)
                elif o == given:
                    b.configure(fg_color=T.BAD_LIGHT, border_color=T.BAD)
                b.configure(hover=False)
        elif t.type == "input" and self.entry:
            self.entry.configure(border_color=T.GOOD if correct else T.BAD, state="disabled")
            self.check_btn.configure(state="disabled")
        elif t.type == "order":
            for w in self.slot_inner.winfo_children():
                w.configure(fg_color=T.GOOD if correct else T.BAD, hover=False)
            self.check_btn.configure(state="disabled")
        elif t.type == "grid_click":
            for i, b in enumerate(self.grid_btns):
                if isinstance(t.visual, dict) and t.visual.get("kind") == "flash_grid":
                    b.configure(image=self._photo_imgs[i])  # Fotos wieder aufdecken
                if i == t.answer:
                    b.configure(fg_color=T.GOOD)
                elif i == given:
                    b.configure(fg_color=T.BAD_LIGHT)
        elif t.type == "multi_click":
            right = set(t.answer)
            for i, b in enumerate(self.grid_btns):
                if i in right:
                    b.configure(fg_color=T.GOOD, border_color=T.GOOD, text_color=T.ON_ACCENT)
                elif i in self.selected:
                    b.configure(fg_color=T.BAD_LIGHT, border_color=T.BAD, text_color=T.TEXT)
            self.check_btn.configure(state="disabled")

    def allow_retry(self, given):
        t = self.task
        self.locked = False
        if t.type in ("choice", "truefalse") and given in self.buttons:
            self.buttons[given].configure(state="disabled", fg_color=T.BAD_LIGHT, border_color=T.BAD)
        elif t.type == "input" and self.entry:
            self.entry.configure(border_color=T.BAD)
            self.entry.delete(0, "end")
            self.entry.focus_set()
            self.after(700, lambda: self.entry.winfo_exists() and self.entry.configure(border_color=self.color))
        elif t.type == "order":
            for i in list(self.placed):
                self._unplace(i)
        elif t.type == "grid_click" and isinstance(given, int):
            self.grid_btns[given].configure(state="disabled", fg_color=T.BAD_LIGHT)

    def can_retry(self) -> bool:
        t = self.task
        if t.type in ("truefalse", "sort", "multi_click"):
            return False
        if t.type == "choice" and len(t.options) <= 2:
            return False
        return self.attempts == 1

    def key(self, ch: str):
        """Tastatur: 1–6 wählt Antwort."""
        if self.locked or self.task.type not in ("choice", "truefalse"):
            return
        if ch.isdigit() and 1 <= int(ch) <= len(self.task.options):
            o = self.task.options[int(ch) - 1]
            if str(self.buttons[o].cget("state")) != "disabled":
                self.submit(o)

    def destroy(self):
        if self.pads is not None:
            self.pads.hide()
        super().destroy()
