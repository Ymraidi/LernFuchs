"""Eine Aufgabe auf dem Tablet darstellen (alle Aufgabentypen) und die Antwort zurückmelden."""

import re

from kivy.clock import Clock
from kivy.metrics import dp, sp
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.textinput import TextInput
from kivy.uix.widget import Widget

from lernfuchs import theme as T
from lernfuchs.tasks import check
from . import visuals
from .ui import Box, C, EmojiImg, NumPad, RButton, Txt, emoji_src, has_emoji, pil_texture, split_emojis

EMOJI_IN_TEXT = re.compile(r"[\U0001F000-\U0001FAFF☀-➿][️‍\U0001F000-\U0001FAFF]*")


def is_emoji(s):
    return bool(s) and all(has_emoji(p) for p in split_emojis(s)) and not any(ch.isalnum() for ch in s)


class TaskView(BoxLayout):
    def __init__(self, app, task, color, on_answer, on_ready, **kw):
        super().__init__(orientation="vertical", spacing=dp(10), padding=(dp(10), dp(6)), **kw)
        self.app, self.task, self.color = app, task, color
        self.light = T.SUBJECTS.get(task.subject, T.SUBJECTS["mix"])[1]
        self.on_answer, self.on_ready = on_answer, on_ready
        self.attempts, self.locked = 0, False
        self.buttons, self.entry, self.selected = {}, None, set()
        self._events = []

        badge = getattr(task, "_badge", None)
        if badge:
            bb = AnchorLayout(size_hint_y=None, height=dp(34))
            b = Box(bg=T.GOLD, radius=12, size_hint=(None, None), height=dp(32), width=dp(20 + 11 * len(badge)))
            b.add_widget(Txt(badge, fs=15, color="#1D2438", bold=True, wrap=False))
            bb.add_widget(b)
            self.add_widget(bb)
        prompt = task.prompt.replace("○", "?")
        found = EMOJI_IN_TEXT.findall(prompt)
        head = BoxLayout(orientation="horizontal", size_hint_y=None, spacing=dp(10))
        if found:
            prompt = re.sub(r"\s+", " ", EMOJI_IN_TEXT.sub("", prompt)).replace(" ?", "?").strip()
        self.prompt_lbl = Txt(prompt, fs=28 if len(prompt) < 60 else 23, bold=True, size_hint_y=None)
        head.add_widget(self.prompt_lbl)
        if found and has_emoji(found[0]):
            head.add_widget(EmojiImg(found[0], 46, pos_hint={"center_y": 0.5}))
        self.prompt_lbl.bind(height=lambda *_: setattr(head, "height", max(self.prompt_lbl.height, dp(50))))
        self.add_widget(head)

        self.visual_box = AnchorLayout(size_hint_y=None, height=0)
        self.add_widget(self.visual_box)
        self.answer_box = BoxLayout(orientation="vertical", spacing=dp(10), size_hint_y=None, height=0)
        self.add_widget(self.answer_box)
        self.add_widget(Widget())  # Platzhalter unten

        vis = task.visual or ({"kind": "listen"} if task.listen else None)
        kind = (vis or {}).get("kind")
        if kind in ("flash", "flash_text", "flash_photos"):
            self._flash(vis)
            return
        if kind == "flash_grid":
            self._build_grid(flash=vis["seconds"])
            return
        w = visuals.render(vis, on_replay=self.speak if task.listen else None)
        if w is not None:
            self._set_visual(w)
        self._build_answers()
        self._later(0.05, self._ready)

    # --- Hilfen --------------------------------------------------------------------
    def _later(self, sec, fn):
        ev = Clock.schedule_once(lambda *_: fn(), sec)
        self._events.append(ev)

    def cleanup(self):
        for ev in self._events:
            ev.cancel()

    def _set_visual(self, w):
        self.visual_box.clear_widgets()
        self.visual_box.add_widget(w)
        self.visual_box.height = w.height + dp(8)

    def _add_answer(self, w, height=None):
        self.answer_box.add_widget(w)
        self.answer_box.height += (height or w.height) + dp(10)

    def speak(self):
        t = self.task
        self.app.speaker.say(t.listen_text if t.listen else (t.speak or t.prompt), force=True)

    def _ready(self):
        if self.task.listen:
            self.app.speaker.say(self.task.speak or self.task.listen_text, force=True)
        elif self.app.profile.settings.get("tts"):
            self.app.speaker.say(self.task.speak or self.task.prompt)
        self.on_ready()

    # --- Kurz zeigen, dann verdecken ---------------------------------------------------
    def _flash(self, vis):
        kind = vis["kind"]
        box = Box(bg=T.SURFACE, radius=18, orientation="horizontal", size_hint=(None, None), padding=dp(12),
                  spacing=dp(10))
        info = Txt("", fs=17, color=T.MUTED, size_hint_y=None, height=dp(24))
        self.app.speaker.say("Gut aufpassen!" if kind != "flash" else "Merke dir die Bilder!", force=True)
        if kind == "flash":
            for e in vis["items"]:
                box.add_widget(EmojiImg(e, 64))
            box.size = (len(vis["items"]) * dp(74) + dp(24), dp(90))
        elif kind == "flash_photos":
            from lernfuchs import photos
            g = GridLayout(cols=min(5, len(vis["items"])), spacing=dp(8))
            size = 118 if len(vis["items"]) <= 5 else 96
            for it in vis["items"]:
                cell = BoxLayout(orientation="vertical", size_hint=(None, None), size=(dp(size), dp(size + 24)))
                img = Image(texture=pil_texture(photos.square_thumb(it["photo"], size * 2)), size_hint=(None, None),
                            size=(dp(size), dp(size)))
                cell.add_widget(img)
                cell.add_widget(Txt(it["label"], fs=13, size_hint_y=None, height=dp(22), wrap=False))
                g.add_widget(cell)
            rows = (len(vis["items"]) + 4) // 5
            box.add_widget(g)
            box.size = (min(5, len(vis["items"])) * dp(size + 8) + dp(24), rows * dp(size + 32) + dp(24))
        elif vis.get("seq"):
            self._seq_lbl = Txt("", fs=90, color=self.color, bold=True, wrap=False)
            box.add_widget(self._seq_lbl)
            box.size = (dp(320), dp(150))
        elif vis.get("list"):
            g = GridLayout(cols=4, spacing=dp(8))
            for w in vis["items"]:
                c = Box(bg=T.CARD, radius=12)
                c.add_widget(Txt(w, fs=24, bold=True, wrap=False))
                g.add_widget(c)
            box.add_widget(g)
            rows = (len(vis["items"]) + 3) // 4
            box.size = (dp(4 * 190), rows * dp(58) + dp(24))
        else:
            small = vis.get("small")
            lab = Txt(vis["items"][0], fs=24 if small else 58, bold=True, color=T.TEXT if small else self.color)
            box.add_widget(lab)
            box.size = (dp(860) if small else dp(560), dp(150) if small else dp(130))
        wrapper = BoxLayout(orientation="vertical", size_hint=(None, None), size=(box.width, box.height + dp(30)))
        wrapper.add_widget(box)
        wrapper.add_widget(info)
        self._set_visual(wrapper)

        def finish():
            info.text = ""
            box.clear_widgets()
            box.add_widget(EmojiImg("🙈", 64))
            self._build_answers()
            if self.app.profile.settings.get("tts"):
                self.app.speaker.say(self.task.speak or self.task.prompt)
            self.on_ready()

        if vis.get("seq"):
            items = list(vis["items"])
            per = float(vis["seconds"])

            def show(i):
                if i >= len(items):
                    return finish()
                self._seq_lbl.text = items[i]
                info.text = f"Zahl {i + 1} von {len(items)}"
                self._later(per, lambda: (setattr(self._seq_lbl, "text", ""), self._later(0.2, lambda: show(i + 1))))
            self._later(0.5, lambda: show(0))
            return
        left = [float(vis["seconds"])]

        def tick():
            if left[0] <= 0.01:
                return finish()
            info.text = f"Gut merken … {left[0]:.0f} s" if vis["seconds"] >= 2 else "Gut hinsehen!"
            step = min(1.0, left[0])
            left[0] -= step
            self._later(step, tick)
        tick()

    # --- Antwortbereich --------------------------------------------------------------
    def _build_answers(self):
        t = self.task
        {"choice": self._build_choice, "truefalse": self._build_choice, "input": self._build_input,
         "order": self._build_order, "sort": self._build_sort, "grid_click": self._build_grid,
         "multi_click": self._build_multi}.get(t.type, lambda: None)()

    def _build_choice(self):
        t = self.task
        opts = t.options
        emoji_opts = all(is_emoji(o) for o in opts)
        longest = max(len(o) for o in opts)
        if t.type == "truefalse":
            cols, bw = 2, 360
        elif emoji_opts or longest <= 6:
            cols, bw = min(len(opts), 6), 140
        elif longest <= 26:
            cols, bw = (2, 440) if len(opts) <= 4 else (3, 300)
        else:
            cols, bw = 1, 860
        rows = (len(opts) + cols - 1) // cols
        g = GridLayout(cols=cols, spacing=dp(12), size_hint=(None, None),
                       size=(cols * dp(bw) + (cols - 1) * dp(12), rows * dp(70) + (rows - 1) * dp(12)))
        for i, o in enumerate(opts):
            icon = None
            text = o
            if emoji_opts:
                icon, text = o, ""
            elif t.emojis.get(o):
                icon = t.emojis[o]
            if t.type == "truefalse":
                icon = "👍" if i == 0 else "👎"
            b = RButton(text, on_press=lambda o=o: self.submit(o), bg=self.light, fg=T.TEXT,
                        fs=24 if longest <= 14 else 19, icon=icon, icon_size=46 if emoji_opts else 30,
                        size_hint=(None, None), size=(dp(bw), dp(70)))
            g.add_widget(b)
            self.buttons[o] = b
        a = AnchorLayout(size_hint_y=None, height=g.height)
        a.add_widget(g)
        self._add_answer(a)

    def _build_input(self):
        t = self.task
        is_num = t.input_kind == "number"
        row = BoxLayout(orientation="horizontal", size_hint=(None, None), height=dp(68), spacing=dp(12))
        width = 220 if is_num else (520 if len(str(t.answer)) > 12 else 380)
        self.entry = TextInput(multiline=False, font_size=sp(32), halign="center", size_hint=(None, None),
                               size=(dp(width), dp(66)), background_color=C(T.INPUT_BG),
                               foreground_color=C(T.TEXT), cursor_color=C(T.TEXT), padding=(dp(10), dp(12)),
                               readonly=is_num, write_tab=False)
        self.entry.bind(on_text_validate=lambda *_: self.submit(self.entry.text))
        row.add_widget(self.entry)
        if t.unit:
            row.add_widget(Txt(t.unit, fs=26, color=T.MUTED, wrap=False, size_hint=(None, 1), width=dp(60)))
        self.check_btn = RButton("Prüfen", on_press=lambda: self.submit(self.entry.text), bg=self.color, icon="✅",
                                 fs=22, size_hint=(None, None), size=(dp(170), dp(66)))
        row.add_widget(self.check_btn)
        row.width = dp(width) + (dp(72) if t.unit else 0) + dp(194)
        a = AnchorLayout(size_hint_y=None, height=dp(68))
        a.add_widget(row)
        self._add_answer(a)
        if is_num:
            extra = "," if ("," in str(t.answer) or t.unit in ("€", "cm")) else ("R" if "R" in str(t.answer) else "")
            pad = NumPad(self.entry, extra)
            pa = AnchorLayout(size_hint_y=None, height=pad.height)
            pa.add_widget(pad)
            self._add_answer(pa)
        else:
            self._later(0.3, lambda: setattr(self.entry, "focus", True))

    # Reihenfolge
    def _build_order(self):
        t = self.task
        self.placed = []
        letters = all(len(x) <= 2 for x in t.items)
        per_row = 9 if letters else 4
        tile_w = 66 if letters else 200
        self.slot_box = Box(bg=self.light, radius=18, orientation="horizontal", size_hint=(None, None),
                            size=(dp(900), dp(84)), padding=dp(10), spacing=dp(6))
        self.slot_hint = Txt("Tippe die Teile in der richtigen Reihenfolge an", fs=17, color=T.MUTED)
        self.slot_box.add_widget(self.slot_hint)
        a = AnchorLayout(size_hint_y=None, height=dp(84))
        a.add_widget(self.slot_box)
        self._add_answer(a)
        rows = (len(t.items) + per_row - 1) // per_row
        cols = min(per_row, len(t.items))
        g = GridLayout(cols=cols, spacing=dp(8), size_hint=(None, None),
                       size=(cols * dp(tile_w + 8), rows * dp(70)))
        self.pool_btns = []
        for i, it in enumerate(t.items):
            b = RButton(it, on_press=lambda i=i: self._place(i), bg=T.SURFACE, fg=T.TEXT, fs=26 if letters else 19,
                        icon=t.emojis.get(it) or None, size_hint=(None, None), size=(dp(tile_w), dp(62)))
            g.add_widget(b)
            self.pool_btns.append(b)
        pa = AnchorLayout(size_hint_y=None, height=g.height)
        pa.add_widget(g)
        self._add_answer(pa)
        self._tile_w, self._letters = tile_w, letters
        self.check_btn = RButton("Fertig", on_press=self._order_done, bg=self.color, icon="✅", fs=22,
                                 size_hint=(None, None), size=(dp(190), dp(60)))
        ca = AnchorLayout(size_hint_y=None, height=dp(60))
        ca.add_widget(self.check_btn)
        self._add_answer(ca)

    def _order_done(self):
        if len(self.placed) == len(self.task.items):
            self.submit([self.task.items[i] for i in self.placed])

    def _place(self, i):
        if self.locked or i in self.placed:
            return
        self.placed.append(i)
        self.pool_btns[i].disable(T.NEUTRAL_BTN)
        self.pool_btns[i].set_fg(T.DISABLED_TEXT)
        self.app.sounds.play("klick")
        self._redraw_slots()

    def _unplace(self, i):
        if self.locked:
            return
        self.placed.remove(i)
        b = self.pool_btns[i]
        b.enabled = True
        b.set_bg(T.SURFACE)
        b.set_fg(T.TEXT)
        self._redraw_slots()

    def _redraw_slots(self):
        self.slot_box.clear_widgets()
        if not self.placed:
            self.slot_box.add_widget(self.slot_hint)
            return
        for i in self.placed:
            it = self.task.items[i]
            self.slot_box.add_widget(RButton(it, on_press=lambda i=i: self._unplace(i), bg=self.color,
                                             fs=24 if self._letters else 17, size_hint=(None, 1),
                                             width=dp(58 if self._letters else 180)))

    # Sortieren
    def _build_sort(self):
        t = self.task
        self.sort_idx, self.sort_errors, self.sort_given = 0, 0, {}
        top = Box(bg=self.light, radius=20, orientation="horizontal", size_hint=(None, None), size=(dp(460), dp(84)),
                  padding=dp(12), spacing=dp(12))
        self.sort_emoji = EmojiImg("⭐", 60)
        self.sort_word = Txt("", fs=28, bold=True)
        top.add_widget(self.sort_emoji)
        top.add_widget(self.sort_word)
        a = AnchorLayout(size_hint_y=None, height=dp(84))
        a.add_widget(top)
        self._add_answer(a)
        self.sort_count = Txt("", fs=15, color=T.MUTED, size_hint_y=None, height=dp(22))
        self._add_answer(self.sort_count, dp(22))
        palette = ["#4D96FF", "#2EB872", "#FF8C42", "#9B5DE5", "#FF6B6B"]
        width = 210 if len(t.buckets) <= 3 else 175
        row = BoxLayout(orientation="horizontal", spacing=dp(10), size_hint=(None, None),
                        size=(len(t.buckets) * dp(width + 10), dp(250)))
        self.bucket_btns, self.bucket_lists = {}, {}
        for i, bkt in enumerate(t.buckets):
            col = BoxLayout(orientation="vertical", spacing=dp(4), size_hint=(None, 1), width=dp(width))
            b = RButton(bkt, on_press=lambda bkt=bkt: self._sort_pick(bkt), bg=palette[i % 5], fs=19,
                        size_hint=(1, None), height=dp(62))
            col.add_widget(b)
            lst = BoxLayout(orientation="vertical", spacing=dp(3))
            col.add_widget(lst)
            self.bucket_btns[bkt], self.bucket_lists[bkt] = b, lst
            row.add_widget(col)
        ra = AnchorLayout(size_hint_y=None, height=dp(250))
        ra.add_widget(row)
        self._add_answer(ra)
        self._sort_show()

    def _sort_show(self):
        t = self.task
        it = t.items[self.sort_idx]
        e = t.emojis.get(it)
        self.sort_emoji.source = emoji_src(e) if e else ""
        self.sort_emoji.opacity = 1 if e else 0
        self.sort_word.text = it
        self.sort_count.text = f"Begriff {self.sort_idx + 1} von {len(t.items)}"

    def _sort_pick(self, bkt):
        if self.locked:
            return
        t = self.task
        it = t.items[self.sort_idx]
        right = t.answer[it]
        self.sort_given[it] = bkt
        ok = bkt == right
        chip = Box(bg=T.GOOD_LIGHT if ok else T.BAD_LIGHT, radius=8, size_hint_y=None, height=dp(28))
        chip.add_widget(Txt(("richtig: " if ok else "") + it, fs=14, wrap=False))
        self.bucket_lists[right].add_widget(chip)
        if not ok:
            self.sort_errors += 1
            self.app.sounds.play("falsch")
            self.locked = True
            self.bucket_btns[right].border = C(T.GOOD)
            self._later(0.9, lambda: (setattr(self.bucket_btns[right], "border", [0, 0, 0, 0]), self._sort_next()))
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

    # Bild antippen (auch Fotos, auch „merken und umdrehen“)
    def _build_grid(self, flash=None):
        t = self.task
        n = len(t.items)
        photo = isinstance(t.items[0], dict)
        cols = 3 if n <= 9 else 4 if n <= 16 else 5
        size = (130 if n <= 9 else 110 if n <= 12 else 96) if photo else (58 if n <= 16 else 50)
        self.grid_btns, self._photo_tex = [], []
        cache = {}
        g = GridLayout(cols=cols, spacing=dp(8), size_hint=(None, None))
        for i, it in enumerate(t.items):
            b = RButton("", on_press=lambda i=i: self.submit(i), bg=T.SURFACE, size_hint=(None, None),
                        size=(dp(size + 14), dp(size + 14 + (20 if flash else 0))), radius=12)
            b.orientation = "vertical"
            b.padding = dp(6)
            if photo:
                from lernfuchs import photos
                key = (it["photo"], it["fx"], str(it.get("patch")))
                if key not in cache:
                    cache[key] = pil_texture(photos.tile(it["photo"], it["crop"], it["fx"], size * 2, it.get("patch")))
                img = Image(texture=cache[key], fit_mode="contain")
                self._photo_tex.append(cache[key])
            else:
                img = Image(source=emoji_src(it), fit_mode="contain")
            b.add_widget(img)
            b._img = img
            if flash and photo:
                b._lab = Txt(it.get("label", ""), fs=12, color=T.MUTED, size_hint_y=None, height=dp(18), wrap=False)
                b.add_widget(b._lab)
            g.add_widget(b)
            self.grid_btns.append(b)
        rows = (n + cols - 1) // cols
        g.size = (cols * dp(size + 22), rows * dp(size + 22 + (20 if flash else 0)))
        a = AnchorLayout(size_hint_y=None, height=g.height)
        a.add_widget(g)
        self._add_answer(a)
        if not flash:
            return
        self.locked = True
        info = Txt("", fs=17, color=T.MUTED, size_hint_y=None, height=dp(26))
        self._set_visual(info)
        self.app.speaker.say("Merk dir, wo welches Bild liegt!", force=True)
        left = [int(flash)]

        def tick():
            if left[0] <= 0:
                q = emoji_src("❓")
                for b in self.grid_btns:
                    b._img.texture = None
                    b._img.source = q
                    b._lab.text = ""
                info.text = ""
                self.locked = False
                if self.app.profile.settings.get("tts"):
                    self.app.speaker.say(self.task.prompt.split("\n")[-1])
                self.on_ready()
                return
            info.text = f"Gut merken … {left[0]} s"
            left[0] -= 1
            self._later(1, tick)
        tick()

    # Mehrere antippen
    def _build_multi(self):
        t = self.task
        n = len(t.items)
        cols = 4 if n <= 16 else 5
        g = GridLayout(cols=cols, spacing=dp(8), size_hint=(None, None),
                       size=(cols * dp(110), ((n + cols - 1) // cols) * dp(70)))
        self.grid_btns = []
        for i, it in enumerate(t.items):
            b = RButton(it, on_press=lambda i=i: self._toggle(i), bg=T.SURFACE, fg=T.TEXT, fs=26,
                        size_hint=(None, None), size=(dp(102), dp(62)))
            g.add_widget(b)
            self.grid_btns.append(b)
        a = AnchorLayout(size_hint_y=None, height=g.height)
        a.add_widget(g)
        self._add_answer(a)
        self.check_btn = RButton("Fertig", on_press=lambda: self.submit(sorted(self.selected)), bg=self.color,
                                 icon="✅", fs=22, size_hint=(None, None), size=(dp(190), dp(60)))
        ca = AnchorLayout(size_hint_y=None, height=dp(60))
        ca.add_widget(self.check_btn)
        self._add_answer(ca)

    def _toggle(self, i):
        if self.locked:
            return
        b = self.grid_btns[i]
        if i in self.selected:
            self.selected.discard(i)
            b.set_bg(T.SURFACE)
            b.set_fg(T.TEXT)
        else:
            self.selected.add(i)
            b.set_bg(self.color)
            b.set_fg(T.ON_ACCENT)
        self.app.sounds.play("klick")

    # --- Auswertung ----------------------------------------------------------------
    def submit(self, given):
        if self.locked:
            return
        if self.task.type == "input" and not str(given).strip():
            return
        self.attempts += 1
        self.locked = True
        self.on_answer(check(self.task, given), given)

    def show_result(self, correct, given):
        t = self.task
        self.locked = True
        if t.type in ("choice", "truefalse"):
            for o, b in self.buttons.items():
                if o == t.answer:
                    b.set_bg(T.GOOD)
                    b.set_fg(T.ON_ACCENT)
                elif o == given:
                    b.set_bg(T.BAD_LIGHT)
        elif t.type == "input" and self.entry:
            self.entry.background_color = C(T.GOOD_LIGHT if correct else T.BAD_LIGHT)
            self.entry.readonly = True
        elif t.type == "order":
            for w in self.slot_box.children:
                if isinstance(w, RButton):
                    w.set_bg(T.GOOD if correct else T.BAD)
        elif t.type == "grid_click":
            flash = isinstance(t.visual, dict) and t.visual.get("kind") == "flash_grid"
            for i, b in enumerate(self.grid_btns):
                if flash:
                    b._img.source = ""
                    b._img.texture = self._photo_tex[i]
                if i == t.answer:
                    b.set_bg(T.GOOD)
                elif i == given:
                    b.set_bg(T.BAD_LIGHT)
        elif t.type == "multi_click":
            right = set(t.answer)
            for i, b in enumerate(self.grid_btns):
                if i in right:
                    b.set_bg(T.GOOD)
                    b.set_fg(T.ON_ACCENT)
                elif i in self.selected:
                    b.set_bg(T.BAD_LIGHT)

    def allow_retry(self, given):
        t = self.task
        self.locked = False
        if t.type in ("choice", "truefalse") and given in self.buttons:
            self.buttons[given].disable(T.BAD_LIGHT)
        elif t.type == "input" and self.entry:
            self.entry.text = ""
            self.entry.background_color = C(T.BAD_LIGHT)
            self._later(0.7, lambda: setattr(self.entry, "background_color", C(T.INPUT_BG)))
        elif t.type == "order":
            for i in list(self.placed):
                self._unplace(i)
        elif t.type == "grid_click" and isinstance(given, int):
            self.grid_btns[given].disable(T.BAD_LIGHT)

    def can_retry(self):
        t = self.task
        if t.type in ("truefalse", "sort", "multi_click"):
            return False
        if t.type == "choice" and len(t.options) <= 2:
            return False
        return self.attempts == 1
