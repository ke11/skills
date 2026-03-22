---
name: weather
description: "Query HK Observatory for real-time weather. Current conditions, 9-day forecast, warnings, and hourly rainfall."
allowed-tools: [Bash]
disable-model-invocation: true
argument-hint: "[detail | stations | forecast | warning | rainfall | all] [en | tc | sc] | <natural language question>"
---

Fetch live Hong Kong weather data from HKO Open Data API for: $ARGUMENTS

## Step 1: Parse Arguments

Split `$ARGUMENTS` by spaces into tokens. Separate into **keywords** and **language**:

- **Language tokens**: `en`, `tc`, `sc` — if found, use as `lang` parameter. Default: `tc`
- **Keywords** (case-insensitive):
  - `detail` → detailed mode (all stations + forecast)
  - `stations` → all station readings only
  - `forecast` → 9-day forecast mode
  - `warning` → warnings mode
  - `rainfall` → hourly rainfall mode
  - `all` → fetch everything
  - No keywords → **default mode**: quick weather summary

## Step 1b: Natural Language Intent Detection

Only run this step if no mode keyword was matched in Step 1.

If `$ARGUMENTS` contains no recognized keyword (step 1 set no mode), check the full raw `$ARGUMENTS` string for **intent patterns**. Check in priority order — the first matching pattern wins. Language tokens (`en`, `tc`, `sc`) must still be extracted first in Step 1, before this check runs.

### Intent Pattern Matching

1. **Rain intent** → set mode to `rain_query` if `$ARGUMENTS` contains any of:
   - Chinese: `落雨`, `下雨`, `會唔會落`, `會不會落`, `有冇雨`, `有沒有雨`, `幾時落雨`, `幾時下雨`, `落雨機會`, `下雨機會`, `降雨`, `雨勢`
   - English (case-insensitive): `rain`, `raining`, `rainfall`, `will it rain`, `going to rain`, `chance of rain`, `precipitation`

2. **Forecast intent** → set mode to `forecast` if `$ARGUMENTS` contains any of:
   - Chinese: `預報`, `天氣預測`, `未來天氣`, `9天`, `九天`, `幾天天氣`, `下星期天氣`, `本週天氣`, `下週天氣`, `天氣展望`, `明天天氣`, `後天天氣`, `預計天氣`
   - English (case-insensitive): `forecast`, `9-day`, `9 day`, `nine day`, `next week weather`, `this week weather`, `tomorrow weather`, `weather tomorrow`, `weather outlook`, `coming days`

3. **Temperature intent** → set mode to `stations` if `$ARGUMENTS` contains any of:
   - Chinese: `氣溫`, `幾度`, `溫度`, `熱唔熱`, `凍唔凍`, `係唔係熱`, `係唔係凍`, `好熱`, `好凍`, `熱嗎`, `凍嗎`, `天氣熱`, `天氣凍`, `現時溫度`
   - English (case-insensitive): `temperature`, `how hot`, `how cold`, `temp`, `degrees`, `celsius`, `warm today`, `cold today`, `is it hot`, `is it cold`

4. **UV intent** → set mode to `stations` if `$ARGUMENTS` contains any of:
   - Chinese: `紫外線`, `UV`, `曬`, `防曬`, `紫外`, `UV指數`
   - English (case-insensitive): `uv`, `ultraviolet`, `uv index`, `sun protection`, `sunburn`

5. **Humidity intent** → set mode to `stations` if `$ARGUMENTS` contains any of:
   - Chinese: `濕度`, `潮濕`, `幾濕`, `濕唔濕`, `濕嗎`
   - English (case-insensitive): `humidity`, `humid`, `how humid`, `moisture`

6. **Typhoon intent** → set mode to `warning` if `$ARGUMENTS` contains any of:
   - Chinese: `颱風`, `台風`, `風球`, `幾號風球`, `掛幾號`, `打風`, `熱帶氣旋`, `風暴`, `強風警告`, `颶風`
   - English (case-insensitive): `typhoon`, `tropical cyclone`, `signal`, `wind signal`, `t8`, `t3`, `no.8`, `no. 8`, `typhoon signal`, `storm signal`

7. **Warning intent** → set mode to `warning` if `$ARGUMENTS` contains any of:
   - Chinese: `警告`, `有冇警告`, `有沒有警告`, `黃色`, `紅色`, `黑色`, `暴雨警告`, `雷暴`, `霜凍`, `水浸`
   - English (case-insensitive): `warning`, `alert`, `red rain`, `black rain`, `yellow rain`, `thunderstorm warning`, `frost warning`

If no pattern matched → set mode to **default**.

## Step 2: Fetch Data

Base URL: `https://data.weather.gov.hk/weatherAPI/opendata/`

**IMPORTANT — parallel fetching**: When a mode requires multiple endpoints, fetch them ALL in a single Bash command using background processes (`&`) and `wait`. Write each response to a temp file, then read them all. This avoids slow sequential tool calls.

### Default Mode — quick summary (single endpoint):

```bash
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang={lang}"
```
Key fields: `generalSituation`, `forecastPeriod`, `forecastDesc`, `outlook`, `updateTime`

