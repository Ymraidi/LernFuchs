"""Wortschatz, Lesetexte und Diktatsätze für Deutsch (Klasse 2–4).

Nomen-Format: Artikel | Silben | Mehrzahl ("-" = keine) | Oberbegriff | ab Klasse | Emoji
"""

NOMEN_RAW = """
der|Hund|Hunde|Tiere|2|🐶
die|Kat-ze|Katzen|Tiere|2|🐱
die|Maus|Mäuse|Tiere|2|🐭
der|Ha-se|Hasen|Tiere|2|🐰
der|Fuchs|Füchse|Tiere|2|🦊
der|Bär|Bären|Tiere|2|🐻
der|I-gel|Igel|Tiere|2|🦔
das|Pferd|Pferde|Tiere|2|🐴
die|Kuh|Kühe|Tiere|2|🐮
das|Schwein|Schweine|Tiere|2|🐷
der|Frosch|Frösche|Tiere|2|🐸
der|Vo-gel|Vögel|Tiere|2|🐦
die|Eu-le|Eulen|Tiere|2|🦉
der|Fisch|Fische|Tiere|2|🐟
die|Bie-ne|Bienen|Tiere|2|🐝
die|Schne-cke|Schnecken|Tiere|2|🐌
der|Lö-we|Löwen|Tiere|2|🦁
der|Af-fe|Affen|Tiere|2|🐵
die|En-te|Enten|Tiere|2|🦆
der|Wal|Wale|Tiere|2|🐳
die|Schlan-ge|Schlangen|Tiere|2|🐍
der|E-le-fant|Elefanten|Tiere|3|🐘
die|Gi-raf-fe|Giraffen|Tiere|3|🦒
das|Eich-hörn-chen|Eichhörnchen|Tiere|3|🐿️
der|Schmet-ter-ling|Schmetterlinge|Tiere|3|🦋
das|Kro-ko-dil|Krokodile|Tiere|3|🐊
der|Pin-gu-in|Pinguine|Tiere|3|🐧
der|Ap-fel|Äpfel|Obst|2|🍎
die|Bir-ne|Birnen|Obst|2|🍐
die|Ba-na-ne|Bananen|Obst|2|🍌
die|Erd-bee-re|Erdbeeren|Obst|2|🍓
die|Kir-sche|Kirschen|Obst|2|🍒
die|Zi-tro-ne|Zitronen|Obst|2|🍋
die|Trau-be|Trauben|Obst|2|🍇
die|Me-lo-ne|Melonen|Obst|2|🍉
die|O-ran-ge|Orangen|Obst|2|🍊
der|Pfir-sich|Pfirsiche|Obst|3|🍑
die|Ka-rot-te|Karotten|Gemüse|2|🥕
die|Gur-ke|Gurken|Gemüse|2|🥒
die|To-ma-te|Tomaten|Gemüse|2|🍅
die|Kar-tof-fel|Kartoffeln|Gemüse|2|🥔
die|Zwie-bel|Zwiebeln|Gemüse|2|🧅
der|Kür-bis|Kürbisse|Gemüse|2|🎃
der|Sa-lat|Salate|Gemüse|2|🥬
der|Brok-ko-li|-|Gemüse|3|🥦
das|Au-to|Autos|Fahrzeuge|2|🚗
der|Bus|Busse|Fahrzeuge|2|🚌
das|Fahr-rad|Fahrräder|Fahrzeuge|2|🚲
der|Zug|Züge|Fahrzeuge|2|🚆
das|Flug-zeug|Flugzeuge|Fahrzeuge|2|✈️
das|Schiff|Schiffe|Fahrzeuge|2|🚢
der|Trak-tor|Traktoren|Fahrzeuge|2|🚜
der|Rol-ler|Roller|Fahrzeuge|2|🛴
die|Ra-ke-te|Raketen|Fahrzeuge|3|🚀
der|Hub-schrau-ber|Hubschrauber|Fahrzeuge|3|🚁
das|Mo-tor-rad|Motorräder|Fahrzeuge|3|🏍️
die|Ho-se|Hosen|Kleidung|2|👖
die|Müt-ze|Mützen|Kleidung|2|🧢
der|Schuh|Schuhe|Kleidung|2|👟
das|Kleid|Kleider|Kleidung|2|👗
der|Hand-schuh|Handschuhe|Kleidung|2|🧤
der|Schal|Schals|Kleidung|2|🧣
die|So-cke|Socken|Kleidung|2|🧦
die|Ja-cke|Jacken|Kleidung|2|🧥
der|Stie-fel|Stiefel|Kleidung|2|👢
das|Hemd|Hemden|Kleidung|3|👔
das|Buch|Bücher|Schulsachen|2|📘
das|Heft|Hefte|Schulsachen|2|📓
der|Stift|Stifte|Schulsachen|2|✏️
die|Sche-re|Scheren|Schulsachen|2|✂️
das|Li-ne-al|Lineale|Schulsachen|2|📏
der|Ruck-sack|Rucksäcke|Schulsachen|2|🎒
der|Pin-sel|Pinsel|Schulsachen|2|🖌️
der|Ra-dier-gum-mi|Radiergummis|Schulsachen|2|
der|Tisch|Tische|Möbel|2|
der|Stuhl|Stühle|Möbel|2|🪑
das|Bett|Betten|Möbel|2|🛏️
der|Schrank|Schränke|Möbel|2|
das|So-fa|Sofas|Möbel|2|🛋️
das|Re-gal|Regale|Möbel|3|
die|Hand|Hände|Körperteile|2|✋
der|Fuß|Füße|Körperteile|2|🦶
die|Na-se|Nasen|Körperteile|2|👃
das|Au-ge|Augen|Körperteile|2|👁️
das|Ohr|Ohren|Körperteile|2|👂
der|Mund|Münder|Körperteile|2|👄
der|Zahn|Zähne|Körperteile|2|🦷
das|Bein|Beine|Körperteile|2|🦵
der|Arm|Arme|Körperteile|2|💪
der|Kopf|Köpfe|Körperteile|2|
der|Bauch|Bäuche|Körperteile|2|
die|Son-ne|Sonnen|Natur|2|☀️
der|Mond|Monde|Natur|2|🌙
der|Stern|Sterne|Natur|2|⭐
die|Wol-ke|Wolken|Natur|2|☁️
der|Re-gen|-|Natur|2|🌧️
der|Schnee|-|Natur|2|❄️
der|Baum|Bäume|Natur|2|🌳
die|Blu-me|Blumen|Natur|2|🌷
der|Berg|Berge|Natur|2|⛰️
der|Fluss|Flüsse|Natur|2|
der|See|Seen|Natur|2|
das|Blatt|Blätter|Natur|2|🍂
der|Wald|Wälder|Natur|2|🌲
die|Wie-se|Wiesen|Natur|2|
der|Re-gen-bo-gen|Regenbogen|Natur|2|🌈
das|Brot|Brote|Essen|2|🍞
der|Kä-se|Käse|Essen|2|🧀
der|Ku-chen|Kuchen|Essen|2|🍰
die|Piz-za|Pizzas|Essen|2|🍕
das|Ei|Eier|Essen|2|🥚
die|Nu-del|Nudeln|Essen|2|🍝
die|Bre-ze|Brezen|Essen|2|🥨
die|Sup-pe|Suppen|Essen|2|🍲
die|Milch|-|Getränke|2|🥛
der|Saft|Säfte|Getränke|2|🧃
das|Was-ser|-|Getränke|2|💧
der|Tee|Tees|Getränke|2|🍵
der|Ball|Bälle|Spielzeug|2|⚽
die|Pup-pe|Puppen|Spielzeug|2|
der|Dra-chen|Drachen|Spielzeug|2|🪁
das|Puz-zle|Puzzles|Spielzeug|2|🧩
der|Wür-fel|Würfel|Spielzeug|2|🎲
der|Ted-dy|Teddys|Spielzeug|2|🧸
die|Trom-mel|Trommeln|Musikinstrumente|2|🥁
die|Flö-te|Flöten|Musikinstrumente|2|
die|Gi-tar-re|Gitarren|Musikinstrumente|3|🎸
die|Gei-ge|Geigen|Musikinstrumente|3|🎻
das|Kla-vier|Klaviere|Musikinstrumente|3|🎹
die|Trom-pe-te|Trompeten|Musikinstrumente|3|🎺
die|Mut-ter|Mütter|Familie|2|
der|Va-ter|Väter|Familie|2|
der|Bru-der|Brüder|Familie|2|
die|Schwes-ter|Schwestern|Familie|2|
die|O-ma|Omas|Familie|2|👵
der|O-pa|Opas|Familie|2|👴
das|Ba-by|Babys|Familie|2|👶
der|Bä-cker|Bäcker|Berufe|2|🥖
der|Leh-rer|Lehrer|Berufe|2|
der|Koch|Köche|Berufe|2|🍳
der|Bau-er|Bauern|Berufe|2|🌾
der|Arzt|Ärzte|Berufe|3|🩺
der|Po-li-zist|Polizisten|Berufe|3|👮
das|Haus|Häuser|Gebäude|2|🏠
die|Schu-le|Schulen|Gebäude|2|🏫
die|Kir-che|Kirchen|Gebäude|2|⛪
die|Burg|Burgen|Gebäude|2|🏰
die|Tür|Türen|Haus|2|🚪
das|Fens-ter|Fenster|Haus|2|🪟
der|Schlüs-sel|Schlüssel|Haus|2|🔑
die|Uhr|Uhren|Haus|2|⏰
die|Ker-ze|Kerzen|Haus|2|🕯️
das|Ge-schenk|Geschenke|Haus|2|🎁
die|Lam-pe|Lampen|Haus|2|💡
"""

