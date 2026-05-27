# Project instructions for future developers / assistants

## Purpose

This project maintains a static, GitHub Pages-ready weather forecast for **Delacau 200 BRM**, Moldova, **31 May 2026**.

The audience is cyclists, not developers. The page must answer:

- What weather should I expect on the route?
- What changes if I finish in 8h, 10h or 13h?
- Which weather provider am I looking at?
- When was the forecast last updated?

## Important product rules

- Romanian is the default language and must be written **without diacritics**.
- Supported main pages:
  - `index.html` — Romanian default, currently AccuWeather
  - `ro/index.html` — Romanian, currently AccuWeather
  - `en/index.html` — English, currently AccuWeather
  - `ru/index.html` — Russian, currently AccuWeather
- Provider-specific pages live in `sources/`.
- There is **no combined/average forecast anymore**. Do not reintroduce provider averaging unless the user explicitly asks.
- Each provider page must show only data from that provider. If a provider does not return max/gust wind, show `— max`; do not invent it by copying average wind.
- Keep the visible report rider-friendly.
- Do not show raw JSON or confusing provider data in the main content.
- Keep forecast sources / technical notes at the bottom.
- Always show the forecast update timestamp in the header area, grouped with the automatic update schedule.
- The site must remain static and GitHub Pages friendly: no build system required.

## Files

- `brevet_delacau_weather_research.py` — main generator script.
- `delacau-200-brm.gpx` — route file used to estimate rider position by kilometer.
- `assets/style.css` — shared responsive styling.
- `assets/theme.js` — light/dark theme toggle.
- `.github/workflows/update-forecast.yml` — daily GitHub Actions update at about 06:00 Moldova time.
- `ANNOUNCEMENT.md` — Telegram announcement texts.
- `LICENSE` — MIT license, copyright Alexandru Diacov.
- Generated pages:
  - `index.html`
  - `ro/index.html`
  - `en/index.html`
  - `ru/index.html`
  - `sources/accuweather.html`, `sources/accuweather-en.html`, `sources/accuweather-ru.html`
  - `sources/ecmwf.html`, `sources/ecmwf-en.html`, `sources/ecmwf-ru.html`
  - `sources/icon.html`, `sources/icon-en.html`, `sources/icon-ru.html`
  - `sources/met-norway.html`, `sources/met-norway-en.html`, `sources/met-norway-ru.html`
  - `sources/7timer.html`, `sources/7timer-en.html`, `sources/7timer-ru.html`
  - `sources/weather-forecast.html`, `sources/weather-forecast-en.html`, `sources/weather-forecast-ru.html`

## How the generator works

1. Reads the GPX route.
2. For each finish scenario — 8h, 10h, 13h — estimates cyclist position every hour.
3. Fetches weather from public sources with short timeouts.
4. Generates separate provider pages for AccuWeather, ECMWF, ICON, MET Norway / Yr, 7Timer Civil and Weather-Forecast.com.
5. Generates Romanian, English and Russian versions.
6. Rewrites the generated HTML/Markdown files; do not manually maintain generated HTML as the source of truth.

## Provider behavior

- AccuWeather: currently the default page; public page gives day/night forecast and gust/max wind.
- ECMWF: hourly model forecast from Open-Meteo.
- ICON: hourly model forecast from Open-Meteo.
- MET Norway / Yr: useful hourly point source; may not always expose gust/max wind.
- 7Timer Civil: 3-hourly source; no true max/gust wind.
- Weather-Forecast.com: broad Chisinau 3-period forecast; no true max/gust wind.

## Network/API rules

- Use short request timeouts only: normally 20-30 seconds maximum per request.
- If a platform fails, record it and do not retry it repeatedly in the same run.
- Do not block the whole update on one failing provider.
- No API keys should be required.

## Daily update workflow

From the project folder:

```bash
python3 brevet_delacau_weather_research.py
```

Then review the generated page locally before committing, especially:

- top summary
- forecast update timestamp and automatic update schedule
- 8h / 10h / 13h scenario rows
- all language pages still render
- reading guidance appears before weather-source selection
- provider source buttons work and order is AccuWeather, ECMWF, ICON, then the rest
- no combined/average forecast appears
- no invented max/gust wind values; use `— max` when unavailable
- for UI changes, compare before/after with `git diff` and open the local page in a browser

Commit and push only after this check:

```bash
git add .
git commit -m "Update forecast for YYYY-MM-DD"
git push
```

## GitHub Pages

The repository is intended to publish from branch `main`, folder `/`.
The public URL is:

`https://adiacov.github.io/delacau-200-brm-weather-forecast/`

## Development principle

Prefer small, understandable changes. Commit after meaningful milestones.
