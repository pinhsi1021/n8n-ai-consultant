"""
n8n_community.py — n8n 社群工作流搜尋與分析

透過 n8n 公開 API（免費，無需 API Key）：
  1. 搜尋社群工作流模板
  2. 取得工作流詳情（節點、描述）
  3. 動態評估困難度
  4. 產出實施步驟
"""

import json
import re
import ssl
import urllib.request
import urllib.parse
import urllib.error

# SSL context — macOS Python 常見需要
try:
    import certifi
    SSL_CTX = ssl.create_default_context(cafile=certifi.where())
except ImportError:
    SSL_CTX = ssl.create_default_context()
    SSL_CTX.check_hostname = False
    SSL_CTX.verify_mode = ssl.CERT_NONE

# ══════════════════════════════════════════════════════════
#  中→英 翻譯字典（業務常見關鍵字）
# ══════════════════════════════════════════════════════════

ZH_TO_EN = {
    # 資料源
    "CRM": "CRM",
    "ERP": "ERP",
    "Excel": "spreadsheet",
    "試算表": "spreadsheet",
    "資料庫": "database",
    "Email": "email",
    "郵件": "email",
    "社群媒體": "social media",
    "表單": "form",
    "網站": "website",

    # 動作
    "預測": "prediction forecast",
    "分類": "classification",
    "偵測": "detection monitoring",
    "辨識": "recognition",
    "分析": "analysis",
    "統計": "statistics analytics",
    "排程": "scheduling",
    "比對": "matching comparison",
    "推薦": "recommendation",
    "篩選": "filter screening",
    "評估": "assessment evaluation",
    "摘要": "summary",
    "翻譯": "translation",
    "轉換": "conversion transform",

    # 輸出
    "報表": "report",
    "通知": "notification alert",
    "警報": "alert warning",
    "回覆": "reply response",
    "報告": "report",

    # 產業
    "零售": "retail ecommerce",
    "製造": "manufacturing production",
    "金融": "finance banking",
    "保險": "insurance",
    "醫療": "healthcare medical",
    "教育": "education learning",
    "物流": "logistics shipping",
    "餐飲": "restaurant food",
    "電商": "ecommerce online store",
    "房地產": "real estate property",
    "行銷": "marketing",
    "人資": "HR human resources",
    "客服": "customer service support",
    "業務": "sales",

    # 常見痛點
    "客戶": "customer client",
    "流失": "churn retention",
    "訂單": "order",
    "庫存": "inventory stock",
    "品質": "quality inspection",
    "瑕疵": "defect quality",
    "排班": "shift scheduling",
    "薪資": "payroll salary",
    "發票": "invoice billing",
    "合約": "contract",
    "審核": "approval review",
    "招募": "recruitment hiring",
    "出勤": "attendance",
    "請假": "leave absence",
    "帳務": "accounting",
    "催收": "collection remind",
    "退貨": "return refund",
    "投訴": "complaint",
    "滿意度": "satisfaction survey",
    "供應鏈": "supply chain",
    "採購": "procurement purchasing",
    "報價": "quotation pricing",
    "生產": "production manufacturing",
    "設備": "equipment maintenance",
    "維修": "maintenance repair",
    "物料": "material",
    "倉儲": "warehouse storage",
    "配送": "delivery shipping",
    "排程": "scheduling planning",
    # 製造業擴充
    "產線": "production line assembly",
    "混亂": "chaos scheduling optimization",
    "刀具": "tool management CNC",
    "機台": "machine equipment CNC",
    "稼動率": "OEE utilization",
    "良率": "yield quality rate",
    "不良率": "defect rate quality",
    "停機": "downtime maintenance",
    "模具": "mold die tooling",
    "SPC": "SPC statistical process control",
    "SOP": "SOP standard operating procedure",
    "工單": "work order production",
    "派工": "dispatch assignment scheduling",
    "巡檢": "inspection patrol quality",
    "異常": "anomaly detection alert",
    "預警": "early warning alert monitoring",
    "預約": "booking appointment",
    "會員": "membership loyalty",
    "行銷": "marketing campaign",
    "廣告": "advertising",
    "SEO": "SEO",
    "社群": "social media",
    "內容": "content",
    "簽核": "approval workflow",
    "文件": "document",
    "合規": "compliance",
    "風控": "risk management",
    "信用": "credit scoring",
    "理賠": "claim processing",
    "保單": "policy insurance",
    "病患": "patient",
    "掛號": "registration appointment",
    "診斷": "diagnosis",
    "處方": "prescription",
    "學生": "student",
    "成績": "grade score",
    "課程": "course class",
    "考試": "exam test",
    "缺貨": "stockout shortage",
    "交期": "delivery time lead time",
    "自動化": "automation",
    "效率": "efficiency productivity",
    "成本": "cost reduction",
    "數據": "data",
    "AI": "AI artificial intelligence",
    "機器學習": "machine learning",
    "聊天機器人": "chatbot",
    "Slack": "Slack",
    "LINE": "LINE messaging",
    "Telegram": "Telegram",
    "Discord": "Discord",
    "Google Sheets": "Google Sheets",
    "Notion": "Notion",
    "Airtable": "Airtable",
}

