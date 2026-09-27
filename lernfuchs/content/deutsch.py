"""Deutsch-Aufgabengeneratoren: Lesen, Hören, Diktat, Rechtschreibung, Wortschatz u. v. m."""

import random
import re

from ..tasks import Task, choice_task, shuffle
from .deutsch_data import (ADJEKTIVE, DIKTAT_SAETZE, KOMPOSITA, MINIMALPAARE, NOMEN, REIME,
                           SATZZEICHEN, TEXTE, VERBEN, WORTFAMILIEN)

C = random.choice
SUBJ = "deutsch"


def _nomen(g, maxlen=99, minlen=1, need_plural=False, need_emoji=False):
    pool = [n for n in NOMEN if n["g"] <= g and minlen <= len(n["w"]) <= maxlen
            and (n["pl"] or not need_plural) and (n["e"] or not need_emoji)]
    return pool or NOMEN


def _len_for(lvl):
    return {1: (2, 4), 2: (3, 5), 3: (4, 7), 4: (5, 9), 5: (6, 16)}[lvl]


# --- Rechtschreib-Hilfen -----------------------------------------------------

GAP_RULES = [
    (r"ie", ["ie", "i", "ei"], "Das lange i schreibt man meistens „ie“."),
    (r"ei", ["ei", "ai", "ie"], "Hier schreibt man „ei“."),
    (r"äu", ["äu", "eu"], "„äu“ kommt von „au“ (z. B. Baum → Bäume)."),
    (r"eu", ["eu", "äu", "oi"], "Gibt es kein verwandtes Wort mit „au“, schreibt man „eu“."),
    (r"ck", ["ck", "k", "kk"], "Nach kurzem Selbstlaut schreibt man „ck“."),
    (r"tz", ["tz", "z", "zz"], "Nach kurzem Selbstlaut schreibt man „tz“."),
    (r"ß", ["ß", "ss", "s"], "Nach langem Selbstlaut oder Zwielaut schreibt man „ß“."),
    (r"ss", ["ss", "ß", "s"], "Nach kurzem Selbstlaut schreibt man „ss“."),
    (r"pf", ["pf", "f"], "Sprich ganz deutlich: p-f!"),
    (r"(ll|mm|nn|tt|pp|ff|rr)", None, "Nach kurzem Selbstlaut wird der Mitlaut oft verdoppelt."),
    (r"[aeouäöü]h(?=[lmnr])", None, "Hier zeigt ein stummes „h“, dass der Selbstlaut lang ist."),
    (r"ä", ["ä", "e"], "„ä“ kommt oft von „a“ (z. B. Apfel → Äpfel)."),
    (r"[dtgkbp]$", None, "Verlängere das Wort, dann hörst du es: z. B. Hund → Hunde."),
    (r"^V", ["V", "F"], "Merkwort mit V!"),
]
_END_ALT = {"d": "t", "t": "d", "g": "k", "k": "g", "b": "p", "p": "b"}


def spelling_gap(word):
    """Findet eine Rechtschreib-Schwierigkeit und macht daraus eine Lücke."""
    found = []
    for pat, opts, rule in GAP_RULES:
        for m in re.finditer(pat, word):
            s, e = m.span()
            part = word[s:e]
            if opts is None:
                if pat.startswith("(ll"):
                    opts_ = [part, part[0]]
                elif pat.startswith("[aeou"):
                    opts_ = [part, part[0], part[0] * 2 if part[0] in "aeo" else part[0] + "e"]
                else:
                    opts_ = [part, _END_ALT[part]]
            else:
                opts_ = list(opts)
            if s == 0 and word[0].isupper():
                opts_ = [o[0].upper() + o[1:] for o in opts_]
                part = part[0].upper() + part[1:]
            found.append((s, e, part, list(dict.fromkeys(opts_)), rule))
    if not found:
        return None
    return C(found)


