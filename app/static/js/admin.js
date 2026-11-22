(() => {
  const AI = window.AI || {};
  const $ = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  // confirm dialogs for destructive forms
  document.addEventListener('submit', (e) => {
    const msg = e.target.dataset.confirm;
    if (msg && !confirm(msg)) e.preventDefault();
  });

  // live image preview
  $$('input[type=file][data-preview]').forEach((inp) => {
    inp.addEventListener('change', () => {
      const f = inp.files[0]; if (!f) return;
      const box = $(inp.dataset.preview);
      box.innerHTML = `<img src="${URL.createObjectURL(f)}" alt="">`;
    });
  });

  // generic row editor (variants / zones)
  function editor(rootSel, cfg) {
    const root = $(rootSel); if (!root) return;
    const body = $('[data-rows]', root), form = root.closest('form');
    const data = JSON.parse($(cfg.data).textContent || '[]');
    const add = (row = {}) => {
      const el = document.createElement('div'); el.className = 'er'; el.dataset.id = row.id ?? '';
      el.innerHTML = cfg.fields.map((f) => f.type === 'check'
        ? `<label class="check" style="margin:0;height:40px"><input type="checkbox" data-k="${f.k}" ${row[f.k] !== false ? 'checked' : ''}><span>${f.ph}</span></label>`
        : `<input type="${f.type}" dir="auto" data-k="${f.k}" placeholder="${f.ph}" ${f.step ? `step="${f.step}"` : ''} ${f.min !== undefined ? `min="${f.min}"` : ''} value="${(row[f.k] ?? '') === null ? '' : String(row[f.k] ?? '').replace(/"/g, '&quot;')}">`
      ).join('') + '<button type="button" class="x" aria-label="${AI.remove}">&times;</button>';
      el.querySelector('.x').onclick = () => el.remove();
      body.appendChild(el);
    };
    (data.length ? data : [{}]).forEach(add);
    $('[data-add-row]', root).onclick = () => add({});
    form.addEventListener('submit', () => {
      const rows = $$('.er[data-id]', body).map((el) => {
        const o = { id: el.dataset.id || null };
        $$('[data-k]', el).forEach((i) => { o[i.dataset.k] = i.type === 'checkbox' ? i.checked : i.value; });
        return o;
      });
      $(cfg.out, form).value = JSON.stringify(rows);
    });
  }
  editor('#variants', { data: '#variants-data', out: '[name=variants_json]', fields: [
    { k: 'label_ar', type: 'text', ph: AI.size_ar }, { k: 'label_en', type: 'text', ph: AI.size_en },
    { k: 'price', type: 'number', ph: AI.price, step: '0.001', min: 0 }, { k: 'sale_price', type: 'number', ph: AI.sale_price, step: '0.001', min: 0 },
    { k: 'stock', type: 'number', ph: AI.stock, step: '1', min: 0 }] });
  editor('#zones', { data: '#zones-data', out: '[name=zones_json]', fields: [
    { k: 'name_ar', type: 'text', ph: AI.area_ar }, { k: 'name_en', type: 'text', ph: AI.area_en },
    { k: 'price', type: 'number', ph: AI.delivery_price, step: '0.001', min: 0 }, { k: 'is_active', type: 'check', ph: AI.active }] });
})();
