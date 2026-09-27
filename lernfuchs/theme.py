"""Farben, Schriften und Stil-Konstanten für LernFuchs.

Zwei Designs: „modern“ (dunkel, sachlich – Standard) und „hell“ (freundlich, pastell).
Alle Module lesen die Werte zur Laufzeit (T.BG usw.), daher wirkt apply() beim nächsten Bildschirmaufbau.
"""

FONT = "Segoe UI"

PALETTES = {
    "modern": {
        "BG": "#0E1525", "CARD": "#172036", "CARD_BORDER": "#253252", "SURFACE": "#1E2944",
        "TEXT": "#E9EEF8", "MUTED": "#8C98B5", "ON_ACCENT": "#FFFFFF",
        "PRIMARY": "#FF8A3D", "PRIMARY_HOVER": "#F27426",
        "GOOD": "#2FCB8A", "GOOD_LIGHT": "#13382F", "BAD": "#F7677A", "BAD_LIGHT": "#3E1C28",
        "GOLD": "#FBBF24", "GOLD_LIGHT": "#3A3013", "NEUTRAL_BTN": "#222D4A", "NEUTRAL_HOVER": "#2C3A5E",
        "TRACK": "#26314F", "INPUT_BG": "#0F182C", "DISABLED_TEXT": "#56627F", "DOT_OFF": "#2E3A5A",
        "READ_BG": "#1B2540", "READ_BORDER": "#2C3A60", "GLASS": "#1D2B48", "GLASS_LINE": "#5B79B0",
        "CLOCK_FACE": "#F4F6FB", "CLOCK_TEXT": "#1D2438", "LOCKED": "#1C2640",
        "APPEARANCE": "dark",
        "SUBJECTS": {
            "deutsch": ("#FF6B81", "#35203A", "#F2566E"),
            "mathe": ("#4C9BFF", "#172C4F", "#3887EE"),
            "sach": ("#2FCB8A", "#133530", "#22B57A"),
            "konz": ("#A78BFA", "#2A2352", "#9372F5"),
            "mix": ("#FF8A3D", "#3A2616", "#F27426"),
        },
    },
    "hell": {
        "BG": "#FFF7EC", "CARD": "#FFFFFF", "CARD_BORDER": "#F1E4D3", "SURFACE": "#F7F1E8",
        "TEXT": "#2B2D42", "MUTED": "#8A8FA3", "ON_ACCENT": "#FFFFFF",
        "PRIMARY": "#FF8C42", "PRIMARY_HOVER": "#F2742A",
        "GOOD": "#2EB872", "GOOD_LIGHT": "#DDF6E8", "BAD": "#FF5A5F", "BAD_LIGHT": "#FFE4E5",
        "GOLD": "#FFC93C", "GOLD_LIGHT": "#FFF3CF", "NEUTRAL_BTN": "#F3EEE7", "NEUTRAL_HOVER": "#E8E0D5",
        "TRACK": "#EFE6DA", "INPUT_BG": "#FFFFFF", "DISABLED_TEXT": "#C9C2B8", "DOT_OFF": "#E6E0D8",
        "READ_BG": "#FFFDF7", "READ_BORDER": "#F3E3C8", "GLASS": "#EAF6FF", "GLASS_LINE": "#9CC7E8",
        "CLOCK_FACE": "#FFFFFF", "CLOCK_TEXT": "#2B2D42", "LOCKED": "#F4F1EC",
        "APPEARANCE": "light",
        "SUBJECTS": {
            "deutsch": ("#FF6B6B", "#FFE3E3", "#F05454"),
            "mathe": ("#4D96FF", "#E1EDFF", "#3A82EE"),
            "sach": ("#2EB872", "#DDF6E8", "#24A262"),
            "konz": ("#9B5DE5", "#EFE4FB", "#8747D6"),
            "mix": ("#FF8C42", "#FFE8D6", "#F2742A"),
        },
    },
}

CURRENT = "modern"


def apply(name: str):
    global CURRENT
    name = name if name in PALETTES else "modern"
    CURRENT = name
    globals().update(PALETTES[name])
    try:
        import customtkinter as ctk
        ctk.set_appearance_mode(PALETTES[name]["APPEARANCE"])
    except Exception:
        pass


apply("modern")

SUBJECT_NAMES = {
    "deutsch": "Deutsch",
    "mathe": "Mathe",
    "sach": "Heimat & Sachkunde",
    "konz": "Konzentration",
    "mix": "Tagesmix",
}

SUBJECT_EMOJI = {
    "deutsch": "📖",
    "mathe": "🔢",
    "sach": "🌍",
    "konz": "🧠",
    "mix": "🎲",
}

# Ränge nach gesammelten Punkten (XP)
RANKS = [(0, "Einsteiger", "🌱"), (60, "Entdecker", "🧭"), (180, "Forscher", "🔬"), (400, "Tüftler", "🛠️"),
         (750, "Experte", "🎓"), (1200, "Meister", "🥋"), (1800, "Genie", "🧠"), (2700, "Legende", "🏆")]


def rank_for(xp: int):
    """(Name, Emoji, aktuelle Schwelle, nächste Schwelle oder None)."""
    cur = RANKS[0]
    nxt = None
    for i, r in enumerate(RANKS):
        if xp >= r[0]:
            cur = r
            nxt = RANKS[i + 1][0] if i + 1 < len(RANKS) else None
    return cur[1], cur[2], cur[0], nxt


def f(size: int, weight: str = "bold"):
    """Schrift-Tupel (CTk skaliert Tupel-Fonts automatisch)."""
    return (FONT, size, weight)
