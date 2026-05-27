# Assistant context — compact source of truth

Project path:

```bash
cd ~/Downloads/delacau-200-brm-weather-forecast
```

This is the Git repository. If `git status` fails, you are probably in `~/Downloads`, not inside the project folder.

## Before changing anything

Read:

1. `PROJECT_INSTRUCTIONS.md`
2. `README.md`
3. `brevet_delacau_weather_research.py`

## Current product

Static GitHub Pages weather forecast for **Delacau 200 BRM**, Moldova, **31 May 2026**.

Public URL:

`https://adiacov.github.io/delacau-200-brm-weather-forecast/`

Audience: non-technical cyclists. The page must be practical, mobile-friendly, and easy to read.

## Current structure

Main/default pages use **AccuWeather** data, but page titles stay generic:

- `index.html` — Romanian default
- `ro/index.html`
- `en/index.html`
- `ru/index.html`

Provider pages are in `sources/`, each in RO/EN/RU:

1. AccuWeather
2. ECMWF
3. ICON
4. MET Norway / Yr
5. 7Timer Civil
6. Weather-Forecast.com

English-only interactive map pages are in `maps/`, one per provider. They use Leaflet from CDN, `assets/map.js`, full GPX route/waypoints, provider-specific scenario rows, wind arrows and optional browser GPS location.

Navigation order must stay: **AccuWeather, ECMWF, ICON, then others**.

## Product rules

- Romanian default, without diacritics.
- Generated HTML files are output; update layout/content in `brevet_delacau_weather_research.py`, then regenerate pages.
- No combined/average forecast. It was removed because it could show wrong numbers.
- Each provider page must use only that provider's data.
- If a provider lacks max/gust wind, show `— max`; do not copy avg wind into max.
- Keep provider notes/technical details at the bottom only, unless user asks otherwise.
- Header title/subtitle should be generic; provider name belongs in source selection/notes, not in the main title.
- Route facts are shown as separate pills: start, distance, elevation gain.
- Forecast update timestamp is grouped with the automatic update schedule near the bottom of the header.
- `How to read this forecast` should appear before `Choose weather source`.
- `Weather source` / provider section is collapsed by default and shows the active provider pill; expanded provider buttons must keep the order above.
- Scenarios are collapsed by default; source switching preserves the currently open scenario via `#scenario-8/10/13`.
- Keep language buttons visible on provider pages; active language must be visible in light and dark mode.
- Use short network timeouts; do not repeatedly call failing APIs.
- Commit and push after meaningful milestones.

## Automation

GitHub Actions workflow:

`.github/workflows/update-forecast.yml`

Runs daily around **06:12 Moldova time** and can be run manually from GitHub Actions.

## Update command

```bash
python3 brevet_delacau_weather_research.py
```

Then review generated pages locally, especially:

- default AccuWeather page
- generic header title/subtitle and route fact pills
- update schedule + forecast update timestamp grouping
- source buttons/order
- language buttons
- 8h / 10h / 13h sections
- wind avg/max behavior
- collapsed weather-source and scenario behavior
- map pages, map buttons, wind arrows and optional location control
- dark/light theme

Then:

```bash
git add .
git commit -m "Update forecast for YYYY-MM-DD"
git push
```

## Branching

Use separate branches for experiments/design/provider additions. Merge to `main` only after user approval.
