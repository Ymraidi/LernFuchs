"""Profil & Fortschritt als JSON-Datei (lokal, offline)."""

import copy
import datetime as dt
import json
import os

# Daten liegen immer lokal (schnell) – nie auf dem Netzlaufwerk.
LEGACY_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "daten")
DATA_DIR = os.environ.get("LERNFUCHS_DATA") or \
    os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "LernFuchs", "daten")
PROFILE_FILE = os.path.join(DATA_DIR, "profil.json")
BACKUP_DIR = os.environ.get("LERNFUCHS_BACKUP") or ""


def _migrate():
    """Übernimmt ein bisheriges Profil (lag früher neben dem Programm bzw. in der Sicherung)."""
    if os.environ.get("LERNFUCHS_DATA") or os.path.exists(PROFILE_FILE):
        return
    for old in (os.path.join(LEGACY_DIR, "profil.json"),
                os.path.join(BACKUP_DIR, "profil.json") if BACKUP_DIR else ""):
        if old and os.path.exists(old):
            try:
                import shutil
                os.makedirs(DATA_DIR, exist_ok=True)
                shutil.copy2(old, PROFILE_FILE)
            except OSError:
                pass
            return


_migrate()

DEFAULT = {
    "version": 1,
    "name": "",
    "settings": {
        "grade": 2,
        # Mindeststufe je Fach (1–8); die Stufe steigt automatisch mit dem Lernerfolg
        "difficulty": {"deutsch": 1, "mathe": 1, "sach": 1, "konz": 1},
        # Sekunden pro Aufgabe (0 = ohne Sanduhr)
        "timer": {"deutsch": 45, "mathe": 30, "sach": 40, "konz": 30},
        "tasks_per_round": 10,
        "daily_goal": 20,
        "sound": True,
        "break_every": 8,
        "tts": True,
        "tts_rate": -1,
        "online": True,
        "voice": "conrad",
        "design": "modern",
        "specials": True,
        "retry": True,
    },
    "skills": {},
    "review": [],
    "stars": 0,
    "stickers": 0,
    "streak": {"last": "", "days": 0},
    "sessions": [],
    "records": {},
}


def today() -> str:
    return dt.date.today().isoformat()


def _merge(base: dict, data: dict) -> dict:
    out = copy.deepcopy(base)
    for k, v in data.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _merge(out[k], v)
        else:
            out[k] = v
    return out


class Profile:
    def __init__(self, path: str = PROFILE_FILE):
        self.path = path
        self.data = copy.deepcopy(DEFAULT)
        self.load()

    # --- Laden/Speichern -----------------------------------------------------
    def load(self):
        try:
            with open(self.path, encoding="utf-8") as fh:
                self.data = _merge(DEFAULT, json.load(fh))
        except (OSError, ValueError):
            self.data = copy.deepcopy(DEFAULT)

    rev = 0  # Änderungszähler – zwischengespeicherte Bildschirme werden dann neu gebaut

    def save(self):
        self.rev += 1
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        tmp = self.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(self.data, fh, ensure_ascii=False, separators=(",", ":"))
        os.replace(tmp, self.path)

    def backup(self):
        """Sicherungskopie des Profils (z. B. auf das Netzlaufwerk) – beim Beenden."""
        if BACKUP_DIR:
            try:
                import shutil
                os.makedirs(BACKUP_DIR, exist_ok=True)
                shutil.copy2(self.path, os.path.join(BACKUP_DIR, "profil.json"))
            except OSError:
                pass

    # --- Bequeme Zugriffe ----------------------------------------------------
    @property
    def settings(self) -> dict:
        return self.data["settings"]

    @property
    def grade(self) -> int:
        return int(self.settings["grade"])

    def skill(self, key: str) -> dict:
        sk = self.data["skills"].setdefault(
            key, {"level": 1.0, "seen": 0, "correct": 0, "hist": []})
        return sk

    def add_stars(self, n: int) -> bool:
        """Sterne gutschreiben. Gibt True zurück, wenn ein neuer Sticker frei wird."""
        before = self.data["stars"] // STARS_PER_STICKER
        self.data["stars"] += n
        after = self.data["stars"] // STARS_PER_STICKER
        if after > before:
            self.data["stickers"] = min(after, len(STICKERS))
            return True
        return False

    def touch_streak(self):
        st = self.data["streak"]
        t = dt.date.today()
        if st["last"] == t.isoformat():
            return
        yesterday = (t - dt.timedelta(days=1)).isoformat()
        st["days"] = st["days"] + 1 if st["last"] == yesterday else 1
        st["last"] = t.isoformat()

    def streak_days(self) -> int:
        st = self.data["streak"]
        t = dt.date.today()
        if st["last"] in (t.isoformat(), (t - dt.timedelta(days=1)).isoformat()):
            return st["days"]
        return 0

    def log_session(self, entry: dict):
        self.data["sessions"].append(entry)
        self.data["sessions"] = self.data["sessions"][-300:]


STARS_PER_STICKER = 25
STICKERS = [
    "🦊", "🐶", "🐱", "🐰", "🐻", "🐼", "🐨", "🐯", "🦁", "🐮",
    "🐷", "🐸", "🐵", "🐔", "🐧", "🐦", "🦉", "🦄", "🐝", "🦋",
    "🐢", "🐙", "🐬", "🐳", "🦈", "🦕", "🦖", "🐘", "🦒", "🦓",
    "🦔", "🐿️", "🦦", "🦥", "🦩", "🦜", "🐞", "🐌", "🦀", "🐉",
    "🚀", "🛸", "🏰", "⚽", "🎸", "🎨", "🏆", "👑", "🌈", "💎",
]
