# Hong Kong AI Agent Skills

[繁體中文](README.md) | English

> **Beta** — A casual project. Skills, APIs, and configuration formats may change without notice. Feedback and contributions welcome.

AI agent skills designed for Hong Kong. All data from public APIs, no keys required.

## Quick Install

```bash
npx skills add ke11/skills --skill hk-weather
npx skills add ke11/skills --skill hk-kmb-eta
npx skills add ke11/skills --skill hk-aed-wait
npx skills add ke11/skills --skill hk-tcsp-licence
```

---

## Skills Overview

| Skill | Function | Data Source |
|-------|----------|-------------|
| [hk-weather](#hk-weather) | Real-time weather, forecasts, warnings, rainfall | [HK Observatory](https://data.weather.gov.hk) |
| [hk-kmb-eta](#hk-kmb-eta) | Bus arrival times, route lookup | [KMB Open Data](https://data.etabus.gov.hk) |
| [hk-aed-wait](#hk-aed-wait) | A&E waiting times | [Hospital Authority](https://www.ha.org.hk/opendata) |
| [hk-tcsp-licence](#hk-tcsp-licence) | TCSP licensee lookup | [Companies Registry / CSDI](https://portal.csdi.gov.hk) |

---

## hk-weather

Hong Kong Weather

Fetches real-time weather data from the Hong Kong Observatory Open Data API.

### Keyword Commands

| Command | Data | Speed |
|---------|------|-------|
| `/hk-weather` | Weather summary | Fast |
| `/hk-weather stations` | Station temps, humidity, rainfall | Fast |
| `/hk-weather forecast` | 9-day forecast | Fast |
| `/hk-weather rainfall` | Hourly rainfall | Fast |
| `/hk-weather warning` | Active warnings | Medium |
| `/hk-weather detail` | All stations + forecast | Medium |
| `/hk-weather all` | Everything | Slow |

### Natural Language

No need to memorize keywords — just ask in English or Chinese:

| Example | Function |
|---------|----------|
| `/hk-weather will it rain today?` | Rain query |
| `/hk-weather is there a typhoon?` | Typhoon / warnings |
| `/hk-weather how hot is it?` | Station temperatures |
| `/hk-weather UV index?` | UV index |
| `/hk-weather weather next week?` | 9-day forecast |

### Language

Append a language code: `en` English, `tc` Traditional Chinese (default), `sc` Simplified Chinese.

### Example Output

```
## Hong Kong Weather Summary

Updated: 2026-03-22 20:45 HKT

Overview: The easterly airstream affecting the coast of Guangdong is gradually moderating.

Forecast (Weather forecast for Hong Kong): Mainly cloudy. Sunny periods during the day with a maximum of around 27 degrees.

Outlook: Sunny periods in the following few days. Hot during the day from mid to late week.

Source: Hong Kong Observatory
```

---

## hk-kmb-eta

KMB Bus ETA

Fetches real-time bus arrival times from the KMB Open Data API.

### Usage

```
/hk-kmb-eta <route> <stop name> [terminal] [en|tc]
```

| Command | Description |
|---------|-------------|
| `/hk-kmb-eta 42C 業成街 藍田` | ETA at 業成街, heading to 藍田 |
| `/hk-kmb-eta 42C 業成街` | Search both directions |
| `/hk-kmb-eta 42C stops` | List all stops on route 42C |
| `/hk-kmb-eta 960 建生 en` | English output |

- **Terminal** — Specify direction using terminal name (e.g. "藍田" = heading to Lam Tin). Omit to search both directions.
- **Language** — `tc` Traditional Chinese (default), `en` English
- **Offline data** — Route and stop data ships with the skill; only ETA requires a live API call

### Example Output

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

## hk-aed-wait

A&E Waiting Time

Fetches real-time Accident & Emergency waiting times from the Hospital Authority Open Data API. Covers all 18 public hospitals, updated every ~15 minutes.

### Usage

```
/hk-aed-wait                     All hospitals (grouped by region)
/hk-aed-wait <hospital name>     Search specific hospital
/hk-aed-wait <hospital> en       English output
```

| Command | Description |
|---------|-------------|
| `/hk-aed-wait` | All hospitals waiting times |
| `/hk-aed-wait 屯門` | Tuen Mun Hospital waiting time |
| `/hk-aed-wait Queen en` | Search "Queen" hospitals in English |

- **Language** — `tc` Traditional Chinese (default), `en` English, `sc` Simplified Chinese

### Example Output

```
## A&E Waiting Time

As of 24/3/2026 6:15PM, estimated A&E waiting time upon arrival.
Half of waiting patients can be seen within the time shown; majority within the time in brackets.

| Hospital | Triage I | Triage II | Triage III | Triage IV & V |
|----------|:--------:|:---------:|:----------:|:-------------:|
| Hong Kong Island | | | | |
| Queen Mary Hospital | 0 minute | less than 15 minutes | 35 minutes (79 minutes) | 3 hours (4 hours) |
| ...

Triage I-V: Critical, Emergency, Urgent, Semi-urgent, Non-urgent.
🔴 = A&E is currently managing Triage I/II cases.

Source: Hospital Authority / CSDI
```

---

## hk-tcsp-licence

TCSP Licensee Lookup

Search Hong Kong Trust or Company Service Provider (TCSP) licensees via the CSDI Portal. Data sourced from the Companies Registry.

### Usage

```
/hk-tcsp-licence <field> <keyword> [en|tc]
```

| Command | Description |
|---------|-------------|
| `/hk-tcsp-licence name FULLYEAR` | Search by English name |
| `/hk-tcsp-licence name 富年` | Search by Chinese name |
| `/hk-tcsp-licence licence TC000002` | Search by licence number |
| `/hk-tcsp-licence address wan chai en` | Search by address (English output) |

- **Field** — `name` (English or Chinese name), `licence` (licence number), `address` (business address)
- **Language** — `tc` Traditional Chinese (default), `en` English
- Results capped at 20; remarks column shown automatically when applicable

### Example Output

```
## TCSP Licensee Search Results

Found 1 record(s) matching "FULLYEAR" in name.

| Licence No | English Name | Chinese Name | Business Address |
|------------|-------------|-------------|------------------|
| TC000002 | FULLYEAR CONSULTANTS LIMITED | 富年顧問有限公司 | UNIT B, 12/F, KA NIN WAH COMMERCIAL BUILDING, 423-425 HENNESSY ROAD, WAN CHAI, HONG KONG |

Source: Companies Registry / CSDI
```

---

## Privacy

This plugin does not collect, store, or transmit any user data. All data is fetched from public APIs using HTTP GET requests only. No API keys or authentication required.

- Weather data: [HK Observatory Open Data API](https://data.weather.gov.hk)
- Bus route and stop data sourced from [DATA.GOV.HK](https://data.gov.hk), used under the [DATA.GOV.HK Terms and Conditions](https://data.gov.hk/en/terms-and-conditions)
- A&E waiting times: [Hospital Authority](https://www.ha.org.hk) / [CSDI Portal](https://portal.csdi.gov.hk)
- TCSP licensee data: [Companies Registry](https://www.cr.gov.hk) / [CSDI Portal](https://portal.csdi.gov.hk)

## License

MIT