# 節點類型複雜度評分
NODE_COMPLEXITY = {
    "n8n-nodes-base.openAi": 3,
    "n8n-nodes-base.httpRequest": 1,
    "@n8n/n8n-nodes-langchain": 4,
    "n8n-nodes-base.code": 2,
    "n8n-nodes-base.if": 1,
    "n8n-nodes-base.switch": 1,
    "n8n-nodes-base.merge": 1,
    "n8n-nodes-base.set": 0,
    "n8n-nodes-base.noOp": 0,
    "n8n-nodes-base.stickyNote": 0,
}

# ══════════════════════════════════════════════════════════
#  英→繁中 翻譯字典（社群工作流翻譯用）
# ══════════════════════════════════════════════════════════

EN_TO_ZH = {
    # 常見動詞/動作
    "automate": "自動化", "automated": "自動化", "automation": "自動化",
    "monitor": "監控", "monitoring": "監控",
    "track": "追蹤", "tracking": "追蹤", "tracker": "追蹤器",
    "analyze": "分析", "analysis": "分析", "analytics": "分析",
    "generate": "產生", "generator": "產生器",
    "detect": "偵測", "detection": "偵測",
    "predict": "預測", "prediction": "預測", "forecast": "預測",
    "classify": "分類", "classification": "分類",
    "schedule": "排程", "scheduling": "排程",
    "notify": "通知", "notification": "通知", "notifications": "通知",
    "alert": "警報", "alerts": "警報",
    "reminder": "提醒", "reminders": "提醒",
    "sync": "同步", "synchronize": "同步",
    "backup": "備份",
    "scrape": "爬取", "scraping": "爬取", "scraper": "爬取器",
    "extract": "擷取", "extraction": "擷取",
    "transform": "轉換", "transformation": "轉換",
    "filter": "篩選", "filtering": "篩選",
    "aggregate": "彙總", "aggregation": "彙總",
    "enrich": "增強", "enrichment": "增強",
    "validate": "驗證", "validation": "驗證",
    "send": "發送", "receive": "接收",
    "create": "建立", "update": "更新", "delete": "刪除",
    "import": "匯入", "export": "匯出",
    "collect": "收集", "collector": "收集器",
    "summarize": "摘要", "summary": "摘要",
    "translate": "翻譯", "translation": "翻譯",
    "process": "處理", "processing": "處理",
    "manage": "管理", "management": "管理", "manager": "管理器",
    "optimize": "優化", "optimization": "優化",
    # 產業領域
    "invoice": "發票", "invoices": "發票",
    "payment": "付款", "payments": "付款",
    "order": "訂單", "orders": "訂單",
    "inventory": "庫存",
    "stock": "庫存", "stocks": "股票",
    "customer": "客戶", "customers": "客戶",
    "client": "客戶", "clients": "客戶",
    "employee": "員工", "employees": "員工",
    "lead": "潛在客戶", "leads": "潛在客戶",
    "sales": "銷售",
    "marketing": "行銷",
    "finance": "財務", "financial": "財務",
    "accounting": "會計",
    "manufacturing": "製造", "production": "生產",
    "quality": "品質", "inspection": "檢驗",
    "maintenance": "維護", "repair": "維修",
    "supply chain": "供應鏈", "procurement": "採購",
    "warehouse": "倉庫", "logistics": "物流",
    "shipping": "出貨", "delivery": "配送",
    "healthcare": "醫療", "medical": "醫療", "patient": "病患",
    "retail": "零售", "ecommerce": "電商", "e-commerce": "電商",
    "education": "教育", "learning": "學習",
    "insurance": "保險",
    "real estate": "房地產", "property": "房產",
    "restaurant": "餐廳", "food": "餐飲",
    # 工具/平台
    "workflow": "工作流", "workflows": "工作流",
    "template": "模板", "templates": "模板",
    "dashboard": "儀表板",
    "report": "報表", "reports": "報表", "reporting": "報表",
    "spreadsheet": "試算表",
    "database": "資料庫",
    "chatbot": "聊天機器人",
    "assistant": "助手",
    "agent": "代理",
    "pipeline": "管線",
    "integration": "整合", "integrations": "整合",
    # AI 相關
    "ai-powered": "AI 驅動", "ai powered": "AI 驅動",
    "intelligent": "智慧",
    "smart": "智慧",
    "machine learning": "機器學習",
    "deep learning": "深度學習",
    "natural language": "自然語言",
    "sentiment": "情緒",
    "recommendation": "推薦",
    # 常見形容詞/副詞
    "automated": "自動化",
    "daily": "每日", "weekly": "每週", "monthly": "每月",
    "real-time": "即時", "realtime": "即時",
    "powerful": "強大",
    "advanced": "進階",
    "comprehensive": "全面",
    "streamline": "精簡化",
    "efficient": "高效", "efficiency": "效率",
    "simple": "簡易", "simplify": "簡化",
    "connect": "連接", "connection": "連線",
    "easy": "輕鬆", "easiest": "最簡單",
    "basic": "基礎", "advanced": "進階",
    "secure": "安全", "security": "安全性",
    "flexible": "靈活", "flexibility": "靈活性",
    "powerful": "強大", "power": "能力",
    "popular": "熱門",
    "save time": "節省時間",
    "manual work": "手動工作",
    "repetitive tasks": "重複性任務",
    "without coding": "無需寫程式",
    "no-code": "無程式碼",
    "low-code": "低程式碼",
    "drag and drop": "拖拉介面",
    "user-friendly": "使用者友善",
    "open source": "開源",
    "community": "社群",
    "workflow automation": "工作流自動化",
    "business process": "業務流程",
    "digital transformation": "數位轉型",
    "api integration": "API 整合",
    "data synching": "資料同步",
    "data processing": "資料處理",
    "error handling": "錯誤處理",
    "version control": "版本控制",
    "team collaboration": "團隊協作",
    "access control": "存取控制",
    # Pronouns & Connectors (New)
    "your": "您的",
    "my": "我的",
    "our": "我們的",
    "their": "他們的",
    "with": "使用",
    "from": "從",
    "to": "至",
    "for": "用於",
    "by": "由",
    "in": "在",
    "on": "在",
    "at": "在",
    "and": "及",
    "or": "或",
    "of": "的",
    "is": "是",
    "are": "是",
    "that": "那",
    "this": "這",
    "the": "",  # Remove articles
    "a": "",    # Remove articles
    "an": "",   # Remove articles
    # Verbs (New)
    "create": "建立", "created": "已建立", "creation": "建立",
    "update": "更新", "updated": "已更新",
    "delete": "刪除", "deleted": "已刪除",
    "send": "發送", "sent": "已發送",
    "get": "取得",
    "post": "發布",
    "sync": "同步", "synced": "已同步",
    "save": "儲存", "saved": "已儲存",
    "export": "匯出",
    "import": "匯入",
    "trigger": "觸發", "triggered": "被觸發",
    "receive": "接收", "received": "已接收",
    "watch": "監看", "watching": "監看中",
    "add": "新增", "added": "已新增",
    "remove": "移除", "removed": "已移除",
    "check": "檢查", "checked": "已檢查",
    "verify": "驗證", "verified": "已驗證",
    "submit": "提交", "submitted": "已提交",
    "process": "處理", "processed": "已處理",
    "start": "開始",
    "stop": "停止",
    "finish": "完成", "finished": "已完成",
    # Nouns (New)
    "data": "資料",
    "file": "檔案", "files": "檔案",
    "record": "記錄", "records": "記錄",
    "row": "列", "rows": "列",
    "item": "項目", "items": "項目",
    "list": "清單", "lists": "清單",
    "message": "訊息", "messages": "訊息",
    "email": "郵件", "emails": "郵件",
    "document": "文件", "documents": "文件",
    "sheet": "工作表", "sheets": "工作表",
    "base": "資料庫",
    "table": "表格", "tables": "表格",
    "form": "表單", "forms": "表單",
    "response": "回覆", "responses": "回覆",
    "api": "API", "apis": "API",
    "webhook": "Webhook", "webhooks": "Webhook",
    "key": "金鑰", "keys": "金鑰",
    "token": "Token", "tokens": "Token",
    "task": "任務", "tasks": "任務",
    "project": "專案", "projects": "專案",
    "issue": "議題", "issues": "議題",
    "ticket": "工單", "tickets": "工單",
    "contact": "聯絡人", "contacts": "聯絡人",
    "deal": "交易", "deals": "交易",
    "company": "公司", "companies": "公司",
    # Description Common Phrases
    "This workflow": "此工作流",
    "allows you to": "讓您可以",
    "helps you": "幫助您",
    "automatically": "自動地",
    "when a new": "當一個新的",
    "is created": "被建立時",
    "is updated": "被更新時",
    "is deleted": "被刪除時",
    "in your": "在您的",
    "from your": "從您的",
    "to your": "到您的",
    "send a message": "發送訊息",
    "send an email": "發送郵件",
    "create a row": "建立一列",
    "update a row": "更新一列",
    "every day": "每天",
    "every hour": "每小時",
    "every week": "每週",
    "using n8n": "使用 n8n",
    "get data from": "從...取得資料",
    "post data to": "將資料發送到...",
    "trigger": "觸發",
}

