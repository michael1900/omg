import random
import json
import os
import requests
from bs4 import BeautifulSoup
import time

# Costanti
M3U8_OUTPUT_FILE = "247ita.m3u8"
REFERER = "forcedtoplay.xyz"
ORIGIN = "forcedtoplay.xyz"
# File e URL statici
daddyLiveChannelsFileName = '247channels.html'
daddyLiveChannelsURL = 'https://daddylive.dad/24-7-channels.php'

# Headers per le richieste
headers = {
    "Accept": "*/*",
    "Accept-Language": "it-IT,it;q=0.9,en-US;q=0.8,en;q=0.7,es;q=0.6,ru;q=0.5",
    "Priority": "u=1, i",
    "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
    "Sec-Ch-UA-Mobile": "?0",
    "Sec-Ch-UA-Platform": "Windows",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Storage-Access": "active",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
}

# Mappa dei loghi per alcuni canali specifici
STATIC_LOGOS = {
    "sky uno": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-uno-it.png",
    "rai 1": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/rai-1-it.png",
    "rai 2": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/rai-2-it.png",
    "rai 3": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/rai-3-it.png",
    "eurosport 1": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/spain/eurosport-1-es.png",
    "eurosport 2": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/spain/eurosport-2-es.png",
    "italia 1": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/italia1-it.png",
    "la7": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/la7-it.png",
    "la7d": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/la7d-it.png",
    "rai sport": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/rai-sport-it.png",
    "rai premium": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/rai-premium-it.png",
    "sky sports golf": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-golf-it.png",
    "sky sport motogp": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-motogp-it.png",
    "sky sport tennis": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-tennis-it.png",
    "sky sport f1": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-f1-it.png",
    "sky sport football": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-football-it.png",
    "sky sport uno": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-uno-it.png",
    "sky sport arena": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-arena-it.png",
    "sky cinema collection": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-collection-it.png",
    "sky cinema uno": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-uno-it.png",
    "sky cinema action": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-action-it.png",
    "sky cinema comedy": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-comedy-it.png",
    "sky cinema uno +24": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-uno-plus24-it.png",
    "sky cinema romance": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-romance-it.png",
    "sky cinema family": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-family-it.png",
    "sky cinema due +24": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-due-plus24-it.png",
    "sky cinema drama": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-drama-it.png",
    "sky cinema suspense": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-cinema-suspense-it.png",
    "sky sport 24": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-24-it.png",
    "sky sport calcio": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-sport-calcio-it.png",
    "sky sport": "https://play-lh.googleusercontent.com/u7UNH06SU4KsMM4ZGWr7wghkJYN75PNCEMxnIYULpA__VPg8zfEOYMIAhUaIdmZnqw=w480-h960-rw",
    "sky calcio 1": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-1-alt-de.png",
    "sky calcio 2": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-2-alt-de.png",
    "sky calcio 3": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-3-alt-de.png",
    "sky calcio 4": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-4-alt-de.png",
    "sky calcio 5": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-5-alt-de.png",
    "sky calcio 6": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-6-alt-de.png",
    "sky calcio 7": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/germany/sky-select-7-alt-de.png",
    "sky serie": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/sky-serie-it.png",
    "20 mediaset": "https://raw.githubusercontent.com/tv-logo/tv-logos/main/countries/italy/20-it.png",
    "dazn 1": "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/DAZN_1_Logo.svg/774px-DAZN_1_Logo.svg.png"
}

