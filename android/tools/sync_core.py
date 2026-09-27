"""Kopiert den gemeinsamen Kern (Aufgaben, Stufen, Fehlerbox, Inhalte) aus ../lernfuchs in die Android-App.

Die Aufgaben-Logik gibt es damit nur EINMAL – Änderungen am PC gelten nach dem Sync auch auf dem Tablet.
"""

import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
ANDROID = os.path.dirname(HERE)
SRC = os.path.join(os.path.dirname(ANDROID), "lernfuchs")
DST = os.path.join(ANDROID, "lernfuchs")

CORE = ["__init__.py", "tasks.py", "adaptive.py", "storage.py", "photos.py", "speech.py", "sound.py", "theme.py"]


def main():
    if os.path.isdir(DST):
        shutil.rmtree(DST)
    os.makedirs(os.path.join(DST, "content"))
    for fn in CORE:
        shutil.copy2(os.path.join(SRC, fn), os.path.join(DST, fn))
    for fn in os.listdir(os.path.join(SRC, "content")):
        if fn.endswith(".py"):
            shutil.copy2(os.path.join(SRC, "content", fn), os.path.join(DST, "content", fn))
    print("Kern synchronisiert:", DST)


if __name__ == "__main__":
    main()