# Silben | er/sie/es-Form | Präteritum (er/sie/es) | ab Klasse
VERBEN_RAW = """
lau-fen|läuft|lief|2
sprin-gen|springt|sprang|2
spie-len|spielt|spielte|2
schwim-men|schwimmt|schwamm|2
le-sen|liest|las|2
schrei-ben|schreibt|schrieb|2
ma-len|malt|malte|2
sin-gen|singt|sang|2
tan-zen|tanzt|tanzte|2
es-sen|isst|aß|2
trin-ken|trinkt|trank|2
schla-fen|schläft|schlief|2
ren-nen|rennt|rannte|2
la-chen|lacht|lachte|2
wei-nen|weint|weinte|2
ko-chen|kocht|kochte|2
ba-cken|backt|backte|2
fah-ren|fährt|fuhr|2
flie-gen|fliegt|flog|2
rech-nen|rechnet|rechnete|2
ge-hen|geht|ging|2
se-hen|sieht|sah|2
ru-fen|ruft|rief|2
klet-tern|klettert|kletterte|2
bau-en|baut|baute|2
wer-fen|wirft|warf|3
fan-gen|fängt|fing|3
tra-gen|trägt|trug|3
hel-fen|hilft|half|3
kom-men|kommt|kam|2
schau-en|schaut|schaute|2
hö-ren|hört|hörte|2
den-ken|denkt|dachte|3
tur-nen|turnt|turnte|2
"""

