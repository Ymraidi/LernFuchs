# 🦊 LernFuchs – Lern-App für die Grundschule (Klasse 2–4)

## Starten
Doppelklick auf **`LernFuchs starten.bat`** (installiert beim ersten Mal die Pakete)
oder im Terminal:
```
python -m pip install -r requirements.txt
python main.py
```

## Inhalte
| Fach | Themen |
|---|---|
| 📖 Deutsch | Lesen & Verstehen, Hör genau hin, Diktat, Rechtschreibung, Buchstaben-Puzzle, Wortschatz, Artikel & Mehrzahl, Wortarten, ABC & Silben, Verben & Zeitformen |
| 🔢 Mathe | Plus & Minus, Mal & Geteilt, Verdoppeln, Zahlen & Vergleichen, Muster, Zahlenmauern, Geld, Uhrzeit, Längen & Größen, Rechengeschichten, Formen, Schriftlich (ab Kl. 3) |
| 🌍 HSU | Körper, Tiere, Pflanzen, Kalender, Wetter & Wasser, Verkehr, Heimat & Bayern, Umwelt & Müll, Technik, Berufe, Entdecken (Klexikon, online) |
| 🧠 Konzentration | Zahlen-Jagd, Zahlen merken, Memory, Buchstaben-Detektiv, Farben-Falle, Zähl genau, Was ist anders?, Bilder merken, Rechenkette hören |

## Android-Tablet-Version (Ordner `android/`)
- Gleiche Aufgaben, Stufen und Fehlerbox wie am PC. Der Kern wird mit `android/tools/sync_core.py` übernommen.
- Design „Kreisel-Arena“: eigener Battle-Kreisel (auf der Startseite antippen zum Wechseln), Kampf gegen einen Rivalen mit Ausdauer-Balken, „3-2-1 – Let it rip!“ und Burst-Sieg. Im Elternbereich lässt sich das Design auf „Modern“ umstellen.
- Sprache über die Android-Sprachausgabe (Google, Deutsch, offline). 3D-Bilder, Animationen und Fotos sind in der App enthalten.
- **APK bauen:** Das Projekt auf GitHub hochladen (`git push`). Unter „Actions“ baut GitHub die App automatisch (erster Lauf ca. 20–40 Minuten). Danach unter „Artifacts“ **LernFuchs-APK** herunterladen, aufs Tablet kopieren und installieren („Unbekannte Apps zulassen“).
- Am PC testen: `cd android`, `python tools/sync_core.py`, `python main.py`.

## Neu in Version 3
- **Schneller:** Die App läuft von der lokalen Festplatte (der Starter kopiert sie automatisch von H:), Daten liegen unter `%LOCALAPPDATA%\LernFuchs`. Das Profil wird beim Beenden in `daten\sicherung` gesichert. Die nächste Aufgabe und ihre Sprachausgabe werden im Voraus vorbereitet.
- **Natürlichere Stimme:** Florian (Microsoft Neural). Aufgaben werden natürlich formuliert („Wie viel ist 7 mal 8?“), Emojis werden als Wort vorgelesen. Zum Rundenende gibt es eine persönliche, wechselnde Rückmeldung.
- **Animationen:** animierte 3D-Emojis (Microsoft Fluent) bei Erfolg, Fehlern, Level-up, Boss und Pokal. Dazu realistische 3D-Symbole, hereingleitende Aufgaben, Kopfschütteln bei Fehlern, fliegende XP und hochzählende Punkte.
- **Konzentration in allen Fächern:** Wort-Blitz & Fokus (Deutsch), Blitzrechnen & Fokus (Mathe), Genau hinsehen mit Foto-Merkspiel (Sachkunde). Außerdem kommt in jeder Runde regelmäßig eine 🎯 Fokus-Aufgabe.
- **Fehler behoben:** Memory mit doppelten Bildern, ich-Form bei „klettern“, zu ähnlich klingende Hörpaare, mehrdeutige Oberbegriffe. Groß-/Kleinschreibung zählt nur noch bei Rechtschreibaufgaben.

## Neu in Version 2
- **Männliche Stimme:** Conrad (natürliche Online-Stimme, wird zwischengespeichert). Ohne Internet übernimmt automatisch Stefan (offline).
- **Stufen 1–8, die sich immer anpassen:** 1–5 = Stoff der eigenen Klasse, 6–8 = PROFI (Stoff der nächsten Klasse). In den ersten Aufgaben eines Themas geht die Stufe besonders schnell hoch.
- **Sonderaufgaben:** Knobeln & Logik (Symbol-Rätsel, Mini-Sudoku, magische Quadrate, Trickfragen), Rätsel & Geheimschrift, Forscherfragen (Weltall, Dinos, Physik).
- **Boss-Aufgabe** am Ende jeder Runde, Blitz-Bonus für schnelle richtige Antworten, XP und Ränge von „Einsteiger“ bis „Legende“.
- **Echte Fotos:** Fehlerbild (Unterschiede finden) und „Was ist anders?“. Die Fotos stammen aus dem Klexikon bzw. von Wikimedia Commons, werden einmal geladen und liegen dann offline vor.
- **Modernes dunkles Design** (im Elternbereich auf „Hell“ umstellbar).

## Pädagogisches Konzept
- **Adaptiv:** 8 Stufen pro Thema. Die Stufe steigt und sinkt automatisch mit dem Lernerfolg. Eltern legen nur eine Mindeststufe fest.
- **Sanduhr** pro Aufgabe (je Fach einstellbar). Bei längeren Aufgaben läuft sie automatisch länger.
- **Wiederholung in anderer Form:** Fehler kommen noch in derselben Runde und an späteren Tagen (nach 1, 3 und 7 Tagen) in anderer Form wieder dran.
- **Motivation:** Sterne, Serien-Bonus, Sticker-Album, Tagesziel, Tage in Folge.
- **Bewegungspausen** zwischendurch fördern die Konzentration.

## Elternbereich
Über 🔒 oben rechts, geschützt durch eine Rechenaufgabe. Dort gibt es Einstellungen, den Fortschritt je Thema und die Fehlerbox.

## Erweitern
- Neue HSU-Fragen: `lernfuchs/content/sach_data.py`. Eine Zeile pro Frage: `Klasse|Frage|richtig|falsch;falsch|Emoji|Erklärung`
- Neue Lesetexte oder Wörter: `lernfuchs/content/deutsch_data.py`
- Neue Mathe-Aufgabentypen: `lernfuchs/content/mathe.py`, dann in `content/topics.py` eintragen

Alle Daten werden lokal im Ordner `daten/` gespeichert.
