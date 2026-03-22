# opentail/skills — AI Agent Skills

[繁體中文](README.md) | English

A collection of skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and other AI agents.

## Installation

```bash
npx skills add opentail/skills --skill weather
```

## Available Skills

### weather — Hong Kong Weather

Fetches real-time weather data from the [Hong Kong Observatory Open Data API](https://data.weather.gov.hk/weatherAPI/doc/HKO_Open_Data_API_Documentation.pdf). No API key required.

| Command | Data | APIs | Speed |
|---------|------|------|-------|
| `/hk-weather` | Weather summary | 1 | Fast |
| `/hk-weather will it rain?` | Rain status + probability + forecast | 3 | Medium |
| `/hk-weather stations` | Station temps, humidity, rainfall | 1 | Fast |
| `/hk-weather forecast` | 9-day forecast | 1 | Fast |
| `/hk-weather rainfall` | Hourly rainfall | 1 | Fast |
| `/hk-weather warning` | Active warnings | 2 | Medium |
| `/hk-weather detail` | All stations + forecast | 2 | Medium |
| `/hk-weather all` | Everything | 6 | Slow |

Append a language code to switch language: `en` (English), `tc` (Traditional Chinese, default), `sc` (Simplified Chinese)

#### Natural Language Questions

The skill supports natural language questions in both English and Traditional/Simplified Chinese — no need to memorize keywords:

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
| `/hk-weather 今日會唔會落雨？` | Rain query |
| `/hk-weather 掛幾號風球？` | Typhoon / warnings |
| `/hk-weather 幾度？` | Station temperatures |

#### Example Output

```
## Hong Kong Weather Overview

**Updated**: 2026-03-22 02:45 HKT

**Overview**: A fresh to strong easterly airstream is affecting the coast of Guangdong. A band of clouds is covering the area.

**Forecast** (Weather forecast for Hong Kong): Mainly cloudy. Minimum temperature around 21 degrees. Sunny periods during the day with a maximum of around 25 degrees. Fresh to strong easterly winds, with strong winds over high ground at first.

**Outlook**: Sunny periods in the following few days. Hot during the day from mid to late week.

_Source: Hong Kong Observatory_
```

## License

MIT
