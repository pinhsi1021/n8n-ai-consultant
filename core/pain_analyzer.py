"""
pain_analyzer.py — 痛點文字分析器

使用 jieba 中文斷詞 + 關鍵字字典，從使用者痛點描述中萃取：
  1. data_sources  — 偵測到的資料來源（CRM、ERP、Excel…）
  2. actions        — 想要的處理動作（預測、分類、偵測、分析…）
  3. outputs        — 期望的輸出（通知、報表、預警、自動化…）
  4. complexity     — 複雜度訊號（跨部門、即時、大量…）
  5. keywords       — jieba 萃取的核心名詞/動詞
  6. industry_hints — 產業相關提示
"""

import jieba
import jieba.analyse
import re

# ── 關鍵字字典 ──

DATA_SOURCE_MAP = {
    "CRM":       ["crm", "客戶關係", "客戶管理", "客戶資料", "會員資料", "客戶系統"],
    "ERP":       ["erp", "企業資源", "進銷存", "庫存系統"],
    "資料庫":    ["資料庫", "database", "db", "sql", "數據庫"],
    "Excel/CSV": ["excel", "csv", "試算表", "報表", "表格", "spreadsheet"],
    "API 介接":  ["api", "介接", "串接", "第三方", "外部系統", "webhook"],
    "Email":     ["email", "郵件", "信箱", "mail", "電子郵件"],
    "網站/爬蟲": ["網站", "爬蟲", "網頁", "crawler", "scraping"],
    "社群媒體":  ["facebook", "fb", "ig", "instagram", "line", "社群", "粉專", "貼文"],
    "IoT/感測器":["iot", "感測器", "sensor", "溫度", "濕度", "壓力", "振動", "電壓", "電流", "轉速"],
    "表單系統":  ["表單", "google form", "問卷", "typeform", "申請單", "簽核"],
    "檔案系統":  ["檔案", "文件", "pdf", "圖片", "照片", "影像", "掃描", "合約"],
    "POS/收銀":  ["pos", "收銀", "結帳", "交易紀錄"],
    "EHR/病歷":  ["病歷", "ehr", "醫療紀錄", "看診", "掛號"],
    "LMS/教學":  ["lms", "學習", "教學平台", "課程", "學生"],
}

ACTION_MAP = {
    "預測分析":   ["預測", "predict", "forecast", "趨勢", "未來", "預估", "銷量"],
    "分類判斷":   ["分類", "判斷", "辨識", "識別", "歸類", "標記", "偵測", "classify"],
    "文字分析":   ["摘要", "語意", "情緒", "sentiment", "nlp", "文字", "分詞", "翻譯"],
    "影像辨識":   ["影像", "圖片", "視覺", "照片", "拍照", "外觀", "瑕疵", "缺陷", "vision"],
    "資料比對":   ["比對", "核對", "匹配", "對帳", "驗證", "檢查", "稽核"],
    "統計彙總":   ["統計", "彙總", "加總", "平均", "計算", "彙整", "aggregate", "分析"],
    "排程優化":   ["排程", "排班", "調度", "時程", "排序", "優化", "最佳化"],
    "風險評估":   ["風險", "評估", "評分", "scoring", "信用", "風控", "審核"],
    "異常偵測":   ["異常", "異常值", "outlier", "偏差", "波動", "不正常", "不良"],
    "推薦引擎":   ["推薦", "推薦系統", "建議", "個人化", "精準行銷"],
}

OUTPUT_MAP = {
    "Email 通知":     ["email通知", "寄信", "發送郵件", "mail", "通知信"],
    "LINE 通知":      ["line通知", "line bot", "line推播", "line"],
    "Slack 通知":     ["slack", "頻道通知"],
    "即時警報":       ["警報", "告警", "預警", "提醒", "alert", "通知", "推播"],
    "自動報表":       ["報表", "報告", "dashboard", "儀表板", "日報", "週報", "月報"],
    "Google Sheets":  ["google sheets", "google試算表", "雲端表格", "sheets"],
    "資料儲存":       ["儲存", "記錄", "歸檔", "存檔", "備份", "log", "資料庫"],
    "自動回覆":       ["自動回覆", "自動回覆", "chatbot", "機器人", "客服"],
    "觸發流程":       ["觸發", "啟動", "自動執行", "自動化", "workflow"],
    "產出文件":       ["產出", "生成", "產生", "文件", "合約", "報價單", "發票"],
}

