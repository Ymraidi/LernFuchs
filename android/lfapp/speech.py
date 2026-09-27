"""Sprachausgabe auf dem Tablet: Android-Sprachsynthese (Google, Deutsch) – offline, natürlich.

Am PC (zum Testen) wird die Windows-Stimme benutzt, falls vorhanden.
"""

from kivy.utils import platform

from lernfuchs.speech import speakify


class Speaker:
    def __init__(self):
        self.enabled = True
        self.rate = 0.95
        self.ok = False
        self._tts = None
        self._win = None
        if platform == "android":
            self._init_android()
        else:
            try:
                import win32com.client
                self._win = win32com.client.Dispatch("SAPI.SpVoice")
                for i in range(self._win.GetVoices().Count):
                    v = self._win.GetVoices().Item(i)
                    if "German" in v.GetDescription():
                        self._win.Voice = v
                self.ok = True
            except Exception:
                self._win = None

    # --- Android ----------------------------------------------------------------------
    def _init_android(self):
        try:
            from jnius import PythonJavaClass, autoclass, java_method

            speaker = self

            class _Init(PythonJavaClass):
                __javainterfaces__ = ["android/speech/tts/TextToSpeech$OnInitListener"]
                __javacontext__ = "app"

                @java_method("(I)V")
                def onInit(self, status):
                    speaker._on_init(status)

            self._listener = _Init()
            activity = autoclass("org.kivy.android.PythonActivity").mActivity
            self._TTS = autoclass("android.speech.tts.TextToSpeech")
            self._String = autoclass("java.lang.String")
            self._tts = self._TTS(activity, self._listener)
        except Exception:
            self._tts = None

    def _on_init(self, status):
        if status != 0 or self._tts is None:
            return
        try:
            from jnius import autoclass
            Locale = autoclass("java.util.Locale")
            self._tts.setLanguage(Locale.GERMANY)
            self._tts.setSpeechRate(self.rate)
            self.ok = True
        except Exception:
            self.ok = False

    # --- API ----------------------------------------------------------------------------
    def set_rate(self, rate):
        self.rate = rate
        if self._tts is not None and self.ok:
            try:
                self._tts.setSpeechRate(rate)
            except Exception:
                pass

    def say(self, text, force=False):
        if not text or (not self.enabled and not force):
            return
        text = speakify(text)
        if self._tts is not None and self.ok:
            try:
                from jnius import cast
                self._tts.speak(cast("java.lang.CharSequence", self._String(text)), 0, None, "lernfuchs")
            except Exception:
                pass
        elif self._win is not None:
            try:
                self._win.Speak(text, 1 | 2)
            except Exception:
                pass

    def stop(self):
        if self._tts is not None and self.ok:
            try:
                self._tts.stop()
            except Exception:
                pass
        elif self._win is not None:
            try:
                self._win.Speak("", 1 | 2)
            except Exception:
                pass

    def is_speaking(self):
        try:
            if self._tts is not None and self.ok:
                return bool(self._tts.isSpeaking())
            if self._win is not None:
                return self._win.Status.RunningState == 2
        except Exception:
            pass
        return False