# Mappa degli ID TVG per alcuni canali specifici
STATIC_TVG_IDS = {
    "sky uno": "sky uno",
    "rai 1": "rai 1",
    "rai 2": "rai 2",
    "rai 3": "rai 3",
    "eurosport 1": "eurosport 1",
    "eurosport 2": "eurosport 2",
    "italia 1": "italia 1",
    "la7": "la7",
    "la7d": "la7d",
    "rai sport": "rai sport",
    "rai premium": "rai premium",
    "sky sports golf": "sky sport golf",
    "sky sport motogp": "sky sport motogp",
    "sky sport tennis": "sky sport tennis",
    "sky sport f1": "sky sport f1",
    "sky sport football": "sky sport football",
    "sky sport uno": "sky sport uno",
    "sky sport arena": "sky sport arena",
    "sky cinema collection": "sky cinema collection",
    "sky cinema uno": "sky cinema uno",
    "sky cinema action": "sky cinema action",
    "sky cinema comedy": "sky cinema comedy",
    "sky cinema uno +24": "sky cinema uno +24",
    "sky cinema romance": "sky cinemar omance",
    "sky cinema family": "sky cinema family",
    "sky cinema due +24": "sky cinema Due +24",
    "sky cinema drama": "sky cinema drama",
    "sky cinema suspense": "sky cinema suspense",
    "sky sport 24": "sky sport 24",
    "sky sport calcio": "Sky Sport Calcio",
    "sky calcio 1": "Sky Sport",
    "sky calcio 2": "Sky Sport 2",
    "sky calcio 3": "sky sport 3",
    "sky calcio 4": "sky sport 4",
    "sky calcio 5": "sky sport 5",
    "sky calcio 6": "sky sport 6",
    "sky calcio 7": "sky sport 7",
    "sky serie": "sky serie",
    "20 mediaset": "Mediaset 20",
}

# Mappa delle categorie per alcuni canali specifici
STATIC_CATEGORIES = {
    "sky uno": "Sky",
    "rai 1": "Rai Tv",
    "rai 2": "Rai Tv",
    "rai 3": "Rai Tv",
    "eurosport 1": "Sport",
    "eurosport 2": "Sport",
    "italia 1": "Mediaset",
    "la7": "Tv Italia",
    "la7d": "Tv Italia",
    "rai sport": "Sport",
    "rai premium": "Rai Tv",
    "sky sports golf": "Sport",
    "sky sport motogp": "Sport",
    "sky sport tennis": "Sport",
    "sky sport f1": "Sport",
    "sky sport football": "Sport",
    "sky sport uno": "Sport",
    "sky sport arena": "Sport",
    "sky cinema collection": "Sky",
    "sky cinema uno": "Sky",
    "sky cinema action": "Sky",
    "sky cinema comedy": "Sky",
    "sky cinema uno +24": "Sky",
    "sky cinema romance": "Sky",
    "sky cinema family": "Sky",
    "sky cinema due +24": "Sky",
    "sky cinema drama": "Sky",
    "sky cinema suspense": "Sky",
    "sky sport 24": "Sport",
    "sky sport calcio": "Sport",
    "sky calcio 1": "Sport",
    "sky calcio 2": "Sport",
    "sky calcio 3": "Sport",
    "sky calcio 4": "Sport",
    "sky calcio 5": "Sport",
    "sky calcio 6": "Sport",
    "sky calcio 7": "Sport",
    "sky serie": "Sky",
    "20 mediaset": "Mediaset",
}

