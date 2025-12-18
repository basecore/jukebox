import os
import subprocess
import glob
import json
import hashlib
import requests
import shutil
import sys

# --- KONFIGURATION ---
SOURCE_DIR = "."         # Ordner mit TAF-Dateien
OUTPUT_DIR = "mp3_converted"
JSON_FILE = "tonies.json"
HEADER_SIZE = 4096       # TAF Header Größe

def show_setup_guide():
    """Zeigt eine ausführliche Anleitung am Anfang"""
    print("=" * 70)
    print("TAF zu MP3 Konverter mit Cover-Download & CUE-Export".center(70))
    print("=" * 70)
    print()
    print("📋 SCHRITT-FÜR-SCHRITT ANLEITUNG:")
    print()
    print("1. Vorbereitung:")
    print("   - Laden Sie die Datei 'tonies.json' herunter (von TeddyBench)")
    print("   - Speichern Sie diese Datei in den gleichen Ordner wie dieses Skript")
    print()
    print("2. TAF-Dateien vorbereiten:")
    print(f"   - Legen Sie alle zu konvertierenden .taf Dateien in: {os.path.abspath(SOURCE_DIR)}")
    print("   - (das ist der aktuelle Ordner, in dem dieses Skript liegt)")
    print()
    print("3. Abhängigkeiten installieren (einmalig):")
    print("   - Öffnen Sie die Eingabeaufforderung (CMD)")
    print("   - Führen Sie aus: py -m pip install requests")
    print()
    print("4. Dieses Skript starten:")
    print("   - Doppelklick auf taf2mp3_smart.py")
    print("   - oder: py taf2mp3_smart.py")
    print()
    print("5. Ergebnis:")
    print(f"   - MP3-Dateien landen in: {os.path.abspath(OUTPUT_DIR)}")
    print("   - Cover werden als separate .jpg-Dateien gespeichert")
    print("   - CUE-Dateien (mit Kapiteln) werden ebenfalls erstellt")
    print()
    print("=" * 70)
    print()

def load_tonies_json(json_path):
    """Lädt die tonies.json Datenbank"""
    print(f"📂 Lade Datenbank: {json_path}")
    print()
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Erstelle eine schnelle Such-Liste: Hash -> Eintrag
        hash_map = {}
        for entry in data:
            pic_url = entry.get('pic')
            if not pic_url: continue
            
            hashes = entry.get('hash', [])
            for h in hashes:
                hash_map[h.lower()] = {
                    'pic_url': pic_url,
                    'title': entry.get('title', 'Unknown'),
                    'series': entry.get('series', ''),
                    'episodes': entry.get('episodes', ''),
                    'tracks': entry.get('tracks', [])  # ← TRACKS HINZUGEFÜGT
                }
        
        print(f"✓ Datenbank geladen: {len(hash_map)} Einträge gefunden")
        print()
        return hash_map
    except FileNotFoundError:
        print(f"✗ FEHLER: {json_path} nicht gefunden!")
        print(f"  Bitte legen Sie die Datei 'tonies.json' in: {os.path.abspath('.')}")
        return {}
    except Exception as e:
        print(f"✗ FEHLER beim Laden der JSON: {e}")
        return {}

def get_audio_hash(filepath):
    """Berechnet den SHA-1 Hash des Audio-Teils (ohne Header)"""
    sys.stdout.write("  ⏳ Berechne Audio-Hash... ")
    sys.stdout.flush()
    
    sha1 = hashlib.sha1()
    try:
        with open(filepath, 'rb') as f:
            f.seek(HEADER_SIZE)
            while True:
                data = f.read(65536)
                if not data: break
                sha1.update(data)
        hash_value = sha1.hexdigest().lower()
        print(f"✓ ({hash_value[:16]}...)")
        return hash_value
    except Exception as e:
        print(f"✗ Fehler: {e}")
        return None

