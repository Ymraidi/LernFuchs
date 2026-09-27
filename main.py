"""LernFuchs starten: Doppelklick auf diese Datei oder auf „LernFuchs starten.bat“.

Liegt das Programm auf einem Netzlaufwerk (z. B. H:), wird es automatisch auf die lokale Festplatte
kopiert und von dort gestartet – das ist um ein Vielfaches schneller.
"""

import os
import shutil
import subprocess
import sys


def _is_network(path: str) -> bool:
    if os.name != "nt":
        return False
    full = os.path.abspath(path)
    if full.startswith("\\\\"):
        return True
    import ctypes
    drive = os.path.splitdrive(full)[0] + "\\"
    return ctypes.windll.kernel32.GetDriveTypeW(drive) == 4  # DRIVE_REMOTE


def _sync(src: str, dst: str):
    """Kopiert nur geänderte Dateien (schnell, auch über das Netzwerk)."""
    for root, dirs, files in os.walk(src):
        dirs[:] = [d for d in dirs if d != "__pycache__"]
        target = os.path.join(dst, os.path.relpath(root, src))
        os.makedirs(target, exist_ok=True)
        for fn in files:
            s, d = os.path.join(root, fn), os.path.join(target, fn)
            st = os.stat(s)
            if not os.path.exists(d) or os.path.getsize(d) != st.st_size or int(os.path.getmtime(d)) != int(st.st_mtime):
                shutil.copy2(s, d)


def _relaunch_locally(here: str) -> bool:
    base = os.path.join(os.environ.get("LOCALAPPDATA") or os.path.expanduser("~"), "LernFuchs", "app")
    try:
        _sync(os.path.join(here, "lernfuchs"), os.path.join(base, "lernfuchs"))
        shutil.copy2(os.path.abspath(__file__), os.path.join(base, "main.py"))
    except OSError:
        return False
    env = dict(os.environ, LERNFUCHS_LOCAL="1")
    env.setdefault("LERNFUCHS_BACKUP", os.path.join(here, "daten", "sicherung"))
    exe = sys.executable
    pyw = os.path.join(os.path.dirname(exe), "pythonw.exe")
    subprocess.Popen([pyw if os.path.exists(pyw) else exe, os.path.join(base, "main.py")], env=env, cwd=base)
    return True


if __name__ == "__main__":
    here = os.path.dirname(os.path.abspath(__file__))
    if not os.environ.get("LERNFUCHS_LOCAL") and _is_network(here) and _relaunch_locally(here):
        sys.exit(0)
    from lernfuchs.app import main
    main()