MISSPELL = [("ie", "i"), ("ie", "ei"), ("ei", "ie"), ("ck", "k"), ("tz", "z"), ("ß", "ss"), ("ss", "ß"),
            ("ll", "l"), ("mm", "m"), ("nn", "n"), ("tt", "t"), ("pp", "p"), ("ff", "f"), ("rr", "r"),
            ("ah", "a"), ("eh", "e"), ("oh", "o"), ("uh", "u"), ("äh", "ä"), ("üh", "ü"), ("öh", "ö"),
            ("ä", "e"), ("äu", "eu"), ("eu", "äu"), ("pf", "f"), ("V", "F"), ("chs", "ks"), ("ng", "nk"),
            ("Sch", "Sh"), ("sch", "sh"), ("ei", "ai"), ("z", "tz"), ("k", "ck"), ("s", "ss"), ("h", "")]


def misspellings(word, n=2):
    out = set()
    for a, b in shuffle(MISSPELL):
        idx = [m.start() for m in re.finditer(re.escape(a), word)]
        if not idx:
            continue
        i = C(idx)
        if a == "h" and (i == 0 or word[i - 1] in "sc"):
            continue
        cand = word[:i] + b + word[i + len(a):]
        if cand != word and len(cand) > 1:
            out.add(cand)
        if len(out) >= n:
            break
    if word[-1] in _END_ALT and len(out) < n:
        out.add(word[:-1] + _END_ALT[word[-1]])
    extra = []
    if word[0].isupper():
        extra.append(word.lower())
    vowels = [i for i, ch in enumerate(word) if ch in "aeiouäöü"]
    if vowels:
        v = vowels[0]
        extra.append(word[:v + 1] + "h" + word[v + 1:])
    if word[-1] not in "aeiouäöü":
        extra.append(word + word[-1])
    elif len(word) > 2 and word[-2] not in "aeiouäöü":
        extra.append(word[:-2] + word[-2] * 2 + word[-1])
    for cand in extra:
        if len(out) >= n:
            break
        if cand != word:
            out.add(cand)
    tries = 0
    while len(out) < n and len(word) > 3 and tries < 20:
        tries += 1
        i = random.randint(1, len(word) - 2)
        cand = word[:i] + word[i + 1] + word[i] + word[i + 2:]
        if cand != word:
            out.add(cand)
    return list(out)[:n]


def word_task(w: str, form: str, emoji: str = "", skill="deutsch.rechtschreibung", g=2) -> Task:
    """Ein Wort in verschiedenen Formen üben (für Wiederholungen)."""
    concept = {"kind": "word", "w": w, "e": emoji}
    vis = {"kind": "emoji", "e": emoji} if emoji else None
    kw = dict(skill=skill, subject=SUBJ, concept=concept)
    if form == "tiles":
        letters = list(w)
        items = shuffle(letters)
        if items == letters and len(set(letters)) > 1:
            items = letters[::-1]
        return Task("order", "Lege das Wort aus den Buchstaben:", answer=letters, items=items,
                    visual=vis, speak=f"Lege das Wort {w}", explain=f"Das Wort heißt: {w}",
                    time_factor=1.2 + len(w) * 0.1, **kw)
    if form == "diktat":
        return Task("input", "Hör gut zu und schreibe das Wort.", answer=w, listen=True, listen_text=w,
                    speak=w, visual=vis, explain=f"Richtig geschrieben: {w}",
                    hint="Nomen schreibt man groß!" if w[0].isupper() else "", time_factor=1.3, **kw)
    if form == "gap":
        gap = spelling_gap(w)
        if gap:
            s, e, part, opts, rule = gap
            shown = w[:s] + "_" * max(2, e - s) + w[e:]
            return Task("choice", f"Was fehlt?\n{shown}", answer=part, options=shuffle(opts), visual=vis,
                        speak=f"Was fehlt im Wort {w}?", explain=f"{w} – {rule}", **kw)
    wrong = misspellings(w, 2)
    return choice_task("Welches Wort ist richtig geschrieben?", w, wrong, visual=vis,
                       speak="Welches Wort ist richtig geschrieben?", explain=f"Richtig: {w}", **kw)


def review_word(c: dict, avoid: str) -> Task:
    forms = {"order": ["diktat", "gap", "choice"], "input": ["tiles", "gap", "choice"],
             "choice": ["tiles", "diktat"]}.get(avoid, ["tiles", "diktat", "gap", "choice"])
    return word_task(c["w"], C(forms), c.get("e", ""))


# --- Lesen & Hören -----------------------------------------------------------

