import os
import subprocess
import glob
import json
import hashlib
import requests
import shutil
import sys
import struct
import re

# --- KONFIGURATION ---
SOURCE_DIR = "."         
OUTPUT_DIR = "mp3_converted"
JSON_FILE = "tonies.json"
HEADER_SIZE = 4096       
OPUS_SAMPLE_RATE = 48000.0

# Einstellungen für die Stille-Suche (Kalibrierung)
SILENCE_DB = "-50dB"       # Ab wann ist es "stille"?
SILENCE_MIN_SEC = "0.5"    # Wie lang muss die Pause mindestens sein?
SYNC_WINDOW = 30.0         # Suchradius in Sekunden um den TAF-Punkt herum

# ==========================================
# TEIL 1: HEADER & OGG ANALYSE (THEORIE)
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

def get_chapters_from_header(filepath):
    """Liest die Soll-Kapitel aus dem Header (Brute Force)."""
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

def scan_ogg_positions(filepath):
    """Liest die Zeitstempel (Granules) aus der Datei."""
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
                page_map[data[4]] = data[2] # Seq -> Granule
                f.seek(sum(f.read(data[6])), 1) # Skip Body
    except: pass
    return page_map

# ==========================================
# TEIL 2: AUDIO ANALYSE (PRAXIS / STILLE)
# ==========================================

def scan_silence_ffmpeg(mp3_path):
    """Scannt die fertige MP3 nach echten Pausen."""
    cmd = ['ffmpeg', '-i', mp3_path, '-af', f'silencedetect=noise={SILENCE_DB}:d={SILENCE_MIN_SEC}', '-f', 'null', '-']
    try:
        res = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, encoding='utf-8')
        starts = []
        ends = []
        for line in res.stderr.split('\n'):
            if "silence_start" in line:
                m = re.search(r"silence_start:\s*([\d\.]+)", line)
                if m: starts.append(float(m.group(1)))
            elif "silence_end" in line:
                m = re.search(r"silence_end:\s*([\d\.]+)", line)
                if m: ends.append(float(m.group(1)))
        
        ranges = []
        for i in range(min(len(starts), len(ends))):
            ranges.append((starts[i], ends[i]))
        return ranges
    except: return []

# ==========================================
# TEIL 3: HELFER
# ==========================================

