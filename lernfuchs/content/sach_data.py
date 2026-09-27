"""Fragen für Heimat- und Sachkunde (HSU).

Format je Zeile: ab Klasse | Frage | richtige Antwort | falsch;falsch(;falsch) | Emoji | Erklärung (optional)
Eigene Fragen (z. B. zu eurem Wohnort) können einfach als neue Zeile ergänzt werden.
"""

RAW = {
    "koerper": """
2|Mit welchem Sinnesorgan riechst du?|Mit der Nase|Mit den Ohren;Mit der Zunge|👃|
2|Mit welchem Sinnesorgan hörst du?|Mit den Ohren|Mit den Augen;Mit der Nase|👂|
2|Mit welchem Sinnesorgan schmeckst du?|Mit der Zunge|Mit den Ohren;Mit den Fingern|👅|
2|Wie viele Sinne hat der Mensch?|Fünf|Drei;Zehn|🧠|Sehen, Hören, Riechen, Schmecken und Tasten.
2|Was pumpt das Blut durch deinen Körper?|Das Herz|Die Lunge;Der Magen|❤️|
2|Womit atmest du?|Mit der Lunge|Mit dem Herzen;Mit dem Magen|🌬️|
2|Wie oft am Tag solltest du Zähne putzen?|Zweimal – morgens und abends|Einmal in der Woche;Nur nach Süßigkeiten|🪥|
2|Wie heißen die ersten Zähne eines Kindes?|Milchzähne|Babyzähne;Weichzähne|🦷|
2|Was ist gut für deine Zähne?|Äpfel und Karotten|Gummibärchen;Limonade|🍎|
2|Wie viele Stunden Schlaf braucht ein Kind in deinem Alter ungefähr?|10 bis 11 Stunden|4 Stunden;20 Stunden|😴|
2|Was solltest du vor dem Essen tun?|Hände waschen|Fernsehen;Schuhe putzen|🧼|
2|Welches Getränk löscht den Durst am besten?|Wasser|Cola;Limonade|💧|
3|Wie viele Zähne hat ein Erwachsener normalerweise?|32|20;50|🦷|Kinder haben 20 Milchzähne, Erwachsene 32 Zähne.
3|Wie viele Knochen hat ein Erwachsener ungefähr?|Etwa 200|Etwa 20;Etwa 2000|🦴|Genau sind es meist 206 Knochen.
3|Wie heißt das größte Organ des Menschen?|Die Haut|Das Herz;Die Leber|🖐️|
3|Warum ist Bewegung wichtig?|Damit Muskeln und Knochen stark bleiben|Damit die Haare wachsen;Damit man nicht trinken muss|🏃|
3|Was sollte man nur selten essen?|Süßigkeiten|Gemüse;Vollkornbrot|🍭|Süßes steht ganz oben in der Ernährungspyramide.
""",
    "tiere": """
2|Welches Tier hält einen Winterschlaf?|Der Igel|Der Hase;Das Reh|🦔|
2|Wie nennt man ein junges Pferd?|Fohlen|Kalb;Ferkel|🐴|
2|Wie nennt man ein junges Schwein?|Ferkel|Welpe;Lamm|🐷|
2|Wie nennt man einen jungen Hund?|Welpe|Kitz;Küken|🐶|
2|Wie nennt man ein junges Schaf?|Lamm|Fohlen;Kalb|🐑|
2|Wie viele Beine hat eine Spinne?|Acht|Sechs;Vier|🕷️|
2|Wie viele Beine hat ein Insekt?|Sechs|Acht;Vier|🐞|Käfer, Bienen und Ameisen sind Insekten.
2|Was frisst eine Kuh?|Gras und Heu|Fleisch;Fische|🐮|
2|Welches Tier legt Eier?|Das Huhn|Die Kuh;Die Katze|🐔|
2|Wo lebt der Maulwurf?|Unter der Erde|Im Baum;Im Wasser|🕳️|
2|Woraus wird ein Frosch?|Aus einer Kaulquappe|Aus einer Raupe;Aus einem Küken|🐸|
2|Woraus wird ein Schmetterling?|Aus einer Raupe|Aus einer Kaulquappe;Aus einer Blüte|🦋|
2|Welcher Vogel kann nicht fliegen?|Der Pinguin|Die Amsel;Der Spatz|🐧|
2|Wie heißt das Männchen vom Huhn?|Der Hahn|Der Erpel;Der Bock|🐓|
2|Wann ist die Eule meistens unterwegs?|Nachts|Mittags;Morgens|🦉|
2|Welches Tier ist ein Säugetier?|Der Hund|Der Frosch;Die Amsel|🐶|Säugetier-Babys trinken Milch bei ihrer Mutter.
3|Welches Tier ist KEIN Fisch?|Der Wal|Der Hai;Die Forelle|🐳|Wale sind Säugetiere und atmen Luft.
3|Wie nennt man Tiere, die nur Pflanzen fressen?|Pflanzenfresser|Fleischfresser;Allesfresser|🐰|
3|Wie atmen Fische?|Mit Kiemen|Mit einer Lunge;Mit der Nase|🐟|
3|Wohin fliegen Schwalben im Herbst?|Nach Afrika|In den Keller;Zum Nordpol|🐦|Zugvögel fliegen in den warmen Süden.
3|Was frisst ein Eichhörnchen gern?|Nüsse und Samen|Fische;Gras|🐿️|
""",
    "pflanzen": """
2|Was braucht eine Pflanze zum Wachsen?|Licht, Wasser und Erde|Nur Dunkelheit;Süßigkeiten|🌱|
2|Welcher Baum trägt Nadeln?|Die Tanne|Die Eiche;Die Buche|🌲|
2|An welchem Baum wachsen Eicheln?|An der Eiche|An der Tanne;An der Birke|🌳|
2|Wie heißen die Teile der Pflanze unter der Erde?|Wurzeln|Blüten;Blätter|🌱|
2|Welche Blume blüht schon ganz früh im Jahr, manchmal im Schnee?|Das Schneeglöckchen|Die Sonnenblume;Die Rose|🌼|
2|Wann verlieren Laubbäume ihre Blätter?|Im Herbst|Im Sommer;Im Frühling|🍂|
2|Was ist KEIN Obst?|Die Karotte|Der Apfel;Die Kirsche|🥕|
3|Wie nennt man Blumen, die als Erste im Jahr blühen?|Frühblüher|Spätblüher;Winterblumen|🌷|
3|Was machen Bienen an den Blüten?|Sie sammeln Nektar und bestäuben die Blüten|Sie fressen die Blätter;Sie bauen dort Nester|🐝|
3|Woraus entsteht die Frucht einer Pflanze?|Aus der Blüte|Aus der Wurzel;Aus dem Stängel|🌸|
3|Wie nennt man den oberen Teil eines Baumes mit Ästen und Blättern?|Die Baumkrone|Der Stamm;Die Wurzel|🌳|
4|Was stellen Pflanzen mit Sonnenlicht in ihren Blättern her?|Nährstoffe und Sauerstoff|Wasser;Erde|🍃|
""",
    "jahr": """
2|Wie viele Tage hat eine Woche?|Sieben|Fünf;Zehn|📅|
2|Wie viele Monate hat ein Jahr?|Zwölf|Zehn;Vierzehn|📅|
2|Welcher Tag kommt nach Mittwoch?|Donnerstag|Dienstag;Freitag|📅|
2|Welcher Tag kommt vor Sonntag?|Samstag|Montag;Freitag|📅|
2|Welcher Monat ist der erste im Jahr?|Januar|Dezember;März|🎆|
2|In welcher Jahreszeit ist Weihnachten?|Im Winter|Im Sommer;Im Herbst|🎄|
2|In welcher Jahreszeit ist es meistens am heißesten?|Im Sommer|Im Winter;Im Herbst|☀️|
2|Wie viele Jahreszeiten gibt es?|Vier|Zwei;Sechs|🍂|
2|Welcher Monat kommt nach April?|Mai|März;Juni|🌷|
2|In welchem Monat beginnt der Frühling?|Im März|Im Juli;Im November|🌷|
2|Welche Tage gehören zum Wochenende?|Samstag und Sonntag|Montag und Dienstag;Freitag und Montag|🛌|
3|Wie viele Tage hat ein Jahr (ohne Schaltjahr)?|365|100;500|📅|
3|Welcher Monat hat nur 28 oder 29 Tage?|Februar|Januar;April|📅|
3|Welcher Monat ist der letzte im Jahr?|Dezember|November;Januar|🎄|
""",
    "wetter": """
2|Was zeigt ein Thermometer an?|Die Temperatur|Die Uhrzeit;Die Windrichtung|🌡️|
2|Was kann man sehen, wenn Sonne und Regen gleichzeitig da sind?|Einen Regenbogen|Ein Gewitter;Nebel|🌈|
2|Was ist gefrorenes Wasser?|Eis|Dampf;Nebel|🧊|
2|Bei wie viel Grad gefriert Wasser?|Bei 0 Grad|Bei 100 Grad;Bei 20 Grad|❄️|
2|Was solltest du bei Gewitter NICHT tun?|Unter einem einzelnen Baum stehen|Ins Haus gehen;Im Auto bleiben|⛈️|
2|Was bemerkt man bei einem Gewitter zuerst?|Den Blitz|Den Donner;Den Regenbogen|⚡|Licht ist viel schneller als Schall.
2|Warum sollen wir Wasser sparen?|Weil sauberes Wasser kostbar ist|Weil Wasser giftig ist;Weil Wasser dick macht|🚰|
3|Bei wie viel Grad kocht Wasser?|Bei 100 Grad|Bei 50 Grad;Bei 0 Grad|♨️|
3|Wie nennt man es, wenn Wasser zu Dampf wird?|Verdunsten|Gefrieren;Schmelzen|💨|
3|Welche Zustände kann Wasser haben?|Fest, flüssig und gasförmig|Nur flüssig;Hart und weich|💧|
3|Woraus besteht eine Wolke?|Aus winzigen Wassertröpfchen|Aus Rauch;Aus Watte|☁️|
3|Wie nennt man es, wenn Eis zu Wasser wird?|Schmelzen|Verdunsten;Frieren|🧊|
""",
    "verkehr": """
2|Was bedeutet eine rote Ampel?|Stehen bleiben|Schnell laufen;Losgehen|🚦|
2|Was bedeutet eine grüne Fußgängerampel?|Gehen – aber vorher trotzdem schauen|Stehen bleiben;Rennen, ohne zu schauen|🚦|
2|Wo gehst du am sichersten über die Straße?|An der Ampel oder am Zebrastreifen|Zwischen parkenden Autos;In einer Kurve|🚸|
2|Wohin schaust du, bevor du über die Straße gehst?|Links, rechts und nochmal links|Nur nach oben;Nur auf den Boden|👀|
2|Was trägst du beim Fahrradfahren immer?|Einen Helm|Eine Mütze;Eine Sonnenbrille|⛑️|
2|Welche Farbe hat ein Stoppschild?|Rot|Blau;Gelb|🛑|
2|Welche Form hat ein Stoppschild?|Ein Achteck|Ein Kreis;Ein Dreieck|🛑|
2|Warum trägst du im Dunkeln helle Kleidung oder Reflektoren?|Damit Autofahrer dich gut sehen|Damit du schneller bist;Weil es wärmer ist|🦺|
2|Ein Ball rollt auf die Straße. Was machst du?|Stehen bleiben und schauen|Sofort hinterherrennen;Die Augen zumachen|⚽|
2|Welche Nummer rufst du bei Feuer oder einem Unfall an?|112|123;555|🚑|
2|Welche Nummer hat die Polizei?|110|123;555|🚓|
3|Was braucht ein verkehrssicheres Fahrrad?|Klingel, Licht und Bremsen|Eine Fahne;Einen Korb|🚲|
3|Wie heißt der gestreifte Überweg für Fußgänger?|Zebrastreifen|Tigerstreifen;Fahrradweg|🦓|
3|Ab welchem Alter müssen Kinder mit dem Rad auf der Straße oder dem Radweg fahren?|Ab 10 Jahren|Ab 4 Jahren;Ab 18 Jahren|🚲|Bis 8 Jahre müssen Kinder auf dem Gehweg fahren.
""",
    "heimat": """
2|Wie heißt unser Land?|Deutschland|Frankreich;Italien|🗺️|
2|Wie heißt die Hauptstadt von Deutschland?|Berlin|München;Hamburg|🏛️|
2|Wie heißt die Hauptstadt von Bayern?|München|Nürnberg;Augsburg|🏰|
2|Welche Farben hat die Flagge von Deutschland?|Schwarz, Rot, Gold|Blau, Weiß, Rot;Grün, Weiß, Rot|🏳️|
2|Wo geht die Sonne auf?|Im Osten|Im Westen;Im Norden|🌅|
2|Wo geht die Sonne unter?|Im Westen|Im Osten;Im Süden|🌇|
2|Wie viele Haupt-Himmelsrichtungen gibt es?|Vier|Zwei;Acht|🧭|Norden, Osten, Süden und Westen.
2|Womit findet man die Himmelsrichtungen?|Mit einem Kompass|Mit einem Thermometer;Mit einer Waage|🧭|
2|Wer leitet eine Stadt oder Gemeinde?|Der Bürgermeister oder die Bürgermeisterin|Die Lehrerin;Der Bäcker|🏛️|
3|Wo ist auf einer Landkarte meistens Norden?|Oben|Unten;Links|🗺️|
3|Wie heißt der höchste Berg Deutschlands?|Die Zugspitze|Der Watzmann;Der Feldberg|🏔️|
3|Welcher große Fluss fließt quer durch Bayern?|Die Donau|Die Elbe;Die Weser|🌊|
3|Welches Gebirge liegt im Süden Bayerns?|Die Alpen|Der Harz;Die Pyrenäen|🏔️|
3|Was erklärt die Legende auf einer Landkarte?|Was die Zeichen und Farben bedeuten|Eine alte Sage;Wie alt die Karte ist|🗺️|
3|In welcher Stadt findet das Oktoberfest statt?|In München|In Berlin;In Nürnberg|🎡|
3|Welche Farben hat die bayerische Flagge?|Weiß und Blau|Rot und Weiß;Grün und Gelb|🔷|
4|Wie viele Bundesländer hat Deutschland?|16|12;20|🗺️|
4|Welches ist das größte Bundesland Deutschlands?|Bayern|Berlin;Hessen|🗺️|
4|Wie heißt die Hauptstadt von Österreich?|Wien|Salzburg;Bern|🏰|
""",
    "umwelt": """
2|Warum trennen wir Müll?|Damit man ihn wiederverwerten kann|Damit er schöner aussieht;Weil er dann leichter ist|♻️|
2|Was bedeutet dieses Zeichen: ♻️?|Recycling – wiederverwerten|Gefahr;Nicht berühren|♻️|
2|Wie kannst du Müll vermeiden?|Eine Brotdose statt Alufolie benutzen|Alles in Plastik einpacken;Viel mehr kaufen|🍱|
2|Was gehört in die Biotonne?|Obst- und Gemüsereste|Batterien;Plastikflaschen|🍌|
2|Wohin gehören alte Batterien?|In eine Sammelbox im Geschäft|In den Restmüll;In die Biotonne|🔋|
3|Wie lange braucht eine Plastikflasche, bis sie in der Natur zerfällt?|Hunderte Jahre|Eine Woche;Ein Jahr|🧴|
3|Womit sparst du Energie?|Licht ausmachen, wenn du den Raum verlässt|Im Winter das Fenster offen lassen;Den Fernseher immer anlassen|💡|
3|Was ist Pfand?|Geld, das man für zurückgebrachte Flaschen bekommt|Eine Strafe;Ein Spielzeug|🍾|
""",
    "technik": """
2|Was schwimmt im Wasser?|Ein Korken|Ein Stein;Ein Schlüssel|🍾|
2|Was geht im Wasser unter?|Ein Stein|Ein Blatt;Ein Korken|🪨|
2|Was misst eine Waage?|Das Gewicht|Die Länge;Die Zeit|⚖️|
2|Woraus wird Papier hergestellt?|Aus Holz|Aus Stein;Aus Plastik|📄|
2|Woraus wird Wolle gemacht?|Aus dem Fell von Schafen|Aus Blättern;Aus Steinen|🐑|
3|Was zieht ein Magnet an?|Gegenstände aus Eisen|Holz;Plastik|🧲|
3|Wie heißen die zwei Enden eines Magneten?|Nordpol und Südpol|Anfang und Ende;Oben und unten|🧲|
3|Was passiert, wenn zwei gleiche Magnetpole zueinander zeigen?|Sie stoßen sich ab|Sie ziehen sich an;Sie werden heiß|🧲|
3|Was leitet Strom gut?|Metall|Holz;Gummi|⚡|
3|Warum darfst du nie etwas in eine Steckdose stecken?|Strom ist lebensgefährlich|Die Steckdose geht kaputt;Es wird laut|🔌|
3|Was braucht ein Feuer zum Brennen?|Brennstoff, Luft und Hitze|Nur Wasser;Nur Sand|🔥|
3|Womit löscht man brennendes Öl in einer Pfanne?|Mit einem Deckel|Mit Wasser;Mit Pusten|🍳|Niemals Wasser auf brennendes Öl!
3|Was braucht eine Lampe, damit sie leuchtet?|Einen geschlossenen Stromkreis|Wasser;Einen Magneten|💡|
3|Woraus wird Glas hergestellt?|Aus Sand|Aus Holz;Aus Wolle|🥛|
""",
    "berufe": """
2|Wer backt Brot und Brezen?|Der Bäcker|Der Metzger;Der Maler|🥖|
2|Wer hilft, wenn es brennt?|Die Feuerwehr|Die Post;Der Friseur|🚒|
2|Wer behandelt kranke Tiere?|Die Tierärztin|Die Zahnärztin;Die Pilotin|🐶|
2|Wer schneidet Haare?|Der Friseur|Der Schreiner;Der Koch|💇|
2|Wer baut Möbel aus Holz?|Der Schreiner|Der Bäcker;Der Gärtner|🪚|
2|Wer bringt Briefe und Pakete?|Die Postbotin|Die Polizistin;Die Ärztin|📬|
2|Wer fliegt ein Flugzeug?|Die Pilotin|Der Kapitän;Der Lokführer|✈️|
2|Wer hilft bei Zahnschmerzen?|Der Zahnarzt|Der Tierarzt;Der Bäcker|🦷|
2|Was hilft, wenn man sich streitet?|Ruhig reden und einander zuhören|Laut schreien;Hauen|🤝|
2|Ein Kind steht allein auf dem Pausenhof. Was tust du?|Fragen, ob es mitspielen will|Es auslachen;Weglaufen|🤗|
3|Wie nennt man Regeln, die für alle in der Klasse gelten?|Klassenregeln|Hausaufgaben;Stundenplan|📋|
3|Wie heißt das Kind, das die Klasse bei Wahlen vertritt?|Klassensprecher|Klassenchef;Hausmeister|🗳️|
""",
    "forscher": """
2|Welcher Planet ist der größte in unserem Sonnensystem?|Jupiter|Mars;Erde;Merkur|🪐|In den Jupiter würde die Erde über 1000-mal hineinpassen.
2|Wie viele Planeten kreisen um unsere Sonne?|Acht|Neun;Zwölf;Fünf|🪐|Merkur, Venus, Erde, Mars, Jupiter, Saturn, Uranus, Neptun.
2|Welcher Planet wird „der Rote Planet“ genannt?|Mars|Venus;Saturn|🔴|Sein Boden enthält viel rostiges Eisen.
2|Was ist die Sonne?|Ein Stern|Ein Planet;Ein Mond|☀️|Die Sonne ist ein ganz normaler Stern – nur sehr nah.
2|Wie lange braucht die Erde für eine Runde um die Sonne?|Ein Jahr|Einen Tag;Einen Monat|🌍|
2|Warum sehen wir den Mond leuchten?|Die Sonne strahlt ihn an|Er hat eigene Lampen;Er brennt|🌙|Der Mond leuchtet nicht selbst.
3|Wie weit ist der Mond ungefähr von der Erde entfernt?|384.000 km|3.840 km;38 km|🌙|Ein Auto bräuchte ohne Pause etwa ein halbes Jahr.
3|Wer betrat 1969 als erster Mensch den Mond?|Neil Armstrong|Albert Einstein;Christoph Kolumbus|👨‍🚀|
3|Wie heißt unsere Galaxie?|Die Milchstraße|Der Große Wagen;Der Sternhaufen|🌌|
2|Welches ist das größte Tier der Welt?|Der Blauwal|Der Elefant;Die Giraffe|🐋|Ein Blauwal kann über 30 Meter lang werden.
2|Welches ist das schnellste Landtier?|Der Gepard|Der Löwe;Das Pferd|🐆|Geparden schaffen über 100 km/h – aber nur kurz.
3|Wie viele Herzen hat ein Oktopus (Krake)?|Drei|Eins;Acht|🐙|Und sein Blut ist blau!
3|Wie viele Halswirbel hat eine Giraffe?|Sieben – so viele wie der Mensch|Fünfzig;Zwei|🦒|Ihre Wirbel sind nur viel länger.
2|Welcher Dinosaurier war ein riesiger Fleischfresser?|Tyrannosaurus rex|Triceratops;Brachiosaurus|🦖|
3|Wann starben die Dinosaurier aus?|Vor etwa 66 Millionen Jahren|Vor 100 Jahren;Vor 2000 Jahren|🦕|Wahrscheinlich nach einem riesigen Meteoriten-Einschlag.
3|Was ist ein Fossil?|Versteinerte Überreste von Lebewesen|Ein seltener Edelstein;Ein altes Werkzeug|🦴|
2|Welches Tier kann seinen Schwanz abwerfen, um zu fliehen?|Die Eidechse|Der Hund;Das Pferd|🦎|Der Schwanz wächst wieder nach.
2|Welche Farbe entsteht, wenn man Blau und Gelb mischt?|Grün|Lila;Orange|🎨|
2|Welche Farbe entsteht aus Rot und Gelb?|Orange|Grün;Braun|🎨|
3|Was zieht alle Dinge zur Erde hin?|Die Schwerkraft|Der Wind;Der Nordpol|🍎|Deshalb fällt ein Apfel nach unten.
3|Warum ist der Himmel blau?|Die Luft streut das blaue Sonnenlicht am stärksten|Das Meer spiegelt sich darin;Die Luft ist blau gefärbt|🌤️|
3|Wie schnell ist Licht ungefähr?|300.000 km pro Sekunde|300 km pro Stunde;3 km pro Sekunde|💡|In einer Sekunde käme es fast 8-mal um die Erde.
3|Warum schwimmt ein riesiges Schiff aus Stahl?|Es verdrängt viel Wasser und ist innen voller Luft|Stahl ist leichter als Wasser;Die Motoren halten es oben|🚢|
3|Was ist ein Vulkan?|Ein Berg, aus dem heiße Lava kommen kann|Ein sehr hoher Baum;Eine Gewitterwolke|🌋|
2|Welcher ist der höchste Berg der Welt?|Der Mount Everest|Die Zugspitze;Der Kilimandscharo|🏔️|Er ist fast 8.849 Meter hoch.
2|Wie heißt der größte Ozean?|Der Pazifik|Der Atlantik;Die Nordsee|🌊|
2|Auf welchem Kontinent liegt Deutschland?|Europa|Afrika;Asien|🌍|
3|Wie viele Kontinente gibt es?|Sieben|Drei;Zwölf|🗺️|Afrika, Antarktika, Asien, Australien, Europa, Nord- und Südamerika.
4|Woraus besteht die Luft hauptsächlich?|Aus Stickstoff|Aus Sauerstoff;Aus Wasserdampf|💨|Etwa 78 % Stickstoff, 21 % Sauerstoff.
2|Welches Gas brauchen wir zum Atmen?|Sauerstoff|Helium;Rauch|🫁|
3|Was erfand Johannes Gutenberg?|Den Buchdruck mit beweglichen Buchstaben|Das Telefon;Das Auto|📜|Das war um 1450 in Mainz.
3|Wie viele Beine hat ein Tausendfüßer meistens?|Viel weniger als 1000|Genau 1000;Genau 100|🐛|Die meisten haben zwischen 30 und 400 Beine.
2|Was passiert mit Wasser im Gefrierfach?|Es wird zu Eis und dehnt sich aus|Es verdunstet;Es wird kleiner|🧊|Darum platzen volle Glasflaschen im Gefrierfach!
3|Womit atmen Wale?|Mit einer Lunge – sie tauchen zum Atmen auf|Mit Kiemen;Durch die Haut|🐳|
4|Wie lange braucht das Sonnenlicht bis zur Erde?|Etwa 8 Minuten|Eine Sekunde;Einen Tag|☀️|
""",
}