def _pick_text(g, lvl):
    pool = [t for t in TEXTE if t[1] <= g and t[2] <= lvl + 1]
    if not pool:
        pool = [t for t in TEXTE if t[1] <= g] or TEXTE
    near = [t for t in pool if abs(t[2] - lvl) <= 1 and t[1] >= g - 1]
    return C(near or pool)


def gen_lesen(g, lvl):
    title, _, _, text, qs = _pick_text(g, lvl)
    n = 2 if lvl <= 1 else 3 if lvl <= 3 else len(qs)
    tasks = []
    for i, (q, right, wrong) in enumerate(qs[:n]):
        t = choice_task(q, right, wrong, skill="deutsch.lesen", subject=SUBJ,
                        visual={"kind": "text", "title": title, "text": text},
                        time_factor=(3.5 + len(text) / 150) if i == 0 else 1.2,
                        speak=q, explain=f"Lies noch einmal genau im Text nach.")
        tasks.append(t)
    return tasks


def gen_hoeren(g, lvl):
    if lvl <= 2 and random.random() < 0.5 or random.random() < 0.25:
        a, b = C(MINIMALPAARE)
        target = C([a, b])
        extra = C([w for p in MINIMALPAARE for w in p if w not in (a, b)])
        opts = [a, b] + ([extra] if lvl >= 2 else [])
        return Task("choice", "Hör genau hin! Welches Wort hörst du?", answer=target, options=shuffle(opts),
                    listen=True, listen_text=target, speak=target, skill="deutsch.hoeren", subject=SUBJ,
                    explain=f"Das Wort war: {target}", concept={"kind": "word", "w": target, "e": ""})
    title, _, _, text, qs = _pick_text(g, lvl)
    n = 2 if lvl <= 2 else 3
    tasks = []
    for i, (q, right, wrong) in enumerate(qs[:n]):
        tasks.append(choice_task(
            q, right, wrong, skill="deutsch.hoeren", subject=SUBJ, listen=True, listen_text=text,
            speak=(f"Hör gut zu. {title}. {text} ... {q}" if i == 0 else q),
            visual={"kind": "listen", "title": title},
            time_factor=(3.0 + len(text) / 120) if i == 0 else 1.2,
            explain="Hör dir die Geschichte noch einmal an."))
    return tasks


def gen_diktat(g, lvl):
    if lvl <= 2:
        lo, hi = _len_for(lvl + (g - 2))
        n = C(_nomen(g, hi, lo, need_emoji=lvl == 1))
        return word_task(n["w"], "diktat", n["e"] if lvl == 1 or random.random() < 0.5 else "",
                         skill="deutsch.diktat")
    if lvl == 3 and random.random() < 0.5:
        n = C(_nomen(g, 9))
        phrase = f"{n['art']} {n['w']}"
        return Task("input", "Hör gut zu und schreibe Artikel und Nomen.", answer=phrase, listen=True,
                    listen_text=phrase, speak=phrase, skill="deutsch.diktat", subject=SUBJ,
                    explain=f"Richtig: {phrase}", hint="Artikel klein, Nomen groß!", time_factor=1.5,
                    concept={"kind": "word", "w": n["w"], "e": n["e"]})
    pool = [s for s in DIKTAT_SAETZE if s[1] <= g and s[2] <= lvl] or DIKTAT_SAETZE[:6]
    sent = C(pool)[0]
    return Task("input", "Hör gut zu und schreibe den Satz.", answer=sent, accept=[sent.rstrip(".!?")],
                listen=True, listen_text=sent, speak=sent, skill="deutsch.diktat", subject=SUBJ,
                explain=f"Richtig: {sent}", hint="Satzanfang und Nomen groß – Punkt am Ende!",
                time_factor=2.5 + len(sent) / 20)


