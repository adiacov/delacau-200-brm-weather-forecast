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

## What this project contains

- `index.html` — Romanian default page, AccuWeather
- `ro/index.html` — Romanian page, AccuWeather
- `en/index.html` — English page, AccuWeather
- `ru/index.html` — Russian page, AccuWeather
- `sources/` — provider-specific pages in Romanian, English and Russian; provider order starts with AccuWeather, ECMWF, ICON
- `assets/style.css` — shared mobile-first design, light/dark theme support
- `assets/theme.js` — visible light/dark theme toggle
- `delacau-200-brm.gpx` — route GPX used for hourly route-position estimates
- `brevet_delacau_weather_research.py` — generator script
- `.github/workflows/update-forecast.yml` — daily automatic update around 06:00 Moldova time
- `ANNOUNCEMENT.md` — Telegram announcement texts
- `PROJECT_INSTRUCTIONS.md` — maintenance/update instructions
- `ASSISTANT_CONTEXT.md` — quick context for future assistant sessions

## Design goal

This is for non-technical riders. The visible page should be simple, practical and easy to read on a phone. Technical details and weather-source notes belong at the bottom only.

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
- Optionally add an interactive route map later.