### Stations Mode — all station readings (single endpoint):

```bash
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang={lang}"
```
Key fields: `temperature.data[]` (place, value), `humidity.data[]` (place, value), `rainfall.data[]` (place, max, min), `uvindex`, `icon`, `warningMessage`, `updateTime`

### Detail Mode — fetch two in parallel:

```bash
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang={lang}" > /tmp/hko_rhrread.json &
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang={lang}" > /tmp/hko_flw.json &
wait
echo "===RHRREAD===" && cat /tmp/hko_rhrread.json && echo ""
echo "===FLW===" && cat /tmp/hko_flw.json && echo ""
rm -f /tmp/hko_rhrread.json /tmp/hko_flw.json
```

### Forecast Mode — 9-day forecast (single endpoint):

```bash
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang={lang}"
```
Key fields: `weatherForecast[]` — each has `forecastDate`, `week`, `forecastWeather`, `forecastMaxtemp.value`, `forecastMintemp.value`, `forecastMaxrh.value`, `forecastMinrh.value`, `forecastWind`, `PSR`, `ForecastIcon`

### Warnings Mode — fetch both in parallel:

```bash
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang={lang}" > /tmp/hko_warnsum.json &
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang={lang}" > /tmp/hko_warninfo.json &
wait
echo "===WARNSUM===" && cat /tmp/hko_warnsum.json && echo ""
echo "===WARNINGINFO===" && cat /tmp/hko_warninfo.json && echo ""
rm -f /tmp/hko_warnsum.json /tmp/hko_warninfo.json
```
`warningInfo` returns `details[]` with `contents[]` (array of text lines), `warningStatementCode`, optional `subtype`, `updateTime`

### Rainfall Mode — hourly rainfall (single endpoint):

```bash
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/hourlyRainfall.php?lang={lang}"
```
Key fields: `obsTime`, `hourlyRainfall[]` — each has `automaticWeatherStation`, `value`, `unit`

### All Mode — fetch all endpoints in parallel:

```bash
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang={lang}" > /tmp/hko_rhrread.json &
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warnsum&lang={lang}" > /tmp/hko_warnsum.json &
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang={lang}" > /tmp/hko_flw.json &
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang={lang}" > /tmp/hko_fnd.json &
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=warningInfo&lang={lang}" > /tmp/hko_warninfo.json &
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/hourlyRainfall.php?lang={lang}" > /tmp/hko_rainfall.json &
wait
echo "===RHRREAD===" && cat /tmp/hko_rhrread.json && echo ""
echo "===WARNSUM===" && cat /tmp/hko_warnsum.json && echo ""
echo "===FLW===" && cat /tmp/hko_flw.json && echo ""
echo "===FND===" && cat /tmp/hko_fnd.json && echo ""
echo "===WARNINGINFO===" && cat /tmp/hko_warninfo.json && echo ""
echo "===RAINFALL===" && cat /tmp/hko_rainfall.json && echo ""
rm -f /tmp/hko_rhrread.json /tmp/hko_warnsum.json /tmp/hko_flw.json /tmp/hko_fnd.json /tmp/hko_warninfo.json /tmp/hko_rainfall.json
```

### Rain Query Mode — fetch three in parallel:

```bash
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=rhrread&lang={lang}" > /tmp/hko_rhrread.json &
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=flw&lang={lang}" > /tmp/hko_flw.json &
curl -s "https://data.weather.gov.hk/weatherAPI/opendata/weather.php?dataType=fnd&lang={lang}" > /tmp/hko_fnd.json &
wait
echo "===RHRREAD===" && cat /tmp/hko_rhrread.json && echo ""
echo "===FLW===" && cat /tmp/hko_flw.json && echo ""
echo "===FND===" && cat /tmp/hko_fnd.json && echo ""
rm -f /tmp/hko_rhrread.json /tmp/hko_flw.json /tmp/hko_fnd.json
```

### Error Handling

After each curl response, check:
- If curl itself fails → report "Failed to reach HKO API" and continue to next endpoint
- If response is empty, null, or not valid JSON → report "No data available for {dataType}" and continue
- Always continue processing remaining endpoints if one fails

## Step 3: Present Results

### Default Mode Output (quick summary)

```
## 香港天氣概況

**更新時間**: {updateTime}

**概況**: {generalSituation}

**預報** ({forecastPeriod}): {forecastDesc}

**展望**: {outlook}
```

- Omit `generalSituation` line if empty
- Keep it compact — no tables, no section headers beyond the title

### Rain Query Mode Output

If `rhrread.warningMessage` is non-empty, display it prominently at the very top.

**For Traditional Chinese (tc/sc):**

```
## 降雨情況

{if warningMessage: show as highlighted alert}

**更新時間**: {updateTime from rhrread}

**目前降雨**:
{if any rainfall.data[].max > 0:}
| 地點 | 雨量 (mm) |
|------|----------|
| {place} | {max} |
| ... | ... |

{else:}
各區目前無錄得雨量

**今日降雨概率**: {fnd.weatherForecast[0].PSR}

**預報**: {flw.forecastDesc}

**展望**: {flw.outlook}

_資料來源：香港天文台_
```

