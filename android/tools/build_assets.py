"""Sammelt alle Bilder für die Android-App (einmalig am PC ausführen, Ergebnis wird mit eingebaut).

- 3D-Emojis (Microsoft Fluent) für alle Emojis aus den Inhalten
- Animierte 3D-Emojis als ZIP-Bildfolgen (Kivy spielt ZIP-Animationen direkt ab)
- Fotos für „Was ist anders?“, „Fehlerbild“ und „Genau hinsehen“
"""

import io
import json
import os
import shutil
import sys
import time
import urllib.parse
import urllib.request
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
ANDROID = os.path.dirname(HERE)
ROOT = os.path.dirname(ANDROID)
sys.path.insert(0, ROOT)
os.environ.setdefault("LERNFUCHS_DATA", os.path.join(HERE, "_cache"))

from PIL import Image  # noqa: E402

from lernfuchs import emoji as E, photos  # noqa: E402
from lernfuchs.content import topics as TP, knobeln, mathe, konz  # noqa: E402
from lernfuchs.content.deutsch_data import NOMEN, KOMPOSITA  # noqa: E402
from lernfuchs.content.sach_data import FRAGEN, SORTS, ORDERS  # noqa: E402
from lernfuchs.storage import STICKERS  # noqa: E402
from lernfuchs import theme as T  # noqa: E402

ASSETS = os.path.join(ANDROID, "assets")
UI_EMOJIS = "⭐🔥🏅🔒✅💡🔊⬅️✖️❓🙈👍👎⏳🎯📒🧐🤔🚀💪🎉🏆💥⚡🔍📡🎲🔁🏠🔄💾🔓⏱️🎧➡️🦊📖🔢🌍🧠"
ANIMS = ["Party Popper", "Clapping Hands Light Skin Tone", "Star-Struck", "Sparkles", "Glowing Star",
         "Hundred Points", "Smiling Face with Sunglasses", "Thinking Face", "Face with Monocle", "Hourglass Done",
         "Collision", "Rocket", "Fire", "Trophy", "Fox", "Flexed Biceps Light Skin Tone", "Brain", "Light Bulb",
         "Gem Stone"]


def all_emojis():
    texts = [t.emoji for t in TP.TOPICS] + list(T.SUBJECT_EMOJI.values()) + [n["e"] for n in NOMEN if n["e"]]
    texts += [f["e"] for lst in FRAGEN.values() for f in lst if f["e"]]
    texts += [e for s in SORTS for e in s[5].values()] + [e for o in ORDERS for e in o[5].values()]
    texts += knobeln.SYMBOLS + mathe.FRUITS + STICKERS + [e for grp in konz.LOOKALIKES for e in grp]
    texts += [k[3] for k in KOMPOSITA] + [r[2] for r in T.RANKS] + [x[0] for x in mathe.SHOP]
    texts += ["🔴", "🔵", "🟡", "🟢", "🌙", "🍐", "🐭", "🔺", "🟦", "🍓", "🍌", "🐸", "🐢", "🦎"]
    chars = set()
    for t in texts:
        for ch in E.split_emojis(t):
            chars.add(ch)
    for ch in UI_EMOJIS:
        pass
    for ch in E.split_emojis(UI_EMOJIS):
        chars.add(ch)
    return sorted(c for c in chars if c.strip())


def main():
    os.makedirs(os.path.join(ASSETS, "emoji3d"), exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "anim"), exist_ok=True)
    os.makedirs(os.path.join(ASSETS, "fotos"), exist_ok=True)
    chars = all_emojis()
    print(len(chars), "Emojis")
    E.prewarm(chars)
    E.prefetch_anims(ANIMS)
    photos.prefetch(max_photos=40)
    for _ in range(90):  # auf Downloads warten
        time.sleep(2)
        if not E._pending and not photos._loading:
            break
    names = {}
    missing = []
    for ch in chars:
        name = E.emoji_name(ch).replace(" ", "_")
        src = E._path_3d(ch)
        if name and os.path.exists(src):
            im = Image.open(src).convert("RGBA")
            im.thumbnail((160, 160), Image.LANCZOS)
            im.save(os.path.join(ASSETS, "emoji3d", name + ".png"), optimize=True)
            names[ch] = name
        else:
            missing.append(ch)
    with open(os.path.join(ASSETS, "emoji_map.json"), "w", encoding="utf-8") as fh:
        json.dump(names, fh, ensure_ascii=False)
    print("3D:", len(names), "fehlend:", "".join(missing))
    for n in ANIMS:
        res = E.load_anim_frames(n, 160, step=3)
        if not res:
            print("Animation fehlt:", n)
            continue
        frames, dur = res
        key = E.anim_key(n).replace(" ", "_")
        with zipfile.ZipFile(os.path.join(ASSETS, "anim", key + ".zip"), "w", zipfile.ZIP_STORED) as z:
            for i, fr in enumerate(frames):
                buf = io.BytesIO()
                fr.save(buf, "PNG", optimize=True)
                z.writestr(f"{i:03d}.png", buf.getvalue())
        print("Animation", key, len(frames), "Bilder")
    idx = {}
    for p, title in photos.random_photos(40):
        fn = os.path.basename(p)
        im = Image.open(p).convert("RGB")
        im.thumbnail((720, 540))
        im.save(os.path.join(ASSETS, "fotos", fn), quality=85)
        idx[fn] = title
    with open(os.path.join(ASSETS, "fotos", "index.json"), "w", encoding="utf-8") as fh:
        json.dump(idx, fh, ensure_ascii=False)
    print("Fotos:", len(idx))


if __name__ == "__main__":
    main()
