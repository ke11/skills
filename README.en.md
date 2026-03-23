# Hong Kong AI Agent Skills

[繁體中文](README.md) | English

> **Beta** — This project is in casual active development. Skills, APIs, and configuration formats may change without notice. We welcome feedback and contributions.

AI agent skills designed for Hong Kong.

---

## Installation

```bash
npx skills add ke11/skills --skill hk-weather
```

---

## Skills

### weather — Hong Kong Weather

Fetches real-time weather data from the [Hong Kong Observatory Open Data API](https://data.weather.gov.hk/weatherAPI/doc/HKO_Open_Data_API_Documentation.pdf). No API key required.

#### Usage

**Keyword Commands** (Precise Mode) — Use specific keywords to get targeted data:

| Command | Data | APIs | Speed |
|---------|------|------|-------|
| `/hk-weather` | Weather summary | 1 | Fast |
| `/hk-weather stations` | Station temps, humidity, rainfall | 1 | Fast |
| `/hk-weather forecast` | 9-day forecast | 1 | Fast |
| `/hk-weather rainfall` | Hourly rainfall | 1 | Fast |
| `/hk-weather warning` | Active warnings | 2 | Medium |
| `/hk-weather detail` | All stations + forecast | 2 | Medium |
| `/hk-weather all` | Everything | 6 | Slow |

**Natural Language Questions** (Relaxed Mode) — No need to memorize keywords, just ask in English:

| Example question | Function |
|---|---|
| `/hk-weather will it rain today?` | Rain query |
| `/hk-weather is it raining?` | Rain query |
| `/hk-weather is there a typhoon?` | Typhoon / warnings |
| `/hk-weather what signal is up?` | Typhoon / warnings |
| `/hk-weather any rainstorm warning?` | Weather warnings |
| `/hk-weather how hot is it?` | Station temperatures |
| `/hk-weather is it humid?` | Station humidity |
| `/hk-weather UV index?` | UV index |
| `/hk-weather weather next week?` | 9-day forecast |

**Language Codes** — Append a language code to the end of any command to switch output language:

| Code | Language | Example |
|------|----------|---------|
| `en` | English | `/hk-weather forecast en` |
| `tc` | Traditional Chinese (default) | `/hk-weather forecast tc` |
| `sc` | Simplified Chinese | `/hk-weather forecast sc` |

#### Example Output

```
● Hong Kong Weather Overview

Updated: 2026-03-22 20:45 HKT

Overview: The easterly airstream affecting the coast of Guangdong is gradually moderating.

Forecast (Weather forecast for Hong Kong): Mainly cloudy. Minimum temperature around 21 degrees. Sunny periods during the day with a maximum of around 27 degrees. Light easterly winds.

Outlook: Sunny periods in the following few days. Hot during the day from mid to late week.

Source: Hong Kong Observatory
```

---

### kmb-eta — KMB/LWB Bus ETA

Fetches real-time bus arrival times from the [KMB Open Data API](https://data.etabus.gov.hk). Supports GPS auto-detection of the nearest bus stop. No API key required.

#### Usage

```
/kmb-eta <route> [bus stop] [I|O] [en|tc|sc]
```

| Command | Description |
|---------|-------------|
| `/kmb-eta 42C` | Auto-detect nearest stop, query route 42C ETA |
| `/kmb-eta 42C 長亨 O` | Query 42C outbound at Cheung Hang stop |
| `/kmb-eta 42C stops` | List all stops on route 42C (find stop names) |
| `/kmb-eta 960 建生 I en` | Query 960 inbound at Kin Sang (English output) |

- **Auto-location mode**: Only route number required — uses macOS GPS to find the nearest stop and direction automatically
- **Manual mode**: Provide route + stop keyword + direction (I=inbound / O=outbound)
- **Languages**: `tc` Traditional Chinese (default), `en` English, `sc` Simplified Chinese

#### Example Output

```
● Bus ETA — Route 42C

Route: TSING YI (CHEUNG HANG ESTATE) → LAM TIN STATION
Stop: CHEUNG HANG BUS TERMINUS (Stop #1)
Distance: ~120m (nearest stop)

| # | ETA   | Remaining | Remark        |
|---|-------|-----------|---------------|
| 1 | 16:54 | 3 min     | Scheduled Bus |
| 2 | 17:00 | 9 min     |               |
| 3 | 17:07 | 16 min    |               |

Updated: 2026-03-23 16:49 HKT
Source: KMB/LWB
```

---

## Privacy

This plugin does not collect, store, or transmit any user data. All requests are made directly to the [Hong Kong Observatory Open Data API](https://data.weather.gov.hk) and the [KMB Open Data API](https://data.etabus.gov.hk) using HTTP GET requests only. No API keys or authentication required. The auto-location feature uses macOS CoreLocation — location data is processed locally and never sent to any server.

## License

MIT
