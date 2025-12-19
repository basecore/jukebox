import os
import subprocess
import glob
import json
import hashlib
import requests
import shutil
import sys
import struct

# --- KONFIGURATION ---
SOURCE_DIR = "."         # Ordner mit TAF-Dateien
OUTPUT_DIR = "mp3_converted"
JSON_FILE = "tonies.json"
TAF_HEADER_SIZE = 4096   # Größe des Headers
OPUS_SAMPLE_RATE = 48000.0 # Tonie Standard Samplerate

# --- TAF & OGG ANALYSE FUNKTIONEN (NEU) ---

def read_varint(data, offset):
    """Liest einen Protobuf Varint sicher aus."""
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

def get_real_chapters(filepath):
    """
    Liest die echten Kapitelmarken (Page IDs) aus dem TAF-Header.
    Entspricht der Logik der TonieToolbox (tonie_header.proto).
    """
    chapters = []
    try:
        with open(filepath, "rb") as f:
            header_data = f.read(TAF_HEADER_SIZE)
            idx = 0
            limit = len(header_data)
            
            # Suche nach Feld 4 (chapterPages)
            while idx < limit:
                try:
                    tag, idx = read_varint(header_data, idx)
                    field = tag >> 3
                    wire = tag & 0x07
                    
                    if field == 4:
                        if wire == 2: # Packed
                            length, idx = read_varint(header_data, idx)
                            end = idx + length
                            while idx < end:
                                val, idx = read_varint(header_data, idx)
                                chapters.append(val)
                            break 
                        else: # Not packed (selten)
                            val, idx = read_varint(header_data, idx)
                            chapters.append(val)
                    else:
                        # Skip unknown fields
                        if wire == 0: read_varint(header_data, idx)
                        elif wire == 1: idx += 8
                        elif wire == 5: idx += 4
                        elif wire == 2:
                            l, idx = read_varint(header_data, idx)
                            idx += l
                        else: break
                except: break
    except Exception as e:
        print(f"  ⚠️  Warnung beim Header-Lesen: {e}")
        
    return sorted(list(set([0] + chapters)))

def scan_ogg_granules(filepath):
    """
    Scannt die OGG-Datei und map Page-Sequence -> Zeitstempel (Granule).
    Dies liefert die physikalisch korrekten Zeiten.
    """
    page_map = {}
    try:
        with open(filepath, "rb") as f:
            f.seek(TAF_HEADER_SIZE)
            file_size = os.fstat(f.fileno()).st_size
            
            while f.tell() < file_size:
                # OggS Magic suchen
                if f.read(4) != b'OggS':
                    f.seek(-3, 1) # Byte für Byte weiter
                    continue
                
                # Header parsen (27 bytes total, 4 schon gelesen)
                head = f.read(23)
                if len(head) < 23: break
                
                # <BBQLLLB: Granule ist Index 2, PageSeq ist Index 4, Segments ist Index 6
                data = struct.unpack("<BBQLLLB", head)
                granule_pos = data[2]
                page_seq = data[4]
                n_segs = data[6]
                
                # Body überspringen
                seg_table = f.read(n_segs)
                body_size = sum(seg_table)
                f.seek(body_size, 1)
                
                page_map[page_seq] = granule_pos
    except Exception as e:
        print(f"  ⚠️  Warnung beim Audio-Scan: {e}")
        
    return page_map

