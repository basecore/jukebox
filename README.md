# 🎵 Jukebox PWA (v62 Stats)

**Die smarte DIY "Toniebox" fürs Handy – 100% AI-Generated Code.**

Dieses Projekt ist eine kinderfreundliche Musik-Player-App, die alte Smartphones in sichere, werbefreie Abspielgeräte verwandelt. Sie läuft als **Progressive Web App (PWA)** komplett offline im Browser.

> 🤖 **Made with Gemini:** Dieses gesamte Projekt (HTML, CSS, JavaScript Logik, Datenbank-Struktur) wurde vollständig durch **Google Gemini 3 Pro** erstellt und analysiert. Es ist ein Experiment, wie weit KI-gestützte Entwicklung ohne manuelles Coden gehen kann.

---

## ✨ Neue Funktionen in v62

* 📊 **Detaillierte Eltern-Statistik:** Ein neues Dashboard im Eltern-Modus zeigt genau an:
    * Hördauer (Heute / Woche / Gesamt).
    * Die Top 5 Lieblings-Hörspiele.
    * Tageszeit-Heatmap (Wann wird gehört?).
    * Anzahl der Interaktionen (NFC-Scans, Umdrehen).
* 🛠️ **Bugfixes:**
    * Das seitliche "Wackeln" des Bildschirms im Kinder-Modus wurde behoben.
    * Lange Dateinamen im Editor werden nun korrekt umgebrochen.
* 💾 **Datenbank Upgrade:** Automatische Migration auf DB-Version 2 für das Event-Logging.

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

### 🔧 Eltern-Modus & Statistik
Verwaltung der Inhalte und Einsicht in das Nutzungsverhalten.

| **Verwaltung** | **Statistik (Neu)** |
|:---:|:---:|
| <img src="docs/screenshots/parent-mode.png" width="180"> | <img src="docs/screenshots/stats_view.png" width="180"> |
| *Tags anlernen & Import* | *Hörverhalten analysieren* |

---

## 🚀 Installation

Da es eine PWA ist, gibt es keinen App-Store-Download. Die App läuft lokal auf deinem Gerät.

1.  **Hosting:** Lade die Dateien (`index.html`, `sw.js`, `manifest.json`, `assets/`) auf einen Webspace (https erforderlich) oder starte einen lokalen Server.
2.  **Öffnen:** Rufe die URL im **Chrome (Android)** oder **Safari (iOS)** auf.
3.  **Installieren:**
    * **Android:** Tippe auf das Menü (3 Punkte) -> "Zum Startbildschirm hinzufügen" (oder "App installieren").
    * **iOS:** Tippe auf "Teilen" -> "Zum Home-Bildschirm".
4.  **Starten:** Öffne die neue App auf dem Homescreen. Sie läuft nun im Vollbild ohne Browser-Leiste.

---

## 📖 Bedienung

### 1. Musik hinzufügen
Die App unterstützt zwei Wege:

* **A) Massen-Import (Empfohlen):**
    Erstelle Ordner mit MP3s und Covern am PC und lade sie über "Massen-Import" hoch. Die App erkennt Zusammenhänge automatisch. Besonders gut funktioniert dies mit der `jukebox.json`, die unser Python-Tool erstellt (siehe unten).
* **B) Manuell anlernen:**
    Gehe auf "Neuen Tag anlernen", wähle Audio & Bild und fülle im Menü **"📝 Erweiterte Infos"** Details wie Beschreibung und Alter aus.

### 2. NFC Tags nutzen (Optional)
Wenn dein Android-Gerät NFC hat:
1.  Gehe auf "Tag scannen & speichern".
2.  Halte eine NFC-Karte oder Figur an das Handy.
3.  Die Musik ist nun mit diesem Tag verknüpft. Im Kinder-Modus startet sie sofort beim Auflegen.

### 3. Kinder-Modus verlassen
Es gibt keinen sichtbaren "Zurück"-Button, damit Kinder die App nicht versehentlich schließen.
➡️ **Tippe 5x schnell hintereinander in die obere rechte Ecke des Bildschirms, um in den Eltern-Modus zurückzukehren.**

---

## 🪄 Das Python-Tool: TAF zu Jukebox

Hast du **eigene Tonie-Dateien (.taf)**? Du kannst diese mit dem beiliegenden Skript `taf_jukebox_final.py` (im Ordner `tools/`) vollautomatisch für die App konvertieren.

**Das Script erledigt alles:**
1.  Wandelt `.taf` (Tonie-Format) in `.mp3` um (inkl. Kapitelmarken in einer `.cue` Datei).
2.  Lädt das **Original-Cover** herunter.
3.  Holt **Metadaten** (Beschreibungstext, Altersempfehlung, Genre) von der Tonie-Website.
4.  Erstellt eine perfekte `jukebox.json` für den Import.

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

## 📂 Dateistruktur

* `index.html` - Der gesamte Quellcode der Anwendung (Logik & Design, v62).
* `sw.js` - Der Service Worker für die Offline-Funktionalität (Cache v62).
* `manifest.json` - Konfiguration für das App-Icon und den Vollbild-Modus.
* `assets/` - Ordner für Icons und Test-Sounds.
* `tools/` - Enthält das Python-Script für den Import von Tonie-Dateien.

---

## 🔗 Projekt & Support

* 🏠 **Projekt:** [github.com/basecore/jukebox](https://github.com/basecore/jukebox/)
* 🐛 **Fehler melden:** [Issues & Bugs](https://github.com/basecore/jukebox/issues)

## 👨‍💻 Credits
Entwickelt von Sebastian Rößer mit Unterstützung von Google Gemini 3 Pro.
Version 62 "Stats Edition".
