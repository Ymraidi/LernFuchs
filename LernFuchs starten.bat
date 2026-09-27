@echo off
rem LernFuchs: kopiert das Programm auf die lokale Festplatte (schnell) und startet es von dort.
rem Das Profil wird beim Beenden zusaetzlich in "daten\sicherung" neben dieser Datei gesichert.
setlocal
set "SRC=%~dp0"
set "BASE=%LOCALAPPDATA%\LernFuchs"
set "DST=%BASE%\app"
robocopy "%SRC%lernfuchs" "%DST%\lernfuchs" /MIR /XD __pycache__ /NFL /NDL /NJH /NJS /NP >nul
copy /Y "%SRC%main.py" "%DST%\main.py" >nul
rem Pakete nur beim allerersten Start installieren (spart bei jedem Start einige Sekunden)
if not exist "%BASE%\pakete_v3.ok" (
    echo Einmalige Einrichtung: installiere benoetigte Pakete ...
    python -m pip install -r "%SRC%requirements.txt" && echo ok> "%BASE%\pakete_v3.ok"
)
set "LERNFUCHS_BACKUP=%SRC%daten\sicherung"
cd /d "%DST%"
start "" pythonw main.py
