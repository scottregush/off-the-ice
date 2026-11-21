# Off the Ice

Chi manca in National League: infortuni, squalifiche e stranieri in tribuna delle 14 squadre, con rientro previsto, ultime 5 partite e le rose personali per il fantahockey.

Sito: https://scottregush.github.io/off-the-ice/

## Come funziona

- `index.html` è l'intera pagina: dati, stile e codice in un solo file, senza server.
- Le rose dei visitatori restano nel loro browser (localStorage).
- I dati vengono ricontrollati automaticamente due volte al giorno (mattino e dopo le partite serali) e il file viene aggiornato solo quando le fonti cambiano.
- `tools/build_site.py` genera `index.html` dalla versione di lavoro della pagina: `python3 -I tools/build_site.py <pagina.html> . https://scottregush.github.io/off-the-ice`
- Il sito si apre in inglese; ogni visitatore può scegliere italiano, francese o tedesco dal menu della lingua e la scelta resta nel suo browser. Anteprime social e meta tag sono in inglese.
- `tools/site_fixes.css` contiene le correzioni di layout per il sito pubblico; `build_site.py` le aggiunge a ogni build, così non si perdono con gli aggiornamenti.

## Fonti

Medical Report di sport.ch, swisshockeynews.ch, tio.ch, hockeyfans.ch e nationalleague.ch. Il sito non è affiliato alla National League né ai club.

## Marchio

- `assets/brand/mark.svg`: il simbolo (punto d'ingaggio con le tacche del cerchio). Rosso `#C8102E` su ghiaccio `#F8FBFD`, oppure anello chiaro con punto rosso su blu notte `#0C1F3A`.
- Caratteri: Big Shoulders per titoli e numeri, Instrument Sans per il testo.
- `og-image.png` (anteprima per WhatsApp e social), `apple-touch-icon.png` e `icon-512.png` vengono rigenerate da `tools/make_brand.js` a ogni aggiornamento, con il numero di indisponibili del giorno.
