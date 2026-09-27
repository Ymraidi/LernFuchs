"""Sonder- und Knobelaufgaben für schlaue Köpfe: Logik, Rätsel, Geheimschrift, Sudoku, magische Quadrate."""

import itertools
import random

from ..tasks import Task, choice_task, shuffle
from .deutsch_data import NOMEN

C = random.choice
R = random.randint
SYMBOLS = ["🍎", "🍌", "🍓", "⭐", "🚀", "⚽", "🎸", "🐙", "💎", "🍩", "🦊", "🌵"]
WEEK = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]


def _scale(g):
    return {2: 1, 3: 3, 4: 10}.get(g, 1)


# =============================== MATHE: KNOBELN ===============================

def _symbol_riddle(g, lvl):
    a_s, b_s, c_s = random.sample(SYMBOLS, 3)
    k = _scale(g)
    a, b, c = R(2, 9) * k, R(2, 9) * k, R(1, 9) * k
    if lvl <= 2:
        lines = [[a_s, "+", a_s, "=", str(2 * a)], [a_s, "+", b_s, "=", str(a + b)], [b_s, "=", "?"]]
        ans, expl = b, f"{a_s} = {a}, also {b_s} = {a + b} − {a} = {b}"
    elif lvl <= 4:
        lines = [[a_s, "+", a_s, "+", a_s, "=", str(3 * a)], [a_s, "+", b_s, "=", str(a + b)],
                 [b_s, "+", c_s, "=", str(b + c)], [c_s, "=", "?"]]
        ans, expl = c, f"{a_s} = {a}, {b_s} = {b}, {c_s} = {c}"
    else:
        a = R(2, 9)
        lines = [[a_s, "×", a_s, "=", str(a * a)], [a_s, "+", b_s, "=", str(a + b)],
                 [a_s, "+", b_s, "×", c_s, "=", "?"]]
        c = R(2, 5)
        lines.insert(2, [c_s, "+", c_s, "=", str(2 * c)])
        ans = a + b * c
        expl = f"{a_s} = {a}, {b_s} = {b}, {c_s} = {c}. Punkt vor Strich: {a} + {b} × {c} = {ans}"
    return Task("input", "Symbol-Rätsel: Jedes Bild steht für eine Zahl. Welche Zahl gehört zum Fragezeichen?",
                answer=str(ans), input_kind="number", visual={"kind": "equations", "lines": lines},
                explain=expl, time_factor=2.2)


def _think_number(g, lvl):
    x = R(2, 12) * _scale(g)
    k = R(2, 9) * _scale(g)
    if lvl >= 5 and k % 2:
        k += 1  # sonst geht das Halbieren nicht auf
    steps = [("addiere", k)] if lvl <= 1 else [("verdopple", None)] if lvl == 2 else \
        [("addiere", k), ("verdopple", None)] if lvl == 3 else \
        [("verdreifache", None), ("subtrahiere", k)] if lvl == 4 else \
        [("verdopple", None), ("addiere", k), ("halbiere", None)]
    v, parts = x, []
    for op, n in steps:
        if op == "addiere":
            v += n
            parts.append(f"{n} dazuzähle")
        elif op == "subtrahiere":
            v -= n
            parts.append(f"{n} abziehe")
        elif op == "verdopple":
            v *= 2
            parts.append("sie verdopple" if not parts else "das Ergebnis verdopple")
        elif op == "verdreifache":
            v *= 3
            parts.append("sie mit 3 malnehme" if not parts else "das Ergebnis mit 3 malnehme")
        elif op == "halbiere":
            v //= 2
            parts.append("sie halbiere" if not parts else "das Ergebnis halbiere")
    text = "Ich denke mir eine Zahl. Wenn ich " + " und dann ".join(parts) + f", erhalte ich {v}.\nWelche Zahl habe ich mir gedacht?"
    return Task("input", text, answer=str(x), input_kind="number", explain=f"Rückwärts rechnen! Die Zahl war {x}.",
                hint="Tipp: Rechne rückwärts – vom Ergebnis aus mit den Umkehraufgaben.", time_factor=2.4)


