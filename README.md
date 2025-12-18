# 🎵 Jukebox NFC - V24

Die ultimative **DIY Toniebox-Alternative** für dein Smartphone.
Verwandle dein Android-Handy in einen kinderleichten, NFC-gesteuerten Hörspiel-Player. Perfekt für unterwegs, im Auto oder im Urlaub.

## ✨ Die Story: "Vibe Coding"
Dieses Projekt ist ein Experiment in **"Vibe Coding"**.
Ich habe **keine einzige Zeile Code selbst geschrieben**. Die gesamte App – von der NFC-Logik über das Datenbank-Design bis hin zu den SVG-Icons – wurde vollständig durch Dialoge mit **Google Gemini** erstellt.

Es ist der Beweis, dass man mit einer guten Idee und KI funktionierende Software bauen kann.

---

## 🚀 Features (V24)

* **100% Kostenlos & Offline-Fähig:** Läuft als PWA (Web-App) direkt auf deinem Handy. Keine Werbung, kein Tracking.
* **Kinder-Modus:**
    * Vollbild-Player mit großen Tasten.
    * **NEU:** Personaliserbares Design! Wähle eine **Hintergrundfarbe** oder lade ein **eigenes Bild** hoch (wird in der Datenbank gespeichert).
    * **NEU:** Bunte Knöpfe optional aktivierbar (Rot, Gelb, Blau, Lila) für einfache Anweisungen ("Drück den roten Knopf").
* **Smarte Technik:**
    * **Playlist-Support:** Spielt Hörbücher mit vielen Kapiteln (CD1, CD2...) nacheinander ab.
    * **Merk-Funktion:** Die App weiß genau, wo das Kind bei "Benjamin Blümchen" aufgehört hat (z.B. Track 3, Minute 12).
    * **Smart Backup:** Sichere deine gesamte Datenbank (inkl. Einstellungen & Design!). Beim Handywechsel kannst du deine MP3s einfach neu auswählen ("Smart Repair"), und alles ist wieder da.
* **Einstellungen:** Start-Modus (direkt Kinder-Modus oder Admin), Max-Lautstärke, Schlaf-Timer.

## ⚠️ WICHTIGE HINWEISE

1.  **Hardware:** Du benötigst ein **Android-Smartphone mit NFC** und den **Chrome Browser**. (Firefox unterstützt kein Web-NFC).
2.  **Keine Original Tonies:** Die App funktioniert mit **leeren NTAG213 oder NTAG215 Stickern** (Cent-Artikel). Originale Tonie-Figuren sind verschlüsselt und funktionieren nicht.
3.  **Hosting:** Die App muss über **HTTPS** laufen (z.B. GitHub Pages), sonst verweigert Android den NFC-Zugriff.

## 🛠️ Installation (in 5 Minuten)

Da dies eine Web-App ist, musst du nichts aus dem App-Store laden.

1.  **Hosting:** Lade die Dateien (`index.html`, `manifest.json`, `sw.js`, `icon.png`) in ein öffentliches GitHub Repository hoch und aktiviere **GitHub Pages** in den Einstellungen.
2.  **Aufrufen:** Öffne deine neue Webseite (`https://dein-name.github.io/jukebox/`) in **Chrome** auf dem Android-Handy.
3.  **Installieren:**
    * Tippe auf das Menü (3 Punkte).
    * Wähle **"App installieren"** oder **"Zum Startbildschirm hinzufügen"**.
    * *Hinweis bei Samsung/iodeOS:* Die App landet oft erst im App-Menü (nicht direkt auf dem Homescreen). Suche dort nach "Jukebox".

## 🎮 Bedienung

### Eltern-Modus (Admin)
* **Neuen Tag anlernen:** Wähle Audio-Dateien (eine oder mehrere für Playlists), optional ein Bild und einen Namen. Klicke auf "Scannen" und halte den NFC-Tag an das Handy.
* **Design:** Wähle unter "Design für Kinder-Modus" ein Hintergrundbild oder eine Farbe.
* **Backup:** Erstelle regelmäßig ein Backup. Die Datei enthält alle Verknüpfungen und Einstellungen.

### Kinder-Modus
* Klicke auf den großen grünen Button oben.
* Das Kind muss nur noch den Tag an das Handy halten -> Musik spielt!
* **Zurück zum Admin:** Tippe **5x schnell** in die obere rechte Ecke des Bildschirms.

---

*Viel Spaß mit deiner Jukebox!*
*Created by **Sebastian Rößer** with the help of **Google Gemini**.*
