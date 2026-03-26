#!/usr/bin/env python3
"""Hong Kong Observatory weather query — fetches and formats HKO open data."""

import sys
import json
import re
from urllib.request import urlopen, Request
from urllib.error import URLError
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://data.weather.gov.hk/weatherAPI/opendata/"

ENDPOINTS = {
    "flw": "weather.php?dataType=flw&lang={}",
    "rhrread": "weather.php?dataType=rhrread&lang={}",
    "fnd": "weather.php?dataType=fnd&lang={}",
    "warnsum": "weather.php?dataType=warnsum&lang={}",
    "warninfo": "weather.php?dataType=warningInfo&lang={}",
    "rainfall": "hourlyRainfall.php?lang={}",
}

MODE_ENDPOINTS = {
    "default": ["flw"],
    "stations": ["rhrread"],
    "detail": ["rhrread", "flw"],
    "forecast": ["fnd"],
    "warning": ["warnsum", "warninfo"],
    "rainfall": ["rainfall"],
    "rain_query": ["rhrread", "flw", "fnd"],
    "all": ["rhrread", "warnsum", "flw", "fnd", "warninfo", "rainfall"],
}

# (mode, [regex_patterns]) — first match wins
INTENT_RULES = [
    ("rain_query", [
        r"落雨|下雨|會唔會落|會不會落|有冇雨|有沒有雨|幾時落雨|幾時下雨|落雨機會|下雨機會|降雨|雨勢",
        r"(?i)\brain|raining|rainfall|will it rain|going to rain|chance of rain|precipitation\b",
    ]),
    ("forecast", [
        r"預報|天氣預測|未來天氣|9天|九天|幾天天氣|下星期天氣|本週天氣|下週天氣|天氣展望|明天天氣|後天天氣|預計天氣",
        r"(?i)\bforecast|9.day|nine day|next week weather|this week weather|tomorrow weather|weather tomorrow|weather outlook|coming days\b",
    ]),
    ("stations", [
        r"氣溫|幾度|溫度|熱唔熱|凍唔凍|係唔係熱|係唔係凍|好熱|好凍|熱嗎|凍嗎|天氣熱|天氣凍|現時溫度",
        r"(?i)\btemperature|how hot|how cold|temp\b|degrees|celsius|warm today|cold today|is it hot|is it cold",
    ]),
    ("stations", [
        r"紫外線|UV|曬|防曬|紫外|UV指數",
        r"(?i)\buv\b|ultraviolet|uv index|sun protection|sunburn",
    ]),
    ("stations", [
        r"濕度|潮濕|幾濕|濕唔濕|濕嗎",
        r"(?i)\bhumidity|humid|how humid|moisture\b",
    ]),
    ("warning", [
        r"颱風|台風|風球|幾號風球|掛幾號|打風|熱帶氣旋|風暴|強風警告|颶風",
        r"(?i)\btyphoon|tropical cyclone|signal|wind signal|t[38]|no\.?\s?8|typhoon signal|storm signal\b",
    ]),
    ("warning", [
        r"警告|有冇警告|有沒有警告|黃色|紅色|黑色|暴雨警告|雷暴|霜凍|水浸",
        r"(?i)\bwarning|alert|red rain|black rain|yellow rain|thunderstorm warning|frost warning\b",
    ]),
]

LANG_TOKENS = {"en", "tc", "sc"}
MODE_TOKENS = {"detail", "stations", "forecast", "warning", "rainfall", "all"}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args(argv):
    lang = "tc"
    mode = None
    remaining = []

    for tok in argv:
        low = tok.lower()
        if low in LANG_TOKENS:
            lang = low
        elif low in MODE_TOKENS:
            mode = low
        else:
            remaining.append(tok)

    if mode:
        return mode, lang

    text = " ".join(remaining)
    if text:
        for intent_mode, patterns in INTENT_RULES:
            for pat in patterns:
                if re.search(pat, text):
                    return intent_mode, lang

    return "default", lang


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def sanitize(obj):
    """Recursively strip HTML tags and potential injection from all strings in API data."""
    if isinstance(obj, str):
        return re.sub(r'<[^>]+>', '', obj)
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v) for v in obj]
    return obj


def fetch_json(url):
    try:
        req = Request(url, headers={"User-Agent": "hk-weather-skill/1.0"})
        with urlopen(req, timeout=10) as resp:
            return sanitize(json.loads(resp.read()))
    except Exception:
        return None


