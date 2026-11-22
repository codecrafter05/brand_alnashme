/* Brand Alnashme — storefront behaviour: cart drawer, checkout, WhatsApp hand-off. */
(() => {
  'use strict';
  const ST = window.STORE, I = ST.i18n;
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const KEY = 'ban_cart_v1', PROFILE = 'ban_profile_v1';
  const esc = (s) => String(s ?? '').replace(/[&<>"']/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));
  const money = (n) => `${Number(n).toFixed(3)} ${ST.currency}`;

  /* ---------- storage (falls back to memory if blocked) ---------- */
  let mem = [];
  const store = {
    get() { try { return JSON.parse(localStorage.getItem(KEY)) || []; } catch { return mem; } },
    set(items) { mem = items; try { localStorage.setItem(KEY, JSON.stringify(items)); } catch { /* private mode */ } updateCount(); },
  };
  const count = () => store.get().reduce((a, i) => a + i.q, 0);
  function updateCount() { const n = count(); $$('[data-cart-count]').forEach((el) => { el.textContent = n; el.dataset.n = n; }); }

  /* ---------- ui helpers ---------- */
  const drawer = $('[data-drawer]'), overlay = $('[data-overlay]'), mnav = $('[data-mobile-nav]');
  let toastTimer;
  function toast(msg) {
    const el = $('[data-toast]'); el.textContent = msg; el.classList.add('on');
    clearTimeout(toastTimer); toastTimer = setTimeout(() => el.classList.remove('on'), 2200);
  }
  function lock(on) { document.body.classList.toggle('lock', on); overlay.classList.toggle('on', on); }
  function setView(name) {
    $$('[data-view]', drawer).forEach((v) => { v.hidden = v.dataset.view !== name; });
    if (name === 'checkout') refreshCheckoutTotals();
  }
  function openDrawer(view = 'cart') {
    closeMenu(); setView(view);
    drawer.classList.add('on'); drawer.setAttribute('aria-hidden', 'false'); lock(true);
    if (view === 'cart') renderCart();
  }
  function closeDrawer() { drawer.classList.remove('on'); drawer.setAttribute('aria-hidden', 'true'); if (!mnav.classList.contains('on')) lock(false); }
  function openMenu() { mnav.classList.add('on'); lock(true); }
  function closeMenu() { mnav.classList.remove('on'); if (!drawer.classList.contains('on')) lock(false); }

  /* ---------- cart ---------- */
  let resolved = { items: [], subtotal: '0.000' };

  async function resolveCart() {
    const items = store.get();
    if (!items.length) return (resolved = { items: [], subtotal: '0.000' });
    try {
      const r = await fetch('/api/cart/resolve', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ items }) });
      resolved = await r.json();
      // server is the source of truth: drop vanished/out-of-stock lines and clamp quantities
      store.set(resolved.items.map((i) => ({ p: i.p, v: i.v, q: i.qty })));
    } catch { /* offline: keep what we have */ }
    return resolved;
  }

  async function renderCart() {
    const body = $('[data-cart-body]'), foot = $('[data-cart-foot]');
    await resolveCart();
    const items = resolved.items;
    if (!items.length) {
      body.innerHTML = `<div class="drawer-empty"><p>${esc(I.cart_empty)}</p><a class="btn ghost" href="/products">${esc(document.documentElement.lang === 'ar' ? 'تصفح المنتجات' : 'Browse products')}</a></div>`;
      foot.hidden = true; return;
    }
    body.innerHTML = items.map((i) => `
      <div class="line" data-line data-p="${i.p}" data-v="${esc(i.v)}" data-stock="${i.stock}">
        ${i.image ? `<img src="${esc(i.image)}" alt="">` : '<span></span>'}
        <div>
          <div class="n">${esc(i.name)}</div>
          <div class="v">${esc(i.label)}</div>
          <div class="row">
            <div class="qty"><button type="button" data-line-dec aria-label="-">−</button><input value="${i.qty}" readonly aria-label="qty"><button type="button" data-line-inc aria-label="+">+</button></div>
            <div class="lt">${i.orig ? `<del>${money(i.orig * i.qty)}</del>` : ''}${money(i.line_total)}</div>
          </div>
          <button class="rm" type="button" data-line-rm>${esc(document.documentElement.lang === 'ar' ? 'حذف' : 'Remove')}</button>
        </div>
      </div>`).join('');
    $('[data-sub]').textContent = money(resolved.subtotal);
    foot.hidden = false;
    renderFreeDelivery();
  }

  function renderFreeDelivery() {
    const box = $('[data-fd]'), fd = ST.freeDelivery, sub = Number(resolved.subtotal);
    if (!fd.enabled || Number(fd.threshold) <= 0) { box.hidden = true; return; }
    const th = Number(fd.threshold), left = th - sub;
    box.hidden = false;
    $('[data-fd-text]').textContent = left > 0 ? I.free_more.replace('{amount}', money(left)) : I.free_unlocked;
    $('[data-fd-bar]').style.width = `${Math.min(100, (sub / th) * 100)}%`;
  }

  function addToCart(p, v, qty, stock) {
    const items = store.get();
    const ex = items.find((i) => i.p === p && i.v === v);
    const want = (ex ? ex.q : 0) + qty;
    if (stock && want > stock) {
      toast(I.only_left.replace('{n}', stock));
      if (ex && ex.q >= stock) return false;
      qty = stock - (ex ? ex.q : 0);
    }
    if (ex) ex.q += qty; else items.push({ p, v, q: qty });
    store.set(items);
    return true;
  }

  /* ---------- product cards / product page ---------- */
  function variantOf(box) {
    const el = $('select[data-variant]', box);
    if (el) { const o = el.selectedOptions[0]; return o && { id: o.value, now: o.dataset.now, orig: o.dataset.orig, stock: Number(o.dataset.stock) }; }
    const r = $('input[type=radio][data-variant]:checked', box) || $('input[type=hidden][data-variant]', box);
    return r && { id: r.value, now: r.dataset.now, orig: r.dataset.orig, stock: Number(r.dataset.stock) };
  }
  function paintPrice(box) {
    const v = variantOf(box); if (!v) return;
    const now = $('[data-now]', box), orig = $('[data-orig]', box);
    if (now) { now.textContent = `${v.now} ${ST.currency}`; now.classList.toggle('sale', !!v.orig); }
    if (orig) { orig.textContent = v.orig || ''; orig.hidden = !v.orig; }
    const note = $('[data-stock-note]', box);
    if (note) note.textContent = v.stock > 0 && v.stock <= 5 ? I.only_left.replace('{n}', v.stock) : '';
  }
  $$('[data-product-form]').forEach(paintPrice);

  document.addEventListener('change', (e) => {
    const box = e.target.closest('[data-product-form]');
    if (box && e.target.matches('[data-variant]')) paintPrice(box);
  });

  document.addEventListener('click', (e) => {
    const t = e.target;
    // add to cart
    const add = t.closest('[data-add]');
    if (add) {
      const box = add.closest('[data-product-form]'), v = variantOf(box);
      if (!v || v.stock <= 0) return;
      const qIn = $('[data-qty-input]', box);
      const qty = Math.max(1, Math.min(99, parseInt(qIn?.value, 10) || 1));
      if (addToCart(Number(box.dataset.product), v.id, qty, v.stock)) openDrawer('cart');
      return;
    }
    // pdp qty stepper
    if (t.closest('[data-inc]') || t.closest('[data-dec]')) {
      const input = $('[data-qty-input]', t.closest('[data-qty]'));
      const d = t.closest('[data-inc]') ? 1 : -1;
      input.value = Math.max(1, Math.min(99, (parseInt(input.value, 10) || 1) + d));
      return;
    }
    // drawer cart lines
    const line = t.closest('[data-line]');
    if (line) {
      const p = Number(line.dataset.p), v = line.dataset.v, stock = Number(line.dataset.stock);
      let items = store.get(); const it = items.find((i) => i.p === p && i.v === v); if (!it) return;
      if (t.closest('[data-line-inc]')) { if (it.q >= stock) return toast(I.only_left.replace('{n}', stock)); it.q += 1; }
      else if (t.closest('[data-line-dec]')) { it.q = Math.max(1, it.q - 1); }
      else if (t.closest('[data-line-rm]')) { items = items.filter((i) => i !== it); }
      else return;
      store.set(items); renderCart(); return;
    }
    if (t.closest('[data-open-cart]')) return openDrawer('cart');
    if (t.closest('[data-close]') || t === overlay) { closeDrawer(); closeMenu(); return; }
    if (t.closest('[data-open-menu]')) return openMenu();
    if (t.closest('[data-close-menu]')) return closeMenu();
    if (t.closest('[data-go-checkout]')) { setView('checkout'); return; }
    if (t.closest('[data-back]')) { e.preventDefault(); setView('cart'); renderCart(); return; }
  });
  document.addEventListener('keydown', (e) => { if (e.key === 'Escape') { closeDrawer(); closeMenu(); } });

  /* ---------- checkout ---------- */
  const form = $('[data-form]');
  const zoneSel = $('select[name=zone_id]', form);

  function fee() {
    const fd = ST.freeDelivery, sub = Number(resolved.subtotal);
    if (fd.enabled && Number(fd.threshold) > 0 && sub >= Number(fd.threshold)) return { free: true, value: 0 };
    const z = ST.zones.find((z) => String(z.id) === zoneSel.value);
    return z ? { free: false, value: Number(z.price) } : null;
  }
  function refreshCheckoutTotals() {
    const sub = Number(resolved.subtotal), f = fee();
    $('[data-co-sub]').textContent = money(sub);
    $('[data-co-fee]').textContent = f ? (f.value === 0 ? I.free : money(f.value)) : I.choose_area_first;
    $('[data-co-total]').textContent = money(sub + (f ? f.value : 0));
  }
  zoneSel.addEventListener('change', refreshCheckoutTotals);

  // remember the customer's details on this device only
  try {
    const saved = JSON.parse(localStorage.getItem(PROFILE) || '{}');
    ['name', 'email', 'phone', 'house', 'road', 'block'].forEach((k) => { if (saved[k] && form.elements[k]) form.elements[k].value = saved[k]; });
    if (saved.zone_id && $(`option[value="${saved.zone_id}"]`, zoneSel)) zoneSel.value = saved.zone_id;
  } catch { /* ignore */ }

  function showErrors(errors) {
    $$('[data-f]', form).forEach((f) => { f.classList.remove('err'); const em = $('.em', f); if (em) em.textContent = ''; });
    Object.entries(errors || {}).forEach(([k, msg]) => {
      const f = $(`[data-f="${k}"]`, form); if (!f) return;
      f.classList.add('err'); $('.em', f).textContent = msg;
    });
    const first = $('.err', form); if (first) first.scrollIntoView({ block: 'center', behavior: 'smooth' });
  }

  form.addEventListener('input', (e) => {
    const f = e.target.closest('[data-f]'); if (!f) return;
    f.classList.remove('err'); const em = $('.em', f); if (em) em.textContent = '';
  });

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const err = $('[data-form-error]', form); err.hidden = true;
    const data = Object.fromEntries(new FormData(form).entries());
    const local = {};
    ['name', 'email', 'phone', 'zone_id', 'house', 'road', 'block'].forEach((k) => { if (!String(data[k] || '').trim()) local[k] = I.err_required; });
    if (data.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(data.email)) local.email = I.err_email;
    if (data.phone && !/^\+?[\d\s-]{8,18}$/.test(data.phone)) local.phone = I.err_phone;
    showErrors(local);
    if (Object.keys(local).length) return;

    const btn = $('[data-submit]', form); btn.disabled = true; btn.textContent = I.sending;
    try {
      const res = await fetch('/api/order', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ...data, lang: ST.lang, items: store.get() }),
      });
      const out = await res.json().catch(() => ({}));
      if (!res.ok || !out.ok) {
        if (out.errors) showErrors(out.errors);
        else { err.textContent = out.error || I.err_generic; err.hidden = false; }
        return;
      }
      try { localStorage.setItem(PROFILE, JSON.stringify({ name: data.name, email: data.email, phone: data.phone, house: data.house, road: data.road, block: data.block, zone_id: data.zone_id })); } catch { /* ignore */ }
      store.set([]); resolved = { items: [], subtotal: '0.000' };
      $('[data-order-num]').textContent = `#${out.order_number}`;
      $('[data-wa-link]').href = out.whatsapp_url;
      form.elements.note.value = '';
      setView('done');
      setTimeout(() => { window.location.href = out.whatsapp_url; }, 900);
    } catch {
      err.textContent = I.err_generic; err.hidden = false;
    } finally {
      btn.disabled = false; btn.textContent = I.place_order;
    }
  });

  updateCount();
})();