LO_SHU = [[2, 7, 6], [9, 5, 1], [4, 3, 8]]


def _magic_square(g, lvl):
    sq = [row[:] for row in LO_SHU]
    for _ in range(R(0, 3)):
        sq = [list(r) for r in zip(*sq[::-1])]
    if random.random() < 0.5:
        sq = [r[::-1] for r in sq]
    add = R(0, 5) * _scale(g)
    mul = 1 if lvl <= 3 else C([1, 2])
    sq = [[v * mul + add for v in r] for r in sq]
    total = sum(sq[0])
    ar, ac = R(0, 2), R(0, 2)
    ans = sq[ar][ac]
    shown = [[v for v in r] for r in sq]
    shown[ar][ac] = "?"
    if lvl >= 4:  # weitere Felder leer – aber nie in der Zeile des Fragezeichens
        others = [(r, c) for r in range(3) for c in range(3) if r != ar and (r, c) != (ar, ac)]
        for r, c in random.sample(others, 2):
            shown[r][c] = None
    return Task("input", f"Magisches Quadrat: Jede Zeile, jede Spalte und beide Diagonalen ergeben {total}.\n"
                         "Welche Zahl gehört ins Feld mit dem Fragezeichen?", answer=str(ans), input_kind="number",
                visual={"kind": "numgrid", "rows": shown, "box": 0}, time_factor=2.2,
                explain=f"In der Zeile fehlt: {total} − (die beiden anderen Zahlen) = {ans}")


def _sudoku_solutions(grid, limit=50):
    cells = [(r, c) for r in range(4) for c in range(4) if grid[r][c] is None]
    sols = []

    def ok(g, r, c, v):
        if v in g[r] or v in (g[i][c] for i in range(4)):
            return False
        br, bc = r // 2 * 2, c // 2 * 2
        return all(g[i][j] != v for i in range(br, br + 2) for j in range(bc, bc + 2))

    def rec(i):
        if len(sols) >= limit:
            return
        if i == len(cells):
            sols.append([row[:] for row in grid])
            return
        r, c = cells[i]
        for v in range(1, 5):
            if ok(grid, r, c, v):
                grid[r][c] = v
                rec(i + 1)
                grid[r][c] = None
    rec(0)
    return sols


def _sudoku(g, lvl):
    base = [[1, 2, 3, 4], [3, 4, 1, 2], [2, 1, 4, 3], [4, 3, 2, 1]]
    perm = shuffle([1, 2, 3, 4])
    sol = [[perm[v - 1] for v in row] for row in base]
    if random.random() < 0.5:
        sol = [list(r) for r in zip(*sol)]
    if random.random() < 0.5:
        sol = [sol[1], sol[0], sol[3], sol[2]] if random.random() < 0.5 else [sol[2], sol[3], sol[0], sol[1]]
    blanks = {1: 3, 2: 5, 3: 7, 4: 9, 5: 10}[lvl]
    ar, ac = R(0, 3), R(0, 3)
    for _ in range(40):
        grid = [row[:] for row in sol]
        cells = [(r, c) for r in range(4) for c in range(4) if (r, c) != (ar, ac)]
        for r, c in random.sample(cells, blanks - 1):
            grid[r][c] = None
        grid[ar][ac] = None
        sols = _sudoku_solutions([row[:] for row in grid])
        if sols and all(s[ar][ac] == sol[ar][ac] for s in sols):
            break
    else:
        grid = [row[:] for row in sol]
        grid[ar][ac] = None
    shown = [[("?" if (r, c) == (ar, ac) else grid[r][c]) for c in range(4)] for r in range(4)]
    return Task("input", "Mini-Sudoku: In jeder Zeile, jeder Spalte und jedem 2×2-Kasten kommen 1, 2, 3 und 4 genau "
                         "einmal vor.\nWelche Zahl gehört ins Fragezeichen-Feld?", answer=str(sol[ar][ac]),
                input_kind="number", visual={"kind": "numgrid", "rows": shown, "box": 2}, time_factor=2.6,
                explain=f"Die Lösung ist {sol[ar][ac]} – prüfe Zeile, Spalte und Kasten.")


