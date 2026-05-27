(() => {
  const data = window.DELACAU_MAP_DATA;
  if (!data || !window.L) return;

  const params = new URLSearchParams(window.location.search);
  let scenario = params.get('scenario') || '10';
  if (!data.scenarios[scenario]) scenario = Object.keys(data.scenarios)[0];
  let mode = params.get('mode') === 'key' ? 'key' : 'all';

  const back = params.get('back') || data.defaultBack || '../index.html';
  const backLink = document.querySelector('[data-back-link]');
  if (backLink) {
    backLink.href = back;
    backLink.addEventListener('click', (event) => {
      if (window.history.length > 1 && document.referrer) {
        event.preventDefault();
        window.history.back();
      }
    });
  }

  const map = L.map('route-map', { scrollWheelZoom: true, tap: true });
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
  }).addTo(map);

  const route = data.route || [];
  const routeLine = L.polyline(route, { color: '#0f766e', weight: 5, opacity: 0.9 }).addTo(map);
  const bounds = routeLine.getBounds();
  if (bounds.isValid()) map.fitBounds(bounds, { padding: [56, 56] });

  const waypointLayer = L.layerGroup().addTo(map);
  (data.waypoints || []).forEach((point) => {
    const isAlert = point.type === 'alert';
    const marker = L.circleMarker([point.lat, point.lon], {
      radius: isAlert ? 6 : 8,
      color: isAlert ? '#b7791f' : '#2563eb',
      fillColor: isAlert ? '#fbbf24' : '#93c5fd',
      fillOpacity: 0.95,
      weight: 2
    });
    marker.bindPopup(`<b>${escapeHtml(point.name)}</b>${point.desc ? `<br>${escapeHtml(point.desc)}` : ''}`);
    marker.addTo(waypointLayer);
  });

  const weatherLayer = L.layerGroup().addTo(map);
  let userMarker = null;
  let accuracyCircle = null;
  let watchingLocation = false;
  let locationWatchId = null;
  const scenarioControl = document.querySelector('[data-scenario-control]');
  const modeControl = document.querySelector('[data-mode-control]');
  const fitButton = document.querySelector('[data-fit-route]');

  function escapeHtml(value) {
    return String(value ?? '').replace(/[&<>'"]/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[char]));
  }

  function fmt(value, suffix = '') {
    return value === null || value === undefined ? '—' : `${value}${suffix}`;
  }

  function windArrow(dir) {
    // Keep the arrow visually aligned with the compass label shown by the forecast.
    return { N: '↑', NE: '↗', E: '→', SE: '↘', S: '↓', SW: '↙', W: '←', NW: '↖' }[dir] || '·';
  }

  function windText(row) {
    return `${escapeHtml(row.wind_dir || '—')}, ${fmt(row.wind)} avg / ${fmt(row.wind_max)} max km/h`;
  }

  function showLocationError(message) {
    const note = document.createElement('div');
    note.className = 'location-note';
    note.textContent = message || 'Location unavailable';
    document.body.appendChild(note);
    window.setTimeout(() => note.remove(), 2600);
  }

  function updateUserLocation(position) {
    const latlng = [position.coords.latitude, position.coords.longitude];
    const accuracy = position.coords.accuracy || 0;
    if (!userMarker) {
      userMarker = L.circleMarker(latlng, {
        radius: 8,
        color: '#ffffff',
        fillColor: '#2563eb',
        fillOpacity: 1,
        weight: 3,
        pane: 'markerPane',
      }).addTo(map).bindPopup('You are here');
      accuracyCircle = L.circle(latlng, {
        radius: accuracy,
        color: '#2563eb',
        fillColor: '#60a5fa',
        fillOpacity: 0.14,
        weight: 1,
      }).addTo(map);
      map.setView(latlng, Math.max(map.getZoom(), 15));
    } else {
      userMarker.setLatLng(latlng);
      accuracyCircle.setLatLng(latlng).setRadius(accuracy);
    }
  }

  function startLocationWatch(button) {
    if (!navigator.geolocation) {
      showLocationError('Location is not supported by this browser');
      return;
    }
    button.classList.add('loading');
    locationWatchId = navigator.geolocation.watchPosition(
      (position) => {
        watchingLocation = true;
        button.classList.remove('loading');
        button.classList.add('active');
        updateUserLocation(position);
      },
      () => {
        button.classList.remove('loading');
        showLocationError('Location unavailable');
      },
      { enableHighAccuracy: true, maximumAge: 8000, timeout: 12000 }
    );
  }

  function addLocationControl() {
    const Control = L.Control.extend({
      options: { position: 'bottomleft' },
      onAdd: () => {
        const button = L.DomUtil.create('button', 'leaflet-control locate-control');
        button.type = 'button';
        button.title = 'Show my location';
        button.setAttribute('aria-label', 'Show my location');
        button.textContent = '⌖';
        L.DomEvent.disableClickPropagation(button);
        L.DomEvent.on(button, 'click', (event) => {
          L.DomEvent.preventDefault(event);
          if (!watchingLocation) {
            startLocationWatch(button);
          } else if (userMarker) {
            map.setView(userMarker.getLatLng(), Math.max(map.getZoom(), 15));
          }
        });
        return button;
      }
    });
    map.addControl(new Control());
  }

  function keyIndexes(rows) {
    const last = rows.length - 1;
    const indexes = new Set([0, Math.round(last * 0.25), Math.round(last * 0.5), Math.round(last * 0.75), last]);
    rows.forEach((row, index) => {
      const previous = rows[index - 1];
      const next = rows[index + 1];
      const cautionStarts = row.caution && (!previous || !previous.caution);
      const cautionEnds = row.caution && (!next || !next.caution);
      if (cautionStarts || cautionEnds) indexes.add(index);
    });
    return indexes;
  }

  function markerIcon(row, compact) {
    const cls = row.caution ? 'warn' : 'ok';
    const temp = fmt(row.temp, '°');
    const arrow = windArrow(row.wind_dir);
    return L.divIcon({
      className: `weather-marker ${cls} ${compact ? 'compact' : ''}`,
      html: `<div class="wm"><span>${escapeHtml(row.time)}</span><strong>${temp} <em>${arrow}</em></strong></div>`,
      iconSize: compact ? [54, 42] : [62, 48],
      iconAnchor: compact ? [27, 42] : [31, 48],
      popupAnchor: [0, -46]
    });
  }

  function popupHtml(row) {
    return `<div class="weather-popup">
      <b>${escapeHtml(row.weather_icon || '')} ${escapeHtml(row.time)} · km ${escapeHtml(row.km)}</b><br>
      ${escapeHtml(row.place)}<br>
      Weather: <b>${escapeHtml(row.weather_label || row.condition || '—')}</b><br>
      Temperature: <b>${fmt(row.temp, '°C')}</b><br>
      Rain: <b>${fmt(row.rain, ' mm')}</b><br>
      Wind: <b><span class="popup-wind-arrow">${windArrow(row.wind_dir)}</span> ${windText(row)}</b><br>
      ${row.caution ? '<span class="status warn">Caution</span> Keep a light rain shell accessible' : '<span class="status ok">Dry</span> Mostly dry'}
    </div>`;
  }

  function setParam(name, value) {
    const next = new URLSearchParams(window.location.search);
    next.set(name, value);
    if (!next.get('back') && back) next.set('back', back);
    window.history.replaceState(null, '', `${window.location.pathname}?${next.toString()}`);
  }

  function nextScenario() {
    const keys = Object.keys(data.scenarios);
    const index = keys.indexOf(scenario);
    return keys[(index + 1) % keys.length];
  }

  function renderControls() {
    if (scenarioControl) {
      scenarioControl.textContent = `Scenario: ${scenario}h ▾`;
      scenarioControl.title = 'Tap to switch scenario: 8h, 10h, 13h';
      scenarioControl.onclick = () => {
        scenario = nextScenario();
        setParam('scenario', scenario);
        render();
      };
    }
    if (modeControl) {
      modeControl.textContent = mode === 'key' ? 'Key hours ▾' : 'All hours ▾';
      modeControl.title = mode === 'key' ? 'Showing only start, finish and important weather changes. Tap to show every hour.' : 'Showing every hourly weather marker. Tap to show key hours only.';
      modeControl.onclick = () => {
        mode = mode === 'key' ? 'all' : 'key';
        setParam('mode', mode);
        render();
      };
    }
  }

  function renderWeather() {
    weatherLayer.clearLayers();
    const rows = data.scenarios[scenario] || [];
    const keys = keyIndexes(rows);
    rows.forEach((row, index) => {
      if (mode !== 'all' && !keys.has(index)) return;
      const marker = L.marker([row.lat, row.lon], { icon: markerIcon(row, mode === 'all') });
      marker.bindPopup(popupHtml(row), { autoPan: true, keepInView: true, autoPanPadding: [18, 72], offset: [0, -8] });
      marker.addTo(weatherLayer);
    });
  }

  function render() {
    renderControls();
    renderWeather();
  }

  if (fitButton) {
    fitButton.addEventListener('click', () => {
      if (bounds.isValid()) map.fitBounds(bounds, { padding: [56, 56] });
    });
  }

  addLocationControl();
  render();
})();
