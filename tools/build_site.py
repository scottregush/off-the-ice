#!/usr/bin/env python3
"""Build the public website (index.html) from the Off the Ice artifact page.

Usage: python3 -I build_site.py <artifact-page.html> <output-dir> [site-url]

The artifact page is the source of truth; this only adapts it for the open web:
- full HTML document with lang="it", meta description, Open Graph and robots tags
- no player photos (they belong to the National League and the clubs): initials only
- no Claude-only features: rosters are saved in the visitor's browser
- robots.txt and sitemap.xml when a site URL is given
"""
import re
import sys
from pathlib import Path
from datetime import date

src, out = Path(sys.argv[1]), Path(sys.argv[2])
site_url = sys.argv[3].rstrip('/') + '/' if len(sys.argv) > 3 else ''
s = src.read_text(encoding='utf8')

# Take only the page content when the file is a saved full document (artifact read).
if '<body>' in s:
    s = s[s.index('<body>') + len('<body>'):]
    s = s[:s.rindex('</body>')] if '</body>' in s else s
s = s.strip()

# Remove the artifact-only <title> and viewport-fit meta from the body; they go into <head>.
s = re.sub(r'<title>.*?</title>\s*', '', s, count=1, flags=re.S)
s = re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>\s*', '', s, count=1)

# 1. No photos: every player falls back to initials.
n_ph = s.count('"ph":true')
s = s.replace('"ph":true', '"ph":false')

# 2. Footer copy that only applies inside Claude.
s = re.sub(r'<p><b>Foto e statistiche\.</b>.*?</p>',
           '<p><b>Statistiche.</b> Statistiche stagionali da <a href="https://www.nationalleague.ch" target="_blank" rel="noopener">nationalleague.ch</a>. '
           'Questo sito non è affiliato alla National League né ai club.</p>', s, count=1, flags=re.S)
s = re.sub(r'<p><b>Le mie rose\.</b>.*?</p>',
           '<p><b>Le mie rose.</b> '+"Le tue rose sono salvate in questo browser. Se accedi con la tua email, vengono salvate anche nel tuo account, così le ritrovi sugli altri dispositivi. L'accesso è facoltativo e l'email serve solo a questo: non viene usata per altro né condivisa. I dati sono conservati presso Supabase, su server in Europa, e puoi eliminare account e dati in qualsiasi momento con «Elimina account» nella pagina delle rose."+' <a href="privacy.html">Privacy</a></p>', s, count=1, flags=re.S)

# 2b. English by default. Visitors pick another language (IT/FR/DE/EN) from the menu, and the choice is kept
#     in their browser; the browser's own language no longer decides.
s = re.sub(r"if \(!start\)\{\n  for \(const n of \(navigator\.languages[^\n]*\n\}\n", '', s, count=1)
s = s.replace("apply(start || 'it');", "apply(start || 'en');")
if "apply(start || 'en');" not in s:
    print('warning: language start code not found; the default language was not set to English')
# The browser-tab title follows the chosen language (the page's own translation left it in Italian).
TITLES_JS = ('document.title = ({it:"Off the Ice · Infortunati e indisponibili della National League", '
             'fr:"Off the Ice · Blessés et absents de la National League", '
             'de:"Off the Ice · Verletzte und Ausfälle der National League", '
             'en:"Off the Ice · Who\'s missing in the National League"})[l] || tr(titleIT);')
s = s.replace('document.title = tr(titleIT);', TITLES_JS)
if TITLES_JS not in s:
    print('warning: title code not found; the browser-tab title is not translated')

# 2c. Screen readers: player buttons are named by their visible text (name, team, status, return date)
#     instead of a label that only says "Open the card of <name>".
s = re.sub(r' aria-label="Apri la scheda di \$\{esc\([^)]*\)\}"', '', s)
# Team bars: the label lists the breakdown by category, which the bars show only by colour.
# (Parentheses, not ' · ': the page's translator splits text at ' · ' before its rules run.)
BAR_OLD = 'aria-label="${esc(t.name)}: ${list.length} indisponibili. Apri la scheda."'
BAR_NEW = ('aria-label="${esc(t.name)}: ${list.length} indisponibili (${order.map(c => [CAT[c].l, list.filter(x => x.cat === c).length])'
           '.filter(z => z[1]).map(z => z[0] + \' \' + z[1]).join(\', \')}). Apri la scheda."')
