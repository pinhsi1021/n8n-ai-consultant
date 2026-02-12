# n8n AI 導入顧問系統 (AI Consultant for n8n)

這是一個專為企業數位轉型設計的 AI 顧問工具，能透過自然語言分析業務痛點，自動生成 n8n 自動化工作流建議、實施路徑圖與成本預估。系統結合了本地規則引擎與 n8n 社群模版搜尋，提供從診斷到解決方案的完整諮詢體驗。

![Consultant Mode](https://raw.githubusercontent.com/pinhsi1021/n8n-ai-consultant/main/docs/screenshot.png) *(示意圖，請替換為實際截圖)*

## 🌟 主要功能 (Key Features)

### 1. 動態痛點分析 (Dynamic Pain Point Analysis)
- **智慧語意理解**：運用 jieba 斷詞與關鍵字權重分析，從模糊的業務描述中提取核心問題（Core Issues）。
- **多維度診斷**：自動識別數據來源（Data Sources）、必要動作（Actions）、輸出形式（Outputs）與複雜度風險（Complexity）。
- **產業專屬建議**：針對製造、零售、金融、醫療等產業提供客製化的數位轉型建議。

### 2. 智慧工作流生成 (Smart Workflow Generation)
- **本地 AI 規劃**：根據分析結果，動態組裝最適合的 n8n 節點邏輯（如 Webhook -> AI Agent -> Database）。
- **社群模版匹配**：即時搜尋 n8n 官方社群，推薦高品質的現成模版，並自動翻譯為繁體中文（支援深層語意翻譯）。
- **顧問模式 (Consultant Mode)**：一鍵切換專業視角，查看更多社群參考資源與技術細節。

### 3. 成本與時程預估 (Estimation)
- **實施路徑圖**：自動生成分階段實施步驟（POC -> Pilot -> Production）。
- **成本估算**：基於節點數量與邏輯複雜度，提供專案導入的預估成本範圍（TWD）。
- **工期預測**：依據步驟複雜度計算所需工時（週）。

## 🛠 技術架構 (Tech Stack)

- **Backend**: Python 3.8+ (標準庫 `http.server`, `urllib`, `json`)
- **NLP Engine**: `jieba` (中文斷詞與關鍵字萃取)
- **Frontend**: HTML5, CSS3 (Modern UI), Vanilla JavaScript
- **Integration**: n8n Community API

## 📋 安裝指南 (Installation Guide)

### 前置需求 (Prerequisites)
- **Python 3.8 或更高版本**：請至 [Python 官網](https://www.python.org/downloads/) 下載並安裝。
- **Git**：用於複製專案程式碼。

### 🚀 快速啟動 (Quick Start)
如果您不想手動逐一安裝，可以使用我們準備的自動化腳本：

**macOS / Linux:**
1. 下載專案後，在終端機執行：
   ```bash
   chmod +x run.sh
   ./run.sh
   ```
   腳本會自動檢查環境、建立虛擬環境、安裝依賴並開啟瀏覽器。

---

### 分步安裝指南 (Manual Installation)

### 步驟 1：下載專案
開啟終端機 (Terminal) 或命令提示字元 (Command Prompt)，執行以下指令：

```bash
git clone https://github.com/pinhsi1021/n8n-ai-consultant.git
cd n8n-ai-consultant
```

### 步驟 2：建立虛擬環境 (建議)
為避免污染全域 Python 環境，建議建立虛擬環境：

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 步驟 3：安裝依賴套件
```bash
pip install -r requirements.txt
```
*(主要依賴僅需 `jieba`，輕量快速)*

## 🚀 啟動系統 (Running the Application)

1. 確認虛擬環境已啟用 (若有建立)。
2. 執行啟動指令：
   ```bash
   python web_server.py
   ```
3. 您將看到以下訊息，代表伺服器已成功啟動：
   ```
     🤖 n8n AI 導入顧問系統 — Web Server
     🌐 http://localhost:8080
   ```
4. 打開瀏覽器，前往 **[http://localhost:8080](http://localhost:8080)** 即可開始使用。

## 📖 使用說明 (Usage)

1. **選擇背景**：在左側設定您的產業類別（如：製造業）與部門（如：生產管理）。
2. **輸入痛點**：在文字框中描述您遇到的問題（支援多行輸入，每行一個痛點）。
   - *範例：「產線設備經常無預警停機，維修人員無法即時收到通知。」*
3. **開始分析**：點擊「開始分析」按鈕。
4. **查看報告**：
   - **本地 AI 分析**：查看系統建議的節點流向、困難度評估與成本預估。
   - **顧問模式**：開啟右上角的「🔒 顧問模式」開關，解鎖下方「n8n 社群參考」分頁，查看更多相似的實戰模版。

## ⚠️ 注意事項
- 本系統為 **顧問諮詢工具**，用於規劃與建議，並非 n8n 自動化軟體本身。
- 若需執行建議的工作流，請自行安裝 [n8n](https://n8n.io/) 或使用 n8n Cloud 服務。
- 本地伺服器預設使用 Port `8080`，若被佔用請修改 `web_server.py` 中的 `PORT` 變數。

## 📞 聯絡與支援
如有任何問題或功能建議，歡迎提交 Issue 或透過 GitHub 聯繫開發者。

---
**License**: MIT
**Author**: Pinhsi
