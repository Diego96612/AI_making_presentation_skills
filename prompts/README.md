# 省 token 的簡報指令

給 Claude Code 使用的一份全域設定和兩份簡報指令（prompt），讓 AI 用最少的 token 製作或修改簡報。

| 檔案 | 用途 |
|---|---|
| [`CLAUDE.md`](CLAUDE.md) | 使用者層級的全域設定，適用所有專案：環境、工具鏈、回答偏好，以及 pptx、docx、pdf、xlsx 的省 token 規則 |
| [`canva-edit.md`](canva-edit.md) | 透過 Canva MCP 修改**現有**的 Canva 簡報，不會自行建立新設計 |
| [`pptx-create-edit.md`](pptx-create-edit.md) | 用 python-pptx 修改 pptx 檔；沒有檔案時會自動建立新的 |

兩份簡報指令都是全自動執行，並且一定會做一次視覺檢查。

## 使用方式

1. 把 [`CLAUDE.md`](CLAUDE.md) 放到 `C:\Users\<使用者名稱>\.claude\CLAUDE.md`（macOS / Linux 為 `~/.claude/CLAUDE.md`），並把「環境設定」改成自己的電腦規格。
2. 開一個新的 Claude Code 對話。
3. 複製整份簡報指令貼上，只修改最下面的 `<request>` 區塊，內容可以寫中文。
4. 常用的話，把 `<request>` 以外的部分存成專案的 `CLAUDE.md`，之後每次只要傳 `<request>` 那段就好。

## 全域 CLAUDE.md 與簡報指令的關係

簡報指令已經配合全域 `CLAUDE.md` 調整，兩者可以同時使用：

| 項目 | 全域 CLAUDE.md | 簡報指令 |
|---|---|---|
| 開始修改 | 未收到開始指令前不動檔案 | 貼上指令本身就是開始指令，不會再停下來確認 |
| Python | 禁用 pip，用 `uv run --with` | pptx 版改用 `uv run --with python-pptx --with pillow` |
| 圖片檢查 | 預設不轉圖片檢查 | 簡報指令明確要求一次視覺檢查，以指令為準 |
| 失敗處理 | 只重試一次 | 相同 |
| 回報格式 | 三行：檔案路徑、改了什麼、驗證結果 | 相同，必要時多列「自行判斷」和「失敗項目」 |
| README.md | 修改專案後自動更新 | pptx 版註明簡報不是程式專案，不建立 README |

> 指令本身用英文撰寫，因為工具名稱和說明都是英文，AI 比較不容易對應錯；同樣的內容，英文也比中文少用一些 token。

## 省 token 的做法

| 做法 | Canva 版 | pptx 版 |
|---|---|---|
| 只讀需要的資料 | 只讀要修改的頁面，讀取時不帶縮圖 | 只讀要修改的頁面，不解壓縮、不讀 XML |
| 合併操作 | 每頁只呼叫一次 `edit-design` | 所有修改合成一支腳本，只執行一次 |
| 低成本視覺檢查 | 直接使用 `edit-design` 回傳的縮圖 | 只渲染改過的頁面，拼成一張低解析度縮圖格 |
| 檢查次數 | 只檢查一次、修正一次 | 只檢查一次、修正一次 |
| 不來回詢問 | 對應不明確時自行判斷，在回報中列出 | 同左 |
| 工具重複使用 | — | `pptx_dump.py`、`pptx_preview.py` 寫一次存在 `./tools/`，之後直接重用 |
| 精簡輸出 | 不解說步驟、不複述需求，只回報固定幾項結果 | 同左，也不在對話中貼出腳本 |

讀取縮圖、圖片和 pptx 的原始 XML 是最耗 token 的部分，所以兩份指令都盡量避開。

## 前置需求

- **Canva 版**：Claude Code 已連接 Canva MCP。
  ```
  claude mcp add --transport http canva https://mcp.canva.com/mcp
  ```
  接著在 Claude Code 輸入 `/mcp` 登入授權。
- **pptx 版**：需要 Python 和 [uv](https://docs.astral.sh/uv/)（Windows 可用 `winget install astral-sh.uv`）。視覺檢查需要本機安裝 LibreOffice，沒有安裝的話會跳過，並在回報中註明。

## 注意事項

- **【待補】**：兩份指令都規定 AI 不可自行編造內容。你沒有提供的文字，會在對應位置標上【待補】，方便你一眼看出哪裡要自己填。如果希望 AI 自行補上內容，刪掉 `<constraints>` 裡的那一行即可。
- **Canva 存檔確認**：Canva 的 `edit-design` 工具規定存檔前要取得使用者同意。指令中已寫明「預先授權」，但 Claude 仍可能停下來詢問一次，直接同意即可。
