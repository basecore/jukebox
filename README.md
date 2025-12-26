# 🎵 Jukebox PWA (v66 Stable)

**Die smarte DIY "Toniebox" fürs Handy – 100% AI-Generated Code.**

Dieses Projekt ist eine kinderfreundliche Musik-Player-App, die alte Smartphones in sichere, werbefreie Abspielgeräte verwandelt. Sie läuft als **Progressive Web App (PWA)** komplett offline im Browser.

> 🤖 **Made with Gemini:** Dieses gesamte Projekt (HTML, CSS, JavaScript Logik, Datenbank-Struktur) wurde vollständig durch **Google Gemini 3 Pro** erstellt und analysiert. Es ist ein Experiment, wie weit KI-gestützte Entwicklung ohne manuelles Coden gehen kann.

---

## ✨ Neue Funktionen in v66

* ✅ **Fortschritts-Anzeige:** Hörspiele, die komplett zu Ende gehört wurden, erhalten nun einen **grünen Haken** auf dem Cover.
* 📊 **Detaillierte Eltern-Statistik:**
    * Dashboard zeigt Hördauer, Top 5 Hörspiele, Tageszeit-Nutzung & „Vollständig gehört".
    * **Fix:** Das Schließen-Problem (X-Button) wurde behoben.
* 🛠️ **System-Updates:**
    * **Fix:** Der Bibliotheks-Button im Kinder-Modus ist nun immer erreichbar (fixierte Position).
    * Verbesserter „Wackelschutz" im Kinder-Modus.
    * Lange Dateinamen werden im Editor nun korrekt umgebrochen.

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
| *Tags anlernen & Import* | *Hörverhalten & Fortschritt (✅)* |

---

# 📲 Installation (Android)

Die App muss nicht über den Play Store geladen werden, sondern wird direkt über den Browser installiert.

1. Öffne **Chrome** auf deinem Android-Smartphone.
2. Rufe die Webseite auf: **https://basecore.github.io/jukebox/**
3. **Warte kurz (bis zu 30 Sekunden):** Oft erscheint am unteren Bildschirmrand automatisch ein Hinweis „Jukebox zum Startbildschirm hinzufügen".
4. Falls nicht, folge diesen Schritten:

| **1. Menü öffnen** | **2. Installieren** |
|:---:|:---:|
| <img src="docs/screenshots/install-app1.png" width="180"> | <img src="docs/screenshots/install-app2.png" width="180"> |
| *Tippe oben rechts auf die 3 Punkte* | *Wähle „App installieren"* |

| **3. Bestätigen** | **4. Widget platzieren** |
|:---:|:---:|
| <img src="docs/screenshots/install-app3.png" width="180"> | <img src="docs/screenshots/install-app4.png" width="180"> |
| *Klicke auf „Installieren"* | *Automatisch oder ziehen* |

*(iOS Nutzer verwenden Safari → Teilen → Zum Home-Bildschirm)*

---

## 📖 Bedienung

### 1. Musik hinzufügen

Die App unterstützt zwei Wege:

* **A) Massen-Import (Empfohlen):**
    Erstelle Ordner mit MP3s und Covern am PC und lade sie über „Massen-Import" hoch. **Tipp:** Wenn du unser Python-Tool (siehe unten) nutzt, wird eine `jukebox.json` erstellt. Wähle diese Datei und den Ordner aus – dann sind alle Titel, Cover und Texte sofort perfekt gesetzt!
* **B) Manuell anlernen:**
    Gehe auf „Neuen Tag anlernen", wähle Audio & Bild und fülle im Menü **„📝 Erweiterte Infos"** Details wie Beschreibung und Alter aus.

### 2. NFC Tags nutzen (Optional)

Wenn dein Android-Gerät NFC hat:
1. Gehe auf „Tag scannen & speichern".
2. Halte eine NFC-Karte oder Figur an das Handy.
3. Die Musik ist nun mit diesem Tag verknüpft. Im Kinder-Modus startet sie sofort beim Auflegen.

### 3. Statistik ansehen (Neu in v66)

Klicke im Eltern-Modus oben rechts auf den Button **„📊 Statistik"**. Hier siehst du, was dein Kind wann und wie lange hört und welche Hörspiele bereits **vollständig (✅)** gehört wurden.

### 4. Kinder-Modus verlassen

Es gibt keinen sichtbaren „Zurück"-Button, damit Kinder die App nicht versehentlich schließen.
➡️ **Tippe 5× schnell hintereinander in die obere rechte Ecke des Bildschirms, um in den Eltern-Modus zurückzukehren.**

---

## 🚀 Schnellstart mit Beispielen

