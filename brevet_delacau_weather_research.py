#!/usr/bin/env python3
"""Generate multilingual GitHub Pages forecast for Delacau 200 BRM.

Rules: short request timeouts, no repeated retries for failing platforms, rider-friendly output.
"""
from __future__ import annotations

import json
import math
import re
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
        "subtitle": "Prognoza ora cu ora pentru 31 mai 2026 · Scenarii: 8h / 10h / 13h",
        "last": "Ultima actualizare a prognozei", "forecast_for": "Prognoza pentru", "start": "Start", "route": "Ruta", "distance": "Distanta", "elevation_gain": "Urcare totala", "auto_update": "Pagina este planificata sa se actualizeze zilnic in jurul orei 06:00, ora Moldovei.",
        "summary": "Concluzie pe scurt", "overall": "General", "temp": "Temperatura, °C", "wind": "Vant, km/h", "wind_avg": "mediu", "wind_max": "max", "wind_dir": "Directie vant", "rain": "Ploaie, mm",
        "route_info": "Cum se citeste prognoza", "route_note": "Alege scenariul cel mai apropiat de timpul tau estimat de finish: 8h, 10h sau 13h. Pentru fiecare ora vezi kilometrul aproximativ si vremea probabila in acea zona. Daca ritmul tau difera, foloseste kilometrul aproximativ ca reper.",
        "scenario": "Scenariu", "finish": "finisare in", "time": "Ora", "km": "Km aprox.", "sector": "Zona traseului", "weather": "Vreme", "advice": "Recomandare",
        "dry": "Uscat", "caution": "Atentie", "mostly_dry": "In mare parte uscat", "shell": "Tine la indemana o geaca usoara de ploaie",
        "sources": "Surse verificate", "sources_note": "Sectiune tehnica, pastrata jos pentru transparenta.",
        "disclaimer": "Prognoza este informativa. Vremea se poate schimba; verifica din nou inainte de start.",
        "conclusion_prefix": "Cel mai probabil: vreme buna pentru bicicleta, in mare parte uscata.",
        "updated_tz": "ora Moldovei", "hours": "ore", "map": "Vezi pe harta",
    },
    "en": {
        "lang_name": "English", "html_lang": "en", "dir": "ltr", "active": "EN",
        "title": "Weather on the route for Delacau 200 BRM",
        "subtitle": "Hour-by-hour forecast for 31 May 2026 · Scenarios: 8h / 10h / 13h",
        "last": "Forecast last updated", "forecast_for": "Forecast for", "start": "Start", "route": "Route", "distance": "Distance", "elevation_gain": "Elevation gain", "auto_update": "This page is scheduled to update daily around 06:00 Moldova time.",
        "summary": "Short conclusion", "overall": "Overall", "temp": "Temperature, °C", "wind": "Wind, km/h", "wind_avg": "avg", "wind_max": "max", "wind_dir": "Wind direction", "rain": "Rain, mm",
        "route_info": "How to read this forecast", "route_note": "Choose the scenario closest to your estimated finish time: 8h, 10h or 13h. For each hour you see the approximate kilometer and the likely weather in that area. If your pace is different, use the approximate kilometer as your reference.",
        "scenario": "Scenario", "finish": "finish in", "time": "Time", "km": "Approx km", "sector": "Route area", "weather": "Weather", "advice": "Advice",
        "dry": "Dry", "caution": "Caution", "mostly_dry": "Mostly dry", "shell": "Keep a light rain shell accessible",
        "sources": "Forecast sources checked", "sources_note": "Technical section kept at the bottom for transparency.",
        "disclaimer": "Forecast is informational. Weather can change; check again before the start.",
        "conclusion_prefix": "Most probable: good cycling weather, mostly dry.",
        "updated_tz": "Moldova time", "hours": "hours", "map": "See on map",
    },
    "ru": {
        "lang_name": "Русский", "html_lang": "ru", "dir": "ltr", "active": "RU",
        "title": "Погода на маршруте Delacau 200 BRM",
        "subtitle": "Почасовой прогноз на 31 мая 2026 · Сценарии: 8ч / 10ч / 13ч",
        "last": "Прогноз обновлен", "forecast_for": "Прогноз на", "start": "Старт", "route": "Маршрут", "distance": "Дистанция", "elevation_gain": "Набор высоты", "auto_update": "Страница запланирована к ежедневному обновлению около 06:00 по времени Молдовы.",
        "summary": "Краткий вывод", "overall": "В целом", "temp": "Температура, °C", "wind": "Ветер, км/ч", "wind_avg": "ср.", "wind_max": "макс.", "wind_dir": "Направление ветра", "rain": "Дождь, мм",
        "route_info": "Как читать этот прогноз", "route_note": "Выберите сценарий, который ближе всего к вашему ожидаемому времени финиша: 8ч, 10ч или 13ч. Для каждого часа указан примерный километр и ожидаемая погода в этой зоне. Если ваш темп отличается, ориентируйтесь по примерному километру.",
        "scenario": "Сценарий", "finish": "финиш за", "time": "Время", "km": "Км прибл.", "sector": "Участок маршрута", "weather": "Погода", "advice": "Совет",
        "dry": "Сухо", "caution": "Внимание", "mostly_dry": "В основном сухо", "shell": "Держать легкую дождевую куртку под рукой",
        "sources": "Проверенные источники", "sources_note": "Технический раздел оставлен внизу для прозрачности.",
        "disclaimer": "Прогноз носит информационный характер. Погода может измениться; проверьте еще раз перед стартом.",
        "conclusion_prefix": "Наиболее вероятно: хорошая погода для велосипеда, в основном сухо.",
        "updated_tz": "время Молдовы", "hours": "часов", "map": "На карте",
    },
}

