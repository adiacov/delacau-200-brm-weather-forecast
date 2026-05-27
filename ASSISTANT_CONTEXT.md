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

Main/default pages use **AccuWeather**:

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

Navigation order must stay: **AccuWeather, ECMWF, ICON, then others**.

## Product rules

- Romanian default, without diacritics.
- No combined/average forecast. It was removed because it could show wrong numbers.
- Each provider page must use only that provider's data.
- If a provider lacks max/gust wind, show `— max`; do not copy avg wind into max.
- Keep provider notes/technical details at the bottom only, unless user asks otherwise.
- `Choose weather source` section should contain only provider buttons.
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
- source buttons/order
- language buttons
- 8h / 10h / 13h sections
- wind avg/max behavior
- dark/light theme

Then:

```bash
git add .
git commit -m "Update forecast for YYYY-MM-DD"
git push
```

## Branching

Use separate branches for experiments/design/provider additions. Merge to `main` only after user approval.