**For English (en):**

```
## Rain Status

{if warningMessage: show as highlighted alert}

**Updated**: {updateTime from rhrread}

**Current Rainfall**:
{if any rainfall.data[].max > 0:}
| Station | Rainfall (mm) |
|---------|---------------|
| {place} | {max} |
| ... | ... |

{else:}
No rainfall currently recorded across stations

**Today's Rain Probability**: {fnd.weatherForecast[0].PSR}

**Forecast**: {flw.forecastDesc}

**Outlook**: {flw.outlook}

_Source: Hong Kong Observatory_
```

**Error handling for rain query mode:**
- If `rhrread` fails → omit Current Rainfall section, continue
- If `flw` fails → omit Forecast and Outlook sections, continue
- If `fnd` fails → omit Today's Rain Probability line silently, continue
- If any section is omitted due to failure, still show other data and attribution line

### Stations Mode Output

```
## 目前天氣

**更新時間**: {updateTime}
```

- Show temperature for all stations in a table
- Show humidity as a compact list
- For rainfall, only mention stations with max > 0. If all zero, say "各區無顯著雨量"
- If UV index data exists, show it
- If `warningMessage` is non-empty, show it prominently at the top

### Detail Mode Output

Show warning messages (from `rhrread.warningMessage`) if non-empty, then current conditions with all stations, then forecast.

```
## 香港天氣概況

**更新時間**: {updateTime from rhrread}
```

#### Current Conditions

```
### 目前天氣

| 地點 | 氣溫 (°C) |
|------|-----------|
| {place} | {value} |
| ... | ... |

**相對濕度**: {humidity place}: {value}%

**降雨**: {list any places with non-zero rainfall}
```

- Show temperature for all stations in a table
- Show humidity as a compact list (typically fewer stations)
- For rainfall, only mention stations with max > 0. If all zero, say "各區無顯著雨量"
- If UV index data exists, show it
- If `warningMessage` has content, display it prominently at the top

#### Forecast Section

```
### 天氣預報

**預報時段**: {forecastPeriod}

{forecastDesc}

**展望**: {outlook}
```

If `generalSituation` is non-empty, show it before the forecast description.

### Forecast Mode Output (9-day)

```
## 9天天氣預報

**更新時間**: {updateTime}

| 日期 | 星期 | 天氣 | 氣溫 (°C) | 濕度 (%) | 風向 | 降雨概率 |
|------|------|------|-----------|---------|------|---------|
| {MM/DD} | {week} | {forecastWeather} | {min}-{max} | {minrh}-{maxrh} | {forecastWind} | {PSR} |
| ... |
```

### Warnings Mode Output

```
## 天氣警告詳情

**更新時間**: {updateTime}
```

If no warnings active:
```
目前沒有任何天氣警告。
```

If warnings exist, for each warning in `warningInfo.details[]`:
```
### {warningStatementCode} {subtype if present}

{contents joined by newlines}

_更新: {updateTime}_
```

Also show summary table from `warnsum`:
```
| 警告 | 狀態 | 發出時間 |
|------|------|---------|
| {name} | {actionCode} | {issueTime} |
```

### Rainfall Mode Output

```
## 過去一小時雨量

**觀測時間**: {obsTime}

| 站點 | 雨量 (mm) |
|------|----------|
| {automaticWeatherStation} | {value} |
| ... |
```

- Filter out stations where `value` is `0` — unless ALL stations are 0, then show all with a note "各區過去一小時無錄得雨量"
- If `value` is `"M"` (maintenance), show as "維修中"
- Sort by rainfall amount descending (highest first)

### All Mode Output

Combine all sections in this order:
1. Warnings (if any)
2. Current conditions
3. Local forecast
4. 9-day forecast
5. Hourly rainfall

## Formatting Rules

- **Attribution**: Always append a source line at the end of ALL output, after all sections:
  - tc/sc: `_資料來源：香港天文台_`
  - en: `_Source: Hong Kong Observatory_`
- Temperatures: display as returned (integer or 1 decimal), with °C
- Humidity: integer, with %
- Rainfall: integer, mm
- Times: convert ISO 8601 timestamps to human-readable HKT format `YYYY-MM-DD HH:MM HKT` (e.g. `2026-03-22T02:45:00+08:00` → `2026-03-22 02:45 HKT`)
- 9-day forecast dates: convert `YYYYMMDD` to `MM/DD` format
- Omit null/empty fields silently — do not show placeholder text for missing data
- Use the language matching `lang` for section headers (tc/sc → Chinese headers as shown above; en → English headers like "Current Weather", "9-Day Forecast", etc.)

## Rules

- **Read-only** — only GET requests, never POST/PUT/DELETE
- Always use `curl -s` for silent mode
- Default language is `tc` (Traditional Chinese)
- If one endpoint fails, still process all remaining endpoints
- All HKO timestamps are in HKT (+08:00) — convert to `YYYY-MM-DD HH:MM HKT` format
- When presenting in English mode, use English section headers accordingly
