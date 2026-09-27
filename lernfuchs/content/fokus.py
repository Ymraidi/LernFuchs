"""Konzentrationsaufgaben in allen Fächern: kurz zeigen – merken – antworten, genau hinsehen, suchen."""

import random

from ..tasks import Task, choice_task, fmt, num_options, shuffle
from .deutsch_data import DIKTAT_SAETZE, NOMEN, TEXTE
from .sach_data import FRAGEN

C = random.choice
R = random.randint


def _flash_secs(lvl, base=2.4):
    return round(max(0.7, base - 0.35 * (lvl - 1)), 1)


# ================================ DEUTSCH =====================================

def _wortblitz(g, lvl):
    lo, hi = {1: (3, 5), 2: (4, 6), 3: (5, 8), 4: (6, 10), 5: (8, 14)}[lvl]
    n = C([x for x in NOMEN if lo <= len(x["w"]) <= hi] or NOMEN)
    return Task("input", "Wort-Blitz! Das Wort erscheint nur ganz kurz. Schreibe es danach richtig auf.",
                answer=n["w"], visual={"kind": "flash_text", "items": [n["w"]], "seconds": _flash_secs(lvl, 2.0)},
                explain=f"Das Wort war: {n['w']}", time_factor=1.2, hint="Nomen schreibt man groß!")


def _woerter_merken(g, lvl):
    k = min(3 + lvl, 8)
    pool = random.sample([x["w"] for x in NOMEN if len(x["w"]) <= 9], k + 3)
    shown, rest = pool[:k], pool[k:]
    if random.random() < 0.5:
        return choice_task("Welches Wort war NICHT dabei?", C(rest), random.sample(shown, 2),
                           visual={"kind": "flash_text", "items": shown, "seconds": 1.2 + k * 0.7, "list": True},
                           explain="Die Wörter waren: " + ", ".join(shown))
    return choice_task("Welches Wort war dabei?", C(shown), random.sample(rest, 2),
                       visual={"kind": "flash_text", "items": shown, "seconds": 1.2 + k * 0.7, "list": True},
                       explain="Die Wörter waren: " + ", ".join(shown))


def _buchstaben_zaehlen(g, lvl):
    if lvl <= 2:
        sent = C([s for s, gg, _ in DIKTAT_SAETZE if len(s) < 35])
    else:
        text = C(TEXTE)[3]
        sents = [s.strip() + "." for s in text.split(".") if 30 < len(s) < 90]
        sent = C(sents or [text[:80]])
    letter = C([ch for ch in "eanrtsil" if sent.lower().count(ch) >= 2] or ["e"])
    cnt = sent.lower().count(letter)
    return Task("input", f"Zähle ganz genau: Wie oft kommt der Buchstabe „{letter}“ vor?\n(groß und klein zählen)",
                answer=str(cnt), input_kind="number", visual={"kind": "code_line", "text": sent},
                explain=f"„{letter}“ kommt {cnt}-mal vor.", time_factor=1.3 + len(sent) / 60,
                hint="Tipp: Gehe mit dem Finger Buchstabe für Buchstabe mit.")


def _fehler_im_satz(g, lvl):
    from .deutsch import misspellings
    sent = C([s for s, gg, _ in DIKTAT_SAETZE if gg <= g + 1])
    words = sent.rstrip(".!?").split()
    cand = [i for i, w in enumerate(words) if len(w) >= 4]
    i = C(cand)
    wrong = misspellings(words[i], 1)
    if not wrong:
        return _wortblitz(g, lvl)
    words[i] = wrong[0]
    opts = list(dict.fromkeys(words))
    return Task("choice", "Fehler-Detektiv: In diesem Satz ist ein Wort falsch geschrieben. Welches?",
                answer=words[i], options=opts, explain=f"Richtig heißt es: {sent}", time_factor=1.4)


