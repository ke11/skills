# KMB Real-time Arrival Information API

Kowloon Motor Bus (KMB) and Long Win Bus (LWB) open data API providing static route/stop information and real-time estimated arrival times.

Based on the official [KMB Data Dictionary v1.02](https://data.etabus.gov.hk/) (10 May 2021).

## Base URL

```
https://data.etabus.gov.hk/v1/transport/kmb
```

- **Method**: GET
- **Authentication**: None required
- **Response format**: JSON
- **Company**: `"KMB"` (includes both KMB and LWB routes)

## Endpoints

### Static Data

| Endpoint | Type | Description |
|----------|------|-------------|
| `GET /route/` | RouteList | All routes |
| `GET /route/{route}/{direction}/{service_type}` | Route | Single route info |
| `GET /stop/` | StopList | All stops (~6700) |
| `GET /stop/{stop_id}` | Stop | Single stop info |
| `GET /route-stop/` | RouteStopList | All route-stop mappings |
| `GET /route-stop/{route}/{direction}/{service_type}` | RouteStop | Stops for a specific route |

### Real-time ETA

| Endpoint | Type | Description |
|----------|------|-------------|
| `GET /eta/{stop_id}/{route}/{service_type}` | ETA | ETA for one stop on one route |
| `GET /stop-eta/{stop_id}` | StopETA | ETA for all routes at one stop |
| `GET /route-eta/{route}/{service_type}` | RouteETA | ETA for all stops on one route |

**Parameters:**
- `{route}`: Route number (e.g., `42C`, `960`, `1A`)
- `{direction}`: `outbound` or `inbound`
- `{service_type}`: Usually `1`; some routes have variants (`2`, `3`, etc.)
- `{stop_id}`: 16-char hex string (e.g., `A3ADFCDF8487ADB9`)

## Response Envelope

All endpoints share this structure:

```json
{
  "type": "Route",
  "version": "1.0",
  "generated_timestamp": "2021-01-21T13:20:20+08:00",
  "data": { ... }
}
```

For list endpoints, `data` is an array of objects.

## Data Dictionary

### Route

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `co` | String | Bus company (always `"KMB"`) | `"KMB"` |
| `route` | String | Route number | `"74B"` |
| `bound` | String | Direction: `O` (outbound), `I` (inbound) | `"O"` |
| `service_type` | String | Service variant | `"1"` |
| `orig_en` | String | Origin in English | `"KOWLOON BAY"` |
| `orig_tc` | String | Origin in Traditional Chinese | `"九龍灣"` |
| `orig_sc` | String | Origin in Simplified Chinese | `"九龙湾"` |
| `dest_en` | String | Destination in English | `"TAI PO CENTRAL"` |
| `dest_tc` | String | Destination in Traditional Chinese | `"大埔中心"` |
| `dest_sc` | String | Destination in Simplified Chinese | `"大埔中心"` |
| `data_timestamp` | String | Data timestamp (ISO 8601) | `"2020-11-29T11:40:00+08:00"` |

### Stop

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `stop` | String | Stop ID (16-char hex) | `"A3ADFCDF8487ADB9"` |
| `name_tc` | String | Stop name in Traditional Chinese | `"中秀茂坪"` |
| `name_en` | String | Stop name in English | `"SAU MAU PING (CENTRAL)"` |
| `name_sc` | String | Stop name in Simplified Chinese | `"中秀茂坪"` |
| `lat` | String | Latitude (WGS84) | `"22.318856"` |
| `long` | String | Longitude (WGS84) | `"114.231353"` |
| `data_timestamp` | String | Data timestamp (ISO 8601) | `"2020-11-29T11:40:00+08:00"` |

### Route-Stop

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `co` | String | Bus company | `"KMB"` |
| `route` | String | Route number | `"1A"` |
| `bound` | String | Direction | `"O"` |
| `service_type` | String | Service variant | `"1"` |
| `seq` | Numeric | Stop sequence number | `1` |
| `stop` | String | Stop ID | `"A3ADFCDF8487ADB9"` |
| `data_timestamp` | String | Data timestamp (ISO 8601) | `"2020-11-29T11:40:00+08:00"` |

### ETA / StopETA / RouteETA

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `co` | String | Bus company | `"KMB"` |
| `route` | String | Route number | `"1A"` |
| `dir` | String | Direction: `O` or `I` | `"O"` |
| `service_type` | String | Service variant | `"1"` |
| `seq` | Numeric | Stop sequence number | `1` |
| `dest_en` | String | Destination in English | `"STAR FERRY"` |
| `dest_tc` | String | Destination in Traditional Chinese | `"尖沙咀碼頭"` |
| `dest_sc` | String | Destination in Simplified Chinese | `"尖沙咀码头"` |
| `eta_seq` | Numeric | ETA sequence (1, 2, or 3) | `1` |
| `eta` | String | Estimated arrival time (ISO 8601) | `"2022-11-29T15:48:00+08:00"` |
| `rmk_en` | String | Remark in English | `"Scheduled Bus"` |
| `rmk_tc` | String | Remark in Traditional Chinese | `"原定班次"` |
| `rmk_sc` | String | Remark in Simplified Chinese | `"原定班次"` |
| `data_timestamp` | String | Data timestamp (ISO 8601) | `"2020-11-29T11:40:00+08:00"` |

**Note:** The per-stop ETA endpoint (`/eta/{stop_id}/{route}/{service_type}`) returns the `stop` field in the response. The RouteETA and StopETA endpoints do **not** include the `stop` field — use `seq` to correlate with route-stop data.

**Note:** Empty data objects denote data not available.

## Notes

- All timestamps are in Hong Kong Time (UTC+8)
- The API serves both KMB and LWB routes under `co: "KMB"`
- ETA data returns up to 3 entries per stop (`eta_seq`: 1, 2, 3)
- Some routes have multiple `service_type` variants with different stop sequences
