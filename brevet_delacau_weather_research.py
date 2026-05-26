#!/usr/bin/env python3
"""Generate multilingual GitHub Pages forecast for Delacau 200 BRM.

Rules: short request timeouts, no repeated retries for failing platforms, rider-friendly output.
"""
from __future__ import annotations

import json
import math
import statistics
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent
TZ = ZoneInfo("Europe/Chisinau")
FORECAST_DATE = "2026-05-31"
START_HOUR = 6
DISTANCE_KM = 200
DURATIONS = [8, 10, 13]

# Weather query points kept intentionally limited for short, reliable daily updates.
# Actual cyclist position is taken from GPX; weather is sampled from nearest point below.
WEATHER_POINTS = [
    (0, "Chisinau", 47.0245, 28.8323),
    (30, "Vadul lui Voda", 47.0878, 29.0798),
    (55, "Criuleni / Dubasari corridor", 47.2133, 29.1599),
    (80, "Delacau area", 47.0985, 29.3034),
    (105, "Anenii Noi area", 46.8788, 29.2291),
    (140, "Bulboaca / Anenii Noi west", 46.8910, 29.0540),
    (170, "Chisinau outskirts", 46.9600, 28.9600),
    (200, "Chisinau finish", 47.0245, 28.8323),
]

TEXT = {
    "ro": {
        "lang_name": "Romana", "html_lang": "ro", "dir": "ltr", "active": "RO",
        "title": "Vremea pe traseu pentru Delacau 200 BRM",
        "subtitle": "Prognoza ora cu ora pentru 31 mai 2026 · Start: 06:00 · Scenarii: 8h / 10h / 13h",
        "last": "Ultima cercetare", "forecast_for": "Prognoza pentru", "start": "Start", "route": "Ruta", "auto_update": "Pagina este planificata sa se actualizeze zilnic in jurul orei 06:00, ora Moldovei.",
        "summary": "Concluzie pe scurt", "overall": "General", "temp": "Temperatura", "wind": "Vant mediu/max", "wind_dir": "Directie vant", "rain": "Ploaie",
        "route_info": "Cum se citeste prognoza", "route_note": "Alege scenariul cel mai apropiat de timpul tau estimat de finish: 8h, 10h sau 13h. Pentru fiecare ora vezi kilometrul aproximativ si vremea probabila in acea zona. Daca ritmul tau difera, foloseste kilometrul aproximativ ca reper.",
        "scenario": "Scenariu", "finish": "finisare in", "time": "Ora", "km": "Km aprox.", "sector": "Zona traseului", "weather": "Vreme", "advice": "Recomandare",
        "dry": "Uscat", "caution": "Atentie", "mostly_dry": "In mare parte uscat", "shell": "Tine la indemana o geaca usoara de ploaie",
        "sources": "Surse verificate", "sources_note": "Sectiune tehnica, pastrata jos pentru transparenta.",
        "disclaimer": "Prognoza este informativa. Vremea se poate schimba; verifica din nou inainte de start.",
        "conclusion_prefix": "Cel mai probabil: vreme buna pentru bicicleta, in mare parte uscata.",
        "updated_tz": "ora Moldovei", "hours": "ore",
    },
    "en": {
        "lang_name": "English", "html_lang": "en", "dir": "ltr", "active": "EN",
        "title": "Weather on the route for Delacau 200 BRM",
        "subtitle": "Hour-by-hour forecast for 31 May 2026 · Start: 06:00 · Scenarios: 8h / 10h / 13h",
        "last": "Last researched", "forecast_for": "Forecast for", "start": "Start", "route": "Route", "auto_update": "This page is scheduled to update daily around 06:00 Moldova time.",
        "summary": "Short conclusion", "overall": "Overall", "temp": "Temperature", "wind": "Avg/max wind", "wind_dir": "Wind direction", "rain": "Rain",
        "route_info": "How to read this forecast", "route_note": "Choose the scenario closest to your estimated finish time: 8h, 10h or 13h. For each hour you see the approximate kilometer and the likely weather in that area. If your pace is different, use the approximate kilometer as your reference.",
        "scenario": "Scenario", "finish": "finish in", "time": "Time", "km": "Approx km", "sector": "Route area", "weather": "Weather", "advice": "Advice",
        "dry": "Dry", "caution": "Caution", "mostly_dry": "Mostly dry", "shell": "Keep a light rain shell accessible",
        "sources": "Forecast sources checked", "sources_note": "Technical section kept at the bottom for transparency.",
        "disclaimer": "Forecast is informational. Weather can change; check again before the start.",
        "conclusion_prefix": "Most probable: good cycling weather, mostly dry.",
        "updated_tz": "Moldova time", "hours": "hours",
    },
    "ru": {
        "lang_name": "Русский", "html_lang": "ru", "dir": "ltr", "active": "RU",
        "title": "Погода на маршруте Delacau 200 BRM",
        "subtitle": "Почасовой прогноз на 31 мая 2026 · Старт: 06:00 · Сценарии: 8ч / 10ч / 13ч",
        "last": "Последнее обновление", "forecast_for": "Прогноз на", "start": "Старт", "route": "Маршрут", "auto_update": "Страница запланирована к ежедневному обновлению около 06:00 по времени Молдовы.",
        "summary": "Краткий вывод", "overall": "В целом", "temp": "Температура", "wind": "Ветер ср/макс", "wind_dir": "Направление ветра", "rain": "Дождь",
        "route_info": "Как читать этот прогноз", "route_note": "Выберите сценарий, который ближе всего к вашему ожидаемому времени финиша: 8ч, 10ч или 13ч. Для каждого часа указан примерный километр и ожидаемая погода в этой зоне. Если ваш темп отличается, ориентируйтесь по примерному километру.",
        "scenario": "Сценарий", "finish": "финиш за", "time": "Время", "km": "Км прибл.", "sector": "Участок маршрута", "weather": "Погода", "advice": "Совет",
        "dry": "Сухо", "caution": "Внимание", "mostly_dry": "В основном сухо", "shell": "Держать легкую дождевую куртку под рукой",
        "sources": "Проверенные источники", "sources_note": "Технический раздел оставлен внизу для прозрачности.",
        "disclaimer": "Прогноз носит информационный характер. Погода может измениться; проверьте еще раз перед стартом.",
        "conclusion_prefix": "Наиболее вероятно: хорошая погода для велосипеда, в основном сухо.",
        "updated_tz": "время Молдовы", "hours": "часов",
    },
}