COMPLEXITY_MAP = {
    "跨部門協作":    ["跨部門", "多部門", "協作", "各部門", "全公司"],
    "即時處理":      ["即時", "real-time", "即時性", "馬上", "立即", "秒級"],
    "大量資料":      ["大量", "海量", "百萬", "千筆", "萬筆", "十萬", "巨量", "big data"],
    "多系統整合":    ["多系統", "多平台", "整合", "串接", "異質系統", "api"],
    "合規/安全":     ["合規", "法規", "gdpr", "個資", "安全", "加密", "隱私"],
    "機器學習":      ["機器學習", "ml", "模型", "訓練", "深度學習", "ai"],
    "高精度要求":    ["精準", "精確", "準確率", "誤差", "品質標準"],
}

# ── 產業痛點常見模式 ──

INDUSTRY_PATTERNS = {
    "製造": {
        "品質": ["品質", "不良率", "瑕疵", "良率", "品管", "品檢", "defect"],
        "產能": ["產能", "產量", "效率", "稼動率", "OEE", "停機", "productiv"],
        "供應鏈": ["供應鏈", "原物料", "缺料", "庫存", "供應商", "採購", "交期"],
        "設備": ["設備", "機台", "維修", "保養", "故障", "維護", "preventive"],
        "人力": ["人力", "人員", "加班", "排班", "離職", "招募", "人事"],
    },
    "零售": {
        "客戶": ["客戶", "會員", "流失", "忠誠度", "留客", "回購"],
        "庫存": ["庫存", "缺貨", "滯銷", "存貨", "倉儲"],
        "銷售": ["銷售", "業績", "營收", "訂單", "促銷", "折扣"],
        "行銷": ["行銷", "廣告", "活動", "轉換率", "精準行銷"],
    },
    "金融": {
        "風控": ["風險", "風控", "信用", "審核", "違約", "徵信"],
        "客戶": ["客戶", "開戶", "KYC", "身分", "驗證"],
        "合規": ["合規", "法規", "洗錢", "AML", "申報"],
    },
    "醫療": {
        "看診": ["看診", "問診", "病患", "病歷", "診斷"],
        "排班": ["排班", "值班", "門診", "掛號", "預約"],
        "藥品": ["藥品", "用藥", "處方", "庫存", "藥物"],
    },
    "餐飲": {
        "訂單": ["訂單", "點餐", "出餐", "外送", "外帶"],
        "食材": ["食材", "進貨", "備料", "保鮮", "過期"],
        "人力": ["人力", "排班", "尖峰", "人手不足"],
    },
}


def analyze_pain_point(pain_text, industry="", department=""):
    """
    分析使用者痛點文字，回傳結構化分析結果。

    Returns
    -------
    dict with keys:
        keywords: list[str]       — 核心關鍵字
        data_sources: list[str]   — 偵測到的資料來源
        actions: list[str]        — 偵測到的動作需求
        outputs: list[str]        — 偵測到的輸出需求
        complexity: list[str]     — 偵測到的複雜度因素
        industry_focus: str       — 產業焦點主題
        pain_summary: str         — 痛點分析摘要
    """
    text = f"{pain_text} {industry} {department}".lower()

    # ── 1. jieba 關鍵字萃取 ──
    keywords = jieba.analyse.extract_tags(pain_text, topK=10, withWeight=False)

    # ── 2. 多維度偵測 ──
    data_sources = _detect(text, DATA_SOURCE_MAP)
    actions = _detect(text, ACTION_MAP)
    outputs = _detect(text, OUTPUT_MAP)
    complexity = _detect(text, COMPLEXITY_MAP)

    # ── 3. 產業焦點偵測 ──
    industry_focus = _detect_industry_focus(text, industry)

    # ── 4. 智慧補全（如果偵測不足）──
    if not data_sources:
        data_sources = _infer_data_sources(keywords, industry)
    if not actions:
        actions = _infer_actions(keywords)
    if not outputs:
        outputs = ["即時警報", "自動報表"]

    # ── 5. 產出摘要 ──
    pain_summary = _build_summary(
        keywords, data_sources, actions, outputs, complexity, industry, industry_focus
    )

    return {
        "keywords": keywords,
        "data_sources": data_sources,
        "actions": actions,
        "outputs": outputs,
        "complexity": complexity,
        "industry_focus": industry_focus,
        "pain_summary": pain_summary,
    }


def _detect(text, category_map):
    """比對關鍵字字典，回傳符合的類別列表"""
    found = []
    for category, keywords in category_map.items():
        for kw in keywords:
            if kw in text:
                if category not in found:
                    found.append(category)
                break
    return found


def _detect_industry_focus(text, industry):
    """偵測產業特定焦點"""
    patterns = INDUSTRY_PATTERNS.get(industry, {})
    best_focus = ""
    best_count = 0
    for focus, keywords in patterns.items():
        count = sum(1 for kw in keywords if kw in text)
        if count > best_count:
            best_count = count
            best_focus = focus
    return best_focus