# 節點名稱翻譯
NODE_NAME_ZH = {
    "schedule trigger": "排程觸發",
    "http request": "HTTP 請求",
    "webhook": "Webhook 接收",
    "code": "自訂程式碼",
    "if": "條件判斷",
    "switch": "多路分流",
    "merge": "資料合併",
    "set": "設定數值",
    "function": "函式",
    "gmail": "Gmail 郵件",
    "slack": "Slack 通知",
    "telegram": "Telegram 訊息",
    "discord": "Discord 訊息",
    "google sheets": "Google 試算表",
    "postgres": "PostgreSQL 資料庫",
    "mysql": "MySQL 資料庫",
    "mongodb": "MongoDB 資料庫",
    "openai": "OpenAI AI 模型",
    "airtable": "Airtable 資料表",
    "notion": "Notion 頁面",
    "shopify": "Shopify 電商",
    "stripe": "Stripe 金流",
    "hubspot": "HubSpot CRM",
    "salesforce": "Salesforce CRM",
    "jira": "Jira 專案管理",
    "trello": "Trello 看板",
    "github": "GitHub 程式碼庫",
    "wait": "等待",
    "respond to webhook": "回應 Webhook",
    "split in batches": "分批處理",
    "item lists": "清單處理",
    "date & time": "日期時間",
    "crypto": "加密處理",
    "xml": "XML 處理",
    "html": "HTML 處理",
    "markdown": "Markdown 處理",
    "rss feed read": "RSS 訂閱讀取",
}


