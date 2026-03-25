# Hong Kong AI Agent Skills

[繁體中文](README.md) | English

> **Beta** — A casual project. Skills, APIs, and configuration formats may change without notice. Feedback and contributions welcome.

AI agent skills designed for Hong Kong. All data from public APIs, no keys required.

## Quick Install

```bash
# Install all
npx skills add ke11/skills

# Or install individual skills
npx skills add ke11/skills --skill hk-weather
npx skills add ke11/skills --skill hk-kmb-eta
npx skills add ke11/skills --skill hk-aed-wait
npx skills add ke11/skills --skill hk-tcsp-licence
npx skills add ke11/skills --skill hk-holiday
npx skills add ke11/skills --skill hk-planner
```

---

## Skills Overview

| Skill | Function | Quick Example | Data Source |
|-------|----------|---------------|-------------|
| [hk-weather](skills/hk-weather/references/usage.md) | Real-time weather, forecasts, warnings, rainfall | `/hk-weather forecast` | [HK Observatory](https://data.weather.gov.hk) |
| [hk-kmb-eta](skills/hk-kmb-eta/references/usage.md) | Bus arrival times, route lookup | `/hk-kmb-eta 42C 業成街` | [KMB Open Data](https://data.etabus.gov.hk) |
| [hk-aed-wait](skills/hk-aed-wait/references/usage.md) | A&E waiting times | `/hk-aed-wait 屯門` | [Hospital Authority](https://www.ha.org.hk/opendata) |
| [hk-tcsp-licence](skills/hk-tcsp-licence/references/usage.md) | TCSP licensee lookup | `/hk-tcsp-licence name 富年` | [Companies Registry / CSDI](https://portal.csdi.gov.hk) |
| [hk-holiday](skills/hk-holiday/references/usage.md) | Public holidays lookup | `/hk-holiday 2026` | [1823 Government Hotline](https://www.1823.gov.hk) |
| [hk-planner](skills/hk-planner/references/flowchart.md) | Activity planner (calendar + holidays + weather) | `/hk-planner hiking next week` | Google Calendar + above skills |

Click a skill name for full usage docs and output examples.

---

## Privacy

This plugin does not collect, store, or transmit any user data. All data is fetched from public APIs using HTTP GET requests only. No API keys or authentication required.

- Weather data: [HK Observatory Open Data API](https://data.weather.gov.hk)
- Bus route and stop data sourced from [DATA.GOV.HK](https://data.gov.hk), used under the [DATA.GOV.HK Terms and Conditions](https://data.gov.hk/en/terms-and-conditions)
- A&E waiting times: [Hospital Authority](https://www.ha.org.hk) / [CSDI Portal](https://portal.csdi.gov.hk)
- TCSP licensee data: [Companies Registry](https://www.cr.gov.hk) / [CSDI Portal](https://portal.csdi.gov.hk)
- Public holidays: [1823 Government Hotline](https://www.1823.gov.hk) / [DATA.GOV.HK](https://data.gov.hk)

## License

MIT