def sec_to_cue(seconds):
    m = int(seconds // 60)
    s = int(seconds % 60)
    f = int((seconds - int(seconds)) * 75)
    return f"{m:02d}:{s:02d}:{f:02d}"

def load_db(path):
    print(f"📂 Lade Datenbank...")
    try:
        with open(path, 'r', encoding='utf-8') as f: data = json.load(f)
        db = {}
        for e in data:
            if not e.get('pic'): continue
            for h in e.get('hash', []):
                db[h.lower()] = {'pic': e['pic'], 'title': e.get('title',''), 'series': e.get('series',''), 'tracks': e.get('tracks',[])}
        print(f"✓ {len(db)} Einträge.")
        return db
    except: return {}

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

def dl_cover(url, path):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(path, 'wb') as f: f.write(r.content)
            return True
    except: pass
    return False

def clean_name(n): return "".join([c if c.isalnum() or c in " .-_()" else "_" for c in n]).strip()

# ==========================================
# TEIL 4: HAUPTPROGRAMM (LOGIK MERGE)
# ==========================================

def main():
    print("="*70)
    print("TAF 2 MP3 PRO SYNC (Header + Silence Calibration)".center(70))
    print("="*70)
    
    db = load_db(JSON_FILE)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    files = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.taf")))
    
    if not files:
        print("Keine Dateien gefunden.")
        input("Enter..."); return

    print(f"Gefunden: {len(files)} Dateien.")
    print("-"*70)
    input("Enter zum Starten...")
    print()

    for i, taf_path in enumerate(files, 1):
        filename = os.path.basename(taf_path)
        base = os.path.splitext(filename)[0]
        mp3_out = os.path.join(OUTPUT_DIR, f"{base}.mp3")
        
        print(f"[{i}/{len(files)}] {filename}")
        
        # 1. Metadaten & Cover
        sys.stdout.write("  -> Metadaten... ")
        h = get_hash(taf_path)
        meta = db.get(h, {})
        title = meta.get('title', base)
        series = meta.get('series', title)
        track_names = meta.get('tracks', [])
        print(f"'{title}'")
        
        cover = "temp_cov.jpg"
        has_cover = False
        if meta.get('pic'):
            if dl_cover(meta['pic'], cover): has_cover = True

        # 2. MP3 erstellen
        if not os.path.exists(mp3_out):
            sys.stdout.write("  -> Audio Konvertierung... ")
            sys.stdout.flush()
            try:
                with open(taf_path, "rb") as f:
                    f.seek(HEADER_SIZE)
                    audio_data = f.read()
                cmd = ['ffmpeg', '-y', '-f', 'ogg', '-i', 'pipe:0']
                if has_cover:
                    cmd += ['-i', cover, '-map', '0:0', '-map', '1:0', '-c:v', 'copy', '-id3v2_version', '3', '-metadata:s:v', 'title="Cover"', '-metadata:s:v', 'comment="Front"']
                cmd += ['-c:a', 'libmp3lame', '-q:a', '2', '-metadata', f'title={title}', '-metadata', f'artist={series}', mp3_out]
                subprocess.run(cmd, input=audio_data, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print("✓")
            except: print("✗ Fehler")
        else: print("  -> MP3 vorhanden.")

        # 3. KALIBRIERUNG & CUE
        sys.stdout.write("  -> CUE Berechnung (Smart Sync)... ")
        sys.stdout.flush()
        
        # A: Theoretische Zeiten (Header)
        chapters = get_chapters_from_header(taf_path)
        page_map = scan_ogg_positions(taf_path)
        
        # B: Echte Pausen (FFmpeg)
        silences = scan_silence_ffmpeg(mp3_out)
        
        if chapters:
            final_cue = []
            
            for idx, page_seq in enumerate(chapters):
                # 1. Berechne "Soll"-Zeit aus Header
                t_soll = 0.0
                if page_seq > 0:
                    prev = page_seq - 1
                    limit = 100
                    while prev >= 0 and prev not in page_map and limit > 0: prev -= 1; limit -= 1
                    if prev in page_map:
                        t_soll = page_map[prev] / 48000.0
                
                # 2. Suche passendste Stille (Kalibrierung)
                # Wir suchen eine Stille in der Nähe von t_soll
                best_match = None
                min_dist = 999999.0
                
                for (s_start, s_end) in silences:
                    # Distanz zur Pause
                    dist = min(abs(t_soll - s_start), abs(t_soll - s_end))
                    # Oder liegt t_soll IN der Pause?
                    if s_start <= t_soll <= s_end: dist = 0
                    
                    if dist < min_dist:
                        min_dist = dist
                        best_match = (s_start, s_end)
                
                # Entscheidung
                t00 = t_soll # Default: Theoretischer Wert
                t01 = t_soll
                
                if best_match and min_dist < SYNC_WINDOW:
                    # Treffer! Wir nutzen die echte Stille.
                    s_start, s_end = best_match
                    t00 = s_start
                    t01 = s_end
                
                final_cue.append((t00, t01))

            # Schreiben
            clean_t = clean_name(title)
            cue_path = os.path.join(OUTPUT_DIR, f"{clean_t}.cue")
            if has_cover: shutil.copy(cover, os.path.join(OUTPUT_DIR, f"{clean_t}.jpg"))
            
            with open(cue_path, "w", encoding="utf-8") as f:
                f.write(f'REM CREATED BY TAF2MP3 PRO SYNC\nTITLE "{title}"\nPERFORMER "{series}"\nFILE "{os.path.basename(mp3_out)}" MP3\n')
                for k, (t00, t01) in enumerate(final_cue, 1):
                    t_name = f"Chapter {k}"
                    if k <= len(track_names): t_name = track_names[k-1]
                    f.write(f'  TRACK {k:02d} AUDIO\n    TITLE "{t_name}"\n')
                    if (t01 - t00) > 0.5: f.write(f'    INDEX 00 {sec_to_cue(t00)}\n')
                    f.write(f'    INDEX 01 {sec_to_cue(t01)}\n')
            print(f"✓ ({len(chapters)} Tracks synched)")
        else:
            print("✗ Keine Kapitel im Header.")

        if os.path.exists(cover): os.remove(cover)
        print()

    print("="*70)
    print(f"Fertig! -> {os.path.abspath(OUTPUT_DIR)}")
    input("Enter...")

if __name__ == "__main__":
    main()
