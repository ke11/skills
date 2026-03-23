# Hong Kong AI Agent Skills

[繁體中文](README.md) | English

> **Beta** — This project is in casual active development. Skills, APIs, and configuration formats may change without notice. We welcome feedback and contributions.

AI agent skills designed for Hong Kong.

---

## Installation

```bash
// Install weather skill (#weather--hong-kong-weather)
npx skills add ke11/skills --skill hk-weather

// Install bus ETA skill (#kmb-eta--kmblwb-bus-eta)
npx skills add ke11/skills --skill kmb-eta
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

### kmb-eta — KMB Bus ETA

Fetches real-time bus arrival times from the [KMB Open Data API](https://data.etabus.gov.hk). No API key required.

#### Usage

```
/kmb-eta <route> <stop name> [terminal name] [en|tc]
```

| Command | Description |
|---------|-------------|
| `/kmb-eta 42C 業成街 藍田` | Query ETA at Yip Shing Street, heading to Lam Tin |
| `/kmb-eta 42C 業成街` | Search both directions for Yip Shing Street |
| `/kmb-eta 42C stops` | List all stops on route 42C (find stop names) |
| `/kmb-eta 960 建生 en` | Query 960 at Kin Sang (English output) |

- **Terminal name**: Specify direction using terminal name (e.g. "藍田" = heading to Lam Tin). Omit to search both directions.
- **Languages**: `tc` Traditional Chinese (default), `en` English
- **Offline data**: Route and stop data ships with the skill; only ETA requires a live API call. Update data: `npx skills update`

#### Example Output

```
## Bus ETA — Route 42C

Route: TSING YI (CHEUNG HANG ESTATE) → LAM TIN STATION
Stop: YIP SHING STREET KWAI CHUNG (Stop #15)

| # | ETA   | Remaining | Remark        |
|---|-------|-----------|---------------|
| 1 | 16:54 | 3 min     | Scheduled Bus |
| 2 | 17:00 | 9 min     |               |
| 3 | 17:07 | 16 min    |               |

Updated: 2026-03-23 16:49 HKT
Source: DATA.GOV.HK / KMB
```

---

## Privacy

This plugin does not collect, store, or transmit any user data. Real-time ETA is fetched from the [KMB Open Data API](https://data.etabus.gov.hk), weather data from the [Hong Kong Observatory Open Data API](https://data.weather.gov.hk), using HTTP GET requests only. No API keys or authentication required.

Bus route and stop data sourced from [DATA.GOV.HK](https://data.gov.hk), provided by The Kowloon Motor Bus Co. (1933) Ltd., used under the [DATA.GOV.HK Terms and Conditions](https://data.gov.hk/en/terms-and-conditions).

## License

MIT
