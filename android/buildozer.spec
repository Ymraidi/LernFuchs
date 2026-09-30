[app]
title = LernFuchs
package.name = lernfuchs
package.domain = de.lernfuchs
source.dir = .
source.include_exts = py,png,jpg,json,zip,wav,ttf
source.exclude_dirs = tools,bin,.buildozer
version = 3.0.0
# Die reinen Python-Pakete „emoji“ und „filetype“ (von Kivy 2.3.1 benötigt) liegen direkt in emoji/ bzw. filetype/
# (spart den pip-Schritt beim Bauen)
requirements = python3,kivy==2.3.1,pillow,pyjnius,android
orientation = landscape
fullscreen = 1
icon.filename = %(source.dir)s/assets/icon.png
presplash.filename = %(source.dir)s/assets/presplash.png
android.presplash_color = #0E1525

# Android-Version: Tablets ab Android 7
android.api = 34
android.minapi = 24
android.archs = arm64-v8a, armeabi-v7a
android.accept_sdk_license = True
android.allow_backup = True

# Stabile Version des Bauwerkzeugs (die Entwicklerversion nutzt Python 3.14, dort ist pip derzeit defekt)
p4a.branch = v2024.01.21
# Keine Berechtigungen nötig: alles läuft offline, Sprache über die Android-Sprachausgabe.

[buildozer]
log_level = 2
warn_on_root = 0