# Silben | Gegenteil | Steigerung | Superlativ
ADJEKTIVE_RAW = """
groß|klein|größer|am größten
klein|groß|kleiner|am kleinsten
schnell|lang-sam|schneller|am schnellsten
lang-sam|schnell|langsamer|am langsamsten
heiß|kalt|heißer|am heißesten
kalt|heiß|kälter|am kältesten
hell|dun-kel|heller|am hellsten
dun-kel|hell|dunkler|am dunkelsten
laut|lei-se|lauter|am lautesten
lei-se|laut|leiser|am leisesten
alt|jung|älter|am ältesten
jung|alt|jünger|am jüngsten
dick|dünn|dicker|am dicksten
dünn|dick|dünner|am dünnsten
lang|kurz|länger|am längsten
kurz|lang|kürzer|am kürzesten
schwer|leicht|schwerer|am schwersten
leicht|schwer|leichter|am leichtesten
nass|tro-cken|nasser|am nassesten
tro-cken|nass|trockener|am trockensten
voll|leer|voller|am vollsten
leer|voll|leerer|am leersten
mü-de|wach|müder|am müdesten
fröh-lich|trau-rig|fröhlicher|am fröhlichsten
trau-rig|fröh-lich|trauriger|am traurigsten
süß|sau-er|süßer|am süßesten
weich|hart|weicher|am weichsten
hart|weich|härter|am härtesten
stark|schwach|stärker|am stärksten
warm|kalt|wärmer|am wärmsten
"""

REIME = [
    ["Haus", "Maus", "raus"], ["Hose", "Rose", "Dose"], ["Tisch", "Fisch", "frisch"],
    ["Kanne", "Tanne", "Pfanne", "Wanne"], ["Hand", "Sand", "Band", "Wand", "Land"],
    ["Nase", "Hase", "Vase"], ["Ball", "Stall", "Knall"], ["Bein", "Stein", "Schwein", "klein"],
    ["Katze", "Tatze", "Glatze"], ["Sonne", "Tonne"], ["Hund", "Mund", "rund", "bunt"],
    ["Kuchen", "suchen"], ["Bett", "nett"], ["Baum", "Traum", "Schaum", "Raum"],
    ["Stern", "fern", "gern"], ["Schnecke", "Ecke", "Decke"], ["Hut", "Mut", "gut", "Wut"],
    ["Brot", "rot", "Boot"], ["Zug", "Krug", "klug"], ["Kopf", "Topf", "Zopf"],
    ["Wurm", "Turm", "Sturm"], ["Fliege", "Ziege", "Wiege"],
    ["Rabe", "Gabe"], ["Wagen", "Kragen", "tragen"],
]

