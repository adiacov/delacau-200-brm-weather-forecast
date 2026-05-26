# Delacau 200 BRM Weather Forecast

Static multilingual weather forecast page for cyclists riding **Delacau 200 BRM** in Moldova on **Sunday, 31 May 2026**.

The page helps riders understand the expected weather **along the route**, depending on their estimated finish time: **8h, 10h or 13h**.

Public page after GitHub Pages is enabled:

`https://adiacov.github.io/delacau-200-brm-weather-forecast/`

## What this project contains

- `index.html` — Romanian default page
- `ro/index.html` — Romanian page
- `en/index.html` — English page
- `ru/index.html` — Russian page
- `assets/style.css` — shared mobile-first design, light/dark theme support
- `assets/theme.js` — visible light/dark theme toggle
- `delacau-200-brm.gpx` — route GPX used for hourly route-position estimates
- `brevet_delacau_weather_research.py` — generator script
- `delacau_200_weather_31may2026.md` — markdown summary
- `PROJECT_INSTRUCTIONS.md` — maintenance/update instructions
- `ASSISTANT_CONTEXT.md` — quick context for future assistant sessions
- `ANNOUNCEMENT.md` — short Telegram announcement text

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
- Update the forecast daily closer to the event.
- Optionally add an interactive route map later.
