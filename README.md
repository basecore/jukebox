# 🎵 Jukebox PWA (v61 Stable) - Die DIY "Toniebox" fürs Handy

Eine kinderfreundliche Musik-Player-App, die als Progressive Web App (PWA) direkt im Browser läuft. Sie verwandelt alte Smartphones in sichere Abspielgeräte für Kinder.

**Aktuell in v61:** Diese Version beinhaltet wichtige Optimierungen für die **Bibliotheks-Ansicht**, damit diese auf allen Geräten zuverlässig öffnet. Zudem sind der neue **Rewind-Button** (30s zurück) und die **Smart-Start-Logik** (Resume bei erneutem Scan) enthalten.

Entwickelt als lokale Lösung: **Kein Cloud-Zwang, kein Tracking, komplett kostenlos.**

---

## 📸 Vorschau

Die App ist in zwei Bereiche unterteilt: Den geschützten **Eltern-Modus** (Verwaltung) und den kindersicheren **Player-Modus**.

### 👶 Kinder-Modus & Bibliothek
Hier spielen die Kinder. Große Bilder, keine Text-Menüs, einfache Bedienung.

| **Der Player (Neu: Rewind)** | **Die Bibliothek** |
|:---:|:---:|
| <img src="docs/screenshots/kid-mode1.png" width="180"> | <img src="docs/screenshots/library_grid.png" width="180"> |
| *Große Steuerung & Cover* | *Visuelles Stöbern & Filtern* |

| **Info-Overlay** | **Details & Dauer** |
|:---:|:---:|
| <img src="docs/screenshots/library_info.png" width="180"> | <img src="docs/screenshots/kid-mode2.png" width="180"> |
| *Beschreibung & Alter* | *Einfacher Player* |

### 🔧 Eltern-Modus (Admin)
Hier verwaltest du die Datenbank, importierst Musik und stellst Limits ein.

| **Admin Grid-Ansicht** | **Metadaten-Editor** |
|:---:|:---:|
| <img src="docs/screenshots/parent-mode3.png" width="180"> | <img src="docs/screenshots/parent-edit.png" width="180"> |
| *Tags visuell verwalten* | *Infos direkt ändern* |

| **Einstellungen** | **Massen-Import** |
|:---:|:---:|
| <img src="docs/screenshots/parent-mode1.png" width="180"> | <img src="docs/screenshots/parent-mode4.png" width="180"> |
| *Lautstärkelimit & Timer* | *Ordner einfach hochladen* |

---

## 📲 Installation (Android)

Die App muss nicht über den Play Store geladen werden, sondern wird direkt über den Browser installiert.

