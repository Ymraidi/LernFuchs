"""Adaptive Schwierigkeit und Fehlerbox (verteilte Wiederholung nach Leitner-Prinzip)."""

import datetime as dt
import json

from .storage import Profile, today
from .tasks import Task

MIN_LEVEL, MAX_LEVEL = 1.0, 8.99
PROFI_FROM = 6  # ab Stufe 6: „Profi“ – Aufgaben aus der nächsthöheren Klasse


def min_level(profile: Profile, subject: str) -> int:
    """Von den Eltern gewählte Mindeststufe (0/1 = keine Untergrenze)."""
    return max(1, min(8, int(profile.settings["difficulty"].get(subject, 0) or 1)))


def level_for(profile: Profile, subject: str, skill: str) -> int:
    """Aktuelle Stufe: passt sich immer an, fällt aber nie unter die Mindeststufe."""
    return max(min_level(profile, subject), int(profile.skill(skill)["level"]))


def is_auto(profile: Profile, subject: str) -> bool:
    return True


def record(profile: Profile, skill: str, correct: bool, time_ratio=None, timeout=False,
           second_try=False, subject=None) -> tuple:
    """Aktualisiert die Stufe nach Lernerfolg. Rückgabe: (alte Stufe, neue Stufe)."""
    sk = profile.skill(skill)
    floor = min_level(profile, subject or skill.split(".")[0])
    if sk["level"] < floor:
        sk["level"] = float(floor)
    old = int(sk["level"])
    early = sk["seen"] < 8           # Einstufungsphase: schnell zum passenden Niveau
    sk["seen"] += 1
    if correct:
        sk["correct"] += 1
    if correct and not second_try:
        delta = 0.3
        if time_ratio is not None and time_ratio < 0.5:
            delta += 0.15             # schnell und richtig
        if len(sk["hist"]) >= 3 and all(sk["hist"][-3:]):
            delta += 0.2              # Serie → schneller aufsteigen
        if early:
            delta *= 1.8
    elif correct:
        delta = 0.0
    elif timeout:
        delta = -0.2
    else:
        delta = -0.2 if early else -0.35
    sk["hist"] = (sk["hist"] + [1 if (correct and not second_try) else 0])[-20:]
    sk["level"] = max(float(floor), min(MAX_LEVEL, sk["level"] + delta))
    return old, int(sk["level"])


def accuracy(profile: Profile, skill: str):
    h = profile.skill(skill)["hist"]
    return (sum(h) / len(h)) if h else None


# --- Fehlerbox ---------------------------------------------------------------

INTERVALS = {1: 0, 2: 1, 3: 3, 4: 7}  # Box → Tage bis zur nächsten Wiederholung


def _key(task: Task) -> str:
    if task.concept:
        c = {k: v for k, v in task.concept.items() if k not in ("x",)}
        return json.dumps(c, sort_keys=True, ensure_ascii=False)
    return f"{task.prompt}|{task.answer}"


def add_mistake(profile: Profile, task: Task):
    key = _key(task)
    box = profile.data["review"]
    for e in box:
        if e["key"] == key:
            e["box"], e["due"], e["last_type"] = 1, today(), task.type
            return
    entry = {"key": key, "skill": task.skill, "subject": task.subject, "box": 1, "due": today(),
             "added": today(), "last_type": task.type, "label": task.prompt.split("\n")[-1][:60]}
    if task.concept:
        entry["concept"] = task.concept
    else:
        entry["task"] = task.to_dict()
    box.append(entry)
    del box[:-200]


def review_result(profile: Profile, key: str, correct: bool, task_type: str):
    box = profile.data["review"]
    for e in list(box):
        if e["key"] != key:
            continue
        e["last_type"] = task_type
        if correct:
            e["box"] += 1
            if e["box"] > 4:
                box.remove(e)
            else:
                e["due"] = (dt.date.today() + dt.timedelta(days=INTERVALS[e["box"]])).isoformat()
        else:
            e["box"] = 1
            e["due"] = (dt.date.today() + dt.timedelta(days=1)).isoformat()


def due_entries(profile: Profile, subject=None, skill=None) -> list:
    t = today()
    return [e for e in profile.data["review"] if e["due"] <= t
            and (subject in (None, "mix") or e["subject"] == subject) and (skill is None or e["skill"] == skill)]


def task_from_entry(entry: dict):
    from .content import topics
    task = None
    if "concept" in entry:
        task = topics.review(entry["concept"], entry.get("last_type", ""))
    if task is None and "task" in entry:
        task = Task.from_dict(entry["task"])
    if task is None:
        return None
    task.skill = entry["skill"]
    task.subject = entry["subject"]
    return task