def sanitize_filename(filename):
    """Entfernt ungültige Zeichen aus Dateinamen"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def download_image(url, target_path):
    """Lädt ein Bild herunter"""
    try:
        sys.stdout.write("  ⏳ Lade Cover herunter... ")
        sys.stdout.flush()
        
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200:
            with open(target_path, 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
            print("✓")
            return True
        else:
            print(f"✗ (HTTP {r.status_code})")
    except Exception as e:
        print(f"✗ ({e})")
    return False

def get_audio_duration(mp3_path):
    """Lädt die Dauer einer MP3-Datei mit FFprobe"""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 
             'default=noprint_wrappers=1:nokey=1:noprint_wrappers=1', mp3_path],
            capture_output=True, text=True, timeout=10
        )
        if result.stdout:
            return float(result.stdout.strip())
    except:
        pass
    return None

def create_cue_file(output_cue, title, artist, tracks, mp3_filename):
    """Erstellt eine CUE-Datei mit den Track-Informationen"""
    if not tracks:
        return
    
    try:
        with open(output_cue, 'w', encoding='utf-8') as f:
            f.write(f'REM CREATED BY TAF2MP3 CONVERTER\n')
            f.write(f'TITLE "{title}"\n')
            f.write(f'PERFORMER "{artist}"\n')
            f.write(f'FILE "{mp3_filename}" MP3\n')
            
            # Berechne grobe Positionen basierend auf Track-Anzahl
            # Dies ist eine Approximation, da wir ohne Audio-Analyse arbeiten
            for idx, track in enumerate(tracks, 1):
                # Vereinfachte Minute-Berechnung: 2 Min pro Track
                minutes = (idx - 1) * 2
                track_name = track if isinstance(track, str) else f"Track {idx}"
                f.write(f'  TRACK {idx:02d} AUDIO\n')
                f.write(f'    TITLE "{track_name}"\n')
                f.write(f'    INDEX 01 {minutes:02d}:00:00\n')
        
        return True
    except Exception as e:
        print(f"  ⚠️  CUE-Datei konnte nicht erstellt werden: {e}")
        return False

def convert_taf_to_mp3():
    """Hauptfunktion: Konvertiert alle TAF-Dateien"""
    
    # 1. Anleitung anzeigen
    show_setup_guide()
    
    input("Drücken Sie Enter, um zu fortfahren...")
    print()
    
    # 2. Datenbank laden
    hash_db = load_tonies_json(JSON_FILE)
    if not hash_db:
        print("✗ Konvertierung abgebrochen. Bitte überprüfen Sie die tonies.json")
        input("Drücken Sie Enter zum Beenden...")
        return
    
    # 3. TAF-Dateien suchen
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    taf_files = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.taf")))
    
    if not taf_files:
        print("✗ Keine .taf Dateien gefunden!")
        print(f"  Bitte legen Sie die TAF-Dateien in: {os.path.abspath(SOURCE_DIR)}")
        input("Drücken Sie Enter zum Beenden...")
        return
    
    print("📁 TAF-Dateien gefunden:")
    print()
    for i, taf_path in enumerate(taf_files, 1):
        filename = os.path.basename(taf_path)
        filesize = os.path.getsize(taf_path) / (1024 * 1024)
        print(f"  {i}. {filename} ({filesize:.1f} MB)")
    
    print()
    print(f"Gesamt: {len(taf_files)} Datei(en) zur Konvertierung")
    print()
    
    input("Drücken Sie Enter, um zu starten...")
    print()
    
    # 4. Konvertierungsschleife
    successful = 0
    failed = 0
    
    for idx, taf_path in enumerate(taf_files, 1):
        filename = os.path.basename(taf_path)
        base_name = os.path.splitext(filename)[0]
        output_mp3 = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
        
        print(f"[{idx}/{len(taf_files)}] Bearbeite: {filename}")
        
        # 5. Hash berechnen
        audio_hash = get_audio_hash(taf_path)
        if not audio_hash:
            print("  ✗ Hash konnte nicht berechnet werden")
            failed += 1
            print()
            continue
        
        entry_data = hash_db.get(audio_hash)
        temp_cover_path = "temp_cover.jpg"
        has_cover = False
        title = "Unknown"
        tracks = []

        if entry_data:
            cover_url = entry_data['pic_url']
            title = entry_data['title']
            series = entry_data.get('series', '')
            episodes = entry_data.get('episodes', '')
            tracks = entry_data.get('tracks', [])  # ← TRACKS AUSLESEN
            
            print(f"  📚 Titel: {title}")
            if series:
                print(f"  📖 Serie: {series}")
            if episodes:
                print(f"  📄 Episode: {episodes}")
            if tracks:
                print(f"  🎵 Kapitel: {len(tracks)} Tracks gefunden")
            
            if download_image(cover_url, temp_cover_path):
                has_cover = True
        else:
            print(f"  ⚠️  Keine Metadaten gefunden")

        # 6. Konvertieren
        try:
            sys.stdout.write("  ⏳ Konvertiere zu MP3... ")
            sys.stdout.flush()
            
            with open(taf_path, "rb") as f:
                f.seek(HEADER_SIZE)
                audio_data = f.read()

            cmd = ['ffmpeg', '-y', '-f', 'ogg', '-i', 'pipe:0']

            if has_cover:
                cmd.extend(['-i', temp_cover_path, '-map', '0:0', '-map', '1:0', 
                            '-c:v', 'copy', '-id3v2_version', '3', 
                            '-metadata:s:v', 'title="Album cover"', 
                            '-metadata:s:v', 'comment="Cover (front)"'])
            
            cmd.extend(['-c:a', 'libmp3lame', '-q:a', '2', output_mp3])
            
            process = subprocess.Popen(cmd, stdin=subprocess.PIPE, 
                                     stdout=subprocess.DEVNULL, 
                                     stderr=subprocess.DEVNULL)
            process.communicate(input=audio_data)
            
            if os.path.exists(output_mp3):
                mp3_size = os.path.getsize(output_mp3) / (1024 * 1024)
                print(f"✓ ({mp3_size:.1f} MB)")
            else:
                raise Exception("MP3-Datei wurde nicht erstellt")
            
            # 7. Cover speichern
            if has_cover:
                safe_title = sanitize_filename(title)
                output_cover = os.path.join(OUTPUT_DIR, f"{safe_title}.jpg")
                shutil.copy(temp_cover_path, output_cover)
                cover_size = os.path.getsize(output_cover) / 1024
                print(f"  🖼️  Cover gespeichert: {safe_title}.jpg ({cover_size:.0f} KB)")
            
            # 8. CUE-DATEI ERSTELLEN (NEU!)
            if tracks:
                safe_title = sanitize_filename(title)
                output_cue = os.path.join(OUTPUT_DIR, f"{safe_title}.cue")
                series = entry_data.get('series', title) if entry_data else title
                
                if create_cue_file(output_cue, title, series, tracks, f"{base_name}.mp3"):
                    print(f"  📝 CUE-Datei erstellt: {safe_title}.cue ({len(tracks)} Tracks)")
            
            successful += 1

        except Exception as e:
            print(f"✗ Fehler: {e}")
            failed += 1
        
        finally:
            if os.path.exists(temp_cover_path):
                os.remove(temp_cover_path)
        
        print()

    # 9. Zusammenfassung
    print("=" * 70)
    print("✓ KONVERTIERUNG ABGESCHLOSSEN".center(70))
    print("=" * 70)
    print()
    print(f"📊 Ergebnis:")
    print(f"  ✓ Erfolgreich: {successful}")
    print(f"  ✗ Fehler: {failed}")
    print()
    print(f"📁 Ausgabeverzeichnis: {os.path.abspath(OUTPUT_DIR)}")
    print()
    print("📄 Generierte Dateien:")
    print("  • MP3-Audiodateien")
    print("  • JPG-Coverbilder")
    print("  • CUE-Dateien (mit Track-Informationen, wo verfügbar)")
    print()
    input("Drücken Sie Enter zum Beenden...")

if __name__ == "__main__":
    convert_taf_to_mp3()
