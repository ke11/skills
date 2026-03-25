# gws CLI — Calendar Reference

## List Events

```bash
gws calendar events list --params '{
  "calendarId": "<CALENDAR_ID>",
  "timeMin": "2026-04-01T00:00:00+08:00",
  "timeMax": "2026-04-30T23:59:59+08:00",
  "singleEvents": true,
  "orderBy": "startTime"
}' --format table
```

## Free/Busy Query

```bash
gws calendar freebusy query --json '{
  "timeMin": "2026-04-01T00:00:00+08:00",
  "timeMax": "2026-04-30T23:59:59+08:00",
  "timeZone": "Asia/Hong_Kong",
  "items": [{"id": "<CALENDAR_ID>"}]
}'
```

Returns `calendars.CALENDAR_ID.busy[]` array with `{start, end}` pairs.

## Create Event

```bash
gws calendar +insert --params '{"calendarId": "<CALENDAR_ID>"}' --json '{
  "summary": "Hiking at Dragon's Back",
  "start": {"date": "2026-04-05"},
  "end": {"date": "2026-04-06"},
  "description": "Planned via hk-planner skill"
}'
```

For all-day events use `date` (YYYY-MM-DD). For timed events use `dateTime` (ISO 8601).

## List Calendars

```bash
gws calendar calendarList list --format json
```

Returns `items[]` with `id` and `summary` (display name). Match `summary` to find the target calendar ID.

## Notes

- All times must include timezone offset (`+08:00` for HKT)
- `singleEvents: true` expands recurring events
- `--format table` for human-readable output, `--format json` for parsing