KOMPOSITA = [
    ("Haus", "die Tür", "die Haustür", "🏠🚪"), ("Schule", "die Tasche", "die Schultasche", "🏫🎒"),
    ("Fuß", "der Ball", "der Fußball", "🦶⚽"), ("Apfel", "der Baum", "der Apfelbaum", "🍎🌳"),
    ("Sonne", "die Blume", "die Sonnenblume", "☀️🌻"), ("Hand", "der Schuh", "der Handschuh", "✋👟"),
    ("Schnee", "der Mann", "der Schneemann", "❄️⛄"), ("Zahn", "die Bürste", "die Zahnbürste", "🦷🪥"),
    ("Regen", "der Schirm", "der Regenschirm", "🌧️☂️"), ("Feuer", "die Wehr", "die Feuerwehr", "🔥🚒"),
    ("Spiel", "der Platz", "der Spielplatz", "🛝"), ("Fahrrad", "der Helm", "der Fahrradhelm", "🚲⛑️"),
    ("Blume", "der Topf", "der Blumentopf", "🌷🪴"), ("Tisch", "das Bein", "das Tischbein", "🦵"),
    ("Tier", "der Arzt", "der Tierarzt", "🐶🩺"), ("Brief", "der Kasten", "der Briefkasten", "✉️📮"),
    ("Eis", "der Bär", "der Eisbär", "🧊🐻‍❄️"), ("Bild", "das Buch", "das Bilderbuch", "🖼️📖"),
    ("Hund", "die Hütte", "die Hundehütte", "🐶🏠"), ("Mond", "das Licht", "das Mondlicht", "🌙💡"),
    ("Kinder", "der Garten", "der Kindergarten", "🧒🌳"), ("Wasser", "das Glas", "das Wasserglas", "💧🥛"),
]

WORTFAMILIEN = [
    ("fahren", ["Fahrer", "Fahrrad", "Abfahrt", "Fahrkarte"], ["Farbe", "Faden", "Feder"]),
    ("spielen", ["Spielplatz", "Spieler", "Spielzeug", "Brettspiel"], ["Spiegel", "Spinne", "Spitze"]),
    ("backen", ["Bäcker", "Backofen", "Bäckerei", "Backblech"], ["Bach", "Balken", "Bagger"]),
    ("schreiben", ["Schreibtisch", "Schreibheft", "Schrift", "Beschreibung"], ["Schrank", "Schraube", "Schrei"]),
    ("lesen", ["Leser", "Lesebuch", "Lesezeichen", "vorlesen"], ["Leiter", "Lehrer", "Löwe"]),
    ("singen", ["Sänger", "Singvogel", "Gesang", "mitsingen"], ["Sieb", "Silber", "Sinn"]),
    ("waschen", ["Waschbär", "Waschmaschine", "Wäsche", "abwaschen"], ["Wasser", "Wachs", "Wespe"]),
    ("springen", ["Springseil", "Springbrunnen", "Sprung", "Springer"], ["Spritze", "Sprache", "Spinat"]),
    ("schlafen", ["Schlafanzug", "Schläfer", "schläfrig", "einschlafen"], ["Schlange", "Schlauch", "Schlamm"]),
]

SATZZEICHEN = [
    ("Wie heißt du", "?"), ("Ich gehe heute in die Schule", "."), ("Pass auf", "!"),
    ("Kommst du mit", "?"), ("Heute scheint die Sonne", "."), ("Hilfe", "!"),
    ("Wo wohnst du", "?"), ("Das ist ja toll", "!"), ("Der Hund bellt laut", "."),
    ("Hast du Hunger", "?"), ("Komm schnell her", "!"), ("Wir spielen Fußball", "."),
    ("Wann beginnt die Pause", "?"), ("Mein Lieblingstier ist der Igel", "."),
    ("Hör sofort auf", "!"), ("Magst du Eis", "?"), ("Oma backt einen Kuchen", "."),
    ("Warum ist der Himmel blau", "?"), ("Au, das tut weh", "!"), ("Im Winter ist es kalt", "."),
]

MINIMALPAARE = [
    ("Mund", "Mond"), ("Hund", "Hand"), ("Tier", "Tür"), ("Kanne", "Kante"), ("Nase", "Hase"),
    ("Bein", "Wein"), ("Maus", "Haus"), ("Topf", "Zopf"), ("Kind", "Rind"), ("Tasse", "Tasche"),
    ("Fisch", "Tisch"), ("Ball", "Wall"), ("Maus", "Laus"), ("Hose", "Dose"), ("Rose", "Hose"), ("Keller", "Teller"), ("Wiese", "Riese"),
    ("Dach", "Bach"), ("Nadel", "Nudel"), ("Kiste", "Küste"), ("Tanne", "Tonne"), ("Leiter", "Leiser"),
]

