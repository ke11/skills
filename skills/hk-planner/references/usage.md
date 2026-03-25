# hk-planner — 活動行程規劃

整合 Google Calendar、公眾假期及天氣預報，推薦最佳活動日期。

## 用法

```
/hk-planner [活動] [日期範圍] [calendar:日曆名稱] [en|tc|sc]
```

| 指令 | 說明 |
|------|------|
| `/hk-planner 行山 下週` | 下週適合行山的日子 |
| `/hk-planner BBQ this weekend calendar:demo` | 用 demo 日曆查週末 BBQ |
| `/hk-planner hiking next month` | 下月行山推薦 |
| `/hk-planner 沙灘 4月` | 4月去沙灘的最佳日子 |

- **活動** — 戶外（行山、沙灘、BBQ）或室內（博物館、購物）
- **日期範圍** — 具體日期、「下週」、「下個月」等，預設為未來 14 天
- **日曆** — `calendar:名稱` 指定日曆，省略則用主日曆
- **語言** — `tc` 繁體中文（預設）、`en` English、`sc` 簡體中文

## 依賴

| 依賴 | 用途 | 安裝 |
|------|------|------|
| `gws` CLI | Google Calendar 查詢 | `npm install -g @googleworkspace/cli` |
| `hk-holiday` | 公眾假期資料 | `npx skills add ke11/skills --skill hk-holiday` |
| `hk-weather` | 天氣預報 | `npx skills add ke11/skills --skill hk-weather` |

## 輸出範例

```
## 活動計劃

📅 日曆: demo · 🎯 活動: 行山

| 日期 | 星期 | 假期 | 天氣 | 上午 | 下午 | 晚上 | 推薦時段 |
|------|------|------|------|:----:|:----:|:----:|----------|
| 3/29 | 日 | — | ⛅ 22-27°C | ✅ | ✅ | ✅ | 🌙 6pm-9pm |
| 3/30 | 一 | — | ⛅ 23-29°C | ✅ | ❌ BBQ | ✅ | 🌅 早晨或 🌙 6pm+ |
| 4/03 | 五 | 🔴 耶穌受難節 | ⛅ 23-28°C | ❌ 游泳 | ✅ | ✅ | 🌙 6pm-9pm |
| 4/04 | 六 | 🔴 復活節 | ☀️ 晴朗 | ❌ 登山 | ❌ 登山 | ✅ | ⭐⭐ 6pm-9pm |
| 4/05 | 日 | — | 🌧️ 未知 | ✅ | ✅ | ✅ | 任意時段 |

### 備註
- ⭐⭐ 最佳（假期 + 好天 + 有空）· ⭐ 推薦 · 🌙 晚間可行
- 天氣預報僅涵蓋未來 9 天
```

## 架構

本技能為編排技能（orchestrator），整合多個數據來源：

```
┌─────────────────────────────┐
│        hk-planner           │  ← 編排層
├──────┬──────────┬───────────┤
│  📅  │    🔴    │    🌤️    │
│ gws  │hk-holiday│hk-weather │  ← 數據層
│ CLI  │  script  │  script   │
└──────┴──────────┴───────────┘
```

詳細流程圖見 [flowchart.md](flowchart.md)。