def fetch_all(keys, lang):
    results = {}
    with ThreadPoolExecutor(max_workers=len(keys)) as pool:
        futures = {
            pool.submit(fetch_json, BASE + ENDPOINTS[k].format(lang)): k
            for k in keys
        }
        for f in as_completed(futures):
            results[futures[f]] = f.result()
    return results


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def fmt_time(ts):
    if not ts:
        return ""
    m = re.match(r"(\d{4}-\d{2}-\d{2})T(\d{2}:\d{2})", str(ts))
    return f"{m.group(1)} {m.group(2)} HKT" if m else str(ts)


def fmt_date(d):
    s = str(d)
    return f"{s[4:6]}/{s[6:8]}" if len(s) == 8 else s


def _l(lang, en, zh):
    return en if lang == "en" else zh


# ---------------------------------------------------------------------------
# Shared helpers for formatters
# ---------------------------------------------------------------------------

def _warning_lines(data):
    """Return blockquote lines for warningMessage, or empty list."""
    wm = data.get("warningMessage", "")
    if isinstance(wm, list):
        wm = " ".join(wm)
    if wm and wm.strip():
        return [f"> {wm.strip()}", ""]
    return []


def _rainfall_table(rains, lang, col_header=None):
    """Return markdown lines for a rainfall table built from rhrread rainfall data.

    *col_header* overrides the value-column label (default: ``Rainfall (mm)``
    in English, ``雨量 (mm)`` in Chinese).

    Returns a list of strings (without leading newline) — the caller decides
    how to join/prefix them.
    """
    wet = [r for r in rains if r.get("max") and r["max"] > 0]
    if wet:
        if col_header is None:
            col_header = _l(lang, "Rainfall (mm)", "雨量 (mm)")
        lines = [
            f"| {_l(lang, 'Station', '地點')} | {col_header} |",
            "|------|------|",
        ]
        for r in sorted(wet, key=lambda x: x.get("max", 0), reverse=True):
            lines.append(f"| {r['place']} | {r['max']} |")
        return lines
    return []


# ---------------------------------------------------------------------------
# Formatters
# ---------------------------------------------------------------------------

def format_default(data, lang):
    if not data:
        return ""
    lines = [f"## {_l(lang, 'Hong Kong Weather Summary', '香港天氣概況')}"]

    ut = fmt_time(data.get("updateTime"))
    if ut:
        lines.append(f"\n**{_l(lang, 'Updated', '更新時間')}**: {ut}")

    gs = data.get("generalSituation", "")
    if gs:
        lines.append(f"\n**{_l(lang, 'Overview', '概況')}**: {gs}")

    fp = data.get("forecastPeriod", "")
    fd = data.get("forecastDesc", "")
    if fd:
        label = _l(lang, "Forecast", "預報")
        lines.append(f"\n**{label}**{f' ({fp})' if fp else ''}: {fd}")

    ol = data.get("outlook", "")
    if ol:
        lines.append(f"\n**{_l(lang, 'Outlook', '展望')}**: {ol}")

    return "\n".join(lines)


def format_stations(data, lang):
    if not data:
        return ""
    lines = _warning_lines(data)

    lines.append(f"## {_l(lang, 'Current Weather', '目前天氣')}")

    ut = fmt_time(data.get("updateTime"))
    if ut:
        lines.append(f"\n**{_l(lang, 'Updated', '更新時間')}**: {ut}")

    # Temperature
    temps = data.get("temperature", {}).get("data", [])
    if temps:
        lines.append(f"\n### {_l(lang, 'Temperature', '氣溫')}\n")
        lines.append(f"| {_l(lang, 'Station', '地點')} | °C |")
        lines.append("|------|------|")
        for t in temps:
            v = t.get("value")
            if v is not None and v != "":
                lines.append(f"| {t['place']} | {v} |")

    # Humidity
    hums = data.get("humidity", {}).get("data", [])
    if hums:
        parts = [f"{h['place']}: {h['value']}%" for h in hums if h.get("value") is not None]
        if parts:
            lines.append(f"\n**{_l(lang, 'Humidity', '相對濕度')}**: {', '.join(parts)}")

    # Rainfall
    rains = data.get("rainfall", {}).get("data", [])
    if rains:
        table = _rainfall_table(rains, lang, col_header="mm")
        if table:
            lines.append(f"\n### {_l(lang, 'Rainfall', '降雨')}\n")
            lines += table
        else:
            lines.append(f"\n**{_l(lang, 'Rainfall', '降雨')}**: {_l(lang, 'No significant rainfall', '各區無顯著雨量')}")

    # UV index
    uv = data.get("uvindex")
    if isinstance(uv, dict) and uv.get("data"):
        for u in uv["data"]:
            if u.get("value") is not None:
                desc = f" ({u['desc']})" if u.get("desc") else ""
                lines.append(f"\n**{_l(lang, 'UV Index', '紫外線指數')}**: {u['place']} {u['value']}{desc}")

    return "\n".join(lines)


