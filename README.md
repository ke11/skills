# opentail/skills — AI 代理技能集

繁體中文 | [English](README.en.md)

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) 及其他 AI 代理的技能集合。

## 安裝

```bash
npx skills add opentail/skills --skill weather
```

## 可用技能

### weather — 香港天氣

從[香港天文台開放數據 API](https://data.weather.gov.hk/weatherAPI/doc/HKO_Open_Data_API_Documentation.pdf) 獲取即時天氣資訊。無需 API 金鑰。

| 指令 | 獲取數據 | API | 速度 |
|------|---------|-----|------|
| `/hk-weather` | 天氣概況摘要 | 1 | 快 |
| `/hk-weather 會唔會落雨？` | 降雨狀況 + 概率 + 預報 | 3 | 中 |
| `/hk-weather stations` | 各站氣溫、濕度、雨量 | 1 | 快 |
| `/hk-weather forecast` | 9天預報 | 1 | 快 |
| `/hk-weather rainfall` | 每小時雨量 | 1 | 快 |
| `/hk-weather warning` | 生效警告 | 2 | 中 |
| `/hk-weather detail` | 各站數據 + 預報 | 2 | 中 |
| `/hk-weather all` | 所有資訊 | 6 | 慢 |

附加語言代碼切換語言：`en`（English）、`tc`（繁體中文，預設）、`sc`（簡體中文）

#### 自然語言提問

本技能支援中英文自然語言提問，無需記憶指令關鍵字：

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
| `/hk-weather will it rain?` | 降雨查詢 |
| `/hk-weather is there a typhoon?` | 颱風/警告狀況 |
| `/hk-weather how hot is it?` | 各站氣溫 |
| `/hk-weather 9-day forecast` | 9天預報 |

#### 輸出範例

```
## 香港天氣概況

**更新時間**: 2026-03-22 02:45 HKT

**概況**: 一股清勁至強風程度的偏東氣流正影響廣東沿岸。同時，一道雲帶覆蓋該區。

**預報** (本港地區今日天氣預測): 大致多雲。早上最低氣溫約21度。日間短暫時間有陽光，最高氣溫約25度。吹和緩至清勁偏東風，初時高地間中吹強風。

**展望**: 隨後數日部分時間有陽光。本週中後期日間炎熱。

_資料來源：香港天文台_
```

## 授權

MIT
