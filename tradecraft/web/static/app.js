/* Tradecraft front end. The approved mock-up's behaviour, with its hard-coded data
   replaced by the engine's JSON API. No build step, no framework. */
(function () {
  'use strict';
  var root = document.documentElement;
  function $(q) { return document.querySelector(q); }
  function h(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }

  // ---- theme (Ledger / Night Desk), as in the mock-up --------------------------------
  var modeBtn = $('#mode');
  function isDark() { var t = root.getAttribute('data-theme'); return t ? t === 'dark' : window.matchMedia('(prefers-color-scheme: dark)').matches; }
  function lab() { modeBtn.textContent = isDark() ? 'Light' : 'Dark'; }
  modeBtn.addEventListener('click', function () { root.setAttribute('data-theme', isDark() ? 'light' : 'dark'); lab(); }); lab();

  // ---- state --------------------------------------------------------------------------
  var STAGES = [['s1', 'Liquidity gate', 'Option chain screen'], ['s2', 'Thesis', 'Directional view'], ['s3', 'Contracts', 'Strategy selection'], ['s4', 'Challenge', 'Risk review']];
  var PAUSE_STAGE = {gate: 0, thesis: 1, stage2_stopped: 1, contracts: 2, challenge: 3, stage4_stopped: 3};
  var BUILT = {s1: true, s2: true, s3: true, s4: true};
  var st = {home: null, view: null, review: null, busy: false, sub: null, own: null, s2rows: null, ended: false};
  var SYMS = [], DAILY = {};

  // ---- API ----------------------------------------------------------------------------
  function api(path, body) {
    var opt = body === undefined ? {} : {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)};
    return fetch(path, opt).then(function (r) {
      return r.json().catch(function () { return null; }).then(function (j) {
        if (!r.ok) { var d = j && j.detail; var e = new Error(typeof d === 'string' ? d : (d && d.message) || 'The request failed.'); e.status = r.status; e.detail = d; throw e; }
        return j;
      });
    });
  }
  function busy(on) { st.busy = on; document.body.setAttribute('aria-busy', on ? 'true' : 'false'); document.querySelectorAll('button').forEach(function (b) { if (on) { b.dataset.was = b.disabled ? '1' : ''; b.disabled = true; } else if (b.dataset.was !== undefined) { b.disabled = b.dataset.was === '1'; delete b.dataset.was; } }); }
  function act(action, fields) {
    if (st.busy || !st.view) return Promise.resolve();
    $('#appMsg').textContent = ''; busy(true);
    return api('/api/requests/' + st.view.request_id + '/action', Object.assign({action: action}, fields || {}))
      .then(function (v) { busy(false); setView(v); })
      .catch(function (e) { busy(false); $('#appMsg').textContent = e.message; });
  }

  // ---- times, in Eastern Time as on the mock-up ----------------------------------------
  var ET = 'America/New_York';
  function hm(iso) { return new Intl.DateTimeFormat('en-GB', {timeZone: ET, hour: '2-digit', minute: '2-digit', hour12: false}).format(new Date(iso)); }
  function dayMonth(iso) { return new Intl.DateTimeFormat('en-GB', {timeZone: ET, day: 'numeric', month: 'long'}).format(new Date(iso)); }
  function etDay(iso) { return new Intl.DateTimeFormat('en-CA', {timeZone: ET}).format(iso ? new Date(iso) : new Date()); }
  function relDay(iso) {
    var d = etDay(iso), today = etDay(), y = etDay(new Date(Date.now() - 864e5).toISOString());
    return d === today ? 'Today ' + hm(iso) : d === y ? 'Yesterday' : dayMonth(iso);
  }

  // ---- screens ------------------------------------------------------------------------
  function showScreen(name) {
    document.querySelectorAll('.screen').forEach(function (e) { e.classList.toggle('on', e.getAttribute('data-s') === name); });
    window.scrollTo(0, 0);
  }
  // While agents run there is no pause: the request is in stage 2 (the only long stage built so far).
  function current() { var v = st.view; if (v && st.ended) return 4; if (!v || v.done) return -1; if (v.pause) return PAUSE_STAGE[v.pause.pause]; if (!(v.running || v.progress)) return -1; var td = v.state.thesis_decision; return td && td.action !== 'reject' ? (v.state.selection ? 3 : 2) : 1; }

  // While a stage runs in the background, ask the engine again every 1.5 seconds.
  function poll() {
    clearTimeout(st.poll);
    if (!st.view || !st.view.running) return;
    st.poll = setTimeout(function () {
      api('/api/requests/open').then(function (v) { if (st.view) setView(v); }).catch(function () { poll(); });
    }, 1500);
  }

  // Developer-only switches (config/test_failures.json): never on without this marker in the header.
  function testMark(list) { var m = $('#tfMark'), on = !!(list && list.length); m.hidden = !on; m.title = on ? 'Developer switch on: ' + list.join(', ') + ' (config/test_failures.json)' : ''; }
  // The recorded demo (tradecraft/demo.py): every page says so, with the date of its data.
  function demoMark(d) { var m = $('#demoMark'); m.hidden = !d; if (d) { m.textContent = 'RECORDED DEMO · DATA OF ' + dayMonth(d.as_of).toUpperCase(); m.title = 'Saved model outputs and a bundled option snapshot. Not live data. Symbols: ' + d.symbols.join(', '); } }
  function setView(v) {
    if (v) { testMark(v.test_failures); demoMark(v.demo); }
    // After "Proceed to decision" the request has ended; its four stages stay reviewable until the user goes home.
    st.ended = !!(v && v.done && v.state && v.state.status === 'proceeded_to_decision');
    // A new request starts on its own first screen: "Take a view yourself" opened in an earlier request does not carry over.
    if (v && (!st.view || st.view.request_id !== v.request_id)) { st.sub = null; st.own = null; }
    st.view = v && (!v.done || st.ended) ? v : null; st.review = null;
    hideLeave();
    if (!st.view) { loadHome(); return; }
    render();
  }

  function render() {
    var v = st.view;
    if (!v) { $('#reqbar').hidden = true; $('#navHome').setAttribute('aria-current', 'page'); renderHome(); showScreen('home'); return; }
    $('#navHome').removeAttribute('aria-current');
    $('#reqbar').hidden = false;
    $('#reqT').textContent = v.symbol;
    var g = v.state.gate || {}, mk = g.market || (st.home && st.home.market) || {};
    var snap = st.home && st.home.snapshot;
    $('#reqSub').textContent = 'Request opened ' + hm(v.opened_at) + ' · ' + (mk.open
      ? 'market open · ' + (g.source === 'snapshot' ? 'live quotes unavailable, on the snapshot' : g.provider === 'Tradier' ? 'quotes from Tradier, real-time' : 'quotes delayed 15 minutes')
      : 'market closed' + (snap ? ' · snapshot of ' + dayMonth(snap.taken_et) : ''));
    renderStages();
    var cur = current(), shown = st.review != null ? st.review : cur, name = shown > 3 ? 'end' : STAGES[shown][0];
    var screen = name;
    if (name === 's1') renderGate(st.review != null);
    if (name === 's2') {
      var working = st.review == null && (v.running || !v.pause || v.pause.pause === 'stage2_stopped');
      if (working) { screen = 's2w'; renderWorking(); }
      else if (st.review == null && st.sub === 'own' && v.state.thesis && v.state.thesis.no_view) { screen = 's2u'; renderBrief(false); renderOwn(); }
      else { st.sub = null; renderBrief(st.review != null); }
    }
    if (name === 's3') renderContracts(st.review != null);
    if (name === 's4') {
      var working4 = st.review == null && (v.running || !v.pause || v.pause.pause === 'stage4_stopped');
      if (working4) { screen = 's2w'; renderWorking(); } else renderChallenge(st.review != null);
    }
    poll();
    if (v.pause && v.pause.error) $('#appMsg').textContent = v.pause.error;
    showScreen(screen);
  }

  function renderStages() {
    var host = $('#stages'), cur = current(); host.textContent = '';
    STAGES.forEach(function (S, i) {
      var b = h('button', 'stg'); b.type = 'button';
      var done = i < cur, isCur = i === cur, sub = done ? 'Complete' : isCur ? 'In progress' : 'Not reached';
      var td = st.view.state.thesis_decision;
      if (done && i === 1 && td && td.at) sub = 'Frozen ' + hm(new Date(td.at * 1000).toISOString());
      if (done) b.classList.add('done'); if (isCur) b.classList.add('cur');
      if (st.review === i || (st.review == null && isCur)) b.classList.add('view');
      b.disabled = !(done || isCur) || !BUILT[S[0]];
      b.appendChild(h('span', 'n', done ? '✓' : String(i + 1)));
      var t = h('span', 't'); t.appendChild(h('b', '', S[1])); t.appendChild(h('i', '', done ? sub : S[2])); b.appendChild(t);
      b.setAttribute('aria-label', 'Stage ' + (i + 1) + ', ' + S[1] + ', ' + sub.toLowerCase());
      b.addEventListener('click', function () { st.review = i === cur ? null : i; $('#appMsg').textContent = ''; render(); });
      host.appendChild(b);
    });
  }

  // ---- home ---------------------------------------------------------------------------
  function loadHome() {
    return api('/api/home').then(function (hm_) {
      testMark(hm_.test_failures); demoMark(hm_.demo);
      st.home = hm_;
      st.ended = false;
      if (hm_.open && !hm_.open.done) { st.view = hm_.open; }     // a reload or a second tab shows the open request
      render();
    }).catch(function (e) { $('#appMsg').textContent = e.message; showScreen('home'); });
  }
  var DIR = {bullish: ['BULLISH', 'bull'], bearish: ['BEARISH', 'bear'], range_bound: ['RANGE-BOUND', 'rngb'], no_view: ['NO VIEW', 'nov']};
  var ENDED = {proceeded_to_decision: 'proceeded to decision', rejected_thesis: 'thesis rejected', stopped_at_contracts: 'stopped at contracts',
    left_at_contracts: 'stopped at contracts', stopped_at_challenge: 'stopped at risk review', left_at_challenge: 'stopped at risk review',
    stopped_stage_4_failure: 'stopped at risk review', left_at_stage4_stopped: 'stopped at risk review', left_at_thesis: 'stopped at thesis',
    stopped_while_running: 'stopped', interrupted: 'interrupted', open: 'in progress'};
  function renderHome() {
    var hm_ = st.home; if (!hm_) return;
    var c = $('#chips'); c.textContent = '';
    c.appendChild(h('span', hm_.market.open ? 'chip ok' : 'chip', hm_.market.open ? 'MARKET OPEN' : 'MARKET CLOSED'));
    c.appendChild(h('span', 'chip', 'QUOTES DELAYED 15 MIN'));
    if (hm_.snapshot) {
      var s = hm_.snapshot.taken_et, today = etDay(s) === etDay();
      c.appendChild(h('span', 'chip', 'SNAPSHOT ' + hm(s) + ' ET ' + (today ? 'TODAY' : dayMonth(s).toUpperCase())));
    }
    var r = $('#recent'); r.textContent = '';
    if (!hm_.recent.length) { r.appendChild(h('p', 'sub', 'No analyses yet. Search for a symbol above to run your first one.')); return; }
    hm_.recent.forEach(function (x, i) {
      var row = h('div', 'row item'); if (!i) row.style.cssText = 'border-top:0;margin-top:0;padding-top:0';
      row.appendChild(h('b', '', x.symbol));
      var d = DIR[x.view] || DIR.no_view, chip = h('span', 'chip dir ' + d[1], d[0]); chip.style.flex = '0 0 auto'; row.appendChild(chip);
      var where = ENDED[x.status] || x.status.replace(/_/g, ' ');
      row.appendChild(h('span', '', (x.strategy ? x.strategy + ' · ' : '') + where.charAt(0).toUpperCase() + where.slice(1)));
      row.appendChild(h('span', 'sub', relDay(x.ended_at || x.opened_at)));
      r.appendChild(row);
    });
  }

  // ---- symbol search: the rule of product-shell section 5, on the local list -------------
  var chosen = null, actI = -1, cur = [];
  function matches(q) {
    q = (q || '').trim().toLowerCase(); if (!q) return [];
    var a = [], b = [], c = [];
    for (var i = 0; i < SYMS.length; i++) {
      var x = SYMS[i], sy = x[0].toLowerCase(), nm = x[1].toLowerCase();
      if (sy.indexOf(q) === 0) a.push(x); else if (nm.indexOf(q) === 0 || nm.indexOf(' ' + q) > -1) b.push(x); else if (sy.indexOf(q) > -1 || nm.indexOf(q) > -1) c.push(x);
    }
    // within the first group: daily-list names, then an exact match, then shorter, then alphabetical
    function key(x) { return (DAILY[x[0]] ? '0' : '1') + (x[0].toLowerCase() === q ? '0' : '1') + String.fromCharCode(48 + x[0].length) + x[0]; }
    a.sort(function (x, y) { var kx = key(x), ky = key(y); return kx < ky ? -1 : kx > ky ? 1 : 0; });
    return a.concat(b, c).slice(0, 8);
  }
  function hl(el, text, q) { var i = text.toLowerCase().indexOf(q.toLowerCase()); if (i < 0) { el.textContent = text; return; } el.appendChild(document.createTextNode(text.slice(0, i))); el.appendChild(h('mark', '', text.slice(i, i + q.length))); el.appendChild(document.createTextNode(text.slice(i + q.length))); }
  function closeSugg() { $('#sugg').hidden = true; $('#tk').setAttribute('aria-expanded', 'false'); $('#tk').removeAttribute('aria-activedescendant'); actI = -1; }
  function setAct(i) { actI = i; [].forEach.call($('#sugg').children, function (li, k) { li.setAttribute('aria-selected', k === i ? 'true' : 'false'); if (k === i) { $('#tk').setAttribute('aria-activedescendant', li.id); li.scrollIntoView({block: 'nearest'}); } }); }
  function choose(x) { chosen = x; $('#tk').value = x[0] + '  ' + x[1]; closeSugg(); $('#askMsg').textContent = ''; }
  function renderSugg() {
    var q = $('#tk').value.trim(), u = $('#sugg'); u.textContent = ''; chosen = null; $('#askMsg').textContent = '';
    if (!q) { closeSugg(); return; }
    cur = matches(q);
    if (!cur.length) { u.appendChild(h('li', 'none', 'No listed symbol matches "' + q + '"')); }
    cur.forEach(function (x, i) { var li = h('li'); li.id = 'sg' + i; li.setAttribute('role', 'option'); var a = h('span', 'sy'), b = h('span', 'nm2'); hl(a, x[0], q); hl(b, x[1], q); li.appendChild(a); li.appendChild(b); li.appendChild(h('span', 'ty', x[2])); li.addEventListener('mousedown', function (e) { e.preventDefault(); choose(x); }); u.appendChild(li); });
    u.hidden = false; $('#tk').setAttribute('aria-expanded', 'true'); setAct(cur.length ? 0 : -1);
  }
  $('#tk').addEventListener('input', renderSugg);
  $('#tk').addEventListener('focus', function () { if ($('#tk').value.trim() && !chosen) renderSugg(); });
  $('#tk').addEventListener('blur', closeSugg);
  $('#tk').addEventListener('keydown', function (e) {
    var open = !$('#sugg').hidden;
    if (e.key === 'ArrowDown' && open && cur.length) { e.preventDefault(); setAct((actI + 1) % cur.length); }
    else if (e.key === 'ArrowUp' && open && cur.length) { e.preventDefault(); setAct((actI - 1 + cur.length) % cur.length); }
    else if (e.key === 'Enter' && open && cur[actI]) { e.preventDefault(); choose(cur[actI]); }
    else if (e.key === 'Escape' && open) { e.preventDefault(); closeSugg(); }
  });
  $('#ask').addEventListener('submit', function (e) {
    e.preventDefault(); if (st.busy) return;
    var pick = chosen || matches($('#tk').value)[0];
    if (!pick) { $('#askMsg').textContent = $('#tk').value.trim() ? 'No listed symbol matches. Choose one from the list.' : 'Type a symbol or a company name.'; $('#tk').focus(); return; }
    closeSugg(); $('#askMsg').textContent = ''; busy(true);
    api('/api/requests', {symbol: pick[0]}).then(function (v) { busy(false); $('#tk').value = ''; chosen = null; setView(v); })
      .catch(function (err) { busy(false); if (err.status === 409) { loadHome(); } else { $('#askMsg').textContent = err.status === 404 ? 'No listed symbol matches' : err.message; } });
  });

  // ---- stage 1: the liquidity gate ------------------------------------------------------
  var OI = [10, 25, 50, 100, 250, 500, 1000];
  var DEF = {max_spread_pct: 5, min_open_interest: 100, dte_min: 42, dte_max: 90, max_strike_distance_pct: 10, min_premium: 0.2};
  function fmt(s) { return {gap: s.max_spread_pct + '%', oi: Number(s.min_open_interest).toLocaleString('en-US'), dte: s.dte_min + ' to ' + s.dte_max, k: s.max_strike_distance_pct + '%', px: '$' + Number(s.min_premium).toFixed(2)}; }
  function num(n) { return Number(n).toLocaleString('en-US'); }
  var REASONS = [['spread', 'Spread too wide'], ['open_interest', 'Open interest below minimum'], ['dte', 'Outside DTE range'], ['strike', 'Strike too far from spot'], ['premium', 'Premium below minimum'], ['invalid_quote', 'Invalid quote']];

  function renderGate(reviewing) {
    var v = st.view, g = v.state.gate, acts = reviewing ? [] : (v.pause.actions || []);
    document.querySelectorAll('[data-s="s1"] [data-review]').forEach(function (e) { e.classList.toggle('on', reviewing); });
    $('#ctl').hidden = true; $('#ovr').hidden = true; $('#ovrMsg').textContent = '';
    var checked = g.status !== 'not_checked';
    var chip = $('#gChip'), line2 = $('#gLine2');
    $('#gProv').hidden = !(checked && g.provisional);
    if (!checked) {
      chip.textContent = 'NOT CHECKED'; chip.className = 'chip un';
      $('#gSrc').textContent = '';
      if (g.reason === 'not_in_snapshot') {
        $('#gHead').textContent = 'Liquidity cannot be judged until the market opens.';
        line2.textContent = v.symbol + ' is not in the daily snapshot. You may continue to the thesis; contracts cannot be chosen until a live screen has passed.';
      } else {
        $('#gHead').textContent = 'Liquidity could not be checked.';
        line2.textContent = 'The option chain could not be retrieved from the live feed or the daily snapshot. You may continue to the thesis; contracts cannot be chosen until a live screen has passed.';
      }
      line2.hidden = false;
    } else {
      var ok = g.status === 'pass';
      chip.textContent = ok ? 'PASS' : 'FAIL'; chip.className = 'chip ' + (ok ? 'ok' : 'fl');
      $('#gHead').textContent = num(g.passing) + (g.passing === 1 ? ' contract passes' : ' contracts pass') + ' the liquidity screen';
      if (g.source === 'live') { $('#gSrc').textContent = 'Live option chain, ' + hm(g.as_of) + ' ET, ' + srcName(g); line2.textContent = srcNote(g).trim(); line2.hidden = !srcNote(g); }
      else {
        $('#gSrc').textContent = 'Snapshot of ' + dayMonth(g.as_of) + ', ' + hm(g.as_of) + ' ET · ' + (g.market && g.market.open ? 'live quotes unavailable' : 'market closed');
        line2.textContent = 'Provisional: based on the latest snapshot. The screen is re-run on live quotes when the market opens.'; line2.hidden = false;
      }
    }
    // style.display, not the hidden attribute: the mock-up's .grid2 rule sets display and would win
    ['liqGrid', 'outPanel'].forEach(function (id) { $('#' + id).style.display = checked ? '' : 'none'; });

    var s = checked ? g.settings : Object.assign({}, DEF, v.state.gate_settings || {}), f = fmt(s), d = fmt(DEF), ch = 0;
    [['vGap', 'gap'], ['vOi', 'oi'], ['vDte', 'dte'], ['vK', 'k'], ['vPx', 'px']].forEach(function (p) { var b = $('#' + p[0]); b.textContent = f[p[1]]; var c = f[p[1]] !== d[p[1]]; b.style.color = c ? 'var(--accent)' : ''; if (c) ch++; });
    var sc = $('#sChip'); sc.textContent = ch ? ch + ' CHANGED FROM DEFAULT' : 'ALL AT DEFAULT'; sc.className = 'chip' + (ch ? ' ac' : '');
    st.settings = s;

    if (checked) {
      var bars = $('#bars'); bars.textContent = '';
      var max = Math.max.apply(null, g.buckets.map(function (b) { return b.passing_other_four; }).concat([1]));
      g.buckets.forEach(function (b) {
        var row = h('div'); row.appendChild(h('span', '', b.from + ' to ' + b.to + ' DTE'));
        var bar = h('i', b.highlighted ? '' : 'out'); bar.style.width = Math.max(b.passing_other_four ? 2 : 0, Math.round(b.passing_other_four / max * 100)) + '%'; row.appendChild(bar);
        row.appendChild(h('span', '', num(b.passing_other_four))); bars.appendChild(row);
      });
      $('#barsNote').textContent = g.dte_matches_one_bucket
        ? 'The highlighted bucket is your DTE setting, ' + f.dte + '. The other buckets are shown for context.'
        : 'Your DTE setting, ' + f.dte + ', falls across the highlighted buckets. Each bar counts its whole bucket, so the highlighted bars can include contracts outside your setting; the count at the top of the screen is for your setting exactly.';
      var sp = g.spread; ['Med', 'Min', 'Max'].forEach(function (k, i) { $('#sp' + k).textContent = sp ? [sp.median, sp.tightest, sp.widest][i].toFixed(1) + '%' : '–'; });
      $('#outLine').textContent = num(g.screened_out) + ' of ' + num(g.considered) + ' contracts screened out. A contract can fail more than one criterion, so the tiles add up to more than ' + num(g.screened_out) + '.';
      var tiles = $('#outTiles'); tiles.textContent = '';
      REASONS.forEach(function (r) {
        var x = g.screened_out_by_reason[r[0]], t = h('div'); t.appendChild(h('span', '', r[1])); t.appendChild(h('b', '', num(x.count)));
        if (x.alone !== undefined) t.appendChild(h('span', '', num(x.alone) + ' for this reason alone'));
        tiles.appendChild(t);
      });
    }

    // buttons: what the workflow offers at this pause, in the mock-up's order
    var a = $('#s1Actions'); a.textContent = '';
    function btn(label, cls, fn, disabled, title) { var b = h('button', 'btn' + (cls ? ' ' + cls : ''), label); b.type = 'button'; if (fn) b.addEventListener('click', fn); if (disabled) b.disabled = true; if (title) b.title = title; a.appendChild(b); return b; }
    var ro = reviewing;
    if (checked) {
      btn('Adjust criteria', '', openCtl, ro || acts.indexOf('adjust') < 0);
      btn('View option chain', '', null, true, 'Not designed yet');
    }
    // Stop is on every state of this screen (pass, fail, not checked), before the primary button
    btn('Stop', '', function () { act('stop'); }, ro);
    if (ro || acts.indexOf('continue') > -1) btn('Continue to thesis', 'pri', function () { act('continue'); }, ro);
    if (!ro && g.status === 'fail') {
      if (acts.indexOf('override') > -1) btn('Override and continue', 'pri', function () { $('#ovr').hidden = false; $('#ovrText').value = ''; $('#ovrText').focus(); });
      else { line2.textContent = (line2.hidden ? '' : line2.textContent + ' ') + 'An invalid quote cannot be overridden.'; line2.hidden = false; }
    }
  }

  // adjust panel, as in the mock-up
  function readCtl() { var a = clampD($('#cD1').value), b = clampD($('#cD2').value); return {max_spread_pct: +$('#cGap').value, min_open_interest: OI[+$('#cOi').value], dte_min: Math.min(a, b), dte_max: Math.max(a, b), max_strike_distance_pct: +$('#cK').value, min_premium: +$('#cPx').value}; }
  function clampD(v) { v = Math.round(Number(v)); return isNaN(v) ? 7 : Math.max(7, Math.min(180, v)); }
  function setCtl(s) { $('#cGap').value = s.max_spread_pct; $('#cOi').value = Math.max(0, OI.indexOf(Number(s.min_open_interest))); $('#cD1').value = s.dte_min; $('#cD2').value = s.dte_max; $('#cK').value = s.max_strike_distance_pct; $('#cPx').value = s.min_premium; syncCtl(); }
  function syncCtl() {
    var s = readCtl(), f = fmt(s), d = fmt(DEF);
    [['oGap', 'gap'], ['oOi', 'oi'], ['oDte', 'dte'], ['oK', 'k'], ['oPx', 'px']].forEach(function (p) { var o = $('#' + p[0]); o.textContent = f[p[1]]; o.closest('.ctl').classList.toggle('chg', f[p[1]] !== d[p[1]]); });
    var key = s.dte_min + '-' + s.dte_max, sel = $('#cPre'); sel.value = [].some.call(sel.options, function (o) { return o.value === key; }) ? key : 'c';
  }
  function openCtl() { var c = $('#ctl'); c.hidden = !c.hidden; if (!c.hidden) { setCtl(st.settings); c.scrollIntoView({block: 'nearest'}); $('#ctlHead').focus({preventScroll: true}); } }
  ['cGap', 'cOi', 'cD1', 'cD2', 'cK', 'cPx'].forEach(function (id) { $('#' + id).addEventListener('input', syncCtl); });
  $('#cPre').addEventListener('change', function () { var v = this.value.split('-'); if (v.length === 2) { $('#cD1').value = v[0]; $('#cD2').value = v[1]; } syncCtl(); });
  $('#ctlCancel').addEventListener('click', function () { setCtl(st.settings); $('#ctl').hidden = true; });
  $('#ctlReset').addEventListener('click', function () { setCtl(DEF); });
  $('#ctlApply').addEventListener('click', function () { act('adjust', {settings: readCtl()}); });

  // override, with a required rationale
  $('#ovrCancel').addEventListener('click', function () { $('#ovr').hidden = true; });
  function confirmOverride() { var t = $('#ovrText').value.trim(); if (!t) { $('#ovrMsg').textContent = 'A rationale is required to override.'; $('#ovrText').focus(); return; } act('override', {rationale: t}); }
  $('#ovrGo').addEventListener('click', confirmOverride);
  $('#ovrText').addEventListener('keydown', function (e) { if (e.key === 'Enter') { e.preventDefault(); confirmOverride(); } });
  $('#ovrText').addEventListener('input', function () { $('#ovrMsg').textContent = ''; });

  document.querySelectorAll('[data-back]').forEach(function (b) { b.addEventListener('click', function () { st.review = null; render(); }); });
  // ---- stage 2: the thesis ------------------------------------------------------------
  var MONTHS = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
  function dm(iso) { if (!iso) return ''; var p = String(iso).slice(0, 10).split('-'); return Number(p[2]) + ' ' + MONTHS[Number(p[1]) - 1]; }
  function days(n) { return n + (Math.abs(n) === 1 ? ' day' : ' days'); }
  function chip(cls, txt) { return h('span', 'chip' + (cls ? ' ' + cls : ''), txt); }
  function clear(q) { var e = $(q); e.textContent = ''; return e; }
  function row(lead, main, small, first) {
    var r = h('div', 'row'); if (first) { r.style.borderTop = '0'; }
    r.appendChild(lead); var d = h('div', '', main); if (small) d.appendChild(h('small', '', small)); r.appendChild(d); return r;
  }
  function stepNo(n) { var s = h('span', 'mono', String(n)); s.style.color = 'var(--accent)'; return s; }
  function words(s) { s = String(s || '').replace(/_/g, ' '); return s.charAt(0).toUpperCase() + s.slice(1); }
  function btn2(host, label, cls, fn, disabled, title) { var b = h('button', 'btn' + (cls ? ' ' + cls : ''), label); b.type = 'button'; b.disabled = !!disabled; if (title) b.title = title; if (fn) b.addEventListener('click', fn); host.appendChild(b); return b; }

  var AGENT_SUB = {evidence_retriever: 'Fetching filings, earnings materials and the calendar', fundamental_analyst: 'Reading filings and estimates',
    regime_assessor: 'Sector, macro and market conditions', technical_analyst: 'Describing price behaviour',
    thesis: 'Combining the findings by precedence', validation: 'Fixed rules, in code',
    critic: 'Bull case, bear case, how the trade loses, objections', output_check: 'Fixed rules, in code'};
  var AGENT_SUB4 = {evidence_retriever: "Searching the project's research, both ways"};

  // The agents-working panel. It stays on screen, with each agent's final status, when the stage stops.
  function renderWorking() {
    var s4 = !!v0().state.selection;
    var v = st.view, stopped = v.pause && (v.pause.pause === 'stage2_stopped' || v.pause.pause === 'stage4_stopped');
    $('#s2wTitle').textContent = (s4 ? 'Challenging the thesis and the strategy on ' : 'Building a thesis on ') + v.symbol;
    $('#agNote').hidden = !!stopped;
    var msg = $('#s2wMsg'); msg.hidden = !stopped && !v.error;
    if (stopped) {
      var sp = v.pause.stop;
      msg.textContent = sp.message + (sp.cause === 'spend_limit' && sp.scope === 'day' && sp.resets_at ? ' The daily limit resets at ' + hm(sp.resets_at) + ' ET.' : '');
    } else if (v.error) msg.textContent = v.error;
    var host = clear('#agents');
    (v.progress || []).forEach(function (p) {
      var s = p.status, cls = s === 'done' ? 'fin' : s === 'working' ? 'run' : '';
      var d = h('div', 'ag ' + cls + (p.parallel ? ' par' : ''));
      var dot = h('span', 'dot'); dot.setAttribute('aria-hidden', 'true'); d.appendChild(dot);
      var x = h('div'); x.appendChild(h('b', '', p.label)); x.appendChild(h('small', '', (s4 && AGENT_SUB4[p.agent]) || AGENT_SUB[p.agent] || '')); d.appendChild(x);
      d.appendChild(s === 'failed' || s === 'timed out' ? chip('fl', s.toUpperCase()) : s === 'not run' ? chip('un', 'NOT RUN') : h('span', 'st', s.toUpperCase()));
      host.appendChild(d);
    });
    var a = clear('#s2wActions');
    if (stopped) {
      var pa = v.pause.actions;
      if (pa.indexOf('retry') > -1) btn2(a, 'Retry', '', function () { act('retry'); });
      if (pa.indexOf('checklists_only') > -1) btn2(a, 'Continue with the checklists only', '', function () { act('checklists_only'); });
      if (pa.indexOf('return') > -1) btn2(a, 'Return to contracts', '', function () { act('return'); });
      btn2(a, 'Stop', pa.length > 1 ? '' : 'pri', function () { act('stop'); });
    } else btn2(a, 'Stop', '', function () { act('stop'); }, !v.running);
  }
  function v0() { return st.view; }

  var KIND = {results_vs_estimates: 'Results against estimates', guidance_change: 'Guidance change', new_event: 'New event'};
  function sourceShort(f) {
    var s = f.source || '';
    var m = s.match(/^SEC EDGAR, (\S+)/); if (m) return m[1];
    if (/^FMP/.test(s)) return 'data provider';
    m = s.match(/^(.+?) \(via /); if (m) return m[1];
    return s === 'computed in code from daily closes' ? 'computed from daily closes' : s;
  }
  function srcDate(f) { var s = sourceShort(f); return s + (f.date ? (s ? ', ' : '') + dm(f.date) : ''); }
  function comparison(f) {
    if (f.kind === 'results_vs_estimates') return 'direction set in code from the two numbers';
    if (f.kind === 'guidance_change') return f.guidance && f.guidance.compared_with === 'consensus' ? 'against consensus' : "against the company's earlier guidance";
    return words(f.event_kind).toLowerCase();
  }
  // Citations are for the validation check, not the screen: drop any id the agent left in its text.
  function clean(text) { return String(text || '').replace(/\s*\((?:(?:and\s+)?[FRM]\d+(?:\s*,\s*|\s+and\s+)?)+\)/g, ''); }
  function findingsOf(t) { return Object.keys(t.findings || {}).map(function (k) { return t.findings[k]; }); }

  function renderBrief(readOnly) {
    var v = st.view, t = v.state.thesis || {}, fig = v.state.figures || {}, m = fig.measured || {}, sym = v.symbol;
    var view = v.state.view, user = v.state.user_thesis, noView = !!t.no_view;
    var actions = (v.pause && v.pause.pause === 'thesis' && !readOnly) ? v.pause.actions : [];
    var head = clear('#s2Head'), acts = clear('#s2Actions'), note = $('#s2Note'); note.hidden = true;
    $('#s2Review').classList.toggle('on', !!readOnly);
    var td = v.state.thesis_decision;
    $('#s2Frozen').textContent = td && td.at ? 'The thesis was frozen at ' + hm(new Date(td.at * 1000).toISOString()) + ' and cannot be changed.' : '';
    function top(children) { var d = h('div'); d.style.cssText = 'display:flex;flex-wrap:wrap;gap:8px 14px;align-items:center'; children.forEach(function (c) { d.appendChild(c); }); head.appendChild(d); }
    function para(txt, strong) { var p = h('p'); p.style.marginTop = '8px'; if (strong) p.appendChild(h('strong', '', txt)); else p.textContent = txt; head.appendChild(p); return p; }
    function big(txt) { var s = h('strong', '', txt); s.style.fontSize = '1.0625rem'; return s; }
    function viewActions() {
      btn2(acts, 'Reject and stop', '', function () { act('reject'); }, readOnly);
      btn2(acts, 'Edit', '', null, true, 'Not available in this version');
      btn2(acts, 'Accept and freeze the thesis', 'pri', function () { act('accept'); }, readOnly);
    }
    var rd = t.report_dates || {};
    var datesLine = 'Latest report: ' + (rd.latest_report ? dm(rd.latest_report) + ' (' + days(rd.latest_report_days_ago) + ' ago)' : 'not available')
      + ' · Next earnings report: ' + (rd.next_report ? dm(rd.next_report) : 'not available');

    // Two results that are not designed: one plain line each.
    var plain = view === 'range_bound' ? 'Range-bound view, set by rule. This screen is not designed yet.'
      : (!noView && t.validation && !t.validation.ok) ? 'The draft failed the validation check after being returned once. This screen is not designed yet.' : null;
    $('#s2Body').hidden = !!plain;
    if (plain) { para(plain).style.marginTop = '0'; if (actions.length || readOnly) viewActions(); return; }

    var days_ = t.recommended_horizon_days, bearish = (user ? user.view : t.view) === 'bearish';
    if (!noView) {
      var chips = [chip('dir ' + (t.view === 'bullish' ? 'bull' : 'bear'), t.view.toUpperCase()), big('Directional thesis, ' + days_ + '-day horizon')];
      if (t.support === 'weak') chips.push(chip('fl', 'WEAKLY SUPPORTED'));
      chips.push(chip('un', 'NO DEMONSTRATED PREDICTIVE EDGE'));
      top(chips);
      para(clean(t.summary.text));
      if (t.support === 'weak' && t.support_note) para(t.support_note, true);
      var dl = h('p', 'sub', datesLine); dl.style.marginTop = '6px'; head.appendChild(dl);
      var why = h('div', 'why'), R = t.rationale, weak = t.support === 'weak';
      [[weak ? 'The basis' : 'The catalyst', clean(R.catalyst.text)], [weak ? 'What is missing' : 'The confirmation', clean(R.confirmation.text)], ['What tempers it', clean(R.tempering.text)]]
        .forEach(function (b) { var d = h('div'); d.appendChild(h('h3', '', b[0])); d.appendChild(h('p', '', b[1])); why.appendChild(d); });
      head.appendChild(why);
      var lab = h('p', 'sub', 'Why the "no demonstrated predictive edge" label: this is a researched view with its evidence shown. The system has not yet shown that its views beat the base rate, and it says so on every thesis.');
      lab.style.marginTop = '10px'; head.appendChild(lab);
      viewActions();
    } else {
      var nv = t.no_view_text || {};
      top([chip('dir nov', 'NO VIEW'), big(nv.headline || 'The system returned no view')]);
      para((nv.sentences || []).join(' '));
      var sub = h('p', 'sub', nv['case'] === 'conflict'
        ? 'A no view is a result, not a failure. The other reason for it is that nothing found carries a direction at all; the screen says which applies.'
        : 'A no view is a result, not a failure.'); sub.style.marginTop = '8px'; head.appendChild(sub);
      var dl2 = h('p', 'sub', datesLine); dl2.style.marginTop = '6px'; head.appendChild(dl2);
      var canOwn = t.own_view_allowed !== false;
      // What the user can do sits in the no-view card itself (operator decision, 19 November 2026).
      var wh = h('h3', 'sh', 'What you can do'); wh.style.marginTop = '14px'; head.appendChild(wh);
      var choices = h('div', 'choices'); head.appendChild(choices);
      var r1 = row(stepNo(1), ''); r1.lastChild.appendChild(h('strong', '', 'Stop.'));
      r1.lastChild.appendChild(document.createTextNode(' The request ends and nothing is recorded.')); choices.appendChild(r1);
      if (canOwn) {
        var r2 = row(stepNo(2), ''); r2.lastChild.appendChild(h('strong', '', 'Take a view yourself.'));
        r2.lastChild.appendChild(document.createTextNode(' Choose the direction, mark what you are relying on from the evidence on this screen, and say what would prove you wrong. The system tells you how much of it carries a direction, records the thesis as yours and carries on to contracts and the challenge.'));
        choices.appendChild(r2);
      }
      var na = h('p', 'sub', 'The agents are not asked again for a different answer.'); na.style.marginTop = '10px'; head.appendChild(na);
      btn2(acts, 'Stop', canOwn ? '' : 'pri', function () { act('stop'); }, readOnly);
      if (canOwn) btn2(acts, 'Take a view yourself', 'pri', function () { st.sub = 'own'; render(); }, readOnly || actions.indexOf('own_view') < 0);
      if (canOwn && nv.override_note) { note.textContent = nv.override_note; note.hidden = false; }
    }

    // Evidence: what carries a direction, then context.
    var ev = clear('#s2Ev'), all = findingsOf(t);
    var carrying = all.filter(function (f) { return f.bearing !== 'none'; });
    var evHead = h('h2', '', 'Evidence that carries a direction ');
    var nBull = carrying.filter(function (f) { return f.bearing === 'supports_bullish'; }).length;
    if (carrying.length) evHead.appendChild(h('span', 'tally', nBull + ' bullish · ' + (carrying.length - nBull) + ' bearish'));
    ev.appendChild(evHead);
    ev.appendChild(h('p', 'sub', 'A finding carries a direction only when the evidence states the comparison: a result against estimates, a change in guidance, or a defined new event.'));
    carrying.forEach(function (f, i) {
      var up = f.bearing === 'supports_bullish';
      ev.appendChild(row(chip('dir ' + (up ? 'bull' : 'bear'), up ? 'BULLISH' : 'BEARISH'), f.text, [KIND[f.kind] || 'Finding', comparison(f), srcDate(f), f.grade].join(' · '), i === 0));
    });
    if (!carrying.length) ev.appendChild(row(chip('un', 'NONE'), 'Nothing found carries a direction', null, true));
    else if (!noView && !carrying.some(function (f) { return f.bearing === (t.view === 'bullish' ? 'supports_bearish' : 'supports_bullish'); }))
      ev.appendChild(row(chip('un', 'NONE'), 'Nothing carrying a direction points ' + (t.view === 'bullish' ? 'lower' : 'higher'), 'Sector and macro evidence: nothing found for or against'));
    // Context and the sector and macro backdrop: each in its own card that folds, with a count.
    function fold(card, rowsQ, countQ, list, sub, openIf) {
      var host = clear(rowsQ), box = $(card);
      box.hidden = !list.length; $(countQ).textContent = list.length;
      host.appendChild(h('p', 'sub', sub));
      list.forEach(function (f, i) { host.appendChild(row(chip('un', 'CONTEXT'), f.text, (f.context_sentence || 'No stated comparison') + ' · ' + srcDate(f), i === 0)); });
      var key = (st.view && st.view.request_id || '') + ':' + list.length;      // keep the user's own open or closed choice
      if (box.dataset.key !== key) { box.dataset.key = key; box.open = openIf; }
    }
    var context = all.filter(function (f) { return f.bearing === 'none' && f.analyst !== 'regime_assessor'; });
    var backdrop = all.filter(function (f) { return f.bearing === 'none' && f.analyst === 'regime_assessor'; });
    fold('#s2Ctx', '#s2CtxRows', '#s2CtxN', context, 'Facts with nothing to compare them against. They are shown and may be quoted, and cannot start, support or cancel a view.', context.length <= 4);
    fold('#s2Back', '#s2BackRows', '#s2BackN', backdrop, 'What the sector and the market have done. Description only: it cannot start, support or cancel a view.', false);

    // Beside it: invalidation criteria for a view, what the user can do after a no view.
    var right = clear('#s2Right');
    if (!noView) {
      var fs = t.falsifiers || [];
      right.appendChild(h('h2', '', 'Invalidation criteria'));
      right.appendChild(h('p', '', 'The thesis no longer holds if ' + (fs.length === 2 ? 'either' : 'any') + ' of these happens:'));
      fs.forEach(function (f, i) { right.appendChild(row(stepNo(i + 1), clean(f.trigger), clean(f.reverses))); });
    }
    right.hidden = noView;        // on a no view the evidence takes the full width

    // Flags and missing inputs.
    // The card folds. Its heading always says how many of each there are, and it starts open
    // when a flag is raised, so a folded card never hides one.
    var flBox = $('#s2Flags'), fl = clear('#s2FlagRows'), flags = t.risk_flags || [], missing = t.inputs_unavailable || [];
    flBox.hidden = !flags.length && !missing.length;
    if (!flBox.hidden) {
      $('#s2FlagN').hidden = !flags.length; $('#s2FlagN').textContent = flags.length + (flags.length === 1 ? ' FLAG' : ' FLAGS');
      $('#s2MissN').hidden = !missing.length; $('#s2MissN').textContent = missing.length + ' MISSING';
      var flKey = (st.view && st.view.request_id || '') + ':' + flags.length + ':' + missing.length;
      if (flBox.dataset.key !== flKey) { flBox.dataset.key = flKey; flBox.open = flags.length > 0; }
      flags.forEach(function (f, i) { fl.appendChild(row(chip('fl', 'FLAG'), words(f.flag), [f.note, f.event_date ? dm(f.event_date) : ''].filter(Boolean).join(' · ') || null, i === 0)); });
      missing.forEach(function (x, i) { var mm = String(x).match(/^(.*?)\s*\((.*)\)$/) || String(x).match(/^(.*?):\s*(.*)$/); fl.appendChild(row(chip('', 'N/A'), words(mm ? mm[1] : x), mm ? words(mm[2]) : null, i === 0 && !flags.length)); });
    }

    // Historical statistics: the recommended row and its neighbours.
    var rows = (m.horizons || []).filter(function (r) { return !r.context_only; });
    var at = Math.max(0, rows.findIndex(function (r) { return r.days === days_; })); if (days_ == null) at = 2;
    var from = Math.min(Math.max(at - 1, 0), Math.max(rows.length - 3, 0)), shown = rows.slice(from, from + 3);
    st.s2rows = shown.map(function (r) { return r.days; });
    $('#s2BaseHead').textContent = bearish ? 'Base rate, lower close' : 'Base rate, higher close';
    var tb = clear('#s2Rows'), sel = null;
    function base(r) { return r.base_rate_pct == null ? null : bearish ? 100 - r.base_rate_pct : r.base_rate_pct; }
    shown.forEach(function (r) {
      var tr = h('tr'); if (r.days === days_) { tr.className = 'sel'; sel = r; }
      tr.appendChild(h('td', '', r.days + ' days' + (r.days === days_ ? ' · recommended' : '')));
      tr.appendChild(h('td', 'n', base(r) == null ? 'n/a' : Math.round(base(r)) + '%'));
      tr.appendChild(h('td', 'n', r.typical_move_pct == null ? 'n/a' : '±' + r.typical_move_pct.toFixed(1) + '%'));
      tb.appendChild(tr);
    });
    var ag = $('#s2Against'); ag.hidden = !(bearish && sel && base(sel) < 50);
    if (!ag.hidden) ag.textContent = 'This view runs against the base rate: ' + sym + ' closed lower in ' + Math.round(base(sel)) + '% of past ' + sel.days + '-day periods.';
    var wy = clear('#s2Why');
    wy.appendChild(h('h3', 'sh', days_ ? 'Why the ' + days_ + '-day row is recommended' : 'No row is recommended'));
    var ul = h('ul', 'plain'); (t.horizon_reasons_code || []).forEach(function (x) { ul.appendChild(h('li', '', x)); }); wy.appendChild(ul);
    if (!noView && (t.horizon_reasons || []).length) {
      var h3 = h('h3', 'sh', 'How the evidence fits this horizon'); h3.style.marginTop = '14px'; wy.appendChild(h3);
      var ul2 = h('ul', 'plain'); t.horizon_reasons.forEach(function (x) { ul2.appendChild(h('li', '', clean(x.text))); }); wy.appendChild(ul2);
    }
    if (noView) { var nd = h('p', 'sub', 'The recommendation takes no account of direction. It is the row preselected if you take a view yourself.'); nd.style.marginTop = '10px'; wy.appendChild(nd); }
    var defs = clear('#s2Defs'), N = sel ? sel.days : null, vol = (m.volatility || {}).state;
    function def(dt, dd) { var d = h('div'); d.appendChild(h('dt', '', dt)); d.appendChild(h('dd', '', dd)); defs.appendChild(d); }
    def(bearish ? 'Base rate, lower close' : 'Base rate, higher close', 'How often ' + sym + ' has finished a period of that length ' + (bearish ? 'below' : 'above') + ' where it started, whatever the news.'
      + (sel && base(sel) != null ? ' Over ' + N + ' days it has done so ' + Math.round(base(sel)) + '% of the time.' : '') + ' This is the benchmark: the thesis is only useful if it does better than this.');
    def('Typical realized move', 'The size of a normal move over that horizon, measured from past prices.'
      + (sel && sel.typical_move_pct != null ? ' Over ' + N + ' days ' + sym + ' has typically ended within about ' + sel.typical_move_pct.toFixed(1) + '% of where it started, up or down.' : '') + ' Use it to judge how far a strike is from spot.');
    var span = N ? 'the next ' + N + ' days' : 'the period ahead';
    def('Current volatility', vol === 'quiet' ? sym + ' has been moving less than it normally does. The figures above may overstate the swings over ' + span + '; quiet periods can end abruptly.'
      : vol === 'normal' ? sym + ' has been moving about as much as it normally does, so the figures above are a fair guide to ' + span + '. In a high-volatility period they would understate the swings.'
      : vol === 'active' ? sym + ' has been moving more than it normally does. The figures above are likely to understate the swings over ' + span + '.'
      : 'Not available.');

    // How the system reasoned: the three branches.
    var br = clear('#s2Branches'), P = t.precedence || {}, NAME = {bullish: 'Bullish', bearish: 'Bearish', no_view: 'No view'};
    function list(ids) { return ids && ids.length ? ids.map(function (i) { var f = (t.findings || {})[i]; return i + (f ? ': ' + f.text : ''); }).join(' | ') : 'none'; }
    (t.branches || []).forEach(function (b) {
      var selected = !b.pruned_reason, met = b.view === 'no_view' ? selected : !!(P[b.view] && P[b.view].meets);
      var r = row(chip(selected ? 'ok' : 'un', selected ? 'SELECTED' : 'PRUNED'), '');
      r.lastChild.appendChild(h('strong', '', NAME[b.view]));
      r.lastChild.appendChild(h('small', '', 'Findings for it: ' + list(b.supporting)));
      r.lastChild.appendChild(h('small', '', 'Findings against it: ' + list(b.opposing)));
      r.lastChild.appendChild(h('small', '', 'Met the rules: ' + (met ? 'yes' : 'no')));
      r.lastChild.appendChild(h('small', '', selected ? 'Selected' : 'Pruned: ' + b.pruned_reason));
      br.appendChild(r);
    });
    $('#s2Reason').hidden = !(t.branches || []).length;
  }

  // "Take a view yourself", after a no view.
  function renderOwn() {
    var v = st.view, t = v.state.thesis, o = t.own_view_options || {}, nv = t.no_view_text || {};
    if (!st.own || st.own.rid !== v.request_id) st.own = {rid: v.request_id, dir: 'bullish', days: o.recommended_days, rely: {}, cond: {}};
    var u = st.own;
    document.querySelectorAll('#uDir button').forEach(function (b) { b.setAttribute('aria-pressed', b.getAttribute('data-d') === u.dir ? 'true' : 'false'); });
    var selH = clear('#uHor'), rowsShown = (st.s2rows && st.s2rows.length ? st.s2rows : o.horizons || []);
    if (rowsShown.indexOf(u.days) < 0) u.days = rowsShown.indexOf(o.recommended_days) > -1 ? o.recommended_days : rowsShown[0];
    rowsShown.forEach(function (d) { var op = h('option', '', d + ' days' + (d === o.recommended_days ? ' · recommended' : '')); op.value = d; op.selected = d === u.days; selH.appendChild(op); });
    var rely = clear('#uRely');
    (o.evidence || []).forEach(function (e) {
      var lab = h('label', 'opt'), box = h('input'); box.type = 'checkbox'; box.checked = !!u.rely[e.id];
      box.addEventListener('change', function () { u.rely[e.id] = box.checked; ownVerdict(); });
      var tx = h('span', 't', e.text), sm = h('small');
      sm.appendChild(e.bearing === 'none' ? chip('un', 'CONTEXT') : chip('dir ' + (e.bearing === 'supports_bullish' ? 'bull' : 'bear'), e.bearing === 'supports_bullish' ? 'BULLISH' : 'BEARISH'));
      sm.appendChild(document.createTextNode(e.bearing === 'none' ? ' no direction' : ' carries a direction'));
      tx.appendChild(sm); lab.appendChild(box); lab.appendChild(tx); rely.appendChild(lab);
    });
    var cond = clear('#uCond');
    ((o.conditions || {})[u.dir] || []).forEach(function (c) {
      var lab = h('label', 'opt'), box = h('input'); box.type = 'checkbox'; box.checked = !!u.cond[c.id];
      box.addEventListener('change', function () { u.cond[c.id] = box.checked; ownVerdict(); });
      var tx = h('span', 't', c.text); if (c.note) tx.appendChild(h('small', '', c.note));
      lab.appendChild(box); lab.appendChild(tx); cond.appendChild(lab);
    });
    var n = $('#uNote'); n.hidden = !nv.override_note; n.textContent = nv.override_note || '';
    ownVerdict();
  }
  function ownPicked() {
    var u = st.own, o = st.view.state.thesis.own_view_options || {};
    return {rely: (o.evidence || []).filter(function (e) { return u.rely[e.id]; }),
            cond: ((o.conditions || {})[u.dir] || []).filter(function (c) { return u.cond[c.id]; }), all: o.evidence || []};
  }
  function ownVerdict() {
    var u = st.own, p = ownPicked(), want = u.dir === 'bullish' ? 'supports_bullish' : 'supports_bearish';
    var sup = p.rely.filter(function (e) { return e.bearing === want; }).length;
    var ctx = p.rely.filter(function (e) { return e.bearing === 'none'; }).length;
    var opp = p.all.filter(function (e) { return e.bearing !== 'none' && e.bearing !== want; }).length;
    var c = $('#uChip'), vd = $('#uVerdict'), w = $('#uWhy');
    function plural(k, one, many) { return k === 1 ? one : many.replace('#', k); }
    var oppLine = opp ? plural(opp, 'One finding that carries a direction points the other way', '# findings that carry a direction point the other way') : '';
    if (!p.rely.length) { c.textContent = 'NOT STARTED'; c.className = 'chip'; vd.textContent = 'Choose what you are relying on.'; w.textContent = ''; }
    else if (sup === 0) { c.textContent = 'NOT SUPPORTED'; c.className = 'chip fl'; vd.textContent = 'Nothing you chose carries a direction that matches your view.';
      w.textContent = (ctx ? plural(ctx, '1 context item', '# context items') + ' chosen; context has no direction. ' : '') + (opp ? oppLine + '.' : ''); }
    else if (opp || ctx) { c.textContent = 'PARTLY SUPPORTED'; c.className = 'chip ac'; vd.textContent = plural(sup, 'One finding with a direction supports your view.', '# findings with a direction support your view.');
      w.textContent = (opp ? oppLine + '; ' + plural(opp, 'it stands', 'they stand') + ' against the thesis whether or not you chose ' + plural(opp, 'it', 'them') + '. ' : '') + (ctx ? ctx + ' of your choices ' + (ctx > 1 ? 'are' : 'is') + ' context and ' + (ctx > 1 ? 'add' : 'adds') + ' no support.' : ''); }
    else { c.textContent = 'WELL SUPPORTED'; c.className = 'chip ok'; vd.textContent = 'Everything you chose carries a direction that matches your view.'; w.textContent = ''; }
    $('#uFreeze').disabled = !(p.rely.length && p.cond.length) || st.busy;
  }
  document.querySelectorAll('#uDir button').forEach(function (b) { b.addEventListener('click', function () { if (!st.own) return; st.own.dir = b.getAttribute('data-d'); st.own.cond = {}; renderOwn(); }); });
  $('#uHor').addEventListener('change', function () { if (st.own) st.own.days = Number(this.value); });
  $('#uBack').addEventListener('click', function () { st.sub = null; $('#appMsg').textContent = ''; render(); });
  $('#uStop').addEventListener('click', function () { act('stop'); });
  $('#uFreeze').addEventListener('click', function () {
    var p = ownPicked(), u = st.own;
    act('own_view', {direction: u.dir, horizon_days: u.days, relied_on: p.rely.map(function (e) { return e.id; }), conditions: p.cond.map(function (c) { return c.id; })});
  });
  // ---- stage 3: contracts (docs/product-shell.md 6.3) ------------------------------------
  var NS = 'http://www.w3.org/2000/svg';
  var PRI = [['match', 'Fit to thesis', 3], ['payoff', 'Reward-to-risk', -9], ['cost', 'Lowest slippage', 5]];
  var HEAD = ['', 'Strategy', 'Max loss', 'Max profit', 'Breakeven', 'Profitable if thesis holds', 'POP: historical / implied', 'Est. slippage', 'Contracts', ''];
  var o3 = {rid: null, open: '__top', cap: null, exp: null};
  function usd(x) { return '$' + Math.round(x).toLocaleString('en-US'); }
  function px(x) { return '$' + Number(x).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}); }
  function pct(x) { return x == null ? 'n/a' : Math.round(x) + '%'; }
  function pct1(x) { return x == null ? 'n/a' : (Math.round(x * 10) / 10) + '%'; }
  function signed(x, money) { if (x == null) return 'n/a'; var a = money ? Math.round(Math.abs(x)) : Math.abs(x); if (money && a === 0) return '$0'; return (x < 0 ? '−' : '+') + (money ? '$' + a : a.toFixed(2)); }
  function sv(n, a, txt) { var e = document.createElementNS(NS, n); for (var k in a) e.setAttribute(k, a[k]); if (txt != null) e.textContent = txt; return e; }
  function s3Params(extra) { var p = Object.assign({}, st.view.state.contracts_params || {}); return Object.assign(p, extra || {}); }
  function qty(c) { return o3.cap == null ? 1 : Math.floor(o3.cap / c.max_loss); }
  function shortName(c) { return c.structure.split('(')[0].trim().toLowerCase(); }
  function horizons(list) { return list.length === 1 ? 'the ' + list[0] + '-day horizon' : 'the ' + list.slice(0, -1).join('-, ') + '- and ' + list[list.length - 1] + '-day horizons'; }
  function eventText(e, exp, what) {
    if (!e.date) return what + ': ' + e.status;
    return what + ': ' + dm(e.date) + (e.date <= exp ? ', before this expiration' : ', after this expiration');
  }

  function chart(c, m, x) {
    var lo = x.chart.low, hi = x.chart.high, be = c.break_even;
    var g = sv('svg', {viewBox: '0 0 520 220', role: 'img', 'aria-label': 'Profit or loss at expiration for ' + c.name + ', breaking even at ' + be.map(px).join(' and ')});
    var pts = c.points, ys = pts.map(function (p) { return p[1]; });
    var loss = c.max_loss / 100, top = Math.max.apply(null, ys), ym = (Math.max(loss, Math.min(top, 2.5 * loss)) || 1) * 1.2;
    var X = function (p) { return 44 + (p - lo) / (hi - lo) * 466; }, Y = function (v) { return 100 - v / ym * 80; };
    var cid = 'oc-' + c.id, cp = sv('clipPath', {id: cid}); cp.appendChild(sv('rect', {x: 44, y: 20, width: 466, height: 160})); g.appendChild(cp);
    var bl = Math.max(lo, x.chart.move_low), bh = Math.min(hi, x.chart.move_high);
    g.appendChild(sv('rect', {class: 'bandr', x: X(bl), y: 20, width: X(bh) - X(bl), height: 160}));
    [-1, -0.5, 0, 0.5, 1].forEach(function (f) {
      var v = f * ym;
      g.appendChild(sv('line', {class: f ? 'ax' : 'zero', x1: 44, x2: 510, y1: Y(v), y2: Y(v)}));
      g.appendChild(sv('text', {class: 'mono-t', x: 38, y: Y(v) + 4, 'text-anchor': 'end', 'font-size': 10}, (v > 0 ? '+' : v < 0 ? '−' : '') + usd(Math.abs(v * 100 * m))));
    });
    [0.08, 0.29, 0.5, 0.71, 0.92].forEach(function (f) { var k = lo + f * (hi - lo); g.appendChild(sv('text', {class: 'mono-t', x: X(k), y: 196, 'text-anchor': 'middle', 'font-size': 10}, '$' + (k >= 100 ? Math.round(k) : k.toFixed(1)))); });
    var all = pts.concat(be.filter(function (b) { return b > lo && b < hi; }).map(function (b) { return [b, 0]; })).sort(function (a, b) { return a[0] - b[0]; });
    function area(sign) { return 'M' + X(all[0][0]) + ' ' + Y(0) + all.map(function (p) { return ' L' + X(p[0]) + ' ' + Y(sign > 0 ? Math.max(p[1], 0) : Math.min(p[1], 0)); }).join('') + ' L' + X(all[all.length - 1][0]) + ' ' + Y(0) + ' Z'; }
    g.appendChild(sv('path', {class: 'lossf', d: area(-1), 'clip-path': 'url(#' + cid + ')'}));
    g.appendChild(sv('path', {class: 'gainf', d: area(1), 'clip-path': 'url(#' + cid + ')'}));
    if (x.levels) [[x.levels.low, '60-day low ' + usd(x.levels.low), 'end', -4], [x.levels.high, '60-day high ' + usd(x.levels.high), 'start', 4]].forEach(function (L) {
      if (L[0] <= lo || L[0] >= hi) return;
      g.appendChild(sv('line', {class: 'lvl', x1: X(L[0]), x2: X(L[0]), y1: 20, y2: 180}));
      var room = L[2] === 'end' ? X(L[0]) > 150 : X(L[0]) < 400;
      g.appendChild(sv('text', {class: 'lvl-t', x: X(L[0]) + (room ? L[3] : -L[3]), y: 31, 'text-anchor': room ? L[2] : (L[2] === 'end' ? 'start' : 'end'), 'font-size': 10}, L[1]));
    });
    g.appendChild(sv('line', {class: 'spot', x1: X(x.spot), x2: X(x.spot), y1: 20, y2: 180}));
    g.appendChild(sv('text', {x: X(x.spot), y: 13, 'text-anchor': 'middle', 'font-size': 11}, 'Spot'));
    g.appendChild(sv('polyline', {class: 'pline', 'clip-path': 'url(#' + cid + ')', points: pts.map(function (p) { return X(p[0]) + ',' + Y(p[1]); }).join(' ')}));
    be.forEach(function (b, i) {
      if (b <= lo || b >= hi) return;
      g.appendChild(sv('circle', {class: 'dot', cx: X(b), cy: Y(0), r: 5}));
      var left = be.length > 1 && i === 0;
      g.appendChild(sv('text', {x: X(b) + (left ? -9 : 9), y: Y(0) + 15, 'text-anchor': left ? 'end' : 'start', 'font-size': 11}, 'Breakeven ' + px(b)));
    });
    var lossLeft = ys[0] <= ys[ys.length - 1], condor = be.length > 1;
    g.appendChild(sv('text', {class: 'strong-t', x: lossLeft ? 48 : 506, y: Y(-loss) + 15, 'text-anchor': lossLeft ? 'start' : 'end', 'font-size': 12}, 'Max loss −' + usd(c.max_loss * m)));
    var gainTxt = c.max_gain == null ? 'Profit continues above the chart' : (top * 100 < c.max_gain - 0.5 ? 'Profit continues beyond the chart' : 'Max profit +' + usd(c.max_gain * m));
    g.appendChild(sv('text', {class: 'strong-t', x: condor ? 277 : lossLeft ? 506 : 48, y: Math.max(Y(Math.min(top, ym)) - 7, 48), 'text-anchor': condor ? 'middle' : lossLeft ? 'end' : 'start', 'font-size': 12}, gainTxt));
    g.appendChild(sv('text', {x: 277, y: 214, 'text-anchor': 'middle', 'font-size': 11}, 'Underlying price at expiration · shaded band is the typical realized move'));
    return g;
  }

  function detail(c, x) {
    var d = h('div', 'odet'), a = h('div', 'oc'), b = h('div', 'os');
    var q = qty(c), m = Math.max(q, 1), exp = x.expiry_chosen;
    a.appendChild(h('h4', '', 'P&L at expiration, ' + (m === 1 ? 'for one contract' : 'for ' + m + ' contracts')));
    var v = h('div', 'viz'); v.appendChild(chart(c, m, x)); a.appendChild(v);
    if (x.levels) a.appendChild(h('p', 'keyline', '60-day high and low of the daily close · context only, they place no strike'));
    var t = h('div', 'tiles');
    [['Profitable if thesis holds, before slippage', pct(c.pays_when_view_right.pct)], ['POP, historical base rate, before slippage', pct(c.base_rate_profit.pct)], ['POP, market-implied, approximate', pct(c.implied_profit.pct)]].forEach(function (r) { var e = h('div', 'tile'); e.appendChild(h('span', '', r[0])); e.appendChild(h('b', '', r[1])); t.appendChild(e); });
    a.appendChild(t);
    b.appendChild(h('h4', '', 'Legs and quotes'));
    var tb = h('table'); tb.innerHTML = '<thead><tr><th>Leg</th><th>Bid</th><th>Ask</th><th>Mid</th></tr></thead>';
    var body = h('tbody');
    c.legs.forEach(function (l) { var tr = h('tr'); tr.appendChild(h('td', '', (l.action === 'buy' ? 'Buy ' : 'Sell ') + l.strike + ' ' + l.type)); [l.bid, l.ask, l.mid].forEach(function (n) { tr.appendChild(h('td', 'n', Number(n).toFixed(2))); }); body.appendChild(tr);
      if (l.spread_above_setting) { var nr = h('tr'), nd = h('td', '', "This leg's quoted spread is " + l.spread_pct + '% of its premium, above your ' + l.spread_setting_pct + '% setting. Cost is judged on the whole structure.'); nd.colSpan = 4; nd.style.cssText = 'color:var(--ink-3);font-size:0.75rem;padding-top:0'; nr.appendChild(nd); body.appendChild(nr); } });
    tb.appendChild(body); b.appendChild(tb);
    b.appendChild(h('p', 'sub', 'Net ' + (c.credit ? 'credit ' : 'debit ') + usd(Math.abs(c.net_price) * m) + ' at mid' + (m === 1 ? ', one contract' : ', ' + m + ' contracts') + ' · est. slippage ' + usd(c.cost.dollars * m) + ', ' + pct1(c.cost.pct_of_risk) + ' of max loss'));
    b.appendChild(h('h4', '', 'Greeks, per contract'));
    var ex = h('div', 'ex3'); [['Delta', signed(c.greeks.delta)], ['Theta, per day', signed(c.greeks.theta, true)], ['Vega, per vol point', signed(c.greeks.vega, true)]].forEach(function (r) { var e = h('div', '', r[0]); e.appendChild(h('b', '', r[1])); ex.appendChild(e); }); b.appendChild(ex);
    b.appendChild(h('h4', '', 'Checks'));
    var ev = x.events, ck = c.checks;
    function evCheck(e) { return e.date ? (e.date <= exp ? 'Yes, ' + dm(e.date) : 'No') : words(e.status); }
    [['Earnings before expiration', evCheck(ev.earnings)],
     [ck.has_short_leg ? 'Ex-dividend before expiration, short leg' : 'Ex-dividend before expiration', ck.has_short_leg ? evCheck(ev.ex_dividend) : 'No short leg'],
     ['Order size vs. open interest', m <= 0.1 * ck.min_leg_open_interest ? 'Within 10%' : 'Above 10%'], ['Contracts', String(q)]]
      .forEach(function (r) { var k = h('div', 'okv'); k.appendChild(h('span', '', r[0])); k.appendChild(h('span', '', r[1])); b.appendChild(k); });
    if (c.levels_sentence) { b.appendChild(h('h4', '', 'Support and resistance')); b.appendChild(h('p', 'sub', c.levels_sentence + ' Context only.')); }
    var o = h('div', 'oth'), oc = c.other_construction; o.appendChild(h('strong', '', 'Equivalent construction. '));
    o.appendChild(document.createTextNode(!oc ? (c.legs.length === 1 ? 'A single leg has one construction.' : 'An iron condor has one construction.')
      : !oc.available ? 'Not available at these strikes.'
      : oc.name + ', has the same payoff. Est. slippage ' + usd(oc.cost.dollars) + ' per contract, ' + pct1(oc.cost.pct_of_risk) + ' of max loss. Not kept: ' + (oc.cost.dollars > c.cost.dollars ? 'it costs more to trade.' : 'it does not cost less to trade.')));
    b.appendChild(o);
    d.appendChild(a); d.appendChild(b); return d;
  }

  function candRow(c, i, x, ro, ranked) {
    var p = x.priority, exp = x.expiry_chosen, open = o3.open === c.id;
    var box = h('div', 'ocand' + (ranked && i === 0 ? ' rec' : '') + (open ? ' open' : '')), r = h('div', 'orow');
    var q = qty(c), m = Math.max(q, 1);
    r.appendChild(h('span', 'v rk', ranked ? String(i + 1) : ''));
    var nm = h('span', 'nm', c.name); nm.setAttribute('data-rank', ranked ? i + 1 : 'Filtered'); r.appendChild(nm);
    if (!ranked) { var fl = h('span', 'chip un rk', 'FILTERED'); fl.style.marginLeft = '8px'; nm.appendChild(fl); }   // no rank: a label, not a number
    [['Max loss', usd(c.max_loss * m)], ['Max profit', c.max_gain == null ? 'Unlimited' : usd(c.max_gain * m)], ['Breakeven', c.break_even.map(px).join(' / ')],
     ['Profitable if thesis holds', pct(c.pays_when_view_right.pct)], ['POP: historical / implied', pct(c.base_rate_profit.pct) + ' / ' + pct(c.implied_profit.pct)],
     ['Est. slippage', usd(c.cost.dollars * m) + ' · ' + pct1(c.cost.pct_of_risk)], ['Contracts', String(q)]]
      .forEach(function (v) { var e = h('span', 'v', v[1]); e.setAttribute('data-l', v[0]); r.appendChild(e); });
    var bt = h('button', '', open ? 'Hide ▴' : 'Detail ▾'); bt.type = 'button'; bt.setAttribute('aria-expanded', open ? 'true' : 'false'); bt.setAttribute('aria-label', (open ? 'Hide detail of ' : 'Show detail of ') + c.name);
    bt.addEventListener('click', function () { o3.open = open ? null : c.id; renderContracts(ro); });
    r.appendChild(bt);
    var why = !ranked ? 'Filtered out: ' + c.removed_reason
      : q === 0 ? 'No contracts fit: one contract risks ' + usd(c.max_loss) + ', above the figure entered. Figures shown are for one contract.'
      : p === 'payoff' ? (i === 0 ? 'Best fit: returns ' : 'Returns ') + c.reward_sentence
      : i === 0 ? 'Best fit: ' + c.best_fit_reason + '.' : c.need;
    var marks = [];
    if (c.checks.earnings_before_expiration) marks.push('Earnings report before expiration (' + dm(x.events.earnings.date) + ').');
    if (c.checks.ex_dividend_before_expiration_short_leg) marks.push('Ex-dividend date before expiration, with a short leg (' + dm(x.events.ex_dividend.date) + ').');
    r.appendChild(h('span', 'why1', why + (marks.length ? ' ' + marks.join(' ') : '')));
    box.appendChild(r); if (open) box.appendChild(detail(c, x)); return box;
  }

  function renderContracts(ro) {
    var v = st.view, s = v.state, x = s.contracts, acts = clear('#s3Actions');
    document.querySelectorAll('[data-s="s3"] [data-review]').forEach(function (e) { e.classList.toggle('on', ro); });
    if (o3.rid !== v.request_id) o3 = {rid: v.request_id, open: '__top', cap: null, exp: null};
    var mine = !!s.user_thesis, view = s.view, d = DIR[view] || DIR.no_view;
    var days = mine ? s.user_thesis.primary_horizon_days : (x && x.thesis_horizon_days) || (s.thesis || {}).primary_horizon_days;
    $('#cTk').textContent = v.symbol;
    var dir = clear('#cDir'); dir.appendChild(h('span', 'chip dir ' + d[1], d[0]));
    var kind = mine ? 'Your thesis' : view === 'range_bound' ? 'Range-bound thesis' : 'Directional thesis';
    var show = function (q, on) { $(q).hidden = !on; };
    var waiting = !x;
    $('#cHead').textContent = kind + ', ' + days + '-day horizon' + (x && x.spot ? ' · spot ' + px(x.spot) + ' · quotes ' + hm(x.as_of) + ' ET' + (x.provisional ? ', ' + dayMonth(x.as_of) : ', ' + srcName(x)) : '');
    show('#cProv', x && x.provisional); show('#cProvLine', x && x.provisional);
    if (x && x.provisional) $('#cProvLine').textContent = 'Snapshot of ' + dayMonth(x.as_of) + ', ' + hm(x.as_of) + ' ET · ' + (x.live_failed ? 'live quotes unavailable from Cboe and Tradier' : 'market closed') + '. Provisional: every figure is from the latest snapshot, not from live quotes.';
    var chosen = x && (x.expiry_options || []).filter(function (o) { return o.selected; })[0];
    show('#cMove', !!(x && chosen && x.typical_move_pct));
    if (x && chosen && x.typical_move_pct) $('#cMove').textContent = (x.implied_move_pct != null ? 'Implied move ±' + x.implied_move_pct + '% to the ' + dm(chosen.expiration) + ' expiration. ' : 'Implied move to the ' + dm(chosen.expiration) + ' expiration: not available. ') + 'The typical realized move over that period is ±' + x.typical_move_pct + '%.';
    var outcome = waiting ? 'waiting' : x.outcome, ok = outcome === 'ok';
    var hasStrip = !!(x && (x.expiry_options || []).length);
    show('#cStrip', hasStrip); show('#cMain', ok); show('#cOut', !!x && (ok || (outcome === 'no_candidates' && ((x.filtered_out || []).length + (x.not_built || []).length) > 0))); show('#cLabels', ok);
    show('#cMsg', !ok); show('#cMsg2', false);
    if (waiting) $('#cMsg').textContent = 'Opening the option chain (Cboe, then Tradier, then the latest snapshot) and building the candidates.';
    else if (!ok) {
      clear('#cMsg').appendChild(h('strong', '', outcome === 'source_failed' ? 'The option data could not be retrieved.' : x.message));
      var more = outcome === 'source_failed' ? 'Source that failed: ' + (x.failed_source || 'not known') + '. ' + x.message
        : outcome === 'market_closed' ? 'This is consistent with what stage 1 showed: ' + v.symbol + ' is not in the daily snapshot, so its liquidity could not be judged either.'
        : (x.filtered_out || []).length ? 'Raising the cost cap, or switching expiration, rebuilds the candidates.' : hasStrip ? 'Switching expiration rebuilds the candidates.' : '';
      show('#cMsg2', !!more); $('#cMsg2').textContent = more;
    }
    if (hasStrip) {
      var ex = clear('#cExps');
      x.expiry_options.forEach(function (o) {
        var c = h(o.selected || ro ? 'div' : 'button', 'exp' + (o.selected ? ' on' : '')), top = h('div');
        if (!o.selected && !ro) { c.type = 'button'; c.style.cssText = 'font:inherit;color:inherit;background:none;text-align:left;cursor:pointer;display:flex;flex-direction:column;justify-content:flex-start;align-items:stretch'; c.addEventListener('click', function () { o3.open = '__top'; act('update', {params: s3Params({expiration: o.expiration})}); }); }
        top.appendChild(h('b', '', dm(o.expiration))); top.appendChild(h('span', 'mono', o.dte + ' DTE')); c.appendChild(top);
        var many = o.horizons_served.length > 1;
        c.appendChild(h('p', '', 'Matches ' + horizons(o.horizons_served) + ' · ' + (o.days_beyond === 0 ? 'on the horizon date' : days_(Math.abs(o.days_beyond)) + (o.days_beyond < 0 ? ' before ' : ' beyond ') + (many ? 'the ' + o.serves_days + '-day horizon' : 'it'))));
        var sm = h('small', '', o.selected ? (o.from_thesis ? 'From the thesis · selected' : 'Selected · horizon amended to ' + x.horizon_amendment.to_days + ' days') : o.from_thesis ? 'From the thesis · switch back to this expiration' : 'Switch to this expiration');
        c.appendChild(sm);
        if (o.poor_match) { var pm = h('small'); pm.style.color = 'var(--ink)'; pm.appendChild(h('strong', '', 'Poor match.')); pm.appendChild(document.createTextNode(' Figures assume holding to expiration. Your thesis covers the first ' + o.serves_days + ' days; closing then will give a different result.')); c.appendChild(pm); }
        ex.appendChild(c);
      });
      show('#cEvents', !!chosen);
      if (chosen) $('#cEvents').textContent = eventText(x.events.earnings, chosen.expiration, 'Next earnings report') + '. ' + eventText(x.events.ex_dividend, chosen.expiration, 'Next ex-dividend date') + '.';
    }
    if (x && x.filters) {                         // the cost-cap control: shown whenever candidates were built, so a cap that filters everything can be loosened
      var cc = $('#cCap'), cap = x.filters.cost_cap_pct;
      show('#cMain', ok || outcome === 'no_candidates' && (x.filtered_out || []).length > 0);
      show('#orows', ok); document.querySelector('[data-s="s3"] .mxl').hidden = !ok; $('#segPri').parentNode.hidden = !ok;
      cc.disabled = ro; if (document.activeElement !== cc) cc.value = cap;
      $('#oCap').textContent = cc.value + '% of max loss';
      $('#capDef').textContent = 'default ' + x.filters.cost_cap_default_pct + '%';
      $('#oCap').style.color = cap !== x.filters.cost_cap_default_pct ? 'var(--accent)' : '';
    }
    var pick = null;
    if (ok) {
      var order = x.candidates;
      if (o3.open === '__top' || (o3.open && !order.concat(x.filtered_out).some(function (c) { return c.id === o3.open; }))) o3.open = order[0].id;
      pick = order.filter(function (c) { return c.id === o3.open; })[0] || order[0];
      if (ro && s.selection) { pick = order.filter(function (c) { return c.id === s.selection.id; })[0] || pick; }
      var pi = PRI.map(function (p) { return p[0]; }).indexOf(x.priority), p = PRI[pi];
      var host = clear('#orows'), hd = h('div', 'ohead');
      HEAD.forEach(function (t, i) { hd.appendChild(h('span', i === p[2] + 2 ? 'hl' : '', t + (i === p[2] + 2 ? ' ▾' : ''))); }); host.appendChild(hd);
      order.forEach(function (c, i) { host.appendChild(candRow(c, i, x, ro, true)); });
      var seg = clear('#segPri');
      PRI.forEach(function (P, i) { var b = h('button', '', P[1]); b.type = 'button'; b.disabled = ro; b.setAttribute('aria-pressed', i === pi ? 'true' : 'false'); b.addEventListener('click', function () { if (i === pi) return; o3.open = '__top'; act('update', {params: s3Params({priority: P[0]})}); }); seg.appendChild(b); });
      var inp = $('#mxl'); inp.disabled = ro;
      if (document.activeElement !== inp) { o3.cap = x.max_loss_for_trade || null; inp.value = o3.cap == null ? '' : String(Math.round(o3.cap)); }
      $('#mxlNote').textContent = o3.cap == null ? 'Every candidate is shown for one contract.' : 'Contracts, max loss, max profit and slippage are resized to fit ' + usd(o3.cap) + '.';
    }
    if (x && (ok || outcome === 'no_candidates')) {
      var f = clear('#cFiltered'), out = x.filtered_out || [], nb = x.not_built || [];
      f.appendChild(h('strong', '', 'Filtered out: ' + (out.length ? out.length : 'none') + '.'));
      f.appendChild(document.createTextNode(out.length ? ' Each is listed below with the reason. It can be opened and cannot be selected.' : ' A candidate removed by a filter is listed here with the reason.'));
      if (nb.length) f.appendChild(document.createTextNode(' Not built: ' + nb.map(function (n) { return n.name.toLowerCase() + ' (' + n.reason + ')'; }).join('; ') + '.'));
      f.appendChild(document.createTextNode(' The top-ranked candidate is the best fit on the chosen ranking, not a recommendation to trade.'));
      var oh = clear('#orowsOut'); oh.hidden = !out.length;
      out.forEach(function (c, i) { oh.appendChild(candRow(c, i, x, ro, false)); });
    }
    var a = (v.pause && v.pause.pause === 'contracts') ? v.pause.actions : [];
    if (!ro && a.indexOf('retry') > -1) btn2(acts, 'Retry', '', function () { act('retry'); });
    btn2(acts, 'Stop', ok ? '' : 'pri', function () { act('stop'); }, ro || waiting);
    if (ok) btn2(acts, 'Continue to the challenge with the ' + shortName(pick), 'pri', function () { act('continue', {selection: {id: pick.id, contracts: qty(pick)}}); }, ro);
  }
  // The live source that answered: Cboe (15-minute delayed) or, when Cboe failed, Tradier.
  function srcName(o) { return o && o.provider === 'Tradier' ? 'Tradier, real-time quotes' : 'Cboe, 15-minute delayed quotes'; }
  function srcNote(o) { return o && o.provider === 'Tradier' && o.provider_fell_back ? ' Cboe could not be reached, so the quotes are from Tradier.' : ''; }
  function days_(n) { return n + (n === 1 ? ' day' : ' days'); }
  $('#mxl').addEventListener('input', function () {
    var n = parseFloat(this.value.replace(/[^0-9.]/g, ''));
    o3.cap = isFinite(n) && n > 0 ? n : null;
    renderContracts(false);
  });
  $('#cCap').addEventListener('input', function () { $('#oCap').textContent = this.value + '% of max loss'; });
  $('#cCap').addEventListener('change', function () {        // applied, and recorded, when the slider is released
    var was = ((st.view.state.contracts || {}).filters || {}).cost_cap_pct;
    if (+this.value !== was) { o3.open = '__top'; this.blur(); act('update', {params: s3Params({cost_cap_pct: +this.value})}); }
  });
  $('#mxl').addEventListener('change', function () {           // recorded when the field loses focus, not on each keystroke
    var was = (st.view.state.contracts || {}).max_loss_for_trade || null;
    if (o3.cap !== was) act('update', {params: s3Params({max_loss: o3.cap})});
  });

  // ---- stage 4: the challenge ----------------------------------------------------------
  var CHIP4 = {flagged: ['fl', 'FLAG'], not_checked: ['un', 'N/C'], not_applicable: ['', 'N/A'], passed: ['ok', 'PASS']};
  var STANDING = {holds: 'HOLDS', holds_in_a_narrower_form: 'NARROWER', does_not_hold: 'DOES NOT HOLD'};
  var o4 = {rid: null, more: false};
  function list4(ids, one, many) { return ids.length ? (ids.length === 1 ? one : many) + ' ' + ids.join(', ') : ''; }
  // What an objection or a loss path rests on, as the mock-up labels it: "THESIS CHECK 2 · CLAIMS 1, 2".
  function grounds(ids) {
    var t = [], c = [], cl = [], p = [], f = [], u = [];
    (ids || []).forEach(function (i) {
      var m = /^(CL|T|C|P|U)(\d+)$/.exec(i);
      if (!m) { f.push(i); return; }
      ({T: t, C: c, CL: cl, P: p, U: u})[m[1]].push(m[1] === 'P' ? i : m[2]);
    });
    return [list4(t, 'THESIS CHECK', 'THESIS CHECKS'), list4(c, 'CONTRACT CHECK', 'CONTRACT CHECKS'), list4(cl, 'CLAIM', 'CLAIMS'),
      list4(p, 'RESEARCH PASSAGE', 'RESEARCH PASSAGES'), list4(f, 'FINDING', 'FINDINGS'), u.length ? 'MISSING INPUT' : ''].filter(Boolean).join(' · ');
  }
  function cbox(title) { var b = h('div', 'cbox'); b.appendChild(h('h4', '', title)); return b; }
  function cline(strong, text, small, cls) { var d = h('div', 'cline' + (cls ? ' ' + cls : '')); if (strong) d.appendChild(h('b', '', strong)); if (text) d.appendChild(document.createTextNode((strong ? ' ' : '') + text)); if (small) d.appendChild(h('small', '', small)); return d; }
  function checkRow(res, name, detail) { var d = h('div', 'cline chk2'); d.appendChild(chip(CHIP4[res][0], CHIP4[res][1])); var x = h('div'); x.appendChild(h('b', '', name)); x.appendChild(h('span', '', detail)); d.appendChild(x); return d; }
  function checksBox(q, title, checks, ro) {
    var box = clear(q), n = {flagged: 0, not_checked: 0, not_applicable: 0, passed: 0};
    checks.forEach(function (c) { n[c.result]++; });
    var head = h('div', 'chead'); head.appendChild(h('h4', '', title));
    head.appendChild(h('span', 'mono', [n.flagged + ' flagged', n.not_checked + ' not checked', n.not_applicable ? n.not_applicable + ' not applicable' : '', n.passed + ' passed'].filter(Boolean).join(' · ')));
    box.appendChild(head);
    // Flagged and could-not-be-checked results are open; a line with a different result inside a check is its own row, uncounted.
    ['flagged', 'not_checked'].forEach(function (r) {
      checks.filter(function (c) { return c.result === r; }).forEach(function (c) {
        box.appendChild(checkRow(r, c.name, c.detail));
        if (r === 'flagged') (c.lines || []).filter(function (l) { return l.result === 'not_checked'; }).forEach(function (l) { box.appendChild(checkRow('not_checked', l.name, l.detail)); });
      });
    });
    var rest = checks.filter(function (c) { return c.result === 'passed' || c.result === 'not_applicable'; });
    if (!rest.length) return;
    var key = q + '|' + st.view.request_id, open = !!o4[key];
    var b = h('button', 'more', n.passed + ' passed ' + (open ? '▴' : '▾')); b.type = 'button'; b.setAttribute('aria-expanded', open ? 'true' : 'false');
    var ul = h('ul', 'passed'); ul.hidden = !open;
    rest.forEach(function (c) { ul.appendChild(h('li', '', c.name + (c.result === 'not_applicable' ? ' · not applicable: ' + c.detail : c.note ? ' · note: ' + c.detail : ''))); });
    b.addEventListener('click', function () { o4[key] = !o4[key]; renderChallenge(ro); });
    box.appendChild(b); box.appendChild(ul);
  }
  function renderChallenge(ro) {
    var v = st.view, s = v.state, sel = s.selection || {}, c = sel.candidate || {}, L = s.checklists || {thesis: [], contract: []};
    var R = s.readiness || {}, K = s.critic, P = s.passages || {}, mine = !!s.user_thesis, d = DIR[s.view] || DIR.no_view;
    document.querySelectorAll('[data-s="s4"] [data-review]').forEach(function (e) { e.classList.toggle('on', ro); });
    $('#chTk').textContent = v.symbol;
    clear('#chDir').appendChild(h('span', 'chip dir ' + d[1], d[0]));
    var q = Math.max(sel.contracts_proposed || 1, 1), nm = c.name || '';
    $('#chFor').textContent = (mine ? 'Your thesis, ' : '') + L.horizon_days + '-day horizon · ' + nm.charAt(0).toLowerCase() + nm.slice(1) + ', exp. ' + dm(c.expiry) + ' · ' + q + (q === 1 ? ' contract' : ' contracts');
    var ready = R.label === 'Ready', ch = $('#chChip');
    ch.className = 'chip ' + (ready ? 'ok' : 'fl'); ch.textContent = ready ? 'READY' : 'NOT READY';
    $('#chReady').textContent = R.headline || ''; $('#chReadySub').textContent = R.sentence || '';
    $('#chCaution').hidden = !(K && K.same_family_as_thesis_agent);
    var np = $('#chNoPass'); np.hidden = !(K && P.retrieved === false);
    if (!np.hidden) np.textContent = 'No research passages were retrieved' + (P.reason ? ': ' + P.reason : '') + '. The critic worked from the checklists and the thesis record alone.';

    var left = clear('#chLeft'); left.appendChild(h('span', 'collab', 'THE CRITIC · JUDGEMENT'));
    if (!K) {
      var un = s.critic_unavailable || {};
      var box = h('div', 'cbox'); box.appendChild(h('p', '', un.kind === 'rejected' ? un.reason : "The critic's output is not available: " + (un.reason || 'the critic did not run.') + ' This screen shows the fixed-rule checks alone.')); box.firstChild.style.marginTop = '0';
      left.appendChild(box);
    } else {
      var names = s.view === 'bullish' ? ['Bull case', 'Bear case'] : s.view === 'bearish' ? ['Bear case', 'Bull case'] : ['Case for', 'Case against'];
      [[names[0], K.case_for], [names[1], K.case_against]].forEach(function (x) { var b = cbox(x[0]); b.appendChild(h('p', '', x[1])); left.appendChild(b); });
      var lose = cbox('How this trade loses');
      (K.loss_paths || []).forEach(function (p) { lose.appendChild(cline(p.title.replace(/\.?$/, '.'), p.text)); });
      left.appendChild(lose);
      var ob = cbox('Objections, most serious first');
      (K.objections || []).forEach(function (o, i) {
        var r = h('div', 'cline obj'); r.appendChild(h('span', 'mono', String(i + 1)));
        var x = h('div'); x.appendChild(h('b', '', o.title.replace(/\.?$/, '.'))); x.appendChild(document.createTextNode(' ' + o.text)); x.appendChild(h('small', '', grounds(o.grounds))); r.appendChild(x); ob.appendChild(r);
      });
      if (!(K.objections || []).length) ob.appendChild(cline('', 'None raised. With clean checks and nothing found against, the critic may concede.'));
      left.appendChild(ob);
    }
    checksBox('#chThesis', 'Thesis', L.thesis, ro);
    checksBox('#chContract', 'Contract', L.contract, ro);

    var acts = clear('#s4Actions'), a = (v.pause && v.pause.pause === 'challenge') ? v.pause.actions : [];
    btn2(acts, 'Proceed to decision', 'pri', function () { act('proceed'); }, ro || a.indexOf('proceed') < 0);
    btn2(acts, 'Return to contracts', '', function () { act('return'); }, ro || a.indexOf('return') < 0);
    btn2(acts, 'Stop', '', function () { act('stop'); }, ro || a.indexOf('stop') < 0);

    // More detail, on request (one fold): each claim's standing, the priced-in reading, what is missing, the passages cited.
    if (o4.rid !== v.request_id) { o4.rid = v.request_id; o4.more = false; }
    var mb = $('#chMore'), wrap = $('#chDetailWrap'), label = "More detail: each claim's standing, the priced-in reading, what is missing, the passages cited";
    mb.hidden = !K; wrap.hidden = !K || !o4.more;
    mb.textContent = label + ' ' + (o4.more ? '▴' : '▾'); mb.setAttribute('aria-expanded', o4.more ? 'true' : 'false');
    mb.onclick = function () { o4.more = !o4.more; renderChallenge(ro); };
    var det = clear('#chDetail');
    if (!K) return;
    var claims = (s.question || {}).claims || [], byId = {}; claims.forEach(function (x) { byId[x.id] = x; });
    var b1 = cbox("Each claim's standing");
    (K.dispositions || []).forEach(function (x) { var cl = byId[x.claim_id] || {}; b1.appendChild(checkRow2(STANDING[x.standing] || x.standing, 'Claim ' + (cl.n || '') + '. ' + (cl.text || ''), x.reason)); });
    det.appendChild(b1);
    var b2 = cbox('The priced-in reading'), figs = K.priced_in_figures || {}, read = {};
    (K.priced_in || []).forEach(function (x) { read[x.claim_id] = x.reading; });
    claims.forEach(function (cl) {
      var f = figs[cl.id] || {};
      var fig = f.pct == null ? 'No figure: the price move since this finding became public could not be measured.' : (f.pct >= 0 ? 'Up ' : 'Down ') + Math.abs(f.pct) + '% since ' + dm(f.since) + (f.typical_moves != null ? ', ' + f.typical_moves + ' of a typical realized move for ' + f.horizon_days + ' days.' : '.');
      b2.appendChild(cline('Claim ' + cl.n + '.', fig + (read[cl.id] ? ' ' + read[cl.id] : ''), 'FIGURE SET BY CODE' + (read[cl.id] ? ' · READING BY THE CRITIC' : '')));
    });
    det.appendChild(b2);
    var b3 = cbox('What is missing'), un2 = K.unavailable || {};
    (K.missing || []).forEach(function (m) { b3.appendChild(cline(words(un2[m.ref] || m.ref).replace(/\.?$/, '.'), m.why_it_matters, 'RECORDED AS UNAVAILABLE IN THE THESIS STAGE')); });
    if (!(K.missing || []).length) b3.appendChild(cline('', 'The critic named nothing from the inputs recorded as unavailable.'));
    det.appendChild(b3);
    var b4 = cbox('Research passages cited'), side = {};
    (P.topics || []).forEach(function (t) { t['for'].forEach(function (r) { side[r] = 'for'; }); t.against.forEach(function (r) { side[r] = 'against'; }); });
    Object.keys(P.passages || {}).forEach(function (r) {
      var p = P.passages[r], txt = p.text.replace(/\s+/g, ' ').replace(/\*\*/g, '');
      b4.appendChild(cline(r + ' · ' + (side[r] || '') + '.', txt.length > 320 ? txt.slice(0, 320) + '…' : txt, (p.source.replace(/\.md$/, '') + ' · ' + p.section + ' · ' + (p.grade === 'ungraded' ? 'ungraded' : 'evidence strength: ' + p.grade)).toUpperCase()));
    });
    if (!Object.keys(P.passages || {}).length) b4.appendChild(cline('', 'No research passages were retrieved.'));
    det.appendChild(b4);
  }
  function checkRow2(label, name, detail) { var d = h('div', 'cline chk2'); d.appendChild(chip('', label)); var x = h('div'); x.appendChild(h('b', '', name)); x.appendChild(h('span', '', detail)); d.appendChild(x); return d; }
  $('#endHome').addEventListener('click', function () { st.view = null; st.ended = false; loadHome(); });

  // ---- leaving an open request (Home or the product name) ------------------------------
  function hideLeave() { $('#leave').classList.remove('on'); }
  function goHome() { if (st.view && !st.ended) { $('#leave').classList.add('on'); $('#leaveStay').focus(); window.scrollTo(0, 0); } else { loadHome(); } }
  $('#brand').addEventListener('click', goHome);
  $('#navHome').addEventListener('click', goHome);
  $('#leaveStay').addEventListener('click', hideLeave);
  $('#leaveGo').addEventListener('click', function () {
    if (st.busy || !st.view) return; busy(true);
    api('/api/requests/' + st.view.request_id + '/leave', {}).then(function () { busy(false); setView(null); })
      .catch(function (e) { busy(false); hideLeave(); $('#appMsg').textContent = e.message; });
  });

  // ---- start --------------------------------------------------------------------------
  api('/api/symbols').then(function (d) { SYMS = d.symbols; (d.daily || []).forEach(function (s) { DAILY[s] = true; }); }).catch(function () { $('#askMsg').textContent = 'The symbol list could not be loaded.'; });
  loadHome();
})();