def _odd_one(g, lvl):
    n = C([2, 3, 4, 5, 10] if lvl <= 2 else [3, 4, 6, 7, 8, 9])
    start = R(1, 5)
    nums = [n * (start + i) for i in range(5)]
    idx = R(0, 4)
    odd = nums[idx] + C([1, -1, 2]) if n > 2 else nums[idx] + 1
    nums[idx] = odd
    return choice_task("Welche Zahl passt nicht in die Reihe?\n" + ",  ".join(map(str, nums)), str(odd),
                       [str(x) for x in nums if x != odd][:3],
                       explain=f"Alle anderen sind Vielfache von {n} (Einmaleins der {n}).", time_factor=1.8)


def _week(g, lvl):
    start = R(0, 6)
    days = R(2, 6) if lvl <= 2 else R(8, 20) if lvl <= 4 else R(21, 100)
    ans = WEEK[(start + days) % 7]
    wrong = random.sample([d for d in WEEK if d != ans], 3)
    if days < 7:
        expl = "Zähle weiter: " + ", ".join(WEEK[(start + i) % 7] for i in range(1, days + 1)) + "."
    else:
        expl = (f"Alle 7 Tage ist wieder {WEEK[start]}. {days} = {days // 7} × 7 + {days % 7}, "
                f"also noch {days % 7} Tag{'e' if days % 7 != 1 else ''} weiter.")
    return choice_task(f"Heute ist {WEEK[start]}. Welcher Wochentag ist in {days} Tagen?", ans, wrong,
                       explain=expl,
                       hint="Tipp: Nach 7 Tagen ist wieder derselbe Wochentag.", time_factor=1.8)


