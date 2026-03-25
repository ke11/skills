# hk-tcsp-licence — TCSP 持牌人查詢

從空間數據共享平台 (CSDI) 查詢香港信託或公司服務持牌人資料，數據來自公司註冊處。

## 用法

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

## 輸出範例

```
## TCSP 持牌人查詢結果

在名稱中找到 1 筆「富年」的記錄。

| 牌照號碼 | 英文名稱 | 中文名稱 | 營業地址 |
|----------|---------|---------|---------|
| TC000002 | FULLYEAR CONSULTANTS LIMITED | 富年顧問有限公司 | UNIT B, 12/F, ... |

資料來源：公司註冊處 / 空間數據共享平台 CSDI
```