def _infer_data_sources(keywords, industry):
    """根據關鍵字和產業推斷資料來源"""
    sources = []
    industry_defaults = {
        "製造": ["ERP", "資料庫"],
        "零售": ["POS/收銀", "CRM"],
        "金融": ["資料庫", "API 介接"],
        "醫療": ["EHR/病歷", "資料庫"],
        "餐飲": ["POS/收銀", "表單系統"],
        "電商": ["API 介接", "資料庫"],
        "物流": ["API 介接", "資料庫"],
        "教育": ["LMS/教學", "表單系統"],
    }
    sources = industry_defaults.get(industry, ["Excel/CSV", "資料庫"])
    return sources


def _infer_actions(keywords):
    """根據關鍵字推斷需要的動作"""
    action_hints = {
        "預測分析": ["流失", "預測", "趨勢", "需求", "銷量"],
        "異常偵測": ["異常", "不良", "瑕疵", "故障", "偏差", "波動"],
        "分類判斷": ["分類", "判斷", "辨識", "篩選"],
        "統計彙總": ["統計", "報表", "彙總", "分析"],
    }
    found = []
    for action, hints in action_hints.items():
        for h in hints:
            if any(h in kw for kw in keywords):
                if action not in found:
                    found.append(action)
                break
    return found or ["統計彙總"]


def _build_summary(keywords, sources, actions, outputs, complexity, industry, focus):
    """產出動態痛點分析摘要（根據偵測結果組合不同句型）"""
    parts = []

    # 開場：產業 + 焦點
    if industry and focus:
        parts.append(f"針對「{industry}」產業的「{focus}」問題進行深度分析")
    elif industry:
        parts.append(f"針對「{industry}」產業的業務痛點進行分析")
    else:
        parts.append("針對您描述的業務痛點進行分析")

    # 關鍵字洞察
    if keywords:
        parts.append(f"。核心關鍵字為「{'、'.join(keywords[:5])}」")

    # 動作需求（動態句型）
    if actions:
        action_str = '、'.join(actions)
        if len(actions) >= 3:
            parts.append(f"。系統偵測到多維度的維度需求：{action_str}，建議分階段實施")
        else:
            parts.append(f"。系統偵測到主要處理能力需求：{action_str}")

    # 資料來源
    if sources:
        parts.append(f"。資料將從 {'、'.join(sources)} 取得")

    # 輸出方式
    if outputs:
        parts.append(f"，結果透過 {'、'.join(outputs)} 輸出")

    # 複雜度警示
    if complexity:
        if len(complexity) >= 2:
            parts.append(f"。⚠️ 注意複雜度因素：{'、'.join(complexity)}，建議由資深工程師協助實施")
        else:
            parts.append(f"。注意複雜度因素：{'、'.join(complexity)}")

    # 產業專屬建議
    industry_advice = {
        ("製造", "品質"): "。💡 建議導入自動化履歷追蹤，結合即時監控儀表板管理品質指標",
        ("製造", "產能"): "。💡 建議導入排程優化模組，搭配每日產能自動報表",
        ("製造", "供應鏈"): "。💡 建議整合 ERP 庫存預警與供應商交期管理，降低缺料風險",
        ("製造", "設備"): "。💡 建議建立設備維護履歷系統，自動觸發保養提醒",
        ("零售", "客戶"): "。💡 建議建立 RFM 客戶分群模型，搭配再行銷自動化提升回購率",
        ("零售", "庫存"): "。💡 建議導入需求預測模型，搭配自動補貨觸發機制",
        ("零售", "銷售"): "。💡 建議建立銷售漏斗分析看板，結合促銷效果追蹤",
        ("金融", "風控"): "。💡 建議導入即時交易監控與異常評分機制，搭配人工覆審流程",
        ("金融", "客戶"): "。💡 建議建立 eKYC 自動化驗證流程，提升開戶效率",
        ("金融", "合規"): "。💡 建議導入自動合規報告生成與 AML 交易篩選",
        ("醫療", "看診"): "。💡 建議導入智慧問診輔助系統，結合病歷自動摘要",
        ("醫療", "排班"): "。💡 建議導入 AI 排班最佳化，考量人力需求與法規限制",
        ("餐飲", "訂單"): "。💡 建議導入智慧出餐排序系統，結合外送平台 API 整合",
        ("餐飲", "食材"): "。💡 建議導入食材用量預測，搭配供應商自動下單",
    }
    advice_key = (industry, focus)
    if advice_key in industry_advice:
        parts.append(industry_advice[advice_key])

    return "".join(parts) + "。"

