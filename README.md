# Off the Ice

Chi manca in National League: infortuni, squalifiche e stranieri in tribuna delle 14 squadre, con rientro previsto, ultime 5 partite e le rose personali per il fantahockey.

Sito: https://scottregush.github.io/off-the-ice/

## Come funziona

- `index.html` è l'intera pagina: dati, stile e codice in un solo file, senza server.
- Le rose dei visitatori restano nel loro browser (localStorage) e, se accedono, anche nel loro account (vedi sotto).
- I dati vengono ricontrollati automaticamente due volte al giorno (mattino e dopo le partite serali) e il file viene aggiornato solo quando le fonti cambiano.
- `tools/build_site.py` genera `index.html` dalla versione di lavoro della pagina: `python3 -I tools/build_site.py <pagina.html> . https://scottregush.github.io/off-the-ice`
- Il sito si apre in inglese; ogni visitatore può scegliere italiano, francese o tedesco dal menu della lingua e la scelta resta nel suo browser. Anteprime social e meta tag sono in inglese.
- `tools/site_sync.js` contiene la sincronizzazione delle rose con l'account; `build_site.py` la inserisce a ogni build.
- `tools/site_fixes.css` e `tools/site_fixes.js` contengono le correzioni di layout e accessibilità per il sito pubblico; `build_site.py` le aggiunge a ogni build (insieme ad alcune piccole modifiche al codice della pagina), così non si perdono con gli aggiornamenti.

## Account e rose su più dispositivi (Supabase)

L'accesso è facoltativo, solo con Google, e serve solo a ritrovare le rose su tutti i dispositivi. Account e rose stanno nel progetto Supabase `eftowfvehagppbeujemr` (server in Europa). È attivo solo sul sito pubblico, non nella versione dentro Claude.

### Preparare il database

Da fare una volta sola, o di nuovo se il progetto viene ricreato:

1. Su supabase.com apri il progetto, poi **SQL Editor → New query**.
2. Incolla tutto il contenuto di `tools/supabase.sql` e premi **Run**. Si può rieseguire senza rischi.

Lo script crea:

- la tabella `rosters`, con una riga per utente che contiene tutte le sue rose;
- le regole di accesso: ogni utente legge e scrive solo la propria riga, chi non ha fatto l'accesso non vede niente;
- la funzione `delete_my_account`, usata da «Elimina account» nella pagina delle rose, che cancella le rose e l'account.

### Impostazioni dell'accesso

In **Authentication** su Supabase:

- **Sign In / Providers**: il sito usa solo *Google*. L'accesso con link via email è stato tolto dal sito perché il servizio email predefinito di Supabase manda al massimo 2 email all'ora e solo agli indirizzi del team del progetto; per riattivarlo servirebbe un servizio di invio proprio (*Authentication → Emails → SMTP Settings*). `build_site.py` toglie il modulo email a ogni build (sezione 2g). Per Google servono Client ID e Client Secret di un client OAuth creato in Google Cloud Console, con questo URI di reindirizzamento autorizzato: `https://eftowfvehagppbeujemr.supabase.co/auth/v1/callback`.
- **URL Configuration**: in *Redirect URLs* deve esserci `https://scottregush.github.io/off-the-ice/`, l'indirizzo a cui il sito chiede di tornare dopo l'accesso. Se manca, dopo il login si finisce sul *Site URL*.

La chiave scritta nella pagina (`sb_publishable_…`) è quella pubblica ed è fatta per stare nel browser: i dati sono protetti dalle regole di accesso, non dalla chiave. La chiave segreta non va mai messa nel sito né nel repository.

### Come funziona la sincronizzazione

- Al primo accesso su un dispositivo, le rose dell'account e quelle già presenti sul dispositivo vengono unite.
- Dopo, ogni modifica viene salvata nell'account; quando si riapre il sito o si torna sulla scheda, il dispositivo prende la versione dell'account.
- Se un salvataggio non riesce (rete assente, Supabase non raggiungibile), la modifica resta segnata sul dispositivo e viene ritentata ogni 30 secondi; finché non arriva, quel dispositivo ha la precedenza. Accanto alle rose compare «account non raggiungibile».
- Un dispositivo con la rosa vuota non sovrascrive mai le rose dell'account.

### Controllare che il database risponda

```bash
curl -s "https://eftowfvehagppbeujemr.supabase.co/rest/v1/rosters?select=data" -H "apikey: <chiave pubblica della pagina>"
```

- `permission denied for table rosters`: tutto a posto (senza accesso non si legge niente).
- `Could not find the table 'public.rosters'`: la tabella manca; l'accesso funziona ma le rose non vengono salvate. Riesegui `tools/supabase.sql`.

Per provare l'accesso su un indirizzo diverso dal sito pubblico, apri la console del browser ed esegui `localStorage.setItem('oti-sb-test', '1')`, poi ricarica; quell'indirizzo va aggiunto anche alle *Redirect URLs* di Supabase.

## Fonti

Medical Report di sport.ch, swisshockeynews.ch, tio.ch, hockeyfans.ch e nationalleague.ch. Il sito non è affiliato alla National League né ai club.

## Marchio

- `assets/brand/mark.svg`: il simbolo (punto d'ingaggio con le tacche del cerchio). Rosso `#C8102E` su ghiaccio `#F8FBFD`, oppure anello chiaro con punto rosso su blu notte `#0C1F3A`.
- Caratteri: Big Shoulders per titoli e numeri, Instrument Sans per il testo.
- `og-image.png` (anteprima per WhatsApp e social), `apple-touch-icon.png` e `icon-512.png` vengono rigenerate da `tools/make_brand.js` a ogni aggiornamento, con il numero di indisponibili del giorno.
