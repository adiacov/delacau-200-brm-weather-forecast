# Project instructions for future developers / assistants

## Purpose

This project maintains a static, GitHub Pages-ready weather forecast for **Delacau 200 BRM**, Moldova, **31 May 2026**.

The audience is cyclists, not developers. The main page must answer:

- What weather should I expect on the route?
- What changes if I finish in 8h, 10h or 13h?
- When was the forecast last researched?

## Important product rules

- Romanian is the default language and must be written **without diacritics**.
- Supported pages:
  - `index.html` — Romanian default
  - `ro/index.html` — Romanian
  - `en/index.html` — English
  - `ru/index.html` — Russian
- Keep the visible report rider-friendly.
- Do not show raw JSON or technical provider data in the main content.
- Keep forecast sources / technical notes at the bottom.
- Always show `Last researched` near the top.
- The site must remain static and GitHub Pages friendly: no build system required.

## Files

- `brevet_delacau_weather_research.py` — main generator script.
- `delacau-200-brm.gpx` — route file used to estimate rider position by kilometer.
- `assets/style.css` — shared responsive styling.
- `assets/theme.js` — light/dark theme toggle.
- Generated pages:
  - `index.html`
  - `ro/index.html`
  - `en/index.html`
  - `ru/index.html`
  - `delacau_200_weather_31may2026.html`
  - `delacau_200_weather_31may2026.md`

## How the generator works

1. Reads the GPX route.
2. For each finish scenario — 8h, 10h, 13h — estimates cyclist position every hour.
3. Fetches weather from public sources with short timeouts.
4. Combines the result into simple rider-facing rows: time, approximate km, route area, temperature, rain, wind, advice.
5. Generates all language pages.

## Network/API rules

- Use short request timeouts only: normally 20-30 seconds maximum per request.
- If a platform fails, record it and do not retry it repeatedly in the same run.
- Do not block the whole update on one failing provider.
- No API keys should be required.

Known source behavior from previous work:

- MET Norway / Yr: useful hourly source.
- 7Timer: useful 3-hourly cross-check.
- Weather-Forecast.com: broad Chisinau cross-check only.
- Open-Meteo: had repeated 502/504/timeouts in this environment.
- wttr.in: date-specific endpoint was not useful for 31 May.
- timeanddate.com: blocked by anti-bot page.

## Daily update workflow

From the project folder:

```bash
python3 brevet_delacau_weather_research.py
```

Then review the generated page locally, especially:

- top summary
- `Last researched` time
- 8h / 10h / 13h scenario rows
- all language pages still render

Commit and push:

```bash
git add .
git commit -m "Update forecast for YYYY-MM-DD"
git push
```

## GitHub Pages

The repository is intended to publish from branch `main`, folder `/`.
The public URL should be:

`https://adiacov.github.io/delacau-200-brm-weather-forecast/`

## Development principle

Prefer small, understandable changes. Commit after meaningful milestones.