def granule_to_cue_time(granule):
    """Konvertiert Granules (48kHz) in MM:SS:FF"""
    seconds = granule / OPUS_SAMPLE_RATE
    m = int(seconds // 60)
    s = int(seconds % 60)
    f = int((seconds - int(seconds)) * 75)
    return f"{m:02d}:{s:02d}:{f:02d}"

# --- HELFER FUNKTIONEN ---

def show_setup_guide():
    print("=" * 70)
    print("TAF zu MP3 ULTIMATE (mit nativer CUE-Berechnung)".center(70))
    print("=" * 70)
    print("1. Legen Sie .taf Dateien in diesen Ordner.")
    print("2. Legen Sie die 'tonies.json' daneben.")
    print("3. Stellen Sie sicher, dass 'ffmpeg' installiert ist.")
    print("=" * 70)
    print()

def load_tonies_json(json_path):
    print(f"📂 Lade Datenbank: {json_path}")
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        hash_map = {}
        for entry in data:
            pic = entry.get('pic')
            if not pic: continue
            for h in entry.get('hash', []):
                hash_map[h.lower()] = {
                    'pic': pic,
                    'title': entry.get('title', 'Unknown'),
                    'series': entry.get('series', ''),
                    'episodes': entry.get('episodes', ''),
                    'tracks': entry.get('tracks', [])
                }
        print(f"✓ Datenbank geladen: {len(hash_map)} Einträge")
        print()
        return hash_map
    except:
        print("✗ tonies.json Fehler (oder nicht gefunden). Mache ohne Metadaten weiter.")
        return {}

def get_audio_hash(filepath):
    sha1 = hashlib.sha1()
    try:
        with open(filepath, 'rb') as f:
            f.seek(TAF_HEADER_SIZE)
            while True:
                data = f.read(65536)
                if not data: break
                sha1.update(data)
        return sha1.hexdigest().lower()
    except: return None

def sanitize_filename(name):
    return "".join([c if c.isalnum() or c in " .-_()" else "_" for c in name]).strip()

def download_image(url, path):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(path, 'wb') as f: f.write(r.content)
            return True
    except: pass
    return False

# --- HAUPT FUNKTION ---

def convert_taf_to_mp3():
    show_setup_guide()
    
    hash_db = load_tonies_json(JSON_FILE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    taf_files = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.taf")))
    
    if not taf_files:
        print("✗ Keine .taf Dateien gefunden!")
        input("Enter zum Beenden...")
        return

    print(f"Gefunden: {len(taf_files)} Dateien")
    print("-" * 70)

    for i, taf_path in enumerate(taf_files, 1):
        filename = os.path.basename(taf_path)
        base_name = os.path.splitext(filename)[0]
        output_mp3 = os.path.join(OUTPUT_DIR, f"{base_name}.mp3")
        
        print(f"[{i}/{len(taf_files)}] Verarbeite: {filename}")
        
        # 1. Metadaten holen
        sys.stdout.write("  -> Prüfe Hash... ")
        sys.stdout.flush()
        audio_hash = get_audio_hash(taf_path)
        meta = hash_db.get(audio_hash, {})
        
        title = meta.get('title', base_name)
        series = meta.get('series', title)
        tracks_meta = meta.get('tracks', [])
        
        print(f"✓ ({title})")
        
        # Cover laden
        cover_path = "temp_cover.jpg"
        has_cover = False
        if meta.get('pic'):
            if download_image(meta['pic'], cover_path):
                has_cover = True

        # 2. MP3 Konvertierung
        if not os.path.exists(output_mp3):
            sys.stdout.write("  -> Konvertiere Audio (ffmpeg)... ")
            sys.stdout.flush()
            try:
                # Audio-Daten lesen
                with open(taf_path, "rb") as f:
                    f.seek(TAF_HEADER_SIZE)
                    audio_data = f.read()
                
                cmd = ['ffmpeg', '-y', '-f', 'ogg', '-i', 'pipe:0']
                if has_cover:
                    cmd.extend(['-i', cover_path, '-map', '0:0', '-map', '1:0', 
                                '-c:v', 'copy', '-id3v2_version', '3', 
                                '-metadata:s:v', 'title="Cover"', '-metadata:s:v', 'comment="Front"'])
                
                cmd.extend(['-c:a', 'libmp3lame', '-q:a', '2', 
                            '-metadata', f'title={title}', 
                            '-metadata', f'artist={series}', 
                            output_mp3])
                
                proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                proc.communicate(input=audio_data)
                print("✓")
            except Exception as e:
                print(f"✗ Fehler: {e}")
        else:
            print("  -> MP3 existiert bereits (überspringe Konvertierung).")

        # 3. CUE Sheet erstellen (NEUE LOGIK)
        sys.stdout.write("  -> Analysiere Kapitel... ")
        sys.stdout.flush()
        
        # A) Echte Kapitel aus Header
        chapters = get_real_chapters(taf_path)
        
        # B) Zeitstempel aus OGG Struktur
        if chapters:
            page_map = scan_ogg_granules(taf_path)
            
            safe_title = sanitize_filename(title)
            cue_path = os.path.join(OUTPUT_DIR, f"{safe_title}.cue")
            
            # Cover kopieren
            if has_cover:
                shutil.copy(cover_path, os.path.join(OUTPUT_DIR, f"{safe_title}.jpg"))

            try:
                with open(cue_path, "w", encoding="utf-8") as cue:
                    cue.write(f'REM CREATED BY TAF2MP3 ULTIMATE\n')
                    cue.write(f'TITLE "{title}"\n')
                    cue.write(f'PERFORMER "{series}"\n')
                    cue.write(f'FILE "{os.path.basename(output_mp3)}" MP3\n')
                    
                    track_counter = 1
                    for page_idx in chapters:
                        # Zeit berechnen
                        timestamp = "00:00:00"
                        if page_idx > 0:
                            # Startzeit = Ende der vorherigen Page
                            prev = page_idx - 1
                            limit = 100 # Suche bis zu 100 Pages zurück falls Lücken
                            while prev >= 0 and prev not in page_map and limit > 0:
                                prev -= 1
                                limit -= 1
                            
                            if prev in page_map:
                                timestamp = granule_to_cue_time(page_map[prev])
                        
                        # Titel aus JSON oder generisch
                        track_title = f"Chapter {track_counter}"
                        if track_counter <= len(tracks_meta):
                            track_title = tracks_meta[track_counter-1]
                            
                        cue.write(f'  TRACK {track_counter:02d} AUDIO\n')
                        cue.write(f'    TITLE "{track_title}"\n')
                        cue.write(f'    INDEX 01 {timestamp}\n')
                        
                        track_counter += 1
                print(f"✓ ({len(chapters)} Tracks)")
            except Exception as e:
                print(f"✗ Fehler beim Schreiben der CUE: {e}")
        else:
            print("✗ Keine Kapitel im Header gefunden.")

        # Cleanup
        if os.path.exists(cover_path): os.remove(cover_path)
        print()

    print("=" * 70)
    print(f"Fertig! Dateien liegen in: {os.path.abspath(OUTPUT_DIR)}")
    input("Enter zum Beenden...")

if __name__ == "__main__":
    convert_taf_to_mp3()
