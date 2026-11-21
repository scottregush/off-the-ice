// Render the brand images from tools/brand.html with the pre-installed Playwright Chromium.
// Usage: node tools/make_brand.js <site-dir> [--sheet <png-path>]
// Writes <site-dir>/og-image.png (1200x630, with today's numbers from index.html),
// <site-dir>/apple-touch-icon.png (180) and <site-dir>/icon-512.png.
const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

(async () => {
  const site = path.resolve(process.argv[2] || '.');
  const sheetIdx = process.argv.indexOf('--sheet');
  const sheetOut = sheetIdx > 0 ? path.resolve(process.argv[sheetIdx + 1]) : null;
  const html = fs.readFileSync(path.join(site, 'index.html'), 'utf8');
  const m = html.match(/const D = (\{.*\});\n/);
  if (!m) throw new Error('data block not found in index.html');
  const D = JSON.parse(m[1]);
  const [y, mo, d] = D.updated.split('-');
  const q = new URLSearchParams({ total: D.inj.length, imports: D.inj.filter(x => x.nat).length, date: `${d}.${mo}.${y}` });
  const url = 'file://' + path.join(__dirname, 'brand.html') + '?' + q;

  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1400, height: 1400 }, deviceScaleFactor: 1 });
  await page.goto(url);
  await page.evaluate(() => document.fonts.ready);
  await page.locator('#og').screenshot({ path: path.join(site, 'og-image.png') });
  await page.locator('#icon').screenshot({ path: path.join(site, 'icon-512.png') });
  const small = await browser.newPage({ viewport: { width: 600, height: 600 }, deviceScaleFactor: 180 / 512 });
  await small.goto(url);
  await small.evaluate(() => document.fonts.ready);
  await small.locator('#icon').screenshot({ path: path.join(site, 'apple-touch-icon.png') });
  if (sheetOut) {
    const big = await browser.newPage({ viewport: { width: 1400, height: 1400 }, deviceScaleFactor: 1 });
    await big.goto(url);
    await big.evaluate(() => document.fonts.ready);
    await big.locator('#sheet').screenshot({ path: sheetOut });
  }
  await browser.close();
  console.log(`brand images written · ${q.get("total")} unavailable · ${q.get("date")}`);
})();
