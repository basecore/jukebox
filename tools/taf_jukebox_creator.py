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
import re
import difflib
from datetime import datetime

# Wir versuchen Playwright zu importieren. Wenn es fehlt, läuft das Script trotzdem (ohne Scraping).
try:
    from playwright.sync_api import sync_playwright
    from bs4 import BeautifulSoup
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("⚠️  Playwright/BeautifulSoup nicht gefunden. Scraping deaktiviert (nur Basis-Daten).")
    print("   Installiere es mit: pip install playwright beautifulsoup4 && playwright install")

# --- KONFIGURATION ---
SOURCE_DIR = "."         
OUTPUT_DIR = "jukebox_output"
HEADER_SIZE = 4096       
OPUS_SAMPLE_RATE = 48000.0
TONIES_DB_URL = "https://raw.githubusercontent.com/toniebox-reverse-engineering/tonies-json/release/toniesV2.json"

# Keywords für automatisches Tagging
TOPIC_KEYWORDS = {
    "Weihnachten": ["weihnacht", "advent", "christmas", "nikolaus", "rentier", "krippe", "winter"],
    "Märchen": ["märchen", "fee", "hex", "prinz", "könig", "wolf", "rotkäppchen", "grimm", "fabel"],
    "Tiere": ["tier", "zoo", "bauernhof", "dino", "pferd", "hund", "katze", "löwe", "bär", "wal"],
    "Einschlafen": ["schlaf", "gute nacht", "träum", "sandmann", "lullaby", "ruhe", "bett"],
    "Musik": ["lied", "sing", "musik", "song", "tanzen", "rhythmus", "orchester", "minimusiker"],
    "Lernen": ["wissen", "lernen", "schule", "was ist was", "entdeck", "forscher", "englisch", "buchstabe", "zahl"],
    "Abenteuer": ["abenteuer", "pirat", "räuber", "schatz", "reise", "detektiv", "drache", "ritter"],
    "Disney": ["disney", "pixar", "micky", "minnie", "donald", "goofy"],
    "Helden": ["held", "super", "spidey", "batman", "paw patrol", "feuerwehrmann", "ninjago"]
}

# ==========================================
# TEIL 1: DATA MINING & LOGIK
# ==========================================

def download_db():
    print("🌐 Lade Tonie-Datenbank (V2) ...", end=" ")
    try:
        r = requests.get(TONIES_DB_URL, timeout=10)
        if r.status_code == 200: 
            print("OK ✓")
            return r.json()
    except: pass
    print("Fehler (nutze Fallback)")
    return []

def normalize_db(json_data):
    """Wandelt die V2 DB in ein Hash-Dictionary um."""
    db = {}
    for item in json_data:
        # V2 Structure: item['article'], item['data'] -> list
        data_entries = item.get('data', [])
        for entry in data_entries:
            # Hash Mapping
            ids = entry.get('ids', [])
            for audio_id in ids:
                h = audio_id.get('hash')
                if h:
                    db[h.lower()] = entry
    return db

def detect_tags(title, desc, genre=""):
    """Erstellt Tags basierend auf Textanalyse."""
    tags = []
    full_text = (str(title) + " " + str(desc) + " " + str(genre)).lower()
    
    for category, keywords in TOPIC_KEYWORDS.items():
        if any(k in full_text for k in keywords):
            tags.append(category)
    
    # Genre hinzufügen falls sinnvoll
    if genre and genre not in tags:
        tags.append(genre)
        
    return list(set(tags))

def extract_age(text):
    if not text: return 0
    nums = re.findall(r'\d+', text)
    return int(nums[0]) if nums else 0