def translate_to_zh(text):
    """將英文文字翻譯成繁體中文（簡易字典翻譯）"""
    if not text:
        return text
    result = text
    # 按長度排序（先替換長片語，避免子字串被先替換）
    sorted_dict = sorted(EN_TO_ZH.items(), key=lambda x: len(x[0]), reverse=True)
    for en, zh in sorted_dict:
        # 用 case-insensitive 替換
        pattern = re.compile(re.escape(en), re.IGNORECASE)
        result = pattern.sub(zh, result)
    return result


def translate_node_name(name):
    """翻譯節點名稱"""
    lower_name = name.lower().strip()
    for en_key, zh_val in NODE_NAME_ZH.items():
        if en_key in lower_name:
            return zh_val
    # fallback: 用 EN_TO_ZH
    return translate_to_zh(name)


# ══════════════════════════════════════════════════════════
#  翻譯
# ══════════════════════════════════════════════════════════

def translate_keywords(zh_keywords, industry=""):
    """
    將中文關鍵字翻譯成英文搜尋詞。
    合併最相關的翻譯結果成一個搜尋字串。
    """
    en_parts = []
    used = set()

    # 先加產業
    if industry and industry in ZH_TO_EN:
        en_parts.append(ZH_TO_EN[industry])
        used.add(industry)

    for kw in zh_keywords:
        if kw in used:
            continue
        if kw in ZH_TO_EN:
            en_parts.append(ZH_TO_EN[kw])
            used.add(kw)
        elif len(kw) >= 2:
            # 嘗試子字串匹配
            for zh_key, en_val in ZH_TO_EN.items():
                if zh_key in kw and zh_key not in used:
                    en_parts.append(en_val)
                    used.add(zh_key)
                    break

    # 最多取 4 個片段
    search_query = " ".join(en_parts[:4])
    return search_query if search_query else "workflow automation"