BAR_TR_OLD = r"  [/^(.+): (\d+) indisponibili\. Apri la scheda\.$/,"
BAR_TR_NEW = (r"  [/^(.+): (\d+) indisponibili \((.+)\)\. Apri la scheda\.$/, m => m[1] + ': ' + m[2] + ' ' + P(['absents', 'Ausfälle', 'unavailable']) + ' (' + "
              r"m[3].split(', ').map(z => { const q = z.match(/^(.+) (\d+)$/); return q ? tr(q[1]) + ' ' + q[2] : z; }).join(', ') + '). ' + P(['Ouvrir la fiche.', 'Profil öffnen.', 'Open the card.'])],"
              '\n')
if BAR_OLD in s and BAR_TR_OLD in s:
    s = s.replace(BAR_OLD, BAR_NEW).replace(BAR_TR_OLD, BAR_TR_NEW + BAR_TR_OLD, 1)
elif BAR_NEW not in s:
    print('warning: team bar label code not found; the bar breakdown is not announced')

# 2e. Patterns common to sports and fantasy injury lists:
#     a) overview lists show the status as a text chip next to the name, not only as a coloured dot;
FEED_OLD = '<span class="nm">${esc(x.n)}</span>${tcode(T[x.t])}</span><span class="txt">${txt}</span>'
FEED_NEW = '<span class="nm">${esc(x.n)}</span>${tcode(T[x.t])}<span class="pill cat-${x.cat}">${CAT[x.cat].l}</span></span><span class="txt">${txt}</span>'
if FEED_OLD in s:
    s = s.replace(FEED_OLD, FEED_NEW)
elif FEED_NEW not in s:
    print('warning: overview list template not found; status chips not added')
#     b) the "Missed" explanation sits with the list it explains, so on phones the first player shows sooner;
m = re.search(r'\s*<p class="lead">(«Saltate».*?)</p>', s, flags=re.S)
if m and '<p class="count" id="inj-count" aria-live="polite"></p>' in s:
    s = s[:m.start()] + s[m.end():]
    s = s.replace('<p class="count" id="inj-count" aria-live="polite"></p>',
                  '<p class="count" id="inj-count" aria-live="polite"></p>\n      <p class="count-note">' + m.group(1) + '</p>', 1)
#     c) rosters: the add-player search comes first, the explanation after it.
m = re.search(r'\s*<p class="lead">(Crea una o più rose.*?)</p>', s, flags=re.S)
if m and '<p id="r-msg" class="r-msg" aria-live="polite"></p>' in s and s.index('<p id="r-msg"') > m.start():
    s = s[:m.start()] + s[m.end():]
    s = s.replace('<p id="r-msg" class="r-msg" aria-live="polite"></p>',
                  '<p id="r-msg" class="r-msg" aria-live="polite"></p>\n      <p class="lead">' + m.group(1) + '</p>', 1)

#     d) rosters: Rename and Transfer are secondary actions, so they sit in a "⋯" menu next to the title
#        (behaviour in tools/site_fixes.js; the existing [data-rename] / [data-xfer] handlers stay as they are).
RMORE_OLD = '<button class="btn ghost" data-rename>Rinomina</button><button class="btn ghost" data-xfer aria-expanded="${xferOpen}">Trasferisci rose</button>'
RMORE_NEW = ('<div class="rmore"><button class="btn ghost rmore-b" type="button" aria-expanded="false" aria-controls="r-more" '
             'aria-label="Altre azioni" title="Altre azioni"><svg viewBox="0 0 20 20" aria-hidden="true" focusable="false">'
             '<circle cx="4.5" cy="10" r="1.6"/><circle cx="10" cy="10" r="1.6"/><circle cx="15.5" cy="10" r="1.6"/></svg></button>'
             '<div class="rmore-m" id="r-more" hidden><button type="button" data-rename>Rinomina</button>'
             '<button type="button" data-xfer>Trasferisci rose</button></div></div>')
if RMORE_OLD in s:
    s = s.replace(RMORE_OLD, RMORE_NEW)
elif RMORE_NEW not in s:
    print('warning: roster title buttons not found; the actions menu was not added')
I18N_KEY = '"Le mie rose":["Mes effectifs","Meine Kader","My rosters"]'
I18N_ADD = '"Altre azioni":["Autres actions","Weitere Aktionen","More actions"],'
if I18N_ADD not in s and I18N_KEY in s:
    s = s.replace(I18N_KEY, I18N_ADD + I18N_KEY, 1)

# 2d. Layout and accessibility fixes for the open web (tools/site_fixes.css and .js), after the page's own.
here = Path(__file__).resolve().parent