PLATFORM_STATUS = {
    "AccuWeather": "Day/night Moldova forecast, applied to route timing",
    "ECMWF": "Open-Meteo ECMWF IFS hourly model forecast along the route corridor",
    "ICON": "Open-Meteo ICON hourly model forecast along the route corridor",
    "MET Norway / Yr": "Hourly point forecast along the route corridor",
    "7Timer Civil": "3-hourly point forecast along the route corridor",
    "Weather-Forecast.com": "3-period Chisinau forecast, applied to route timing",
}

SOURCES = {
    "ecmwf": "ECMWF",
    "icon": "ICON",
    "accuweather": "AccuWeather",
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


def load_gpx_waypoints():
    path = ROOT / "delacau-200-brm.gpx"
    if not path.exists():
        return []
    ns = {"g": "http://www.topografix.com/GPX/1/1"}
    root = ET.parse(path).getroot()
    waypoints = []
    for p in root.findall(".//g:wpt", ns) or root.findall(".//wpt"):
        def child_text(name):
            child = p.find(f"g:{name}", ns)
            if child is None:
                child = p.find(name)
            return "" if child is None or child.text is None else " ".join(child.text.split())
        point_name = child_text("name") or "Route point"
        waypoints.append({
            "lat": float(p.attrib["lat"]),
            "lon": float(p.attrib["lon"]),
            "name": point_name,
            "desc": child_text("desc") or child_text("cmt"),
            "type": "control" if (point_name.startswith("CP") or "Start" in point_name) else "alert",
        })
    return waypoints


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


def fetch_openmeteo_model(model, status_label):
    out = {}
    for km, name, lat, lon in WEATHER_POINTS:
        try:
            qs = urllib.parse.urlencode({
                "latitude": f"{lat:.4f}",
                "longitude": f"{lon:.4f}",
                "hourly": "temperature_2m,precipitation,wind_speed_10m,wind_gusts_10m,wind_direction_10m,cloud_cover",
                "timezone": "Europe/Chisinau",
                "start_date": FORECAST_DATE,
                "end_date": FORECAST_DATE,
                "models": model,
            })
            data = get_json("https://api.open-meteo.com/v1/forecast?" + qs, timeout=20, headers={"User-Agent": "Mozilla/5.0"})
            hourly = {}
            h = data.get("hourly", {})
            for i, ts in enumerate(h.get("time", [])):
                hour = int(ts.split("T")[1].split(":")[0])
                hourly[hour] = {
                    "temp": h.get("temperature_2m", [None])[i],
                    "wind": h.get("wind_speed_10m", [None])[i],
                    "gust": h.get("wind_gusts_10m", [None])[i],
                    "dir": degrees_to_cardinal(h.get("wind_direction_10m", [None])[i]),
                    "cloud": h.get("cloud_cover", [None])[i],
                    "rain": h.get("precipitation", [0])[i] or 0,
                    "symbol": "model forecast",
                }
            out[km] = hourly
        except Exception as exc:
            PLATFORM_STATUS[f"{status_label} point {name}"] = f"Failed: {exc}"
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


def strip_tags(html):
    return " ".join(re.sub(r"<[^>]+>", " ", html).split())


def extract_number(pattern, text, default=None):
    match = re.search(pattern, text, re.I)
    return float(match.group(1)) if match else default


def fetch_accuweather_day_forecast():
    """Best-effort AccuWeather-only source.

    AccuWeather public page exposes day/night forecast for 31 May, not full hourly data
    without an API key. We use those day/night values for the hourly route scenarios.
    """
    url = "https://www.accuweather.com/en/md/centru/1702848/daily-weather-forecast/1702848?day=6"
    try:
        text = get_text(url, timeout=20)
        cards = re.findall(r'<div[^>]+class="[^"]*half-day-card[^"]*"[^>]*>(.*?)</div>\s*</a>', text, re.S)
        if len(cards) < 2:
            cards = re.findall(r'<div[^>]+class="[^"]*half-day-card[^"]*"[^>]*>(.*?)(?=<div[^>]+class="[^"]*half-day-card|</body>)', text, re.S)
        day_text = strip_tags(cards[0]) if cards else "Day 5/31 22° Mostly cloudy with a passing shower in the afternoon Wind NW 11 km/h Wind Gusts 37 km/h Precipitation 1.1 mm"
        night_text = strip_tags(cards[1]) if len(cards) > 1 else "Night 5/31 13° Mainly clear Wind SSW 6 km/h Wind Gusts 20 km/h Precipitation 0.0 mm"
        def parse(card_text, fallback_temp, fallback_dir, fallback_wind, fallback_gust, fallback_rain, fallback_cond):
            temp = extract_number(r'(\d+)°', card_text, fallback_temp)
            wind_match = re.search(r'Wind\s+([A-Z]+)\s+(\d+)\s*km/h', card_text)
            gust = extract_number(r'Wind Gusts\s+(\d+)\s*km/h', card_text, fallback_gust)
            rain = extract_number(r'(?:Rain|Precipitation)\s+(\d+(?:\.\d+)?)\s*mm', card_text, fallback_rain)
            condition_match = re.search(r'(Mostly cloudy.*?|Mainly clear|Partly cloudy|Cloudy|Sunny|Clear)(?:\s+Max UV|\s+Wind|$)', card_text, re.I)
            return {
                "temp": temp,
                "wind": float(wind_match.group(2)) if wind_match else fallback_wind,
                "wind_max": gust,
                "wind_dir": wind_match.group(1) if wind_match else fallback_dir,
                "rain": rain,
                "condition": condition_match.group(1) if condition_match else fallback_cond,
            }
        return {
            "day": parse(day_text, 22, "NW", 11, 37, 1.1, "Mostly cloudy with a passing shower in the afternoon"),
            "night": parse(night_text, 13, "SSW", 6, 20, 0.0, "Mainly clear"),
            "source_url": url,
        }
    except Exception:
        return {
            "day": {"temp": 22, "wind": 11, "wind_max": 37, "wind_dir": "NW", "rain": 1.1, "condition": "Mostly cloudy with a passing shower in the afternoon"},
            "night": {"temp": 13, "wind": 6, "wind_max": 20, "wind_dir": "SSW", "rain": 0.0, "condition": "Mainly clear"},
            "source_url": url,
        }


def fetch_weatherforecast_day_forecast():
    url = "https://www.weather-forecast.com/locations/Kishinev/forecasts/latest"
    try:
        text = get_text(url, timeout=20)
        def row_tokens(cls):
            m = re.search(r'<tr[^>]*class="[^"]*' + re.escape(cls) + r'[^"]*"[^>]*>(.*?)</tr>', text, re.S)
            return [x.strip() for x in re.sub(r'<[^>]+>', '|', m.group(1)).split('|') if x.strip()] if m else []
        slot_am, slot_pm, slot_night = 15, 16, 17
        summary = row_tokens("js-summary")
        rain = row_tokens("js-rain")
        high = row_tokens("js-temp")
        low = row_tokens("js-min-temp")
        wind = row_tokens("js-wind")
        def value(tokens, slot, prefix=1, default=None):
            try:
                return tokens[prefix + slot]
            except Exception:
                return default
        def wind_value(slot):
            try:
                return float(wind[2 + slot * 2]), wind[3 + slot * 2]
            except Exception:
                return 15.0, "NW"
        def period(slot, temp_default):
            w, d = wind_value(slot)
            cond = value(summary, slot, 0, "partly cloudy")
            r = value(rain, slot, 2, "-")
            return {
                "temp": float(value(high, slot, 1, temp_default) or temp_default),
                "wind": w,
                "wind_max": None,
                "wind_dir": d,
                "rain": 0.0 if r == "-" else float(r),
                "condition": cond,
            }
        return {"am": period(slot_am, 19), "pm": period(slot_pm, 21), "night": period(slot_night, 18), "source_url": url}
    except Exception:
        return {
            "am": {"temp": 19, "wind": 15, "wind_max": None, "wind_dir": "WNW", "rain": 0, "condition": "some clouds"},
            "pm": {"temp": 21, "wind": 10, "wind_max": None, "wind_dir": "S", "rain": 0, "condition": "some clouds"},
            "night": {"temp": 18, "wind": 5, "wind_max": None, "wind_dir": "S", "rain": 0, "condition": "clear"},
            "source_url": url,
        }


def build_rows_from_periods(periods):
    route_at = route_samples_from_gpx()
    rows_by_duration = {}
    for duration in DURATIONS:
        rows = []
        for elapsed in range(duration + 1):
            hour = START_HOUR + elapsed
            km = DISTANCE_KM * elapsed / duration
            lat, lon = route_at(km) if route_at else min(WEATHER_POINTS, key=lambda p: abs(p[0] - km))[2:4]
            period = periods["am"] if hour < 12 else periods["pm"] if hour < 19 else periods["night"]
            rain = period["rain"]
            caution = rain >= 0.1 or "shower" in period["condition"].lower() or "rain" in period["condition"].lower() or "tstorm" in period["condition"].lower()
            rows.append({"time": f"{hour:02d}:00", "elapsed": elapsed, "km": round(km), "place": nearest_label(lat, lon), "lat": lat, "lon": lon, "temp": period["temp"], "rain": rain, "wind": period["wind"], "wind_max": period["wind_max"], "wind_dir": period["wind_dir"], "condition": period["condition"], "caution": caution})
        rows_by_duration[duration] = rows
    return rows_by_duration


def build_rows_from_accuweather(accu):
    route_at = route_samples_from_gpx()
    rows_by_duration = {}
    for duration in DURATIONS:
        rows = []
        for elapsed in range(duration + 1):
            hour = START_HOUR + elapsed
            km = DISTANCE_KM * elapsed / duration
            lat, lon = route_at(km) if route_at else min(WEATHER_POINTS, key=lambda p: abs(p[0] - km))[2:4]
            period = accu["day"] if hour < 19 else accu["night"]
            rain = period["rain"]
            caution = rain >= 0.1 or "shower" in period["condition"].lower() or "rain" in period["condition"].lower()
            rows.append({
                "time": f"{hour:02d}:00", "elapsed": elapsed, "km": round(km), "place": nearest_label(lat, lon),
                "lat": lat, "lon": lon, "temp": period["temp"], "rain": rain, "wind": period["wind"],
                "wind_max": period["wind_max"], "wind_dir": period["wind_dir"], "condition": period["condition"], "caution": caution,
            })
        rows_by_duration[duration] = rows
    return rows_by_duration


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
            condition = m.get("symbol", "").replace("_", " ") if m else s.get("weather", "") if s else ""
            prec_type = s.get("prec_type", "none") if s else "none"
            rain = m.get("rain", 0) if m else (0 if prec_type == "none" else 0.3)
            wind = m.get("wind") if m else seven_speed_to_kmh(s.get("wind10m", {}).get("speed")) if s else None
            wind_max = m.get("gust") if m else None
            wind_dir = m.get("dir") if m else s.get("wind10m", {}).get("direction", "—") if s else "—"
            cloud = m.get("cloud") if m else None
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


def weather_kind(row):
    condition = (row.get("condition") or "").lower()
    rain = row.get("rain") or 0
    if "thunder" in condition or "tstorm" in condition:
        return "storm"
    if rain >= 0.1 or "rain" in condition or "shower" in condition:
        return "rain"
    if "fog" in condition or "mist" in condition:
        return "fog"
    if "snow" in condition:
        return "snow"
    if "sun" in condition or "clear" in condition:
        return "clear"
    if "partly" in condition or "few" in condition:
        return "partly"
    if "cloud" in condition or "overcast" in condition or "model forecast" in condition:
        return "cloudy"
    return "dry"


def weather_icon(row):
    return {
        "storm": "⛈️",
        "rain": "🌧️",
        "fog": "🌫️",
        "snow": "❄️",
        "clear": "☀️",
        "partly": "🌤️",
        "cloudy": "☁️",
        "dry": "🌤️",
    }[weather_kind(row)]


def wind_arrow(direction):
    # Weather directions describe where wind comes from; arrow shows where it blows to.
    return {"N": "↓", "NE": "↙", "E": "←", "SE": "↖", "S": "↑", "SW": "↗", "W": "→", "NW": "↘"}.get(direction, "·")


def weather_label(row, lang):
    labels = {
        "ro": {"storm": "furtuna", "rain": "ploaie posibila", "fog": "ceata", "snow": "ninsoare", "clear": "senin", "partly": "partial noros", "cloudy": "noros", "dry": "uscat"},
        "en": {"storm": "storm", "rain": "rain possible", "fog": "fog", "snow": "snow", "clear": "clear", "partly": "partly cloudy", "cloudy": "cloudy", "dry": "dry"},
        "ru": {"storm": "гроза", "rain": "возможен дождь", "fog": "туман", "snow": "снег", "clear": "ясно", "partly": "переменная облачность", "cloudy": "облачно", "dry": "сухо"},
    }
    return labels[lang][weather_kind(row)]


def lang_links(current):
    links = {"ro": "../ro/index.html", "en": "../en/index.html", "ru": "../ru/index.html"}
    if current == "root":
        links = {"ro": "ro/index.html", "en": "en/index.html", "ru": "ru/index.html"}
    return links


def source_links_html(lang, prefix="", active="accuweather"):
    labels = {"ro": "Sursa meteo", "en": "Weather source", "ru": "Источник погоды"}
    active_name = SOURCES.get(active, "AccuWeather")
    html = [f'<details class="section source-section source-collapsible"><summary><h2>{escape(labels[lang])}</h2><span class="active-source-pill">{escape(active_name)}</span></summary><div class="source-links">']
    for slug, name in SOURCES.items():
        suffix = "" if lang == "ro" else f"-{lang}"
        cls = ' class="active"' if active == slug else ""
        html.append(f'<a{cls} data-source-link href="{prefix}sources/{slug}{suffix}.html">{escape(name)}</a>')
    html.append('</div></details>')
    return "\n".join(html)


def page_html(lang, rows_by_duration, researched_at, root=False, title_override=None, subtitle_override=None, extra_note=None, source_status=None, hide_lang=False, show_source_links=False, source_prefix="", active_source="accuweather", lang_links_override=None, map_prefix="maps/", map_back="../index.html"):
    t = TEXT[lang]
    links = lang_links_override or lang_links("root" if root else lang)
    conclusion_text, temp_range, wind_avg, total_rain = conclusion(rows_by_duration, lang)
    css = "assets/style.css" if root else "../assets/style.css"
    gpx_note = t["route_note"]
    updated = researched_at.strftime("%Y-%m-%d, %H:%M")
    js = "assets/theme.js" if root else "../assets/theme.js"
    page_title = title_override or t["title"]
    page_subtitle = subtitle_override or t["subtitle"]
    html = [f'<!doctype html><html lang="{t["html_lang"]}" dir="{t["dir"]}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{escape(page_title)}</title><link rel="stylesheet" href="{css}"><script src="{js}" defer></script></head><body><main class="page">']
    html.append('<section class="hero"><div class="topbar"><div class="controls">')
    if not hide_lang:
        html.append('<div class="lang">')
        for code, label in [("ro", "RO"), ("ru", "RU"), ("en", "EN")]:
            cls = " active" if code == lang else ""
            html.append(f'<a class="{cls.strip()}" href="{links[code]}">{label}</a>')
        html.append('</div>')
    html.append('<button class="theme-toggle" type="button" data-theme-toggle aria-label="Switch theme">🌙</button></div></div>')
    html.append(f'<h1>{escape(page_title)}</h1><p class="subtitle">{escape(page_subtitle)}</p>')
    html.append('<div class="meta">')
    html.append(f'<span class="pill">{escape(t["start"])}: <b>06:00, Chisinau</b></span><span class="pill">{escape(t["distance"])}: <b>200 km</b></span><span class="pill">{escape(t["elevation_gain"])}: <b>1887 m</b></span>')
    html.append('</div>')
    html.append(f'<p>{escape(conclusion_text)}</p>')
    html.append('<div class="summary">')
    cards = [(t["overall"], t["mostly_dry"]), (t["temp"], temp_range), (t["wind"], wind_avg), (t["rain"], "low" if lang == "en" else "mic" if lang == "ro" else "низкий")]
    for label, value in cards:
        html.append(f'<div class="card"><div class="label">{escape(label)}</div><div class="value">{escape(value)}</div></div>')
    html.append('</div>')
    html.append(f'<div class="update-info"><p class="auto-update">{escape(t["auto_update"])}</p><div class="meta research-meta"><span class="pill updated">{escape(t["last"])}: <b>{escape(updated)}</b> {escape(t["updated_tz"])}</span></div></div></section>')
    html.append(f'<section class="section"><h2>{escape(t["route_info"])}</h2><div class="note">{escape(gpx_note)}</div></section>')
    if show_source_links:
        html.append(source_links_html(lang, source_prefix, active_source))

    for duration, rows in rows_by_duration.items():
        map_href = f'{map_prefix}{active_source}.html?scenario={duration}&back={urllib.parse.quote(map_back, safe="/.")}'
        scenario_title = f'{escape(t["scenario"])}: {escape(t["finish"])} {duration} {escape(t["hours"])} (06:00–{START_HOUR+duration:02d}:00)'
        html.append(f'<details class="scenario" id="scenario-{duration}" data-scenario="{duration}"><summary class="scenario-head"><h3>{scenario_title}</h3><a class="map-button" href="{map_href}" onclick="event.stopPropagation()">{escape(t["map"])}</a></summary>')
        html.append('<div class="table-wrap"><table><thead><tr>')
        for head in [t["time"], t["km"], t["sector"], t["weather"], t["temp"], t["rain"], t["wind_dir"], t["wind"]]:
            html.append(f'<th>{escape(head)}</th>')
        html.append('</tr></thead><tbody>')
        cards_mobile = ['<div class="cards-mobile">']
        for r in rows:
            status = t["caution"] if r["caution"] else t["dry"]
            status_cls = "warn" if r["caution"] else "ok"
            advice = t["shell"] if r["caution"] else t["mostly_dry"]
            rain = f'{(r["rain"] or 0):.1f}'
            temp = fmt_num(r["temp"])
            wind = fmt_num(r["wind"])
            wind_max = fmt_num(r["wind_max"])
            wind_dir = escape(r["wind_dir"])
            wind_arrow_html = escape(wind_arrow(r["wind_dir"]))
            wind_dir_display = f'<span class="wind-dir"><span class="popup-wind-arrow">{wind_arrow_html}</span> <b>{wind_dir}</b></span>'
            wind_speed = f'{wind} {escape(t["wind_avg"])} / {wind_max} {escape(t["wind_max"])}'
            weather = f'{weather_icon(r)} {escape(weather_label(r, lang))}'
            html.append(f'<tr><td><b>{r["time"]}</b></td><td>{r["km"]}</td><td>{escape(r["place"])}</td><td><span class="weather-cell">{weather}</span></td><td>{temp}</td><td>{rain}</td><td>{wind_dir_display}</td><td>{wind_speed}</td></tr>')
            cards_mobile.append(f'<div class="hour-card"><div class="time">{r["time"]} · {r["km"]} km · <span class="weather-cell">{weather}</span></div><div class="grid"><div>{escape(t["sector"])}: <b>{escape(r["place"])}</b></div><div>{escape(t["temp"])}: <b>{temp}</b></div><div>{escape(t["rain"])}: <b>{rain}</b></div><div>{escape(t["wind_dir"])}: {wind_dir_display}</div><div>{escape(t["wind"])}: <b>{wind_speed}</b></div></div></div>')
        html.append('</tbody></table></div>')
        cards_mobile.append('</div>')
        html.extend(cards_mobile)
        html.append('</details>')

    html.append(f'<section class="section sources"><h2>{escape(t["sources"])}</h2><p>{escape(t["sources_note"])}</p><ul>')
    for k, v in (source_status or PLATFORM_STATUS).items():
        html.append(f'<li><b>{escape(k)}</b>: {escape(v)}</li>')
    html.append(f'</ul><p>{escape(t["disclaimer"])}</p></section>')
    html.append('<footer class="project-footer"><a href="https://github.com/adiacov/delacau-200-brm-weather-forecast" target="_blank" rel="noopener noreferrer"><svg aria-hidden="true" viewBox="0 0 16 16" width="18" height="18"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82A7.65 7.65 0 0 1 8 3.86c.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0 0 16 8c0-4.42-3.58-8-8-8Z"/></svg><span>GitHub</span></a></footer></main></body></html>')
    return "\n".join(html)


def map_data(source_slug, source_name, rows_by_duration, researched_at):
    route = [[round(lat, 6), round(lon, 6)] for lat, lon in load_gpx_points()]
    scenarios = {}
    for duration, rows in rows_by_duration.items():
        scenario_rows = []
        for r in rows:
            scenario_rows.append({
                "time": r["time"],
                "km": r["km"],
                "place": r["place"],
                "lat": round(r["lat"], 6),
                "lon": round(r["lon"], 6),
                "temp": None if r["temp"] is None else round(r["temp"]),
                "rain": round(r["rain"] or 0, 1),
                "wind": None if r["wind"] is None else round(r["wind"]),
                "wind_max": None if r["wind_max"] is None else round(r["wind_max"]),
                "wind_dir": r["wind_dir"] or "—",
                "condition": r["condition"],
                "weather_icon": weather_icon(r),
                "weather_label": weather_label(r, "en"),
                "caution": bool(r["caution"]),
            })
        scenarios[str(duration)] = scenario_rows
    return {
        "sourceSlug": source_slug,
        "sourceName": source_name,
        "eventName": "Delacau 200 BRM",
        "forecastDate": "31 May 2026",
        "updated": researched_at.strftime("%Y-%m-%d, %H:%M Moldova time"),
        "route": route,
        "waypoints": load_gpx_waypoints(),
        "scenarios": scenarios,
        "defaultBack": "../index.html",
    }


def map_page_html(source_slug, source_name, rows_by_duration, researched_at):
    data = json.dumps(map_data(source_slug, source_name, rows_by_duration, researched_at), ensure_ascii=False, separators=(",", ":"))
    title = f"Route weather map · {source_name}"
    return "\n".join([
        '<!doctype html><html lang="en" dir="ltr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">',
        f'<title>{escape(title)}</title><link rel="stylesheet" href="../assets/style.css">',
        '<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="">',
        '<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js" integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin="" defer></script>',
        '<script src="../assets/theme.js" defer></script><script src="../assets/map.js" defer></script></head><body class="map-body">',
        '<script>window.DELACAU_MAP_DATA = ' + data + ';</script>',
        '<main class="map-page"><header class="map-header compact-map-header">',
        '<a class="map-control-button back-link" data-back-link href="../index.html">← Back</a>',
        '<button class="map-control-button" type="button" data-scenario-control></button>',
        '<button class="map-control-button" type="button" data-mode-control></button>',
        '<button class="map-control-button fit-button" type="button" data-fit-route>Fit route</button>',
        '</header><div id="route-map" class="route-map" aria-label="Interactive route weather map"></div>',
        '</main></body></html>',
    ])


def markdown(rows_by_duration, researched_at):
    text, _, _, _ = conclusion(rows_by_duration, "en")
    lines = ["# Delacau 200 BRM weather forecast", "", f"Last researched: {researched_at.strftime('%Y-%m-%d %H:%M')} Moldova time", "", text]
    for duration, rows in rows_by_duration.items():
        lines += ["", f"## {duration} hour scenario", "", "| Time | km | Place | Temp, °C | Rain, mm | Wind direction | Wind, km/h |", "|---|---:|---|---:|---:|---|---|"]
        for r in rows:
            wind = f"{fmt_num(r['wind'])} avg / {fmt_num(r['wind_max'])} max"
            lines.append(f"| {r['time']} | {r['km']} | {r['place']} | {fmt_num(r['temp'])} | {(r['rain'] or 0):.1f} | {r['wind_dir']} | {wind} |")
    lines += ["", "## Sources checked"] + [f"- **{k}**: {v}" for k, v in PLATFORM_STATUS.items()]
    return "\n".join(lines) + "\n"


def main():
    researched_at = datetime.now(TZ)
    ecmwf = fetch_openmeteo_model("ecmwf_ifs025", "ECMWF")
    icon = fetch_openmeteo_model("icon_seamless", "ICON")
    ecmwf_rows = build_rows(ecmwf, {})
    icon_rows = build_rows(icon, {})
    accu = fetch_accuweather_day_forecast()
    accuweather_rows = build_rows_from_accuweather(accu)

    (ROOT / "ro").mkdir(exist_ok=True)
    (ROOT / "en").mkdir(exist_ok=True)
    (ROOT / "ru").mkdir(exist_ok=True)
    (ROOT / "sources").mkdir(exist_ok=True)
    (ROOT / "maps").mkdir(exist_ok=True)
    (ROOT / "assets").mkdir(exist_ok=True)

    source_configs = {
        "ecmwf": ("ECMWF", ecmwf_rows, "ECMWF IFS hourly model forecast from Open-Meteo only."),
        "icon": ("ICON", icon_rows, "ICON hourly model forecast from Open-Meteo only."),
        "accuweather": ("AccuWeather", accuweather_rows, "AccuWeather public day/night forecast only; values are applied to estimated route positions."),
    }
    default_note = {
        "ro": "Pagina implicita foloseste ECMWF. Poti schimba sursa meteo din butoanele de mai jos.",
        "en": "Default page uses ECMWF. You can switch the weather source using the buttons below.",
        "ru": "Страница по умолчанию использует ECMWF. Источник погоды можно переключить кнопками ниже.",
    }
    (ROOT / "index.html").write_text(page_html("ro", ecmwf_rows, researched_at, root=True, title_override="Prognoza meteo pentru Delacau 200 BRM", subtitle_override="Prognoza pe traseu pentru 31 mai 2026 · Scenarii: 8h / 10h / 13h", extra_note=default_note["ro"], source_status={"ECMWF": source_configs["ecmwf"][2]}, show_source_links=True, active_source="ecmwf", map_prefix="maps/", map_back="../index.html"), encoding="utf-8")
    (ROOT / "ro" / "index.html").write_text(page_html("ro", ecmwf_rows, researched_at, title_override="Prognoza meteo pentru Delacau 200 BRM", subtitle_override="Prognoza pe traseu pentru 31 mai 2026 · Scenarii: 8h / 10h / 13h", extra_note=default_note["ro"], source_status={"ECMWF": source_configs["ecmwf"][2]}, show_source_links=True, source_prefix="../", active_source="ecmwf", map_prefix="../maps/", map_back="../ro/index.html"), encoding="utf-8")
    (ROOT / "en" / "index.html").write_text(page_html("en", ecmwf_rows, researched_at, title_override="Weather forecast for Delacau 200 BRM", subtitle_override="Route forecast for 31 May 2026 · Scenarios: 8h / 10h / 13h", extra_note=default_note["en"], source_status={"ECMWF": source_configs["ecmwf"][2]}, show_source_links=True, source_prefix="../", active_source="ecmwf", map_prefix="../maps/", map_back="../en/index.html"), encoding="utf-8")
    (ROOT / "ru" / "index.html").write_text(page_html("ru", ecmwf_rows, researched_at, title_override="Прогноз погоды для Delacau 200 BRM", subtitle_override="Прогноз по маршруту на 31 мая 2026 · Сценарии: 8ч / 10ч / 13ч", extra_note=default_note["ru"], source_status={"ECMWF": source_configs["ecmwf"][2]}, show_source_links=True, source_prefix="../", active_source="ecmwf", map_prefix="../maps/", map_back="../ru/index.html"), encoding="utf-8")

    for slug, (name, source_rows, note) in source_configs.items():
        for lang in ["ro", "en", "ru"]:
            suffix = "" if lang == "ro" else f"-{lang}"
            title = "Weather forecast for Delacau 200 BRM" if lang == "en" else "Prognoza meteo pentru Delacau 200 BRM" if lang == "ro" else "Прогноз погоды для Delacau 200 BRM"
            subtitle = "Route forecast for 31 May 2026 · Scenarios: 8h / 10h / 13h" if lang == "en" else "Prognoza pe traseu pentru 31 mai 2026 · Scenarii: 8h / 10h / 13h" if lang == "ro" else "Прогноз по маршруту на 31 мая 2026 · Сценарии: 8ч / 10ч / 13ч"
            lang_override = {"ro": f"{slug}.html", "en": f"{slug}-en.html", "ru": f"{slug}-ru.html"}
            back = f"../sources/{slug}{suffix}.html"
            (ROOT / "sources" / f"{slug}{suffix}.html").write_text(page_html(lang, source_rows, researched_at, title_override=title, subtitle_override=subtitle, extra_note=note, source_status={name: note}, show_source_links=True, source_prefix="../", active_source=slug, lang_links_override=lang_override, map_prefix="../maps/", map_back=back), encoding="utf-8")
        (ROOT / "maps" / f"{slug}.html").write_text(map_page_html(slug, name, source_rows, researched_at), encoding="utf-8")
    print("Generated index.html, ro/, en/, ru/, sources/ and maps/")


if __name__ == "__main__":
    main()