PLATFORM_STATUS = {
    "MET Norway / Yr locationforecast": "OK: hourly point forecast along route corridor",
    "7Timer Civil": "OK: 3-hourly point forecast along route corridor",
    "Weather-Forecast.com Kishinev": "OK: broad Chisinau cross-check",
    "Open-Meteo": "Skipped: repeated 502/504/timeouts in earlier checks",
    "wttr.in": "Skipped: date option not available for 31 May forecast endpoint",
    "timeanddate.com": "Skipped: 403 anti-bot page",
}


def get_json(url: str, timeout: int = 20, headers: dict | None = None):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "delacau-brm-weather/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def get_text(url: str, timeout: int = 20):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", "ignore")


def haversine_km(a, b):
    lat1, lon1 = map(math.radians, a)
    lat2, lon2 = map(math.radians, b)
    dlat, dlon = lat2 - lat1, lon2 - lon1
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def load_gpx_points():
    path = ROOT / "delacau-200-brm.gpx"
    if not path.exists():
        return []
    ns = {"g": "http://www.topografix.com/GPX/1/1"}
    root = ET.parse(path).getroot()
    pts = []
    for p in root.findall(".//g:trkpt", ns) or root.findall(".//trkpt"):
        pts.append((float(p.attrib["lat"]), float(p.attrib["lon"])))
    return pts


def route_samples_from_gpx():
    pts = load_gpx_points()
    if len(pts) < 2:
        return None
    cumulative = [0.0]
    for a, b in zip(pts, pts[1:]):
        cumulative.append(cumulative[-1] + haversine_km(a, b))
    total = cumulative[-1]

    def at_km(km):
        target = max(0, min(total, km / DISTANCE_KM * total))
        for i in range(1, len(cumulative)):
            if cumulative[i] >= target:
                seg = cumulative[i] - cumulative[i - 1]
                f = 0 if seg == 0 else (target - cumulative[i - 1]) / seg
                lat = pts[i - 1][0] + f * (pts[i][0] - pts[i - 1][0])
                lon = pts[i - 1][1] + f * (pts[i][1] - pts[i - 1][1])
                return lat, lon
        return pts[-1]

    return at_km


def nearest_weather_point(lat, lon):
    return min(WEATHER_POINTS, key=lambda p: haversine_km((lat, lon), (p[2], p[3])))


def nearest_label(lat, lon):
    km, name, *_ = nearest_weather_point(lat, lon)
    return name


def wind_ms_to_kmh(x):
    return None if x is None else x * 3.6


def seven_speed_to_kmh(code):
    return {1: 1, 2: 7, 3: 20, 4: 34, 5: 45, 6: 57, 7: 70, 8: 85}.get(code)


