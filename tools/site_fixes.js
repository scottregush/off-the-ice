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

  /* Rosters "⋯" menu (Rename, Transfer rosters): a disclosure button with a short list of actions.
     Enter/Space or click opens it and focuses the first action; arrow keys move; Escape or a click
     elsewhere closes it. Choosing an action runs the page's own handler and closes the menu. */
  const rmore = () => document.querySelector('.rmore');
  const setMenu = (open, focus) => {
    const box = rmore(); if (!box) return;
    const b = box.querySelector('.rmore-b'), m = box.querySelector('.rmore-m');
    m.hidden = !open; b.setAttribute('aria-expanded', String(open));
    if (open){ m.classList.remove('end'); if (m.getBoundingClientRect().right > document.documentElement.clientWidth - 8) m.classList.add('end'); }
    if (open && focus) m.querySelector('button').focus();
    if (!open && focus) b.focus();
  };
  document.addEventListener('click', e => {
    const box = rmore(); if (!box) return;
    if (e.target.closest('.rmore-b')){ setMenu(box.querySelector('.rmore-m').hidden, e.detail === 0); return; }
    if (e.target.closest('.rmore-m button')){ setTimeout(() => setMenu(false, false), 0); return; }
    if (!e.target.closest('.rmore')) setMenu(false, false);
  });
  document.addEventListener('keydown', e => {
    const box = rmore(); if (!box || !box.contains(document.activeElement)) return;
    const m = box.querySelector('.rmore-m');
    if (e.key === 'Escape' && !m.hidden){ e.preventDefault(); e.stopPropagation(); setMenu(false, true); return; }
    if (m.hidden || !['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(e.key)) return;
    const items = [...m.querySelectorAll('button')], i = items.indexOf(document.activeElement);
    const next = e.key === 'Home' ? 0 : e.key === 'End' ? items.length - 1
      : (i + (e.key === 'ArrowDown' ? 1 : -1) + items.length) % items.length;
    e.preventDefault(); items[next].focus();
  });
  document.addEventListener('focusout', e => {
    const box = rmore(); if (!box || !box.contains(e.target)) return;
    setTimeout(() => { const b = rmore(); if (b && !b.contains(document.activeElement) && document.activeElement !== document.body) setMenu(false, false); }, 0);
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
