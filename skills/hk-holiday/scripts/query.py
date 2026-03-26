#!/usr/bin/env python3
"""Hong Kong public holidays query — fetches data from the 1823 government calendar."""

import sys
import json
from datetime import datetime, date, timedelta
from urllib.request import urlopen, Request

ENDPOINTS = {
    "en": "https://www.1823.gov.hk/common/ical/en.json",
    "tc": "https://www.1823.gov.hk/common/ical/tc.json",
    "sc": "https://www.1823.gov.hk/common/ical/sc.json",
}

LANG_TOKENS = {"en", "tc", "sc"}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args(argv):
    lang = "tc"
    year = None
    show_next = False
    for tok in argv:
        low = tok.lower()
        if low in LANG_TOKENS:
            lang = low
        elif low == "next":
            show_next = True
        elif low.isdigit() and len(low) == 4:
            year = int(low)

    return lang, year, show_next


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def fetch_json(url):
    try:
        req = Request(url, headers={"User-Agent": "hk-holiday-skill/1.0"})
        with urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def parse_events(data):
    """Extract holiday events from the iCal JSON structure."""
    events = []
    try:
        vevents = data["vcalendar"][0]["vevent"]
    except (KeyError, IndexError, TypeError):
        return events

    for ev in vevents:
        try:
            raw_date = ev["dtstart"][0]
            dt = datetime.strptime(raw_date, "%Y%m%d").date()
            summary = ev.get("summary", "")
            events.append({"date": dt, "summary": summary})
        except (KeyError, IndexError, ValueError, TypeError):
            continue

    events.sort(key=lambda e: e["date"])
    return events


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

WEEKDAY_EN = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
WEEKDAY_TC = ["一", "二", "三", "四", "五", "六", "日"]


def weekday_str(dt, lang):
    idx = dt.weekday()
    if lang == "en":
        return WEEKDAY_EN[idx]
    return WEEKDAY_TC[idx]


def _l(lang, en, tc, sc=None):
    if lang == "en":
        return en
    if lang == "sc" and sc is not None:
        return sc
    return tc


def days_until_str(delta_days, lang):
    if delta_days == 0:
        return _l(lang, "Today", "今日")
    if delta_days == 1:
        return _l(lang, "Tomorrow", "明日")
    if lang == "en":
        return f"in {delta_days} days"
    return _l(lang, "", f"{delta_days} 日後", f"{delta_days} 日后")


# ---------------------------------------------------------------------------
# Consecutive days off (holidays + weekends)
# ---------------------------------------------------------------------------

def build_streak_map(events):
    """Build a map: holiday_date -> (streak_length, is_first_holiday_in_streak).

    Streaks include weekends bridging holidays but only holiday dates are keyed.
    A streak must be >= 3 total days off to be shown.
    """
    holiday_set = {e["date"]: e["summary"] for e in events}
    streaks = []
    visited = set()

    for ev in events:
        if ev["date"] in visited:
            continue
        streak = []
        d = ev["date"]
        # Expand backwards to catch preceding weekends
        while True:
            prev = d - timedelta(days=1)
            if prev in holiday_set or prev.weekday() >= 5:
                d = prev
            else:
                break
        # Walk forward
        while d in holiday_set or d.weekday() >= 5:
            streak.append((d, holiday_set.get(d)))
            if d in holiday_set:
                visited.add(d)
            d += timedelta(days=1)
        if len(streak) >= 3:
            streaks.append(streak)

    # Map each holiday date to (streak_length, is_first_holiday, start_date, end_date)
    streak_map = {}
    for streak in streaks:
        length = len(streak)
        start = streak[0][0]
        end = streak[-1][0]
        first_holiday = True
        for d, label in streak:
            if label is not None:  # only holiday dates
                streak_map[d] = (length, first_holiday, start, end)
                first_holiday = False

    return streak_map


def streak_col(dt, streak_map, lang):
    """Return the streak column value for a holiday date."""
    if dt not in streak_map:
        return ""
    length, is_first, start, end = streak_map[dt]
    if is_first:
        s = start.strftime("%-m/%-d")
        e = end.strftime("%-m/%-d")
        return _l(lang, f"{length}d ({s} → {e})", f"{length}日 ({s} → {e})", f"{length}日 ({s} → {e})")
    return ""


# ---------------------------------------------------------------------------
# Output formatting
# ---------------------------------------------------------------------------

def format_next(events, lang, today):
    """Show only the next upcoming holiday."""
    upcoming = [e for e in events if e["date"] >= today]
    if not upcoming:
        return _l(lang,
                   "No upcoming holidays found.",
                   "找不到即將來臨的公眾假期。",
                   "找不到即将来临的公众假期。")

    ev = upcoming[0]
    delta = (ev["date"] - today).days
    countdown = days_until_str(delta, lang)

    lines = [_l(lang, "## Next Public Holiday", "## 下一個公眾假期", "## 下一个公众假期")]
    lines.append("")
    lines.append(f"**{ev['summary']}**")
    lines.append(f"{ev['date'].strftime('%Y-%m-%d')} ({weekday_str(ev['date'], lang)}) — {countdown}")

    # Reuse build_streak_map for consecutive days off detection
    streak_map = build_streak_map(upcoming)
    if ev["date"] in streak_map:
        length, _, start, end = streak_map[ev["date"]]
        lines.append("")
        lines.append(_l(lang,
                         f"Consecutive days off ({length} days incl. weekends):",
                         f"連續假期（{length} 日，含週末）：",
                         f"连续假期（{length} 日，含周末）："))
        lines.append(f"{start.strftime('%m-%d')} ({weekday_str(start, lang)}) → {end.strftime('%m-%d')} ({weekday_str(end, lang)})")

    return "\n".join(lines)


