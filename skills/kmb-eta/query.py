#!/usr/bin/env python3
"""KMB bus ETA query. Reads static data from data.json, fetches only live ETA.

Usage: python3 query.py <route> [stop] [terminal] [en|tc] [stops]
"""
import json, urllib.request, sys, os
from datetime import datetime, timezone, timedelta

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, 'data.json')
BASE = "https://data.etabus.gov.hk/v1/transport/kmb"
HKT = timezone(timedelta(hours=8))


def main():
    args = sys.argv[1:]

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

    if stops_mode:
        list_stops(db, route, lang)
    elif not remaining:
        usage()
    else:
        query_eta(db, route, remaining, lang)


def usage():
    print('用法: /kmb-eta <路線> <車站名> [總站名] [en|tc]')
    print('例子: /kmb-eta 42C 業成街 藍田')
    print('      /kmb-eta 42C stops')


def list_stops(db, route, lang):
    found = False
    for label, dir_tc, dir_en in [('O', '出站', 'Outbound'), ('I', '入站', 'Inbound')]:
        rk = f'{route}/{label}/1'
        if rk not in db.get('routes', {}) or rk not in db.get('route_stops', {}):
            continue
        rt = db['routes'][rk]
        rs = db['route_stops'][rk]
        found = True
        dl = dir_en if lang == 'en' else dir_tc
        orig = rt.get(f'orig_{lang}', rt.get('orig_tc', ''))
        dest = rt.get(f'dest_{lang}', rt.get('dest_tc', ''))
        h_route = 'Route' if lang == 'en' else '路線'
        h_stops = 'All Stops' if lang == 'en' else '車站列表'
        print(f'## {h_route} {route} — {h_stops}\n')
        print(f'### {orig} → {dest} ({dl})\n')
        h = 'Stop Name' if lang == 'en' else '車站名稱'
        print(f'| # | {h} |')
        print('|---|----------|')
        for seq, sid in rs:
            s = db['stops'].get(sid)
            if s:
                print(f'| {seq} | {s.get(lang, s.get("tc", ""))} |')
        print()
    if not found:
        print('ERROR=NO_ROUTE')
    else:
        hint = f'_Usage: /kmb-eta {route} <stop name> <terminal> to query ETA_' if lang == 'en' else f'_使用方式: /kmb-eta {route} <車站名稱> <總站名> 查詢到站時間_'
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

    # Resolve direction: longest suffix match against dest
    tokens = remaining.split() if remaining.strip() else []
    filter_dir = ''
    kw_tokens = tokens[:]
    if tokens:
        for i in range(len(tokens)):
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
            eta_data = json.loads(r.read())
    except:
        eta_data = None

    # Format output
    rt = routes.get(direction, {})
    orig = rt.get(f'orig_{lang}', rt.get('orig_tc', ''))
    dest = rt.get(f'dest_{lang}', rt.get('dest_tc', ''))
    stop_name = stop_en if lang == 'en' else stop_tc

    if lang == 'en':
        print(f'## Bus ETA — Route {route}\n')
        print(f'**Route**: {orig} → {dest}')
        print(f'**Stop**: {stop_name} (Stop #{seq})\n')
    else:
        print(f'## 巴士到站時間 — {route}\n')
        print(f'**路線**: {orig} → {dest}')
        print(f'**車站**: {stop_name} (第{seq}站)\n')

    now = datetime.now(HKT)
    entries = [e for e in (eta_data or {}).get('data', []) if e.get('dir') == direction]

    if not entries:
        print('No ETA data available.' if lang == 'en' else '目前沒有到站時間資料。')
        return

    rmk_key = f'rmk_{lang}'
    if lang == 'en':
        print('| # | ETA | Remaining | Remark |')
        print('|---|-----|-----------|--------|')
    else:
        print('| # | 預計到達 | 剩餘時間 | 備註 |')
        print('|---|---------|---------|------|')

    unit = 'min' if lang == 'en' else '分鐘'
    for i, e in enumerate(entries[:3], 1):
        eta_str = e.get('eta', '')
        rmk = e.get(rmk_key, '') or ''
        if eta_str:
            try:
                eta_time = datetime.fromisoformat(eta_str)
                time_str = eta_time.strftime('%H:%M')
                diff = (eta_time - now).total_seconds() / 60
                remaining_str = '---' if diff < 0 else f'<1 {unit}' if diff < 1 else f'{int(diff)} {unit}'
            except:
                time_str = '---'
                remaining_str = '---'
        else:
            time_str = '---'
            remaining_str = '---'
        print(f'| {i} | {time_str} | {remaining_str} | {rmk} |')

    ts = (eta_data or {}).get('generated_timestamp', '')
    try:
        ts_str = datetime.fromisoformat(ts).strftime('%Y-%m-%d %H:%M HKT')
    except:
        ts_str = ts

    print()
    if lang == 'en':
        print(f'_Updated: {ts_str}_')
        print('_Source: DATA.GOV.HK / KMB_')
    else:
        print(f'_更新時間: {ts_str}_')
        print('_資料來源：DATA.GOV.HK / 九巴_')


if __name__ == '__main__':
    main()
