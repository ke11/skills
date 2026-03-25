# 香港 AI 代理技能

繁體中文 | [English](README.en.md)

> **Beta** — 休閒項目。技能、API 和配置格式可能會無通知地改變。歡迎提供反饋和貢獻。

為香港設計的 AI 代理技能。所有數據來自公開 API，無需金鑰。

## 快速安裝

```bash
npx skills add ke11/skills --skill hk-weather
npx skills add ke11/skills --skill hk-kmb-eta
npx skills add ke11/skills --skill hk-aed-wait
npx skills add ke11/skills --skill hk-tcsp-licence
npx skills add ke11/skills --skill hk-holiday
```

---

## 技能一覽

| 技能 | 功能 | 數據來源 |
|------|------|---------|
| [hk-weather](#hk-weather) | 即時天氣、預報、警告、雨量 | [香港天文台](https://data.weather.gov.hk) |
| [hk-kmb-eta](#hk-kmb-eta) | 巴士到站時間、路線查詢 | [九巴開放數據](https://data.etabus.gov.hk) |
| [hk-aed-wait](#hk-aed-wait) | 急症室等候時間 | [醫院管理局](https://www.ha.org.hk/opendata) |
| [hk-tcsp-licence](#hk-tcsp-licence) | TCSP 持牌人查詢 | [公司註冊處 / CSDI](https://portal.csdi.gov.hk) |
| [hk-holiday](#hk-holiday) | 公眾假期查詢 | [1823 政府熱線](https://www.1823.gov.hk) |

---

## hk-weather

香港天氣

從香港天文台開放數據 API 獲取即時天氣資訊。

### 關鍵字指令

| 指令 | 獲取數據 | 速度 |
|------|---------|------|
| `/hk-weather` | 天氣概況摘要 | 快 |
| `/hk-weather stations` | 各站氣溫、濕度、雨量 | 快 |
| `/hk-weather forecast` | 9天預報 | 快 |
| `/hk-weather rainfall` | 每小時雨量 | 快 |
| `/hk-weather warning` | 生效警告 | 中 |
| `/hk-weather detail` | 各站數據 + 預報 | 中 |
| `/hk-weather all` | 所有資訊 | 慢 |

### 自然語言提問

無需記憶指令，直接用中文或英文提問：

| 提問範例 | 功能 |
|---------|------|
| `/hk-weather 今日會唔會落雨？` | 降雨查詢 |
| `/hk-weather 而家係咪打風？` | 颱風/警告狀況 |
| `/hk-weather 而家幾度？` | 各站氣溫 |
| `/hk-weather 紫外線幾高？` | 紫外線指數 |
| `/hk-weather 下星期天氣如何？` | 9天預報 |

### 語言

在指令最後附加語言代碼：`en` English、`tc` 繁體中文（預設）、`sc` 簡體中文。

### 輸出範例

```
## 香港天氣概況

更新時間: 2026-03-22 20:45 HKT

概況: 現時影響廣東沿岸的偏東氣流正逐漸緩和。

預報 (本港地區今日天氣預測): 大致多雲。日間短暫時間有陽光，最高氣溫約27度。

展望: 隨後數日部分時間有陽光。本週中後期日間炎熱。

資料來源：香港天文台
```

---

## hk-kmb-eta

九巴到站時間

從九巴開放數據 API 獲取即時巴士到站時間。

### 用法

```
/hk-kmb-eta <路線> <車站名> [總站名] [en|tc]
```

| 指令 | 說明 |
|------|------|
| `/hk-kmb-eta 42C 業成街 藍田` | 查詢往藍田方向的業成街站 |
| `/hk-kmb-eta 42C 業成街` | 搜尋兩個方向的業成街站 |
| `/hk-kmb-eta 42C stops` | 列出 42C 所有車站 |
| `/hk-kmb-eta 960 建生 en` | 英文輸出 |

- **總站名** — 用總站名指定方向（如「藍田」即往藍田方向），省略則搜尋兩個方向
- **語言** — `tc` 繁體中文（預設）、`en` English
- **離線資料** — 路線及車站資料隨技能安裝，僅到站時間需即時查詢

### 輸出範例

```
## 巴士到站時間 — 42C

路線: 青衣(長亨邨) → 藍田站
車站: 葵涌業成街 (第15站)

| # | 預計到達 | 剩餘時間 | 備註     |
|---|---------|---------|----------|
| 1 | 16:54   | 3 分鐘  | 原定班次  |
| 2 | 17:00   | 9 分鐘  |          |
| 3 | 17:07   | 16 分鐘 |          |

更新時間: 2026-03-23 16:49 HKT
資料來源：DATA.GOV.HK / 九巴
```

---

## hk-aed-wait

急症室等候時間

從醫院管理局開放數據 API 獲取即時急症室等候時間，涵蓋全港18間公立醫院，每約15分鐘更新。

### 用法

```
/hk-aed-wait                     所有醫院（按地區分組）
/hk-aed-wait <醫院名>            查詢指定醫院
/hk-aed-wait <hospital> en       英文輸出
```

| 指令 | 說明 |
|------|------|
| `/hk-aed-wait` | 全部醫院等候時間 |
| `/hk-aed-wait 屯門` | 屯門醫院等候時間 |
| `/hk-aed-wait Queen en` | 搜尋 "Queen" 相關醫院（英文） |

- **語言** — `tc` 繁體中文（預設）、`en` English、`sc` 簡體中文

### 輸出範例

```
## 急症室等候時間

於2026年3月24日 下午6時15分，病人到達急症室求診預計等候時間。
一半輪候病人能在以下時間內就診，大部份人可於括號內顯示的時間就診。

| 醫院 | 分流類別 I | 分流類別 II | 分流類別 III | 分流類別 IV & V |
|------|:---------:|:----------:|:-----------:|:--------------:|
| 港島區 | | | | |
| 瑪麗醫院 | 0 分鐘 | 少於 15 分鐘 | 35 分鐘 (79 分鐘) | 3 小時 (4 小時) |
| ...

分流類別 I-V 指危殆、危急、緊急、次緊急及非緊急類別。
🔴 指急症室正在治理分流類別 I/II 的病人。

資料來源：醫院管理局 / 空間數據共享平台 CSDI
```

---

## hk-tcsp-licence

TCSP 持牌人查詢

從空間數據共享平台 (CSDI) 查詢香港信託或公司服務持牌人資料，數據來自公司註冊處。

### 用法

```
/hk-tcsp-licence <欄位> <關鍵字> [en|tc]
```

| 指令 | 說明 |
|------|------|
| `/hk-tcsp-licence name FULLYEAR` | 按英文名稱搜尋 |
| `/hk-tcsp-licence name 富年` | 按中文名稱搜尋 |
| `/hk-tcsp-licence licence TC000002` | 按牌照號碼搜尋 |
| `/hk-tcsp-licence address wan chai en` | 按營業地址搜尋（英文輸出） |

- **欄位** — `name`（英文或中文名稱）、`licence`（牌照號碼）、`address`（營業地址）
- **語言** — `tc` 繁體中文（預設）、`en` English
- 結果上限為 20 筆，有備註的記錄會自動顯示備註欄

### 輸出範例

```
## TCSP 持牌人查詢結果

在名稱中找到 1 筆「富年」的記錄。

| 牌照號碼 | 英文名稱 | 中文名稱 | 營業地址 |
|----------|---------|---------|---------|
| TC000002 | FULLYEAR CONSULTANTS LIMITED | 富年顧問有限公司 | UNIT B, 12/F, KA NIN WAH COMMERCIAL BUILDING, 423-425 HENNESSY ROAD, WAN CHAI, HONG KONG |

資料來源：公司註冊處 / 空間數據共享平台 CSDI
```

---

## hk-holiday

公眾假期

從 1823 政府日曆 API 獲取香港公眾假期資料，支援繁體中文、簡體中文及英文。

### 用法

```
/hk-holiday                即將來臨的公眾假期
/hk-holiday 2025           2025年所有公眾假期
/hk-holiday next           下一個公眾假期
/hk-holiday next en        下一個公眾假期（英文）
```

| 指令 | 說明 |
|------|------|
| `/hk-holiday` | 即將來臨的假期（附倒數） |
| `/hk-holiday 2025` | 2025年完整假期表 |
| `/hk-holiday 2026 sc` | 2026年假期表（簡體中文） |
| `/hk-holiday next` | 下一個公眾假期 |
| `/hk-holiday next en` | 下一個公眾假期（英文） |

- **語言** — `tc` 繁體中文（預設）、`en` English、`sc` 簡體中文

### 輸出範例

```
## 即將來臨的香港公眾假期

| 日期 | 假期名稱 | 最長連續假期 | 倒數 |
|------|----------|------|------|
| 2026-04-03 (五) | 🔴 耶穌受難節 | ⭐ 5日 (4/3 → 4/7) | 9 日後 |
| 2026-04-04 (六) | 🔴 耶穌受難節翌日 |  | 10 日後 |
| 2026-05-01 (五) | 🔴 勞動節 | ⭐ 3日 (5/1 → 5/3) | 37 日後 |
| ...

🔴 假期 · ⚫ 已過 · ⭐ 最長連續假期（含週末）

資料來源：1823，香港特別行政區政府
```

---

## 私隱

本插件不收集、儲存或傳輸任何用戶數據。所有數據僅使用 HTTP GET 請求從公開 API 獲取，無需 API 金鑰或身份驗證。

- 天氣資料：[香港天文台公開數據 API](https://data.weather.gov.hk)
- 巴士路線及車站資料來源於 [DATA.GOV.HK](https://data.gov.hk)，依據[資料一線通使用條款](https://data.gov.hk/tc/terms-and-conditions)使用
- 急症室等候時間：[醫院管理局](https://www.ha.org.hk) / [CSDI 空間數據共享平台](https://portal.csdi.gov.hk)
- TCSP 持牌人資料：[公司註冊處](https://www.cr.gov.hk) / [CSDI 空間數據共享平台](https://portal.csdi.gov.hk)
- 公眾假期：[1823 政府熱線](https://www.1823.gov.hk) / [資料一線通](https://data.gov.hk)

## 授權

MIT