# ══════════════════════════════════════════════════════════
#  n8n API 呼叫
# ══════════════════════════════════════════════════════════

API_BASE = "https://api.n8n.io/api"
TIMEOUT = 8  # 秒


def search_workflows(keywords_en, rows=6):
    """
    搜尋 n8n 社群工作流。

    Returns
    -------
    list[dict] — 每個含 id, name, totalViews, user
    """
    params = urllib.parse.urlencode({
        "search": keywords_en,
        "rows": rows,
        "page": 1,
    })
    url = f"{API_BASE}/templates/search?{params}"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "n8n-ai-consultant/1.0",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=SSL_CTX) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("workflows", [])
    except Exception as e:
        print(f"[n8n_community] Search error: {e}")
        return []


def get_workflow_detail(workflow_id):
    """
    取得單一工作流的完整詳情。

    Returns
    -------
    dict or None
    """
    url = f"{API_BASE}/workflows/{workflow_id}"

    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "n8n-ai-consultant/1.0",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=TIMEOUT, context=SSL_CTX) as resp:
            raw = json.loads(resp.read().decode("utf-8"))
            attrs = raw.get("data", {}).get("attributes", {})
            return attrs
    except Exception as e:
        print(f"[n8n_community] Detail error for {workflow_id}: {e}")
        return None


# ══════════════════════════════════════════════════════════
#  工作流分析（困難度 + 步驟）
# ══════════════════════════════════════════════════════════

