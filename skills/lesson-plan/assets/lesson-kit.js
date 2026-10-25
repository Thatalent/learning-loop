/* Lesson Kit: config-driven interactive learning activities for frontend-slides decks.
 * Paste this whole file into a <script> tag in the lesson. Each activity takes a container
 * element and a plain-data config, so a lesson only has to supply content, never new logic.
 *
 * Every activity: keyboard accessible (no drag-only interactions), immediate feedback with an
 * explanation, a hint before the answer, retry, and a record in Kit.results for the summary slide.
 *
 *   Kit.sequence(el, {id, level, prompt, items:[...in correct order], explain})
 *   Kit.sort(el, {id, level, prompt, buckets:[...], items:[{text, bucket}], explain})
 *   Kit.hotspots(el, {id, level, prompt, svg, spots:[{x, y, label, text}], quiz:[{ask, spot}]})
 *   Kit.simulate(el, {id, level, prompt, controls:[...], render(state) -> html, goal:{ask, check(state), success}})
 *   Kit.spot(el, {id, level, prompt, lines:[...], bug, hint, explain, prose})   prose:true for emails, policies, plans
 *   Kit.branch(el, {id, level, prompt, start, nodes:{key:{text, choices:[{label, next, feedback, good}]} | {text, end:true, good}}})
 *   Kit.estimate(el, {id, level, prompt, min, max, step, answer, tolerance, unit, explain})
 *   Kit.fade(el, {id, level, prompt, steps:[{text} | {before, after, accept:[...], placeholder}], explain})
 *   Kit.predict(el, {id, level, prompt, options:[...], answer, reveal})
 *   Kit.summary(el, {levels:[...], next:{Remember:'…', ...}})
 */
