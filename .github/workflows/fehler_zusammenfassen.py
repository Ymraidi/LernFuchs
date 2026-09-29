"""Fasst ein gescheitertes Buildozer-Protokoll zusammen und gibt es als GitHub-Hinweis aus."""

import re
import sys

try:
    log = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
except OSError:
    log = ["(kein build.log)"]

ANSI = re.compile(r"\x1b\[[0-9;]*m")
NOISE = re.compile(r"performance hint|Declare '|Use an 'int' return|^\s*#\s|Exception check on")
log = [ANSI.sub("", line) for line in log]
clean = [line for line in log if not NOISE.search(line)]

cut = len(clean)
for i, line in enumerate(clean):
    if "Command failed" in line or "Buildozer failed" in line:
        cut = i
        break
before = clean[max(0, cut - 90):cut + 3]
hits = [line for line in clean
        if re.search(r"\berror\b|Error:|ERROR|failed|Traceback|ModuleNotFound|No such file|not found", line)]


def esc(text):
    return text.replace("%", "%25").replace("\r", "").replace("\n", "%0A")


print("::error title=Vor dem Abbruch::" + esc("\n".join(before)[-40000:]))
print("::error title=Fehlerzeilen::" + esc("\n".join(hits[-40:])[-20000:]))
