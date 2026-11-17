# Off the Ice

Chi manca in National League: infortuni, squalifiche e stranieri in tribuna delle 14 squadre, con rientro previsto, ultime 5 partite e le rose personali per il fantahockey.

Sito: https://scottregush.github.io/off-the-ice/

## Come funziona

- `index.html` è l'intera pagina: dati, stile e codice in un solo file, senza server.
- Le rose dei visitatori restano nel loro browser (localStorage).
- I dati vengono ricontrollati automaticamente due volte al giorno (mattino e dopo le partite serali) e il file viene aggiornato solo quando le fonti cambiano.
- `tools/build_site.py` genera `index.html` dalla versione di lavoro della pagina: `python3 -I tools/build_site.py <pagina.html> . https://scottregush.github.io/off-the-ice`

## Fonti

Medical Report di sport.ch, swisshockeynews.ch, tio.ch, hockeyfans.ch e nationalleague.ch. Il sito non è affiliato alla National League né ai club.