def gen_rechtschreibung(g, lvl):
    kind = C(["gap", "gap", "choice", "gross"] + (["satzzeichen"] if lvl >= 2 else [])
             + (["tiles"] if lvl <= 2 else []))
    lo, hi = _len_for(min(5, lvl + (g - 2)))
    if kind == "gross":
        n = C(_nomen(g, hi))
        v = C([x for x in VERBEN if x["g"] <= g])
        a = C(ADJEKTIVE)
        opts = [n["w"].lower(), v["w"], a["w"]]
        return Task("choice", "Welches Wort schreibt man groß?", answer=n["w"].lower(), options=shuffle(opts),
                    skill="deutsch.rechtschreibung", subject=SUBJ,
                    explain=f"{n['w']} ist ein Nomen ({n['art']} {n['w']}). Nomen schreibt man groß!")
    if kind == "satzzeichen":
        s, mark = C(SATZZEICHEN)
        return Task("choice", f"Welches Satzzeichen fehlt?\n{s} ___", answer=mark, options=[".", "?", "!"],
                    skill="deutsch.rechtschreibung", subject=SUBJ, speak=s,
                    explain={"?": "Eine Frage endet mit ?", "!": "Ein Ausruf oder Befehl endet mit !",
                             ".": "Ein Aussagesatz endet mit einem Punkt."}[mark])
    pool = _nomen(g, hi, lo) + [{"w": v["w"], "e": ""} for v in VERBEN if v["g"] <= g and lo <= len(v["w"]) <= hi]
    n = C(pool)
    return word_task(n["w"], kind, n.get("e", ""), g=g)


def gen_puzzle(g, lvl):
    if lvl >= 3 and random.random() < 0.4:
        pool = [n for n in NOMEN if n["syl"].count("-") >= (1 if lvl == 3 else 2) and n["g"] <= g]
        n = C(pool)
        syl = n["syl"].split("-")
        items = shuffle(syl)
        while items == syl:
            items = shuffle(syl)
        return Task("order", "Setze die Silben zum Wort zusammen:", answer=syl, items=items,
                    visual={"kind": "emoji", "e": n["e"]} if n["e"] else None, skill="deutsch.puzzle",
                    subject=SUBJ, explain=f"{n['syl']} → {n['w']}", speak="Setze die Silben zusammen.",
                    concept={"kind": "word", "w": n["w"], "e": n["e"]})
    lo, hi = _len_for(lvl)
    n = C(_nomen(g, hi, lo, need_emoji=lvl <= 3))
    t = word_task(n["w"], "tiles", n["e"], skill="deutsch.puzzle")
    return t


# --- Wortschatz --------------------------------------------------------------

RELATED = [{"Essen", "Obst", "Gemüse", "Getränke"}, {"Möbel", "Haus"}, {"Familie", "Berufe"},
           {"Spielzeug", "Musikinstrumente"}, {"Kleidung"}, {"Schulsachen"}]
CATS = ["Tiere", "Obst", "Gemüse", "Fahrzeuge", "Kleidung", "Schulsachen", "Möbel", "Körperteile",
        "Essen", "Spielzeug", "Musikinstrumente", "Familie", "Berufe", "Getränke"]


