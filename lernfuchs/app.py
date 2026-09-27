"""Hauptfenster und Navigation."""

import customtkinter as ctk

from . import theme as T
from .emoji import emoji_photo
from .sound import Sounds
from .speech import Speaker
from .storage import Profile


class App(ctk.CTk):
    def __init__(self):
        from .storage import Profile as _P
        T.apply(_P().settings.get("design", "modern"))
        super().__init__(fg_color=T.BG)
        self.title("LernFuchs – Lernen mit Spaß")
        self.geometry("1200x820")
        self.minsize(1040, 740)
        try:
            self._icon = emoji_photo("🦊", 64)
            self.iconphoto(True, self._icon)
        except Exception:
            pass
        self.profile = Profile()
        self.speaker = Speaker(root=self)
        self.sounds = Sounds()
        self.apply_settings()
        self.container = ctk.CTkFrame(self, fg_color=T.BG, corner_radius=0)
        self.container.pack(fill="both", expand=True)
        self.screen = None
        self._screen_cache = {}
        self._key_handler = None
        self.bind("<Key>", self._dispatch_key)
        self.protocol("WM_DELETE_WINDOW", self._close)
        self.after(700, self._warmup)
        if not self.profile.data["name"]:
            from .ui.screens import WelcomeScreen
            self.show(WelcomeScreen)
        else:
            self.go_home()

    # --- Navigation ------------------------------------------------------------
    CACHEABLE = ("HomeScreen", "SubjectScreen")

    def show(self, cls, **kw):
        """Bildschirm wechseln. Start- und Fachseiten werden zwischengespeichert (sofortiger Wechsel)."""
        self.speaker.stop()
        old = self.screen
        self.screen = None
        if old is not None:
            if getattr(old, "_cache_key", None):
                old.pack_forget()
            else:
                old.destroy()
        key = None
        if cls.__name__ in self.CACHEABLE:
            key = (cls.__name__, tuple(sorted(kw.items())), self.profile.rev, T.CURRENT)
            cached = self._screen_cache.get(key)
            if cached is not None and cached.winfo_exists():
                self.screen = cached
                cached.pack(fill="both", expand=True)
                return
            for k in [k for k in self._screen_cache if k[:2] == key[:2]]:  # veraltete Version entfernen
                self._screen_cache.pop(k).destroy()
        self.screen = cls(self, **kw)
        if key:
            self.screen._cache_key = key
            self._screen_cache[key] = self.screen
        self.screen.pack(fill="both", expand=True)

    def go_home(self):
        from .ui.screens import HomeScreen
        self.show(HomeScreen)

    def show_parent(self):
        from .ui.parent import ParentGate
        self.show(ParentGate)

    def start_session(self, subject, topic=None, review_only=False):
        from .ui.session_screen import SessionScreen
        self.show(SessionScreen, subject=subject, topic=topic, review_only=review_only)

    def open_topic(self, topic):
        if topic.kind == "game":
            from .ui.games import GAMES
            self.show(GAMES[topic.id], topic=topic)
        elif topic.kind == "online":
            from .ui.discover import DiscoverScreen
            self.show(DiscoverScreen, topic=topic)
        else:
            self.start_session(topic.subject, topic)

    # --- Tastatur ---------------------------------------------------------------
    def bind_key(self, fn):
        self._key_handler = fn

    def unbind_key(self):
        self._key_handler = None

    def _dispatch_key(self, event):
        if self._key_handler:
            self._key_handler(event)

    # --- Einstellungen ------------------------------------------------------------
    def apply_settings(self):
        st = self.profile.settings
        self.speaker.enabled = bool(st.get("tts", True))
        self.speaker.online = bool(st.get("online", True))
        self.speaker.set_voice(st.get("voice", "conrad"))
        self.speaker.set_rate(st.get("tts_rate", -1))
        if T.CURRENT != st.get("design", "modern"):
            T.apply(st.get("design", "modern"))
            self.configure(fg_color=T.BG)
            if hasattr(self, "container"):
                self.container.configure(fg_color=T.BG)
        if st.get("online", True):
            from . import photos
            if len(photos.available()) < 25:
                photos.prefetch()
        self.sounds.enabled = bool(st.get("sound", True))

    def _warmup(self):
        """Lädt im Hintergrund 3D-Emojis, Animationen und häufige Sätze vor – danach läuft alles ohne Wartezeit."""
        from . import emoji as E
        E.online = bool(self.profile.settings.get("online", True))
        if not E.online:
            return
        from .content import topics as TP, knobeln, mathe, konz
        from .content.deutsch_data import NOMEN, KOMPOSITA
        from .content.sach_data import FRAGEN, SORTS, ORDERS
        from .storage import STICKERS
        from .ui import widgets, session_screen
        texts = [t.emoji for t in TP.TOPICS] + list(T.SUBJECT_EMOJI.values()) + [n["e"] for n in NOMEN if n["e"]]
        texts += [f["e"] for lst in FRAGEN.values() for f in lst if f["e"]]
        texts += [e for s in SORTS for e in s[5].values()] + [e for o in ORDERS for e in o[5].values()]
        texts += knobeln.SYMBOLS + mathe.FRUITS + STICKERS + [e for grp in konz.LOOKALIKES for e in grp]
        texts += [k[3] for k in KOMPOSITA] + [r[2] for r in T.RANKS]
        texts += list("⭐🔥🏅🔒✅💡🔊⬅️✖️❓🙈👍👎⏳🎯📒🧐🤔🚀💪🎉🏆💥⚡🔍📡🎲🔁🏠🔄💾🔓⏱️")
        E.prefetch_anims(list(widgets.ANIM_STILL))  # zuerst die Animationen, dann die 3D-Symbole
        E.prewarm([t for t in texts if t])
        self.speaker.prefetch(session_screen.SPOKEN_PRAISE + session_screen.SPOKEN_FAST + [
            "Gut aufpassen!", "Merke dir die Bilder!", "Merk dir, wo welches Bild liegt!", "Boss besiegt! Stark!",
            "5 richtige in Folge!", "10 richtige in Folge!"])

    def _close(self):
        try:
            self.speaker.stop()
            self.profile.save()
            self.profile.backup()
        finally:
            self.destroy()


def main():
    App().mainloop()
