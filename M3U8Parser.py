import re
import os

def parse_m3u8_file(file_path):
    """
    Parsa un file M3U8 ed estrae le informazioni sui canali e i loro URL con header.
    """
    channels = []
    current_channel = None
    current_headers = {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                if line.startswith('#EXTINF:'):
                    # Salva il canale precedente se esiste
                    if current_channel:
                        channels.append({
                            'name': current_channel.get('name', 'Unknown Channel'),
                            'group': current_channel.get('group', 'Undefined'),
                            'logo': current_channel.get('logo', ''),
                            'tvg_id': current_channel.get('tvg_id', ''),
                            'url': '', # L'URL verrà aggiunto nella prossima riga non commentata
                            'headers': current_headers.copy()
                        })
                    
                    # Inizia un nuovo canale
                    current_channel = {}
                    current_headers = {} # Resetta gli header per il nuovo canale

                    # Estrai info da EXTINF
                    match = re.search(r'tvg-id="([^"]*)"', line)
                    if match:
                        current_channel['tvg_id'] = match.group(1)
                    match = re.search(r'tvg-name="([^"]*)"', line)
                    if match:
                        current_channel['name'] = match.group(1)
                    match = re.search(r'tvg-logo="([^"]*)"', line)
                    if match:
                        current_channel['logo'] = match.group(1)
                    match = re.search(r'group-title="([^"]*)"', line)
                    if match:
                        current_channel['group'] = match.group(1)
                    # Estrai il nome del canale dopo la virgola
                    match = re.search(r',(.+)$', line)
                    if match:
                         # Usa il nome dopo la virgola come fallback o aggiunta
                         # Preferiamo tvg-name se presente, altrimenti usiamo questo
                         if 'name' not in current_channel or not current_channel['name']:
                             current_channel['name'] = match.group(1).strip()


                elif line.startswith('#EXTVLCOPT:'):
                    # Estrai header da EXTVLCOPT
                    match = re.search(r'http-([^=]+)=(.+)', line)
                    if match:
                        header_key = match.group(1).strip()
                        header_value = match.group(2).strip()
                        # Normalizza i nomi degli header (es. http-user-agent -> User-Agent)
                        if header_key == 'referrer':
                            current_headers['Referer'] = header_value
                        elif header_key == 'user-agent':
                            current_headers['User-Agent'] = header_value
                        elif header_key == 'origin':
                            current_headers['Origin'] = header_value
                        else:
                             # Aggiungi altri header se presenti
                             current_headers[header_key] = header_value

                elif line and not line.startswith('#'):
                    # Questa è la riga dell'URL
                    if current_channel:
                        current_channel['url'] = line
                        # Aggiungi il canale alla lista e resetta
                        channels.append({
                            'name': current_channel.get('name', 'Unknown Channel'),
                            'group': current_channel.get('group', 'Undefined'),
                            'logo': current_channel.get('logo', ''),
                            'tvg_id': current_channel.get('tvg_id', ''),
                            'url': current_channel['url'],
                            'headers': current_headers.copy()
                        })
                        current_channel = None # Resetta per il prossimo blocco
                        current_headers = {} # Resetta gli header

        # Aggiungi l'ultimo canale se il file non termina con un URL
        if current_channel and current_channel.get('url'):
             channels.append({
                'name': current_channel.get('name', 'Unknown Channel'),
                'group': current_channel.get('group', 'Undefined'),
                'logo': current_channel.get('logo', ''),
                'tvg_id': current_channel.get('tvg_id', ''),
                'url': current_channel['url'],
                'headers': current_headers.copy()
            })


    except FileNotFoundError:
        print(f"Errore: File non trovato a {file_path}")
        return []
    except Exception as e:
        print(f"Errore durante la lettura o il parsing del file M3U8: {e}")
        return []

    return channels

if __name__ == "__main__":
    # Esempio di utilizzo:
    m3u8_file = '/home/pi/daddy/new/itaevents.m3u8'
    channel_list = parse_m3u8_file(m3u8_file)

    if channel_list:
        print(f"Trovati {len(channel_list)} canali nel file {m3u8_file}")
        print("\nPrimi 5 canali:")
        for i, channel in enumerate(channel_list[:5]):
            print(f"--- Canale {i+1} ---")
            print(f"Nome: {channel['name']}")
            print(f"Gruppo: {channel['group']}")
            print(f"Logo: {channel['logo']}")
            print(f"URL: {channel['url']}")
            print(f"Headers: {channel['headers']}")
            print("-" * 10)
    else:
        print("Nessun canale trovato o errore nel parsing.")