# Sortieraufgaben: (Thema, ab Klasse, Aufgabe, Kategorien, {Begriff: Kategorie}, {Begriff: Emoji})
SORTS = [
    ("umwelt", 2, "Wohin gehört der Müll?", ["Gelber Sack", "Papier", "Bio", "Glas", "Restmüll"],
     {"Joghurtbecher": "Gelber Sack", "Zeitung": "Papier", "Bananenschale": "Bio", "Marmeladenglas": "Glas",
      "Windel": "Restmüll", "Konservendose": "Gelber Sack", "Karton": "Papier", "Apfelrest": "Bio",
      "Glasflasche": "Glas", "Staubsaugerbeutel": "Restmüll", "Eierschalen": "Bio", "Milchtüte": "Gelber Sack"},
     {"Joghurtbecher": "🥣", "Zeitung": "📰", "Bananenschale": "🍌", "Marmeladenglas": "🫙", "Windel": "🧷",
      "Konservendose": "🥫", "Karton": "📦", "Apfelrest": "🍏", "Glasflasche": "🍾", "Staubsaugerbeutel": "🧹",
      "Eierschalen": "🥚", "Milchtüte": "🧃"}),
    ("tiere", 2, "Welche Tiergruppe?", ["Säugetier", "Vogel", "Insekt", "Fisch"],
     {"Hund": "Säugetier", "Kuh": "Säugetier", "Wal": "Säugetier", "Amsel": "Vogel", "Adler": "Vogel",
      "Pinguin": "Vogel", "Biene": "Insekt", "Ameise": "Insekt", "Marienkäfer": "Insekt", "Forelle": "Fisch",
      "Hai": "Fisch", "Pferd": "Säugetier"},
     {"Hund": "🐶", "Kuh": "🐮", "Wal": "🐳", "Amsel": "🐦", "Adler": "🦅", "Pinguin": "🐧", "Biene": "🐝",
      "Ameise": "🐜", "Marienkäfer": "🐞", "Forelle": "🐟", "Hai": "🦈", "Pferd": "🐴"}),
    ("pflanzen", 2, "Laubbaum oder Nadelbaum?", ["Laubbaum", "Nadelbaum"],
     {"Eiche": "Laubbaum", "Buche": "Laubbaum", "Ahorn": "Laubbaum", "Birke": "Laubbaum", "Linde": "Laubbaum",
      "Kastanie": "Laubbaum", "Tanne": "Nadelbaum", "Fichte": "Nadelbaum", "Kiefer": "Nadelbaum", "Lärche": "Nadelbaum"},
     {"Tanne": "🌲", "Fichte": "🌲", "Kiefer": "🌲", "Lärche": "🌲", "Eiche": "🌳", "Buche": "🌳", "Ahorn": "🍁",
      "Birke": "🌳", "Linde": "🌳", "Kastanie": "🌰"}),
    ("wetter", 3, "Fest, flüssig oder gasförmig?", ["fest", "flüssig", "gasförmig"],
     {"Stein": "fest", "Eis": "fest", "Holz": "fest", "Milch": "flüssig", "Saft": "flüssig", "Öl": "flüssig",
      "Wasserdampf": "gasförmig", "Luft": "gasförmig"},
     {"Stein": "🪨", "Eis": "🧊", "Holz": "🪵", "Milch": "🥛", "Saft": "🧃", "Öl": "🫒", "Wasserdampf": "♨️",
      "Luft": "🌬️"}),
    ("technik", 2, "Schwimmt es oder geht es unter?", ["schwimmt", "geht unter"],
     {"Korken": "schwimmt", "Holzstück": "schwimmt", "Blatt": "schwimmt", "Gummiente": "schwimmt",
      "Stein": "geht unter", "Schlüssel": "geht unter", "Murmel": "geht unter", "Nagel": "geht unter"},
     {"Korken": "🍾", "Holzstück": "🪵", "Blatt": "🍃", "Gummiente": "🦆", "Stein": "🪨", "Schlüssel": "🔑",
      "Murmel": "🔵", "Nagel": "📌"}),
    ("technik", 3, "Zieht der Magnet es an?", ["ja", "nein"],
     {"Büroklammer": "ja", "Nagel": "ja", "Schraube": "ja", "Radiergummi": "nein", "Holzlöffel": "nein",
      "Glasmurmel": "nein", "Papier": "nein", "Wollfaden": "nein"},
     {"Büroklammer": "📎", "Nagel": "📌", "Schraube": "🔩", "Radiergummi": "🧽", "Holzlöffel": "🥄",
      "Glasmurmel": "🔮", "Papier": "📄", "Wollfaden": "🧶"}),
    ("koerper", 2, "Oft essen oder nur selten?", ["oft", "selten"],
     {"Gemüse": "oft", "Obst": "oft", "Wasser": "oft", "Vollkornbrot": "oft", "Chips": "selten",
      "Gummibärchen": "selten", "Limonade": "selten", "Pommes": "selten"},
     {"Gemüse": "🥦", "Obst": "🍎", "Wasser": "💧", "Vollkornbrot": "🍞", "Chips": "🍟", "Gummibärchen": "🍬",
      "Limonade": "🥤", "Pommes": "🍟"}),
    ("jahr", 2, "Welche Jahreszeit passt?", ["Frühling", "Sommer", "Herbst", "Winter"],
     {"Schneemann bauen": "Winter", "Im See baden": "Sommer", "Drachen steigen lassen": "Herbst",
      "Ostereier suchen": "Frühling", "Kastanien sammeln": "Herbst", "Schlitten fahren": "Winter",
      "Eis essen im Freibad": "Sommer", "Tulpen blühen": "Frühling"},
     {"Schneemann bauen": "⛄", "Im See baden": "🏊", "Drachen steigen lassen": "🪁", "Ostereier suchen": "🥚",
      "Kastanien sammeln": "🌰", "Schlitten fahren": "🛷", "Eis essen im Freibad": "🍦", "Tulpen blühen": "🌷"}),
]