Im Repository-Ordner `example/` findest du vorbereitete Beispieldateien, mit denen du die App sofort testen kannst – komplett mit Cover-Bildern, Metadaten und Beschreibungen.

### Download der Beispieldateien

**Option 1: Einzelne Dateien herunterladen**

Öffne im Browser: https://github.com/basecore/jukebox/tree/main/example

Lade folgende Dateien herunter:
- `jukebox.json` – Metadaten-Datei mit allen Informationen
- `Die drei Schneeflocken der Freundschaft.mp3`
- `Die drei Schneeflocken der Freundschaft.png`
- `Schneeflocken.mp3`
- `Schneeflocken.png`
- `Wusel in der Werkstatt.mp3`
- `Wusel in der Werkstatt.png`

**Option 2: Komplettes Repository als ZIP (empfohlen)**

1. Gehe auf https://github.com/basecore/jukebox
2. Klicke auf den grünen **„Code"**-Button
3. Wähle **„Download ZIP"**
4. Entpacke die Datei und navigiere zum Ordner `jukebox/example/`

### Beispiele in die App importieren

1. Starte die Jukebox im Eltern-Modus
2. Klicke auf **„📂 Massen-Import"**
3. Wähle zunächst die `jukebox.json` aus
4. Wähle dann den Ordner mit den MP3- und PNG-Dateien
5. ✅ Fertig! Die Beispiel-Hörspiele erscheinen jetzt mit Cover, Altersempfehlung und Beschreibung in der Bibliothek

### Was ist in den Beispielen enthalten?

| Titel | Genre | Alter | Laufzeit |
|-------|-------|-------|----------|
| Die drei Schneeflocken der Freundschaft – Das Hörspiel | Hörspiel | 4+ | 5 Min |
| Schneeflocken – Das Lied | Musik | 3+ | 4 Min |
| Wusel in der Werkstatt | Hörspiel | 4+ | 1 Min |

Die `jukebox.json` definiert alle Metadaten: Seriennamen, Episodentitel, ausführliche Beschreibungen, Genre, Altersempfehlung, Sprache und passende Tags (Freundschaft, Winter, Abenteuer, Humor).

---

## 🪄 Das Python-Tool: TAF zu Jukebox

Hast du **eigene Tonie-Dateien (.taf)**? Du kannst diese mit dem beiliegenden Skript `taf_jukebox_final.py` (im Ordner `tools/`) vollautomatisch für die App konvertieren.

**Das Script erledigt alles:**
1. Wandelt `.taf` (Tonie-Format) in `.mp3` um (inkl. Kapitelmarken in einer `.cue` Datei).
2. Lädt das **Original-Cover** herunter.
3. Holt **Metadaten** (Beschreibungstext, Altersempfehlung, Genre) von der Tonie-Website.
4. Erstellt eine perfekte `jukebox.json` für den Import.

### Anleitung für PC/Mac

1. **Vorbereitung:**
    * Installiere [Python](https://www.python.org/)
    * Installiere [FFmpeg](https://ffmpeg.org/) (muss im System-Pfad sein)

2. **Dateien ablegen:**
    * Kopiere das Script `taf_jukebox_final.py` und deine `.taf`-Dateien in einen gemeinsamen Ordner

3. **Abhängigkeiten installieren:**
    Öffne ein Terminal in dem Ordner und führe aus:
    ```
    pip install requests beautifulsoup4 playwright
    playwright install
    ```

4. **Script starten:**
    ```
    python taf_jukebox_final.py
    ```

5. **Ergebnis:**
    Es entsteht ein Ordner `jukebox_output`. Diesen Ordner kannst du nun direkt über **„📂 Massen-Import"** in die App laden!

---

## 📂 Dateistruktur

* `index.html` – Der gesamte Quellcode der Anwendung (Logik & Design, v66)
* `sw.js` – Der Service Worker für die Offline-Funktionalität (Cache v66)
* `manifest.json` – Konfiguration für das App-Icon und den Vollbild-Modus
* `assets/` – Ordner für Icons und Test-Sounds
* `example/` – Beispieldateien (MP3s, PNGs, `jukebox.json`) für schnellen Start
* `tools/` – Enthält das Python-Script für den Import von Tonie-Dateien
* `docs/screenshots/` – Screenshots für diese Anleitung

---

## 🔗 Projekt & Support

* 🏠 **Projekt:** https://github.com/basecore/jukebox
* 🐛 **Fehler melden:** https://github.com/basecore/jukebox/issues

## 👨‍💻 Credits

Entwickelt von Sebastian Rößer mit Unterstützung von **Google Gemini 3 Pro**.  
Version 66 „Stable Stats Edition".