def scrape_tonie_details(page, url):
    """Scrapt Beschreibung, Alter, Genre von tonies.com"""
    if not url or not PLAYWRIGHT_AVAILABLE: return {}
    
    try:
        page.goto(url, timeout=15000, wait_until="domcontentloaded")
        
        # Cookies & Expand
        try: page.get_by_role("button", name=re.compile("Alle akzeptieren|Akzeptieren")).click(timeout=500)
        except: pass
        try: page.get_by_text("Mehr anzeigen", exact=False).first.click(timeout=500)
        except: pass
        
        soup = BeautifulSoup(page.content(), 'html.parser')
        res = {}
        
        # Beschreibung
        m = soup.find(string=lambda t: t and "Inhalt:" in t)
        if m:
            c = m.find_parent()
            if len(c.get_text()) < 50: c = c.parent
            text = c.get_text(separator="\n").replace("Inhalt:", "").split("Titelliste")[0].strip()
            res['description'] = text
            
        # Badges scannen (Alter, Genre)
        all_texts = [t.get_text(strip=True) for t in soup.find_all(['span', 'div', 'p'])]
        for txt in all_texts:
            if 'Jahre' in txt and 'ab' in txt.lower() and len(txt) < 15:
                res['min_age'] = extract_age(txt)
            elif txt in ['Hörspiel', 'Hörbuch', 'Musik', 'Wissen', 'Deutsch', 'Englisch']:
                # Einfache Heuristik für Genre/Sprache
                if txt in ['Deutsch', 'Englisch']: res['language'] = txt
                else: res['genre'] = txt
                
        return res
    except: return {}

# ==========================================
# TEIL 2: AUDIO / TAF UTILS (Vom User)
# ==========================================

def read_varint(data, offset):
    value = 0; shift = 0; curr = offset
    while True:
        if curr >= len(data): raise ValueError("EOF")
        byte = data[curr]; curr += 1
        value |= (byte & 0x7f) << shift
        if not (byte & 0x80): break
        shift += 7
    return value, curr

