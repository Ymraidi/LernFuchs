"""Mathe-Aufgabengeneratoren für Klasse 2–4 mit Stufen 1–5.

Jeder Generator hat die Signatur gen(grade, level) -> Task.
Die Aufgaben werden bei jedem Aufruf neu erzeugt (hohe Variation).
"""

import random

from ..tasks import Task, YES, NO, choice_task, fmt, num_options, shuffle, truefalse_task

R = random.randint
C = random.choice

KIDS = ["Mia", "Leo", "Emma", "Ben", "Lina", "Paul", "Hannah", "Noah", "Lea", "Elias", "Sofia", "Luis", "Ida",
        "Felix"]
NAMES = ["Mia", "Leo", "Emma", "Ben", "Lina", "Paul", "Hannah", "Noah", "Lea", "Elias",
         "Sofia", "Luis", "Ida", "Felix", "Oma", "Opa", "Mama", "Papa"]
FRUITS = ["🍎", "🍐", "🍓", "🍌", "🍊", "🍒", "🥕", "⚽", "🧸", "🚗", "⭐", "🐞"]


def _calc(a, op, b):
    return {"+": a + b, "−": a - b, "×": a * b, ":": a // b}[op]


# --- Grundrechenaufgabe in verschiedenen Formen ------------------------------

def arith_task(a, op, b, skill, form=None, visual=None, time_factor=1.0) -> Task:
    res = _calc(a, op, b)
    concept = {"kind": "arith", "a": a, "op": op, "b": b, "skill": skill}
    form = form or C(["input", "input", "input", "choice", "truefalse", "gap"])
    expl = f"{fmt(a)} {op} {fmt(b)} = {fmt(res)}"
    kw = dict(skill=skill, subject="mathe", concept=concept, explain=expl,
              time_factor=time_factor, visual=visual)
    if form == "choice":
        return Task("choice", f"{fmt(a)} {op} {fmt(b)} = ?", answer=fmt(res),
                    options=num_options(res), **kw)
    if form == "truefalse":
        true = random.random() < 0.5
        shown = res if true else res + C([-10, -2, -1, 1, 2, 10] if res > 10 else [-1, 1, 2])
        if shown < 0:
            shown, true = res, True
        return truefalse_task(f"Stimmt das?\n{fmt(a)} {op} {fmt(b)} = {fmt(shown)}", true, **kw)
    if form == "gap":
        if random.random() < 0.5 or op == ":":
            return Task("input", f"{fmt(a)} {op} ___ = {fmt(res)}", answer=str(b),
                        input_kind="number", **kw)
        return Task("input", f"___ {op} {fmt(b)} = {fmt(res)}", answer=str(a),
                    input_kind="number", **kw)
    if form == "reverse":  # Umkehraufgabe
        inv = {"+": "−", "−": "+", "×": ":", ":": "×"}[op]
        return Task("input", f"Umkehraufgabe:\n{fmt(res)} {inv} {fmt(b)} = ?", answer=str(a),
                    input_kind="number", **kw)
    return Task("input", f"{fmt(a)} {op} {fmt(b)} = ?", answer=str(res), input_kind="number", **kw)


def review_arith(c: dict, avoid: str) -> Task:
    forms = ["input", "choice", "truefalse", "gap", "reverse"]
    forms = [f for f in forms if f != avoid]
    return arith_task(c["a"], c["op"], c["b"], c["skill"], form=C(forms))


# --- Plus & Minus ------------------------------------------------------------

def _plusminus_numbers(g, lvl):
    if g <= 2:
        if lvl == 1:
            a, b = R(2, 15), R(1, 9)
            if random.random() < 0.5:
                return a, "+", min(b, 20 - a)
            a = R(10, 20)
            return a, "−", R(1, a - 1 if a < 10 else 9)
        if lvl == 2:
            if random.random() < 0.4:
                return R(1, 6) * 10, C("+−"), R(1, 3) * 10
            a = R(2, 8) * 10 + R(1, 5)
            return (a, "+", R(1, 9 - a % 10)) if random.random() < 0.5 else (a, "−", R(1, a % 10))
        if lvl == 3:
            a = R(1, 8) * 10 + R(3, 9)
            if random.random() < 0.5:
                return a, "+", R(10 - a % 10, 9)
            a = R(2, 9) * 10 + R(0, 6)
            return a, "−", R(a % 10 + 1, 9)
        a, b = R(15, 69), R(11, 39)
        if random.random() < 0.5:
            return a, "+", min(b, 100 - a)
        a = R(40, 99)
        return a, "−", R(11, a - 5)
    if g == 3:
        if lvl == 1:
            return R(1, 7) * 100, C("+−"), R(1, 2) * 100
        if lvl == 2:
            a = R(12, 80) * 10
            return a, C("+−"), R(1, 9) * 10
        if lvl == 3:
            a = R(120, 850)
            return a, C("+−"), R(12, 99)
        a = R(250, 700)
        return (a, "+", R(111, 999 - a)) if random.random() < 0.5 else (a, "−", R(111, a - 20))
    # Klasse 4
    if lvl == 1:
        return R(1, 8) * 1000, C("+−"), R(1, 3) * 1000
    if lvl == 2:
        return R(12, 90) * 100, C("+−"), R(11, 40) * 100
    if lvl == 3:
        return R(1200, 8900), C("+−"), R(120, 999)
    a = R(20000, 90000)
    return (a, "+", R(1000, 99999 - a)) if random.random() < 0.5 else (a, "−", R(1000, a - 1000))


def gen_plusminus(g, lvl):
    skill = "mathe.plusminus"
    tf = 1.0 + 0.3 * (g - 2)
    if lvl >= 5 and random.random() < 0.5:
        # Kettenaufgabe oder Ergänzen
        if random.random() < 0.5:
            top = {2: 100, 3: 1000, 4: 10000}[g]
            a = R(top // 10, top - top // 10)
            step = {2: 10, 3: 100, 4: 1000}[g]
            target = ((a // step) + 1) * step if random.random() < 0.5 else top
            return Task("input", f"Ergänze bis {fmt(target)}:\n{fmt(a)} + ___ = {fmt(target)}",
                        answer=str(target - a), input_kind="number", skill=skill, subject="mathe",
                        explain=f"{fmt(a)} + {fmt(target - a)} = {fmt(target)}", time_factor=tf,
                        concept={"kind": "arith", "a": a, "op": "+", "b": target - a, "skill": skill})
        a, _, b = _plusminus_numbers(g, 3)
        c = R(2, 9) * (1 if g == 2 else 10)
        res = a + b - c
        if res < 0:
            res, c = a + b, 0
        return Task("input", f"{fmt(a)} + {fmt(b)} − {fmt(c)} = ?", answer=str(res),
                    input_kind="number", skill=skill, subject="mathe", time_factor=tf * 1.3,
                    explain=f"{fmt(a)} + {fmt(b)} = {fmt(a + b)}, dann − {fmt(c)} = {fmt(res)}")
    a, op, b = _plusminus_numbers(g, min(lvl, 4))
    if op == "−" and b > a:
        a, b = b, a
    visual = None
    if g == 2 and lvl == 1 and op == "+" and a + b <= 20 and random.random() < 0.5:
        e1, e2 = random.sample(FRUITS, 2)
        visual = {"kind": "emoji_groups", "groups": [[e1, a], [e2, b]], "sep": "+"}
        return arith_task(a, op, b, skill, form="input", visual=visual)
    form = None if lvl >= 3 else C(["input", "input", "choice", "truefalse"])
    return arith_task(a, op, b, skill, form=form, time_factor=tf)


# --- Mal & Geteilt -----------------------------------------------------------

def gen_einmaleins(g, lvl):
    skill = "mathe.einmaleins"
    if g <= 2:
        rows = {1: [2, 5, 10], 2: [2, 3, 4, 5, 10], 3: list(range(1, 11)),
                4: list(range(2, 11)), 5: list(range(2, 11))}[lvl]
        a, b = C(rows), R(1, 10)
        if random.random() < 0.5:
            a, b = b, a
        if lvl >= 4 and random.random() < 0.45:
            return arith_task(a * b, ":", b if b else 1, skill,
                              form=C(["input", "choice", "gap"]))
        if lvl <= 2 and random.random() < 0.35 and a <= 5 and b <= 8:
            visual = {"kind": "emoji_array", "emoji": C(FRUITS), "rows": a, "cols": b}
            return arith_task(a, "×", b, skill, form="input", visual=visual)
        return arith_task(a, "×", b, skill, form=None if lvl >= 3 else C(["input", "choice", "truefalse"]))
    if g == 3:
        if lvl <= 2:
            a, b = R(2, 10), R(2, 10)
            return arith_task(a * b, ":", b, skill) if lvl == 2 and random.random() < 0.6 \
                else arith_task(a, "×", b, skill)
        if lvl == 3:
            a, b = R(2, 9) * 10, R(2, 9)
            return arith_task(a * b, ":", b, skill) if random.random() < 0.4 else arith_task(a, "×", b, skill)
        if lvl == 4:
            return arith_task(R(12, 49), "×", R(2, 9), skill, time_factor=1.8)
        d = R(3, 9)
        q, r = R(3, 9), R(1, d - 1)
        n = q * d + r
        return Task("input", f"{n} : {d} = ?\n(mit Rest, z. B. 7 R 1)", answer=f"{q} R {r}",
                    accept=[f"{q} Rest {r}"], input_kind="number", skill=skill, subject="mathe",
                    explain=f"{q} × {d} = {q * d}, Rest {r}", time_factor=1.6)
    # Klasse 4
    if lvl == 1:
        return arith_task(R(3, 10), "×", R(3, 10), skill)
    if lvl == 2:
        a, b = R(2, 9) * C([100, 1000]), R(2, 9)
        return arith_task(a * b, ":", b, skill) if random.random() < 0.4 else arith_task(a, "×", b, skill)
    if lvl == 3:
        return arith_task(R(11, 25), "×", R(11, 19), skill, form="input", time_factor=2.5)
    if lvl == 4:
        return arith_task(R(112, 489), "×", R(3, 9), skill, form="input", time_factor=2.5)
    b = R(3, 9)
    return arith_task(R(21, 110) * b, ":", b, skill, form="input", time_factor=2.5)


# --- Verdoppeln & Halbieren --------------------------------------------------

def gen_verdoppeln(g, lvl):
    skill = "mathe.verdoppeln"
    scale = {2: 1, 3: 10, 4: 100}[g]
    limit = {1: 10, 2: 20, 3: 50, 4: 100, 5: 100}[lvl] * scale
    if random.random() < 0.5 or lvl == 1:
        n = R(1, limit // 2)
        if lvl >= 3 and scale == 1:
            n = R(11, limit // 2)
        prompt, ans = f"Verdopple {fmt(n)}.", n * 2
        expl = f"{fmt(n)} + {fmt(n)} = {fmt(ans)}"
    else:
        n = R(2, limit // 2) * 2
        prompt, ans = f"Halbiere {fmt(n)}.", n // 2
        expl = f"{fmt(ans)} + {fmt(ans)} = {fmt(n)}"
    form = C(["input", "input", "choice"])
    kw = dict(skill=skill, subject="mathe", explain=expl,
              concept={"kind": "arith", "a": n if "Verd" in prompt else n, "op": "×" if "Verd" in prompt else ":",
                       "b": 2, "skill": skill})
    if g == 2 and lvl == 1 and random.random() < 0.5:
        e = C(FRUITS)
        return Task("input", f"Verdopple: Wie viele sind es doppelt so viele?", answer=str(n * 2),
                    input_kind="number", visual={"kind": "emoji_groups", "groups": [[e, n], [e, n]],
                                                 "sep": "+"}, **{**kw, "explain": f"{n} + {n} = {2 * n}"})
    if form == "choice":
        return Task("choice", prompt, answer=fmt(ans), options=num_options(ans), **kw)
    return Task("input", prompt, answer=str(ans), input_kind="number", **kw)


# --- Zahlen vergleichen & Zahlenraum ----------------------------------------

def gen_zahlen(g, lvl):
    skill = "mathe.zahlen"
    top = {2: 100, 3: 1000, 4: 1000000}[g]
    kw = dict(skill=skill, subject="mathe")
    kind = C(["vergleich", "nachbar", "stelle", "gerade", "ordnen", "zehner"] if lvl >= 2
             else ["vergleich", "nachbar", "gerade"])
    if kind == "vergleich":
        a = R(1, top - 1)
        b = a + C([-10, -1, 1, 10, 0, R(-20, 20)]) if lvl >= 2 else R(1, top - 1)
        b = max(0, min(top, b))
        if lvl >= 4 and g == 2:
            b1 = R(1, b) if b > 1 else 0
            left = f"{fmt(a)}"
            right = f"{fmt(b1)} + {fmt(b - b1)}"
        else:
            left, right = fmt(a), fmt(b)
        ans = "<" if a < b else (">" if a > b else "=")
        return Task("choice", f"Welches Zeichen passt?\n{left}  ○  {right}", answer=ans,
                    options=["<", "=", ">"], explain=f"{left} {ans} {right}",
                    hint="Das Krokodil frisst immer die größere Zahl!", **kw)
    if kind == "nachbar":
        n = R(2, top - 2)
        if random.random() < 0.5:
            return Task("input", f"Welche Zahl kommt direkt nach {fmt(n)}?", answer=str(n + 1),
                        input_kind="number", explain=f"Nach {fmt(n)} kommt {fmt(n + 1)}.", **kw)
        return Task("input", f"Welche Zahl kommt direkt vor {fmt(n)}?", answer=str(n - 1),
                    input_kind="number", explain=f"Vor {fmt(n)} kommt {fmt(n - 1)}.", **kw)
    if kind == "zehner":
        step = 10 if g == 2 else (100 if g == 3 else 1000)
        n = R(step + 1, top - step - 1)
        if n % step == 0:
            n += R(1, step - 1)
        lo = n // step * step
        ans = f"{fmt(lo)} und {fmt(lo + step)}"
        wrong = [f"{fmt(lo - step)} und {fmt(lo)}", f"{fmt(lo + step)} und {fmt(lo + 2 * step)}"]
        name = {10: "Zehnern", 100: "Hundertern", 1000: "Tausendern"}[step]
        return choice_task(f"Zwischen welchen {name} liegt {fmt(n)}?", ans, wrong, **kw)
    if kind == "stelle":
        if g == 2:
            z, e = R(1, 9), R(0, 9)
            if random.random() < 0.5:
                return Task("input", f"{z} Zehner und {e} Einer.\nWelche Zahl ist das?",
                            answer=str(z * 10 + e), input_kind="number",
                            explain=f"{z}Z {e}E = {z * 10 + e}", **kw)
            n = z * 10 + e
            what = C(["Zehner", "Einer"])
            return Task("input", f"Wie viele {what} hat die Zahl {n}?",
                        answer=str(z if what == "Zehner" else e), input_kind="number",
                        explain=f"{n} = {z} Zehner und {e} Einer", **kw)
        if g == 3:
            h, z, e = R(1, 9), R(0, 9), R(0, 9)
            return Task("input", f"{h} Hunderter, {z} Zehner und {e} Einer.\nWelche Zahl ist das?",
                        answer=str(h * 100 + z * 10 + e), input_kind="number",
                        explain=f"{h}H {z}Z {e}E = {h * 100 + z * 10 + e}", **kw)
        t, h = R(1, 99), R(0, 9)
        return Task("input", f"{t} Tausender und {h} Hunderter.\nWelche Zahl ist das?",
                    answer=str(t * 1000 + h * 100), input_kind="number",
                    explain=f"= {fmt(t * 1000 + h * 100)}", **kw)
    if kind == "gerade":
        n = R(1, top if g < 4 else 1000)
        ans = "gerade" if n % 2 == 0 else "ungerade"
        return Task("choice", f"Ist {fmt(n)} gerade oder ungerade?", answer=ans,
                    options=["gerade", "ungerade"],
                    explain=f"Schau auf die letzte Ziffer: {str(n)[-1]}.", **kw)
    nums = random.sample(range(1, top), 4 if lvl < 4 else 5)
    asc = random.random() < 0.6
    ordered = sorted(nums, reverse=not asc)
    return Task("order", "Ordne die Zahlen – " + ("die kleinste zuerst!" if asc else "die größte zuerst!"),
                answer=[fmt(n) for n in ordered], items=shuffle([fmt(n) for n in nums]),
                explain=" , ".join(fmt(n) for n in ordered), time_factor=1.5, **kw)


# --- Zahlenfolgen & Muster ---------------------------------------------------

PATTERN_SETS = [["🔴", "🔵"], ["🟡", "🟢", "🔴"], ["⭐", "🌙"], ["🍎", "🍐", "🍐"],
                ["🐶", "🐱", "🐭"], ["🔺", "🟦", "🟦", "🔺"]]


def gen_folgen(g, lvl):
    skill = "mathe.folgen"
    kw = dict(skill=skill, subject="mathe", time_factor=1.4)
    if lvl == 1 and random.random() < 0.5:
        base = C(PATTERN_SETS)
        n = len(base) * 2 + R(0, len(base) - 1)
        seq = [base[i % len(base)] for i in range(n + 1)]
        ans = seq[-1]
        pool = sorted({e for s in PATTERN_SETS for e in s} - {ans})
        opts = list({ans, *[e for e in base if e != ans]} | set(random.sample(pool, 2)))[:3]
        if ans not in opts:
            opts[0] = ans
        return Task("choice", "Welches Bild kommt als Nächstes?", answer=ans, options=shuffle(opts),
                    visual={"kind": "pattern", "seq": seq[:-1] + ["?"]}, **kw)
    mult = {2: 1, 3: 10, 4: 100}[g]
    if lvl <= 2:
        step = C([1, 2, 10, 5] if lvl == 1 else [2, 3, 5, 10, -2, -10])
        seq = [R(0, 30) * mult + (50 * mult if step < 0 else 0)]
        rule = f"immer {'+' if step > 0 else '−'}{abs(step) * mult}"
        for _ in range(5):
            seq.append(seq[-1] + step * mult)
    elif lvl <= 4:
        if random.random() < 0.5:
            step = C([3, 4, 6, 7, 9, 11, -3, -4, -5])
            seq = [R(10, 40) * mult + (60 * mult if step < 0 else 0)]
            for _ in range(5):
                seq.append(seq[-1] + step * mult)
            rule = f"immer {'+' if step > 0 else '−'}{abs(step) * mult}"
        else:
            s1, s2 = C([(2, 3), (5, -2), (10, -1), (3, 1), (4, -2)])
            seq = [R(1, 20) * mult + 10 * mult]
            for i in range(5):
                seq.append(seq[-1] + (s1 if i % 2 == 0 else s2) * mult)
            rule = f"abwechselnd {s1 * mult:+} und {s2 * mult:+}"
    else:
        if random.random() < 0.5:
            seq = [R(1, 5)]
            for _ in range(5):
                seq.append(seq[-1] * 2)
            rule = "immer verdoppeln (×2)"
        else:
            seq = [R(1, 10)]
            for i in range(5):
                seq.append(seq[-1] + i + 1)
            rule = "+1, +2, +3, +4, …"
    pos = len(seq) - 1 if lvl < 3 or random.random() < 0.6 else R(1, len(seq) - 2)
    shown = [fmt(x) if i != pos else "___" for i, x in enumerate(seq)]
    return Task("input", "Setze die Zahlenfolge fort:\n" + ",  ".join(shown), answer=str(seq[pos]),
                input_kind="number", explain=f"Regel: {rule}", **kw)


# --- Zahlenmauern ------------------------------------------------------------

def gen_zahlenmauer(g, lvl):
    skill = "mathe.zahlenmauer"
    base_n = 3 if (g == 2 and lvl <= 3) else 4
    top_lim = {2: 100, 3: 1000, 4: 10000}[g]
    hi = max(4, top_lim // (4 if base_n == 3 else 8))
    base = [R(1, hi // (2 if lvl < 3 else 1)) for _ in range(base_n)]
    if g >= 3 and lvl <= 2:
        base = [R(1, hi // 10) * 10 for _ in range(base_n)]
    rows = [base]
    while len(rows[-1]) > 1:
        r = rows[-1]
        rows.append([r[i] + r[i + 1] for i in range(len(r) - 1)])
    # Welche Zelle ist versteckt?
    if lvl in (1, 4):
        ri, ci = len(rows) - 1, 0
    elif lvl == 2:
        ri, ci = 1, R(0, len(rows[1]) - 1)
    else:
        ri, ci = 0, R(0, base_n - 1)
    ans = rows[ri][ci]
    shown = [[(v if not (i == ri and j == ci) else None) for j, v in enumerate(row)]
             for i, row in enumerate(rows)]
    if ri == 0:
        # Für versteckte Basiszellen muss die Zelle darüber sichtbar sein, die anderen bleiben sichtbar.
        pass
    return Task("input", "Zahlenmauer: Zwei Steine nebeneinander ergeben zusammen den Stein darüber.\n"
                         "Welche Zahl gehört in den leeren Stein?",
                answer=str(ans), input_kind="number", skill=skill, subject="mathe",
                visual={"kind": "wall", "rows": shown}, time_factor=1.8,
                explain="Plus nach oben, Minus nach unten!")


# --- Geld & Einkaufen --------------------------------------------------------

COINS = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000]  # in Cent
SHOP = [("🍦", "ein Eis", 150), ("🥨", "eine Breze", 90), ("📘", "ein Heft", 120),
        ("✏️", "einen Stift", 80), ("🧃", "einen Saft", 110), ("🍫", "eine Schokolade", 130),
        ("⚽", "einen Ball", 900), ("🧸", "einen Teddy", 1200), ("📚", "ein Buch", 800),
        ("🍎", "einen Apfel", 50), ("🍌", "eine Banane", 40), ("🥛", "eine Milch", 120),
        ("🎨", "Farbstifte", 600), ("🪁", "einen Drachen", 1500), ("🧩", "ein Puzzle", 1100)]


def euro(ct: int) -> str:
    if ct % 100 == 0:
        return f"{ct // 100} €"
    if ct < 100:
        return f"{ct} ct"
    return f"{ct // 100},{ct % 100:02d} €"


def gen_geld(g, lvl):
    skill = "mathe.geld"
    kw = dict(skill=skill, subject="mathe", time_factor=1.6)
    if lvl == 1 or (lvl == 2 and random.random() < 0.5):
        pool = [1, 2, 5, 10, 20, 50] if lvl == 1 else [10, 20, 50, 100, 200, 500, 1000]
        coins = sorted([C(pool) for _ in range(R(3, 5))], reverse=True)
        total = sum(coins)
        if total < 100:
            return Task("input", "Wie viel Geld ist das?", answer=str(total), unit="ct",
                        input_kind="number", visual={"kind": "coins", "values": coins},
                        explain=" + ".join(euro(c) for c in coins) + f" = {euro(total)}", **kw)
        if total % 100 == 0:
            return Task("input", "Wie viel Geld ist das?", answer=str(total // 100), unit="€",
                        input_kind="number", visual={"kind": "coins", "values": coins},
                        explain=f"Zusammen {euro(total)}", **kw)
        return Task("input", "Wie viel Geld ist das? (in Cent)", answer=str(total), unit="ct",
                    input_kind="number", visual={"kind": "coins", "values": coins},
                    explain=f"Zusammen {euro(total)} = {total} ct", **kw)
    if lvl in (2, 3):
        items = random.sample(SHOP, 2)
        if g == 2:
            items = [(e, n, max(1, p // 100) * 100) for e, n, p in items]
        total = sum(p for _, _, p in items)
        name = C(NAMES)
        txt = f"{name} kauft {items[0][1]} ({euro(items[0][2])}) und {items[1][1]} ({euro(items[1][2])}).\n" \
              f"Wie viel kostet das zusammen?"
        vis = {"kind": "emoji_groups", "groups": [[items[0][0], 1], [items[1][0], 1]], "sep": "+"}
        if total % 100 == 0:
            return Task("input", txt, answer=str(total // 100), unit="€", input_kind="number",
                        visual=vis, explain=f"{euro(items[0][2])} + {euro(items[1][2])} = {euro(total)}", **kw)
        return Task("input", txt, answer=f"{total / 100:.2f}".replace(".", ","), unit="€",
                    accept=[str(total / 100)], input_kind="number", visual=vis,
                    explain=f"{euro(items[0][2])} + {euro(items[1][2])} = {euro(total)}", **kw)
    # Rückgeld
    e, n, p = C(SHOP)
    if g == 2:
        p = max(1, p // 100) * 100
    pay = next(x for x in [500, 1000, 2000, 5000] if x > p)
    back = pay - p
    txt = f"Du kaufst {n} für {euro(p)} und bezahlst mit {euro(pay)}.\nWie viel Rückgeld bekommst du?"
    if back % 100 == 0:
        return Task("input", txt, answer=str(back // 100), unit="€", input_kind="number",
                    visual={"kind": "emoji", "e": e},
                    explain=f"{euro(pay)} − {euro(p)} = {euro(back)}", **kw)
    return Task("input", txt, answer=f"{back / 100:.2f}".replace(".", ","), unit="€",
                accept=[str(back / 100)], input_kind="number", visual={"kind": "emoji", "e": e},
                explain=f"{euro(pay)} − {euro(p)} = {euro(back)}", **kw)


# --- Uhrzeit -----------------------------------------------------------------

def say_time(h, m):
    nh = h % 12 + 1
    h12 = h % 12 or 12
    return {0: f"{h12} Uhr", 5: f"5 nach {h12}", 10: f"10 nach {h12}", 15: f"Viertel nach {h12}",
            20: f"20 nach {h12}", 25: f"5 vor halb {nh}", 30: f"halb {nh}", 35: f"5 nach halb {nh}",
            40: f"20 vor {nh}", 45: f"Viertel vor {nh}", 50: f"10 vor {nh}", 55: f"5 vor {nh}"}.get(m, f"{h12}:{m:02d} Uhr")


def digital(h, m):
    return f"{h}:{m:02d} Uhr"


# (Aktivität, frühester Beginn, spätester Beginn, typische Dauer in Minuten)
ACTIVITIES = [("Der Film", 15, 18, [45, 60, 90]), ("Das Fußballtraining", 15, 17, [45, 60, 90]),
              ("Der Schwimmkurs", 14, 16, [30, 45, 60]), ("Die Geburtstagsfeier", 14, 15, [90, 120, 150]),
              ("Die Hausaufgaben", 13, 16, [15, 20, 30, 45]), ("Die große Pause", 9, 10, [15, 20, 30]),
              ("Das Abendessen", 18, 19, [15, 20, 30]), ("Der Ausflug in den Zoo", 9, 10, [120, 180, 240]),
              ("Die Musikstunde", 15, 17, [30, 45, 60])]


def gen_uhr(g, lvl):
    skill = "mathe.uhr"
    kw = dict(skill=skill, subject="mathe", time_factor=1.5)
    if lvl >= 5 or (g >= 3 and lvl >= 3 and random.random() < 0.5):
        what, h0, h1, durs = C(ACTIVITIES)
        h, m = R(h0, h1), C([0, 15, 30, 45])
        dur = C(durs if g >= 3 else [d for d in durs if d in (15, 30, 45, 60, 90, 120)] or durs)
        eh, em = divmod(h * 60 + m + dur, 60)
        return choice_task(f"{what} beginnt um {digital(h, m)} und dauert {dur} Minuten.\nWann ist es zu Ende?",
                           digital(eh, em), [digital(eh, (em + 15) % 60), digital(eh + 1, em), digital(eh - 1, em),
                                             digital(eh, (em + 30) % 60), digital(h, m)],
                           explain=f"{digital(h, m)} + {dur} min = {digital(eh, em)}", **kw)
    if lvl >= 4 and random.random() < 0.3:
        q = C([("Wie viele Minuten hat eine Stunde?", "60"), ("Wie viele Minuten sind eine halbe Stunde?", "30"),
               ("Wie viele Minuten sind eine Viertelstunde?", "15"), ("Wie viele Stunden hat ein Tag?", "24"),
               ("Wie viele Sekunden hat eine Minute?", "60"), ("Wie viele Minuten sind eine Dreiviertelstunde?", "45")])
        return Task("input", q[0], answer=q[1], input_kind="number", **kw)
    mins = {1: [0], 2: [0, 30], 3: [0, 15, 30, 45], 4: list(range(0, 60, 5))}[min(lvl, 4)]
    h, m = R(1, 12), C(mins)
    colloquial = lvl >= 2 and random.random() < 0.5
    fmt_t = say_time if colloquial else (lambda hh, mm: digital(hh, mm))
    wrong = set()
    while len(wrong) < 3:
        wh, wm = C([(h % 12 + 1, m), (h, C(mins)), ((h + 10) % 12 + 1, m), (h, (m + 30) % 60),
                    (m // 5 or 12, (h * 5) % 60)])
        if (wh, wm) != (h, m) and wm in range(0, 60, 5):
            wrong.add(fmt_t(wh, wm))
    wrong.discard(fmt_t(h, m))
    return choice_task("Wie spät ist es?", fmt_t(h, m), list(wrong)[:3],
                       visual={"kind": "clock", "h": h, "m": m},
                       explain=f"Es ist {say_time(h, m)} ({digital(h, m)}).",
                       hint="Der kurze Zeiger zeigt die Stunden, der lange die Minuten.", **kw)


# --- Größen: Längen, Gewichte, Volumen ---------------------------------------

ESTIMATES = {
    2: [("Wie lang ist ein Bleistift?", "15 cm", ["15 m", "1 cm"], "✏️"),
        ("Wie hoch ist eine Tür?", "2 m", ["2 cm", "20 m"], "🚪"),
        ("Wie lang ist ein Fußballfeld?", "100 m", ["100 cm", "10 cm"], "⚽"),
        ("Wie groß ist ein Kind in der 2. Klasse?", "125 cm", ["125 m", "12 cm"], "🧒"),
        ("Wie lang ist ein Auto?", "4 m", ["4 cm", "40 m"], "🚗"),
        ("Wie breit ist ein Heft?", "21 cm", ["21 m", "2 cm"], "📘"),
        ("Wie lang ist ein Marienkäfer?", "1 cm", ["1 m", "10 cm"], "🐞"),
        ("Wie hoch ist ein Tisch?", "75 cm", ["75 m", "7 cm"], "🪑"),
        ("Wie lang ist ein Schulbus?", "12 m", ["12 cm", "120 m"], "🚌"),
        ("Wie lang ist eine Banane?", "20 cm", ["2 m", "2 cm"], "🍌")],
    3: [("Wie schwer ist eine Tafel Schokolade?", "100 g", ["100 kg", "1 g"], "🍫"),
        ("Wie schwer ist ein Kind der 3. Klasse?", "30 kg", ["30 g", "300 kg"], "🧒"),
        ("Wie schwer ist ein Apfel?", "150 g", ["150 kg", "15 kg"], "🍎"),
        ("Wie weit ist ein Schulweg zu Fuß meistens?", "1 km", ["1 cm", "100 km"], "🚶"),
        ("Wie schwer ist eine Tüte Mehl?", "1 kg", ["1 g", "10 kg"], "🥖"),
        ("Wie hoch ist ein Kirchturm?", "60 m", ["60 cm", "6 km"], "⛪"),
        ("Wie schwer ist ein Fahrrad?", "12 kg", ["12 g", "120 kg"], "🚲")],
    4: [("Wie viel passt in einen Eimer?", "10 l", ["10 ml", "100 l"], "🪣"),
        ("Wie viel passt in einen Teelöffel?", "5 ml", ["5 l", "50 l"], "🥄"),
        ("Wie schwer ist ein Elefant?", "5 t", ["5 kg", "50 g"], "🐘"),
        ("Wie viel Wasser passt in eine Badewanne?", "150 l", ["150 ml", "15 ml"], "🛁"),
        ("Wie viel ist in einem Glas Saft?", "200 ml", ["200 l", "2 ml"], "🧃"),
        ("Wie weit ist es von München nach Hamburg?", "800 km", ["800 m", "8 km"], "🗺️")],
}

CONVERT = {
    2: [("m", "cm", 100)],
    3: [("m", "cm", 100), ("kg", "g", 1000), ("km", "m", 1000)],
    4: [("m", "cm", 100), ("kg", "g", 1000), ("km", "m", 1000), ("l", "ml", 1000), ("t", "kg", 1000)],
}


def gen_groessen(g, lvl):
    skill = "mathe.groessen"
    kw = dict(skill=skill, subject="mathe", time_factor=1.4)
    kind = C(["lineal", "schaetzen"] if lvl <= 2 and g == 2 else ["schaetzen", "umrechnen", "lineal"])
    if kind == "lineal":
        cm = R(2, 12) if lvl <= 2 else R(2, 12) + C([0, 0.5])
        return Task("input", "Wie lang ist der Stift? Miss mit dem Lineal!", answer=fmt(cm), unit="cm",
                    input_kind="number", visual={"kind": "ruler", "length": cm},
                    explain=f"Der Stift ist {fmt(cm)} cm lang.", **kw)
    if kind == "schaetzen":
        pool = [q for gg in range(2, g + 1) for q in ESTIMATES[gg]]
        q, right, wrong, e = C(pool)
        return choice_task(q, right, wrong, visual={"kind": "emoji", "e": e}, **kw)
    big, small, factor = C(CONVERT[g])
    if lvl <= 3:
        n = R(1, 9)
        return Task("input", f"{n} {big} = ___ {small}", answer=str(n * factor), unit=small,
                    input_kind="number", explain=f"1 {big} = {factor} {small}", **kw)
    n, rest = R(1, 9), R(1, factor - 1) if factor == 100 else R(1, 9) * 100 + R(0, 99)
    return Task("input", f"{n} {big} {rest} {small} = ___ {small}", answer=str(n * factor + rest), unit=small,
                input_kind="number", explain=f"{n} {big} = {n * factor} {small}, plus {rest} {small}", **kw)


# --- Rechengeschichten (Sachaufgaben aus dem Alltag) -------------------------

def _story(g, lvl):
    # Zahlen bleiben realistisch (kein Buch mit 8800 Seiten); große Zahlen kommen über eigene Geschichten
    k = 1 if g == 2 else (5 if lvl < 3 else 10)
    n1, n2 = C(KIDS), C(KIDS)
    stories = []

    a, b = R(12, 45) * k, R(5, 30) * k
    stories.append((f"{n1} hat {a} Murmeln. Beim Spielen gewinnt {n1} noch {b} dazu.\n"
                    f"Wie viele Murmeln sind es jetzt?", a + b, "Murmeln", f"{a} + {b} = {a + b}", "🔵"))
    a, o, e = R(25, 45), R(3, 12), R(2, 9)
    stories.append((f"Im Schulbus sitzen {a} Kinder. An der Haltestelle steigen {o} Kinder aus "
                    f"und {e} steigen ein.\nWie viele Kinder sitzen jetzt im Bus?",
                    a - o + e, "Kinder", f"{a} − {o} + {e} = {a - o + e}", "🚌"))
    kids, each = R(3, 8), R(2, 5)
    stories.append((f"Zum Geburtstag von {n1} kommen {kids} Kinder. Jedes Kind bekommt {each} Muffins.\n"
                    f"Wie viele Muffins braucht man?", kids * each, "Muffins",
                    f"{kids} × {each} = {kids * each}", "🧁"))
    teams = R(2, 4)
    stories.append((f"Eine Fußballmannschaft hat 11 Spieler. Beim Turnier spielen {teams} Mannschaften.\n"
                    f"Wie viele Spieler sind das zusammen?", 11 * teams, "Spieler",
                    f"{teams} × 11 = {11 * teams}", "⚽"))
    money, price = R(10, 20) * max(1, k // 10 or 1), R(3, 9)
    stories.append((f"Du hast {money} € Taschengeld gespart. Du kaufst ein Buch für {price} €.\n"
                    f"Wie viel Geld hast du noch?", money - price, "€", f"{money} − {price} = {money - price}", "💶"))
    boxes = R(2, 8)
    stories.append((f"In einen Eierkarton passen 6 Eier. {n1} kauft {boxes} Kartons.\nWie viele Eier sind das?",
                    6 * boxes, "Eier", f"{boxes} × 6 = {6 * boxes}", "🥚"))
    kids, each = R(2, 6), R(2, 8)
    stories.append((f"{kids * each} Gummibärchen werden gerecht an {kids} Kinder verteilt.\n"
                    f"Wie viele bekommt jedes Kind?", each, "Gummibärchen",
                    f"{kids * each} : {kids} = {each}", "🍬"))
    pages, read = R(40, 90) * k, R(10, 35) * k
    stories.append((f"Ein Buch hat {pages} Seiten. {n1} hat schon {read} Seiten gelesen.\n"
                    f"Wie viele Seiten fehlen noch?", pages - read, "Seiten", f"{pages} − {read} = {pages - read}", "📖"))
    bikes = R(3, 12)
    stories.append((f"Vor der Schule stehen {bikes} Fahrräder.\nWie viele Räder sind das zusammen?",
                    bikes * 2, "Räder", f"{bikes} × 2 = {bikes * 2}", "🚲"))
    tables = R(3, 9)
    stories.append((f"Im Klassenzimmer stehen {tables} Tische. Jeder Tisch hat 4 Beine.\n"
                    f"Wie viele Tischbeine sind das?", tables * 4, "Tischbeine", f"{tables} × 4 = {tables * 4}", "🪑"))
    boys, girls = R(8, 14), R(8, 14)
    stories.append((f"In der Klasse von {C(KIDS)} sind {boys} Jungen und {girls} Mädchen.\n"
                    f"Wie viele Kinder sind in der Klasse?", boys + girls, "Kinder",
                    f"{boys} + {girls} = {boys + girls}", "🏫"))
    pieces, kids = 8, R(2, 4)
    stories.append((f"Eine Pizza hat 8 Stücke. {kids} Kinder essen jeweils 2 Stücke.\n"
                    f"Wie viele Stücke bleiben übrig?", pieces - 2 * kids, "Stücke",
                    f"{kids} × 2 = {2 * kids}, 8 − {2 * kids} = {8 - 2 * kids}", "🍕"))
    a, b = R(15, 40) * k, R(10, 30) * k
    stories.append((f"{n1} sammelt im Herbst {a} Kastanien, {n2} sammelt {b}.\n"
                    f"Wie viele Kastanien haben beide zusammen?", a + b, "Kastanien", f"{a} + {b} = {a + b}", "🌰"))
    pause, gone = C([15, 20, 30]), R(5, 12)
    stories.append((f"Die große Pause dauert {pause} Minuten. {gone} Minuten sind schon vorbei.\n"
                    f"Wie viele Minuten darfst du noch spielen?", pause - gone, "Minuten",
                    f"{pause} − {gone} = {pause - gone}", "⏰"))
    packs, per = R(2, 6), C([5, 10, 4])
    price = R(2, 4)
    stories.append((f"Ein Päckchen Sticker kostet {price} €. {n1} kauft {packs} Päckchen.\n"
                    f"Wie viel muss {n1} bezahlen?", price * packs, "€", f"{packs} × {price} = {price * packs}", "🏷️"))
    stairs, done = R(20, 60), R(5, 18)
    stories.append((f"Die Treppe zum Turm hat {stairs} Stufen. Du bist schon {done} Stufen gestiegen.\n"
                    f"Wie viele Stufen hast du noch vor dir?", stairs - done, "Stufen",
                    f"{stairs} − {done} = {stairs - done}", "🗼"))
    weeks = R(2, 6)
    stories.append((f"Eine Woche hat 7 Tage. Die Ferien dauern {weeks} Wochen.\nWie viele Tage sind das?",
                    7 * weeks, "Tage", f"{weeks} × 7 = {7 * weeks}", "🏖️"))
    if g >= 3:
        a, b = R(120, 480), R(80, 390)
        stories.append((f"In der Bücherei stehen {a} Kinderbücher und {b} Sachbücher.\n"
                        f"Wie viele Bücher sind das zusammen?", a + b, "Bücher", f"{a} + {b} = {a + b}", "📚"))
        tot, out = R(350, 900), R(40, 300)
        stories.append((f"Im Zug sitzen {tot} Fahrgäste. Am Bahnhof steigen {out} aus.\n"
                        f"Wie viele Fahrgäste bleiben im Zug?", tot - out, "Fahrgäste", f"{tot} − {out} = {tot - out}", "🚆"))
    if g >= 4:
        a, b = R(12000, 40000), R(5000, 25000)
        stories.append((f"Beim Fußballspiel sitzen {fmt(a)} Fans auf der Haupttribüne und {fmt(b)} in der Kurve.\n"
                        f"Wie viele Fans sind im Stadion?", a + b, "Fans", f"{fmt(a)} + {fmt(b)} = {fmt(a + b)}", "🏟️"))
        km = R(420, 980)
        stories.append((f"Familie Maier fährt in den Urlaub: {km} km hin und {km} km zurück.\n"
                        f"Wie viele Kilometer fahren sie insgesamt?", 2 * km, "km", f"{km} × 2 = {2 * km}", "🚗"))
    if g >= 3:
        pp, cnt = R(12, 45), R(3, 8)
        stories.append((f"Eine Klasse fährt ins Museum. Der Eintritt kostet {pp} € pro Gruppe. "
                        f"Es fahren {cnt} Gruppen.\nWie viel kostet der Eintritt zusammen?", pp * cnt, "€",
                        f"{cnt} × {pp} = {pp * cnt}", "🏛️"))
        km = R(3, 9)
        stories.append((f"Papa fährt jeden Tag {km} km zur Arbeit und {km} km zurück.\n"
                        f"Wie viele km sind das in 5 Arbeitstagen?", km * 2 * 5, "km",
                        f"{km} + {km} = {2 * km}, {2 * km} × 5 = {10 * km}", "🚗"))
    return C(stories)


def gen_sachaufgaben(g, lvl):
    text, ans, unit, expl, e = _story(g, lvl)
    return Task("input", text, answer=str(ans), unit=unit, input_kind="number",
                skill="mathe.sachaufgaben", subject="mathe", visual={"kind": "emoji", "e": e},
                explain="Rechnung: " + expl, time_factor=2.2 + 0.2 * (g - 2),
                hint="Lies genau: Was weißt du? Was ist gefragt?")


# --- Formen & Geometrie ------------------------------------------------------

SHAPES = {"Kreis": 0, "Dreieck": 3, "Quadrat": 4, "Rechteck": 4, "Fünfeck": 5, "Sechseck": 6}


def gen_formen(g, lvl):
    skill = "mathe.formen"
    kw = dict(skill=skill, subject="mathe", time_factor=1.3)
    kind = C(["name", "ecken", "zaehlen"] + (["umfang", "flaeche"] if g >= 3 else []))
    if lvl == 1:
        kind = C(["name", "ecken"])
    if kind == "name":
        pool = ["Kreis", "Dreieck", "Quadrat", "Rechteck"] + (["Fünfeck", "Sechseck"] if lvl >= 3 else [])
        s = C(pool)
        return choice_task("Wie heißt diese Form?", s, random.sample([p for p in pool if p != s], 3),
                           visual={"kind": "shape", "name": s}, **kw)
    if kind == "ecken":
        s = C([k for k in SHAPES if k != "Kreis"])
        return Task("input", f"Wie viele Ecken hat ein {s}?", answer=str(SHAPES[s]), input_kind="number",
                    visual={"kind": "shape", "name": s}, explain=f"Ein {s} hat {SHAPES[s]} Ecken.", **kw)
    if kind == "zaehlen":
        n_total = 6 + lvl * 2
        target = C(["Kreis", "Dreieck", "Quadrat"])
        lst = [C(["Kreis", "Dreieck", "Quadrat", "Rechteck"]) for _ in range(n_total)]
        cnt = lst.count(target)
        plural = {"Kreis": "Kreise", "Dreieck": "Dreiecke", "Quadrat": "Quadrate"}[target]
        return Task("input", f"Zähle genau: Wie viele {plural} siehst du?", answer=str(cnt), input_kind="number",
                    visual={"kind": "shapes", "list": lst}, explain=f"Es sind {cnt} {plural}.",
                    **{**kw, "time_factor": 1.8})
    w, h = R(2, 9), R(2, 6)
    if kind == "umfang":
        return Task("input", f"Ein Rechteck ist {w} cm lang und {h} cm breit.\nWie groß ist der Umfang?",
                    answer=str(2 * (w + h)), unit="cm", input_kind="number",
                    visual={"kind": "rect", "w": w, "h": h, "mode": "umfang"},
                    explain=f"{w} + {h} + {w} + {h} = {2 * (w + h)} cm", **kw)
    return Task("input", "Wie viele Kästchen (cm²) ist das Rechteck groß?", answer=str(w * h), unit="cm²",
                input_kind="number", visual={"kind": "rect", "w": w, "h": h, "mode": "flaeche"},
                explain=f"{w} × {h} = {w * h} Kästchen", **kw)


# --- Schriftliches Rechnen (ab Klasse 3) ------------------------------------

def gen_schriftlich(g, lvl):
    skill = "mathe.schriftlich"
    if g == 4 and lvl >= 3 and random.random() < 0.5:
        a, b = R(123, 999 if lvl < 5 else 4999), R(3, 9)
        op, res = "×", a * b
    else:
        digits = 3 if g == 3 else 4
        lo, hi = 10 ** (digits - 1), 10 ** digits - 1
        a = R(lo * 2, hi)
        if random.random() < 0.5:
            b = R(lo, hi - a) if hi - a > lo else R(10, 99)
            op, res = "+", a + b
        else:
            b = R(lo // 2, a - 1)
            op, res = "−", a - b
    width = max(len(str(a)), len(str(b)), len(str(res))) + 2
    lines = [str(a).rjust(width), (op + " " + str(b).rjust(width - 2)).rjust(width)]
    return Task("input", "Rechne schriftlich:", answer=str(res), input_kind="number", skill=skill,
                subject="mathe", visual={"kind": "column", "lines": lines}, time_factor=3.0,
                explain=f"{a} {op} {b} = {res}",
                concept={"kind": "arith", "a": a, "op": op, "b": b, "skill": skill})
