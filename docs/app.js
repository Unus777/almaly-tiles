const load = fetch('data.json').then(r => r.json());
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const cover = t => t.photos.length
  ? `<img src="img/${t.art}/${t.photos[0]}_t.jpg" alt="${esc(t.name)}" loading="lazy">`
  : 'фото скоро';

async function renderCatalog() {
  const { tiles } = await load;
  const [q, fmt, srf, stock, grid, count] =
    ['q','fmt','srf','stock','grid','count'].map(id => document.getElementById(id));
  const fill = (sel, key) => [...new Set(tiles.map(t => t[key]))].sort()
    .forEach(v => sel.add(new Option(v, v)));
  fill(fmt, 'format'); fill(srf, 'surface');

  const draw = () => {
    const s = q.value.trim().toLowerCase();
    const list = tiles.filter(t =>
      (!fmt.value || t.format === fmt.value) &&
      (!srf.value || t.surface === srf.value) &&
      (!stock.checked || t.in_stock) &&
      (!s || (t.name + ' ' + t.art).toLowerCase().includes(s)));
    grid.innerHTML = list.map(t => `
      <a class="card" href="tile.html?a=${t.art}">
        <div class="ph">${cover(t)}</div>
        <div class="b">
          <h3>${esc(t.name)}</h3>
          <div class="art">${t.art}</div>
          <div class="meta"><span class="tag">${t.format}</span><span class="tag">${esc(t.surface)}</span>
            ${t.in_stock ? '<span class="tag ok">В наличии</span>' : '<span class="tag off">Под заказ</span>'}</div>
        </div>
      </a>`).join('') || '<p style="color:var(--dim)">Ничего не найдено.</p>';
    count.textContent = `${list.length} из ${tiles.length}`;
  };
  [q, fmt, srf, stock].forEach(el => el.addEventListener('input', draw));
  draw();
  document.getElementById('stat').textContent =
    `${tiles.length} моделей, ${tiles.filter(t => t.photos.length).length} с фотографиями`;
}

async function renderTile() {
  const { tiles } = await load;
  const art = new URLSearchParams(location.search).get('a');
  const t = tiles.find(x => x.art === art);
  const box = document.getElementById('tile');
  if (!t) { box.innerHTML = '<p class="back">Плитка не найдена. <a href="index.html">В каталог</a></p>'; return; }
  document.title = `${t.name} ${t.art} — Алмалы-Керамик`;

  const gallery = t.photos.length ? `
    <div class="main-ph"><img id="big" src="img/${t.art}/${t.photos[0]}.jpg" alt="${esc(t.name)}"></div>
    <div class="thumbs">${t.photos.map((p, i) => `
      <img src="img/${t.art}/${p}_t.jpg" alt="Фото ${i + 1}" aria-current="${i === 0}"
           data-full="img/${t.art}/${p}.jpg">`).join('')}</div>`
    : '<div class="main-ph"><div class="ph" style="aspect-ratio:4/3">Фотографии этой модели пока не загружены</div></div>';

  box.innerHTML = `
    <a class="back" href="index.html">← Все модели</a>
    <div class="tile">
      <div>${gallery}</div>
      <div>
        <h1>${esc(t.name)}</h1>
        <div class="art">${t.art}</div>
        <table class="spec">
          <tr><th>Формат</th><td>${t.format} см</td></tr>
          <tr><th>Поверхность</th><td>${esc(t.surface)}</td></tr>
          <tr><th>Упаковка</th><td>${esc(t.packing)}</td></tr>
          <tr><th>Паллета</th><td>${esc(t.pallet)}</td></tr>
          <tr><th>Наличие</th><td>${t.in_stock ? 'Есть на складе Москва' : 'Под заказ'}</td></tr>
        </table>
        <img class="qr" src="qr/${t.art}.png" alt="QR-код модели ${t.art}">
        <a class="dl" href="qr/${t.art}.png" download>Скачать QR-код</a>
      </div>
    </div>`;

  box.querySelector('.thumbs')?.addEventListener('click', e => {
    const th = e.target.closest('img[data-full]'); if (!th) return;
    document.getElementById('big').src = th.dataset.full;
    box.querySelectorAll('.thumbs img').forEach(i => i.setAttribute('aria-current', i === th));
  });
}