# Reihenfolgen: (Thema, ab Klasse, Aufgabe, richtige Reihenfolge, Anzahl gezeigt oder 0 = alle, Emojis)
ORDERS = [
    ("jahr", 2, "Bringe die Wochentage in die richtige Reihenfolge!",
     ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"], 4, {}),
    ("jahr", 2, "Bringe die Jahreszeiten in die richtige Reihenfolge – beginne mit dem Frühling!",
     ["Frühling", "Sommer", "Herbst", "Winter"], 0,
     {"Frühling": "🌷", "Sommer": "☀️", "Herbst": "🍂", "Winter": "❄️"}),
    ("jahr", 2, "Bringe die Monate in die richtige Reihenfolge!",
     ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
      "November", "Dezember"], 4, {}),
    ("tiere", 2, "Wie wird aus dem Laich ein Frosch? Bringe in die richtige Reihenfolge!",
     ["Froschlaich", "Kaulquappe", "Kaulquappe mit Beinen", "Frosch"], 0, {"Frosch": "🐸"}),
    ("tiere", 2, "Wie entsteht ein Schmetterling? Bringe in die richtige Reihenfolge!",
     ["Ei", "Raupe", "Puppe", "Schmetterling"], 0, {"Raupe": "🐛", "Schmetterling": "🦋", "Ei": "🥚"}),
    ("pflanzen", 2, "Wie wächst ein Baum? Bringe in die richtige Reihenfolge!",
     ["Samen", "Keimling", "junger Baum", "großer Baum"], 0,
     {"Samen": "🌰", "Keimling": "🌱", "junger Baum": "🌿", "großer Baum": "🌳"}),
    ("wetter", 3, "Der Wasserkreislauf – was passiert nacheinander?",
     ["Wasser verdunstet", "Wolken bilden sich", "Es regnet", "Wasser fließt ins Meer"], 0,
     {"Wasser verdunstet": "☀️", "Wolken bilden sich": "☁️", "Es regnet": "🌧️", "Wasser fließt ins Meer": "🌊"}),
    ("heimat", 2, "Himmelsrichtungen im Uhrzeigersinn – beginne im Norden!",
     ["Norden", "Osten", "Süden", "Westen"], 0, {}),
]


def parse():
    out = {}
    for topic, block in RAW.items():
        rows = []
        for line in block.strip().splitlines():
            parts = line.split("|")
            if len(parts) < 5:
                continue
            g, q, r, w, e = parts[:5]
            x = parts[5] if len(parts) > 5 else ""
            rows.append({"g": int(g), "q": q, "r": r, "w": [s for s in w.split(";") if s], "e": e, "x": x})
        out[topic] = rows
    return out


FRAGEN = parse()