def enrich_workflow(detail, wf_id=None):
    """
    從 n8n 工作流詳情中，提取節點、計算困難度、產出步驟。

    Parameters
    ----------
    detail : dict — get_workflow_detail() 的回傳
    wf_id : int or str — 工作流 ID（detail 中可能沒有 id）

    Returns
    -------
    dict with: name, description, url, nodes, difficulty, difficulty_reasons,
               difficulty_display, steps, node_count, categories
    """
    if not detail:
        return None

    name = detail.get("name", "Untitled Workflow")
    description = detail.get("description", "")
    resolved_id = wf_id or detail.get("id") or ""

    # ── 解析節點 ──
    workflow_data = detail.get("workflow", {})
    raw_nodes = workflow_data.get("nodes", [])

    nodes = []
    node_types = []
    for n in raw_nodes:
        node_type = n.get("type", "")
        # 跳過 sticky notes 和 noOp
        if "stickyNote" in node_type or "noOp" in node_type:
            continue
        node_name = n.get("name", "Unknown")
        nodes.append({
            "name": node_name,
            "type": _simplify_type(node_type),
            "desc": _guess_node_desc(node_name, node_type, n.get("parameters", {})),
        })
        node_types.append(node_type)

    node_count = len(nodes)

    # ── 計算困難度 ──
    difficulty, reasons = _calculate_difficulty(nodes, node_types, node_count, description)

    # ── 產出步驟 ──
    steps = _extract_steps(description, nodes, name)

    # ── 翻譯為繁中 ──
    name_zh = translate_to_zh(name)
    desc_zh = translate_to_zh(_clean_description(description))
    nodes_zh = []
    for n in nodes[:12]:
        nodes_zh.append({
            "name": translate_node_name(n["name"]),
            "type": n["type"],
            "desc": translate_to_zh(n["desc"]),
        })
    steps_zh = []
    for s in steps:
        steps_zh.append({
            "step": s["step"],
            "title": translate_to_zh(s["title"]),
            "desc": translate_to_zh(s["desc"]),
            "duration": s.get("duration", ""),
        })

    # ── 組裝 ──
    url = f"https://n8n.io/workflows/{resolved_id}" if resolved_id else ""
    categories = _extract_categories(detail)

    return {
        "id": resolved_id,
        "name": name_zh,
        "name_en": name,
        "description": desc_zh,
        "description_en": _clean_description(description),
        "url": url,
        "nodes": nodes_zh,
        "node_count": node_count,
        "difficulty": difficulty,
        "difficulty_display": "★" * difficulty + "☆" * (5 - difficulty),
        "difficulty_reasons": reasons,
        "steps": steps_zh,
        "categories": categories,
    }


def _simplify_type(node_type):
    """將 n8n 節點 type 簡化為可讀名稱"""
    # n8n-nodes-base.httpRequest → HTTP Request
    parts = node_type.split(".")
    raw_name = parts[-1] if len(parts) > 1 else node_type

    # CamelCase → spaced
    spaced = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', raw_name)
    return spaced.title() if spaced else node_type


def _guess_node_desc(name, node_type, params):
    """根據節點名稱和類型推測描述"""
    lower_type = node_type.lower()

    if "trigger" in lower_type or "trigger" in name.lower():
        return f"觸發條件：{name}"
    if "openai" in lower_type or "langchain" in lower_type:
        return f"AI 處理：{name}"
    if "httprequest" in lower_type:
        url = params.get("url", "")
        if url:
            domain = url.split("/")[2] if len(url.split("/")) > 2 else ""
            return f"API 呼叫：{domain or name}"
        return f"HTTP 請求：{name}"
    if "if" in lower_type or "switch" in lower_type:
        return f"條件判斷：{name}"
    if "code" in lower_type:
        return f"自訂邏輯：{name}"
    if "gmail" in lower_type or "email" in lower_type:
        return f"郵件操作：{name}"
    if "slack" in lower_type:
        return f"Slack 通知：{name}"
    if "sheets" in lower_type or "spreadsheet" in lower_type:
        return f"試算表操作：{name}"
    if "postgres" in lower_type or "mysql" in lower_type or "database" in lower_type:
        return f"資料庫操作：{name}"
    if "webhook" in lower_type:
        return f"Webhook 接收：{name}"

    return f"執行：{name}"