def gen_wortschatz(g, lvl):
    kinds = ["oberbegriff", "passtnicht", "gegenteil", "reim", "kompositum"]
    if g >= 3:
        kinds += ["wortfamilie", "wortfamilie"]
    kind = C(kinds[:3] if lvl == 1 else kinds)
    kw = dict(skill="deutsch.wortschatz", subject=SUBJ)
    if kind in ("oberbegriff", "passtnicht"):
        cats = [c for c in CATS if len([n for n in NOMEN if n["cat"] == c and n["g"] <= g]) >= 4]
        cat = C(cats)
        related = next((grp for grp in RELATED if cat in grp), {cat})
        members = random.sample([n for n in NOMEN if n["cat"] == cat and n["g"] <= g], 3)
        if kind == "oberbegriff":
            wrong = random.sample([c for c in cats if c not in related], 2)
            return choice_task("Welcher Oberbegriff passt?\n" + ", ".join(m["w"] for m in members),
                               cat, wrong, visual={"kind": "emoji_row", "items": [m["e"] for m in members if m["e"]]},
                               explain=f"{', '.join(m['w'] for m in members)} sind {cat}.", **kw)
        odd = C([n for n in NOMEN if n["cat"] not in related and n["cat"] not in ("Natur", "Haus", "Gebäude")
                 and n["g"] <= g])
        return choice_task("Welches Wort passt nicht dazu?", odd["w"], [m["w"] for m in members],
                           explain=f"{', '.join(m['w'] for m in members)} gehören zu „{cat}“ – {odd['w']} nicht.",
                           emojis={m["w"]: m["e"] for m in members + [odd] if m["e"]}, **kw)
    if kind == "gegenteil":
        a = C(ADJEKTIVE)
        wrong = random.sample([x["w"] for x in ADJEKTIVE if x["w"] not in (a["w"], a["opp"])], 2)
        return choice_task(f"Was ist das Gegenteil von „{a['w']}“?", a["opp"], wrong,
                           explain=f"{a['w']} ↔ {a['opp']}", **kw)
    if kind == "reim":
        grp = C(REIME)
        w, r = random.sample(grp, 2)
        others = [x for gr in REIME if w not in gr for x in gr]
        wrong = random.sample([o for o in others if o[-2:] != w[-2:]], 2)
        return choice_task(f"Was reimt sich auf „{w}“?", r, wrong, explain=f"{w} – {r} reimt sich!", **kw)
    if kind == "kompositum":
        a, b, res, emo = C(KOMPOSITA)
        art_b, word_b = b.split()
        if lvl >= 3 and random.random() < 0.5:
            art, word = res.split()
            return Task("choice", f"{a} + {b} = {word}\nWelcher Artikel passt zu „{word}“?", answer=art,
                        options=["der", "die", "das"], visual={"kind": "emoji", "e": emo},
                        explain=f"Das letzte Wort bestimmt den Artikel: {b} → {res}", **kw)
        right = res.split()[1]
        wrong = [word_b + a.lower(), C([k[2].split()[1] for k in KOMPOSITA if k[2] != res])]
        return choice_task(f"Setze zusammen:\n{a} + {word_b} = ?", right, wrong,
                           visual={"kind": "emoji", "e": emo}, explain=f"{a} + {word_b} = {right}", **kw)
    fam, members, outs = C(WORTFAMILIEN)
    return choice_task(f"Welches Wort gehört NICHT zur Wortfamilie „{fam}“?", C(outs),
                       random.sample(members, 3), explain=f"Zur Familie „{fam}“ gehören z. B.: {', '.join(members)}.",
                       **kw)


# --- Artikel & Mehrzahl ------------------------------------------------------

def _wrong_plurals(n):
    w, pl = n["w"], n["pl"]
    cands = {w + "s", w + "en", w + "e", w + "er", w + "n"}
    if re.search(r"[aou]", w):
        um = re.sub(r"([aou])(?!.*[aou])", lambda m: {"a": "ä", "o": "ö", "u": "ü"}[m.group(1)], w)
        cands |= {um + "e", um + "er"}
    cands.discard(pl)
    cands.discard(w) if w != pl else None
    return random.sample(sorted(cands), 2)


AMBIG_ARTIKEL = {"Radiergummi", "Joghurt", "Puzzle", "Brokkoli"}
ALT_PLURAL = {"Pizza": ["Pizzen"], "Sofa": ["Sofas"], "Kaktus": ["Kakteen"], "Schal": ["Schale"]}


def gen_artikel(g, lvl):
    kw = dict(skill="deutsch.artikel", subject=SUBJ)
    kind = C(["artikel", "artikel", "mehrzahl"] + (["einzahl"] if lvl >= 3 else []))
    if kind == "artikel":
        n = C([x for x in _nomen(g, need_emoji=lvl <= 2) if x["w"] not in AMBIG_ARTIKEL])
        return Task("choice", f"der, die oder das?\n___ {n['w']}", answer=n["art"], options=["der", "die", "das"],
                    visual={"kind": "emoji", "e": n["e"]} if n["e"] else None, speak=f"der, die oder das? {n['w']}",
                    explain=f"{n['art']} {n['w']}", concept={"kind": "word", "w": n["w"], "e": n["e"]}, **kw)
    n = C(_nomen(g, need_plural=True))
    if kind == "mehrzahl":
        if lvl >= 4:
            return Task("input", f"Schreibe die Mehrzahl:\n{n['art']} {n['w']} → die ___", answer=n["pl"],
                        accept=ALT_PLURAL.get(n["w"], []),
                        visual={"kind": "emoji", "e": n["e"]} if n["e"] else None,
                        explain=f"{n['art']} {n['w']} → die {n['pl']}", time_factor=1.4, **kw)
        return choice_task(f"Einzahl und Mehrzahl:\nein{'e' if n['art'] == 'die' else ''} {n['w']} – viele ___",
                           n["pl"], _wrong_plurals(n),
                           visual={"kind": "emoji_groups", "groups": [[n["e"], 1], [n["e"], 3]], "sep": "→"}
                           if n["e"] else None, explain=f"{n['art']} {n['w']} → die {n['pl']}", **kw)
    right = f"{n['art']} {n['w']}"
    wrong = [f"{C([a for a in ('der', 'die', 'das') if a != n['art']])} {n['w']}"]
    wp = _wrong_plurals(n)[0]
    wrong.append(f"{n['art']} {wp}")
    return choice_task(f"Wie heißt die Einzahl?\ndie {n['pl']}", right, wrong, explain=f"die {n['pl']} → {right}", **kw)


