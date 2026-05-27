# Assistant context

When the user asks about this project, first go to:

```bash
cd ~/Downloads/delacau-200-brm-weather-forecast
```

This is the Git repository. Running `git status` from `~/Downloads` will fail because the repo is inside this folder.

Read these files before making changes:

1. `PROJECT_INSTRUCTIONS.md` — product rules and update workflow
2. `README.md` — public project overview
3. `brevet_delacau_weather_research.py` — generator script

Core rules:

- Audience: non-technical cyclists.
- Romanian default, without diacritics.
- Main pages are AccuWeather-based by default: `index.html`, `ro/index.html`, `en/index.html`, `ru/index.html`.
- Provider-specific pages are in `sources/`; navigation order starts with AccuWeather, ECMWF, ICON.
- Do **not** restore the old combined/average forecast. It was removed because it could show wrong numbers.
- Each provider page must use only that provider's data.
- If a provider does not provide max/gust wind, show `— max`; do not copy average wind into max.
- Keep visible content simple and rider-friendly.
- Weather/provider technical details stay at the bottom.
- Use short network timeouts; do not repeatedly call failing APIs.
- Commit and push after meaningful milestones.

Daily update command:

```bash
python3 brevet_delacau_weather_research.py
```

Then review locally and run:

```bash
git add .
git commit -m "Update forecast for YYYY-MM-DD"
git push
```
