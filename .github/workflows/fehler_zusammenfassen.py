"""Fasst ein gescheitertes Buildozer-Protokoll zusammen (mehrere kurze GitHub-Hinweise, je < 4000 Zeichen)."""

import re
import sys

try:
    log = open(sys.argv[1], encoding="utf-8", errors="replace").read().splitlines()
except OSError:
    log = ["(kein build.log)"]

ANSI = re.compile(r"\x1b\[[0-9;]*m")
NOISE = re.compile(r"performance hint|Declare '|Use an 'int' return|Exception check on|^\s*#\s|^export |\.pyc\b|"
                   r"checking |^\s*$")
log = [ANSI.sub("", line).strip()[:220] for line in log]
clean = [line for line in log if not NOISE.search(line)]

# Buildozer hängt am Ende eine lange Umgebungsliste an – alles ab dem Abbruch-Hinweis zählt nicht
end = len(clean)
for i in range(len(clean) - 1, -1, -1):
    if "Buildozer failed" in clean[i] or "Command failed" in clean[i]:
        end = i + 1
        break
tail = clean[max(0, end - 60):end]


def esc(text):
    return text.replace("%", "%25").replace("\r", "").replace("\n", "%0A")


chunk, n = [], 0
for line in tail:
    chunk.append(line)
    if sum(len(x) + 1 for x in chunk) > 3500:
        n += 1
        print(f"::error title=Ende Teil {n}::" + esc("\n".join(chunk)))
        chunk = []
if chunk:
    n += 1
    print(f"::error title=Ende Teil {n}::" + esc("\n".join(chunk)))

MARK = re.compile(r"BUILD FAILED|FAILURE:|What went wrong|Error:|error:|ErrorReturnCode|Exception:", re.I)
marks = [line for line in clean[:end] if MARK.search(line)]
print("::warning title=Fehlermarken::" + esc("\n".join(marks[-15:])[-3500:]))
