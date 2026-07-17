# Delacau 200 BRM Weather Forecast (archived — moved to Velometeo)

**This project is superseded by [Velometeo](https://github.com/adiacov/velometeo).**

All public pages here now redirect to the new forecast page:

`https://adiacov.github.io/velometeo/event.html?event=delacau-200-brm`

## What changed

- Every HTML page (`index.html`, `en/`, `ro/`, `ru/`, `sources/`, `maps/`) was
  replaced with a redirect to the Velometeo event page.
- The daily update workflow (`.github/workflows/update-forecast.yml`) was
  removed — nothing here regenerates anymore.
- The generator script, GPX, and assets remain in the repository (and its git
  history) for reference only; they are no longer used.

## Original project

A static multilingual weather forecast page for cyclists riding
**Delacau 200 BRM** in Moldova, with per-provider forecasts (ECMWF, ICON,
AccuWeather), finish-time scenarios (8h/10h/13h), and interactive route maps.
The pre-redirect version is available in git history before the redirect
commit.
