# Project instructions for future forecast updates

Project: Delacau 200 BRM weather forecast, Moldova, 31 May 2026.

Goal: maintain a static, GitHub Pages-ready multilingual weather forecast for riders.

## Site structure

- `index.html` — Romanian default page
- `ro/index.html` — Romanian page, same content as default
- `en/index.html` — English page
- `ru/index.html` — Russian page
- `assets/style.css` — shared mobile-first style with automatic light/dark theme
- `delacau-200-brm.gpx` — route file
- `brevet_delacau_weather_research.py` — generator script

## Update workflow

When asked to update the forecast:

1. Use short network timeouts only, normally 20-30 seconds maximum per request.
2. If a weather API/platform fails, record it and do not retry it repeatedly in the same run.
3. Run:
   ```bash
   python3 brevet_delacau_weather_research.py
   ```
4. Review generated pages quickly.
5. Commit the update:
   ```bash
   git add .
   git commit -m "Update forecast for YYYY-MM-DD"
   ```

## Forecast rules

- Main visible content must be rider-friendly, not technical.
- Do not show raw JSON or confusing provider columns in the main page.
- Forecast sources and technical details belong at the bottom.
- Always show `Last researched` near the top of each page.
- Romanian is default and should be written without diacritics.
- Keep the page static and GitHub Pages friendly: no build system required.

## GitHub Pages

The repository can be published from branch `main`, folder `/`.
The default page will be `index.html`.
