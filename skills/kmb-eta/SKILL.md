---
name: kmb-eta
description: "Query KMB/LWB real-time bus arrival time. Auto-detects nearest stop from GPS location."
allowed-tools: [Bash]
disable-model-invocation: true
argument-hint: "<route> [bus stop] [I|O] [en|tc|sc]"
---

Fetch real-time KMB/LWB bus ETA for: $ARGUMENTS

## Step 1: Parse Arguments

Split `$ARGUMENTS` by spaces into tokens. Extract:

- **Route** (required): First token that looks like a bus route number (alphanumeric, e.g. `42C`, `1A`, `960`, `E33`). Case-insensitive, convert to uppercase.
- **Language tokens**: `en` (English), `tc` (Traditional Chinese, default), `sc` (Simplified Chinese). Default: `tc`
- **Direction tokens**: `I` (inbound), `O` (outbound). Case-insensitive. Optional.
- **Mode keyword**: `stops` — if present, list all stops on the route and exit (see Flow C below).
- **Stop keyword**: Any remaining tokens joined together form the stop search keyword. Can be Chinese (e.g. `長亨`, `油塘`) or English (e.g. `cheung hang`, `yau tong`).

If no route is provided, show usage and stop:
```
用法: /kmb-eta <路線> [車站] [I|O] [en|tc|sc]
例子: /kmb-eta 42C                  ← 自動定位最近車站
      /kmb-eta 42C 長亨 O           ← 指定車站及方向
      /kmb-eta 42C stops            ← 列出所有車站
      /kmb-eta 960 建生 I en        ← 英文輸出
```

## Step 2: Resolve Stop

There are three flows depending on the arguments provided.

### Flow C: List Stops Mode (keyword is `stops`)

If the stop keyword is `stops` (case-insensitive), list all stops on the route for both directions.

**Step 2C-1**: Fetch route-stops for both directions, route info, and all stops in parallel:

```bash
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{ROUTE}/outbound/1" > /tmp/kmb_rs_o.json &
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{ROUTE}/inbound/1" > /tmp/kmb_rs_i.json &
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/route/{ROUTE}/outbound/1" > /tmp/kmb_route_o.json &
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/route/{ROUTE}/inbound/1" > /tmp/kmb_route_i.json &
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/stop" > /tmp/kmb_stops.json &
wait
```

**Step 2C-2**: Build and display the stop list using python3:

```bash
python3 -c "
import json, sys

lang = sys.argv[1]
stops = json.load(open('/tmp/kmb_stops.json'))['data']
stop_map = {s['stop']: s for s in stops}

name_key = 'name_' + lang

for direction, label, dir_label_tc, dir_label_en in [('outbound', 'O', '出站', 'Outbound'), ('inbound', 'I', '入站', 'Inbound')]:
    fname_rs = f'/tmp/kmb_rs_{label.lower()}.json'
    fname_rt = f'/tmp/kmb_route_{label.lower()}.json'
    try:
        rs = json.load(open(fname_rs))['data']
        rt = json.load(open(fname_rt))['data']
    except:
        continue
    if not rs:
        continue

    dir_label = dir_label_en if lang == 'en' else dir_label_tc
    orig = rt.get('orig_' + lang, '')
    dest = rt.get('dest_' + lang, '')
    print(f'### {label} {dir_label}: {orig} → {dest}')
    print()
    if lang == 'en':
        print('| # | Stop Name |')
        print('|---|-----------|')
    else:
        print('| # | 車站名稱 |')
        print('|---|----------|')
    for r in rs:
        s = stop_map.get(r['stop'])
        if s:
            print(f'| {r[\"seq\"]} | {s.get(name_key, s[\"name_tc\"])} |')
    print()
" "{LANG}"
```

**Step 2C-3**: Present the output with a header, then clean up and stop (do not proceed to Step 3):

Output header (tc):
```
## 路線 {ROUTE} 車站列表
```

Output header (en):
```
## Route {ROUTE} — All Stops
```

Append usage hint at the end:
- tc/sc: `_使用方式: /kmb-eta {ROUTE} <車站名稱> <I|O> 查詢到站時間_`
- en: `_Usage: /kmb-eta {ROUTE} <bus stop> <I|O> to query ETA_`

Clean up temp files:
```bash
rm -f /tmp/kmb_rs_o.json /tmp/kmb_rs_i.json /tmp/kmb_route_o.json /tmp/kmb_route_i.json /tmp/kmb_stops.json
```

**Stop here** — do not proceed to Step 3 or Step 4.

### Flow A: Auto-Location (no stop keyword provided)

**Step 2A-1**: Get current GPS location via macOS CoreLocation. Run this Swift script:

```bash
LOC=$(swift - 2>/dev/null <<'SWIFT'
import CoreLocation
import Foundation

class D: NSObject, CLLocationManagerDelegate {
    var done = false; var lat = 0.0; var lon = 0.0; var ok = false
    func locationManager(_ m: CLLocationManager, didUpdateLocations l: [CLLocation]) {
        if let c = l.last { lat = c.coordinate.latitude; lon = c.coordinate.longitude; ok = true }
        done = true
    }
    func locationManager(_ m: CLLocationManager, didFailWithError e: Error) { done = true }
    func locationManagerDidChangeAuthorization(_ m: CLLocationManager) {
        let s = m.authorizationStatus
        if s == .denied || s == .restricted { done = true }
    }
}
let m = CLLocationManager(); let d = D(); m.delegate = d
m.desiredAccuracy = kCLLocationAccuracyBest; m.startUpdatingLocation()
let t = Date().addingTimeInterval(5)
while !d.done && Date() < t { RunLoop.current.run(until: Date().addingTimeInterval(0.1)) }
if d.ok { print("\(d.lat),\(d.lon)") } else { print("FAILED") }
SWIFT
)
echo "$LOC"
```

If the output is `FAILED` or empty, show this error and stop:
```
無法取得目前位置。請提供車站關鍵字及方向：
/kmb-eta {route} <車站名稱> <I|O>
例子: /kmb-eta {route} 長亨 O
```

**Step 2A-2**: Extract latitude and longitude from the output (format: `lat,lon`). Store as `USER_LAT` and `USER_LON`.

**Step 2A-3**: Fetch route-stops for both directions and all stops in parallel:

```bash
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{ROUTE}/outbound/1" > /tmp/kmb_rs_o.json &
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{ROUTE}/inbound/1" > /tmp/kmb_rs_i.json &
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/stop" > /tmp/kmb_stops.json &
wait
```

**Step 2A-4**: Find the nearest stop on this route using python3:

```bash
python3 -c "
import json, math, sys

lat, lon = float(sys.argv[1]), float(sys.argv[2])
route = sys.argv[3]

stops = json.load(open('/tmp/kmb_stops.json'))['data']
stop_map = {s['stop']: s for s in stops}

results = []
for direction, label in [('outbound', 'O'), ('inbound', 'I')]:
    fname = f'/tmp/kmb_rs_{label.lower()}.json'
    try:
        rs = json.load(open(fname))['data']
    except:
        continue
    for r in rs:
        sid = r['stop']
        s = stop_map.get(sid)
        if not s:
            continue
        slat, slon = float(s['lat']), float(s['long'])
        p = math.pi / 180
        a = 0.5 - math.cos((slat - lat) * p) / 2 + math.cos(lat * p) * math.cos(slat * p) * (1 - math.cos((slon - lon) * p)) / 2
        d = 2 * 6371000 * math.asin(math.sqrt(a))
        results.append((d, sid, s['name_tc'], s['name_en'], s['name_sc'], label, r['seq']))

if not results:
    print('NO_ROUTE')
    sys.exit(0)

results.sort()
best = results[0]
print(f'{best[1]}|{best[2]}|{best[3]}|{best[4]}|{best[5]}|{best[6]}|{best[0]:.0f}')
" "$USER_LAT" "$USER_LON" "{ROUTE}"
```

Output format: `stop_id|name_tc|name_en|name_sc|direction|seq|distance_meters`

If output is `NO_ROUTE`, the route number is invalid. Show error:
```
找不到路線 {ROUTE}。請確認路線編號是否正確。
```

Parse the output. Store: `STOP_ID`, `STOP_NAME_TC`, `STOP_NAME_EN`, `STOP_NAME_SC`, `DIRECTION` (O or I), `SEQ`, `DISTANCE`.

Clean up temp files:
```bash
rm -f /tmp/kmb_rs_o.json /tmp/kmb_rs_i.json /tmp/kmb_stops.json
```

### Flow B: Stop Keyword Search (stop keyword provided)

A direction token MUST also be provided. If direction is missing, show error:
```
請同時提供方向 (I=入站 / O=出站)：
/kmb-eta {ROUTE} {keyword} <I|O>
```

**Step 2B-1**: Determine the API direction string: `I` → `inbound`, `O` → `outbound`.

**Step 2B-2**: Fetch route-stops for the given direction and all stops in parallel:

```bash
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/route-stop/{ROUTE}/{DIRECTION_STR}/1" > /tmp/kmb_rs.json &
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/stop" > /tmp/kmb_stops.json &
wait
```

**Step 2B-3**: Search for matching stop using python3:

```bash
python3 -c "
import json, sys

keyword = sys.argv[1].lower()

stops = json.load(open('/tmp/kmb_stops.json'))['data']
stop_map = {s['stop']: s for s in stops}

try:
    rs = json.load(open('/tmp/kmb_rs.json'))['data']
except:
    print('NO_ROUTE')
    sys.exit(0)

if not rs:
    print('NO_ROUTE')
    sys.exit(0)

matches = []
for r in rs:
    s = stop_map.get(r['stop'])
    if not s:
        continue
    names = (s.get('name_tc','') + ' ' + s.get('name_en','') + ' ' + s.get('name_sc','')).lower()
    if keyword in names:
        matches.append((int(r['seq']), r['stop'], s['name_tc'], s['name_en'], s['name_sc']))

if not matches:
    # Show all stops on this route for reference
    print('NO_MATCH')
    for r in rs:
        s = stop_map.get(r['stop'])
        if s:
            print(f\"  {r['seq']}. {s['name_tc']} ({s['name_en']})\")
    sys.exit(0)

matches.sort()
best = matches[0]
print(f'{best[1]}|{best[2]}|{best[3]}|{best[4]}')
" "{KEYWORD}"
```