1.  Öffne **Chrome** auf deinem Android-Smartphone.
2.  Rufe die Webseite auf: **[https://basecore.github.io/jukebox/](https://basecore.github.io/jukebox/)**
3.  **Warte kurz (bis zu 30 Sekunden):** Oft erscheint am unteren Bildschirmrand automatisch ein Hinweis *"Jukebox zum Startbildschirm hinzufügen"*.
4.  Falls nicht, folge diesen Schritten:

| **1. Menü öffnen** | **2. Installieren** |
|:---:|:---:|
| <img src="docs/screenshots/install-app1.png" width="180"> | <img src="docs/screenshots/install-app2.png" width="180"> |
| *Tippe oben rechts auf die 3 Punkte* | *Wähle "App installieren"* |

| **3. Bestätigen** | **4. Widget platzieren** |
|:---:|:---:|
| <img src="docs/screenshots/install-app3.png" width="180"> | <img src="docs/screenshots/install-app4.png" width="180"> |
| *Klicke auf "Installieren"* | *Automatisch oder ziehen* |

---

## ✨ Neue Features (v61)

### 👶 Player-Upgrades
* **⏪ Rewind-Button:** Ein neuer Button erlaubt es, **30 Sekunden zurückzuspringen**. Perfekt, wenn das Kind kurz abgelenkt war.
* **🧠 Smart Start:** Wird derselbe NFC-Tag während der Wiedergabe erneut aufgelegt, fängt das Hörspiel nicht mehr von vorne an, sondern läuft einfach weiter (oder pausiert/startet an aktueller Stelle).

### 🛠️ Admin Power-Up
* **Smart Scroll:** Ein Klick auf "Bearbeiten" springt nun direkt zum Eingabeformular, ohne dass du scrollen musst.
* **Admin Grid-Ansicht:** Verwalte Tags als Kacheln mit Covern. Umschaltbar auf Listenansicht (☰).
* **In-App Editor:** Bearbeite **Beschreibung, Alter, Genre und Laufzeit** direkt in der App. Du siehst nun auch die echten Dateinamen der verknüpften MP3s.

### 📚 Die Bibliothek (Tigerbox-Style)
* **Visuelle Übersicht:** Große Cover-Kacheln in einem übersichtlichen Raster.
* **Filter & Verlauf:** Filtere nach Alter ("Ab 3 Jahren") oder Genre und sieh dir die zuletzt gehörten Titel an.
* **Info-Overlay:** Ein Klick auf das "i" zeigt Details zum Hörspiel.

---

## 🪄 Das Python-Tool: TAF zu Jukebox

Wenn du **eigene Tonie-Dateien (.taf)** besitzt, kannst du diese mit dem Skript `taf_jukebox_final.py` (im Ordner `tools/`) vollautomatisch für die App aufbereiten.

**Das Script erledigt alles:**
1.  Wandelt `.taf` in `.mp3` um (inkl. Kapitelmarken in einer `.cue` Datei).
2.  Lädt das **Original-Cover** herunter.
3.  Holt **Metadaten** (Beschreibungstext, Altersempfehlung, Genre) von der Tonie-Website.
4.  Erstellt die perfekte `jukebox.json` für den Import.

### Anleitung für PC/Mac:

1.  **Vorbereitung:**
    * Installiere [Python](https://www.python.org/).
    * Installiere [FFmpeg](https://ffmpeg.org/) (muss im System-Pfad sein).
2.  **Dateien ablegen:**
    * Kopiere das Script `taf_jukebox_final.py` und deine `.taf`-Dateien in einen gemeinsamen Ordner.
3.  **Abhängigkeiten installieren:**
    Öffne ein Terminal in dem Ordner und führe aus:
    ```bash
    pip install requests beautifulsoup4 playwright
    playwright install
    ```
4.  **Script starten:**
    ```bash
    python taf_jukebox_final.py
    ```
5.  **Ergebnis:**
    Es entsteht ein Ordner `jukebox_output`. Diesen Ordner kannst du nun direkt über **"📂 Massen-Import"** in die App laden!

---

## 📖 Bedienungsanleitung

### 1. Musik hinzufügen
Die App unterstützt zwei Wege:

* **A) Massen-Import (Empfohlen):**
    Erstelle Ordner mit MP3s und Covern am PC und lade sie über "Massen-Import" hoch. Wenn du eine `jukebox.json` hast (vom Python-Tool), werden alle Infos automatisch gesetzt.
* **B) Manuell anlernen:**
    Gehe auf "Neuen Tag anlernen", wähle Audio & Bild und fülle im neuen Menü **"📝 Erweiterte Infos"** die Beschreibung und das Alter aus.

### 2. Einstellungen
* **Lautstärke:** Stelle sicher, dass die physische Handy-Lautstärke auf 100% steht und regle das Limit in der App.
* **Kindersicherung:** Du kannst den Bibliotheks-Button im Kinder-Modus ausblenden, falls gewünscht.

### 3. Kinder-Modus verlassen
Es gibt keinen sichtbaren "Zurück"-Button, damit Kinder nicht aus Versehen rausgehen.
➡️ **Tippe 5x schnell hintereinander in die obere rechte Ecke des Bildschirms.**

---

## 📂 Dateistruktur

* `index.html` - Der komplette Code (V61).
* `sw.js` - Offline-Logik (Cache V61).
* `manifest.json` - App-Icon Konfiguration.
* `assets/` - Bilder und Icons.
* `jukebox.json` - Deine Datenbank (Optional).
* `tools/` - Python-Script für den Import.

---

## 🔗 Projekt & Support

* 🏠 **Projekt:** [github.com/basecore/jukebox](https://github.com/basecore/jukebox/)
* 🐛 **Fehler melden:** [Issues & Bugs](https://github.com/basecore/jukebox/issues)

## 👨‍💻 Credits
Entwickelt von Sebastian Rößer.
Version 61 "Stable".
