#!/usr/bin/env python3
"""Hospital A&E waiting time query — fetches real-time data from Hospital Authority."""

import sys
import json
import re
from urllib.request import urlopen, Request
from urllib.error import URLError

ENDPOINTS = {
    "en": "https://www.ha.org.hk/opendata/aed/aedwtdata2-en.json",
    "tc": "https://www.ha.org.hk/opendata/aed/aedwtdata2-tc.json",
    "sc": "https://www.ha.org.hk/opendata/aed/aedwtdata2-sc.json",
}

LANG_TOKENS = {"en", "tc", "sc"}

# Hospital-to-region mapping (matches HA website grouping)
REGIONS = {
    "tc": [
        ("港島區", [
            "東區尤德夫人那打素醫院", "瑪麗醫院", "律敦治醫院",
        ]),
        ("九龍區", [
            "明愛醫院", "廣華醫院", "伊利沙伯醫院", "基督教聯合醫院",
        ]),
        ("新界區", [
            "雅麗氏何妙齡那打素醫院", "北區醫院", "北大嶼山醫院",
            "博愛醫院", "威爾斯親王醫院", "瑪嘉烈醫院", "長洲醫院",
            "天水圍醫院", "將軍澳醫院", "屯門醫院", "仁濟醫院",
        ]),
    ],
    "en": [
        ("Hong Kong Island", [
            "Pamela Youde Nethersole Eastern Hospital", "Queen Mary Hospital",
            "Ruttonjee Hospital",
        ]),
        ("Kowloon", [
            "Caritas Medical Centre", "Kwong Wah Hospital",
            "Queen Elizabeth Hospital", "United Christian Hospital",
        ]),
        ("New Territories", [
            "Alice Ho Miu Ling Nethersole Hospital", "North District Hospital",
            "North Lantau Hospital", "Pok Oi Hospital",
            "Prince of Wales Hospital", "Princess Margaret Hospital",
            "St John Hospital", "Tin Shui Wai Hospital",
            "Tseung Kwan O Hospital", "Tuen Mun Hospital", "Yan Chai Hospital",
        ]),
    ],
}


# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------

def parse_args(argv):
    lang = "tc"
    remaining = []

    for tok in argv:
        low = tok.lower()
        if low in LANG_TOKENS:
            lang = low
        else:
            remaining.append(tok)

    query = " ".join(remaining).strip()
    return query, lang


# ---------------------------------------------------------------------------
# Data fetching
# ---------------------------------------------------------------------------

def sanitize(obj):
    """Recursively strip HTML tags from all strings in API data."""
    if isinstance(obj, str):
        return re.sub(r'<[^>]+>', '', obj)
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v) for v in obj]
    return obj


def fetch_json(url):
    try:
        req = Request(url, headers={"User-Agent": "hk-aed-wait-skill/1.0"})
        with urlopen(req, timeout=10) as resp:
            return sanitize(json.loads(resp.read()))
    except Exception:
        return None


def _l(lang, en, zh):
    return en if lang == "en" else zh


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------

def _pct_cell(h, p50_key, p95_key):
    """Format a percentile cell: 'p50 (p95)' or just 'p50' if p95 is empty."""
    p50 = h.get(p50_key, "—")
    p95 = h.get(p95_key, "")
    return f"{p50} ({p95})" if p95 else p50


def _triage_cell(wt, manage, lang=None):
    """Format a triage I/II cell with managing-case indicator."""
    if manage in ("Y", "是"):
        return f"{wt} 🔴"
    return wt


def _table_header(lang):
    """Return the markdown table header lines for A&E wait time tables."""
    if lang == "en":
        return [
            f"\n| Hospital | Triage I | Triage II | Triage III | Triage IV & V |",
            "|----------|:--------:|:---------:|:----------:|:-------------:|",
        ]
    return [
        f"\n| 醫院 | 分流類別 I | 分流類別 II | 分流類別 III | 分流類別 IV & V |",
        "|------|:---------:|:----------:|:-----------:|:--------------:|",
    ]


def _legend(lang):
    """Return the markdown legend lines."""
    lines = [""]
    if lang == "en":
        lines.append("_Triage I-V: Critical, Emergency, Urgent, Semi-urgent, Non-urgent._")
        lines.append("_🔴 = A&E is currently managing Triage I/II cases._")
    else:
        lines.append("_分流類別 I-V 指危殆、危急、緊急、次緊急及非緊急類別。_")
        lines.append("_🔴 指急症室正在治理分流類別 I/II 的病人。_")
    return lines