def format_forecast(data, lang):
    if not data:
        return ""
    lines = [f"## {_l(lang, '9-Day Forecast', '9天天氣預報')}"]

    ut = fmt_time(data.get("updateTime"))
    if ut:
        lines.append(f"\n**{_l(lang, 'Updated', '更新時間')}**: {ut}")

    forecasts = data.get("weatherForecast", [])
    if forecasts:
        hd = _l(lang, "Date", "日期")
        hw = _l(lang, "Day", "星期")
        hx = _l(lang, "Weather", "天氣")
        ht = _l(lang, "Temp (°C)", "氣溫 (°C)")
        hr = _l(lang, "RH (%)", "濕度 (%)")
        hf = _l(lang, "Wind", "風向")
        hp = _l(lang, "Rain %", "降雨概率")
        lines.append(f"\n| {hd} | {hw} | {hx} | {ht} | {hr} | {hf} | {hp} |")
        lines.append("|------|------|------|------|------|------|------|")
        for fc in forecasts:
            d = fmt_date(fc.get("forecastDate", ""))
            w = fc.get("week", "")
            wx = fc.get("forecastWeather", "")
            tmin = fc.get("forecastMintemp", {}).get("value", "")
            tmax = fc.get("forecastMaxtemp", {}).get("value", "")
            rmin = fc.get("forecastMinrh", {}).get("value", "")
            rmax = fc.get("forecastMaxrh", {}).get("value", "")
            wind = fc.get("forecastWind", "")
            psr = fc.get("PSR", "")
            lines.append(f"| {d} | {w} | {wx} | {tmin}-{tmax} | {rmin}-{rmax} | {wind} | {psr} |")

    return "\n".join(lines)


def format_warning(data, lang):
    warnsum = data.get("warnsum")
    warninfo = data.get("warninfo")
    lines = [f"## {_l(lang, 'Weather Warnings', '天氣警告詳情')}"]
    has_warnings = False

    if warninfo and isinstance(warninfo, dict) and warninfo.get("details"):
        has_warnings = True
        for detail in warninfo["details"]:
            code = detail.get("warningStatementCode", "")
            subtype = detail.get("subtype", "")
            header = f"### {code}"
            if subtype:
                header += f" {subtype}"
            lines.append(f"\n{header}\n")
            contents = detail.get("contents", [])
            if contents:
                lines.append("\n".join(str(c) for c in contents))
            wut = fmt_time(detail.get("updateTime"))
            if wut:
                lines.append(f"\n_{_l(lang, 'Updated', '更新')}: {wut}_")

    if warnsum and isinstance(warnsum, dict):
        active = {k: v for k, v in warnsum.items() if isinstance(v, dict) and v.get("name")}
        if active:
            has_warnings = True
            lines.append(f"\n### {_l(lang, 'Summary', '警告摘要')}\n")
            lines.append(f"| {_l(lang, 'Warning', '警告')} | {_l(lang, 'Status', '狀態')} | {_l(lang, 'Issued', '發出時間')} |")
            lines.append("|------|------|------|")
            for k, v in active.items():
                lines.append(f"| {v.get('name', k)} | {v.get('actionCode', '')} | {v.get('issueTime', '')} |")

    if not has_warnings:
        lines.append(f"\n{_l(lang, 'No weather warnings currently in effect.', '目前沒有任何天氣警告。')}")

    return "\n".join(lines)


