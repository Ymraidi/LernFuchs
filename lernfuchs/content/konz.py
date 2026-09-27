"""Aufgabenbasierte Konzentrationsübungen (die Spiele liegen in ui/games.py)."""

import random

from ..tasks import Task, choice_task, shuffle

C = random.choice
SUBJ = "konz"

LOOKALIKES = [["🐞", "🐜", "🕷️"], ["🍎", "🍅", "🍒"], ["🐶", "🐱", "🦊"], ["⭐", "🌟", "✨"],
              ["🚗", "🚕", "🚙"], ["🔴", "🟠", "🟤"], ["🐸", "🐢", "🦎"], ["🌷", "🌹", "🌺"],
              ["⚽", "🏀", "🥎"], ["🐟", "🐠", "🐡"]]


def gen_zaehlen(g, lvl):
    group = C(LOOKALIKES)
    target = group[0] if random.random() < 0.5 else C(group)
    total = 10 + lvl * 4 + (g - 2) * 3
    kinds = group[:2] if lvl <= 2 else group
    items = [C(kinds) for _ in range(total)]
    cnt = items.count(target)
    if cnt == 0:
        items[random.randrange(total)] = target
        cnt = 1
    return Task("input", f"Zähle ganz genau: Wie viele {target} siehst du?", answer=str(cnt), input_kind="number",
                visual={"kind": "emoji_grid", "items": items, "cols": 8 if total > 24 else 6},
                skill="konz.zaehlen", subject=SUBJ, explain=(f"Es sind {cnt}." if cnt != 1 else "Es ist nur einer."), time_factor=1.2 + total / 20,
                hint="Tipp: Zeile für Zeile zählen und mit dem Finger mitgehen!")


FX_TEXT = {"patch": "Ein kleiner Teil des Fotos ist verändert.", "mirror": "Es ist gespiegelt.", "color": "Es hat andere Farben.", "rotate": "Es steht auf dem Kopf.",
           "zoom": "Es ist näher herangezoomt.", "hue": "Die Farben sind leicht verschoben.", "dark": "Es ist dunkler."}


def gen_anders(g, lvl):
    from .. import photos
    path = photos.random_photo()
    if path:
        try:
            n = {1: 9, 2: 9, 3: 12, 4: 16, 5: 16}[lvl]
            crop, fx, patch = photos.odd_tile_spec(path, lvl)
            items = [{"photo": path, "crop": list(crop), "fx": None} for _ in range(n)]
            idx = random.randrange(n)
            items[idx]["fx"] = fx
            items[idx]["patch"] = patch
            return Task("grid_click", "Ein Foto ist anders als alle anderen. Finde es!", answer=idx, items=items,
                        skill="konz.anders", subject=SUBJ, explain=FX_TEXT.get(fx, ""), time_factor=0.9 + lvl * 0.15)
        except Exception:
            pass
    group = C(LOOKALIKES)
    base, odd = random.sample(group, 2)
    n = {1: 9, 2: 12, 3: 16, 4: 20, 5: 25}[lvl]
    items = [base] * n
    idx = random.randrange(n)
    items[idx] = odd
    return Task("grid_click", "Finde das Bild, das anders ist!", answer=idx, items=items,
                skill="konz.anders", subject=SUBJ, explain="Schau genau hin – Reihe für Reihe.", time_factor=0.8)


def gen_merken(g, lvl):
    pool = shuffle(["🍎", "🚗", "🐶", "⚽", "🌈", "🎈", "🐟", "🌙", "🍌", "✏️", "🎁", "🦋", "🚀", "🍕", "🔑", "🐢"])
    n = min(3 + lvl + (g - 2), 9)
    shown = pool[:n]
    secs = max(3, 7 - lvl // 2) + n // 3
    kind = C(["dabei", "fehlt"] if lvl <= 2 else ["dabei", "fehlt", "position"])
    if kind == "dabei":
        ans = C(shown)
        wrong = random.sample(pool[n:], 2)
        t = choice_task("Welches Bild war dabei?", ans, wrong)
    elif kind == "fehlt":
        ans = C(pool[n:])
        t = choice_task("Welches Bild war NICHT dabei?", ans, random.sample(shown, 2))
    else:
        pos = random.randrange(n)
        ans = shown[pos]
        wrong = random.sample([s for s in shown if s != ans], 2)
        t = choice_task(f"Welches Bild war an Platz {pos + 1}?", ans, wrong)
    t.visual = {"kind": "flash", "items": shown, "seconds": secs}
    t.skill, t.subject, t.time_factor = "konz.merken", SUBJ, 1.0
    t.speak = "Merke dir die Bilder!"
    t.explain = "Die Bilder waren: " + " ".join(shown)
    return t


def gen_rechenkette(g, lvl):
    steps = 2 + lvl + (1 if g >= 3 else 0)
    hi = {2: 10, 3: 20, 4: 50}[g]
    val = random.randint(2, hi)
    parts = [f"Starte mit {val}."]
    for _ in range(steps):
        if random.random() < 0.5 or val < 3:
            n = random.randint(1, min(hi, 9 + lvl))
            val += n
            parts.append(f"plus {n}")
        else:
            n = random.randint(1, min(val - 1, 9 + lvl))
            val -= n
            parts.append(f"minus {n}")
    text = parts[0] + " " + ", ".join(parts[1:]) + "."
    rechnung = str(int(parts[0].split()[-1].rstrip("."))) + " " + " ".join(
        ("+ " if p.startswith("plus") else "− ") + p.split()[-1] for p in parts[1:])
    return Task("input", "Hör gut zu und rechne im Kopf mit!\nWelche Zahl kommt heraus?", answer=str(val),
                input_kind="number", listen=True, listen_text=text, speak=text,
                visual={"kind": "listen", "title": "Rechenkette"}, skill="konz.rechenkette", subject=SUBJ,
                explain=f"{rechnung} = {val}", time_factor=1.2 + steps * 0.15)
