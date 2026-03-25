---
name: hk-planner
description: "Plan outings, day trips, and activities in Hong Kong by checking calendar availability, public holidays, and weather forecasts. Use this skill when the user wants to plan a trip, find good days for outdoor activities, schedule a hike or BBQ, plan around long weekends, 計劃行程, 搵日去行山, 邊日適合戶外活動, or asks things like 'when should I go hiking next month' or '下個月邊日好天可以去沙灘'."
allowed-tools: [Bash]
disable-model-invocation: true
model: haiku
effort: low
argument-hint: "[activity] [date range] [calendar:name] [en|tc|sc]"
---

# Hong Kong Activity Planner

An orchestrator skill that combines calendar availability, public holidays, and weather forecasts to help plan outings and activities in Hong Kong.

```
hk-planner/
├── SKILL.md              # Skill instructions (this file)
└── references/
    └── gws-calendar.md   # gws CLI calendar reference
```

## Dependencies

This skill requires the `gws` CLI and calls scripts from other skills. Check they exist before using:

```bash
# Check gws CLI
which gws > /dev/null 2>&1 || echo "MISSING: gws CLI — install with: npm install -g @googleworkspace/cli"

# Check sub-skills
for skill in hk-holiday hk-weather; do
  found=false
  for path in .claude/skills .agents/skills .agent/skills skills; do
    [ -f "$path/$skill/scripts/run.sh" ] && found=true && break
  done
  $found || echo "MISSING: $skill — install with: npx skills add ke11/skills --skill $skill"
done
```

If `gws` is missing, the calendar features won't work — tell the user to install it. If a sub-skill is missing, continue with the data sources that are available.

## How It Works

Gather data from three sources, combine into a recommendation, and present it directly.

1. **Google Calendar** (via `gws` CLI) — find free days
2. **hk-holiday** skill — identify public holidays and long weekends
3. **hk-weather** skill — check weather forecast for outdoor activities

## Step 1: Understand the Request

Parse what the user wants:
- **Activity type**: outdoor (hiking, beach, BBQ) or indoor (museum, shopping)
- **Date range**: specific dates, "next month", "this weekend", etc. Default to next 14 days if unspecified
- **Calendar**: if the user specifies `calendar:name`, use that calendar. Otherwise default to **primary** calendar.
- **Preferences**: group size, avoid heat, rain tolerance, etc.

## Step 2: Gather Data

Run these in parallel where possible:

### 2a. Resolve Calendar

Find the calendar ID by listing calendars and matching by name:

```bash
gws calendar calendarList list --format json
```

Search `items[].summary` for the calendar name (case-insensitive). Use the matching `items[].id` for subsequent queries.

If no calendar name is specified, use `primary` as the calendar ID (the user's default calendar).

If the specified calendar is not found, list available calendars and ask the user to pick one.

### 2b. Calendar Availability

Check the resolved calendar for busy/free times. See `references/gws-calendar.md` for the gws CLI commands.

Query events in the date range to find which days are already booked.

### 2c. Public Holidays

Run the hk-holiday skill to get upcoming holidays:
```bash
bash .agents/skills/hk-holiday/scripts/run.sh "$DATE_ARGS"
```

Holidays are good candidates — the user is off work. Long weekends (⭐ streaks) are especially valuable for day trips.

### 2d. Weather Forecast

For outdoor activities, run the hk-weather skill:
```bash
bash .agents/skills/hk-weather/scripts/run.sh "forecast"
```

The 9-day forecast helps assess upcoming weather. Beyond 9 days, weather data isn't available — note this limitation to the user.

## Step 3: Present the Plan

Combine all three data sources into a day-by-day recommendation with time-of-day granularity.

Split each day into three time slots and check calendar events against each:
- **上午** (Morning): before 12:00
- **下午** (Afternoon): 12:00–18:00
- **晚上** (Evening): after 18:00

For each slot:
- ✅ = free on calendar
- ❌ + reason = busy (show event name, e.g. ❌ BBQ, ❌ 登山)

**Output format:**
```
## 活動計劃 / Activity Plan

📅 日曆: {calendar_name} · 🎯 活動: {activity}

| 日期 | 星期 | 假期 | 天氣 | 上午 | 下午 | 晚上 | 推薦時段 |
|------|------|------|------|:----:|:----:|:----:|----------|
| 3/29 | 日 | — | ⛅ 22-27°C | ✅ | ✅ | ✅ | 🌙 6pm-9pm |
| 3/30 | 一 | — | ⛅ 23-29°C | ✅ | ❌ BBQ | ✅ | 🌅 早晨或 🌙 6pm+ |
| 4/03 | 五 | 🔴 耶穌受難節 | ⛅ 23-28°C | ❌ 游泳 | ✅ | ✅ | 🌙 6pm-9pm |
| 4/04 | 六 | 🔴 復活節 | ☀️ 晴朗 | ❌ 登山 | ❌ 登山 | ✅ | ⭐⭐ 6pm-9pm |
| 4/05 | 日 | — | 🌧️ 未知 | ✅ | ✅ | ✅ | 任意時段 |

### 備註
- ⭐⭐ 最佳（假期 + 好天 + 有空）· ⭐ 推薦 · 🌙 晚間可行
- 天氣預報僅涵蓋未來 9 天，超出範圍顯示「未知」
- 📅 日曆: {calendar_name}
```

**Scoring logic for 推薦時段:**
- ⭐⭐ = holiday/weekend + good weather + fully free → best day, show best time slot
- ⭐ = good weather + mostly free → recommended, show available slots
- 🌙/🌅 = partially busy → suggest available time slots
- Show "任意時段" if all slots are free and no strong weather signal

**Weather icons:**
- ☀️ sunny/clear → great for outdoor
- ⛅ cloudy/partly cloudy → OK for outdoor
- 🌧️ rain → flag for outdoor activities
- 🌡️ show temperature range from forecast

## Step 4: Offer to Create Event

After the user picks a date, offer to create a calendar event on the same calendar using `gws calendar +insert`. See `references/gws-calendar.md` for the command.

## Language

Follow the user's language. Default to `tc` (Traditional Chinese). Pass the appropriate language code when calling hk-holiday and hk-weather.
