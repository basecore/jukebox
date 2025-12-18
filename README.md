# 🎵 Jukebox PWA (v26) - DIY "Toniebox" für das Handy

Eine kinderfreundliche Musik-Player-App, die als Progressive Web App (PWA) direkt im Browser läuft. Sie ermöglicht es, Musik und Hörspiele über **NFC-Tags** (wie bei einer Toniebox) zu starten. Ideal, um alten Smartphones neues Leben als Kinder-Abspielgerät einzuhauchen.

Entwickelt als lokale Lösung ohne Cloud-Zwang, ohne Tracking und komplett kostenlos.

## ✨ Neue Features in v26
* **🔋 Eco-Mode (OLED Sparmodus):** Dreht man das Handy auf das Display (Face-down), wird der Bildschirm schwarz, aber die Musik läuft weiter. Spart extrem viel Akku bei OLED-Displays und verhindert versehentliches Tippen.
* **💡 Screen Wake Lock:** Verhindert, dass das Handy in den Sperrbildschirm geht, während Musik läuft.
* **🔊 Audio-Test:** Ein Button in den Einstellungen spielt einen Test-Ton, um die maximale Lautstärke sicher für Kinderohren einzustellen.
* **⏱️ mm:ss Anzeige:** Die Zeit wird nun korrekt zweistellig (04:05) angezeigt.
* **📱 iOS Support (Beta):** Button zum Freigeben der Bewegungssensoren auf iPhones (für den Eco-Modus). *Hinweis: NFC-Schreiben/Lesen funktioniert primär unter Android Chrome.*

## 🚀 Funktionen
* **NFC-Steuerung:** Musik durch Auflegen von Figuren/Karten starten.
* **Kinder-Modus:**
    * Große, bunte Tasten.
    * Gesperrte Einstellungen.
    * Geheimer Ausweg (5x Tippen).
* **Eltern-Bereich:**
    * Tags anlernen & verwalten.
    * Maximale Lautstärke begrenzen.
    * Schlaf-Timer (Fade-out).
    * Design anpassen (Hintergrundbild oder Farbe).
    * Datenbank Backup & Restore.
* **Offline-Fähig:** Speichert Musik und Cover direkt im Browser (IndexedDB).

## 🛠️ Installation & Voraussetzungen

### Benötigte Hardware
1.  **Android Smartphone** mit NFC (empfohlen).
2.  **NFC-Tags** (NTAG213, NTAG215 oder NTAG216) – z.B. Sticker, Karten oder Schlüsselanhänger.
3.  Optional: Bluetooth-Lautsprecher für besseren Klang.

### Software-Setup (Hosting)
Da die App auf Hardware-Funktionen (NFC, Service Worker) zugreift, muss sie entweder über **HTTPS** oder via **localhost** laufen.

**Option A: Einfach (GitHub Pages / Netlify)**
1.  Lade die Dateien (`index.html`, `manifest.json`, `sw.js`, Icons) in ein GitHub Repository hoch.
2.  Aktiviere "GitHub Pages" in den Einstellungen.
3.  Öffne die URL auf dem Handy.

**Option B: Lokal (Android)**
1.  Verbinde das Handy mit dem PC.
2.  Erstelle einen Ordner `Jukebox` auf dem Handy.
3.  Kopiere alle Dateien hinein.
4.  Nutze eine App wie "Web Server for Chrome" auf dem Handy, um den Ordner auf `localhost:8080` bereitzustellen.

### PWA Installation
1.  Öffne die URL in **Google Chrome** auf dem Android-Gerät.
2.  Tippe auf das Menü (3 Punkte) -> **"Zum Startbildschirm hinzufügen"** oder **"App installieren"**.
3.  Starte die App nun über das Icon auf dem Homescreen (damit verschwindet die Adressleiste).

## 📖 Bedienungsanleitung

### 1. Musik hinzufügen (Eltern-Modus)
1.  Klicke auf **"Neuen Tag anlernen"**.
2.  Wähle eine oder mehrere MP3-Dateien aus (`1. Audio Datei`).
3.  (Optional) Wähle ein Cover-Bild (`2. Cover Bild`).
4.  Vergib einen Namen.
5.  Klicke auf **"📡 Tag scannen & speichern"**.
6.  Halte den NFC-Tag an die Rückseite des Handys.
7.  *Fertig!*

### 2. Kinder-Modus aktivieren
1.  Klicke ganz oben auf **"▶ ZUM KINDER-MODUS"**.
2.  Das Design ändert sich, Menüs verschwinden.
3.  Das Kind kann nun Tags auflegen, um Musik zu hören.

### 3. Kinder-Modus verlassen (WICHTIG!)
Es gibt keinen sichtbaren "Zurück"-Button, damit Kinder nicht aus Versehen die Einstellungen öffnen.
➡️ **Tippe 5x schnell hintereinander in die obere rechte Ecke des Bildschirms.**

### 4. Einstellungen
* **Display anlassen:** Aktivieren, damit das Display an bleibt (Cover sichtbar).
* **Stromsparen beim Umdrehen:** Aktivieren, Handy auf das Display legen -> Bildschirm aus (Audio an).
* **Lautstärke:** Schieberegler nutzen und mit dem "Test-Ton" prüfen.

## 📂 Dateistruktur

* `index.html` - Der komplette Code der App (Logic & Design).
* `manifest.json` - Konfiguration für die Installation als App.
* `sw.js` - Service Worker (für Offline-Support, muss im selben Ordner liegen).
* `icon.png` / `icon512_rounded.png` - App Icons.

## ⚠️ Wichtige Hinweise
* **Browser:** Nutze **Chrome** auf Android. Firefox oder Samsung Internet unterstützen WebNFC oft nicht vollständig.
* **iOS/iPhone:** Apple unterstützt *Web NFC* aktuell (Stand 2025) noch nicht in Safari. Die App läuft dort als Player, aber das Scannen von Tags funktioniert nur unter Android.
* **Speicher:** Die Musik wird im Browserspeicher abgelegt. Wenn du die "Browserdaten löschst", ist die Musik weg! Nutze die **Backup-Funktion** in den Einstellungen.

## 👨‍💻 Credits
Entwickelt von Sebastian Rößer.
Ein Open-Source Projekt für Eltern, die die Kontrolle über ihre Audiodaten behalten wollen.
