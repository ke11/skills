# 1823 Public Holidays Calendar API

Data source: [DATA.GOV.HK](https://data.gov.hk/en-data/dataset/hk-dpo-statistic-cal)
Documentation: [Data Dictionary (PDF)](https://www.1823.gov.hk/f/upload/1229/1823_cal_dictionary.pdf)

## Endpoints

| Endpoint | Language |
|----------|----------|
| `GET /common/ical/en.json` | English |
| `GET /common/ical/tc.json` | 繁體中文 |
| `GET /common/ical/sc.json` | 简体中文 |

Base URL: `https://www.1823.gov.hk`

No API key required. Read-only GET requests only.

## Response Structure

```json
{
  "vcalendar": [
    {
      "prodid": "-//1823 Contact Centre, HKSAR Government//Hong Kong Public Holidays//EN",
      "version": "2.0",
      "calscale": "GREGORIAN",
      "x-wr-timezone": "Asia/Hong_Kong",
      "x-wr-calname": "Hong Kong Public Holidays",
      "x-wr-caldesc": "Hong Kong Public Holidays",
      "vevent": [
        {
          "dtstart": ["20260101", { "value": "DATE" }],
          "dtend": ["20260102", { "value": "DATE" }],
          "dtstamp": "20250506T032740Z",
          "transp": "TRANSPARENT",
          "uid": "20260101@1823.gov.hk",
          "summary": "The first day of January"
        }
      ]
    }
  ]
}
```

## Field Reference

| Field | Description | Type |
|-------|-------------|------|
| `vcalendar` | iCalendar root | array |
| `prodid` | Product identifier | text |
| `version` | iCalendar version | text |
| `calscale` | Calendar scale (GREGORIAN) | text |
| `x-wr-timezone` | Timezone (Asia/Hong_Kong) | text |
| `x-wr-calname` | Calendar display name | text |
| `x-wr-caldesc` | Calendar description | text |
| `vevent` | Array of holiday events | array |
| `vevent[].dtstart` | Event start date `[YYYYMMDD, {value: "DATE"}]` | array |
| `vevent[].dtend` | Event end date `[YYYYMMDD, {value: "DATE"}]` | array |
| `vevent[].dtstamp` | Last revised timestamp | text |
| `vevent[].transp` | Transparency (always TRANSPARENT) | text |
| `vevent[].uid` | Unique identifier (`YYYYMMDD@1823.gov.hk`) | text |
| `vevent[].summary` | Holiday name (localized) | text |

## Notes

- Dataset is iCal data converted to JSON format
- Covers multiple years (currently 2024–2026)
- Each event spans exactly one day (`dtend` = `dtstart` + 1 day)
- Holiday names are localized per endpoint (EN/TC/SC)
- `uid` is based on the start date, unique per holiday