def _calculate_difficulty(nodes, node_types, node_count, description):
    """動態計算社群工作流的困難度"""
    score = 1
    reasons = []

    # 節點數量
    if node_count >= 15:
        score += 2
        reasons.append(f"工作流包含 {node_count} 個節點，流程複雜度高")
    elif node_count >= 8:
        score += 1
        reasons.append(f"工作流包含 {node_count} 個節點，屬於中等規模")
    else:
        reasons.append(f"工作流僅 {node_count} 個節點，結構精簡")

    # AI 節點
    ai_nodes = [t for t in node_types if "openai" in t.lower() or "langchain" in t.lower() or "ai" in t.lower()]
    if ai_nodes:
        score += 1
        reasons.append(f"包含 {len(ai_nodes)} 個 AI 節點，需要設定 AI 模型與 Prompt")

    # API 呼叫數
    http_nodes = [t for t in node_types if "httprequest" in t.lower().replace(" ", "")]
    if len(http_nodes) >= 3:
        score += 1
        reasons.append(f"需要串接 {len(http_nodes)} 個外部 API，整合複雜度較高")
    elif len(http_nodes) >= 1:
        reasons.append(f"需要串接 {len(http_nodes)} 個外部 API")

    # 條件分流
    decision_nodes = [t for t in node_types if "if" in t.lower() or "switch" in t.lower()]
    if len(decision_nodes) >= 2:
        score += 1
        reasons.append(f"包含 {len(decision_nodes)} 個條件分流，邏輯分支多")

    # 資料庫
    db_nodes = [t for t in node_types if "postgres" in t.lower() or "mysql" in t.lower() or "mongo" in t.lower()]
    if db_nodes:
        score += 1
        reasons.append("需要設定資料庫連線，需有資料庫管理經驗")

    # 認證需求（從 description 判斷）
    desc_lower = description.lower()
    if "credentials" in desc_lower or "api key" in desc_lower or "oauth" in desc_lower:
        reasons.append("需要設定外部服務的認證憑證（API Key / OAuth）")

    score = min(score, 5)

    if score <= 2 and len(reasons) < 3:
        reasons.append("整體而言適合 n8n 初學者上手")

    return score, reasons


def _extract_steps(description, nodes, name):
    """從 description 中提取 How it works 步驟，或自動產生"""
    steps = []

    # 嘗試從 description 的 "How it works" 段落提取
    how_match = re.search(r'(?:How it works|What this workflow does)[:\s]*\n(.*?)(?:\n\n|\n##|\Z)',
                          description, re.DOTALL | re.IGNORECASE)

    if how_match:
        raw = how_match.group(1)
        # 提取數字列表項
        items = re.findall(r'\d+\.\s*\*?\*?(.+?)(?:\n|$)', raw)
        for i, item in enumerate(items[:7], 1):
            clean = re.sub(r'\*\*|\*|`', '', item).strip().rstrip(".")
            if clean:
                steps.append({
                    "step": i,
                    "title": clean[:60],
                    "desc": clean,
                    "duration": "",
                })

    # 如果沒有提取到步驟，自動產生
    if len(steps) < 3:
        steps = _generate_steps(nodes, name)

    return steps


def _generate_steps(nodes, name):
    """根據節點結構自動產生實施步驟"""
    steps = [
        {
            "step": 1,
            "title": "匯入工作流模板",
            "desc": f"從 n8n 社群下載「{name}」模板，匯入你的 n8n 環境。",
            "duration": "10 分鐘",
        },
        {
            "step": 2,
            "title": "設定認證憑證",
            "desc": "為工作流中使用的外部服務（API、資料庫）設定連線憑證。",
            "duration": "30~60 分鐘",
        },
    ]

    step_num = 3

    # 根據節點類型加步驟
    has_ai = any("openai" in n.get("type", "").lower() or "ai" in n.get("type", "").lower() for n in nodes)
    has_api = any("http" in n.get("type", "").lower() for n in nodes)
    has_db = any("postgres" in n.get("type", "").lower() or "mysql" in n.get("type", "").lower() for n in nodes)

    if has_ai:
        steps.append({
            "step": step_num,
            "title": "調校 AI Prompt",
            "desc": "根據你的業務場景，調整 AI 節點的 Prompt 與輸出格式。",
            "duration": "1~2 小時",
        })
        step_num += 1

    if has_api:
        steps.append({
            "step": step_num,
            "title": "對接外部 API",
            "desc": "將 HTTP Request 節點的 URL 與參數替換為你的實際 API 端點。",
            "duration": "1~3 小時",
        })
        step_num += 1

    if has_db:
        steps.append({
            "step": step_num,
            "title": "設定資料庫連線",
            "desc": "設定 Postgres/MySQL 節點的連線資訊，確認查詢語句正確。",
            "duration": "1~2 小時",
        })
        step_num += 1

    steps.append({
        "step": step_num,
        "title": "測試與微調",
        "desc": "用測試資料執行工作流，確認每個節點的輸出正確。",
        "duration": "2~4 小時",
    })
    step_num += 1

    steps.append({
        "step": step_num,
        "title": "正式啟用",
        "desc": "啟用排程或觸發條件，開始自動執行。監控前幾天的執行紀錄。",
        "duration": "持續",
    })

    return steps


