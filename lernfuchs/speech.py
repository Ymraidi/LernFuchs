"""Vorlesen: natürliche Neural-Stimme (online, mit Zwischenspeicher) oder Windows-Stimme (offline).

Stimmen:
  conrad / killian  – männlich, sehr natürlich (Microsoft Neural, NUR Deutsch, benötigt Internet; wird gespeichert)
  (Mehrsprachige Stimmen wie „Florian Multilingual“ werden bewusst nicht verwendet: sie raten die Sprache
   und lesen deutsche Sätze teils englisch vor.)
  stefan                      – männlich, offline (Windows)
  hedda                       – weiblich, offline (Windows)
Fällt die Online-Stimme aus oder ist sie zu langsam, spricht automatisch Stefan.
"""

import asyncio
import ctypes
import hashlib
import os
import re
import threading
import time

from .storage import DATA_DIR

_SPEAK_ASYNC = 1
_PURGE = 2
CACHE_DIR = os.path.join(DATA_DIR, "stimme")
from concurrent.futures import ThreadPoolExecutor
_POOL = ThreadPoolExecutor(max_workers=3)

NEURAL = {"conrad": "de-DE-ConradNeural", "killian": "de-DE-KillianNeural"}
VOICE_LABELS = {"conrad": "Conrad (männlich, natürlich, online)", "killian": "Killian (männlich, natürlich, online)",
                "stefan": "Stefan (männlich, offline – klingt eher technisch)",
                "hedda": "Hedda (weiblich, offline)"}


def speakify(text: str) -> str:
    """Macht Aufgaben natürlich vorlesbar: „7 × 8 = ?“ → „Wie viel ist 7 mal 8?“, Emojis weg."""
    t = text.strip()
    t = re.sub(r"^(.*?)\s*=\s*\?\s*$", r"Wie viel ist \1?", t, flags=re.M)
    t = re.sub(r"^___\s*([+−×:])\s*(\S+)\s*=\s*(\S+)$", r"Welche Zahl \1 \2 ergibt \3?", t, flags=re.M)
    t = re.sub(r"^(\S+)\s*([+−×:])\s*___\s*=\s*(\S+)$", r"\1 \2 welche Zahl ergibt \3?", t, flags=re.M)
    t = t.replace("\n", ". ").replace("?.", "?").replace(":.", ":").replace("!.", "!")
    t = t.replace("(cm²)", "")
    for unit, word in UNITS:  # „7 m = ___ cm“ → „7 Meter sind wie viele Zentimeter?“
        t = re.sub(r"=\s*_+\s*" + unit + r"(?![\wäöüß])", " sind wie viele " + word + "?", t)
        t = re.sub(r"_+\s*" + unit + r"(?![\wäöüß])", "wie viele " + word, t)
    t = re.sub(r"\.\s*\.", ".", t)
    t = t.replace("○", " und ").replace("„", "").replace("“", "")
    try:  # Emojis als deutsches Wort vorlesen (🐞 → Marienkäfer)
        import emoji as emj
        t = emj.replace_emoji(t, replace=lambda ch, data: " " + emj.demojize(ch, language="de").strip(":")
                              .replace("_", " ") + " ")
    except Exception:
        pass
    t = re.sub(r"_+", " Lücke ", t)
    t = t.replace("×", " mal ").replace("·", " mal ")
    t = re.sub(r"(\d)\s*:\s*(\d+)(?!\d*\s*Uhr)", r"\1 geteilt durch \2", t)
    t = t.replace("−", " minus ")
    t = t.replace("+", " plus ").replace("=", " ist ")
    t = t.replace("<", " kleiner als ").replace(">", " größer als ")
    t = t.replace("€", " Euro ").replace("→", ", ")
    t = re.sub(r"(\d)\s*ct\b", r"\1 Cent", t)
    for unit, word in UNITS:
        t = re.sub(r"(\d)\s*" + unit + r"(?![\wäöüß])", r"\1 " + word, t)
    for abbr, word in ABBR:
        t = t.replace(abbr, word)
    t = t.replace("…", " ")
    t = re.sub("[\U0001F000-\U0001FAFF\u2600-\u27BF\uFE0F\u200d]", "", t)
    return re.sub(r"\s+", " ", t).strip()


UNITS = [("cm²", "Quadratzentimeter"), ("km", "Kilometer"), ("kg", "Kilogramm"), ("cm", "Zentimeter"),
         ("mm", "Millimeter"), ("ml", "Milliliter"), ("min", "Minuten"), ("m", "Meter"), ("g", "Gramm"),
         ("l", "Liter"), ("t", "Tonnen"), ("s", "Sekunden")]
ABBR = [("z. B.", "zum Beispiel"), ("z.B.", "zum Beispiel"), ("bzw.", "beziehungsweise"), ("ca.", "circa"),
        ("usw.", "und so weiter"), ("Nr.", "Nummer"), ("Std.", "Stunden"), ("PROFI", "Profi")]


class _MCI:
    """MP3-Wiedergabe über die Windows-Multimedia-API (ohne Zusatzpakete)."""

    def __init__(self):
        self._send = ctypes.windll.winmm.mciSendStringW
        self._open = False

    def play(self, path):
        self.stop()
        if self._send(f'open "{path}" type mpegvideo alias lfvoice', None, 0, 0) == 0:
            self._open = True
            self._send("play lfvoice", None, 0, 0)

    def playing(self) -> bool:
        if not self._open:
            return False
        buf = ctypes.create_unicode_buffer(64)
        self._send("status lfvoice mode", buf, 64, 0)
        return buf.value == "playing"

    def stop(self):
        if self._open:
            self._send("stop lfvoice", None, 0, 0)
            self._send("close lfvoice", None, 0, 0)
            self._open = False