def _update_header(update_time, lang):
    """Return the update-time description lines."""
    if not update_time:
        return []
    if lang == "en":
        return [
            f"\nAs of {update_time}, estimated A&E waiting time upon arrival.",
            "Half of waiting patients can be seen within the time shown; majority within the time in brackets.",
        ]
    return [
        f"\n於{update_time}，病人到達急症室求診預計等候時間。",
        "一半輪候病人能在以下時間內就診，大部份人可於括號內顯示的時間就診。",
    ]


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def format_row(h, lang):
    """Format a single hospital as a table row."""
    name = h.get("hospName", "")
    t1_cell = _triage_cell(h.get("t1wt", "—"), h.get("manageT1case", ""))
    t2_cell = _triage_cell(h.get("t2wt", "—"), h.get("manageT2case", ""))
    t3_cell = _pct_cell(h, "t3p50", "t3p95")
    t45_cell = _pct_cell(h, "t45p50", "t45p95")
    na_vals = {"N/A", "不適用"}
    if h.get("manageT1case", "") in na_vals:
        t1 = h.get("t1wt", "—")
        t2 = h.get("t2wt", "—")
        return f"| {name} | ⚠️ **{t1}** | ⚠️ **{t2}** | {t3_cell} | {t45_cell} |"
    return f"| {name} | {t1_cell} | {t2_cell} | {t3_cell} | {t45_cell} |"


def format_all(data, lang):
    hospitals = data.get("waitTime", [])
    update_time = data.get("updateTime", "")

    if not hospitals:
        return _l(lang, "No data available.", "暫無數據。")

    # Build lookup by hospital name
    by_name = {h.get("hospName", ""): h for h in hospitals}

    lines = [_l(lang, "## A&E Waiting Time", "## 急症室等候時間")]
    lines.extend(_update_header(update_time, lang))
    lines.extend(_table_header(lang))

    regions = REGIONS.get(lang, REGIONS.get("tc"))
    used = set()

    for region_name, region_hospitals in regions:
        # Region header row
        lines.append(f"| **{region_name}** | | | | |")

        for hosp_name in region_hospitals:
            h = by_name.get(hosp_name)
            if not h:
                continue
            used.add(hosp_name)
            lines.append(format_row(h, lang))

    # Any hospitals not in region mapping (fallback)
    remaining = [h for h in hospitals if h.get("hospName", "") not in used]
    if remaining:
        lines.append(f"| **{_l(lang, 'Other', '其他')}** | | | | |")
        for h in remaining:
            lines.append(format_row(h, lang))

    lines.extend(_legend(lang))

    return "\n".join(lines)


def format_search(data, query, lang):
    hospitals = data.get("waitTime", [])
    update_time = data.get("updateTime", "")

    query_lower = query.lower()
    matches = [h for h in hospitals if query_lower in h.get("hospName", "").lower()]

    if not matches:
        lines = [_l(lang,
                     f"## A&E Waiting Time\n\nNo hospital found matching \"{query}\".",
                     f"## 急症室等候時間\n\n找不到符合「{query}」的醫院。")]
        lines.append("")
        lines.append(_l(lang, "**Available hospitals:**", "**可查詢的醫院：**"))
        for h in hospitals:
            lines.append(f"- {h.get('hospName', '')}")
        return "\n".join(lines)

    lines = [_l(lang, "## A&E Waiting Time", "## 急症室等候時間")]
    lines.extend(_update_header(update_time, lang))
    lines.extend(_table_header(lang))

    for h in matches:
        lines.append(format_row(h, lang))

    lines.extend(_legend(lang))

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    raw = " ".join(sys.argv[1:])
    args = raw.split() if raw.strip() else []
    query, lang = parse_args(args)

    data = fetch_json(ENDPOINTS[lang])
    if data is None:
        print(_l(lang,
               "Failed to reach Hospital Authority API. Please try again later.",
               "無法連接醫院管理局 API，請稍後再試。"))
        sys.exit(1)

    if query:
        output = format_search(data, query, lang)
    else:
        output = format_all(data, lang)

    attr = _l(lang,
              "_Source: Hospital Authority / CSDI_",
              "_資料來源：醫院管理局 / 空間數據共享平台 CSDI_")
    print(f"---BEGIN---\n{output}\n\n{attr}\n---END---")


if __name__ == "__main__":
    main()
