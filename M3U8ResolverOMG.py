#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# M3U8 Resolver per OMG TV
# Questo script risolve gli URL di streaming M3U8 con logica iframe
# Versione 1.0.0

import sys
import json
import os
import requests
import re
import logging
import traceback
from urllib.parse import urlparse, quote_plus

# Configurazione
RESOLVER_VERSION = "1.0.0"
CACHE_DURATION = 20 * 60  # 20 minuti

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("m3u8_resolver.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("m3u8_resolver")

def create_proxy_session(proxy_config):
    """
    Crea una sessione configurata per utilizzare il proxy
    """
    if not proxy_config:
        logger.info("Utilizzo connessione diretta (nessun proxy)")
        return requests.Session()
    
    try:
        proxy_url = proxy_config.get('url', '').strip('/')
        proxy_pwd = proxy_config.get('password', '')
        
        if not proxy_url:
            logger.warning("URL proxy non specificato, utilizzo connessione diretta")
            return requests.Session()
        
        proxy_session = requests.Session()
        
        logger.info(f"Configurazione proxy: URL={proxy_url}")
        
        return proxy_session
        
    except Exception as e:
        logger.error(f"Errore nella configurazione del proxy: {e}")
        return requests.Session()

def build_proxy_url(proxy_config, original_url, headers=None):
    """
    Costruisce l'URL per il proxy con endpoint stream standard
    """
    if not proxy_config:
        return original_url
    
    proxy_url = proxy_config.get('url', '').strip('/')
    proxy_pwd = proxy_config.get('password', '')
    
    # Prepara i parametri per il proxy
    params = {
        'api_password': proxy_pwd,
        'd': original_url
    }
    
    # Aggiungi headers con prefisso h_
    if headers:
        headers_map = {
            'User-Agent': headers.get('User-Agent', headers.get('user-agent', '')),
            'Referer': headers.get('Referer', headers.get('referer', '')),
            'Origin': headers.get('Origin', headers.get('origin', ''))
        }
        
        for key, value in headers_map.items():
            if value:
                params[f'h_{key.lower()}'] = value
    
    # Costruisci l'URL completo del proxy usando sempre /proxy/stream
    proxy_full_url = f"{proxy_url}/proxy/stream?{urlencode(params)}"
    
    logger.info(f"URL proxy generato: {proxy_full_url}")
    
    return proxy_full_url

def resolve_m3u8_link(url, headers=None, channel_name=None, session=None):
    """
    Tenta di risolvere un URL M3U8.
    Prova prima la logica specifica per iframe (tipo Daddylive), inclusa la lookup della server_key.
    Se fallisce, verifica se l'URL iniziale era un M3U8 diretto e lo restituisce.
    """
    if not url:
        logger.error("URL non fornito.")
        return {"resolved_url": None, "headers": headers or {}}

    logger.info(f"Tentativo di risoluzione URL: {url}")
    # Utilizza gli header forniti, altrimenti usa un User-Agent di default
    current_headers = headers if headers else {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0+Safari/537.36'}

    initial_response_text = None
    final_url_after_redirects = None

    try:
        # Utilizza una sessione per gestire i cookie e i redirect
        with session or requests.Session() as session:
            # Primo passo: Richiesta all'URL iniziale
            logger.info(f"Passo 1: Richiesta a {url}")
            response = session.get(url, headers=current_headers, allow_redirects=True, timeout=10)
            response.raise_for_status() # Solleva un'eccezione per risposte con stato di errore (4xx o 5xx)
            initial_response_text = response.text
            final_url_after_redirects = response.url # Mantieni questo per debug se necessario
            logger.info(f"Passo 1 completato. URL finale dopo redirect: {final_url_after_redirects}")

            # Prova la logica dell'iframe
            logger.info("Tentativo con logica iframe...")
            try:
                # Secondo passo (Iframe): Trova l'iframe src nella risposta iniziale
                iframes = re.findall(r'iframe src="([^"]+)', initial_response_text)
                if not iframes:
                    # Se non trova l'iframe, solleva un'eccezione per passare al fallback
                    raise ValueError("Nessun iframe src trovato.")

                url2 = iframes[0]
                logger.info(f"Passo 2 (Iframe): Trovato iframe URL: {url2}")

                # Terzo passo (Iframe): Richiesta all'URL dell'iframe
                # Aggiorna Referer e Origin per la richiesta all'iframe
                referer_raw = urlparse(url2).scheme + "://" + urlparse(url2).netloc
                current_headers['Referer'] = url2
                current_headers['Origin'] = referer_raw
                logger.info(f"Passo 3 (Iframe): Richiesta a {url2}")
                response = session.get(url2, headers=current_headers, timeout=10)
                response.raise_for_status()
                iframe_response_text = response.text
                logger.info("Passo 3 (Iframe) completato.")

                # Quarto passo (Iframe): Estrai parametri dinamici dall'iframe response
                channel_key_match = re.search(r'(?s) channelKey = \"([^"]*)', iframe_response_text)
                auth_ts_match = re.search(r'(?s) authTs\s*= \"([^"]*)', iframe_response_text)
                auth_rnd_match = re.search(r'(?s) authRnd\s*= \"([^"]*)', iframe_response_text)
                auth_sig_match = re.search(r'(?s) authSig\s*= \"([^"]*)', iframe_response_text)
                auth_host_match = re.search(r'\}\s*fetchWithRetry\(\s*\'([^\']*)', iframe_response_text)
                # Estrai anche il parametro per la server lookup URL
                server_lookup_match = re.search('n fetchWithRetry\(\s*\'([^\']*)', iframe_response_text)

                if not all([channel_key_match, auth_ts_match, auth_rnd_match, auth_sig_match, auth_host_match, server_lookup_match]):
                     raise ValueError("Impossibile estrarre tutti i parametri dinamici dall'iframe response.")

                channel_key = channel_key_match.group(1)
                auth_ts = auth_ts_match.group(1)
                auth_rnd = auth_rnd_match.group(1)
                auth_sig = quote_plus(auth_sig_match.group(1)) # Codifica auth_sig
                auth_host = auth_host_match.group(1)
                server_lookup = server_lookup_match.group(1) # Parametro per la server lookup URL

                logger.info("Passo 4 (Iframe): Parametri dinamici estratti.")

                # Quinto passo (Iframe): Richiesta di autenticazione
                auth_url = f'{auth_host}{channel_key}&ts={auth_ts}&rnd={auth_rnd}&sig={auth_sig}'
                logger.info(f"Passo 5 (Iframe): Richiesta di autenticazione a {auth_url}")
                auth_response = session.get(auth_url, headers=current_headers, timeout=10)
                auth_response.raise_for_status()
                logger.info("Passo 5 (Iframe) completato.")

                # Sesto passo (Iframe): Richiesta di server lookup per ottenere la server_key
                server_lookup_url = f"https://{urlparse(url2).netloc}{server_lookup}{channel_key}"
                logger.info(f"Passo 6 (Iframe): Richiesta server lookup a {server_lookup_url}")
                server_lookup_response = session.get(server_lookup_url, headers=current_headers, timeout=10)
                server_lookup_response.raise_for_status()
                server_lookup_data = server_lookup_response.json() # Assumiamo che la risposta sia JSON
                logger.info("Passo 6 (Iframe) completato.")

                # Settimo passo (Iframe): Estrai server_key dalla risposta di server lookup
                server_key = server_lookup_data.get('server_key')
                if not server_key:
                    raise ValueError("'server_key' non trovato nella risposta di server lookup.")
                logger.info(f"Passo 7 (Iframe): Estratto server_key: {server_key}")

                # Ottavo passo (Iframe): Costruisci il link finale
                # Trova l'host finale per l'm3u8 (potrebbe essere diverso da auth_host)
                host_match = re.search('(?s)m3u8 =.*?:.*?:.*?".*?".*?"([^"]*)', iframe_response_text)
                if not host_match:
                     raise ValueError("Impossibile trovare l'host finale per l'm3u8.")
                host = host_match.group(1)
                logger.info(f"Passo 8 (Iframe): Trovato host finale per m3u8: {host}")

                # Costruisci l'URL finale del flusso
                final_stream_url = (
                    f'https://{server_key}{host}{server_key}/{channel_key}/mono.m3u8'
                )

                # Prepara gli header per lo streaming
                stream_headers = {
                    'User-Agent': current_headers.get('User-Agent', ''),
                    'Referer': referer_raw,
                    'Origin': referer_raw
                }
                
                return {
                    "resolved_url": final_stream_url,
                    "headers": stream_headers
                }

            except (ValueError, requests.exceptions.RequestException) as e:
                # Se la logica iframe fallisce, prova il fallback
                logger.error(f"Logica iframe fallita: {e}")
                logger.info("Tentativo fallback: verifica se l'URL iniziale era un M3U8 diretto...")

                # Fallback: Verifica se la risposta iniziale era un file M3U8 diretto
                if initial_response_text and initial_response_text.strip().startswith('#EXTM3U'):
                    logger.info("Fallback riuscito: Trovato file M3U8 diretto.")
                    return {
                        "resolved_url": final_url_after_redirects,
                        "headers": current_headers
                    }
                else:
                    logger.error("Fallback fallito: La risposta iniziale non era un M3U8 diretto.")
                    return {
                        "resolved_url": url,  # Restituisci l'URL originale in caso di fallimento
                        "headers": current_headers
                    }

    except requests.exceptions.RequestException as e:
        logger.error(f"Errore durante la richiesta HTTP iniziale: {e}")
        logger.debug(f"Dettagli errore: {traceback.format_exc()}")
        return {"resolved_url": url, "headers": current_headers}
    except Exception as e:
        logger.error(f"Errore generico durante la risoluzione: {e}")
        logger.debug(f"Dettagli errore: {traceback.format_exc()}")
        return {"resolved_url": url, "headers": current_headers}

def resolve_link(url, headers=None, channel_name=None, proxy_config=None):
    """
    Funzione principale che risolve un link
    """
    logger.info(f"Risoluzione URL: {url}")
    logger.info(f"Canale: {channel_name}")
    
    # Crea una sessione, con proxy se configurato
    session = create_proxy_session(proxy_config) if proxy_config else requests.Session()
    
    try:
        # Risolvi l'URL usando la sessione
        resolved_result = resolve_m3u8_link(url, headers, channel_name, session)
        
        # Se proxy è configurato, passa la risoluzione attraverso il proxy
        if proxy_config and resolved_result.get('resolved_url'):
            proxy_url = build_proxy_url(proxy_config, resolved_result['resolved_url'], resolved_result['headers'])
            
            return {
                "resolved_url": resolved_result['resolved_url'],
                "proxied_url": proxy_url,
                "headers": resolved_result['headers']
            }
        
        return resolved_result
    
    except Exception as e:
        logger.error(f"Errore generale nella risoluzione: {e}")
        return {"resolved_url": url, "headers": headers or {}}

def main():
    """
    Funzione principale che gestisce i parametri di input
    """
    # Verifica parametri di input
    if len(sys.argv) < 2:
        print("Utilizzo: python3 M3U8Resolver.py [--check|--resolve input_file output_file]")
        sys.exit(1)
    
    # Comando check: verifica che lo script sia valido
    if sys.argv[1] == "--check":
        print("resolver_ready: True")
        sys.exit(0)
    
    # Comando resolve: risolvi un URL
    if sys.argv[1] == "--resolve" and len(sys.argv) >= 4:
        input_file = sys.argv[2]
        output_file = sys.argv[3]
        
        try:
            # Leggi i parametri di input
            with open(input_file, 'r') as f:
                input_data = json.load(f)
            
            url = input_data.get('url', '')
            headers = input_data.get('headers', {})
            channel_name = input_data.get('channel_name', 'unknown')
            proxy_config = input_data.get('proxy_config', None)
            
            # Risolvi l'URL
            result = resolve_link(url, headers, channel_name, proxy_config)
            
            # Scrivi il risultato
            with open(output_file, 'w') as f:
                json.dump(result, f, indent=2)
            
            print(f"URL risolto salvato in: {output_file}")
            sys.exit(0)
        except Exception as e:
            print(f"Errore: {str(e)}")
            sys.exit(1)
    
    print("Comando non valido")
    sys.exit(1)

if __name__ == "__main__":
    main()