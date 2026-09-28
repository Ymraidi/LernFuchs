"""Kreisel-Arena: Aufgaben rund um Battle-Kreisel (im Stil von Beyblade), mit eigenen Figuren und Kreiseln."""

import random

from ..tasks import Task, choice_task, fmt

C = random.choice
R = random.randint

BLADER = ["Leon", "Mia", "Ben", "Lina", "Noah", "Ida", "Paul", "Emma"]
BEYS = ["Sturmfalke", "Feuerdrache", "Eiswolf", "Donnerlöwe", "Blitzadler", "Nebelkobra", "Titanbär", "Sonnenphönix"]
TYPEN = {"Angriff": "greift schnell und hart an", "Verteidigung": "ist schwer und steht fest",
         "Ausdauer": "dreht sich besonders lange", "Balance": "kann von allem ein bisschen"}


def _names():
    a, b = random.sample(BLADER, 2)
    x, y = random.sample(BEYS, 2)
    return a, b, x, y


def gen_bey_mathe(g, lvl):
    a, b, x, y = _names()
    k = 1 if g == 2 else 10 if g == 3 else 100
    kind = C(["dauer", "punkte", "turnier", "teile", "vergleich", "runden"] + (["mal"] if lvl >= 2 else []))
    kw = dict(time_factor=2.2, visual={"kind": "emoji", "e": "🌀"})
    if kind == "dauer":
        t1, t2 = R(25, 70), R(20, 65)
        if t1 == t2:
            t1 += 3
        hi, lo = max(t1, t2), min(t1, t2)
        winner = x if t1 > t2 else y
        return Task("input", f"{a}s Kreisel „{x}“ dreht sich {t1} Sekunden, {b}s „{y}“ {t2} Sekunden.\n"
                             f"Wie viele Sekunden länger dreht sich „{winner}“?", answer=str(hi - lo), unit="s",
                    input_kind="number", explain=f"{hi} − {lo} = {hi - lo}", **kw)
    if kind == "punkte":
        burst, ueber, dreh = R(0, 3), R(0, 3), R(1, 4)
        total = burst * 2 + ueber * 2 + dreh
        return Task("input", f"Im Arena-Turnier gibt es für einen Burst-Sieg 2 Punkte, für einen Sieg aus der Arena "
                             f"2 Punkte und für einen Ausdreh-Sieg 1 Punkt.\n{a} schafft {burst} Burst-Siege, "
                             f"{ueber} Arena-Siege und {dreh} Ausdreh-Siege. Wie viele Punkte sind das?",
                    answer=str(total), input_kind="number",
                    explain=f"{burst} × 2 + {ueber} × 2 + {dreh} × 1 = {total}", **{**kw, "time_factor": 2.8})
    if kind == "turnier":
        n = C([4, 8, 16] if lvl <= 3 else [8, 16, 32])
        return Task("input", f"Bei einem Kreisel-Turnier treten {n} Blader an. In jedem Kampf scheidet einer aus.\n"
                             f"Wie viele Kämpfe braucht man, bis ein Sieger feststeht?", answer=str(n - 1),
                    input_kind="number", explain=f"Jeder außer dem Sieger verliert genau einmal: {n} − 1 = {n - 1}",
                    hint="Tipp: Wie viele Blader müssen verlieren?", **{**kw, "time_factor": 2.6})
    if kind == "teile":
        n = R(2, 6) if g == 2 else R(4, 12)
        return Task("input", f"Ein Battle-Kreisel besteht aus 3 Teilen: Ring, Scheibe und Spitze.\n"
                             f"{a} baut {n} Kreisel. Wie viele Teile braucht {a}?", answer=str(3 * n),
                    input_kind="number", explain=f"{n} × 3 = {3 * n}", **kw)
    if kind == "vergleich":
        p1, p2 = R(12, 40) * k, R(8, 35) * k
        return Task("input", f"{a} hat {fmt(p1)} Turnierpunkte gesammelt, {b} hat {fmt(p2)} Punkte.\n"
                             f"Wie viele Punkte haben beide zusammen?", answer=str(p1 + p2), input_kind="number",
                    explain=f"{fmt(p1)} + {fmt(p2)} = {fmt(p1 + p2)}", **kw)
    if kind == "mal":
        u, s = R(3, 9), R(2, 8)
        return Task("input", f"„{x}“ dreht sich {u}-mal in jeder Zehntelsekunde um sich selbst.\n"
                             f"Wie oft dreht er sich in {s} Zehntelsekunden?", answer=str(u * s), input_kind="number",
                    explain=f"{s} × {u} = {u * s}", **kw)
    need, have = C([3, 4, 5]), R(0, 2)
    return Task("input", f"Wer zuerst {need} Punkte hat, gewinnt das Finale. {a} hat schon {have} Punkte.\n"
                         f"Wie viele Punkte fehlen {a} noch zum Sieg?", answer=str(need - have), input_kind="number",
                explain=f"{need} − {have} = {need - have}", **kw)


