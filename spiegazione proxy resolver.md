spiegazione proxy resolver 

## Spiegazione delle modifiche
Ho integrato la funzionalità di M3U8Resolver.py direttamente in proxy.py con le seguenti modifiche:

1. Ho aggiunto la funzione resolve_m3u8_link() che contiene la logica di risoluzione dei link da M3U8Resolver.py
2. Ho creato un nuovo endpoint /proxy/resolve che:
   - Accetta un URL da risolvere
   - Utilizza la funzione resolve_m3u8_link() per ottenere l'URL risolto
   - Restituisce un file M3U8 che punta all'URL risolto attraverso il proxy
Ora puoi utilizzare il proxy in questo modo:

1. Per risolvere un canale e riprodurlo immediatamente:
   
   ```
   http://localhost:7860/proxy/resolve?url=https://example.com/channel/123
   ```
2. Puoi anche passare header personalizzati:
   
   ```
   http://localhost:7860/proxy/resolve?url=https://example.com/channel/123&
   h_User_Agent=Mozilla/5.0&h_Referer=https://example.com
   ```
Questo approccio integra completamente la funzionalità di risoluzione nel proxy, permettendoti di risolvere i link dei canali al volo quando li richiedi.