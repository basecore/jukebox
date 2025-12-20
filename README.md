# 🎵 Jukebox PWA (v33) - Die DIY "Toniebox" fürs Handy

Eine kinderfreundliche Musik-Player-App, die als Progressive Web App (PWA) direkt im Browser läuft. Sie ermöglicht es, Musik und Hörspiele über **NFC-Tags** (wie bei einer Toniebox) zu starten. Ideal, um alten Smartphones neues Leben als Kinder-Abspielgerät einzuhauchen.

Entwickelt als lokale Lösung ohne Cloud-Zwang, ohne Tracking und komplett kostenlos.

---

## 📸 Vorschau

| **Eltern-Modus (Admin)** | **Kinder-Modus (Player)** |
|:---:|:---:|
| <img src="docs/screenshots/parent1.png" width="180"> <img src="docs/screenshots/parent2.png" width="180"> <img src="docs/screenshots/parent3.png" width="180"> | <img src="docs/screenshots/children1.png" width="180"> <img src="docs/screenshots/children2.png" width="180"> <img src="docs/screenshots/children3.png" width="180"> |
| *Tag-Verwaltung, Settings & Upload* | *Einfache Bedienung, Cover & Visuals* |

---

## ⚠️ Wichtige Hinweise & Limitierungen

Da dies eine Web-App ist, die auf Standard-Smartphone-Hardware läuft, gibt es Unterschiede zur echten Toniebox:

1.  **❌ Keine "Wegnahme"-Erkennung:**
    * Die Musik stoppt **nicht**, wenn die Figur vom Handy genommen wird.
    * *Grund:* Smartphone-NFC-Leser registrieren nur den Moment des "Scannens" (einmaliges Event).
    * *Lösung:* Zum Stoppen muss der Pause-Button auf dem Display gedrückt werden.

2.  **⚠️ iOS / iPhone Einschränkungen:**
    * Apple unterstützt *Web NFC* im Safari-Browser aktuell noch nicht.
    * *Folge:* Auf iPhones funktioniert die App nur als Player (Manuelle Auswahl). Das **Anlernen und Scannen von Tags geht nur unter Android**.

3.  **🔓 Original-Tonies verwenden (Experten-Info):**
    * Grundsätzlich ist die App für **eigene NFC-Sticker (NTAG213/215)** gedacht.
    * Original-Tonies sind oft verschlüsselt oder im "Privacy Mode".
    * **Möglichkeit ("Klopf-Methode"):** Wenn du eine Tonie-Figur verwenden willst, klopfe sie mehrmals schnell gegen eine echte Toniebox (aktiviert). Dies öffnet kurzzeitig den Privacy-Modus, sodass das Handy die ID lesen kann.
    * **Nachteil:** Sobald die Figur wieder regulär auf einer Toniebox stand, ist der Modus wieder zu und du musst erneut "klopfen", bevor das Handy sie erkennt.
    * **Wichtig:** Die App liest **nicht** die Musik von der Figur! Du musst die Audio-Datei (MP3) selbst besitzen und auf das Handy laden.
    * *Tipp:* Um Audio von deinen eigenen Tonies zu sichern/konvertieren, nutze das Python-Script `tools/taf2mp3_smart.py` in diesem Repository.

---

## ✨ Features (v33)

### 🚀 Performance & Komfort
* **⚡ Auto-Start NFC (Neu in v33):** Der Scanner startet nun sofort, wenn der Kinder-Modus geöffnet wird. Kein extra Tippen aufs Display mehr nötig (auf unterstützten Geräten).
* **💾 Smart Resume:** Die App speichert die Position sofort beim Pausieren oder Minimieren. Beim nächsten Start des gleichen Tags geht es exakt dort weiter.

### 🎧 Audio & Steuerung
* **🔊 Intelligente Lautstärkebegrenzung:** Du legst ein Limit fest (z.B. 40%). Der Lautstärkebalken im Kinder-Modus skaliert sich darauf (Logarithmisch für natürliches Hören).
* **📜 CUE-Sheet Support:** Lade `.cue`-Dateien hoch, um echte Kapitelnamen anzuzeigen und den `⏭️` Skip-Button zu nutzen.
* **⏱️ Anzeige:** Korrekte Zeitanzeige in `mm:ss`.

