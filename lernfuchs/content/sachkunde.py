"""Generatoren für Heimat- und Sachkunde."""

import random

from ..tasks import Task, choice_task, shuffle, truefalse_task
from .sach_data import FRAGEN, ORDERS, SORTS

C = random.choice
SUBJ = "sach"


def fact_task(f: dict, skill: str, form: str = "choice", n_opts: int = 3) -> Task:
    concept = {"kind": "fact", **f, "skill": skill}
    kw = dict(skill=skill, subject=SUBJ, concept=concept, explain=f.get("x") or f"Richtig ist: {f['r']}",
              visual={"kind": "emoji", "e": f["e"]} if f.get("e") else None, time_factor=1.2)
    if form == "truefalse":
        true = random.random() < 0.5
        shown = f["r"] if true else C(f["w"])
        return truefalse_task(f"{f['q']}\nAntwort: „{shown}“", true, speak=f"{f['q']} Antwort: {shown}. Stimmt das?",
                              **kw)
    wrong = random.sample(f["w"], min(len(f["w"]), n_opts - 1))
    return choice_task(f["q"], f["r"], wrong, **kw)


def review_fact(c: dict, avoid: str) -> Task:
    f = {k: c[k] for k in ("g", "q", "r", "w", "e", "x") if k in c}
    return fact_task(f, c.get("skill", "sach"), form="truefalse" if avoid != "truefalse" else "choice")


def _sort_task(entry, lvl, skill):
    _, _, prompt, buckets, mapping, emos = entry
    n = min(len(mapping), {1: 4, 2: 5, 3: 6, 4: 7, 5: 8}[lvl])
    # aus jeder Kategorie mindestens ein Begriff
    chosen = []
    for b in buckets:
        chosen.append(C([k for k, v in mapping.items() if v == b]))
    rest = [k for k in mapping if k not in chosen]
    chosen += random.sample(rest, max(0, min(len(rest), n - len(chosen))))
    return Task("sort", prompt, answer={k: mapping[k] for k in chosen}, items=shuffle(chosen), buckets=buckets,
                emojis={k: emos.get(k, "") for k in chosen}, skill=skill, subject=SUBJ,
                time_factor=0.6 * len(chosen), explain="Schau dir die richtigen Gruppen noch einmal an.")


def _order_task(entry, skill):
    _, _, prompt, seq, k, emos = entry
    if k and k < len(seq):
        start = random.randint(0, len(seq) - k)
        seq = seq[start:start + k]
    items = shuffle(seq)
    while items == seq:
        items = shuffle(seq)
    return Task("order", prompt, answer=list(seq), items=items, emojis=dict(emos), skill=skill, subject=SUBJ,
                time_factor=0.5 * len(seq) + 0.8, explain=" → ".join(seq))


def make_gen(topic: str):
    skill = f"sach.{topic}"

    def gen(g, lvl):
        facts = [f for f in FRAGEN.get(topic, []) if f["g"] <= g + (1 if lvl >= 5 else 0)] or FRAGEN[topic]
        sorts = [s for s in SORTS if s[0] == topic and s[1] <= g]
        orders = [o for o in ORDERS if o[0] == topic and o[1] <= g]
        r = random.random()
        if sorts and r < 0.12 + 0.03 * lvl:
            return _sort_task(C(sorts), lvl, skill)
        if orders and r > 0.88 - 0.02 * lvl:
            return _order_task(C(orders), skill)
        f = C(facts)
        if lvl >= 3 and random.random() < 0.25:
            return fact_task(f, skill, "truefalse")
        return fact_task(f, skill, "choice", n_opts=3 + (1 if lvl >= 4 and len(f["w"]) > 2 else 0))

    return gen
