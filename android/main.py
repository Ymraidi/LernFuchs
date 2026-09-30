"""LernFuchs für Android-Tablets (Kivy). Am PC zum Testen: python main.py

Der Start ist abgesichert: Tritt ein Fehler auf, zeigt die App die Fehlermeldung auf dem Bildschirm an
(statt sich kommentarlos zu schließen) und speichert sie zusätzlich in daten/fehler.txt.
"""

import json
import os
import shutil
import traceback

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
from kivy.base import ExceptionHandler, ExceptionManager  # noqa: E402
from kivy.core.window import Window  # noqa: E402
from kivy.uix.label import Label  # noqa: E402
from kivy.uix.scrollview import ScrollView  # noqa: E402


def save_error(text):
    try:
        os.makedirs(_DATA, exist_ok=True)
        with open(os.path.join(_DATA, "fehler.txt"), "a", encoding="utf-8") as fh:
            fh.write(text + "\n\n")
    except OSError:
        pass


def error_view(text):
    """Große, gut lesbare Fehlermeldung (zum Abfotografieren)."""
    sv = ScrollView(do_scroll_x=False)
    lbl = Label(text="LernFuchs – Fehler beim Start\nBitte dieses Bild abfotografieren und schicken:\n\n" + text,
                color=(1, 0.85, 0.85, 1), font_size="15sp", halign="left", valign="top", size_hint_y=None,
                padding=(20, 20))
    lbl.bind(width=lambda *_: setattr(lbl, "text_size", (lbl.width - 40, None)),
             texture_size=lambda *_: setattr(lbl, "height", lbl.texture_size[1] + 40))
    sv.add_widget(lbl)
    return sv


class _ShowErrors(ExceptionHandler):
    """Fehler während der Benutzung: anzeigen statt abstürzen."""

    def handle_exception(self, exc):
        text = traceback.format_exc()
        save_error(text)
        app = App.get_running_app()
        try:
            if app and getattr(app, "sm", None) is not None:
                from kivy.uix.popup import Popup
                Popup(title="Ups – ein Fehler (bitte Foto schicken)", content=error_view(text),
                      size_hint=(0.9, 0.9)).open()
                return ExceptionManager.PASS
        except Exception:
            pass
        return ExceptionManager.RAISE


ExceptionManager.add_handler(_ShowErrors())


class LernFuchsApp(App):
    title = "LernFuchs"

    def build(self):
        try:
            return self._build()
        except Exception:
            text = traceback.format_exc()
            save_error(text)
            Window.clearcolor = (0.1, 0.05, 0.08, 1)
            return error_view(text)

    def _build(self):
        from kivy.uix.screenmanager import ScreenManager, SlideTransition
        from lernfuchs import theme as T
        from lernfuchs.storage import Profile
        from lfapp.speech import Speaker
        from lfapp.ui import C
        Window.softinput_mode = "below_target"
        Window.bind(on_keyboard=self._on_key)
        self.profile = Profile()
        T.apply(self.profile.settings.get("tablet_theme", "bey"))
        Window.clearcolor = C(T.BG)
        self.speaker = Speaker()
        try:
            self.sounds = Sounds()
        except Exception:  # Klänge sind nicht wichtig genug, um den Start zu verhindern
            save_error(traceback.format_exc())
            self.sounds = _NoSounds()
        try:
            install_photos()
        except Exception:
            save_error(traceback.format_exc())
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
            if getattr(self, "sm", None) and self.sm.current_screen and \
                    self.sm.current_screen.__class__.__name__ != "HomeScreen":
                self.go_home()
                return True
        return False

    def on_pause(self):
        if getattr(self, "profile", None):
            self.profile.save()
        return True

    def on_stop(self):
        if getattr(self, "profile", None):
            self.profile.save()


class _NoSounds:
    enabled = False

    def play(self, name):
        pass


class Sounds:
    def __init__(self):
        from kivy.core.audio import SoundLoader
        from lernfuchs.sound import _MELODIES, _write
        from lernfuchs.storage import DATA_DIR
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
    from lernfuchs.storage import DATA_DIR
    from lfapp.ui import ASSETS
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


if __name__ == "__main__":
    try:
        LernFuchsApp().run()
    except Exception:
        save_error(traceback.format_exc())
        raise
