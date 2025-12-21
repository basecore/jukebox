import os
import subprocess
import glob
import json
import hashlib
import requests
import shutil
import sys
import struct
import time

# --- KONFIGURATION ---
SOURCE_DIR = "."         
OUTPUT_DIR = "mp3_converted"
JSON_FILE = "tonies.json"
HEADER_SIZE = 4096       
OPUS_SAMPLE_RATE = 48000.0

# ==========================================
# TEIL 1: ANALYSE-FUNKTIONEN (ROBUST)
# ==========================================

def read_varint(data, offset):
    value = 0
    shift = 0
    curr = offset
    while True:
        if curr >= len(data): raise ValueError("EOF")
        byte = data[curr]
        curr += 1
        value |= (byte & 0x7f) << shift
        if not (byte & 0x80): break
        shift += 7
    return value, curr

def get_chapters_robust(filepath):
    """Findet Kapitel-Marker im Header (Brute Force)."""
    best_chapters = []
    try:
        with open(filepath, "rb") as f:
            data = f.read(HEADER_SIZE)
            for i in range(len(data) - 2):
                if data[i] == 0x22:
                    try:
                        length = data[i+1]
                        start = i + 2
                        end = start + length
                        if end > len(data): continue
                        temp = []
                        curr = start
                        while curr < end:
                            val, curr = read_varint(data, curr)
                            temp.append(val)
                        if len(temp) > len(best_chapters):
                            if all(temp[j] <= temp[j+1] for j in range(len(temp)-1)):
                                best_chapters = temp
                    except: continue
    except: pass
    return sorted(list(set([0] + best_chapters)))

def scan_ogg_timestamps(filepath):
    """Liest Zeitstempel aus OGG-Pages."""
    page_map = {}
    try:
        with open(filepath, "rb") as f:
            f.seek(HEADER_SIZE)
            file_size = os.fstat(f.fileno()).st_size
            while f.tell() < file_size:
                pos = f.tell()
                sig = f.read(4)
                if sig != b'OggS':
                    if not sig: break
                    f.seek(pos + 1); continue
                head = f.read(23)
                if len(head) < 23: break
                data = struct.unpack("<BBQLLLB", head)
                page_map[data[4]] = data[2] 
                f.seek(sum(f.read(data[6])), 1)
    except: pass
    return page_map

