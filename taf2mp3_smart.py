#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TAF zu MP3 Konverter PRO DELUXE
✓ Ausführliche Schritt-für-Schritt Anleitung
✓ Eine MP3 pro Hörspiel (kombinierte Tracks)
✓ Cover-Download aus tonies.json
✓ CUE-Kapitel mit EXAKTEN echten Zeiten (nicht geschätzt!)
✓ Volle Metadaten-Unterstützung

Installation:
  pip install tonietoolbox requests
"""

import os
import subprocess
import glob
import json
import hashlib
import shutil
import sys
from datetime import datetime

SOURCE_DIR = "."
OUTPUT_DIR = "mp3_converted"
JSON_FILE = "tonies.json"
HEADER_SIZE = 4096

def show_setup_guide():
    """Ausführliche Schritt-für-Schritt Anleitung"""
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 70)
    print("TAF zu MP3 Konverter mit Cover-Download & CUE-Export".center(70))
    print("=" * 70)
    print()
    print("📋 SCHRITT-FÜR-SCHRITT ANLEITUNG:")
    print()
    print("1. Vorbereitung:")
    print("   - Laden Sie die Datei 'tonies.json' herunter")
    print("   - Link: https://github.com/toniebox-reverse-engineering/tonies-json/releases")
    print("   - Speichern Sie diese Datei in den gleichen Ordner wie dieses Skript")
    print()
    print("2. TAF-Dateien vorbereiten:")
    print(f"   - Legen Sie alle zu konvertierenden .taf Dateien in:")
    print(f"     {os.path.abspath(SOURCE_DIR)}")
    print("   - (das ist der aktuelle Ordner, in dem dieses Skript liegt)")
    print()
    print("3. Abhängigkeiten installieren (einmalig):")
    print("   - Öffnen Sie die Eingabeaufforderung (CMD/PowerShell)")
    print("   - Führen Sie aus: pip install tonietoolbox requests")
    print()
    print("4. Dieses Skript starten:")
    print("   - Doppelklick auf diese Datei")
    print("   - oder: py taf2mp3_pro.py")
    print()
    print("5. Ergebnis:")
    print(f"   - MP3-Dateien landen in: {os.path.abspath(OUTPUT_DIR)}")
    print("   - Cover werden als separate .jpg-Dateien gespeichert")
    print("   - CUE-Dateien (mit exakten Kapitel-Zeiten) werden erstellt")
    print()
    print("=" * 70)
    print()

def find_opus2tonie():
    """Sucht opus2tonie.py automatisch"""
    if os.path.exists("opus2tonie.py"):
        return "opus2tonie.py"
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "show", "tonietoolbox"],
                              capture_output=True, text=True)
        if "Location:" in result.stdout:
            location = result.stdout.split("Location:")[1].strip().split("
")[0]
            path = os.path.join(location, "tonietoolbox", "opus2tonie.py")
            if os.path.exists(path):
                return path
    except:
        pass
    return None

def load_tonies_json(json_path):
    """Lädt tonies.json und erstellt Hash-Datenbank"""
    print(f"📂 Lade Datenbank: {json_path}")
    print()
    
    hash_db = {}
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for entry in data:
            hashes = entry.get('hash', [])
            for h in hashes:
                hash_db[h.lower()] = {
                    'title': entry.get('title', 'Unknown'),
                    'series': entry.get('series', ''),
                    'episodes': entry.get('episodes', ''),
                    'tracks': entry.get('tracks', []),
                    'pic': entry.get('pic', '')
                }
        
        print(f"✓ Datenbank geladen: {len(hash_db)} Einträge gefunden")
        print()
        return hash_db
    except FileNotFoundError:
        print(f"✗ FEHLER: {json_path} nicht gefunden!")
        print(f"  Bitte legen Sie die Datei 'tonies.json' in:")
        print(f"  {os.path.abspath('.')}")
        return {}
    except Exception as e:
        print(f"✗ FEHLER beim Laden der JSON: {e}")
        return {}

def get_audio_hash(filepath):
    """Berechnet SHA-1 Hash des Audio-Teils (ohne Header)"""
    sys.stdout.write("  ⏳ Berechne Audio-Hash... ")
    sys.stdout.flush()
    
    sha1 = hashlib.sha1()
    try:
        with open(filepath, 'rb') as f:
            f.seek(HEADER_SIZE)
            while True:
                data = f.read(65536)
                if not data:
                    break
                sha1.update(data)
        hash_value = sha1.hexdigest().lower()
        print(f"✓")
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
        
        import requests
        r = requests.get(url, stream=True, timeout=10)
        if r.status_code == 200:
            with open(target_path, 'wb') as f:
                f.write(r.content)
            print("✓")
            return True
        else:
            print(f"✗ (HTTP {r.status_code})")
    except Exception as e:
        print(f"✗ ({e})")
    return False

def split_taf_to_tracks(taf_path, output_dir):
    """Splittet TAF in OPUS-Tracks mit opus2tonie"""
    opus2tonie_script = find_opus2tonie()
    if not opus2tonie_script:
        print("  ⚠️  opus2tonie.py nicht gefunden!")
        print("     pip install tonietoolbox")
        return []
    
    try:
        sys.stdout.write("  ⏳ Splitte TAF in Tracks... ")
        sys.stdout.flush()
        
        result = subprocess.run(
            [sys.executable, opus2tonie_script, '--split', taf_path],
            cwd=output_dir,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        opus_files = sorted(glob.glob(os.path.join(output_dir, "*.opus")))
        if opus_files:
            print(f"✓ ({len(opus_files)} Tracks)")
            return opus_files
        print("✗")
        return []
    except Exception as e:
        print("✗")
        return []

def get_opus_duration(opus_file):
    """Ermittelt ECHTE Dauer einer OPUS-Datei"""
    try:
        cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
               '-of', 'default=noprint_wrappers=1:nokey=1', opus_file]
        result = subprocess.run(cmd, stdout=subprocess.PIPE, text=True, timeout=10)
        if result.stdout.strip():
            return float(result.stdout.strip())
    except:
        pass
    return None

def create_cue_file(output_cue, title, artist, track_names, durations, mp3_filename):
    """
    Erstellt CUE-Datei mit EXAKTEN Track-Grenzen
    Nutzt echte Dauern, nicht geschätzt!
    """
    if not track_names:
        return True
    
    try:
        with open(output_cue, 'w', encoding='utf-8') as f:
            f.write(f'REM CREATED BY TAF2MP3 CONVERTER
')
            f.write(f'TITLE "{title}"
')
            f.write(f'PERFORMER "{artist}"
')
            f.write(f'FILE "{mp3_filename}" MP3
')
            
            current_time_ms = 0.0  # Millisekunden für maximale Genauigkeit
            
            for idx, (track_name, duration) in enumerate(zip(track_names, durations), 1):
                # Konvertiere zu MM:SS:FF (CUE-Format, 75 Frames/Sekunde)
                total_frames = int(round(current_time_ms * 75 / 1000))
                
                minutes = total_frames // (75 * 60)
                remaining_frames = total_frames % (75 * 60)
                seconds = remaining_frames // 75
                frames = remaining_frames % 75
                
                f.write(f'  TRACK {idx:02d} AUDIO
')
                f.write(f'    TITLE "{track_name}"
')
                f.write(f'    INDEX 01 {minutes:02d}:{seconds:02d}:{frames:02d}
')
                
                # Addiere echte Dauer in Millisekunden
                current_time_ms += duration * 1000
        
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
        series = ""
        tracks = []

        if entry_data:
            cover_url = entry_data.get('pic', '')
            title = entry_data['title']
            series = entry_data.get('series', '')
            episodes = entry_data.get('episodes', '')
            tracks = entry_data.get('tracks', [])
            
            print(f"  📚 Titel: {title}")
            if series:
                print(f"  📖 Serie: {series}")
            if episodes:
                print(f"  📄 Episode: {episodes}")
            if tracks:
                print(f"  🎵 Kapitel: {len(tracks)} Tracks gefunden")
            
            if cover_url and download_image(cover_url, temp_cover_path):
                has_cover = True
        else:
            print(f"  ⚠️  Keine Metadaten gefunden")

        # 6. TAF splitten für Track-Durations
        temp_dir = os.path.join(OUTPUT_DIR, f"temp_{base_name}")
        os.makedirs(temp_dir, exist_ok=True)
        
        opus_files = split_taf_to_tracks(taf_path, temp_dir)
        if not opus_files:
            failed += 1
            shutil.rmtree(temp_dir, ignore_errors=True)
            print()
            continue
        
        # 7. Kombiniere zu EINER MP3
        print(f"  ⏳ Kombiniere zu MP3...")
        
        concat_file = os.path.join(temp_dir, "concat.txt")
        try:
            with open(concat_file, 'w') as f:
                for opus_file in opus_files:
                    f.write(f"file '{os.path.abspath(opus_file)}'
")
            
            cmd = [
                'ffmpeg', '-y', '-f', 'concat', '-safe', '0',
                '-i', concat_file,
                '-c:a', 'libmp3lame', '-q:a', '2',
                '-metadata', f'title={title}',
                '-metadata', f'artist={series if series else title}',
                '-metadata', 'composer=tonies',
                '-metadata', 'genre=Tonies'
            ]
            
            # Füge Cover hinzu falls vorhanden
            if has_cover:
                cmd.extend([
                    '-i', temp_cover_path,
                    '-map', '0:0', '-map', '1:0',
                    '-c:v', 'copy', '-id3v2_version', '3',
                    '-metadata:s:v', 'title=Album cover',
                    '-metadata:s:v', 'comment=Cover (front)'
                ])
            
            cmd.append(output_mp3)
            
            process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            process.communicate()
            
            if os.path.exists(output_mp3) and os.path.getsize(output_mp3) > 0:
                mp3_size = os.path.getsize(output_mp3) / (1024 * 1024)
                print(f"  ✓ MP3 ({mp3_size:.1f} MB)")
            else:
                print("  ❌ MP3 fehlgeschlagen")
                failed += 1
                shutil.rmtree(temp_dir, ignore_errors=True)
                print()
                continue
        except Exception as e:
            print(f"  ❌ Fehler: {e}")
            failed += 1
            shutil.rmtree(temp_dir, ignore_errors=True)
            print()
            continue
        
        # 8. Cover speichern
        if has_cover:
            safe_title = sanitize_filename(title)
            output_cover = os.path.join(OUTPUT_DIR, f"{safe_title}.jpg")
            shutil.copy(temp_cover_path, output_cover)
            cover_size = os.path.getsize(output_cover) / 1024
            print(f"  🖼️  Cover gespeichert: {safe_title}.jpg ({cover_size:.0f} KB)")
        
        # 9. CUE-DATEI MIT EXAKTEN ZEITEN ERSTELLEN
        if tracks:
            durations = []
            for opus_file in opus_files:
                duration = get_opus_duration(opus_file)
                if duration:
                    durations.append(duration)
            
            if durations and len(durations) == len(tracks):
                safe_title = sanitize_filename(title)
                output_cue = os.path.join(OUTPUT_DIR, f"{safe_title}.cue")
                
                if create_cue_file(output_cue, title, series if series else title,
                                  tracks, durations, f"{base_name}.mp3"):
                    print(f"  📝 CUE-Datei erstellt: {safe_title}.cue ({len(tracks)} Tracks mit exakten Zeiten)")
        
        # Aufräumen
        shutil.rmtree(temp_dir, ignore_errors=True)
        if os.path.exists(temp_cover_path):
            os.remove(temp_cover_path)
        
        successful += 1
        print()

    # 10. Zusammenfassung
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
    print("  • MP3-Audiodateien (eine pro Hörspiel)")
    print("  • JPG-Coverbilder")
    print("  • CUE-Dateien (mit exakten Kapitel-Zeiten)")
    print()
    
    input("Drücken Sie Enter zum Beenden...")

if __name__ == "__main__":
    try:
        convert_taf_to_mp3()
    except KeyboardInterrupt:
        print("

⚠️  Abgebrochen")
