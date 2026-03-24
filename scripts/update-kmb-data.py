#!/usr/bin/env python3
"""Fetch all KMB/LWB static data and save as skills/hk-kmb-eta/scripts/data.json.

Data sourced from DATA.GOV.HK (https://data.gov.hk)
provided by The Kowloon Motor Bus Co. (1933) Ltd.

Run: python3 scripts/update-kmb-data.py
"""
import json, urllib.request, sys, os
from datetime import datetime, timezone, timedelta

BASE = "https://data.etabus.gov.hk/v1/transport/kmb"
OUT = os.path.join(os.path.dirname(__file__), '..', 'skills', 'hk-kmb-eta', 'scripts', 'data.json')

def fetch(url):
    print(f"  Fetching {url} ...", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.loads(r.read())

print("Updating KMB data...", file=sys.stderr)

stops_raw = fetch(f'{BASE}/stop')['data']
routes_raw = fetch(f'{BASE}/route/')['data']
rs_raw = fetch(f'{BASE}/route-stop')['data']

stops = {}
for s in stops_raw:
    stops[s['stop']] = {'tc': s['name_tc'], 'en': s['name_en']}

routes = {}
for r in routes_raw:
    key = f"{r['route']}/{r['bound']}/{r['service_type']}"
    routes[key] = {
        'orig_tc': r['orig_tc'], 'orig_en': r['orig_en'],
        'dest_tc': r['dest_tc'], 'dest_en': r['dest_en']
    }

route_stops = {}
for r in rs_raw:
    key = f"{r['route']}/{r['bound']}/{r['service_type']}"
    if key not in route_stops:
        route_stops[key] = []
    route_stops[key].append([int(r['seq']), r['stop']])
for key in route_stops:
    route_stops[key].sort()

hkt = timezone(timedelta(hours=8))
data = {
    'generated': datetime.now(hkt).strftime('%Y-%m-%d'),
    'stops': stops,
    'routes': routes,
    'route_stops': route_stops
}

out = os.path.normpath(OUT)
with open(out, 'w') as f:
    json.dump(data, f, ensure_ascii=False, separators=(',', ':'))

size = os.path.getsize(out)
print(f"\nDone: {out}", file=sys.stderr)
print(f"  Stops: {len(stops)}, Routes: {len(routes)}, Route-stop keys: {len(route_stops)}", file=sys.stderr)
print(f"  Size: {size / 1024:.0f} KB", file=sys.stderr)
