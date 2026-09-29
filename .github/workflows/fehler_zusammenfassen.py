"""Fasst ein gescheitertes Buildozer-Protokoll zusammen und gibt es als GitHub-Hinweis aus."""

import re
import sys

try:
    log = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
except OSError:
    log = ["(kein build.log)"]

ANSI = re.compile(r"\x1b\[[0-9;]*m")
NOISE = re.compile(r"performance hint|Declare '|Use an 'int' return|Exception check on|^\s*#\s|^export |\.pyc\b")
log = [ANSI.sub("", line) for line in log]
clean = [line for line in log if not NOISE.search(line)]

MARK = re.compile(r"BUILD FAILED|FAILURE:|What went wrong|Command failed|Error:|error:|Exception|STDERR:|"
                  r"ErrorReturnCode|No such file|not found|Traceback", re.I)
marks = [i for i, line in enumerate(clean) if MARK.search(line)]


def esc(text):
    return text.replace("%", "%25").replace("\r", "").replace("\n", "%0A")


# Die ersten echten Fehlerstellen sind meist die Ursache – beide Enden zeigen
blocks = []
for i in (marks[:3] + marks[-4:]):
    blocks.append(f"--- Zeile {i} ---")
    blocks.extend(clean[max(0, i - 12):i + 8])
print("::error title=Fehlerstellen::" + esc("\n".join(blocks)[-45000:]))
print("::error title=Letzte Zeilen::" + esc("\n".join(clean[-70:])[-20000:]))