class Speaker:
    def __init__(self, root=None):
        self.root = root
        self.enabled = True
        self.online = True
        self.rate = -1
        self.voice = "conrad"
        self._gen = 0
        self._waiting = False
        self._sapi = None
        self._sapi_tokens = {}
        self._mci = None
        self._pending = {}
        try:
            import win32com.client
            self._sapi = win32com.client.Dispatch("SAPI.SpVoice")
            for cat_path in (r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech_OneCore\Voices",
                             r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices"):
                try:
                    cat = win32com.client.Dispatch("SAPI.SpObjectTokenCategory")
                    cat.SetId(cat_path, False)
                    toks = cat.EnumerateTokens()
                    for i in range(toks.Count):
                        desc = toks.Item(i).GetDescription()
                        for key in ("Stefan", "Hedda", "Katja"):
                            if key in desc and key.lower() not in self._sapi_tokens:
                                self._sapi_tokens[key.lower()] = toks.Item(i)
                except Exception:
                    pass
        except Exception:
            self._sapi = None
        try:
            self._mci = _MCI()
        except Exception:
            self._mci = None
        self._apply_sapi_voice()

    # --- Einstellungen ---------------------------------------------------------
    def set_voice(self, name: str):
        self.voice = name if name in VOICE_LABELS else "conrad"
        self._apply_sapi_voice()

    def _apply_sapi_voice(self):
        if not self._sapi:
            return
        want = "hedda" if self.voice == "hedda" else "stefan"
        tok = self._sapi_tokens.get(want) or self._sapi_tokens.get("stefan") or self._sapi_tokens.get("hedda")
        if tok is not None:
            try:
                self._sapi.Voice = tok
            except Exception:
                pass
        try:
            self._sapi.Rate = self.rate
        except Exception:
            pass

    def set_rate(self, rate: int):
        self.rate = int(rate)
        self._apply_sapi_voice()

    @property
    def available(self) -> bool:
        return self._sapi is not None or self._mci is not None

    def _neural(self) -> bool:
        return self.voice in NEURAL and self.online and self._mci is not None and self.root is not None

    # --- Neural (online) ----------------------------------------------------------
    def _cache_path(self, text):
        key = hashlib.md5(f"{self.voice}|{self.rate}|{text}".encode("utf-8")).hexdigest()
        return os.path.join(CACHE_DIR, key + ".mp3")

    def _synth(self, text, path):
        try:
            import edge_tts
            os.makedirs(CACHE_DIR, exist_ok=True)
            tmp = path + ".part"
            rate = f"{self.rate * 6:+d}%"
            asyncio.run(edge_tts.Communicate(text, NEURAL[self.voice], rate=rate).save(tmp))
            if os.path.getsize(tmp) > 500:
                os.replace(tmp, path)
            return True
        except Exception:
            return False

    def prefetch(self, texts):
        """Erzeugt Sprachdateien im Voraus (z. B. für Lesetexte), damit es später sofort klingt."""
        if not self._neural():
            return
        todo = []
        for t in texts:
            if t:
                t = speakify(t)
                p = self._cache_path(t)
                if not os.path.exists(p) and p not in self._pending:
                    self._pending[p] = True
                    todo.append((t, p))
        for t, p in todo:
            def work(t=t, p=p):
                self._synth(t, p)
                self._pending.pop(p, None)
            _POOL.submit(work)

    # --- API -------------------------------------------------------------------
    def say(self, text: str, force: bool = False):
        if not text or (not self.enabled and not force):
            return
        text = speakify(text)
        self.stop()
        self._gen += 1
        gen = self._gen
        if self._neural():
            path = self._cache_path(text)
            if os.path.exists(path):
                self._mci.play(path)
                return
            state = {"done": False, "ok": False}
            self._waiting = True

            def work():
                state["ok"] = self._synth(text, path)
                state["done"] = True
            threading.Thread(target=work, daemon=True).start()
            deadline = time.monotonic() + min(12.0, 6.0 + len(text) / 100)

            def poll():
                if gen != self._gen:
                    return
                if state["done"] or time.monotonic() > deadline:
                    self._waiting = False
                if state["done"]:
                    if state["ok"] and os.path.exists(path):
                        self._mci.play(path)
                    else:
                        self._sapi_say(text)
                    return
                if time.monotonic() > deadline:
                    self._sapi_say(text)  # Internet hängt → Offline-Stimme
                    return
                self.root.after(40, poll)
            self.root.after(40, poll)
            return
        self._sapi_say(text)

    def _sapi_say(self, text):
        if self._sapi is not None:
            try:
                self._sapi.Speak(text, _SPEAK_ASYNC | _PURGE)
            except Exception:
                pass

    def is_speaking(self) -> bool:
        """True, solange gesprochen wird oder eine Sprachausgabe gerade erzeugt wird."""
        if self._waiting:
            return True
        try:
            if self._mci is not None and self._mci.playing():
                return True
        except Exception:
            pass
        try:
            if self._sapi is not None and self._sapi.Status.RunningState == 2:
                return True
        except Exception:
            pass
        return False

    def stop(self):
        self._gen += 1
        self._waiting = False
        if self._mci is not None:
            try:
                self._mci.stop()
            except Exception:
                pass
        if self._sapi is not None:
            try:
                self._sapi.Speak("", _SPEAK_ASYNC | _PURGE)
            except Exception:
                pass