### 🔋 Energie & Display
* **🌗 Eco-Modus (OLED-Sparmodus):**
    * Legt man das Handy mit dem Display nach unten auf den Tisch, wird der Bildschirm schwarz.
    * Die Musik läuft weiter, das Handy sperrt sich nicht. Spart extrem Akku.
* **💡 Screen Wake Lock:** Verhindert, dass das Handy in den Sperrbildschirm geht (nutzt Video-Loop-Trick für maximale Kompatibilität).

### 🛠️ Technik
* **Offline-First:** Alle Daten (MP3, Cover) werden im Browser-Speicher (IndexedDB) gehalten. Kein Internet nötig beim Abspielen.
* **Backup & Restore:** Datenbank kann exportiert und auf anderen Geräten importiert werden.

---

## 🛠️ Installation & Hardware

### 1. Benötigte Hardware
* **Android Smartphone** mit NFC (empfohlen).
* **NFC-Tags** (Typ: NTAG213, NTAG215 oder NTAG216) – oder Original-Tonies (siehe oben).
* Optional: Bluetooth-Lautsprecher.

### 2. Software-Setup (Hosting)
Damit Sensoren (Eco-Modus) und NFC funktionieren, **MUSS** die App über einen Server laufen.

**Option A: Lokal auf dem Handy (Offline / Empfohlen)**
1.  Erstelle einen Ordner `Jukebox` auf dem internen Speicher des Handys.
2.  Kopiere alle Dateien und Ordner (`index.html`, `assets/`, `sw.js`, etc.) dort hinein.
3.  Installiere eine Webserver-App (z.B. *"Web Server for Chrome"*).
4.  Starte den Server und öffne die Adresse (meist `http://127.0.0.1:8080`) in **Chrome**.

**Option B: Online (GitHub Pages)**
1.  Lade die Dateien in ein GitHub Repository hoch (inkl. aller Unterordner).
2.  Aktiviere "GitHub Pages" in den Repository-Einstellungen.
3.  Öffne die URL (`https://dein-name.github.io/...`) auf dem Handy.

### 3. Als App installieren (PWA)
1.  Öffne die URL in **Chrome** auf dem Android-Gerät.
2.  Tippe auf das Menü (3 Punkte) -> **"Zum Startbildschirm hinzufügen"** oder **"App installieren"**.
3.  Starte die App nun über das Icon auf dem Homescreen.

---

## 📖 Bedienungsanleitung

### Musik hinzufügen (Eltern-Modus)
1.  Klicke auf **"Neuen Tag anlernen"**.
2.  **Audio:** Wähle die MP3-Datei(en).
3.  **(Optional) Cue:** Wähle eine passende `.cue` Datei für Kapitelmarken.
4.  **Cover:** Wähle ein Bild.
5.  **Name:** Gib dem Hörspiel einen Namen.
6.  Klicke auf **"📡 Tag scannen & speichern"** und halte den NFC-Tag (oder geklopften Tonie) an die Rückseite.

### Einstellungen (WICHTIG!)
* ⚠️ **Hardware-Tasten:** Stelle die physischen Lautstärke-Tasten am Handy auf **100%**.
* **Limit:** Schiebe den Regler "Maximale Lautstärke" auf das gewünschte Limit.
* **Test:** Drücke auf **"🔊 Test-Ton"**, um die Maximallautstärke zu prüfen.

### Kinder-Modus verlassen
Es gibt keinen sichtbaren "Zurück"-Button.
➡️ **Tippe 5x schnell hintereinander in die obere rechte Ecke des Bildschirms.**

---

## 📂 Dateistruktur (Cleaned)

* `index.html` - Der komplette Code der App.
* `manifest.json` - PWA Konfiguration.
* `sw.js` - Service Worker (für Offline-Support).
* `assets/`
    * `img/` - Hintergrundbilder.
    * `icons/` - App Icons für Android/iOS.
* `docs/screenshots/` - Bilder für diese Anleitung.
* `tools/`
    * `taf2mp3_smart.py` - Script zum Konvertieren von Tonie-Dateien.
    * `eco_debug.html` - Test-Tool für Sensoren.

## 👨‍💻 Credits
Entwickelt von Sebastian Rößer.
Ein Open-Source Projekt für Eltern, die die Kontrolle über ihre Audiodaten behalten wollen.
