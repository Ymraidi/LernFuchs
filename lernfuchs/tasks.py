"""Aufgaben-Datenmodell, Antwortprüfung und Hilfsfunktionen für Generatoren."""

from __future__ import annotations

import random
import re
from dataclasses import dataclass, field, asdict

YES, NO = "Stimmt", "Stimmt nicht"
# Hier zählt Groß-/Kleinschreibung (Rechtschreib-Training); sonst wird sie ignoriert.
STRICT_CASE = {"deutsch.diktat", "deutsch.rechtschreibung", "deutsch.artikel", "deutsch.verben", "deutsch.puzzle",
               "deutsch.fokus"}


@dataclass
class Task:
    # choice | input | truefalse | order | sort
    type: str
    prompt: str
    answer: object = ""
    options: list = field(default_factory=list)
    skill: str = ""
    subject: str = ""
    visual: dict | None = None
    speak: str | None = None        # Vorlesetext (None = Aufgabentext)
    listen: bool = False            # Höraufgabe: Text wird nur vorgelesen
    listen_text: str = ""
    input_kind: str = "text"        # number | text
    unit: str = ""
    explain: str = ""
    time_factor: float = 1.0
    concept: dict | None = None     # Grundlage für Wiederholung in anderer Form
    accept: list = field(default_factory=list)
    items: list = field(default_factory=list)      # order/sort
    buckets: list = field(default_factory=list)    # sort
    emojis: dict = field(default_factory=dict)     # Emoji je Option/Item
    hint: str = ""

    def to_dict(self) -> dict:
        return asdict(self)

    @staticmethod
    def from_dict(d: dict) -> "Task":
        return Task(**{k: v for k, v in d.items() if k in Task.__dataclass_fields__})


# --- Antwortprüfung ----------------------------------------------------------

def _num(s: str):
    s = s.strip().replace(" ", "").replace("€", "").replace("ct", "")
    s = s.replace(".", "") if re.fullmatch(r"\d{1,3}(\.\d{3})+", s) else s
    s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _norm_text(s: str) -> str:
    s = s.strip().replace("’", "'")
    s = re.sub(r"\s+", " ", s)
    return s


def _norm_rest(s: str) -> str:
    s = s.lower().replace(" ", "").replace("rest", "r")
    return s


def check(task: Task, given) -> bool:
    if task.type in ("choice", "truefalse"):
        return given == task.answer
    if task.type == "order":
        return list(given) == list(task.answer)
    if task.type in ("sort", "grid_click"):
        return given == task.answer
    # input
    answers = [str(task.answer)] + [str(a) for a in task.accept]
    g = str(given)
    if task.input_kind == "number":
        if "R" in str(task.answer):
            return any(_norm_rest(g) == _norm_rest(a) for a in answers)
        gv = _num(g)
        if gv is None:
            return False
        return any(_num(a) is not None and abs(_num(a) - gv) < 1e-6 for a in answers)
    if task.skill in STRICT_CASE:
        return any(_norm_text(g) == _norm_text(a) for a in answers)
    return any(_norm_text(g).casefold().rstrip(".!") == _norm_text(a).casefold().rstrip(".!") for a in answers)


# --- Hilfen für Generatoren --------------------------------------------------

def shuffle(lst: list) -> list:
    lst = list(lst)
    random.shuffle(lst)
    return lst


def fmt(n) -> str:
    """Zahl deutsch formatiert (Tausenderpunkt ab 10 000)."""
    if isinstance(n, float) and not n.is_integer():
        return f"{n:.2f}".rstrip("0").replace(".", ",")
    n = int(n)
    return f"{n:,}".replace(",", ".") if abs(n) >= 10000 else str(n)


def num_options(ans: int, k: int = 4, lo: int = 0) -> list:
    """Plausible Ablenker rund um das Ergebnis."""
    cand = set()
    steps = [1, -1, 2, -2, 10, -10]
    if ans >= 100:
        steps += [100, -100, 20, -20]
    if ans >= 10000:
        steps += [1000, -1000]
    random.shuffle(steps)
    for s in steps:
        v = ans + s
        if v >= lo and v != ans:
            cand.add(v)
        if len(cand) >= k + 2:
            break
    s = str(ans)
    if len(s) >= 2 and s[-1] != s[-2]:
        sw = int(s[:-2] + s[-1] + s[-2])
        if sw != ans and sw >= lo:
            cand.add(sw)
    opts = random.sample(sorted(cand), min(k - 1, len(cand)))
    return shuffle([fmt(o) for o in opts] + [fmt(ans)])


def choice_task(prompt, answer, wrong, max_wrong: int = 3, **kw) -> Task:
    wrong = [w for w in dict.fromkeys(wrong) if w != answer][:max_wrong]
    opts = shuffle([answer] + wrong)
    return Task("choice", prompt, answer=answer, options=opts, **kw)


def truefalse_task(statement: str, true: bool, **kw) -> Task:
    return Task("truefalse", statement, answer=YES if true else NO, options=[YES, NO], **kw)