const Kit = (() => {
  const LEVELS = ['Remember', 'Understand', 'Apply', 'Analyze', 'Evaluate', 'Create'];
  const results = {};        // id -> {level, label, ok, tries}
  const listeners = [];
  let store = null;
  try { store = window.localStorage; } catch (e) { store = null; }
  const KEY = 'lesson-kit:' + (document.title || location.pathname);
  try { Object.assign(results, JSON.parse((store && store.getItem(KEY)) || '{}')); } catch (e) {}

  const esc = s => String(s).replace(/[&<>"]/g, c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));
  const h = (tag, attrs = {}, html = '') => { const e = document.createElement(tag); for (const k in attrs) e.setAttribute(k, attrs[k]); e.innerHTML = html; return e; };
  const shuffle = (a, keepFrom) => { const b = a.slice(); for (let t = 0; t < 20; t++) { for (let i = b.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [b[i], b[j]] = [b[j], b[i]]; } if (!keepFrom || b.some((x, i) => x !== keepFrom[i])) break; } return b; };

  function record(cfg, ok) {
    const r = results[cfg.id] || { level: cfg.level || 'Understand', label: cfg.label || cfg.prompt || cfg.id, ok: false, tries: 0 };
    r.tries += 1; if (ok) r.ok = true; r.level = cfg.level || r.level; r.label = cfg.label || r.label;
    results[cfg.id] = r;
    try { store && store.setItem(KEY, JSON.stringify(results)); } catch (e) {}
    listeners.forEach(f => f(results));
  }
  function shell(el, cfg, kind) {
    el.classList.add('kit', 'kit-' + kind);
    el.innerHTML = '';
    if (cfg.prompt) el.appendChild(h('p', { class: 'kit-prompt' }, esc(cfg.prompt)));
    const body = h('div', { class: 'kit-body' });
    const bar = h('div', { class: 'kit-bar' });
    const fb = h('div', { class: 'kit-feedback', role: 'status', 'aria-live': 'polite' });
    el.append(body, bar, fb);
    return { body, bar, fb };
  }
  function button(label, cls = '') { const b = h('button', { type: 'button', class: 'kit-btn ' + cls }, esc(label)); return b; }
  function say(fb, ok, msg) { fb.className = 'kit-feedback ' + (ok === true ? 'is-good' : ok === false ? 'is-bad' : 'is-info'); fb.innerHTML = msg; }

  /* ---------- Sequence (Parsons-style ordering) ---------- */
  function sequence(el, cfg) {
    const { body, bar, fb } = shell(el, cfg, 'sequence');
    let order = shuffle(cfg.items, cfg.items), revealed = false;
    const list = h('ol', { class: 'kit-seq' });
    body.appendChild(list);
    const draw = (focusIdx) => {
      list.innerHTML = '';
      order.forEach((t, i) => {
        const li = h('li', { class: 'kit-seq-item', draggable: 'true' });
        li.innerHTML = `<span class="kit-seq-text">${esc(t)}</span>`;
        const up = button('↑', 'kit-icon'); up.setAttribute('aria-label', 'Move up: ' + t); up.disabled = i === 0;
        const dn = button('↓', 'kit-icon'); dn.setAttribute('aria-label', 'Move down: ' + t); dn.disabled = i === order.length - 1;
        up.onclick = () => { [order[i - 1], order[i]] = [order[i], order[i - 1]]; draw(i - 1); };
        dn.onclick = () => { [order[i + 1], order[i]] = [order[i], order[i + 1]]; draw(i + 1); };
        li.addEventListener('dragstart', e => { e.dataTransfer.setData('text/plain', String(i)); li.classList.add('is-dragging'); });
        li.addEventListener('dragend', () => li.classList.remove('is-dragging'));
        li.addEventListener('dragover', e => e.preventDefault());
        li.addEventListener('drop', e => { e.preventDefault(); const from = +e.dataTransfer.getData('text/plain'); const [m] = order.splice(from, 1); order.splice(i, 0, m); draw(i); });
        li.append(up, dn); list.appendChild(li);
        if (focusIdx === i) (i === 0 ? dn : up).focus();
      });
    };
    draw();
    const check = button('Check order', 'kit-primary');
    check.onclick = () => {
      const wrong = order.map((t, i) => t !== cfg.items[i]);
      [...list.children].forEach((li, i) => li.classList.toggle('is-wrong', wrong[i]));
      const ok = !wrong.some(Boolean) && !revealed; record(cfg, ok);
      if (revealed) { say(fb, null, '<b>The answer was shown</b>, so this one counts as practice. Come back to it later and try it cold.'); return; }
      say(fb, ok, ok ? `<b>Correct.</b> ${esc(cfg.explain || '')}` : `<b>${wrong.filter(Boolean).length} step(s) are out of place</b> (marked). Think about what each step needs to exist before it can run.`);
    };
    const reveal = button('Show answer', 'kit-ghost');
    reveal.onclick = () => { revealed = true; order = cfg.items.slice(); draw(); say(fb, null, `<b>The order:</b> ${esc(cfg.explain || '')}`); };
    bar.append(check, reveal);
  }

  /* ---------- Sort into buckets (classification) ---------- */
  function sort(el, cfg) {
    const { body, bar, fb } = shell(el, cfg, 'sort');
    const placed = {}; let picked = null;
    const pool = h('div', { class: 'kit-pool' });
    const zones = h('div', { class: 'kit-buckets' });
    body.append(pool, zones);
    const items = shuffle(cfg.items.map((it, i) => ({ ...it, i })));
    const draw = () => {
      pool.innerHTML = ''; zones.innerHTML = '';
      items.filter(it => placed[it.i] == null).forEach(it => {
        const b = button(it.text, 'kit-chip' + (picked === it.i ? ' is-picked' : ''));
        b.setAttribute('aria-pressed', picked === it.i); b.draggable = true;
        b.onclick = () => { picked = picked === it.i ? null : it.i; draw(); };
        b.addEventListener('dragstart', e => e.dataTransfer.setData('text/plain', String(it.i)));
        pool.appendChild(b);
      });
      if (!pool.children.length) pool.appendChild(h('span', { class: 'kit-muted' }, 'All placed. Check your sort.'));
      cfg.buckets.forEach((name, bi) => {
        const z = h('div', { class: 'kit-bucket' });
        const head = button(name + (picked != null ? '  ← place here' : ''), 'kit-bucket-head');
        head.onclick = () => { if (picked != null) { placed[picked] = bi; picked = null; draw(); } };
        z.addEventListener('dragover', e => e.preventDefault());
        z.addEventListener('drop', e => { e.preventDefault(); placed[+e.dataTransfer.getData('text/plain')] = bi; picked = null; draw(); });
        z.appendChild(head);
        items.filter(it => placed[it.i] === bi).forEach(it => {
          const c = button(it.text + ' ✕', 'kit-chip is-placed'); c.dataset.i = it.i;
          c.setAttribute('aria-label', 'Remove ' + it.text + ' from ' + name);
          c.onclick = () => { delete placed[it.i]; draw(); };
          z.appendChild(c);
        });
        zones.appendChild(z);
      });
    };
    draw();
    const check = button('Check sort', 'kit-primary');
    check.onclick = () => {
      if (Object.keys(placed).length < items.length) { say(fb, null, 'Place every card first.'); return; }
      let wrong = 0;
      zones.querySelectorAll('.is-placed').forEach(c => { const it = cfg.items[+c.dataset.i]; const bad = cfg.buckets[placed[+c.dataset.i]] !== it.bucket; c.classList.toggle('is-wrong', bad); wrong += bad; });
      const ok = wrong === 0; record(cfg, ok);
      say(fb, ok, ok ? `<b>All sorted correctly.</b> ${esc(cfg.explain || '')}` : `<b>${wrong} card(s) are in the wrong group</b> (marked). Tap a card to move it back.`);
    };
    bar.append(check);
  }

  /* ---------- Hotspots on a diagram (explore, then quiz) ---------- */
  function hotspots(el, cfg) {
    const { body, bar, fb } = shell(el, cfg, 'hotspots');
    const stage = h('div', { class: 'kit-hs-stage' }, cfg.svg);
    body.appendChild(stage);
    let mode = 'explore', q = 0;
    const seen = new Set();
    cfg.spots.forEach((s, i) => {
      const b = button(String(i + 1), 'kit-hs-dot'); b.style.left = s.x + '%'; b.style.top = s.y + '%';
      b.setAttribute('aria-label', mode === 'explore' ? s.label : 'Spot ' + (i + 1));
      b.onclick = () => {
        if (mode === 'explore') { seen.add(i); b.classList.add('is-seen'); say(fb, null, `<b>${esc(s.label)}.</b> ${esc(s.text)}`); if (seen.size === cfg.spots.length && cfg.quiz) quizBtn.disabled = false; return; }
        const want = cfg.quiz[q].spot, ok = i === want; record({ ...cfg, id: cfg.id + ':' + q, label: cfg.quiz[q].ask }, ok);
        if (ok) { q++; say(fb, true, q < cfg.quiz.length ? `<b>Yes.</b> Next: ${esc(cfg.quiz[q].ask)}` : '<b>All found.</b> You can name every part of this system.'); if (q >= cfg.quiz.length) { mode = 'done'; record(cfg, true); } }
        else say(fb, false, `<b>Not that one</b> (that's ${esc(s.label)}). Try again: ${esc(cfg.quiz[q].ask)}`);
      };
      stage.appendChild(b);
    });
    say(fb, null, `Tap each numbered spot to explore (${cfg.spots.length}).`);
    const quizBtn = button('Quiz me on it', 'kit-primary'); quizBtn.disabled = !!cfg.quiz;
    quizBtn.onclick = () => { mode = 'quiz'; q = 0; stage.querySelectorAll('.kit-hs-dot').forEach(d => d.setAttribute('aria-label', 'Spot ' + d.textContent)); say(fb, null, `<b>Find it:</b> ${esc(cfg.quiz[0].ask)}`); };
    if (cfg.quiz) bar.append(quizBtn);
  }

  /* ---------- Simulation (explorable explanation with a goal) ---------- */
  function simulate(el, cfg) {
    const { body, bar, fb } = shell(el, cfg, 'simulate');
    const state = {}; const ctr = h('div', { class: 'kit-sim-controls' }); const view = h('div', { class: 'kit-sim-view' });
    body.append(ctr, view);
    cfg.controls.forEach(c => {
      state[c.key] = c.value;
      const row = h('label', { class: 'kit-sim-row' });
      if (c.type === 'toggle') {
        const t = h('input', { type: 'checkbox' }); t.checked = !!c.value;
        t.onchange = () => { state[c.key] = t.checked; draw(); };
        row.append(t, h('span', {}, esc(c.label)));
      } else {
        const out = h('output', { class: 'kit-sim-val' });
        const r = h('input', { type: 'range', min: c.min, max: c.max, step: c.step || 1, value: c.value });
        const fmt = v => (c.format ? c.format(v) : v);
        out.textContent = fmt(c.value);
        r.oninput = () => { state[c.key] = +r.value; out.textContent = fmt(+r.value); draw(); };
        row.append(h('span', { class: 'kit-sim-label' }, esc(c.label)), r, out);
      }
      ctr.appendChild(row);
    });
    let solved = false;
    const draw = () => {
      view.innerHTML = cfg.render(state);
      if (cfg.goal && !solved && cfg.goal.check(state)) { solved = true; record(cfg, true); say(fb, true, `<b>You found it.</b> ${esc(cfg.goal.success || '')}`); }
    };
    if (cfg.goal) say(fb, null, `<b>Your goal:</b> ${esc(cfg.goal.ask)}`);
    draw();
  }

  /* ---------- Spot the bug (erroneous example) ---------- */
  function spot(el, cfg) {
    const { body, bar, fb } = shell(el, cfg, 'spot');
    const bugs = [].concat(cfg.bug); let revealed = false;
    const pre = h('div', { class: cfg.prose ? 'kit-code kit-prose' : 'kit-code', role: 'list' });
    body.appendChild(pre);
    cfg.lines.forEach((ln, i) => {
      const b = button('', 'kit-line'); b.setAttribute('role', 'listitem');
      b.innerHTML = cfg.prose ? `<span class="kit-ln">${i + 1}</span><span class="kit-prose-text">${esc(ln) || '&nbsp;'}</span>` : `<span class="kit-ln">${i + 1}</span><code>${esc(ln) || '&nbsp;'}</code>`;
      b.onclick = () => {
        const ok = bugs.includes(i) && !revealed; record(cfg, ok); b.classList.add(bugs.includes(i) ? 'is-good' : 'is-wrong');
        if (revealed) { say(fb, null, '<b>The answer was shown</b>, so this one counts as practice. Come back to it later and try it cold.'); return; }
        say(fb, ok, ok ? `<b>${cfg.prose ? "That's the one." : "That's the bug."}</b> ${esc(cfg.explain || '')}` : `<b>${cfg.prose ? 'Sentence' : 'Line'} ${i + 1} is fine.</b> ${esc(cfg.hint || 'Look for the line whose effect reaches beyond where it is written.')}`);
      };
      pre.appendChild(b);
    });
    const reveal = button('Show me', 'kit-ghost');
    reveal.onclick = () => { revealed = true; pre.children[bugs[0]].classList.add('is-good'); say(fb, null, `<b>Line ${bugs[0] + 1}.</b> ${esc(cfg.explain || '')}`); };
    bar.append(reveal);
  }

  /* ---------- Branching scenario (decisions with consequences) ---------- */
  function branch(el, cfg) {
    const { body, bar, fb } = shell(el, cfg, 'branch');
    let path = [];
    const go = (key) => {
      const n = cfg.nodes[key]; body.innerHTML = '';
      body.appendChild(h('div', { class: 'kit-branch-text' }, esc(n.text)));
      if (n.end) {
        record(cfg, !!n.good);
        say(fb, !!n.good, (n.good ? '<b>Good outcome.</b> ' : '<b>Rough outcome.</b> ') + 'Your path: ' + path.map(esc).join(' → '));
        const again = button('Try a different path', 'kit-ghost'); again.onclick = () => { path = []; say(fb, null, ''); go(cfg.start); };
        body.appendChild(again); return;
      }
      const opts = h('div', { class: 'kit-branch-opts' });
      n.choices.forEach(c => {
        const b = button(c.label, 'kit-choice');
        b.onclick = () => { path.push(c.label); say(fb, c.good === false ? false : c.good === true ? true : null, esc(c.feedback || '')); go(c.next); };
        opts.appendChild(b);
      });
      body.appendChild(opts);
    };
    go(cfg.start);
  }

  /* ---------- Estimate (calibration slider) ---------- */
  function estimate(el, cfg) {
    const { body, bar, fb } = shell(el, cfg, 'estimate');
    const out = h('output', { class: 'kit-est-val' });
    const r = h('input', { type: 'range', min: cfg.min, max: cfg.max, step: cfg.step || 1, value: Math.round((cfg.min + cfg.max) / 2) });
    r.setAttribute('aria-label', cfg.prompt);
    const sync = () => out.textContent = `${r.value}${cfg.unit ? ' ' + cfg.unit : ''}`; r.oninput = sync; sync();
    const track = h('div', { class: 'kit-est-track' }); track.append(r);
    body.append(track, out);
    const lock = button('Lock in my estimate', 'kit-primary');
    lock.onclick = () => {
      const v = +r.value, ok = Math.abs(v - cfg.answer) <= (cfg.tolerance || 0); record(cfg, ok);
      const mark = h('div', { class: 'kit-est-answer' }); mark.style.left = ((cfg.answer - cfg.min) / (cfg.max - cfg.min) * 100) + '%'; mark.title = 'Actual';
      track.querySelectorAll('.kit-est-answer').forEach(m => m.remove()); track.appendChild(mark);
      say(fb, ok, `${ok ? '<b>Close enough.</b>' : `<b>Off by ${Math.abs(v - cfg.answer)}${cfg.unit ? ' ' + cfg.unit : ''}.</b>`} The answer is ${cfg.answer}${cfg.unit ? ' ' + cfg.unit : ''}. ${esc(cfg.explain || '')}`);
    };
    bar.append(lock);
  }

  /* ---------- Faded worked example (complete the missing steps) ---------- */
  function fade(el, cfg) {
    const { body, bar, fb } = shell(el, cfg, 'fade');
    const inputs = []; let revealed = false;
    const list = h('ol', { class: 'kit-fade' }); body.appendChild(list);
    cfg.steps.forEach(s => {
      const li = h('li');
      if (s.accept) {
        li.append(document.createTextNode(s.before || ''));
        const inp = h('input', { type: 'text', class: 'kit-fade-input', placeholder: s.placeholder || '…', 'aria-label': (s.before || '') + ' blank' });
        inp.dataset.accept = JSON.stringify(s.accept.map(a => a.toLowerCase().trim()));
        inputs.push(inp); li.append(inp, document.createTextNode(s.after || ''));
        li.classList.add('is-blank');
      } else li.textContent = s.text;
      list.appendChild(li);
    });
    const check = button('Check my steps', 'kit-primary');
    check.onclick = () => {
      let wrong = 0;
      inputs.forEach(inp => { const ok = JSON.parse(inp.dataset.accept).some(a => inp.value.toLowerCase().trim().includes(a)); inp.classList.toggle('is-wrong', !ok); inp.classList.toggle('is-good', ok); wrong += !ok; });
      const ok = wrong === 0 && !revealed; record(cfg, ok);
      if (revealed) { say(fb, null, '<b>The answer was shown</b>, so this one counts as practice. Come back to it later and try it cold.'); return; }
      say(fb, ok, ok ? `<b>All steps complete.</b> ${esc(cfg.explain || '')}` : `<b>${wrong} step(s) need another look</b> (marked).`);
    };
    const reveal = button('Show answers', 'kit-ghost');
    reveal.onclick = () => { revealed = true; inputs.forEach(inp => { inp.value = JSON.parse(inp.dataset.accept)[0]; inp.classList.add('is-good'); }); say(fb, null, esc(cfg.explain || '')); };
    bar.append(check, reveal);
  }

  /* ---------- Predict, then reveal (a guess before the explanation) ---------- */
  function predict(el, cfg) {
    const { body, bar, fb } = shell(el, cfg, 'predict');
    const opts = h('div', { class: 'kit-branch-opts' }); body.appendChild(opts);
    cfg.options.forEach((o, i) => {
      const b = button(o, 'kit-choice');
      b.onclick = () => { opts.querySelectorAll('button').forEach(x => x.disabled = true); const ok = i === cfg.answer; record(cfg, ok); b.classList.add(ok ? 'is-good' : 'is-wrong'); opts.children[cfg.answer].classList.add('is-good'); say(fb, ok, `${ok ? '<b>You predicted it.</b>' : '<b>Good guess. Guessing first makes the answer stick.</b>'} ${esc(cfg.reveal || '')}`); };
      opts.appendChild(b);
    });
  }

  /* ---------- Summary (results by Bloom level, with next steps) ---------- */
  function summary(el, cfg = {}) {
    el.classList.add('kit', 'kit-summary');
    const draw = () => {
      const rows = LEVELS.map(L => {
        const rs = Object.entries(results).filter(([id, r]) => r.level === L && !id.includes(':'));
        if (!rs.length) return '';
        const done = rs.filter(([, r]) => r.ok).length, firstTry = rs.filter(([, r]) => r.ok && r.tries === 1).length;
        const state = done === rs.length ? 'is-good' : done ? 'is-info' : 'is-bad';
        return `<tr class="${state}"><th>${L}</th><td>${done} of ${rs.length} solved${firstTry ? ` · ${firstTry} first try` : ''}</td><td>${esc((cfg.next || {})[L] || '')}</td></tr>`;
      }).join('');
      const edge = LEVELS.find(L => Object.entries(results).some(([id, r]) => r.level === L && !id.includes(':') && !r.ok));
      el.innerHTML = rows ? `<table class="kit-results"><tr><th>Level</th><th>Your result</th><th>Next step</th></tr>${rows}</table>` +
        `<p class="kit-prompt">${edge ? `Your next goal: <b>${edge}</b>. Revisit the ${edge} activity in two days, without notes.` : 'Everything solved. Teach it: write a one-page explainer for the next person.'}</p>`
        : '<p class="kit-muted">Complete the activities and your results appear here.</p>';
    };
    listeners.push(draw); draw();
  }

  function reset() { for (const k in results) delete results[k]; try { store && store.removeItem(KEY); } catch (e) {} listeners.forEach(f => f(results)); }

  return { sequence, sort, hotspots, simulate, spot, branch, estimate, fade, predict, summary, results, reset, LEVELS };
})();
