# A&E Waiting Time API

Hospital Authority open data API providing real-time Accident & Emergency waiting times across 18 public hospitals in Hong Kong.

## Endpoints

| Language | URL |
|----------|-----|
| English | `https://www.ha.org.hk/opendata/aed/aedwtdata2-en.json` |
| 繁體中文 | `https://www.ha.org.hk/opendata/aed/aedwtdata2-tc.json` |
| 简体中文 | `https://www.ha.org.hk/opendata/aed/aedwtdata2-sc.json` |

- **Method**: GET
- **Authentication**: None required
- **Update frequency**: Every ~15 minutes
- **Original source (xlsx)**: `https://www.ha.org.hk/opendata/aed/aedwtdata2-en.xlsx`

## Response Structure

```json
{
  "waitTime": [ ...array of hospital objects... ],
  "updateTime": "24/3/2026 5:30PM"
}
```

## Data Dictionary

Based on the official [Hospital Authority Data Specification](https://www.ha.org.hk/opendata/Data-Specification-for-A&E-Waiting-Time-en.pdf).

| Field | Type | Length | Description |
|-------|------|--------|-------------|
| `hospName` | Text | 150 | Full name of hospital |
| `t1wt` | Text | 40 | Estimated wait for Triage I (Critical) |
| `manageT1case` | Text | 3 | Whether A&E is managing T1 cases |
| `t2wt` | Text | 40 | Estimated wait for Triage II (Emergency) |
| `manageT2case` | Text | 3 | Whether A&E is managing T2 cases |
| `t3p50` | Text | 30 | Triage III (Urgent) — 50th percentile wait |
| `t3p95` | Text | 30 | Triage III (Urgent) — 95th percentile wait |
| `t45p50` | Text | 30 | Triage IV & V (Semi-urgent/Non-urgent) — 50th percentile wait |
| `t45p95` | Text | 30 | Triage IV & V (Semi-urgent/Non-urgent) — 95th percentile wait |
| `updateTime` | Text | 40 | Last update time (e.g. `27/07/2025 10:45 AM`) |

### Field Details

#### `t1wt` / `t2wt` — Critical & Emergency wait times

Values are one of:
- `"Managing multiple resuscitation cases"` — the A&E is currently handling critical patients
- `"0 minute"` / `"0 分鐘"` — immediate, no wait
- Estimated wait in minutes (e.g. `"less than 15 minutes"`)

#### `manageT1case` / `manageT2case` — Case management flags

| Value | Meaning |
|-------|---------|
| `Y` / `是` | Currently managing cases of this triage category |
| `N` / `否` | Not currently managing cases |
| `N/A` / `不適用` | A&E is managing multiple resuscitation cases (T1/T2 wait times unavailable) |

When value is `N/A`, the corresponding `t1wt`/`t2wt` field shows `"Managing multiple resuscitation cases"`.

#### `t3p50` / `t3p95` — Urgent wait times

- **p50** (median): Half of waiting patients can receive consultation within this time
- **p95**: Majority of waiting patients can receive consultation within this time
- Unit: **minutes** (e.g. `"23 minutes"`, `"23 分鐘"`)

#### `t45p50` / `t45p95` — Semi-urgent & Non-urgent wait times

- **p50** (median): Half of waiting patients can receive consultation within this time
- **p95**: Majority of waiting patients can receive consultation within this time
- Unit: **hours**, rounded up to nearest 0.5 hours (e.g. `"3.5 hours"`, `"3.5 小時"`)

## Triage Categories

| Category | Severity | Target Response Time |
|----------|----------|---------------------|
| T1 — Critical | Life-threatening, immediate resuscitation | Immediate |
| T2 — Emergency | Potentially life-threatening | ≤15 minutes |
| T3 — Urgent | Significant illness/injury | ≤30 minutes |
| T4 — Semi-urgent | Minor conditions | ≤60 minutes |
| T5 — Non-urgent | Minor ailments | ≤60 minutes |

Most walk-in A&E patients are triaged as T3, T4, or T5.

## Hospitals (18)

| English | 中文 |
|---------|------|
| Alice Ho Miu Ling Nethersole Hospital | 雅麗氏何妙齡那打素醫院 |
| Caritas Medical Centre | 明愛醫院 |
| Kwong Wah Hospital | 廣華醫院 |
| North District Hospital | 北區醫院 |
| North Lantau Hospital | 北大嶼山醫院 |
| Pamela Youde Nethersole Eastern Hospital | 東區尤德夫人那打素醫院 |
| Pok Oi Hospital | 博愛醫院 |
| Prince of Wales Hospital | 威爾斯親王醫院 |
| Princess Margaret Hospital | 瑪嘉烈醫院 |
| Queen Elizabeth Hospital | 伊利沙伯醫院 |
| Queen Mary Hospital | 瑪麗醫院 |
| Ruttonjee Hospital | 律敦治醫院 |
| St John Hospital | 長洲醫院 |
| Tin Shui Wai Hospital | 天水圍醫院 |
| Tseung Kwan O Hospital | 將軍澳醫院 |
| Tuen Mun Hospital | 屯門醫院 |
| United Christian Hospital | 基督教聯合醫院 |
| Yan Chai Hospital | 仁濟醫院 |

## CSDI Dataset

This dataset is also registered on the CSDI portal:
- **Dataset ID**: `fhb_rcd_1636947932221_94410`
- **Provider**: Hospital Authority
- **CSDI page**: `https://portal.csdi.gov.hk/csdi-webpage/dataset/fhb_rcd_1636947932221_94410`

## Example Request

```bash
curl -s https://www.ha.org.hk/opendata/aed/aedwtdata2-en.json | python3 -m json.tool
```