# (Titel, ab Klasse, Stufe 1–5, Text, [(Frage, richtig, [falsch, falsch])])
TEXTE = [
    ("Mein Hund Bello", 2, 1,
     "Ich habe einen Hund. Er heißt Bello. Bello ist braun und hat lange Ohren. "
     "Er spielt gern mit dem Ball. Jeden Morgen gehe ich mit Bello spazieren. "
     "Dann wedelt er mit dem Schwanz.",
     [("Wie heißt der Hund?", "Bello", ["Bruno", "Bella"]),
      ("Welche Farbe hat Bello?", "Braun", ["Schwarz", "Weiß"]),
      ("Womit spielt Bello gern?", "Mit dem Ball", ["Mit der Katze", "Mit einem Stock"])]),
    ("Der kleine Igel", 2, 1,
     "Im Garten wohnt ein kleiner Igel. Er heißt Stachel. Am Tag schläft Stachel unter einem "
     "Laubhaufen. Wenn es dunkel wird, sucht er Futter. Er frisst gern Käfer und Würmer. "
     "Im Winter hält Stachel einen langen Winterschlaf.",
     [("Wo schläft Stachel am Tag?", "Unter einem Laubhaufen", ["Auf einem Baum", "Im Haus"]),
      ("Was frisst Stachel gern?", "Käfer und Würmer", ["Nudeln und Brot", "Gras und Heu"]),
      ("Was macht Stachel im Winter?", "Er hält Winterschlaf", ["Er fliegt in den Süden", "Er baut einen Schneemann"])]),
    ("Ein Tag am See", 2, 1,
     "Lena und ihr Bruder Max fahren mit dem Fahrrad an den See. Die Sonne scheint und es ist heiß. "
     "Max springt sofort ins Wasser. Lena baut eine Burg aus Sand. Am Nachmittag essen beide ein Eis. "
     "Lena nimmt Erdbeere, Max nimmt Schokolade.",
     [("Wie fahren die Kinder zum See?", "Mit dem Fahrrad", ["Mit dem Bus", "Mit dem Auto"]),
      ("Was baut Lena?", "Eine Sandburg", ["Ein Boot", "Ein Baumhaus"]),
      ("Welches Eis isst Max?", "Schokolade", ["Erdbeere", "Vanille"])]),
    ("Der verlorene Schlüssel", 2, 2,
     "Oma Rosi sucht ihren Schlüssel. Sie schaut in der Küche nach, aber da ist er nicht. "
     "Dann sucht sie im Wohnzimmer unter dem Sofa. Da liegt nur ein alter Ball. "
     "Ihr Enkel Tim hat eine Idee: „Schau doch mal in deiner Jackentasche!“ "
     "Und tatsächlich – dort steckt der Schlüssel. Oma lacht und gibt Tim einen Keks.",
     [("Was sucht Oma Rosi?", "Ihren Schlüssel", ["Ihre Brille", "Ihr Handy"]),
      ("Was liegt unter dem Sofa?", "Ein alter Ball", ["Der Schlüssel", "Eine Katze"]),
      ("Wo ist der Schlüssel?", "In der Jackentasche", ["In der Küche", "Im Garten"]),
      ("Was bekommt Tim?", "Einen Keks", ["Ein Eis", "Einen Euro"])]),
    ("Der Schneemann", 2, 2,
     "Über Nacht hat es geschneit. Alles ist weiß. Emil und Sara ziehen warme Jacken, Mützen und "
     "Handschuhe an. Im Garten rollen sie drei dicke Kugeln. Daraus bauen sie einen Schneemann. "
     "Er bekommt eine Karotte als Nase und zwei Steine als Augen. Sara setzt ihm einen alten Hut auf. "
     "Am Abend trinken die Kinder heißen Kakao.",
     [("Wie viele Kugeln rollen die Kinder?", "Drei", ["Zwei", "Vier"]),
      ("Was bekommt der Schneemann als Nase?", "Eine Karotte", ["Einen Stein", "Eine Gurke"]),
      ("Was trinken die Kinder am Abend?", "Heißen Kakao", ["Kalte Milch", "Apfelsaft"])]),
    ("Das Fußballspiel", 2, 2,
     "Am Samstag hat Jonas ein Fußballspiel. Seine Mannschaft trägt rote Trikots. Die andere "
     "Mannschaft spielt in Blau. Zur Pause steht es 0 zu 1. Der Trainer sagt: „Gebt nicht auf!“ "
     "In der zweiten Halbzeit schießt Jonas zwei Tore. Am Ende gewinnt seine Mannschaft 2 zu 1. Alle jubeln.",
     [("Welche Farbe haben die Trikots von Jonas' Mannschaft?", "Rot", ["Blau", "Grün"]),
      ("Wie steht es zur Pause?", "0 zu 1", ["2 zu 1", "1 zu 1"]),
      ("Wie viele Tore schießt Jonas?", "Zwei", ["Eins", "Drei"]),
      ("Was sagt der Trainer?", "Gebt nicht auf!", ["Geht nach Hause!", "Macht eine Pause!"])]),
    ("Die Schnecke Susi", 2, 3,
     "Susi ist eine Weinbergschnecke. Sie trägt ihr Haus immer auf dem Rücken. Wenn es regnet, freut "
     "sich Susi, denn dann ist der Boden schön feucht. Sie kriecht ganz langsam über die Wiese und frisst "
     "frische Blätter. Wenn Gefahr droht, zieht sich Susi schnell in ihr Haus zurück. Mit ihren Fühlern "
     "kann sie riechen und tasten.",
     [("Was trägt Susi auf dem Rücken?", "Ihr Haus", ["Einen Rucksack", "Ein Blatt"]),
      ("Warum freut sich Susi über Regen?", "Weil der Boden dann feucht ist", ["Weil sie baden will", "Weil sie Angst vor der Sonne hat"]),
      ("Was macht Susi bei Gefahr?", "Sie zieht sich in ihr Haus zurück", ["Sie rennt schnell weg", "Sie ruft um Hilfe"]),
      ("Wozu braucht Susi ihre Fühler?", "Zum Riechen und Tasten", ["Zum Laufen", "Zum Fliegen"])]),
    ("Ausflug in den Zoo", 2, 3,
     "Die Klasse 2b macht einen Ausflug in den Zoo. Zuerst besuchen die Kinder die Affen. Ein kleiner "
     "Affe klaut einer Besucherin die Mütze! Danach gehen sie zu den Elefanten. Der größte Elefant heißt "
     "Benni und ist schon 40 Jahre alt. Zum Schluss sehen sie die Pinguine bei der Fütterung. Jeder "
     "Pinguin bekommt drei Fische. Müde, aber glücklich fahren alle mit dem Bus zurück zur Schule.",
     [("Welche Tiere besuchen die Kinder zuerst?", "Die Affen", ["Die Elefanten", "Die Pinguine"]),
      ("Was klaut der kleine Affe?", "Eine Mütze", ["Eine Banane", "Einen Schuh"]),
      ("Wie alt ist Benni?", "40 Jahre", ["14 Jahre", "4 Jahre"]),
      ("Wie viele Fische bekommt jeder Pinguin?", "Drei", ["Zwei", "Zehn"])]),
    ("Der Herbst ist da", 2, 4,
     "Im Herbst werden die Tage kürzer und die Nächte länger. Die Blätter an den Bäumen färben sich gelb, "
     "orange und rot. Dann fallen sie herunter. Die Kinder sammeln Kastanien und basteln daraus lustige "
     "Tiere. Viele Vögel fliegen in den warmen Süden. Das Eichhörnchen versteckt Nüsse für den Winter. "
     "Manchmal vergisst es aber, wo es sie vergraben hat. Dann wächst dort im Frühling ein neuer Baum.",
     [("Was passiert im Herbst mit den Tagen?", "Sie werden kürzer", ["Sie werden länger", "Sie bleiben gleich"]),
      ("Was basteln die Kinder aus Kastanien?", "Lustige Tiere", ["Laternen", "Drachen"]),
      ("Wohin fliegen viele Vögel?", "In den warmen Süden", ["In den kalten Norden", "Auf den höchsten Berg"]),
      ("Was passiert, wenn das Eichhörnchen Nüsse vergisst?", "Es wächst ein neuer Baum", ["Die Nüsse werden zu Steinen", "Es schneit"])]),
    ("Paula backt Pfannkuchen", 2, 4,
     "Paula will für ihre Familie Pfannkuchen backen. Papa hilft ihr. Zuerst holen sie Mehl, Milch, Eier "
     "und eine Prise Salz. Paula verrührt alles mit dem Schneebesen zu einem glatten Teig. Papa macht die "
     "Pfanne heiß, denn der Herd ist gefährlich. Nach zehn Minuten liegen acht goldene Pfannkuchen auf dem "
     "Teller. Paulas kleiner Bruder isst am liebsten Pfannkuchen mit Apfelmus.",
     [("Wer hilft Paula?", "Papa", ["Mama", "Oma"]),
      ("Womit verrührt Paula den Teig?", "Mit dem Schneebesen", ["Mit einem Löffel", "Mit den Händen"]),
      ("Warum macht Papa die Pfanne heiß?", "Weil der Herd gefährlich ist", ["Weil Paula keine Lust hat", "Weil Papa Hunger hat"]),
      ("Wie viele Pfannkuchen liegen auf dem Teller?", "Acht", ["Zehn", "Sechs"])]),
    ("Die Feuerwehr kommt", 3, 3,
     "Mitten in der Nacht heult die Sirene. Die Freiwillige Feuerwehr wird gerufen: In einer Scheune am "
     "Dorfrand brennt es. Innerhalb von fünf Minuten sind die Feuerwehrleute im Gerätehaus, ziehen ihre "
     "Schutzkleidung an und fahren mit Blaulicht los. Mit zwei Schläuchen löschen sie das Feuer. Zum Glück "
     "waren keine Tiere in der Scheune. Die Feuerwehrleute arbeiten ehrenamtlich – das bedeutet, sie "
     "bekommen für ihre Hilfe kein Geld. Tagsüber haben sie ganz normale Berufe.",
     [("Was brennt?", "Eine Scheune", ["Ein Wohnhaus", "Ein Wald"]),
      ("Wie viele Schläuche benutzen sie?", "Zwei", ["Einen", "Fünf"]),
      ("Was bedeutet „ehrenamtlich“?", "Sie bekommen kein Geld dafür", ["Sie arbeiten nur nachts", "Sie sind sehr berühmt"]),
      ("Wie schnell sind die Feuerwehrleute im Gerätehaus?", "In fünf Minuten", ["In einer Stunde", "In zwanzig Minuten"])]),
    ("Unser Bayern", 3, 3,
     "Bayern ist das größte Bundesland in Deutschland. Die Hauptstadt ist München. Im Süden liegen die "
     "Alpen mit dem höchsten Berg Deutschlands, der Zugspitze. Sie ist fast 3000 Meter hoch. Durch Bayern "
     "fließen große Flüsse wie die Donau und die Isar. Die bayerische Flagge ist weiß-blau mit Rauten. "
     "Viele Menschen besuchen im Herbst das Oktoberfest in München.",
     [("Wie heißt die Hauptstadt von Bayern?", "München", ["Nürnberg", "Berlin"]),
      ("Wie heißt der höchste Berg Deutschlands?", "Die Zugspitze", ["Der Watzmann", "Der Brocken"]),
      ("Welche Farben hat die bayerische Flagge?", "Weiß und Blau", ["Rot und Weiß", "Schwarz, Rot und Gold"]),
      ("Welcher Fluss fließt durch Bayern?", "Die Isar", ["Die Elbe", "Die Weser"])]),
    ("Der Wasserkreislauf", 3, 4,
     "Wasser ist immer unterwegs. Wenn die Sonne auf Meere, Seen und Flüsse scheint, verdunstet das Wasser. "
     "Es steigt als unsichtbarer Wasserdampf in die Luft. Hoch oben ist es kalt, deshalb bilden sich aus dem "
     "Dampf winzige Tröpfchen. Viele Tröpfchen zusammen sind eine Wolke. Werden die Tropfen zu schwer, fallen "
     "sie als Regen herunter. Ist es sehr kalt, fällt Schnee. Das Wasser fließt in Bäche und Flüsse und "
     "schließlich wieder ins Meer. Dann beginnt alles von vorne.",
     [("Was passiert, wenn die Sonne auf das Wasser scheint?", "Es verdunstet", ["Es gefriert", "Es wird salzig"]),
      ("Woraus besteht eine Wolke?", "Aus winzigen Wassertröpfchen", ["Aus Rauch", "Aus Watte"]),
      ("Wann fällt Schnee statt Regen?", "Wenn es sehr kalt ist", ["Wenn es windig ist", "Wenn die Sonne scheint"]),
      ("Warum nennt man das einen Kreislauf?", "Weil alles immer wieder von vorne beginnt", ["Weil Wolken rund sind", "Weil Wasser im Kreis fließt"])]),
    ("Die Honigbiene", 4, 3,
     "Bienen leben in einem Volk mit bis zu 50 000 Tieren. Jedes Volk hat nur eine Königin. Sie legt jeden "
     "Tag bis zu 2000 Eier. Die meisten Bienen sind Arbeiterinnen. Sie putzen den Stock, füttern die Larven "
     "und sammeln Nektar und Blütenstaub, den man auch Pollen nennt. Aus dem Nektar machen sie Honig. Dabei "
     "bestäuben die Bienen die Blüten. Ohne Bienen würden viele Obstbäume keine Früchte tragen. Deshalb "
     "sind Bienen für uns Menschen sehr wichtig.",
     [("Wie viele Königinnen hat ein Bienenvolk?", "Eine", ["Zwei", "Hundert"]),
      ("Wie nennt man Blütenstaub noch?", "Pollen", ["Nektar", "Wachs"]),
      ("Warum sind Bienen so wichtig?", "Sie bestäuben Blüten, damit Früchte wachsen", ["Sie halten den Garten sauber", "Sie vertreiben Mücken"]),
      ("Wer legt die Eier?", "Die Königin", ["Die Arbeiterinnen", "Der Imker"])]),
    ("Leben auf der Burg", 4, 4,
     "Vor vielen hundert Jahren, im Mittelalter, bauten Ritter und Adlige Burgen. Die Burgen standen oft auf "
     "Bergen, damit man Feinde früh sehen konnte. Eine dicke Mauer und ein tiefer Graben schützten die "
     "Bewohner. Über den Graben führte eine Zugbrücke, die man hochziehen konnte. Im höchsten Turm, dem "
     "Bergfried, konnten sich die Menschen bei einem Angriff verstecken. Das Leben auf der Burg war aber "
     "nicht so gemütlich, wie viele denken: Im Winter war es kalt und zugig, denn es gab keine Heizung und "
     "oft keine Glasfenster.",
     [("Warum standen Burgen oft auf Bergen?", "Damit man Feinde früh sehen konnte", ["Weil es dort wärmer war", "Weil es im Tal verboten war"]),
      ("Wie heißt der höchste Turm einer Burg?", "Bergfried", ["Burgturm", "Kirchturm"]),
      ("Wozu diente die Zugbrücke?", "Man konnte sie hochziehen und so die Burg schützen", ["Zum Angeln", "Für Pferderennen"]),
      ("Warum war es im Winter ungemütlich?", "Es gab keine Heizung und oft keine Glasfenster", ["Es gab zu viele Ritter", "Es gab nichts zu essen"])]),
]