def format_year(events, year, lang):
    """Show all holidays in a specific year. Only holiday rows, streak column counts weekends."""
    today = date.today()
    filtered = [e for e in events if e["date"].year == year]
    if not filtered:
        return _l(lang,
                   f"No holidays found for {year}.",
                   f"找不到 {year} 年的公眾假期資料。",
                   f"找不到 {year} 年的公众假期资料。")

    streak_map = build_streak_map(filtered)

    lines = [_l(lang,
                 f"## {year} Hong Kong Public Holidays",
                 f"## {year} 年香港公眾假期",
                 f"## {year} 年香港公众假期")]
    lines.append("")

    if lang == "en":
        lines.append("| # | Date | Holiday | Longest Break | Countdown |")
        lines.append("|--:|------|---------|-------|-----------|")
    elif lang == "sc":
        lines.append("| # | 日期 | 假期名称 | 最长连续假期 | 倒数 |")
        lines.append("|--:|------|----------|------|------|")
    else:
        lines.append("| # | 日期 | 假期名稱 | 最長連續假期 | 倒數 |")
        lines.append("|--:|------|----------|------|------|")

    for i, ev in enumerate(filtered, 1):
        wd = weekday_str(ev["date"], lang)
        delta = (ev["date"] - today).days
        sc = streak_col(ev["date"], streak_map, lang)
        date_col = f"{ev['date'].strftime('%Y-%m-%d')} ({wd})"
        if delta < 0:
            countdown = _l(lang, "Passed", "已過", "已过")
            dot = "⚫"
        else:
            countdown = days_until_str(delta, lang)
            dot = "🔴"
        streak_display = f"⭐ {sc}" if sc else ""
        lines.append(f"| {i} | {date_col} | {dot} {ev['summary']} | {streak_display} | {countdown} |")

    lines.append("")
    lines.append(_l(lang,
                     f"Total: {len(filtered)} public holidays",
                     f"合共 {len(filtered)} 日公眾假期",
                     f"合共 {len(filtered)} 日公众假期"))
    lines.append("")
    lines.append(_l(lang,
                     "_🔴 Holiday · ⚫ Passed · ⭐ Longest consecutive days off (incl. weekends)_",
                     "_🔴 假期 · ⚫ 已過 · ⭐ 最長連續假期（含週末）_",
                     "_🔴 假期 · ⚫ 已过 · ⭐ 最长连续假期（含周末）_"))

    return "\n".join(lines)


def format_upcoming(events, lang, today):
    """Show upcoming holidays. Only holiday rows, streak column counts weekends."""
    upcoming = [e for e in events if e["date"] >= today]

    if not upcoming:
        return _l(lang,
                   "No upcoming holidays found.",
                   "找不到即將來臨的公眾假期。",
                   "找不到即将来临的公众假期。")

    streak_map = build_streak_map(upcoming)

    lines = [_l(lang, "## Upcoming Hong Kong Public Holidays",
                "## 即將來臨的香港公眾假期",
                "## 即将来临的香港公众假期")]
    lines.append("")

    if lang == "en":
        lines.append("| Date | Holiday | Longest Break | Countdown |")
        lines.append("|------|---------|-------|-----------|")
    elif lang == "sc":
        lines.append("| 日期 | 假期名称 | 最长连续假期 | 倒数 |")
        lines.append("|------|----------|------|------|")
    else:
        lines.append("| 日期 | 假期名稱 | 最長連續假期 | 倒數 |")
        lines.append("|------|----------|------|------|")

    for ev in upcoming:
        delta = (ev["date"] - today).days
        wd = weekday_str(ev["date"], lang)
        countdown = days_until_str(delta, lang)
        sc = streak_col(ev["date"], streak_map, lang)
        date_col = f"{ev['date'].strftime('%Y-%m-%d')} ({wd})"
        streak_display = f"⭐ {sc}" if sc else ""
        lines.append(f"| {date_col} | 🔴 {ev['summary']} | {streak_display} | {countdown} |")

    lines.append("")
    lines.append(_l(lang,
                     "_🔴 Holiday · ⭐ Longest consecutive days off (incl. weekends)_",
                     "_🔴 假期 · ⭐ 最長連續假期（含週末）_",
                     "_🔴 假期 · ⭐ 最长连续假期（含周末）_"))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    raw = " ".join(sys.argv[1:])
    args = raw.split() if raw.strip() else []
    lang, year, show_next = parse_args(args)

    data = fetch_json(ENDPOINTS[lang])
    if data is None:
        print(_l(lang,
                  "Failed to reach 1823 calendar API. Please try again later.",
                  "無法連接 1823 日曆 API，請稍後再試。",
                  "无法连接 1823 日历 API，请稍后再试。"))
        sys.exit(1)

    events = parse_events(data)
    if not events:
        print(_l(lang,
                  "No holiday data found.",
                  "找不到假期資料。",
                  "找不到假期资料。"))
        sys.exit(1)

    today = date.today()

    if show_next:
        output = format_next(events, lang, today)
    elif year:
        output = format_year(events, year, lang)
    else:
        output = format_upcoming(events, lang, today)

    attr = _l(lang,
              "_Source: 1823, HKSAR Government_",
              "_資料來源：1823，香港特別行政區政府_",
              "_资料来源：1823，香港特别行政区政府_")
    print(f"---BEGIN---\n{output}\n\n{attr}\n---END---")


if __name__ == "__main__":
    main()