def granule_to_cue(granule):
    seconds = granule / OPUS_SAMPLE_RATE
    m = int(seconds // 60)
    s = int(seconds % 60)
    f = int((seconds - int(seconds)) * 75)
    return f"{m:02d}:{s:02d}:{f:02d}"

# ==========================================
# TEIL 2: HELFER
# ==========================================

def clean_filename(name):
    return "".join([c if c.isalnum() or c in " .-_()" else "_" for c in name]).strip()

def load_json_db(path):
    print(f"📂 Lade Datenbank: {path}")
    try:
        with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
        db = {}
        for entry in data:
            pic = entry.get('pic')
            if not pic: continue
            for h in entry.get('hash', []):
                db[h.lower()] = {
                    'pic': pic,
                    'title': entry.get('title', 'Unknown'),
                    'series': entry.get('series', ''),
                    'tracks': entry.get('tracks', [])
                }
        print(f"✓ {len(db)} Einträge geladen.")
        return db
    except: 
        print("⚠️  tonies.json nicht gefunden.")
        return {}

def get_hash(path):
    s = hashlib.sha1()
    try:
        with open(path, 'rb') as f:
            f.seek(HEADER_SIZE)
            while True:
                d = f.read(65536)
                if not d: break
                s.update(d)
        return s.hexdigest().lower()
    except: return None

def dl_cover(url, target):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(target, 'wb') as f: f.write(r.content)
            return True
    except: pass
    return False

# ==========================================
# TEIL 3: PROGRESS BAR FUNKTION
# ==========================================

def convert_audio_with_progress(audio_data, mp3_path, title, series, cover_path=None):
    """Führt FFmpeg aus und zeigt einen Fortschrittsbalken basierend auf Input-Daten."""
    cmd = ['ffmpeg', '-y', '-f', 'ogg', '-i', 'pipe:0']
    
    if cover_path:
        cmd += ['-i', cover_path, '-map', '0:0', '-map', '1:0', '-c:v', 'copy', 
                '-id3v2_version', '3', '-metadata:s:v', 'title="Cover"', 
                '-metadata:s:v', 'comment="Front"']
    
    cmd += ['-c:a', 'libmp3lame', '-q:a', '2', 
            '-metadata', f'title={title}', 
            '-metadata', f'artist={series}', 
            mp3_path]

    # Prozess starten, stdin als Pipe
    process = subprocess.Popen(
        cmd, 
        stdin=subprocess.PIPE, 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
    )

    total_size = len(audio_data)
    chunk_size = 64 * 1024 # 64KB Chunks
    bytes_written = 0

    display_name = os.path.basename(mp3_path)
    
    try:
        # Daten stückweise schreiben
        for i in range(0, total_size, chunk_size):
            chunk = audio_data[i:i+chunk_size]
            process.stdin.write(chunk)
            bytes_written += len(chunk)
            
            # Prozent berechnen
            percent = int((bytes_written / total_size) * 100)
            
            # Ausgabe auf gleicher Zeile (\r)
            sys.stdout.write(f"\r  -> Audio: {display_name} ... {percent}%")
            sys.stdout.flush()
            
        process.stdin.close()
        process.wait()
        
        # Zeile abschließen mit Haken
        sys.stdout.write(f"\r  -> Audio: {display_name} ✓          \n")
        sys.stdout.flush()
        return True
    except Exception as e:
        print(f"\n  ✗ Fehler bei FFmpeg: {e}")
        return False

# ==========================================
# TEIL 4: HAUPTPROGRAMM
# ==========================================

def main():
    print("=" * 70)
    print("TAF 2 MP3 DETAIL (Info & Progress)".center(70))
    print("=" * 70)
    
    # 1. Dateien suchen & Auflisten
    taf_files = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.taf")))
    
    if not taf_files:
        print("✗ Keine .taf Dateien gefunden!")
        input("Enter..."); return

    print(f"Gefunden: {len(taf_files)} Dateien")
    for i, f in enumerate(taf_files, 1):
        print(f"  {i}. {os.path.basename(f)}")
    print("-" * 70)
    
    # input("Drücke Enter zum Starten...")
    print()

    db = load_json_db(JSON_FILE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for i, taf_path in enumerate(taf_files, 1):
        filename = os.path.basename(taf_path)
        original_base = os.path.splitext(filename)[0]
        
        print(f"[{i}/{len(taf_files)}] Lade: {filename}")
        
        # A) Metadaten ermitteln
        file_hash = get_hash(taf_path)
        meta = db.get(file_hash, {})
        
        title = meta.get('title', original_base)
        series = meta.get('series', title)
        track_names = meta.get('tracks', [])
        
        final_name = clean_filename(title)
        print(f"  -> Ziel: '{final_name}'")
        
        # Pfade
        mp3_path = os.path.join(OUTPUT_DIR, f"{final_name}.mp3")
        cue_path = os.path.join(OUTPUT_DIR, f"{final_name}.cue")
        jpg_path = os.path.join(OUTPUT_DIR, f"{final_name}.jpg")

        # B) Cover laden
        cover_tmp = "temp_cover.jpg"
        has_cover = False
        
        # Prüfen ob Cover schon da ist
        if os.path.exists(jpg_path):
            print(f"  -> Cover: {os.path.basename(jpg_path)} (Existiert bereits) ✓")
            has_cover = True
            shutil.copy(jpg_path, cover_tmp) # Für FFmpeg bereitstellen
        elif meta.get('pic'):
            if dl_cover(meta['pic'], cover_tmp): 
                has_cover = True
                shutil.copy(cover_tmp, jpg_path)
                print(f"  -> Cover: {os.path.basename(jpg_path)} ✓")

        # C) Audio Konvertierung (mit Progress Bar)
        if not os.path.exists(mp3_path):
            try:
                with open(taf_path, "rb") as f:
                    f.seek(HEADER_SIZE)
                    audio_data = f.read()
                
                # Rufe die neue Funktion mit Fortschrittsanzeige auf
                convert_audio_with_progress(audio_data, mp3_path, title, series, cover_tmp if has_cover else None)
                
            except Exception as e:
                print(f"  ✗ Audio Fehler: {e}")
        else:
            print(f"  -> Audio: {os.path.basename(mp3_path)} (Existiert bereits) ✓")

        # D) CUE Sheet
        chapters = get_chapters_robust(taf_path)
        
        if chapters and len(chapters) > 1:
            page_map = scan_ogg_timestamps(taf_path)
            try:
                with open(cue_path, "w", encoding="utf-8") as f:
                    f.write(f'REM CREATED BY TAF2MP3 DETAIL\n')
                    f.write(f'TITLE "{title}"\nPERFORMER "{series}"\n')
                    f.write(f'FILE "{os.path.basename(mp3_path)}" MP3\n')
                    
                    track_no = 1
                    for page_idx in chapters:
                        time_str = "00:00:00"
                        if page_idx > 0:
                            prev = page_idx - 1
                            tries = 100
                            while prev >= 0 and prev not in page_map and tries > 0:
                                prev -= 1; tries -= 1
                            if prev in page_map:
                                time_str = granule_to_cue(page_map[prev])
                        
                        t_name = f"Chapter {track_no}"
                        if track_no <= len(track_names): t_name = track_names[track_no-1]
                        
                        f.write(f'  TRACK {track_no:02d} AUDIO\n')
                        f.write(f'    TITLE "{t_name}"\n')
                        f.write(f'    INDEX 01 {time_str}\n')
                        track_no += 1
                
                print(f"  -> CUE Sheet: {os.path.basename(cue_path)} ✓ ({len(chapters)} Tracks)")
            except Exception as e: 
                print(f"  ✗ CUE Fehler: {e}")
        else:
            print("  ✗ CUE Sheet: Keine Kapitel gefunden.")

        # Cleanup
        if os.path.exists(cover_tmp): os.remove(cover_tmp)
        print() # Leerzeile

    print("=" * 70)
    print("Fertig! Alle Dateien befinden sich in:")
    print(f"📂 {os.path.abspath(OUTPUT_DIR)}")
    print("=" * 70)
    input("Drücken Sie Enter zum Beenden...")

if __name__ == "__main__":
    main()
