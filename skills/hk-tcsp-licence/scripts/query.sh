#!/usr/bin/env bash
# TCSP Licensee query — searches Companies Registry data via CSDI Portal.
set -euo pipefail

WFS_URL="https://portal.csdi.gov.hk/server/services/common/cr_rcd_1668395265357_67292/MapServer/WFSServer"
MAX_RESULTS=20

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
lang="tc"
field=""
keyword_parts=()

for tok in "$@"; do
  low=$(echo "$tok" | tr '[:upper:]' '[:lower:]')
  case "$low" in
    en|tc) lang="$low" ;;
    name|licence|license|address)
      if [ -z "$field" ]; then
        [ "$low" = "license" ] && field="licence" || field="$low"
      else
        keyword_parts+=("$tok")
      fi
      ;;
    *) keyword_parts+=("$tok") ;;
  esac
done

keyword="${keyword_parts[*]:-}"

# ---------------------------------------------------------------------------
# Validate required arguments
# ---------------------------------------------------------------------------
if [ -z "$keyword" ]; then
  echo "ERROR=NO_KEYWORD"
  exit 0
fi

if [ -z "$field" ]; then
  echo "ERROR=NO_FIELD keyword=${keyword}"
  exit 0
fi

# ---------------------------------------------------------------------------
# Build OGC WFS XML filter
# ---------------------------------------------------------------------------
# XML-escape the keyword (& < > " ')
xml_escape() {
  echo "$1" | sed "s/&/\&amp;/g; s/</\&lt;/g; s/>/\&gt;/g; s/\"/\&quot;/g; s/'/\&apos;/g"
}

kw_escaped=$(xml_escape "$keyword")
kw_upper=$(echo "$keyword" | tr '[:lower:]' '[:upper:]')
kw_upper_escaped=$(xml_escape "$kw_upper")

like_block() {
  local col="$1" val="$2"
  echo "<fes:PropertyIsLike wildCard=\"*\" singleChar=\".\" escapeChar=\"!\"><fes:ValueReference>${col}</fes:ValueReference><fes:Literal>*${val}*</fes:Literal></fes:PropertyIsLike>"
}

case "$field" in
  name)
    inner="<fes:Or>$(like_block Name_of_TCSP_Licensee_in_English "$kw_upper_escaped")$(like_block Name_of_TCSP_Licensee_in_Chinese "$kw_escaped")</fes:Or>"
    ;;
  licence)
    inner=$(like_block Licence_No "$kw_upper_escaped")
    ;;
  address)
    inner=$(like_block Business_Address "$kw_upper_escaped")
    ;;
esac

xml_body="<?xml version=\"1.0\"?><wfs:GetFeature service=\"WFS\" version=\"2.0.0\" count=\"${MAX_RESULTS}\" outputFormat=\"GeoJSON\" xmlns:wfs=\"http://www.opengis.net/wfs/2.0\" xmlns:fes=\"http://www.opengis.net/fes/2.0\"><wfs:Query typeNames=\"geotagging\"><fes:Filter>${inner}</fes:Filter></wfs:Query></wfs:GetFeature>"

# ---------------------------------------------------------------------------
# Fetch data
# ---------------------------------------------------------------------------
response=$(curl -s --max-time 15 \
  -X POST \
  -H "Referer: https://portal.csdi.gov.hk/" \
  -H "Content-Type: application/xml" \
  -d "$xml_body" \
  "$WFS_URL" 2>/dev/null) || true

if [ -z "$response" ]; then
  echo "ERROR=API_UNREACHABLE"
  exit 1
fi

# ---------------------------------------------------------------------------
# Parse JSON and format output (minimal python3 for reliable JSON handling)
# ---------------------------------------------------------------------------
echo "$response" | python3 -c "
import sys, json, re

def sanitize(obj):
    if isinstance(obj, str):
        return re.sub(r'<[^>]+>', '', obj)
    if isinstance(obj, dict):
        return {k: sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [sanitize(v) for v in obj]
    return obj

lang = '${lang}'
field = '${field}'
keyword = '''${keyword}'''
max_results = ${MAX_RESULTS}

def _l(en, zh):
    return en if lang == 'en' else zh

field_labels = {
    'en': {'name': 'name', 'licence': 'licence no.', 'address': 'address'},
    'tc': {'name': '名稱', 'licence': '牌照號碼', 'address': '地址'},
}
fl = field_labels.get(lang, field_labels['tc']).get(field, field)
attr = _l('_Source: Companies Registry / CSDI_', '_資料來源：公司註冊處 / 空間數據共享平台 CSDI_')

try:
    data = sanitize(json.loads(sys.stdin.read()))
except Exception:
    print(_l('Failed to parse API response.', '無法解析 API 回應。'))
    sys.exit(1)

if 'error' in data:
    msg = data['error'] if isinstance(data['error'], str) else data['error'].get('message', 'Unknown')
    print(_l(f'API error: {msg}', f'API 錯誤：{msg}'))
    sys.exit(1)

features = data.get('features', [])
count = len(features)

if count == 0:
    out = _l(
        f'## TCSP Licensee Search\n\nNo results found for \"{keyword}\" in {fl}.',
        f'## TCSP 持牌人查詢\n\n在{fl}中找不到「{keyword}」的記錄。')
    print(f'---BEGIN---\n{out}\n\n{attr}\n---END---')
    sys.exit(0)

has_more = count >= max_results
count_str = f'{count}+' if has_more else str(count)

lines = [_l('## TCSP Licensee Search Results', '## TCSP 持牌人查詢結果')]
lines.append('')
lines.append(_l(
    f'Found {count_str} record(s) matching \"{keyword}\" in {fl}.',
    f'在{fl}中找到 {count_str} 筆「{keyword}」的記錄。'))

get = lambda f: f.get('properties', f.get('attributes', {}))

has_remarks = any(get(f).get('Remarks_in_English') or get(f).get('Remarks_in_Chinese') for f in features)

lines.append('')
if has_remarks:
    lines.append(_l(
        '| Licence No | English Name | Chinese Name | Business Address | Remarks |',
        '| 牌照號碼 | 英文名稱 | 中文名稱 | 營業地址 | 備註 |'))
    lines.append('|------------|-------------|-------------|------------------|---------|')
else:
    lines.append(_l(
        '| Licence No | English Name | Chinese Name | Business Address |',
        '| 牌照號碼 | 英文名稱 | 中文名稱 | 營業地址 |'))
    lines.append('|------------|-------------|-------------|------------------|')

for f in features:
    a = get(f)
    lic = a.get('Licence_No', '') or '—'
    en_name = a.get('Name_of_TCSP_Licensee_in_English', '') or '—'
    cn_name = a.get('Name_of_TCSP_Licensee_in_Chinese', '') or '—'
    addr = a.get('Business_Address', '') or '—'
    if has_remarks:
        remark = _l(a.get('Remarks_in_English', '') or '', a.get('Remarks_in_Chinese', '') or '')
        lines.append(f'| {lic} | {en_name} | {cn_name} | {addr} | {remark} |')
    else:
        lines.append(f'| {lic} | {en_name} | {cn_name} | {addr} |')

if has_more:
    lines.append('')
    lines.append(_l(
        f'_Showing first {max_results} results. Refine your search for more specific results._',
        f'_顯示前 {max_results} 筆結果，請縮小搜尋範圍以獲得更精確的結果。_'))

print('---BEGIN---')
print('\n'.join(lines))
print('')
print(attr)
print('---END---')
"