# --- Wortarten ---------------------------------------------------------------

def _wort_mit_art():
    t = C(["Nomen", "Verb", "Adjektiv"])
    if t == "Nomen":
        return C(NOMEN)["w"], t
    if t == "Verb":
        return C(VERBEN)["w"], t
    return C(ADJEKTIVE)["w"], t


def gen_wortarten(g, lvl):
    kw = dict(skill="deutsch.wortarten", subject=SUBJ)
    if lvl >= 3 and random.random() < 0.5:
        words = {}
        while len(words) < (5 if lvl == 3 else 7):
            w, t = _wort_mit_art()
            words[w] = t
        return Task("sort", "Sortiere die Wörter: Nomen, Verb oder Adjektiv?", answer=words,
                    items=shuffle(list(words)), buckets=["Nomen", "Verb", "Adjektiv"], time_factor=2.5,
                    explain="Nomen: Namenwörter (groß) · Verben: Tunwörter · Adjektive: Wiewörter", **kw)
    w, t = _wort_mit_art()
    tip = {"Nomen": "Nomen sind Namenwörter für Menschen, Tiere, Dinge – man schreibt sie groß.",
           "Verb": "Verben sagen, was jemand tut (Tunwörter).",
           "Adjektiv": "Adjektive sagen, wie etwas ist (Wiewörter)."}[t]
    return Task("choice", f"Welche Wortart ist „{w}“?", answer=t, options=["Nomen", "Verb", "Adjektiv"],
                explain=tip, **kw)


# --- ABC & Silben ------------------------------------------------------------

ABC = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def gen_abc(g, lvl):
    kw = dict(skill="deutsch.abc", subject=SUBJ)
    kind = C(["ordnen", "buchstabe", "silben", "ordnen"])
    if kind == "buchstabe":
        i = random.randint(1, 24)
        before = random.random() < 0.5
        ans = ABC[i - 1] if before else ABC[i + 1]
        wrong = random.sample([c for c in ABC[max(0, i - 3):i + 4] if c not in (ans, ABC[i])], 2)
        return choice_task(f"Welcher Buchstabe kommt im ABC {'vor' if before else 'nach'} {ABC[i]}?", ans, wrong,
                           explain=f"… {ABC[i - 1]}, {ABC[i]}, {ABC[i + 1]} …", **kw)
    if kind == "silben":
        pool = [n for n in NOMEN + VERBEN if n.get("g", 2) <= g]
        n = C(pool)
        cnt = n["syl"].count("-") + 1
        return Task("choice", f"Wie viele Silben hat „{n['w']}“?\nKlatsche mit!", answer=str(cnt),
                    options=["1", "2", "3", "4"], speak=f"Wie viele Silben hat {n['w']}?",
                    explain=f"{n['syl'].replace('-', ' – ')} = {cnt} Silbe{'n' if cnt > 1 else ''}", **kw)
    k = 3 if lvl == 1 else 4 if lvl <= 3 else 5
    if lvl >= 4 and g >= 3:
        letter = C([L for L in "BFHKMSTW" if sum(1 for n in NOMEN if n["w"][0] == L) >= k])
        words = random.sample(sorted({n["w"] for n in NOMEN if n["w"][0] == letter}), k)
        extra = " Tipp: Schau auf den 2. Buchstaben!"
    else:
        by_first = {}
        for n in _nomen(g):
            by_first.setdefault(n["w"][0], n["w"])
        words = random.sample(list(by_first.values()), k)
        extra = ""
    ordered = sorted(words, key=abc_key)
    return Task("order", "Ordne nach dem ABC!" + extra, answer=ordered, items=shuffle(words),
                explain=" → ".join(ordered), time_factor=1.2 + 0.3 * k, **kw)


