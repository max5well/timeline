let events = [];
let summaryCache = {}; // Cache für LLM summaries

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
  console.log('renderTimeline START with', data.length, 'events');

  const container = document.getElementById('timelineContainer');
  const timeline = document.getElementById('timeline');

  if (!timeline) {
    console.error('Timeline element not found!');
    return;
  }

  timeline.innerHTML = '';
  console.log('Timeline cleared');

  if (data.length === 0) {
    timeline.innerHTML = "<p style='padding:20px'>Keine Ereignisse gefunden.</p>";
    console.log('No events to display');
    return;
  }

  console.log('Calculating year range...');
  const minYear = Math.min(...data.map(e => e.year));
  const maxYear = Math.max(...data.map(e => e.year));
  console.log('Year range:', minYear, 'to', maxYear);

  // scale dynamically depending on range
  let widthPerYear = 2;
  const yearRange = maxYear - minYear || 100; // Prevent division by zero
  let totalWidth = yearRange * widthPerYear + 400;

  if (totalWidth < 1200) widthPerYear = 1200 / yearRange;
  if (totalWidth > 6000) widthPerYear = 6000 / yearRange;

  totalWidth = yearRange * widthPerYear + 400;
  timeline.style.width = totalWidth + 'px';

  console.log('Extracting categories...');
  const categories = [...new Set(data.map(e => e.category))];
  console.log('Found categories:', categories);

  categories.forEach((cat, catIndex) => {
    console.log(`Processing category ${catIndex + 1}/${categories.length}:`, cat);

    const row = document.createElement('div');
    const catClass = className(cat);
    console.log('Category class name:', catClass);
    row.className = `category-row ${catClass}`;

    const label = document.createElement('div');
    label.className = 'category-label';
    label.textContent = cat;
    row.appendChild(label);

    const eventsInCat = data.filter(e => e.category === cat);
    console.log(`Events in category "${cat}":`, eventsInCat.length);

    eventsInCat.forEach((ev, evIndex) => {
      console.log(`  Event ${evIndex + 1}/${eventsInCat.length}:`, ev.title);
      const x = (ev.year - minYear) * widthPerYear + 200;
      const div = document.createElement('div');
      div.className = `event ${catClass}`;
      div.style.left = `${x}px`;
      div.innerHTML = `
        <div class="dot"></div>
        <div class="label">
          ${ev.region} ${formatYear(ev.year)}<br>
          <strong>${ev.title}</strong>
        </div>
        <div class="info-icon">ℹ️</div>
      `;

      // Add click handler directly (no setTimeout)
      const infoIcon = div.querySelector('.info-icon');
      if (infoIcon) {
        infoIcon.addEventListener('click', (e) => {
          e.stopPropagation();
          showEventSummary(ev);
        });
      }

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
  console.log('Finalizing timeline...');
  container.scrollLeft = 0;
  container.style.minHeight = `${categories.length * 160 + 100}px`;
  console.log('renderTimeline COMPLETED successfully');
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
  // Remove emojis and special characters, keep only letters
  try {
    return cat.replace(/[\u{1F000}-\u{1FFFF}]/gu, '')
              .replace(/[\u{2600}-\u{26FF}]/gu, '')  // Remove misc symbols
              .replace(/[\u{2700}-\u{27BF}]/gu, '')  // Remove dingbats
              .trim()
              .toLowerCase()
              .replace(/[^a-z]/g, '') || 'default';
  } catch (e) {
    console.error('className error:', e, cat);
    return 'default';
  }
}

// ==============================
// 💬 Event Summary Popup
// ==============================
async function showEventSummary(event) {
  // Create or get popup
  let popup = document.getElementById('summary-popup');
  if (!popup) {
    popup = document.createElement('div');
    popup.id = 'summary-popup';
    popup.className = 'summary-popup';
    document.body.appendChild(popup);
  }

  // Show loading
  popup.innerHTML = `
    <div class="popup-content">
      <button class="close-btn" onclick="document.getElementById('summary-popup').style.display='none'">✕</button>
      <h3>${event.title}</h3>
      <p class="event-meta">${event.region} • ${formatYear(event.year)}</p>
      <div class="summary-content">
        <p>⏳ Lade Zusammenfassung...</p>
      </div>
    </div>
  `;
  popup.style.display = 'flex';

  // Check cache
  const cacheKey = `${event.title}_${event.year}`;
  if (summaryCache[cacheKey]) {
    displaySummary(popup, summaryCache[cacheKey]);
    return;
  }

  // Fetch summary from API
  try {
    const res = await fetch('/events/summary', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(event)
    });
    const data = await res.json();

    if (data.summary) {
      summaryCache[cacheKey] = data.summary;
      displaySummary(popup, data.summary);
    } else {
      displaySummary(popup, ['Keine Zusammenfassung verfügbar']);
    }
  } catch (err) {
    console.error('Error loading summary:', err);
    displaySummary(popup, ['❌ Fehler beim Laden der Zusammenfassung']);
  }
}

function displaySummary(popup, bulletPoints) {
  const summaryDiv = popup.querySelector('.summary-content');
  summaryDiv.innerHTML = '<ul class="summary-list">' +
    bulletPoints.map(point => `<li>${point}</li>`).join('') +
    '</ul>';
}

// ==============================
// 🔍 Filter + search
// ==============================
let filterTimeout;
function applyFilters() {
  // Debounce to prevent multiple rapid calls
  clearTimeout(filterTimeout);
  filterTimeout = setTimeout(() => {
    try {
      console.log('applyFilters called');
      const catEl = document.getElementById('categoryFilter');
      const regEl = document.getElementById('regionFilter');
      const searchEl = document.getElementById('searchInput');

      if (!catEl || !regEl || !searchEl) {
        console.error('Filter elements not found');
        return;
      }

      const cat = catEl.value;
      const reg = regEl.value;
      const search = searchEl.value.toLowerCase();

      console.log('Filters:', { cat, reg, search });

      const filtered = events.filter(e =>
        (!cat || e.category === cat) &&
        (!reg || e.region === reg) &&
        (!search || e.title.toLowerCase().includes(search))
      );

      console.log(`Filtered ${filtered.length} events`);
      renderTimeline(filtered);
      console.log('renderTimeline completed');
    } catch (err) {
      console.error('Error in applyFilters:', err);
      alert('Filter error: ' + err.message);
    }
  }, 100); // 100ms debounce
}

// init
document.addEventListener('DOMContentLoaded', () => {
  loadEvents();

  // event listeners
  const catFilter = document.getElementById('categoryFilter');
  const regFilter = document.getElementById('regionFilter');
  const searchInput = document.getElementById('searchInput');

  if (catFilter) catFilter.addEventListener('change', applyFilters);
  if (regFilter) regFilter.addEventListener('change', applyFilters);
  if (searchInput) searchInput.addEventListener('input', applyFilters);
});
