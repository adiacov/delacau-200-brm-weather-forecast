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
- Pages: `index.html`, `ro/index.html`, `en/index.html`, `ru/index.html`.
- Keep visible content simple and rider-friendly.
- Weather/provider technical details stay at the bottom.
- Use short network timeouts; do not repeatedly call failing APIs.
- Commit and push after meaningful milestones.

Daily update command:

```bash
python3 brevet_delacau_weather_research.py
```

Then:

```bash
git add .
git commit -m "Update forecast for YYYY-MM-DD"
git push
```