def abc_key(w: str) -> str:
    w = w.lower()
    for a, b in (("ä", "a"), ("ö", "o"), ("ü", "u"), ("ß", "ss")):
        w = w.replace(a, b)
    return w


# --- Verben (Personalform, Zeitformen) & Adjektive (Steigerung) --------------

OBJ = {"laufen": "schnell", "springen": "hoch", "spielen": "Fußball", "schwimmen": "im See", "lesen": "ein Buch",
       "schreiben": "einen Brief", "malen": "ein Bild", "singen": "ein Lied", "tanzen": "im Garten",
       "essen": "einen Apfel", "trinken": "Tee", "schlafen": "lange", "rennen": "zur Schule", "lachen": "laut",
       "weinen": "leise", "kochen": "Suppe", "backen": "einen Kuchen", "fahren": "Fahrrad", "fliegen": "nach Rom",
       "rechnen": "Aufgaben", "gehen": "nach Hause", "sehen": "einen Film", "rufen": "laut", "klettern": "auf den Baum",
       "bauen": "eine Burg", "werfen": "den Ball", "fangen": "den Ball", "tragen": "die Tasche", "helfen": "Mama",
       "kommen": "nach Hause", "schauen": "aus dem Fenster", "hören": "Musik", "denken": "nach", "turnen": "in der Halle"}
PERSONEN = ["Tom", "Lisa", "Oma", "Opa", "Mia", "Ben", "mein Freund", "meine Schwester"]


def _satzanfang(s):
    return s[0].upper() + s[1:]


def gen_verben(g, lvl):
    kw = dict(skill="deutsch.verben", subject=SUBJ)
    v = C([x for x in VERBEN if x["g"] <= g])
    kinds = ["ich", "er"] + (["praet", "praet", "steigerung"] if g >= 3 or lvl >= 4 else [])
    kind = C(kinds)
    if kind == "ich":
        ans = v["w"][:-1] + "e" if v["w"].endswith(("ern", "eln")) else v["w"][:-1]
        wrong = [v["w"], v["er"]]
        obj = OBJ.get(v["w"], "")
        return choice_task(f"Setze richtig ein ({v['w']}):\nIch ___ {obj}.", ans, wrong,
                           explain=f"Ich {ans} {obj}.", **kw)
    if kind == "er":
        ans = v["er"]
        cands = [v["w"], v["w"][:-1], v["w"][:-2] + "t", v["w"][:-2] + "et"]
        wrong = random.sample([w for w in dict.fromkeys(cands) if w != ans], 2)
        name = C(PERSONEN)
        obj = OBJ.get(v["w"], "")
        return choice_task(f"Setze richtig ein ({v['w']}):\n{_satzanfang(name)} ___ {obj}.", ans, wrong,
                           explain=f"{_satzanfang(name)} {ans} {obj}.", **kw)
    if kind == "praet":
        ans = v["prae"]
        stem = v["w"][:-2] if v["w"].endswith("en") else v["w"][:-1]
        wrong = list(dict.fromkeys([stem + "te", v["er"], "ge" + stem + "t"]))
        wrong = [w for w in wrong if w != ans][:2]
        name = C(PERSONEN)
        obj = OBJ.get(v["w"], "")
        satz = f"Heute {v['er']} {name} {obj}.\nGestern ___ {name} {obj}."
        expl = f"Gestern {v['prae']} {name} {obj}. ({v['w']} → {v['prae']})"
        if lvl >= 4:
            return Task("input", satz, answer=ans, explain=expl, time_factor=1.4, **kw)
        return choice_task(satz, ans, wrong, explain=expl, **kw)
    a = C(ADJEKTIVE)
    cands = ["am " + a["w"] + "sten", "am " + a["w"] + "esten", "am " + a["komp"] + "sten", "am mehr " + a["w"]]
    wrong = random.sample([w for w in dict.fromkeys(cands) if w != a["sup"]], 2)
    return choice_task(f"Steigere das Adjektiv:\n{a['w']} – {a['komp']} – ___", a["sup"], wrong[:2],
                       explain=f"{a['w']} – {a['komp']} – {a['sup']}", **kw)
