const rosterKey = r => r.name + '|' + r.ids.join('.');
const hasRosters = l => l.some(r => r.ids.length) || l.length > 1;
let sbRetry = null;
function sbLater(){ clearTimeout(sbRetry); sbRetry = setTimeout(() => { sbRetry = null; if (sbSess) sbPull(false); }, 30000); }
/* Read the account copy and reconcile it with this device:
   - first login here: the account's rosters plus the ones made on this device;
   - changes made here that never reached the account (offline, errors): this device wins;
   - otherwise the account wins. Nothing is written when there is nothing to save. */
async function sbPull(first){
  if (!(await sbToken())) return;
  try {
    if (!sbUser) sbUser = await sbFetch('/auth/v1/user');
    const rows = await sbFetch('/rest/v1/rosters?select=data&user_id=eq.' + encodeURIComponent(sbUser.id));
    const remote = (rows && rows[0] && rows[0].data ? cleanList(rows[0].data.list) : null) || [];
    const joined = store.get('oti-sb-joined') === sbUser.id, dirty = store.get('oti-sb-dirty') === '1';
    const local = JSON.parse(listJSON());
    let list;
    if (!joined){
      const known = new Set(remote.map(rosterKey));
      list = remote.filter(r => r.ids.length || !hasRosters(local)).concat(local.filter(r => r.ids.length && !known.has(rosterKey(r)))).slice(0, MAXROSE);
      if (!list.length) list = remote.length ? remote : local;
    } else list = dirty || !remote.length ? local : remote;
    if (JSON.stringify(list) !== listJSON()){ S.list = list.map(r => ({id: r.id, name: r.name, ids: r.ids})); ensure(); saveLocal(); refresh(); }
    store.set('oti-sb-joined', sbUser.id); sbPulled = true; sbState = 'in';
    if (JSON.stringify(list) !== JSON.stringify(remote) && (remote.length || hasRosters(list))) await sbPushNow();
    else store.set('oti-sb-dirty', '');
  } catch (e){
    console.warn('Off the Ice: account sync failed', e.status, e.message);
    if (e.status === 401){ sbSess = null; sbUser = null; sbSave(); sbState = 'out'; } else { sbState = 'slow'; sbLater(); }
  }
  renderAcct();
}
async function sbPushNow(){
  clearTimeout(sbTimer); sbTimer = null;
  if (!sbUser || !(await sbToken())) return;
  try {
    await sbFetch('/rest/v1/rosters?on_conflict=user_id', {method: 'POST', headers: {Prefer: 'resolution=merge-duplicates,return=minimal'},
      body: JSON.stringify({user_id: sbUser.id, data: {v: 2, list: JSON.parse(listJSON())}, updated_at: new Date().toISOString()})});
    store.set('oti-sb-dirty', ''); sbState = 'in';
  } catch (e){ console.warn('Off the Ice: saving to the account failed', e.status, e.message); sbState = 'slow'; sbLater(); }
  renderAcct();
}
function sbPush(){
  if (!SB_ON || !sbSess) return;
  store.set('oti-sb-dirty', '1');                                /* cleared once the account has this version */
  if (!sbUser || !sbPulled){ if (!sbRetry) sbLater(); return; }
  clearTimeout(sbTimer); sbTimer = setTimeout(sbPushNow, 700);
}
