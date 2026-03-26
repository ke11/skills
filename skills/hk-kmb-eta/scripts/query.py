#!/usr/bin/env python3
"""KMB bus ETA query. Reads static data from data.json, fetches only live ETA.

Usage: python3 query.py <route> [stop] [terminal] [en|tc] [stops]
"""
import json, urllib.request, urllib.error, sys, os, re
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, 'data.json')
BASE = "https://data.etabus.gov.hk/v1/transport/kmb"
HKT = timezone(timedelta(hours=8))

STRINGS = {
    'en': {
        'route': 'Route',
        'stops': 'All Stops',
        'stop_name': 'Stop Name',
        'no_eta': 'No ETA data available.',
        'unit': 'min',
        'title': 'Bus ETA',
        'route_label': 'Route',
        'stop_label': 'Stop',
        'eta_col': 'ETA',
        'remaining_col': 'Remaining',
        'remark_col': 'Remark',
        'updated': 'Updated',
        'source': 'Source: DATA.GOV.HK / KMB',
        'outbound': 'Outbound',
        'inbound': 'Inbound',
    },
    'tc': {
        'route': '路線',
        'stops': '車站列表',
        'stop_name': '車站名稱',
        'no_eta': '目前沒有到站時間資料。',
        'unit': '分鐘',
        'title': '巴士到站時間',
        'route_label': '路線',
        'stop_label': '車站',
        'eta_col': '預計到達',
        'remaining_col': '剩餘時間',
        'remark_col': '備註',
        'updated': '更新時間',
        'source': '資料來源：DATA.GOV.HK / 九巴',
        'outbound': '出站',
        'inbound': '入站',
    },
}


def sanitize(obj):
    """Recursively strip HTML tags from all strings in API data."""
    if isinstance(obj, str):
        return re.sub(r'<[^>]+>', '', obj)
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v) for v in obj]
    return obj


def main():
    # $ARGUMENTS arrives as a single quoted string — split it here
    raw = " ".join(sys.argv[1:])
    args = raw.split() if raw.strip() else []

    lang = 'tc'
    stops_mode = False
    filtered = []
    for token in args:
        low = token.lower()
        if low in ('en', 'tc'):
            lang = low
        elif low == 'stops':
            stops_mode = True
        else:
            filtered.append(token)

    if not filtered:
        usage()
        return

    route = filtered[0].upper()
    remaining = ' '.join(filtered[1:])

    if not os.path.exists(DATA_FILE):
        print('ERROR=NO_DATA')
        return

    with open(DATA_FILE) as f:
        db = json.load(f)

    print('---BEGIN---')
    if stops_mode:
        list_stops(db, route, lang)
    elif not remaining:
        usage()
    else:
        query_eta(db, route, remaining, lang)
    print('---END---')


def usage():
    print('用法: /hk-kmb-eta <路線> <車站名> [總站名] [en|tc]')
    print('例子: /hk-kmb-eta 42C 業成街 藍田')
    print('      /hk-kmb-eta 42C stops')


def list_stops(db, route, lang):
    s = STRINGS[lang]
    found = False
    dir_labels = {'O': s['outbound'], 'I': s['inbound']}
    for label in ['O', 'I']:
        rk = f'{route}/{label}/1'
        if rk not in db.get('routes', {}) or rk not in db.get('route_stops', {}):
            continue
        rt = db['routes'][rk]
        rs = db['route_stops'][rk]
        found = True
        dl = dir_labels[label]
        orig = rt.get(f'orig_{lang}', rt.get('orig_tc', ''))
        dest = rt.get(f'dest_{lang}', rt.get('dest_tc', ''))
        print(f'## {s["route"]} {route} — {s["stops"]}\n')
        print(f'### {orig} → {dest} ({dl})\n')
        print(f'| # | {s["stop_name"]} |')
        print('|---|----------|')
        for seq, sid in rs:
            st = db['stops'].get(sid)
            if st:
                print(f'| {seq} | {st.get(lang, st.get("tc", ""))} |')
        print()
    if not found:
        print('ERROR=NO_ROUTE')
    else:
        if lang == 'en':
            hint = f'_Usage: /hk-kmb-eta {route} <stop name> <terminal> to query ETA_'
        else:
            hint = f'_使用方式: /hk-kmb-eta {route} <車站名稱> <總站名> 查詢到站時間_'
        print(hint)