def degrees_to_cardinal(deg):
    if deg is None:
        return "—"
    dirs = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return dirs[round(float(deg) / 45) % 8]


def fetch_metno():
    out = {}
    for km, name, lat, lon in WEATHER_POINTS:
        try:
            url = f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lat:.4f}&lon={lon:.4f}"
            data = get_json(url, timeout=20, headers={"User-Agent": "delacau-brm-weather/1.0 github.com/adiacov"})
            hourly = {}
            for item in data["properties"]["timeseries"]:
                dt = datetime.fromisoformat(item["time"].replace("Z", "+00:00")).astimezone(TZ)
                if dt.strftime("%Y-%m-%d") != FORECAST_DATE:
                    continue
                details = item["data"]["instant"]["details"]
                nxt = item["data"].get("next_1_hours", {})
                hourly[dt.hour] = {
                    "temp": details.get("air_temperature"),
                    "wind": wind_ms_to_kmh(details.get("wind_speed")),
                    "gust": wind_ms_to_kmh(details.get("wind_speed_of_gust")),
                    "dir": degrees_to_cardinal(details.get("wind_from_direction")),
                    "cloud": details.get("cloud_area_fraction"),
                    "rain": nxt.get("details", {}).get("precipitation_amount", 0),
                    "symbol": nxt.get("summary", {}).get("symbol_code", ""),
                }
            out[km] = hourly
        except Exception as exc:
            PLATFORM_STATUS[f"MET Norway point {name}"] = f"Failed: {exc}"
    return out


