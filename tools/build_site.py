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
           '<p><b>Le mie rose.</b> Le tue rose sono salvate solo in questo browser: nessun altro può vederle '
           'e non vengono inviate a nessun server.</p>', s, count=1, flags=re.S)

# 3. Initials only: no need to keep the image markup reachable.
updated = re.search(r'"updated":"(\d{4}-\d{2}-\d{2})"', s)
updated = updated.group(1) if updated else date.today().isoformat()

title = 'Off the Ice · Infortunati e indisponibili della National League'
desc = ('Chi manca in National League: infortuni, squalifiche e stranieri in tribuna delle 14 squadre di hockey, '
        'con rientro previsto, ultime 5 partite e le tue rose per il fantahockey. Aggiornato due volte al giorno.')

head = f'''<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="robots" content="index,follow">
<meta name="google-site-verification" content="UMQqYc_pF2QXIGmAaknFINabVE4EtxecVviGykGKkk8">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:locale" content="it_CH">
{f'<link rel="canonical" href="{site_url}">' if site_url else ''}
{f'<meta property="og:url" content="{site_url}">' if site_url else ''}
<meta name="theme-color" content="#0C1F3A">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Ccircle cx='16' cy='16' r='13' fill='none' stroke='%23C8102E' stroke-width='3'/%3E%3Ccircle cx='16' cy='16' r='5' fill='%23C8102E'/%3E%3C/svg%3E">
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
print(f'built {out/"index.html"} · photos removed: {n_ph} · data date: {updated}')
