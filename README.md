# ChatGPT_TWS

工具可以自動從資料夾中的 `.pptx` 檔案擷取專案名稱與 SCHEDULE TABLE 的日期，並把整理後的資訊同步到線上 Excel。程式會同時維護一份版本紀錄檔，方便掌握每個專案更新的版本。

## 安裝環境

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest  # 執行測試時需要
```

## 使用方式

執行 CLI 時需要提供 PPTX 資料夾路徑，以及目標 Excel（Microsoft Graph）相關資訊。Graph Access Token 可以透過 `--token` 參數提供，也可以預先設定在環境變數 `GRAPH_API_TOKEN`。

```bash
python -m pptx_schedule \
  --pptx-dir ./presentations \
  --drive-id <DRIVE_ID> \
  --item-id <ITEM_ID> \
  --worksheet Sheet1 \
  --table ProjectSchedule \
  --version-store ./pptx_versions.json \
  --clear-before-update
```

常用參數說明：

- `--recursive`：遞迴搜尋子資料夾內的 PPTX 檔案。
- `--dry-run`：僅顯示將寫入 Excel 的內容，不會真的更新 Excel 或版本檔。
- `--project-name-pattern` / `--project-name-keyword`：客製化專案名稱的擷取規則。
- `--schedule-keyword`：指定判斷 SCHEDULE TABLE 的關鍵字。
- `--dayfirst`：遇到模糊日期格式（例如 `10/11/2024`）時採用「日/月/年」解析。

執行後會產生（或更新） `pptx_versions.json`，記錄每個專案最新的版本號與時間戳記。

## 測試

```bash
pytest
```
