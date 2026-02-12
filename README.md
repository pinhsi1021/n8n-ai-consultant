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

## � 極速啟動 (One-Line Start)

**複製以下指令，貼上並按下 Enter，即可自動安裝並啟動系統：**

```bash
git clone https://github.com/pinhsi1021/n8n-ai-consultant.git && cd n8n-ai-consultant && chmod +x run.sh && ./run.sh
```

*(系統會自動檢查環境、安裝必要套件並開啟瀏覽器)*

---

<details>
<summary><strong>👇 點擊展開：手動安裝說明 (Manual Installation)</strong></summary>

### 前置需求
- **Python 3.8+** (Mac 通常內建，Windows 需安裝)
- **Git**

### 步驟
1. 下載專案：
   ```bash
   git clone https://github.com/pinhsi1021/n8n-ai-consultant.git
   cd n8n-ai-consultant
   ```
2. 建立環境與安裝：
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. 啟動：
   ```bash
   python web_server.py
   ```
</details>

## 📖 使用說明 (Usage)

1. **選擇背景**：在左側設定您的產業類別（如：製造業）與部門（如：生產管理）。
2. **輸入痛點**：在文字框中描述您遇到的問題。
3. **開分析**：點擊按鈕，查看本地 AI 建議與成本預估。
4. **顧問模式**：開啟右上角開關，獲取 n8n 社群模版推薦。

## ⚠️ 常見問題
- **一定要安裝 Python 嗎？**  
  是的，本系統後端核心使用 Python 運行。Mac/Linux 通常已內建，Windows 用戶需先安裝一次。
- **需要安裝 Node.js 嗎？**  
  **不需要**。本顧問工具完全獨立運行。

## 📞 聯絡與支援
如有任何問題，歡迎提交 Issue 或透過 GitHub 聯繫開發者。

---
**License**: MIT
**Author**: Pinhsi
