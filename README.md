# Reduce-token-usage-when-making-presentations

簡報節省 token 方法：給 Claude Code 使用的兩份指令（prompt）。

| 檔案 | 用途 |
|---|---|
| [`prompts/canva-edit.md`](prompts/canva-edit.md) | 透過 Canva MCP 修改**既有**的 Canva 簡報（不會新建設計） |
| [`prompts/pptx-create-edit.md`](prompts/pptx-create-edit.md) | 用 python-pptx 修改 pptx；沒有檔案時自動新建 |

兩份都是全自動執行、必做一次視覺檢查，並以最少 token 為目標。

## 使用方式

1. 開一個新的 Claude Code 對話。
2. 複製整份指令貼上，只修改最下面的 `<request>` 區塊（可以寫中文）。
3. 長期使用的話，把 `<request>` 以外的部分存成專案的 `CLAUDE.md`，之後每次只傳 `<request>` 即可。

## 省 token 的主要做法

- **只讀需要的資料**：只讀要修改的頁面；Canva 讀取時不帶縮圖，pptx 不解壓、不讀 XML。
- **合併操作**：Canva 每頁只呼叫一次 `edit-design`；pptx 所有修改合成一支腳本只跑一次。
- **低成本視覺檢查**：Canva 直接用 `edit-design` 回傳的縮圖；pptx 只渲染改過的頁面，拼成一張低解析度縮圖格。只檢查一次、修正一次。
- **不來回詢問**：對應不明確時自行判斷，在回報中列出「自行判斷的地方」。
- **工具重複使用**：pptx 的 `pptx_dump.py`、`pptx_preview.py` 寫一次存在 `./tools/`，之後直接重用。
- **精簡輸出**：不解說步驟、不複述需求、不貼腳本，只回報固定幾項結果。

## 前置需求

- **Canva 版**：Claude Code 已連接 Canva MCP
  ```
  claude mcp add --transport http canva https://mcp.canva.com/mcp
  ```
  之後在 Claude Code 輸入 `/mcp` 登入授權。
- **pptx 版**：Python；視覺檢查需要本機安裝 LibreOffice（沒有會跳過並在回報註明）。

## 注意

Canva 的 `edit-design` 工具說明要求存檔前取得使用者同意。指令中已寫明「預先授權」，但 Claude 仍可能停下來詢問一次，直接同意即可。