def get_chapters_robust(filepath):
    best_chapters = []
    try:
        with open(filepath, "rb") as f:
            data = f.read(HEADER_SIZE)
            for i in range(len(data) - 2):
                if data[i] == 0x22:
                    try:
                        length = data[i+1]; start = i + 2; end = start + length
                        if end > len(data): continue
                        temp = []; curr = start
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
    m = int(seconds // 60); s = int(seconds % 60); f = int((seconds - int(seconds)) * 75)
    return f"{m:02d}:{s:02d}:{f:02d}"

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

# ==========================================
# TEIL 3: KONVERTER & OUTPUT
# ==========================================

def clean_filename(name):
    return "".join([c if c.isalnum() or c in " .-_()" else "_" for c in name]).strip()

def dl_cover(url, target):
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(target, 'wb') as f: f.write(r.content)
            return True
    except: pass
    return False

def convert_audio(audio_data, mp3_path, meta, cover_path=None):
    cmd = ['ffmpeg', '-y', '-f', 'ogg', '-i', 'pipe:0']
    if cover_path:
        cmd += ['-i', cover_path, '-map', '0:0', '-map', '1:0', '-c:v', 'copy', 
                '-id3v2_version', '3', '-metadata:s:v', 'title="Cover"', '-metadata:s:v', 'comment="Front"']
    
    # ID3 Tags für Filter
    title = meta.get('title', 'Unknown')
    artist = meta.get('series', 'Tonie')
    comment = meta.get('description', '')[:200] # Kurz halten für ID3 oder komplett rein
    genre = meta.get('genre', 'Audio')

    cmd += ['-c:a', 'libmp3lame', '-q:a', '2', 
            '-metadata', f'title={title}', 
            '-metadata', f'artist={artist}',
            '-metadata', f'genre={genre}',
            '-metadata', f'comment={comment}',
            mp3_path]

    try:
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        process.communicate(input=audio_data)
        return process.returncode == 0
    except: return False

# ==========================================
# TEIL 4: MAIN LOOP
# ==========================================

def main():
    print("=" * 60)
    print("   JUKEBOX CREATOR & TAF CONVERTER")
    print("=" * 60)
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 1. Dateien finden
    taf_files = sorted(glob.glob(os.path.join(SOURCE_DIR, "*.taf")))
    if not taf_files:
        print("✗ Keine .taf Dateien gefunden."); return

    # 2. DB Laden
    raw_db = download_db()
    db = normalize_db(raw_db)
    
    jukebox_entries = []
    
    # 3. Browser Start (falls Playwright da ist)
    browser = None
    page = None
    if PLAYWRIGHT_AVAILABLE:
        print("🚀 Starte Scraper-Engine (für Altersfreigabe & Details)...")
        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

    print(f"\nVerarbeite {len(taf_files)} Dateien...\n")
    
    for i, taf_path in enumerate(taf_files, 1):
        file_hash = get_hash(taf_path)
        meta = db.get(file_hash, {})
        
        # Basis-Daten
        series = meta.get('series', '')
        episode = meta.get('episode', '')
        title = f"{series} - {episode}" if series and episode else (series or episode or "Unbekannt")
        orig_filename = clean_filename(title)
        
        print(f"[{i}/{len(taf_files)}] {orig_filename}")
        
        # Scrape & Enrich (Fehlende Daten holen)
        scraped_info = {}
        if page and meta.get('web'):
            # Wir scrapen nur, wenn wichtige Filter fehlen
            if not meta.get('description') or not meta.get('age'):
                print("   🔍 Scrape Details...", end=" ")
                scraped_info = scrape_tonie_details(page, meta.get('web'))
                print("OK")
        
        # Daten Mergen (Scraped > DB)
        final_desc = scraped_info.get('description') or meta.get('description', '')
        final_age = scraped_info.get('min_age') or meta.get('age') or 0
        try: final_age = int(final_age)
        except: final_age = 0
        
        final_genre = scraped_info.get('genre') or "Hörspiel"
        
        # Auto-Tags generieren
        tags = detect_tags(title, final_desc, final_genre)
        
        # Pfade
        base_name = clean_filename(title)
        mp3_name = f"{base_name}.mp3"
        jpg_name = f"{base_name}.jpg"
        
        target_mp3 = os.path.join(OUTPUT_DIR, mp3_name)
        target_jpg = os.path.join(OUTPUT_DIR, jpg_name)
        
        # Cover
        has_cover = False
        if not os.path.exists(target_jpg) and meta.get('image'):
            dl_cover(meta['image'], target_jpg)
        if os.path.exists(target_jpg): has_cover = True
        
        # Konvertierung
        if not os.path.exists(target_mp3):
            print("   🎵 Konvertiere...", end=" ")
            try:
                with open(taf_path, "rb") as f:
                    f.seek(HEADER_SIZE)
                    audio_data = f.read()
                
                # Meta-Objekt für ID3
                id3_meta = {'title': title, 'series': series, 'description': final_desc, 'genre': final_genre}
                if convert_audio(audio_data, target_mp3, id3_meta, target_jpg if has_cover else None):
                    print("Fertig ✓")
                else: print("Fehler ✗")
            except Exception as e: print(f"Error: {e}")
        else:
            print("   ⏭️  MP3 existiert bereits.")
            
        # Jukebox Entry erstellen (NEUE STRUKTUR)
        entry = {
            "tagId": f"auto_{file_hash[:10]}", # Generierte ID oder echter Hash
            "name": title,
            "playlistFileNames": [mp3_name],
            "imageFileName": jpg_name if has_cover else None,
            # Hier die erweiterten Filter-Daten:
            "meta": {
                "series": series,
                "episode": episode,
                "description": final_desc,
                "age_recommendation": final_age, # Zahl (int) zum Filtern!
                "genre": final_genre,
                "language": scraped_info.get('language', 'Deutsch'),
                "runtime": meta.get('runtime', 0)
            },
            "tags": tags, # Liste von Tags ["Weihnachten", "Hörspiel", ...]
            "filter_age": final_age # Für schnellen Zugriff
        }
        jukebox_entries.append(entry)
        print()

    # Browser Stop
    if browser: browser.close()
    
    # 4. JSON Speichern
    json_out = os.path.join(OUTPUT_DIR, "jukebox.json")
    print("-" * 60)
    print(f"💾 Erstelle {json_out} ...")
    
    with open(json_out, 'w', encoding='utf-8') as f:
        json.dump(jukebox_entries, f, indent=4, ensure_ascii=False)
        
    print("✅ FERTIG! Du kannst die jukebox.json jetzt in dein Tool laden.")
    print("   Die Filter funktionieren nun über 'filter_age' und 'tags'.")

if __name__ == "__main__":
    main()