def _doppelt(g, lvl):
    pool = [s for s, _, _ in DIKTAT_SAETZE
            if len({w.lower() for w in s.rstrip(".!?").split()}) == len(s.rstrip(".!?").split())]
    sent = C(pool).rstrip(".!?").split()
    i = R(1, len(sent) - 1)
    words = sent[:i] + [sent[i - 1]] + sent[i:] if lvl <= 2 else sent[:]
    if lvl > 2:  # schwerer: das doppelte Wort steht woanders
        dup = C(sent)
        pos = R(0, len(sent))
        words = sent[:pos] + [dup] + sent[pos:]
        target = dup
    else:
        target = sent[i - 1]
    shown = " ".join(words) + "."
    return choice_task("Genau lesen: Welches Wort steht doppelt im Satz?\n" + shown, target,
                       random.sample([w for w in sent if w != target], min(2, len(sent) - 1)),
                       explain=f"„{target}“ steht zweimal da.", time_factor=1.2)


def gen_fokus_deutsch(g, lvl):
    return C([_wortblitz, _wortblitz, _woerter_merken, _buchstaben_zaehlen, _fehler_im_satz, _doppelt])(g, lvl)


# ================================= MATHE ======================================

def _blitzrechnen(g, lvl):
    from .mathe import _plusminus_numbers
    a, op, b = _plusminus_numbers(g, min(4, lvl))
    if op == "−" and b > a:
        a, b = b, a
    if lvl >= 3 and random.random() < 0.4:
        a, b, op = R(2, 9), R(2, 9), "×"
    res = {"+": a + b, "−": a - b, "×": a * b}[op]
    expr = f"{fmt(a)} {op} {fmt(b)}"
    return Task("input", "Blitzrechnen! Die Aufgabe ist gleich wieder weg – merke sie dir und rechne im Kopf.",
                answer=str(res), input_kind="number",
                visual={"kind": "flash_text", "items": [expr], "seconds": _flash_secs(lvl, 2.6)},
                explain=f"{expr} = {fmt(res)}", time_factor=1.2)


def _zahlen_kette(g, lvl):
    n = 2 + lvl
    hi = {2: 9, 3: 20, 4: 50}[g]
    nums = [R(1, hi) for _ in range(n)]
    return Task("input", "Zahlen-Kette: Die Zahlen erscheinen nacheinander. Addiere sie alle im Kopf!",
                answer=str(sum(nums)), input_kind="number",
                visual={"kind": "flash_text", "items": [str(x) for x in nums], "seconds": _flash_secs(lvl, 1.5),
                        "seq": True},
                explain=" + ".join(map(str, nums)) + f" = {sum(nums)}", time_factor=1.2)


def _fehlende_zahl(g, lvl):
    size = {1: 3, 2: 4, 3: 4, 4: 5, 5: 5}[lvl]
    start = {2: 1, 3: R(1, 50), 4: R(1, 500)}[g]
    nums = list(range(start, start + size * size))
    missing = C(nums)
    grid_nums = [x for x in nums if x != missing] + [None]
    random.shuffle(grid_nums)
    rows = [grid_nums[i * size:(i + 1) * size] for i in range(size)]
    return Task("input", f"Welche Zahl von {start} bis {start + size * size - 1} fehlt im Gitter?",
                answer=str(missing), input_kind="number", visual={"kind": "numgrid", "rows": rows, "box": 0},
                explain=f"Es fehlt die {missing}.", time_factor=1.2 + size * 0.25)


def _alle_finden(g, lvl):
    k = C([2, 5, 10] if lvl <= 2 else [3, 4, 6, 7, 8, 9])
    n = {1: 12, 2: 16, 3: 16, 4: 20, 5: 20}[lvl]
    top = k * 10 if k >= 5 else k * 15
    targets = random.sample(range(k, top + 1, k), R(3, 5))
    others = random.sample([x for x in range(1, top + 1) if x % k], n - len(targets))
    items = shuffle([str(x) for x in targets + others])
    ans = sorted(i for i, x in enumerate(items) if int(x) % k == 0)
    return Task("multi_click", f"Tippe ALLE Zahlen aus der {k}er-Reihe an – und keine andere!", answer=ans,
                items=items, explain="Richtig: " + ", ".join(items[i] for i in ans), time_factor=1.5)


