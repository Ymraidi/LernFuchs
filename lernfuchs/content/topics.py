"""Themenkatalog: welche Themen es gibt, ab welcher Klasse, und welcher Generator sie erzeugt."""

import random
from dataclasses import dataclass
from typing import Callable, Optional

from . import deutsch, fokus, knobeln, konz, mathe, sachkunde
from ..tasks import Task


@dataclass
class Topic:
    id: str
    subject: str
    title: str
    emoji: str
    min_g: int = 2
    max_g: int = 4
    gen: Optional[Callable] = None
    kind: str = "tasks"   # tasks | game | online
    desc: str = ""
    special: bool = False  # Knobel-/Sonderthema
    fokus: bool = False    # Konzentrationsthema

    @property
    def skill(self) -> str:
        return f"{self.subject}.{self.id}"


TOPICS = [
    # Deutsch
    Topic("lesen", "deutsch", "Lesen & Verstehen", "📖", gen=deutsch.gen_lesen, desc="Geschichten lesen, Fragen beantworten"),
    Topic("hoeren", "deutsch", "Hör genau hin", "👂", gen=deutsch.gen_hoeren, desc="Zuhören und verstehen"),
    Topic("diktat", "deutsch", "Diktat", "✍️", gen=deutsch.gen_diktat, desc="Hören und richtig schreiben"),
    Topic("rechtschreibung", "deutsch", "Rechtschreibung", "🔤", gen=deutsch.gen_rechtschreibung,
          desc="ie, ck, tz, ß, groß & klein"),
    Topic("puzzle", "deutsch", "Buchstaben-Puzzle", "🧩", gen=deutsch.gen_puzzle, desc="Wörter aus Buchstaben bauen"),
    Topic("wortschatz", "deutsch", "Wortschatz", "💬", gen=deutsch.gen_wortschatz,
          desc="Oberbegriffe, Gegenteile, Reime"),
    Topic("artikel", "deutsch", "Artikel & Mehrzahl", "🏷️", gen=deutsch.gen_artikel, desc="der, die, das – eins, viele"),
    Topic("wortarten", "deutsch", "Wortarten", "🧱", gen=deutsch.gen_wortarten, desc="Nomen, Verb, Adjektiv"),
    Topic("abc", "deutsch", "ABC & Silben", "🔠", gen=deutsch.gen_abc, desc="Alphabet und Silben klatschen"),
    Topic("verben", "deutsch", "Verben & Zeitformen", "⏪", gen=deutsch.gen_verben, desc="ich laufe, er lief"),
    Topic("fokus", "deutsch", "Wort-Blitz & Fokus", "🎯", gen=fokus.gen_fokus_deutsch,
          desc="Kurz sehen, merken, genau lesen", fokus=True),
    Topic("raetsel", "deutsch", "Rätsel & Geheimschrift", "🕵️", gen=knobeln.gen_raetsel,
          desc="Codes knacken, Denk-Paare, Wortketten", special=True),
    # Mathe
    Topic("plusminus", "mathe", "Plus & Minus", "➕", gen=mathe.gen_plusminus, desc="Addieren und Subtrahieren"),
    Topic("einmaleins", "mathe", "Mal & Geteilt", "✖️", gen=mathe.gen_einmaleins, desc="Einmaleins und Teilen"),
    Topic("verdoppeln", "mathe", "Verdoppeln & Halbieren", "👯", gen=mathe.gen_verdoppeln),
    Topic("zahlen", "mathe", "Zahlen & Vergleichen", "🔢", gen=mathe.gen_zahlen, desc="<, >, Nachbarzahlen, Stellenwerte"),
    Topic("folgen", "mathe", "Muster & Zahlenfolgen", "🔁", gen=mathe.gen_folgen),
    Topic("zahlenmauer", "mathe", "Zahlenmauern", "🧱", gen=mathe.gen_zahlenmauer),
    Topic("geld", "mathe", "Geld & Einkaufen", "💶", gen=mathe.gen_geld, desc="Münzen, Preise, Rückgeld"),
    Topic("uhr", "mathe", "Uhrzeit", "🕒", gen=mathe.gen_uhr, desc="Uhr lesen und Zeitspannen"),
    Topic("groessen", "mathe", "Längen & Größen", "📏", gen=mathe.gen_groessen, desc="cm, m, kg, Liter"),
    Topic("sachaufgaben", "mathe", "Rechengeschichten", "🛒", gen=mathe.gen_sachaufgaben, desc="Mathe im Alltag"),
    Topic("formen", "mathe", "Formen & Geometrie", "🔺", gen=mathe.gen_formen),
    Topic("schriftlich", "mathe", "Schriftlich rechnen", "📝", 3, gen=mathe.gen_schriftlich),
    Topic("blitz", "mathe", "Blitzrechnen & Fokus", "⚡", gen=fokus.gen_fokus_mathe,
          desc="Aufgaben blitzen nur kurz auf", fokus=True),
    Topic("knobeln", "mathe", "Knobeln & Logik", "🧩", gen=knobeln.gen_knobeln,
          desc="Symbol-Rätsel, Sudoku, magische Quadrate", special=True),
    # Heimat & Sachkunde
    Topic("koerper", "sach", "Mein Körper", "🧍", gen=sachkunde.make_gen("koerper"), desc="Sinne, Zähne, Gesundheit"),
    Topic("tiere", "sach", "Tiere", "🦔", gen=sachkunde.make_gen("tiere")),
    Topic("pflanzen", "sach", "Pflanzen & Wald", "🌳", gen=sachkunde.make_gen("pflanzen")),
    Topic("jahr", "sach", "Kalender & Jahreszeiten", "📅", gen=sachkunde.make_gen("jahr")),
    Topic("wetter", "sach", "Wetter & Wasser", "🌦️", gen=sachkunde.make_gen("wetter")),
    Topic("verkehr", "sach", "Verkehr & Schulweg", "🚦", gen=sachkunde.make_gen("verkehr")),
    Topic("heimat", "sach", "Heimat & Bayern", "🗺️", gen=sachkunde.make_gen("heimat"), desc="Himmelsrichtungen, Karte"),
    Topic("umwelt", "sach", "Umwelt & Müll", "♻️", gen=sachkunde.make_gen("umwelt")),
    Topic("technik", "sach", "Technik & Stoffe", "🧲", gen=sachkunde.make_gen("technik"), desc="Magnet, Strom, Wasser"),
    Topic("berufe", "sach", "Berufe & Miteinander", "🧑‍🚒", gen=sachkunde.make_gen("berufe")),
    Topic("genau", "sach", "Genau hinsehen", "🔍", gen=fokus.gen_fokus_sach,
          desc="Fotos und Fakten merken", fokus=True),
    Topic("forscher", "sach", "Forscherfragen", "🔭", gen=sachkunde.make_gen("forscher"),
          desc="Weltall, Dinos, Naturwissenschaft", special=True),
    Topic("entdecken", "sach", "Entdecken (Internet)", "📡", kind="online", desc="Kinderlexikon: Neues entdecken"),
    # Konzentration
    Topic("fehlerbild", "konz", "Fehlerbild", "🔎", kind="game", desc="Finde die Unterschiede im echten Foto"),
    Topic("schulte", "konz", "Zahlen-Jagd", "🎯", kind="game", desc="Tippe die Zahlen der Reihe nach"),
    Topic("zahlenmerken", "konz", "Zahlen merken", "🧠", kind="game", desc="Merke dir die Zahlenreihe"),
    Topic("memory", "konz", "Memory", "🃏", kind="game", desc="Finde die Paare"),
    Topic("detektiv", "konz", "Buchstaben-Detektiv", "🔍", kind="game", desc="Finde alle b – aber nicht d!"),
    Topic("farben", "konz", "Farben-Falle", "🎨", kind="game", desc="Welche Farbe hat das Wort?"),
    Topic("zaehlen", "konz", "Zähl genau", "🐞", gen=konz.gen_zaehlen),
    Topic("anders", "konz", "Was ist anders?", "👀", gen=konz.gen_anders, desc="Echte Fotos genau vergleichen"),
    Topic("merken", "konz", "Bilder merken", "🖼️", gen=konz.gen_merken),
    Topic("rechenkette", "konz", "Rechenkette hören", "🎧", gen=konz.gen_rechenkette),
]

