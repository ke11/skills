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

| 技能 | 功能 | 快速範例 | 數據來源 |
|------|------|---------|---------|
| [hk-weather](skills/hk-weather/references/usage.md) | 即時天氣、預報、警告、雨量 | `/hk-weather forecast` | [香港天文台](https://data.weather.gov.hk) |
| [hk-kmb-eta](skills/hk-kmb-eta/references/usage.md) | 巴士到站時間、路線查詢 | `/hk-kmb-eta 42C 業成街` | [九巴開放數據](https://data.etabus.gov.hk) |
| [hk-aed-wait](skills/hk-aed-wait/references/usage.md) | 急症室等候時間 | `/hk-aed-wait 屯門` | [醫院管理局](https://www.ha.org.hk/opendata) |
| [hk-tcsp-licence](skills/hk-tcsp-licence/references/usage.md) | TCSP 持牌人查詢 | `/hk-tcsp-licence name 富年` | [公司註冊處 / CSDI](https://portal.csdi.gov.hk) |
| [hk-holiday](skills/hk-holiday/references/usage.md) | 公眾假期查詢 | `/hk-holiday 2026` | [1823 政府熱線](https://www.1823.gov.hk) |

點擊技能名稱查看完整用法及輸出範例。

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
