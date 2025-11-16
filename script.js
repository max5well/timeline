let events = [];

// ==============================
// 🚀 Load events from API
// ==============================
async function loadEvents() {
  try {
    const res = await fetch('/events');
    events = await res.json();
    fillFilters(events);
    renderTimeline(events);
  } catch (err) {
    console.error("❌ Fehler beim Laden der Events:", err);
  }
}

// ==============================
// 🧩 Populate dropdown filters
// ==============================
function fillFilters(events) {
  const catSelect = document.getElementById('categoryFilter');
  const regSelect = document.getElementById('regionFilter');
  catSelect.innerHTML = '<option value="">Kategorie: Alle</option>';
  regSelect.innerHTML = '<option value="">Region: Alle</option>';

  const categories = [...new Set(events.map(e => e.category))];
  const regions = [...new Set(events.map(e => e.region))];

  categories.forEach(c => {
    const opt = document.createElement('option');
    opt.value = c;
    opt.textContent = c;
    catSelect.appendChild(opt);
  });

  regions.forEach(r => {
    const opt = document.createElement('option');
    opt.value = r;
    opt.textContent = r;
    regSelect.appendChild(opt);
  });
}

// ==============================
// 🕰️ Render timeline dynamically
// ==============================
function renderTimeline(data) {
  const container = document.getElementById('timelineContainer');
  const timeline = document.getElementById('timeline');

  timeline.innerHTML = '';

  if (data.length === 0) {
    timeline.innerHTML = "<p style='padding:20px'>Keine Ereignisse gefunden.</p>";
    return;
  }

  const minYear = Math.min(...data.map(e => e.year));
  const maxYear = Math.max(...data.map(e => e.year));

  // scale dynamically depending on range
  let widthPerYear = 2;
  let totalWidth = (maxYear - minYear) * widthPerYear + 400;

  if (totalWidth < 1200) widthPerYear = 1200 / (maxYear - minYear);
  if (totalWidth > 6000) widthPerYear = 6000 / (maxYear - minYear);

  totalWidth = (maxYear - minYear) * widthPerYear + 400;
  timeline.style.width = totalWidth + 'px';

  const categories = [...new Set(data.map(e => e.category))];

  categories.forEach(cat => {
    const row = document.createElement('div');
    row.className = `category-row ${className(cat)}`;

    const label = document.createElement('div');
    label.className = 'category-label';
    label.textContent = cat;
    row.appendChild(label);

    data.filter(e => e.category === cat).forEach(ev => {
      const x = (ev.year - minYear) * widthPerYear + 200;
      const div = document.createElement('div');
      div.className = `event ${className(cat)}`;
      div.style.left = `${x}px`;
      div.innerHTML = `
        <div class="dot"></div>
        <div class="label">
          ${ev.region} ${formatYear(ev.year)}<br>
          <strong>${ev.title}</strong>
        </div>
      `;
      row.appendChild(div);
    });

    timeline.appendChild(row);
  });

  // add bottom scale
  const scale = document.createElement('div');
  scale.className = 'year-scale';
  const step = niceStep((maxYear - minYear) / 10);

  for (let y = minYear; y <= maxYear; y += step) {
    const mark = document.createElement('div');
    mark.className = 'year-mark';
    mark.style.left = (y - minYear) * widthPerYear + 200 + 'px';
    mark.textContent = formatYear(y);
    scale.appendChild(mark);
  }

  timeline.appendChild(scale);

  // refresh scroll width and height to ensure scroll works
  container.scrollLeft = 0;
  container.style.minHeight = `${categories.length * 160 + 100}px`;
}

// helper to make clean intervals
function niceStep(rawStep) {
  const pow10 = Math.pow(10, Math.floor(Math.log10(rawStep)));
  const n = rawStep / pow10;
  if (n < 1.5) return 1 * pow10;
  if (n < 3) return 2 * pow10;
  if (n < 7) return 5 * pow10;
  return 10 * pow10;
}

// format years
function formatYear(y) {
  return y < 0 ? `${Math.abs(y)} v. Chr.` : y;
}

function className(cat) {
  return cat.toLowerCase().replace(/[^a-z]/g, '');
}

// ==============================
// 🔍 Filter + search
// ==============================
function applyFilters() {
  const cat = document.getElementById('categoryFilter').value;
  const reg = document.getElementById('regionFilter').value;
  const search = document.getElementById('searchInput').value.toLowerCase();

  const filtered = events.filter(e =>
    (!cat || e.category === cat) &&
    (!reg || e.region === reg) &&
    (!search || e.title.toLowerCase().includes(search))
  );

  renderTimeline(filtered);
}

// event listeners
document.getElementById('categoryFilter').addEventListener('change', applyFilters);
document.getElementById('regionFilter').addEventListener('change', applyFilters);
document.getElementById('searchInput').addEventListener('input', applyFilters);

// init
loadEvents();