def format_rainfall(data, lang):
    if not data:
        return ""
    lines = [f"## {_l(lang, 'Hourly Rainfall', '過去一小時雨量')}"]

    obs = data.get("obsTime")
    if obs:
        lines.append(f"\n**{_l(lang, 'Observation Time', '觀測時間')}**: {fmt_time(obs)}")

    readings = data.get("hourlyRainfall", [])
    if not readings:
        lines.append(f"\n{_l(lang, 'No data available.', '暫無數據。')}")
        return "\n".join(lines)

    wet = []
    maintenance = []
    for r in readings:
        v = r.get("value")
        name = r.get("automaticWeatherStation", "")
        if v == "M":
            maintenance.append(name)
        elif v is not None:
            try:
                fv = float(v)
                if fv > 0:
                    wet.append((name, fv))
            except ValueError:
                pass

    if wet:
        wet.sort(key=lambda x: x[1], reverse=True)
        lines.append(f"\n| {_l(lang, 'Station', '站點')} | {_l(lang, 'Rainfall (mm)', '雨量 (mm)')} |")
        lines.append("|------|------|")
        for name, val in wet:
            lines.append(f"| {name} | {val:g} |")
    else:
        lines.append(f"\n{_l(lang, 'No rainfall recorded in the past hour.', '各區過去一小時無錄得雨量。')}")

    if maintenance:
        lines.append(f"\n_{_l(lang, 'Under maintenance', '維修中')}: {', '.join(maintenance)}_")

    return "\n".join(lines)


def format_rain_query(data, lang):
    rhrread = data.get("rhrread")
    flw = data.get("flw")
    fnd = data.get("fnd")
    lines = []

    # Warning message
    if rhrread:
        lines += _warning_lines(rhrread)

    lines.append(f"## {_l(lang, 'Rain Status', '降雨情況')}")

    if rhrread:
        ut = fmt_time(rhrread.get("updateTime"))
        if ut:
            lines.append(f"\n**{_l(lang, 'Updated', '更新時間')}**: {ut}")

        rains = rhrread.get("rainfall", {}).get("data", [])
        lines.append(f"\n**{_l(lang, 'Current Rainfall', '目前降雨')}**:")
        table = _rainfall_table(rains, lang)
        if table:
            lines.append("")
            lines += table
        else:
            lines.append(f"\n{_l(lang, 'No rainfall currently recorded.', '各區目前無錄得雨量。')}")

    if fnd:
        forecasts = fnd.get("weatherForecast", [])
        if forecasts:
            psr = forecasts[0].get("PSR", "")
            if psr:
                label = _l(lang, "Today's Rain Probability", "今日降雨概率")
                lines.append(f"\n**{label}**: {psr}")

    if flw:
        fd = flw.get("forecastDesc", "")
        if fd:
            lines.append(f"\n**{_l(lang, 'Forecast', '預報')}**: {fd}")
        ol = flw.get("outlook", "")
        if ol:
            lines.append(f"\n**{_l(lang, 'Outlook', '展望')}**: {ol}")

    return "\n".join(lines)


def format_detail(data, lang):
    parts = []
    if data.get("rhrread"):
        parts.append(format_stations(data["rhrread"], lang))
    if data.get("flw"):
        parts.append(format_default(data["flw"], lang))
    return "\n\n".join(p for p in parts if p)


def format_all(data, lang):
    parts = []
    if data.get("warnsum") or data.get("warninfo"):
        parts.append(format_warning(data, lang))
    if data.get("rhrread"):
        parts.append(format_stations(data["rhrread"], lang))
    if data.get("flw"):
        parts.append(format_default(data["flw"], lang))
    if data.get("fnd"):
        parts.append(format_forecast(data["fnd"], lang))
    if data.get("rainfall"):
        parts.append(format_rainfall(data["rainfall"], lang))
    return "\n\n".join(p for p in parts if p)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

FORMATTERS = {
    "default": lambda d, l: format_default(d.get("flw") or {}, l),
    "stations": lambda d, l: format_stations(d.get("rhrread") or {}, l),
    "detail": format_detail,
    "forecast": lambda d, l: format_forecast(d.get("fnd") or {}, l),
    "warning": format_warning,
    "rainfall": lambda d, l: format_rainfall(d.get("rainfall") or {}, l),
    "rain_query": format_rain_query,
    "all": format_all,
}


def main():
    # $ARGUMENTS arrives as a single quoted string — split it here
    raw = " ".join(sys.argv[1:])
    args = raw.split() if raw.strip() else []
    mode, lang = parse_args(args)
    data = fetch_all(MODE_ENDPOINTS[mode], lang)

    if all(v is None for v in data.values()):
        print(_l(lang, "Failed to reach HKO API. Please try again later.",
                  "無法連接香港天文台 API，請稍後再試。"))
        sys.exit(1)

    output = FORMATTERS.get(mode, FORMATTERS["default"])(data, lang)
    attr = _l(lang, "_Source: Hong Kong Observatory_", "_資料來源：香港天文台_")
    print(f"---BEGIN---\n{output}\n\n{attr}\n---END---")


if __name__ == "__main__":
    main()