# (Satz, ab Klasse, Stufe)
DIKTAT_SAETZE = [
    ("Der Hund bellt.", 2, 3), ("Die Katze schläft.", 2, 3), ("Ich habe einen Ball.", 2, 3),
    ("Mama backt einen Kuchen.", 2, 4), ("Wir gehen in die Schule.", 2, 4), ("Das Auto ist rot.", 2, 3),
    ("Die Sonne scheint.", 2, 3), ("Opa liest ein Buch.", 2, 4), ("Der Vogel singt im Baum.", 2, 4),
    ("Ich trinke gern Milch.", 2, 4), ("Die Maus ist klein.", 2, 3), ("Im Winter fällt Schnee.", 2, 4),
    ("Der Fuchs läuft schnell über die Wiese.", 2, 5), ("Im Herbst fallen die bunten Blätter.", 2, 5),
    ("Mein Bruder spielt gern Fußball.", 2, 5), ("Die Kinder bauen eine große Sandburg.", 2, 5),
    ("Am Abend leuchten die Sterne am Himmel.", 3, 4), ("Der Igel sucht im Garten nach Futter.", 3, 4),
    ("Wir fahren mit dem Fahrrad zum See.", 3, 4), ("Die fleißigen Bienen sammeln süßen Nektar.", 4, 4),
    ("Nach dem Gewitter zeigte sich ein Regenbogen.", 4, 4), ("Die Feuerwehr kam mit Blaulicht und Sirene.", 4, 5),
    ("Im Mittelalter lebten Ritter auf Burgen.", 4, 5),
]


def _parse():
    nomen = []
    for line in NOMEN_RAW.strip().splitlines():
        art, syl, pl, cat, grade, emo = (line.split("|") + [""])[:6]
        nomen.append({"art": art, "syl": syl, "w": syl.replace("-", ""), "pl": None if pl == "-" else pl,
                      "cat": cat, "g": int(grade), "e": emo.strip()})
    verben = []
    for line in VERBEN_RAW.strip().splitlines():
        syl, er, prae, grade = line.split("|")
        verben.append({"syl": syl, "w": syl.replace("-", ""), "er": er, "prae": prae, "g": int(grade)})
    adj = []
    for line in ADJEKTIVE_RAW.strip().splitlines():
        syl, opp, komp, sup = line.split("|")
        adj.append({"syl": syl, "w": syl.replace("-", ""), "opp": opp.replace("-", ""), "komp": komp, "sup": sup})
    return nomen, verben, adj


NOMEN, VERBEN, ADJEKTIVE = _parse()
