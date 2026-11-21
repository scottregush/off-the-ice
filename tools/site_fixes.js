/* Accessibility fixes for the public site, added by build_site.py after the page's own script. */
(() => {
  /* Desktop side panel (player card, non-modal): Tab past its last control, or Shift+Tab before its first,
     goes back to the element that opened it, so keyboard users continue where they were in the page. */
  let lastOutside = null;
  document.addEventListener('focusin', e => { if (!e.target.closest('dialog')) lastOutside = e.target; });
  document.addEventListener('keydown', e => {
    if (e.key !== 'Tab') return;
    const d = document.querySelector('dialog.side[open]');
    if (!d || !d.contains(document.activeElement)) return;
    const f = [...d.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select,textarea,[tabindex]:not([tabindex="-1"])')]
      .filter(x => x.getClientRects().length);
    if (!f.length) return;
    const edge = e.shiftKey ? f[0] : f[f.length - 1];
    if (document.activeElement !== edge) return;
    const back = (lastOutside && lastOutside.isConnected) ? lastOutside : document.querySelector('main .is-open');
    if (!back) return;
    e.preventDefault();
    back.focus();
  });

  /* Language switch rewrites the text of every live region at once; mute them for that moment
     so screen readers don't read out a dozen identical hints. */
  document.addEventListener('click', e => {
    if (!e.target.closest('[data-lang-set]')) return;
    const live = [...document.querySelectorAll('[aria-live="polite"]')];
    live.forEach(x => x.setAttribute('aria-live', 'off'));
    setTimeout(() => live.forEach(x => x.setAttribute('aria-live', 'polite')), 500);
  }, true);
})();