If output starts with `NO_ROUTE`, the route/direction is invalid. Show error.

If output starts with `NO_MATCH`, show the list of stops on this route from the output and ask user to refine their keyword.

Otherwise, parse: `STOP_ID`, `STOP_NAME_TC`, `STOP_NAME_EN`, `STOP_NAME_SC`. `DISTANCE` is not applicable.

Clean up temp files:
```bash
rm -f /tmp/kmb_rs.json /tmp/kmb_stops.json
```

## Step 3: Fetch ETA

Map `DIRECTION`: `O` → `outbound`, `I` → `inbound`.

Fetch ETA and route info in parallel:

```bash
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/eta/{STOP_ID}/{ROUTE}/1" > /tmp/kmb_eta.json &
curl -s "https://data.etabus.gov.hk/v1/transport/kmb/route/{ROUTE}/{DIRECTION_STR}/1" > /tmp/kmb_route.json &
wait
echo "===ETA===" && cat /tmp/kmb_eta.json && echo ""
echo "===ROUTE===" && cat /tmp/kmb_route.json && echo ""
rm -f /tmp/kmb_eta.json /tmp/kmb_route.json
```

## Step 4: Present Results

From the ETA response, filter entries matching the resolved direction (`dir` field = `DIRECTION`). Each entry has:
- `eta`: ISO 8601 timestamp of estimated arrival
- `eta_seq`: sequence (1, 2, 3)
- `rmk_tc`, `rmk_en`, `rmk_sc`: remark text
- `dest_tc`, `dest_en`, `dest_sc`: destination

From the route response:
- `orig_tc/en/sc`: route origin
- `dest_tc/en/sc`: route destination

Choose field suffix based on language: `tc` → `_tc`, `en` → `_en`, `sc` → `_sc`.

Calculate "remaining time" = `eta` timestamp minus current time, in minutes. If negative or eta is empty/null, show `---`.

### Output Format (Traditional Chinese — default)

```
## 巴士到站時間 — {ROUTE}

**路線**: {orig} → {dest}
**車站**: {stop_name} (第{SEQ}站)
{if DISTANCE: **距離**: 約 {DISTANCE}m（最近車站）}

| # | 預計到達 | 剩餘時間 | 備註 |
|---|---------|---------|------|
| 1 | {HH:MM} | {N} 分鐘 | {rmk} |
| 2 | {HH:MM} | {N} 分鐘 | {rmk} |
| 3 | {HH:MM} | {N} 分鐘 | {rmk} |

_更新時間: {data_timestamp as YYYY-MM-DD HH:MM HKT}_
_資料來源：九巴/龍運_
```

### Output Format (English)

```
## Bus ETA — Route {ROUTE}

**Route**: {orig} → {dest}
**Stop**: {stop_name} (Stop #{SEQ})
{if DISTANCE: **Distance**: ~{DISTANCE}m (nearest stop)}

| # | ETA | Remaining | Remark |
|---|-----|-----------|--------|
| 1 | {HH:MM} | {N} min | {rmk} |
| 2 | {HH:MM} | {N} min | {rmk} |
| 3 | {HH:MM} | {N} min | {rmk} |

_Updated: {data_timestamp as YYYY-MM-DD HH:MM HKT}_
_Source: KMB/LWB_
```

### Output Format (Simplified Chinese)

Same as Traditional Chinese but use `_sc` fields and:
- Attribution: `_数据来源：九巴/龙运_`
- Headers: `巴士到站时间`, `路线`, `车站`, `距离`, `预计到达`, `剩余时间`, `备注`, `更新时间`

### Special Cases

- If ETA response `data` array is empty → show "目前沒有到站時間資料" / "No ETA data available"
- If `eta` field is null or empty for an entry → show `---` for ETA and remaining time
- If `rmk` is empty → leave the remark cell blank
- Omit the `距離` line if stop was resolved via keyword (Flow B), not auto-location
- Times: convert ISO 8601 `eta` to `HH:MM` format. Convert `data_timestamp` to `YYYY-MM-DD HH:MM HKT`

## Error Handling

- If any curl request fails → report connection error and stop
- If route returns empty data → "找不到路線 {ROUTE}" / "Route {ROUTE} not found"
- If ETA returns empty → show route/stop info but note no ETA available
- Always clean up `/tmp/kmb_*.json` temp files

## Rules

- **Read-only** — only GET requests
- Always use `curl -s` for silent mode
- Default language is `tc` (Traditional Chinese)
- Route numbers are case-insensitive, always convert to uppercase
- All timestamps are in HKT (+08:00)