def _clean_description(desc):
    """清理 markdown 描述，取前 200 字"""
    if not desc:
        return ""
    # 移除 markdown 標記
    clean = re.sub(r'#+\s*', '', desc)
    clean = re.sub(r'\*\*|\*|`|!\[.*?\]\(.*?\)|\[|\]|\(.*?\)', '', clean)
    clean = re.sub(r'\n{2,}', '\n', clean).strip()
    # 取前 200 字
    if len(clean) > 200:
        clean = clean[:200].rsplit(" ", 1)[0] + "..."
    return clean


def _extract_categories(detail):
    """提取分類標籤"""
    categories = []
    cats = detail.get("categories", [])
    if isinstance(cats, list):
        for c in cats:
            if isinstance(c, dict):
                categories.append(c.get("name", ""))
            elif isinstance(c, str):
                categories.append(c)
    return [c for c in categories if c][:5]


# ══════════════════════════════════════════════════════════
#  主入口
# ══════════════════════════════════════════════════════════

def search_and_enrich(zh_keywords, industry="", max_results=5):
    """
    完整搜尋流程：多輪翻譯搜尋 → 合併去重 → 取詳情 → 評估困難度。
    確保至少返回 3 個結果（如果有的話）。

    Returns
    -------
    list[dict] — 每個已包含 nodes, difficulty, steps 等完整資訊
    """
    seen_ids = set()
    all_raw = []

    def _collect(query, label, rows=8):
        """搜尋並收集結果，去重"""
        print(f"[n8n_community] {label}: {query}")
        results = search_workflows(query, rows=rows)
        for wf in results:
            wf_id = wf.get("id")
            if wf_id and wf_id not in seen_ids:
                seen_ids.add(wf_id)
                all_raw.append(wf)

    # ── 第1輪：完整翻譯搜尋 ──
    en_query = translate_keywords(zh_keywords, industry)
    _collect(en_query, "Search-1 full")

    # ── 第2輪：產業 + 核心動作 ──
    if len(all_raw) < max_results and len(zh_keywords) >= 2:
        en_query2 = translate_keywords(zh_keywords[:2], industry)
        _collect(en_query2, "Search-2 industry+action")

    # ── 第3輪：只用產業 + automation ──
    if len(all_raw) < 3 and industry:
        industry_en = ZH_TO_EN.get(industry, industry)
        _collect(f"{industry_en} workflow automation", "Search-3 industry+auto")

    # ── 第4輪：更寬泛的搜尋 ──
    if len(all_raw) < 3:
        for kw in zh_keywords[:3]:
            if kw in ZH_TO_EN:
                _collect(ZH_TO_EN[kw], f"Search-4 fallback '{kw}'")
            if len(all_raw) >= max_results:
                break

    # 按瀏覽數排序（優先推薦高品質模板）
    all_raw.sort(key=lambda w: w.get("totalViews", 0), reverse=True)

    results = []
    for wf in all_raw[:max_results]:
        wf_id = wf.get("id")
        if not wf_id:
            continue

        detail = get_workflow_detail(wf_id)
        if not detail:
            continue

        enriched = enrich_workflow(detail, wf_id=wf_id)
        if enriched:
            enriched["views"] = wf.get("totalViews", 0)
            enriched["creator"] = wf.get("user", {}).get("username", "")
            results.append(enriched)

    return results
