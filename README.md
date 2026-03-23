# 香港 AI 代理技能

繁體中文 | [English](README.en.md)

> **Beta** — 本項目正在休閒開發中。技能、API 和配置格式可能會無通知地改變。歡迎提供反饋和貢獻。

為香港設計的 AI 代理開發技能。

---

## Installation

```bash
npx skills add ke11/skills --skill hk-weather
```

---

## Skills

### weather — 香港天氣

從[香港天文台開放數據 API](https://data.weather.gov.hk/weatherAPI/doc/HKO_Open_Data_API_Documentation.pdf) 獲取即時天氣資訊。無需 API 金鑰。

#### Usage

**關鍵字指令** (精確模式) — 使用特定關鍵字以獲得對應數據：

| 指令 | 獲取數據 | API | 速度 |
|------|---------|-----|------|
| `/hk-weather` | 天氣概況摘要 | 1 | 快 |
| `/hk-weather stations` | 各站氣溫、濕度、雨量 | 1 | 快 |
| `/hk-weather forecast` | 9天預報 | 1 | 快 |
| `/hk-weather rainfall` | 每小時雨量 | 1 | 快 |
| `/hk-weather warning` | 生效警告 | 2 | 中 |
| `/hk-weather detail` | 各站數據 + 預報 | 2 | 中 |
| `/hk-weather all` | 所有資訊 | 6 | 慢 |

**自然語言提問** (輕鬆模式) — 無需記憶指令，直接用中文提問：

| 提問範例 | 功能 |
|---------|------|
| `/hk-weather 今日會唔會落雨？` | 降雨查詢 |
| `/hk-weather 幾時落雨？` | 降雨查詢 |
| `/hk-weather 而家係咪打風？` | 颱風/警告狀況 |
| `/hk-weather 掛幾號風球？` | 颱風/警告狀況 |
| `/hk-weather 有冇暴雨警告？` | 天氣警告 |
| `/hk-weather 而家幾度？` | 各站氣溫 |
| `/hk-weather 濕唔濕？` | 各站濕度 |
| `/hk-weather 紫外線幾高？` | 紫外線指數 |
| `/hk-weather 下星期天氣如何？` | 9天預報 |

**語言代碼** (Language Codes) — 在指令最後附加語言代碼以切換輸出語言：

| 代碼 | 語言 | 範例 |
|------|------|------|
| `en` | English | `/hk-weather forecast en` |
| `tc` | 繁體中文 (預設) | `/hk-weather forecast tc` |
| `sc` | 簡體中文 | `/hk-weather forecast sc` |

#### Example Output

```
● 香港天氣概況

更新時間：2026-03-22 20:45 HKT

概況：現時影響廣東沿岸的偏東氣流正逐漸緩和。

預報 (本港地區今日天氣預測): 大致多雲。早上最低氣溫約21度。日間短暫時間有陽光，最高氣溫約27度。吹和緩偏東風。

展望：隨後數日部分時間有陽光。本週中後期日間炎熱。

資料來源：香港天文台
```

---

### kmb-eta — 九巴/龍運到站時間

從[九巴開放數據 API](https://data.etabus.gov.hk) 獲取即時巴士到站時間。無需 API 金鑰。

#### Usage

```
/kmb-eta <路線> <車站名> [總站名] [en|tc|sc]
```

| 指令 | 說明 |
|------|------|
| `/kmb-eta 42C 業成街 藍田` | 查詢往藍田方向的業成街站到站時間 |
| `/kmb-eta 42C 業成街` | 搜尋兩個方向的業成街站 |
| `/kmb-eta 42C stops` | 列出 42C 所有車站（查找車站名稱用） |
| `/kmb-eta 960 建生 en` | 查詢 960 建生站（英文輸出） |

- **總站名**：用總站名指定方向（如「藍田」即往藍田方向），省略則搜尋兩個方向
- **語言**：`tc` 繁體中文（預設）、`en` English、`sc` 簡體中文
- **離線資料**：路線及車站資料隨技能安裝，僅到站時間需即時查詢。更新資料：`npx skills update`

#### Example Output

```
● 巴士到站時間 — 42C

路線: 青衣(長亨邨) → 藍田站
車站: 業成街 (第18站)

| # | 預計到達 | 剩餘時間 | 備註     |
|---|---------|---------|----------|
| 1 | 16:54   | 3 分鐘  | 原定班次  |
| 2 | 17:00   | 9 分鐘  |          |
| 3 | 17:07   | 16 分鐘 |          |

更新時間: 2026-03-23 16:49 HKT
資料來源：DATA.GOV.HK / 九巴
```

---

## Privacy

本插件不收集、儲存或傳輸任何用戶數據。即時到站時間直接從[九巴開放數據 API](https://data.etabus.gov.hk) 查詢，天氣資料從[香港天文台公開數據 API](https://data.weather.gov.hk) 查詢，僅使用 HTTP GET 請求，無需 API 金鑰或身份驗證。

巴士路線及車站資料來源於 [DATA.GOV.HK](https://data.gov.hk)，由九龍巴士（一九三三）有限公司提供，依據[資料一線通使用條款](https://data.gov.hk/tc/terms-and-conditions)使用。

## License

MIT