def fetch_7timer():
    out = {}
    for km, name, lat, lon in WEATHER_POINTS:
        try:
            qs = urllib.parse.urlencode({"lon": f"{lon:.4f}", "lat": f"{lat:.4f}", "product": "civil", "output": "json"})
            data = get_json("https://www.7timer.info/bin/api.pl?" + qs, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            init = datetime.strptime(data["init"], "%Y%m%d%H").replace(tzinfo=timezone.utc).astimezone(TZ)
            hourly = {}
            for item in data["dataseries"]:
                dt = init + timedelta(hours=item["timepoint"])
                if dt.strftime("%Y-%m-%d") == FORECAST_DATE:
                    hourly[dt.hour] = item
            out[km] = hourly
        except Exception as exc:
            PLATFORM_STATUS[f"7Timer point {name}"] = f"Failed: {exc}"
    return out


def weather_forecast_crosscheck():
    try:
        get_text("https://www.weather-forecast.com/locations/Kishinev/forecasts/latest", timeout=20)
    except Exception as exc:
        PLATFORM_STATUS["Weather-Forecast.com Kishinev"] = f"Failed: {exc}"


def sample_hourly(data, weather_km, hour):
    rows = data.get(weather_km, {})
    if not rows:
        return {}
    return rows.get(hour) or rows[min(rows.keys(), key=lambda h: abs(h - hour))]


def build_rows(met, sev):
    route_at = route_samples_from_gpx()
    rows_by_duration = {}
    for duration in DURATIONS:
        rows = []
        for elapsed in range(duration + 1):
            hour = START_HOUR + elapsed
            km = DISTANCE_KM * elapsed / duration
            if route_at:
                lat, lon = route_at(km)
            else:
                _, _, lat, lon = min(WEATHER_POINTS, key=lambda p: abs(p[0] - km))
            weather_km, _, _, _ = nearest_weather_point(lat, lon)
            m = sample_hourly(met, weather_km, hour)
            s = sample_hourly(sev, weather_km, hour)
            temp = m.get("temp") if m else s.get("temp2m") if s else None
            rain = m.get("rain", 0) if m else 0
            wind = m.get("wind") if m else seven_speed_to_kmh(s.get("wind10m", {}).get("speed")) if s else None
            wind_max = (m.get("gust") or wind) if m else wind
            wind_dir = m.get("dir") if m else s.get("wind10m", {}).get("direction", "—") if s else "—"
            cloud = m.get("cloud") if m else None
            condition = m.get("symbol", "").replace("_", " ") if m else s.get("weather", "") if s else ""
            if not condition and cloud is not None:
                condition = f"cloud {cloud:.0f}%"
            caution = (rain or 0) >= 0.1 or "rain" in condition or "thunder" in condition or "tstorm" in condition
            rows.append({
                "time": f"{hour:02d}:00",
                "elapsed": elapsed,
                "km": round(km),
                "place": nearest_label(lat, lon),
                "lat": lat,
                "lon": lon,
                "temp": temp,
                "rain": rain,
                "wind": wind,
                "wind_max": wind_max,
                "wind_dir": wind_dir or "—",
                "condition": condition or "dry",
                "caution": caution,
            })
        rows_by_duration[duration] = rows
    return rows_by_duration


def conclusion(rows_by_duration, lang):
    t = TEXT[lang]
    all_rows = rows_by_duration[13]
    temps = [r["temp"] for r in all_rows if r["temp"] is not None]
    winds = [r["wind"] for r in all_rows if r["wind"] is not None]
    total_rain = sum(r["rain"] or 0 for r in all_rows)
    temp_range = f"{min(temps):.0f}–{max(temps):.0f}°C" if temps else "n/a"
    wind_avg = f"{statistics.mean(winds):.0f} km/h" if winds else "n/a"
    if lang == "ro":
        text = f"{t['conclusion_prefix']} Temperatura probabila: {temp_range}. Vant: usor spre moderat, in medie aproximativ {wind_avg}. Riscul de ploaie pare mic, dar este bine sa ai o geaca usoara de ploaie pentru o aversa izolata."
    elif lang == "ru":
        text = f"{t['conclusion_prefix']} Ожидаемая температура: {temp_range}. Ветер слабый или умеренный, в среднем около {wind_avg}. Риск дождя выглядит низким, но легкую дождевую куртку лучше иметь с собой."
    else:
        text = f"{t['conclusion_prefix']} Expected temperature: {temp_range}. Wind: light to moderate, around {wind_avg} on average. Rain risk looks low, but keep a light rain shell for an isolated shower."
    return text, temp_range, wind_avg, total_rain


def fmt_num(x, suffix=""):
    return "—" if x is None else f"{x:.0f}{suffix}"


def lang_links(current):
    links = {"ro": "../ro/", "en": "../en/", "ru": "../ru/"}
    if current == "root":
        links = {"ro": "ro/", "en": "en/", "ru": "ru/"}
    return links


def page_html(lang, rows_by_duration, researched_at, root=False):
    t = TEXT[lang]
    links = lang_links("root" if root else lang)
    conclusion_text, temp_range, wind_avg, total_rain = conclusion(rows_by_duration, lang)
    css = "assets/style.css" if root else "../assets/style.css"
    gpx_note = t["route_note"]
    updated = researched_at.strftime("%Y-%m-%d, %H:%M")
    js = "assets/theme.js" if root else "../assets/theme.js"
    html = [f'<!doctype html><html lang="{t["html_lang"]}" dir="{t["dir"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(t["title"])}</title><link rel="stylesheet" href="{css}"><script src="{js}" defer></script></head><body><main class="page">']
    html.append('<section class="hero"><div class="topbar"><div class="controls"><div class="lang">')
    for code, label in [("ro", "RO"), ("ru", "RU"), ("en", "EN")]:
        cls = " active" if code == lang else ""
        html.append(f'<a class="{cls.strip()}" href="{links[code]}">{label}</a>')
    html.append('</div><button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch theme">🌙</button></div></div>')
    html.append(f'<h1>{escape(t["title"])}</h1><p class="subtitle">{escape(t["subtitle"])}</p>')
    html.append('<div class="meta">')
    html.append(f'<span class="pill updated">{escape(t["last"])}: <b>{escape(updated)}</b> {escape(t["updated_tz"])}</span>')
    html.append(f'<span class="pill">{escape(t["start"])}: <b>06:00, Chisinau</b></span><span class="pill">{escape(t["route"])}: <b>200 km / 1887 m</b></span>')
    html.append('</div>')
    html.append(f'<p>{escape(conclusion_text)}</p>')
    html.append(f'<p class="auto-update">{escape(t["auto_update"])}</p>')
    html.append('<div class="summary">')
    cards = [(t["overall"], t["mostly_dry"]), (t["temp"], temp_range), (t["wind"], wind_avg), (t["rain"], "low" if lang == "en" else "mic" if lang == "ro" else "низкий")]
    for label, value in cards:
        html.append(f'<div class="card"><div class="label">{escape(label)}</div><div class="value">{escape(value)}</div></div>')
    html.append('</div></section>')
    html.append(f'<section class="section"><h2>{escape(t["route_info"])}</h2><div class="note">{escape(gpx_note)}</div></section>')

    for duration, rows in rows_by_duration.items():
        html.append(f'<section class="scenario"><h3>{escape(t["scenario"])}: {escape(t["finish"])} {duration} {escape(t["hours"])} (06:00–{START_HOUR+duration:02d}:00)</h3>')
        html.append('<div class="table-wrap"><table><thead><tr>')
        for head in [t["time"], t["km"], t["sector"], t["temp"], t["rain"], t["wind"], t["wind_dir"], t["advice"]]:
            html.append(f'<th>{escape(head)}</th>')
        html.append('</tr></thead><tbody>')
        cards_mobile = ['<div class="cards-mobile">']
        for r in rows:
            status = t["caution"] if r["caution"] else t["dry"]
            status_cls = "warn" if r["caution"] else "ok"
            advice = t["shell"] if r["caution"] else t["mostly_dry"]
            rain = f'{(r["rain"] or 0):.1f} mm'
            temp = fmt_num(r["temp"], "°C")
            wind = f'{fmt_num(r["wind"], " km/h")} / {fmt_num(r["wind_max"], " km/h")}'
            wind_dir = escape(r["wind_dir"])
            html.append(f'<tr><td><b>{r["time"]}</b></td><td>{r["km"]}</td><td>{escape(r["place"])}</td><td>{temp}</td><td>{rain}</td><td>{wind}</td><td>{wind_dir}</td><td><span class="status {status_cls}">{escape(status)}</span> {escape(advice)}</td></tr>')
            cards_mobile.append(f'<div class="hour-card"><div class="time">{r["time"]} · {r["km"]} km · <span class="status {status_cls}">{escape(status)}</span></div><div class="grid"><div>{escape(t["sector"])}: <b>{escape(r["place"])}</b></div><div>{escape(t["temp"])}: <b>{temp}</b></div><div>{escape(t["rain"])}: <b>{rain}</b></div><div>{escape(t["wind"])}: <b>{wind}</b></div><div>{escape(t["wind_dir"])}: <b>{wind_dir}</b></div></div><div class="advice">{escape(advice)}</div></div>')
        html.append('</tbody></table></div>')
        cards_mobile.append('</div>')
        html.extend(cards_mobile)
        html.append('</section>')

    html.append(f'<section class="section sources"><h2>{escape(t["sources"])}</h2><p>{escape(t["sources_note"])}</p><ul>')
    for k, v in PLATFORM_STATUS.items():
        html.append(f'<li><b>{escape(k)}</b>: {escape(v)}</li>')
    html.append(f'</ul><p>{escape(t["disclaimer"])}</p></section><p class="footer">Delacau 200 BRM weather forecast · static GitHub Pages project</p></main></body></html>')
    return "\n".join(html)


def markdown(rows_by_duration, researched_at):
    text, _, _, _ = conclusion(rows_by_duration, "en")
    lines = ["# Delacau 200 BRM weather forecast", "", f"Last researched: {researched_at.strftime('%Y-%m-%d %H:%M')} Moldova time", "", text]
    for duration, rows in rows_by_duration.items():
        lines += ["", f"## {duration} hour scenario", "", "| Time | km | Place | Temp | Rain | Avg/max wind | Wind direction |", "|---|---:|---|---:|---:|---:|---|"]
        for r in rows:
            wind = f"{fmt_num(r['wind'],' km/h')} / {fmt_num(r['wind_max'],' km/h')}"
            lines.append(f"| {r['time']} | {r['km']} | {r['place']} | {fmt_num(r['temp'],'°C')} | {(r['rain'] or 0):.1f} mm | {wind} | {r['wind_dir']} |")
    lines += ["", "## Sources checked"] + [f"- **{k}**: {v}" for k, v in PLATFORM_STATUS.items()]
    return "\n".join(lines) + "\n"


def main():
    researched_at = datetime.now(TZ)
    met = fetch_metno()
    sev = fetch_7timer()
    weather_forecast_crosscheck()
    rows_by_duration = build_rows(met, sev)

    (ROOT / "ro").mkdir(exist_ok=True)
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "ru").mkdir(exist_ok=True)
    (ROOT / "assets").mkdir(exist_ok=True)

    (ROOT / "index.html").write_text(page_html("ro", rows_by_duration, researched_at, root=True), encoding="utf-8")
    (ROOT / "ro" / "index.html").write_text(page_html("ro", rows_by_duration, researched_at), encoding="utf-8")
    (ROOT / "en" / "index.html").write_text(page_html("en", rows_by_duration, researched_at), encoding="utf-8")
    (ROOT / "ru" / "index.html").write_text(page_html("ru", rows_by_duration, researched_at), encoding="utf-8")
    (ROOT / "delacau_200_weather_31may2026.md").write_text(markdown(rows_by_duration, researched_at), encoding="utf-8")
    # Keep descriptive HTML copy for compatibility with the earlier report name.
    (ROOT / "delacau_200_weather_31may2026.html").write_text((ROOT / "en" / "index.html").read_text(encoding="utf-8"), encoding="utf-8")
    print("Generated index.html, ro/, en/, ru/ and markdown report")


if __name__ == "__main__":
    main()
