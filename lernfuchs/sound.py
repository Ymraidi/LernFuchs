"""Kleine, freundliche Klänge (werden beim ersten Start als WAV erzeugt)."""

import math
import os
import struct
import wave

from .storage import DATA_DIR

SOUND_DIR = os.path.join(DATA_DIR, "klaenge")

_MELODIES = {
    "richtig": [(784, 0.09), (1047, 0.16)],
    "falsch": [(330, 0.12), (262, 0.2)],
    "stufe": [(523, 0.1), (659, 0.1), (784, 0.1), (1047, 0.25)],
    "sticker": [(659, 0.08), (784, 0.08), (988, 0.08), (1319, 0.3)],
    "klick": [(1200, 0.03)],
    "zeit": [(440, 0.15), (440, 0.15)],
    "fertig": [(523, 0.12), (659, 0.12), (784, 0.12), (1047, 0.12), (784, 0.1), (1047, 0.35)],
}


def _write(path, notes, rate=22050):
    frames = bytearray()
    for freq, dur in notes:
        n = int(rate * dur)
        for i in range(n):
            t = i / rate
            env = min(1.0, i / (rate * 0.01)) * max(0.0, 1 - i / n) ** 1.5
            v = env * (0.6 * math.sin(2 * math.pi * freq * t) + 0.15 * math.sin(4 * math.pi * freq * t))
            frames += struct.pack("<h", int(v * 12000))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))


class Sounds:
    def __init__(self):
        self.enabled = True
        self._ok = False
        try:
            import winsound  # noqa: F401
            os.makedirs(SOUND_DIR, exist_ok=True)
            for name, notes in _MELODIES.items():
                p = os.path.join(SOUND_DIR, name + ".wav")
                if not os.path.exists(p):
                    _write(p, notes)
            self._ok = True
        except Exception:
            self._ok = False

    def play(self, name: str):
        if not (self.enabled and self._ok):
            return
        try:
            import winsound
            winsound.PlaySound(os.path.join(SOUND_DIR, name + ".wav"),
                               winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
        except Exception:
            pass
