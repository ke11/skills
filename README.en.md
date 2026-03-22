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

## Privacy

This plugin does not collect, store, or transmit any user data. All requests are made directly to the [Hong Kong Observatory Open Data API](https://data.weather.gov.hk) using HTTP GET requests only. No API keys or authentication required.

## License

MIT