# 2f. Account sync (rosters across devices): the reconcile/save code from tools/site_sync.js replaces the page's own,
#     so changes that fail to reach the account are kept and retried, and an empty device never overwrites the account.
SYNC_RE = re.compile(r"const rosterKey = r => .*?\nfunction sbPush\(\)\{.*?\n(?=async function sbSendLink)", re.S)
if (here / 'site_sync.js').exists():
    sync_js = (here / 'site_sync.js').read_text(encoding='utf8').strip() + '\n'
    if SYNC_RE.search(s):
        s = SYNC_RE.sub(lambda m: sync_js, s, count=1)
    else:
        print('warning: account sync code not found; tools/site_sync.js was not applied')
s = re.sub(r'\s*<style id="site-fixes">.*?</style>', '', s, flags=re.S)
s = re.sub(r'\s*<script id="site-fixes-js">.*?</script>', '', s, flags=re.S)
if (here / 'site_fixes.css').exists():
    s += '\n<style id="site-fixes">\n' + (here / 'site_fixes.css').read_text(encoding='utf8').strip() + '\n</style>'
if (here / 'site_fixes.js').exists():
    s += '\n<script id="site-fixes-js">\n' + (here / 'site_fixes.js').read_text(encoding='utf8').strip() + '\n</script>'

# 3. Initials only: no need to keep the image markup reachable.
updated = re.search(r'"updated":"(\d{4}-\d{2}-\d{2})"', s)
updated = updated.group(1) if updated else date.today().isoformat()

y_, m_, d_ = updated.split('-')
updated_it = f'{d_}.{m_}.{y_}'
# English by default: search and share previews read these tags without running the page.
# The page then sets the tab title to the visitor's chosen language (see TITLES_JS above).
title_en = "Off the Ice · Who's missing in the National League"
desc = ("Who's missing in the National League: injuries, suspensions and scratched imports for all 14 teams, "
        'with expected return, last 5 games and your own fantasy hockey rosters. Updated twice a day.')

head = f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title_en}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow">
<meta name="google-site-verification" content="UMQqYc_pF2QXIGmAaknFINabVE4EtxecVviGykGKkk8">
<meta property="og:type" content="website">
<meta property="og:title" content="{title_en}">
<meta property="og:description" content="{desc}">
<meta property="og:locale" content="en_GB">
<meta property="og:locale:alternate" content="it_CH">
<meta property="og:locale:alternate" content="fr_CH">
<meta property="og:locale:alternate" content="de_CH">
{f'<link rel="canonical" href="{site_url}">' if site_url else ''}
{f'<meta property="og:url" content="{site_url}">' if site_url else ''}
<meta name="theme-color" content="#0C1F3A">
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<link rel="apple-touch-icon" href="apple-touch-icon.png">
{f'<meta property="og:image" content="{site_url}og-image.png?v={updated}">' if site_url else ''}
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="Off the Ice: unavailable players in the National League, updated {updated_it}">
<meta property="og:site_name" content="Off the Ice">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_en}">
<meta name="twitter:description" content="{desc}">
{f'<meta name="twitter:image" content="{site_url}og-image.png?v={updated}">' if site_url else ''}
<style>:root{{color-scheme:light;box-sizing:border-box;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}html{{scroll-padding-top:env(safe-area-inset-top,0px)}}body{{margin:0;padding:0}}img{{max-width:100%}}[hidden]:not([hidden=until-found i]){{display:none!important}}</style>
</head>
<body>
'''
out.mkdir(parents=True, exist_ok=True)
(out / 'index.html').write_text(head + s + '\n</body>\n</html>\n', encoding='utf8')
(out / '.nojekyll').write_text('', encoding='utf8')
if site_url:
    (out / 'robots.txt').write_text(f'User-agent: *\nAllow: /\nSitemap: {site_url}sitemap.xml\n', encoding='utf8')
    (out / 'sitemap.xml').write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f'  <url><loc>{site_url}</loc><lastmod>{updated}</lastmod><changefreq>daily</changefreq></url>\n</urlset>\n',
        encoding='utf8')
mark = Path(__file__).resolve().parent.parent / 'assets' / 'brand' / 'mark.svg'
if mark.exists() and mark.resolve() != (out / 'favicon.svg').resolve():
    (out / 'favicon.svg').write_text(mark.read_text(encoding='utf8'), encoding='utf8')
import subprocess, shutil
maker = Path(__file__).resolve().parent / 'make_brand.js'
if shutil.which('node') and maker.exists():
    r = subprocess.run(['node', str(maker), str(out)], capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip()[:400])
print(f'built {out/"index.html"} · photos removed: {n_ph} · data date: {updated}')