def _combinatorics(g, lvl):
    if lvl <= 4 or random.random() < 0.5:
        a, b = R(2, 4), R(2, 4)
        return Task("input", f"Du hast {a} verschiedene T-Shirts und {b} verschiedene Hosen.\n"
                             "Wie viele verschiedene Outfits kannst du anziehen?", answer=str(a * b),
                    input_kind="number", explain=f"Zu jedem T-Shirt passen {b} Hosen: {a} × {b} = {a * b}",
                    time_factor=2.0)
    n = R(3, 6)
    return Task("input", f"{n} Kinder begrüßen sich. Jedes Kind gibt jedem anderen genau einmal die Hand.\n"
                         "Wie viele Handschläge sind das?", answer=str(n * (n - 1) // 2), input_kind="number",
                explain=" + ".join(str(i) for i in range(n - 1, 0, -1)) + f" = {n * (n - 1) // 2}",
                hint="Tipp: Das erste Kind gibt allen anderen die Hand, das zweite nur noch den übrigen …",
                time_factor=2.4)


def _ages(g, lvl):
    d, young = R(2, 6), R(3, 9)
    old = young + d
    return Task("input", f"Tom ist {d} Jahre älter als seine Schwester Lea. Zusammen sind sie {young + old} Jahre alt.\n"
                         "Wie alt ist Lea?", answer=str(young), input_kind="number",
                explain=f"({young + old} − {d}) : 2 = {young}. Probe: {young} + {old} = {young + old}",
                hint="Tipp: Nimm den Unterschied weg – dann sind beide gleich alt.", time_factor=2.4)


def _balance(g, lvl):
    a, b, c = random.sample(["🍎", "🍍", "🍋", "🍉", "🥥"], 3)
    x, y = R(2, 3), R(2, 4)
    lines = [[a, "wiegt so viel wie"] + [b] * x, [b, "wiegt so viel wie"] + [c] * y, [a, "wiegt so viel wie", "?"] + [c]]
    return Task("input", "Waage-Rätsel: Wie viele Früchte der letzten Sorte wiegen so viel wie eine der ersten Sorte?",
                answer=str(x * y), input_kind="number", visual={"kind": "equations", "lines": lines},
                explain=f"{x} × {y} = {x * y}", time_factor=2.4)


TRICKS = [
    ("Ein Bauer hat 7 Schafe. Alle bis auf 3 laufen weg. Wie viele Schafe bleiben?", "3", ["4", "7"],
     "„Alle bis auf 3“ heißt: 3 bleiben da."),
    ("Was ist schwerer: 1 kg Federn oder 1 kg Steine?", "Beides gleich schwer", ["Die Steine", "Die Federn"],
     "1 kg ist 1 kg!"),
    ("Welcher Monat hat 28 Tage?", "Alle Monate", ["Nur der Februar", "Keiner"], "Jeder Monat hat mindestens 28 Tage."),
    ("Du überholst beim Rennen die Person auf Platz 2. Auf welchem Platz bist du jetzt?", "Platz 2",
     ["Platz 1", "Platz 3"], "Du nimmst ihren Platz ein – also Platz 2."),
    ("Wie oft kann man 5 von 25 abziehen?", "Einmal – danach sind es ja 20", ["Fünfmal", "Zehnmal"],
     "Nach dem ersten Mal ziehst du von 20 ab, nicht mehr von 25."),
    ("Eine Seerose verdoppelt jeden Tag ihre Fläche. Nach 10 Tagen ist der Teich voll. Wann war er halb voll?",
     "Am 9. Tag", ["Am 5. Tag", "Am 8. Tag"], "Am nächsten Tag verdoppelt sie sich – also einen Tag vorher."),
    ("Ein Ziegelstein wiegt 1 kg plus einen halben Ziegelstein. Wie schwer ist ein Ziegelstein?", "2 kg",
     ["1,5 kg", "1 kg"], "Der halbe Stein wiegt 1 kg – also wiegt der ganze 2 kg."),
    ("Mias Mutter hat drei Kinder: Tick, Trick und …?", "Mia", ["Track", "Tom"], "Mia ist selbst das dritte Kind!"),
]


def gen_knobeln(g, lvl):
    pool = [_symbol_riddle, _think_number, _odd_one, _week]
    if lvl >= 2:
        pool += [_magic_square, _sudoku]
    if lvl >= 3:
        pool += [_combinatorics, _ages, _balance, _sudoku]
    if lvl >= 2 and random.random() < 0.15:
        q, r, w, x = C(TRICKS)
        return choice_task("Trickfrage! " + q, r, w, explain=x, time_factor=1.6)
    return C(pool)(g, lvl)


# ========================== DEUTSCH: RÄTSEL & CODES ===========================

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def _plain_nouns(minlen, maxlen):
    return [n for n in NOMEN if minlen <= len(n["w"]) <= maxlen and not any(ch in n["w"] for ch in "ÄÖÜäöüß")]


def _case_variants(w):
    return [w, w.upper(), w.lower(), w.capitalize()]


def _caesar(g, lvl):
    shift = {1: 1, 2: 1, 3: 2, 4: 3, 5: C([3, 4, 5])}[lvl]
    n = C(_plain_nouns(3, 5 + lvl))
    w = n["w"].upper()
    code = "".join(ABC[(ABC.index(ch) + shift) % 26] for ch in w)
    return Task("input", f"Geheimschrift! Jeder Buchstabe wurde im ABC um {shift} nach hinten verschoben "
                         f"(A → {ABC[shift]}).\nEntschlüssle das Wort:", answer=n["w"], accept=_case_variants(n["w"]),
                visual={"kind": "code", "text": code, "shift": shift, "table": lvl <= 3},
                explain=f"{code} → {w}", hint="Gehe für jeden Buchstaben im ABC zurück.", time_factor=2.6)


def _anagram(g, lvl):
    lo, hi = {1: (4, 5), 2: (5, 6), 3: (6, 8), 4: (7, 10), 5: (9, 14)}[lvl]
    pool = [n for n in NOMEN if lo <= len(n["w"]) <= hi] or NOMEN
    n = C(pool)
    letters = list(n["w"].upper())
    mixed = letters[:]
    while mixed == letters:
        random.shuffle(mixed)
    vis = {"kind": "code", "text": "".join(mixed), "shift": 0, "table": False}
    t = Task("input", "Buchstabensalat: Welches Wort steckt darin?", answer=n["w"], accept=_case_variants(n["w"]),
             visual=vis, explain=f"Das Wort heißt {n['w']}.", time_factor=2.2,
             hint=f"Es ist {n['art']} … und gehört zu „{n['cat']}“.")
    return t


WORTKETTEN = [  # (vorne, Lösung, hinten, Wort 1, Wort 2)
    ("Haus", "Tür", "Schlüssel", "Haustür", "Türschlüssel"), ("Fuß", "Ball", "Spiel", "Fußball", "Ballspiel"),
    ("Sonnen", "Blume", "Topf", "Sonnenblume", "Blumentopf"), ("Apfel", "Baum", "Haus", "Apfelbaum", "Baumhaus"),
    ("Schul", "Tasche", "Lampe", "Schultasche", "Taschenlampe"), ("Regen", "Schirm", "Mütze", "Regenschirm", "Schirmmütze"),
    ("Hand", "Schuh", "Karton", "Handschuh", "Schuhkarton"), ("Kinder", "Garten", "Zaun", "Kindergarten", "Gartenzaun"),
    ("Wasser", "Glas", "Flasche", "Wasserglas", "Glasflasche"), ("Tisch", "Tennis", "Ball", "Tischtennis", "Tennisball"),
    ("Butter", "Brot", "Dose", "Butterbrot", "Brotdose"), ("Nacht", "Tisch", "Decke", "Nachttisch", "Tischdecke"),
    ("Post", "Karte", "Spiel", "Postkarte", "Kartenspiel"), ("Kopf", "Kissen", "Schlacht", "Kopfkissen", "Kissenschlacht"),
    ("Mond", "Licht", "Schalter", "Mondlicht", "Lichtschalter"), ("Sand", "Burg", "Graben", "Sandburg", "Burggraben"),
    ("Schnee", "Mann", "Schaft", "Schneemann", "Mannschaft"), ("Weihnachts", "Baum", "Haus", "Weihnachtsbaum", "Baumhaus"),
    ("Eis", "Berg", "Steiger", "Eisberg", "Bergsteiger"), ("Zahn", "Arzt", "Praxis", "Zahnarzt", "Arztpraxis"),
]

ANALOGIEN = [
    ("Hund", "bellen", "Katze", "miauen", ["zwitschern", "wiehern"]),
    ("Auge", "sehen", "Ohr", "hören", ["riechen", "schmecken"]),
    ("Fisch", "Wasser", "Vogel", "Luft", ["Nest", "Baum"]),
    ("Kuh", "Kalb", "Pferd", "Fohlen", ["Ferkel", "Lamm"]),
    ("Tag", "Sonne", "Nacht", "Mond", ["Wolke", "Bett"]),
    ("Buch", "lesen", "Lied", "singen", ["tanzen", "schreiben"]),
    ("schnell", "langsam", "laut", "leise", ["groß", "hoch"]),
    ("Arzt", "Krankenhaus", "Lehrer", "Schule", ["Büro", "Tafel"]),
    ("Schiff", "Hafen", "Flugzeug", "Flughafen", ["Bahnhof", "Garage"]),
    ("Hand", "Handschuh", "Fuß", "Socke", ["Mütze", "Bein"]),
    ("Winter", "Schnee", "Herbst", "Laub", ["Sonne", "Blüten"]),
    ("Maler", "Pinsel", "Schreiner", "Säge", ["Schere", "Löffel"]),
    ("Biene", "Honig", "Kuh", "Milch", ["Gras", "Käse"]),
    ("groß", "Riese", "klein", "Zwerg", ["Maus", "Kind"]),
]

WAS_BIN_ICH = [
    ("Ich habe Zähne, kann aber nicht beißen.", "Ein Kamm", ["Ein Hund", "Ein Löffel"]),
    ("Ich habe Zeiger, aber keine Finger.", "Eine Uhr", ["Ein Handschuh", "Ein Baum"]),
    ("Je mehr du wegnimmst, desto größer werde ich.", "Ein Loch", ["Ein Berg", "Ein Kuchen"]),
    ("Ich habe einen Hals, aber keinen Kopf.", "Eine Flasche", ["Eine Schlange", "Ein Löffel"]),
    ("Ich werde nass, während ich trockne.", "Ein Handtuch", ["Ein Regenschirm", "Die Sonne"]),
    ("Ich habe Blätter, bin aber kein Baum.", "Ein Buch", ["Ein Stein", "Ein Stuhl"]),
    ("Ich habe ein Auge, kann aber nicht sehen.", "Eine Nadel", ["Ein Stein", "Ein Löffel"]),
    ("Ich habe vier Beine, kann aber nicht laufen.", "Ein Tisch", ["Ein Hund", "Ein Käfer"]),
    ("Ich gehe durch die Fensterscheibe, ohne sie zu zerbrechen.", "Das Licht", ["Ein Ball", "Der Wind"]),
    ("Morgens gehe ich auf vier Beinen, mittags auf zwei und abends auf drei.", "Der Mensch",
     ["Ein Hund", "Ein Vogel"]),
    ("Ich bin immer vor dir, aber du kannst mich nie sehen.", "Die Zukunft", ["Dein Schatten", "Deine Nase"]),
    ("Man kann mich brechen, ohne mich anzufassen.", "Ein Versprechen", ["Ein Glas", "Ein Ast"]),
    ("Ich laufe, wenn du erkältet bist.", "Die Nase", ["Der Fuß", "Die Uhr"]),
    ("Je mehr es von mir gibt, desto weniger siehst du.", "Die Dunkelheit", ["Das Licht", "Die Brille"]),
]


def _kette(g, lvl):
    a, mid, b, w1, w2 = C(WORTKETTEN)
    if lvl <= 3:
        wrong = random.sample(sorted({k[1] for k in WORTKETTEN if k[1] != mid}), 2)
        return choice_task(f"Wortkette: Welches Wort passt hinter „{a}“ UND vor „{b}“?\n{a} + ___ + {b}", mid, wrong,
                           explain=f"{w1} und {w2}", time_factor=1.8)
    return Task("input", f"Wortkette: Welches Wort passt hinter „{a}“ UND vor „{b}“?\n{a} + ___ + {b}", answer=mid,
                accept=_case_variants(mid), explain=f"{w1} und {w2}", time_factor=2.2)


def _analogie(g, lvl):
    a, b, c, d, wrong = C(ANALOGIEN)
    return choice_task(f"Denk-Paare:\n„{a}“ gehört zu „{b}“ wie „{c}“ zu …?", d, wrong,
                       explain=f"{a} → {b}, genauso {c} → {d}", time_factor=1.6)


def _wasbinich(g, lvl):
    q, r, w = C(WAS_BIN_ICH)
    return choice_task(f"Rätsel – Was bin ich?\n{q}", r, w, explain=f"Lösung: {r}", time_factor=1.8)


def _rueckwaerts(g, lvl):
    n = C([x for x in NOMEN if 4 <= len(x["w"]) <= 4 + lvl * 2] or NOMEN)
    code = n["w"].upper()[::-1]
    return Task("input", "Spiegel-Code: Lies das Wort rückwärts!", answer=n["w"], accept=_case_variants(n["w"]),
                visual={"kind": "code", "text": code, "shift": 0, "table": False}, explain=f"{code} → {n['w']}",
                time_factor=1.6)


def gen_raetsel(g, lvl):
    pool = [_caesar, _anagram, _kette, _analogie, _wasbinich, _rueckwaerts]
    return C(pool)(g, lvl)