def _groesstes(g, lvl):
    from .mathe import _plusminus_numbers
    exprs = []
    while len(exprs) < 3:
        a, op, b = _plusminus_numbers(g, min(4, lvl))
        if op == "−" and b > a:
            a, b = b, a
        v = a + b if op == "+" else a - b
        if v not in [e[1] for e in exprs]:
            exprs.append((f"{fmt(a)} {op} {fmt(b)}", v))
    best = max(exprs, key=lambda e: e[1])
    return choice_task("Schnell überlegen: Welche Rechnung hat das GRÖSSTE Ergebnis?", best[0],
                       [e[0] for e in exprs if e != best],
                       explain=", ".join(f"{e} = {fmt(v)}" for e, v in exprs), time_factor=1.3)


def gen_fokus_mathe(g, lvl):
    pool = [_blitzrechnen, _blitzrechnen, _zahlen_kette, _fehlende_zahl, _alle_finden, _groesstes]
    return C(pool)(g, lvl)


# =============================== SACHKUNDE ====================================

def _foto_kim(g, lvl):
    from .. import photos
    pics = photos.random_photos(min(4 + lvl, 9))
    if len(pics) < 4:
        return _merk_fakt(g, lvl)
    items = []
    for path, title in pics:
        from PIL import Image
        w, h = Image.open(path).size
        side = min(w, h)
        items.append({"photo": path, "crop": [(w - side) // 2, (h - side) // 2, (w + side) // 2, (h + side) // 2],
                      "fx": None, "label": title})
    idx = random.randrange(len(items))
    return Task("grid_click", f"Merk dir, wo welches Foto liegt! Gleich werden sie umgedreht.\n"
                              f"Wo lag das Foto „{items[idx]['label']}“?", answer=idx, items=items,
                visual={"kind": "flash_grid", "seconds": max(3, 8 - lvl)},
                explain=f"Das Foto „{items[idx]['label']}“ lag an Platz {idx + 1}.", time_factor=1.0)


def _foto_fehlt(g, lvl):
    from .. import photos
    pics = photos.random_photos(min(3 + lvl, 8) + 2)
    if len(pics) < 5:
        return _merk_fakt(g, lvl)
    shown, rest = pics[:-2], pics[-2:]
    items = [{"photo": p, "label": t} for p, t in shown]
    miss = rest[0][1]
    return choice_task("Welches Foto war NICHT dabei?", miss, random.sample([t for _, t in shown], 2),
                       visual={"kind": "flash_photos", "items": items, "seconds": max(3, 3 + len(items) * 0.8 - lvl * 0.3)},
                       explain="Gezeigt wurden: " + ", ".join(t for _, t in shown))


def _merk_fakt(g, lvl):
    f = C([x for x in FRAGEN["forscher"] + FRAGEN["tiere"] if x["g"] <= g + 1])
    text = f"{f['q']}\n→ {f['r']}"
    return choice_task(f["q"], f["r"], random.sample(f["w"], min(2, len(f["w"]))),
                       visual={"kind": "flash_text", "items": [text], "seconds": max(3.5, 7 - lvl * 0.6),
                               "small": True},
                       explain=f.get("x") or f"Richtig: {f['r']}", time_factor=1.0)


def _tiere_merken(g, lvl):
    tiere = [n["w"] for n in NOMEN if n["cat"] == "Tiere"]
    k = min(3 + lvl, 8)
    pool = random.sample(tiere, k + 2)
    shown = pool[:k]
    order = random.random() < 0.4 and lvl >= 3
    if order:
        pos = R(0, k - 1)
        return choice_task(f"Welches Tier stand an Platz {pos + 1}?", shown[pos],
                           random.sample([t for t in shown if t != shown[pos]], 2),
                           visual={"kind": "flash_text", "items": shown, "seconds": 1.5 + k * 0.8, "list": True},
                           explain="Reihenfolge: " + ", ".join(shown))
    return choice_task("Welches Tier war NICHT dabei?", pool[k], random.sample(shown, 2),
                       visual={"kind": "flash_text", "items": shown, "seconds": 1.5 + k * 0.7, "list": True},
                       explain="Gezeigt wurden: " + ", ".join(shown))


def gen_fokus_sach(g, lvl):
    return C([_foto_kim, _foto_kim, _foto_fehlt, _merk_fakt, _tiere_merken])(g, lvl)
