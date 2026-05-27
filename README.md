# Delacau 200 BRM Weather Forecast

Static multilingual weather forecast page for cyclists riding **Delacau 200 BRM** in Moldova on **Sunday, 31 May 2026**.

The page helps riders understand the expected weather **along the route**, depending on their estimated finish time: **8h, 10h or 13h**.

Public page:

`https://adiacov.github.io/delacau-200-brm-weather-forecast/`

## Current product behavior

- The default page uses **AccuWeather**.
- The old combined/average forecast was removed.
- Users can switch between separate provider pages:
  - AccuWeather
  - ECMWF
  - ICON
  - MET Norway / Yr
  - 7Timer Civil
  - Weather-Forecast.com
- Each provider page shows only that provider's data.
- If max/gust wind is unavailable from a provider, the page shows `— max` instead of inventing a value.
- Each scenario can open an English interactive route map with route, checkpoints, weather markers, wind arrows and optional browser GPS location.

## What this project contains

- `index.html` — Romanian default page, AccuWeather
- `ro/index.html` — Romanian page, AccuWeather
- `en/index.html` — English page, AccuWeather
- `ru/index.html` — Russian page, AccuWeather
- `sources/` — provider-specific pages in Romanian, English and Russian; provider order starts with AccuWeather, ECMWF, ICON
- `maps/` — generated English interactive map pages, one per provider
- `assets/style.css` — shared mobile-first design, light/dark theme support
- `assets/theme.js` — visible light/dark theme toggle and collapsed-section behavior
- `assets/map.js` — reusable Leaflet map behavior, weather markers, wind arrows and browser GPS location
- `delacau-200-brm.gpx` — route GPX used for hourly route-position estimates and map route/waypoints
- `brevet_delacau_weather_research.py` — generator script
- `.github/workflows/update-forecast.yml` — daily automatic update around 06:00 Moldova time
- `ANNOUNCEMENT.md` — Telegram announcement texts
- `LICENSE` — MIT license, copyright Alexandru Diacov
- `PROJECT_INSTRUCTIONS.md` — maintenance/update instructions
- `ASSISTANT_CONTEXT.md` — quick context for future assistant sessions

## Design goal

This is for non-technical riders. The visible page should be simple, practical and easy to read on a phone. The header uses generic weather-forecast wording, shows route facts as separate pills, and groups the automatic update schedule with the forecast update timestamp. Technical details and weather-source notes belong at the bottom only.

## Generated pages

The HTML pages are generated output. For layout/content generation, update `brevet_delacau_weather_research.py` and regenerate the pages. For visual styling, update `assets/style.css`. For light/dark/collapsed-section behavior, update `assets/theme.js`. For interactive map behavior, update `assets/map.js`.

## Updating the forecast

Run:

```bash
python3 brevet_delacau_weather_research.py
```

Then review the generated pages and commit the result:

```bash
git add .
git commit -m "Update forecast for YYYY-MM-DD"
git push
```

The script uses public weather sources with short request timeouts. No API keys are required.

## GitHub Pages setup

In GitHub:

1. Open repository **Settings**
2. Open **Pages**
3. Source: **Deploy from a branch**
4. Branch: **main**
5. Folder: **/ (root)**
6. Save

After GitHub builds the page, it should be available at:

`https://adiacov.github.io/delacau-200-brm-weather-forecast/`

## Future improvements

- Review and polish Romanian/Russian/English wording.
- Update/add weather providers if better public sources are found.
- Optionally improve the interactive map with route-kilometer estimation from live GPS.