BY_ID = {(t.subject, t.id): t for t in TOPICS}
BY_SKILL = {t.skill: t for t in TOPICS}


def topics_for(subject: str, grade: int, kinds=("tasks", "game", "online")):
    return [t for t in TOPICS if t.subject == subject and t.min_g <= grade <= t.max_g and t.kind in kinds]


def effective(grade: int, level: int) -> tuple:
    """Stufe 1–5 = Stoff der eigenen Klasse, Stufe 6–8 = Profi (Stoff der nächsten Klasse)."""
    if level <= 5:
        return grade, level
    if grade < 4:
        return grade + 1, level - 3
    return 4, 5


SPECIAL_FOR = {"mathe": "knobeln", "deutsch": "raetsel", "sach": "forscher", "konz": "knobeln", "mix": "knobeln"}


FOKUS_FOR = {"deutsch": "fokus", "mathe": "blitz", "sach": "genau"}


def fokus_topic(subject: str) -> Topic:
    tid = FOKUS_FOR.get(subject) or random.choice(list(FOKUS_FOR.values()))
    return next(t for t in TOPICS if t.id == tid)


def special_topic(subject: str) -> Topic:
    tid = SPECIAL_FOR.get(subject, "knobeln")
    return next(t for t in TOPICS if t.id == tid)


def generate(topic: Topic, grade: int, level: int) -> list:
    """Erzeugt eine oder mehrere Aufgaben (z. B. Lesetext mit mehreren Fragen)."""
    g_eff, l_eff = effective(grade, level)
    for _ in range(5):
        try:
            res = topic.gen(g_eff, l_eff)
        except (ValueError, IndexError, StopIteration, KeyError):
            continue  # seltener Zufallsfall ohne gültige Zahlen → neu würfeln
        tasks = res if isinstance(res, list) else [res]
        for t in tasks:
            t.skill = topic.skill
            t.subject = topic.subject
        return tasks
    return []


def review(concept: dict, avoid: str):
    """Wiederholung einer schwierigen Aufgabe in einer anderen Form."""
    kind = concept.get("kind")
    if kind == "arith":
        return mathe.review_arith(concept, avoid)
    if kind == "word":
        return deutsch.review_word(concept, avoid)
    if kind == "fact":
        return sachkunde.review_fact(concept, avoid)
    return None


def random_topic(subject: str, grade: int) -> Topic:
    return random.choice(topics_for(subject, grade, ("tasks",)))