BEY_TEXTE = [
    ("Das große Arena-Finale", 2,
     "Heute ist das Finale der Stadtmeisterschaft. Leon tritt mit seinem Kreisel Sturmfalke an. Sein Gegner ist "
     "Ben mit dem schweren Titanbär. Die Schiedsrichterin ruft: „Drei, zwei, eins – los!“ Beide Kreisel sausen in "
     "die Arena. Titanbär ist ein Verteidigungs-Kreisel und steht ganz fest. Sturmfalke greift immer wieder an. "
     "Nach einem starken Treffer fliegt Titanbär in drei Teile auseinander. Das ist ein Burst-Sieg! Leon jubelt und "
     "gibt Ben die Hand. „Das war ein toller Kampf“, sagt Ben.",
     [("Wie heißt Leons Kreisel?", "Sturmfalke", ["Titanbär", "Feuerdrache"]),
      ("Was für ein Kreisel ist Titanbär?", "Ein Verteidigungs-Kreisel", ["Ein Angriffs-Kreisel", "Ein Ausdauer-Kreisel"]),
      ("In wie viele Teile fliegt Titanbär auseinander?", "In drei Teile", ["In zwei Teile", "In vier Teile"]),
      ("Was macht Leon nach dem Sieg?", "Er gibt Ben die Hand", ["Er geht sofort nach Hause", "Er lacht Ben aus"])]),
    ("Mias Trainingsplan", 2,
     "Mia möchte beim nächsten Turnier gewinnen. Deshalb trainiert sie jeden Tag nach den Hausaufgaben. Zuerst übt "
     "sie den Start: Der Kreisel muss ganz gerade in die Arena. Dann testet sie, wie lange ihr Eiswolf sich dreht. "
     "Am Montag sind es 48 Sekunden, am Freitag schon 55 Sekunden. Ihr Trainer sagt: „Ein guter Blader braucht "
     "Geduld, Konzentration und Fairness.“ Mia schreibt die drei Wörter auf einen Zettel und hängt ihn über ihr Bett.",
     [("Wann trainiert Mia?", "Nach den Hausaufgaben", ["Vor der Schule", "Nur am Wochenende"]),
      ("Wie lange dreht sich Eiswolf am Freitag?", "55 Sekunden", ["48 Sekunden", "15 Sekunden"]),
      ("Was braucht ein guter Blader laut Trainer?", "Geduld, Konzentration und Fairness",
       ["Nur einen teuren Kreisel", "Viel Glück und Lautstärke"]),
      ("Wohin hängt Mia den Zettel?", "Über ihr Bett", ["An die Tür", "In die Schule"])]),
]

KREISEL_FAKTEN = [
    (2, "Warum fällt ein Kreisel nicht um, solange er sich schnell dreht?",
     "Die schnelle Drehung hält ihn stabil aufrecht", ["Er ist mit Magneten festgeklebt", "Die Luft trägt ihn"], "🌀",
     "Je schneller er sich dreht, desto stabiler steht er – das nennt man Kreiselwirkung."),
    (2, "Warum wird ein Kreisel mit der Zeit langsamer?",
     "Reibung an der Spitze und in der Luft bremst ihn", ["Er wird müde", "Der Boden zieht ihn nach unten"], "🌀",
     "Reibung wandelt die Drehbewegung in Wärme um."),
    (2, "Welche Spitze dreht sich meist am längsten?", "Eine spitze, glatte Spitze",
     ["Eine breite, raue Spitze", "Eine Spitze aus Gummi"], "📍", "Wenig Reibung = lange Drehzeit."),
    (3, "Warum ist ein schwerer Kreisel schwerer aus der Arena zu stoßen?",
     "Er hat mehr Masse und bewegt sich nicht so leicht", ["Er ist klebriger", "Er ist leiser"], "⚖️",
     "Mehr Masse bedeutet mehr Trägheit."),
    (3, "Wo liegt bei einem guten Kreisel das meiste Gewicht?", "Außen am Rand",
     ["Genau in der Mitte oben", "Nur an der Spitze"], "⭕", "Gewicht außen sorgt für mehr Schwung und Ausdauer."),
    (2, "Was ist fair nach einem Turnierkampf?", "Dem Gegner die Hand geben",
     ["Den Kreisel des Gegners verstecken", "Laut schimpfen"], "🤝", ""),
    (3, "Seit wann spielen Kinder mit Kreiseln?", "Schon seit Tausenden von Jahren",
     ["Erst seit 10 Jahren", "Seit es Computer gibt"], "🏺", "Sogar im alten Ägypten gab es schon Kreisel."),
    (2, "Was passiert mit einem Kreisel, der sich schneller dreht?", "Er steht stabiler",
     ["Er fällt sofort um", "Er wird schwerer"], "🌀", ""),
]


def gen_bey_lesen(g, lvl):
    title, _, text, qs = C(BEY_TEXTE)
    n = 2 if lvl <= 1 else 3 if lvl <= 3 else len(qs)
    tasks = []
    for i, (q, right, wrong) in enumerate(qs[:n]):
        tasks.append(choice_task(q, right, wrong, visual={"kind": "text", "title": title, "text": text},
                                 time_factor=(3.5 + len(text) / 150) if i == 0 else 1.2, speak=q,
                                 explain="Lies noch einmal genau im Text nach."))
    return tasks


def gen_bey_wissen(g, lvl):
    grade, q, r, w, e, x = C([f for f in KREISEL_FAKTEN if f[0] <= g + 1])
    concept = {"kind": "fact", "g": grade, "q": q, "r": r, "w": w, "e": e, "x": x, "skill": "sach.bey"}
    return choice_task(q, r, w, visual={"kind": "emoji", "e": e}, explain=x or f"Richtig: {r}", concept=concept)