def query_eta(db, route, remaining, lang):
    stops = db['stops']

    routes = {}
    for label in ['O', 'I']:
        rk = f'{route}/{label}/1'
        if rk in db.get('routes', {}):
            routes[label] = db['routes'][rk]
    if not routes:
        print('ERROR=NO_ROUTE')
        return

    rs_data = {}
    for label in ['O', 'I']:
        rk = f'{route}/{label}/1'
        if rk in db.get('route_stops', {}):
            rs_data[label] = db['route_stops'][rk]

    # Resolve direction from trailing tokens, always keeping at least 1 keyword token.
    # Match backwards so a stop name like "建生" isn't consumed as a dest hint for "建生邨".
    tokens = remaining.split() if remaining.strip() else []
    filter_dir = ''
    kw_tokens = tokens[:]
    if len(tokens) >= 2:
        for i in range(len(tokens) - 1, 0, -1):
            candidate = ' '.join(tokens[i:]).lower()
            matched = False
            for label, rt in routes.items():
                for key in ['dest_tc', 'dest_en']:
                    val = rt.get(key, '').lower()
                    if val and candidate in val:
                        filter_dir = label
                        kw_tokens = tokens[:i]
                        matched = True
                        break
                if matched:
                    break
            if matched:
                break

    keyword = ' '.join(kw_tokens)
    if not keyword:
        print('ERROR=NO_KEYWORD')
        return

    # Keyword search
    route_dest = {l: routes[l].get('dest_tc', '') for l in routes}
    search_dirs = [filter_dir] if filter_dir else ['O', 'I']
    matches = []
    all_stops = []
    for label in search_dirs:
        if label not in rs_data:
            continue
        for seq, sid in rs_data[label]:
            s = stops.get(sid)
            if not s:
                continue
            dest = route_dest.get(label, '')
            all_stops.append((label, seq, s.get('tc', ''), s.get('en', ''), dest))
            names = (s.get('tc', '') + ' ' + s.get('en', '')).lower()
            if keyword.lower() in names:
                matches.append((seq, sid, s.get('tc', ''), s.get('en', ''), label))

    if not matches:
        print('ERROR=NO_MATCH')
        for label, seq, ntc, nen, dest in all_stops:
            print(f'  {seq}. {ntc} ({nen}) [往{dest}]')
        return

    matches.sort()
    b = matches[0]
    stop_id, stop_tc, stop_en, direction, seq = b[1], b[2], b[3], b[4], b[0]

    # Fetch ETA (only live API call)
    try:
        with urllib.request.urlopen(f'{BASE}/eta/{stop_id}/{route}/1', timeout=10) as r:
            eta_data = sanitize(json.loads(r.read()))
    except (urllib.error.URLError, json.JSONDecodeError, OSError):
        eta_data = None

    # Format output
    s = STRINGS[lang]
    rt = routes.get(direction, {})
    orig = rt.get(f'orig_{lang}', rt.get('orig_tc', ''))
    dest = rt.get(f'dest_{lang}', rt.get('dest_tc', ''))
    stop_name = stop_en if lang == 'en' else stop_tc

    if lang == 'en':
        print(f'## {s["title"]} — {s["route"]} {route}\n')
        print(f'**{s["route_label"]}**: {orig} → {dest}')
        print(f'**{s["stop_label"]}**: {stop_name} (Stop #{seq})\n')
    else:
        print(f'## {s["title"]} — {route}\n')
        print(f'**{s["route_label"]}**: {orig} → {dest}')
        print(f'**{s["stop_label"]}**: {stop_name} (第{seq}站)\n')

    now = datetime.now(HKT)
    entries = [e for e in (eta_data or {}).get('data', []) if e.get('dir') == direction]

    if not entries:
        print(s['no_eta'])
        return

    rmk_key = f'rmk_{lang}'
    print(f'| # | {s["eta_col"]} | {s["remaining_col"]} | {s["remark_col"]} |')
    if lang == 'en':
        print('|---|-----|-----------|--------|')
    else:
        print('|---|---------|---------|------|')

    unit = s['unit']
    for i, e in enumerate(entries[:3], 1):
        eta_str = e.get('eta', '')
        rmk = e.get(rmk_key, '') or ''
        if eta_str:
            try:
                eta_time = datetime.fromisoformat(eta_str)
                time_str = eta_time.strftime('%H:%M')
                diff = (eta_time - now).total_seconds() / 60
                remaining_str = '---' if diff < 0 else f'<1 {unit}' if diff < 1 else f'{int(diff)} {unit}'
            except (ValueError, KeyError):
                time_str = '---'
                remaining_str = '---'
        else:
            time_str = '---'
            remaining_str = '---'
        print(f'| {i} | {time_str} | {remaining_str} | {rmk} |')

    ts = (eta_data or {}).get('generated_timestamp', '')
    try:
        ts_str = datetime.fromisoformat(ts).strftime('%Y-%m-%d %H:%M HKT')
    except (ValueError, KeyError):
        ts_str = ts

    print()
    print(f'_{s["updated"]}: {ts_str}_')
    print(f'_{s["source"]}_')


if __name__ == '__main__':
    main()