def get_stream_link(dlhd_id, max_retries=3):
    print(f"Getting stream link for channel ID: {dlhd_id}...")

    base_timeout = 10  # Base timeout in seconds

    for attempt in range(max_retries):
        try:
            # Use timeout for all requests
            response = requests.get(
                f"https://daddylive.dad/embed/stream-{dlhd_id}.php",
                headers=headers,
                timeout=base_timeout
            )
            response.raise_for_status()
            response.encoding = 'utf-8'

            response_text = response.text
            if not response_text:
                print(f"Warning: Empty response received for channel ID: {dlhd_id} (attempt {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    # Calculate exponential backoff with jitter
                    sleep_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                    continue
                return None

            soup = BeautifulSoup(response_text, 'html.parser')
            iframe = soup.find('iframe', id='thatframe')

            if iframe is None:
                print(f"Debug: iframe with id 'thatframe' NOT FOUND for channel ID {dlhd_id} (attempt {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                    continue
                return None

            if iframe and iframe.get('src'):
                real_link = iframe.get('src')
                parent_site_domain = real_link.split('/premiumtv')[0]
                server_key_link = (f'{parent_site_domain}/server_lookup.php?channel_id=premium{dlhd_id}')
                server_key_headers = headers.copy()
                server_key_headers["Referer"] = f"https://newembedplay.xyz/premiumtv/daddylivehd.php?id={dlhd_id}"
                server_key_headers["Origin"] = "https://newembedplay.xyz"
                server_key_headers["Sec-Fetch-Site"] = "same-origin"

                response_key = requests.get(
                    server_key_link,
                    headers=server_key_headers,
                    allow_redirects=False,
                    timeout=base_timeout
                )

                # Add adaptive delay between requests
                time.sleep(random.uniform(1, 3))
                response_key.raise_for_status()

                try:
                    server_key_data = response_key.json()
                except json.JSONDecodeError:
                    print(f"JSON Decode Error for channel ID {dlhd_id}: Invalid JSON response: {response_key.text[:100]}...")
                    if attempt < max_retries - 1:
                        sleep_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                        continue
                    return None

                if 'server_key' in server_key_data:
                    server_key = server_key_data['server_key']
                    stream_url = f"https://{server_key}new.newkso.ru/{server_key}/premium{dlhd_id}/mono.m3u8"
                    print(f"Stream URL retrieved for channel ID: {dlhd_id}")
                    return stream_url
                else:
                    print(f"Error: 'server_key' not found in JSON response from {server_key_link} (attempt {attempt+1}/{max_retries})")
                    if attempt < max_retries - 1:
                        sleep_time = (2 ** attempt) + random.uniform(0, 1)
                        print(f"Retrying in {sleep_time:.2f} seconds...")
                        time.sleep(sleep_time)
                        continue
                    return None
            else:
                print(f"Error: iframe with id 'thatframe' found, but 'src' attribute is missing for channel ID {dlhd_id} (attempt {attempt+1}/{max_retries})")
                if attempt < max_retries - 1:
                    sleep_time = (2 ** attempt) + random.uniform(0, 1)
                    print(f"Retrying in {sleep_time:.2f} seconds...")
                    time.sleep(sleep_time)
                    continue
                return None

        except requests.exceptions.Timeout:
            print(f"Timeout error for channel ID {dlhd_id} (attempt {attempt+1}/{max_retries})")
            if attempt < max_retries - 1:
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                continue
            return None

        except requests.exceptions.RequestException as e:
            print(f"Request Exception for channel ID {dlhd_id} (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                continue
            return None

        except Exception as e:
            print(f"General Exception for channel ID {dlhd_id} (attempt {attempt+1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                sleep_time = (2 ** attempt) + random.uniform(0, 1)
                print(f"Retrying in {sleep_time:.2f} seconds...")
                time.sleep(sleep_time)
                continue
            return None

    return None  # If we get here, all retries failed

def fetch_with_debug(filename, url):
    try:
        print(f'Downloading {url}...')
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        with open(filename, 'wb') as file:
            file.write(response.content)

        print(f'File {filename} downloaded successfully.')
    except requests.exceptions.RequestException as e:
        print(f'Error downloading {url}: {e}')

def search_category(channel_name):
    return STATIC_CATEGORIES.get(channel_name.lower().strip(), "Undefined")

def search_streams(file_path, keyword):
    matches = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            soup = BeautifulSoup(file.read(), 'html.parser')
            links = soup.find_all('a', href=True)

        for link in links:
            if keyword.lower() in link.text.lower():
                href = link['href']
                stream_number = href.split('-')[-1].replace('.php', '')
                stream_name = link.text.strip()
                match = (stream_number, stream_name)

                if match not in matches:
                    matches.append(match)
    except FileNotFoundError:
        print(f'The file {file_path} does not exist.')
    return matches

def search_logo(channel_name):
    channel_name_lower = channel_name.lower().strip()
    for key, url in STATIC_LOGOS.items():
        if key in channel_name_lower:
            return url
    return "https://raw.githubusercontent.com/cribbiox/eventi/refs/heads/main/ddlive.png"

def search_tvg_id(channel_name):
    channel_name_lower = channel_name.lower().strip()
    for key, tvg_id in STATIC_TVG_IDS.items():
        if key in channel_name_lower:
            return tvg_id
    return "unknown"

def generate_m3u8_247(matches):
    if not matches:
        print("No matches found for 24/7 channels. Skipping M3U8 generation.")
        return 0

    processed_247_channels = 0

    # Inizializza il file M3U8
    with open(M3U8_OUTPUT_FILE, 'w', encoding='utf-8') as file:
        file.write('#EXTM3U\n')

    # Aggiungi i canali 24/7
    with open(M3U8_OUTPUT_FILE, 'a', encoding='utf-8') as file:
        for channel in matches:
            channel_id = channel[0]
            channel_name = channel[1].replace("Italy", "").replace("8", "").replace("(251)", "").replace("(252)", "").replace("(253)", "").replace("(254)", "").replace("(255)", "").replace("(256)", "").replace("(257)", "").replace("HD+", "")
            tvicon_path = search_logo(channel_name)
            tvg_id = search_tvg_id(channel_name)
            category = search_category(channel_name)
            print(f"Processing 24/7 channel: {channel_name} - Channel Count (24/7): {processed_247_channels + 1}")

            stream_url_dynamic = get_stream_link(channel_id)

            if stream_url_dynamic:
                file.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name} (D)\n")
                file.write(f'#EXTVLCOPT:http-referrer=https://{REFERER}/\n')
                file.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36\n')
                file.write(f'#EXTVLCOPT:http-origin=https://{ORIGIN}\n')
                file.write(f"{stream_url_dynamic}\n\n")
                processed_247_channels += 1
            else:
                print(f"Failed to get stream URL for 24/7 channel ID: {channel_id}. Skipping M3U8 entry for this channel.")

    return processed_247_channels

def add_dazn1_channel():
    print("Aggiunta manuale del canale DAZN 1")
    channel_id = "877"
    channel_name = "DAZN 1"
    tvicon_path = STATIC_LOGOS.get("dazn 1", "https://upload.wikimedia.org/wikipedia/commons/thumb/a/a2/DAZN_1_Logo.svg/774px-DAZN_1_Logo.svg.png")
    tvg_id = "DAZN 1"
    category = "Sport"

    stream_url_dynamic = get_stream_link(channel_id)
    if stream_url_dynamic:
        with open(M3U8_OUTPUT_FILE, 'a', encoding='utf-8') as file:
            file.write(f"#EXTINF:-1 tvg-id=\"{tvg_id}\" tvg-name=\"{channel_name}\" tvg-logo=\"{tvicon_path}\" group-title=\"{category}\", {channel_name} (D)\n")
            file.write(f'#EXTVLCOPT:http-referrer=https://caq21harderv991gpluralplay.xyz/\n')
            file.write('#EXTVLCOPT:http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36\n')
            file.write('#EXTVLCOPT:http-origin=https://caq21harderv991gpluralplay.xyz\n')
            file.write(f"{stream_url_dynamic}\n\n")
            return 1
    else:
        print(f"Failed to get stream URL for DAZN 1 channel ID: {channel_id}")
        return 0

# Rimuovi il file esistente per garantirne la rigenerazione
if os.path.exists(M3U8_OUTPUT_FILE):
    os.remove(M3U8_OUTPUT_FILE)

# Fetch e generazione M3U8 per i canali 24/7
fetch_with_debug(daddyLiveChannelsFileName, daddyLiveChannelsURL)
matches_247 = search_streams(daddyLiveChannelsFileName, "Italy")
total_247_channels = generate_m3u8_247(matches_247)

# Aggiungi il canale DAZN 1
dazn_added = add_dazn1_channel()

print(f"Script completato. Canali 24/7 aggiunti: {total_247_channels}, DAZN 1 aggiunto: {dazn_added}")
