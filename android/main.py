"""LernFuchs für Android-Tablets (Kivy). Am PC zum Testen: python main.py"""

import json
import os
import shutil

from kivy.utils import platform

# Datenordner festlegen, BEVOR die gemeinsamen Module geladen werden
if platform == "android":
    _DATA = os.path.join(os.environ.get("ANDROID_PRIVATE", os.getcwd()), "daten")
else:
    _DATA = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "LernFuchs", "tablet_daten")
os.environ.setdefault("LERNFUCHS_DATA", _DATA)

if platform != "android":
    # Am PC (Test): Bildschirmdichte fest vorgeben – manche PCs melden sonst 0
    os.environ.setdefault("KIVY_METRICS_DENSITY", "1")
    os.environ.setdefault("KIVY_METRICS_FONTSCALE", "1")
    from kivy.config import Config
    Config.set("graphics", "width", "1280")
    Config.set("graphics", "height", "800")
    Config.set("input", "mouse", "mouse,multitouch_on_demand")

from kivy.app import App  # noqa: E402
from kivy.core.audio import SoundLoader  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.uix.screenmanager import ScreenManager, SlideTransition  # noqa: E402

from lernfuchs import theme as T  # noqa: E402
from lernfuchs.storage import DATA_DIR, Profile  # noqa: E402
from lfapp.speech import Speaker  # noqa: E402
from lfapp.ui import ASSETS, C  # noqa: E402


class Sounds:
    def __init__(self):
        from lernfuchs.sound import _MELODIES, _write
        self.enabled = True
        self._s = {}
        folder = os.path.join(DATA_DIR, "klaenge")
        os.makedirs(folder, exist_ok=True)
        for name, notes in _MELODIES.items():
            p = os.path.join(folder, name + ".wav")
            if not os.path.exists(p):
                _write(p, notes)
            self._s[name] = SoundLoader.load(p)

    def play(self, name):
        s = self._s.get(name)
        if self.enabled and s:
            s.stop()
            s.play()


def install_photos():
    """Mitgelieferte Fotos in den Datenordner übernehmen (einmalig)."""
    dst = os.path.join(DATA_DIR, "fotos")
    idx_file = os.path.join(dst, "index.json")
    if os.path.exists(idx_file):
        return
    os.makedirs(dst, exist_ok=True)
    src = os.path.join(ASSETS, "fotos")
    try:
        with open(os.path.join(src, "index.json"), encoding="utf-8") as fh:
            titles = json.load(fh)
    except (OSError, ValueError):
        return
    idx = {}
    for fn, title in titles.items():
        if os.path.exists(os.path.join(src, fn)):
            shutil.copy2(os.path.join(src, fn), os.path.join(dst, fn))
            idx[title] = {"file": fn, "title": title}
    with open(idx_file, "w", encoding="utf-8") as fh:
        json.dump(idx, fh, ensure_ascii=False)


class LernFuchsApp(App):
    title = "LernFuchs"

    def build(self):
        Window.clearcolor = C(T.BG)
        Window.softinput_mode = "below_target"
        Window.bind(on_keyboard=self._on_key)
        self.profile = Profile()
        T.apply(self.profile.settings.get("tablet_theme", "bey"))
        Window.clearcolor = C(T.BG)
        self.speaker = Speaker()
        self.sounds = Sounds()
        install_photos()
        self.apply_settings()
        self.sm = ScreenManager(transition=SlideTransition(duration=0.25))
        self._n = 0
        if self.profile.data["name"]:
            self.go_home()
        else:
            from lfapp.screens import WelcomeScreen
            self._show(WelcomeScreen(self, name=self._name()))
        return self.sm

    # --- Navigation --------------------------------------------------------------------
    def _name(self):
        self._n += 1
        return f"s{self._n}"

    def _show(self, screen, direction="left"):
        old = self.sm.current_screen
        self.sm.transition.direction = direction
        self.sm.add_widget(screen)
        self.sm.current = screen.name
        if old is not None:
            self.sm.transition.bind(on_complete=lambda *_: old.parent and self.sm.remove_widget(old))

    def go_home(self):
        from lfapp.screens import HomeScreen
        self.speaker.stop()
        self._show(HomeScreen(self, name=self._name()), "right")

    def open(self, what):
        from lfapp import screens
        cls = {"collection": screens.CollectionScreen, "gate": screens.GateScreen, "parent": screens.ParentScreen}[what]
        self._show(cls(self, name=self._name()))

    def open_subject(self, subject):
        from lfapp.screens import SubjectScreen
        self._show(SubjectScreen(self, subject, name=self._name()))

    def open_topic(self, topic):
        if topic.kind == "game":
            from lfapp.games import GAMES
            if topic.id in GAMES:
                self._show(GAMES[topic.id](self, topic, name=self._name()))
        elif topic.kind == "tasks":
            self.start_session(topic.subject, topic)

    def start_session(self, subject, topic=None, review_only=False):
        from lfapp.session import SessionScreen
        self.speaker.stop()
        self._show(SessionScreen(self, subject, topic, review_only, name=self._name()))

    def show_result(self, **kw):
        from lfapp.screens import ResultScreen
        self._show(ResultScreen(self, name=self._name(), **kw))

    def apply_settings(self):
        st = self.profile.settings
        self.speaker.enabled = bool(st.get("tts", True))
        self.speaker.set_rate(float(st.get("tablet_rate", 0.95)))
        self.sounds.enabled = bool(st.get("sound", True))

    def _on_key(self, window, key, *args):
        if key == 27:  # Zurück-Taste von Android → zur Startseite statt App schließen
            if self.sm.current_screen and self.sm.current_screen.__class__.__name__ != "HomeScreen":
                self.go_home()
                return True
        return False

    def on_pause(self):
        self.profile.save()
        return True

    def on_stop(self):
        self.profile.save()


if __name__ == "__main__":
    LernFuchsApp().run()
