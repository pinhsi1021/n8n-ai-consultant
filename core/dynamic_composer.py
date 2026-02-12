"""
dynamic_composer.py — 動態 n8n 工作流組合引擎

根據 pain_analyzer 的分析結果，動態組裝：
  1. n8n 工作流節點序列
  2. 困難度分數 + 客製化理由
  3. 客製化實施步驟

無需外部 API，純 Python 邏輯。
"""


# ══════════════════════════════════════════════════════════
#  n8n 節點元件庫（可組合的零件）
# ══════════════════════════════════════════════════════════

TRIGGER_NODES = {
    "排程觸發": {
        "type": "Schedule Trigger",
        "desc_tpl": "每{freq}自動執行工作流",
        "default_freq": "日",
    },
    "Webhook 觸發": {
        "type": "Webhook",
        "desc_tpl": "接收外部系統{source}的即時事件通知",
        "default_source": "",
    },
    "表單觸發": {
        "type": "n8n Form Trigger",
        "desc_tpl": "使用者填寫{form_name}表單後自動啟動",
        "default_form_name": "需求",
    },
    "Email 觸發": {
        "type": "Email Trigger (IMAP)",
        "desc_tpl": "偵測到新{email_type}郵件時自動啟動",
        "default_email_type": "",
    },
}

DATA_SOURCE_NODES = {
    "CRM": {
        "name": "讀取 CRM 資料",
        "type": "HTTP Request / CRM API",
        "desc_tpl": "從 CRM 系統取得{data_desc}",
        "default_data_desc": "客戶行為與交易紀錄",
    },
    "ERP": {
        "name": "讀取 ERP 資料",
        "type": "HTTP Request / ERP API",
        "desc_tpl": "從 ERP 系統匯入{data_desc}",
        "default_data_desc": "生產與庫存數據",
    },
    "資料庫": {
        "name": "查詢資料庫",
        "type": "Postgres / MySQL",
        "desc_tpl": "查詢資料庫取得{data_desc}",
        "default_data_desc": "相關業務數據",
    },
    "Excel/CSV": {
        "name": "讀取試算表",
        "type": "Spreadsheet File / Google Sheets",
        "desc_tpl": "讀取 Excel 或 CSV 中的{data_desc}",
        "default_data_desc": "業務數據",
    },
    "API 介接": {
        "name": "API 資料介接",
        "type": "HTTP Request",
        "desc_tpl": "透過 API 取得{data_desc}",
        "default_data_desc": "外部系統資料",
    },
    "Email": {
        "name": "讀取郵件內容",
        "type": "Email Read (IMAP)",
        "desc_tpl": "自動讀取並解析{data_desc}相關郵件",
        "default_data_desc": "",
    },
    "社群媒體": {
        "name": "抓取社群數據",
        "type": "HTTP Request / Social API",
        "desc_tpl": "取得社群平台上的{data_desc}",
        "default_data_desc": "貼文、留言或評價數據",
    },
    "IoT/感測器": {
        "name": "感測器數據接收",
        "type": "MQTT / Webhook",
        "desc_tpl": "接收 IoT 感測器的{data_desc}",
        "default_data_desc": "設備運行數據",
    },
    "POS/收銀": {
        "name": "讀取 POS 交易",
        "type": "HTTP Request / Database",
        "desc_tpl": "取得 POS 系統的{data_desc}",
        "default_data_desc": "交易與銷售紀錄",
    },
    "EHR/病歷": {
        "name": "讀取醫療紀錄",
        "type": "FHIR API / Database",
        "desc_tpl": "從醫療系統取得{data_desc}",
        "default_data_desc": "病患紀錄與診斷資料",
    },
    "LMS/教學": {
        "name": "讀取學習數據",
        "type": "HTTP Request / LMS API",
        "desc_tpl": "從教學平台取得{data_desc}",
        "default_data_desc": "學生學習進度與成績",
    },
    "表單系統": {
        "name": "接收表單資料",
        "type": "Webhook / Google Forms",
        "desc_tpl": "接收來自表單的{data_desc}",
        "default_data_desc": "使用者填寫資料",
    },
    "檔案系統": {
        "name": "讀取文件檔案",
        "type": "Read Binary File / S3",
        "desc_tpl": "讀取{data_desc}相關文件",
        "default_data_desc": "",
    },
    "網站/爬蟲": {
        "name": "網頁資料擷取",
        "type": "HTTP Request / HTML Extract",
        "desc_tpl": "從目標網站擷取{data_desc}",
        "default_data_desc": "公開資訊",
    },
}

PROCESS_NODES = {
    "預測分析": {
        "name": "AI 預測分析",
        "type": "OpenAI / Code Node",
        "desc_tpl": "基於歷史數據，對「{target}」進行趨勢預測與風險評估",
    },
    "分類判斷": {
        "name": "AI 分類與判斷",
        "type": "OpenAI / Code Node",
        "desc_tpl": "自動將「{target}」分類為不同等級或類別",
    },
    "文字分析": {
        "name": "文字語意分析",
        "type": "OpenAI / Code Node",
        "desc_tpl": "對「{target}」進行語意理解、摘要或情緒分析",
    },
    "影像辨識": {
        "name": "影像 AI 辨識",
        "type": "OpenAI Vision / Code Node",
        "desc_tpl": "對「{target}」影像進行自動辨識與標記",
    },
    "資料比對": {
        "name": "自動資料比對",
        "type": "Code Node / Merge",
        "desc_tpl": "將多筆「{target}」資料進行交叉比對，找出差異",
    },
    "統計彙總": {
        "name": "數據統計彙總",
        "type": "Code Node / Aggregate",
        "desc_tpl": "對「{target}」數據進行統計計算與趨勢彙總",
    },
    "排程優化": {
        "name": "AI 排程優化",
        "type": "OpenAI / Code Node",
        "desc_tpl": "根據「{target}」資料，產出最佳化排程建議",
    },
    "風險評估": {
        "name": "風險評分模型",
        "type": "OpenAI / Code Node",
        "desc_tpl": "對「{target}」進行多維度風險評分（高/中/低）",
    },
    "異常偵測": {
        "name": "異常偵測引擎",
        "type": "Code Node / OpenAI",
        "desc_tpl": "自動偵測「{target}」中的異常模式與偏差值",
    },
    "推薦引擎": {
        "name": "AI 推薦引擎",
        "type": "OpenAI / Code Node",
        "desc_tpl": "根據「{target}」行為數據，產出個人化推薦",
    },
}

DECISION_NODE = {
    "name": "條件分流",
    "type": "IF / Switch Node",
    "desc_tpl": "根據{criteria}結果，將資料分流至不同處理路徑",
}

OUTPUT_NODES = {
    "Email 通知": {
        "name": "Email 通知",
        "type": "Send Email / Gmail",
        "desc_tpl": "自動發送{content}通知郵件給{recipient}",
        "default_content": "分析結果",
        "default_recipient": "相關負責人",
    },
    "LINE 通知": {
        "name": "LINE 推播通知",
        "type": "HTTP Request (LINE API)",
        "desc_tpl": "透過 LINE 推播{content}給{recipient}",
        "default_content": "即時結果",
        "default_recipient": "相關人員",
    },
    "Slack 通知": {
        "name": "Slack 頻道通知",
        "type": "Slack",
        "desc_tpl": "將{content}發送到 Slack 指定頻道",
        "default_content": "分析摘要",
    },
    "即時警報": {
        "name": "即時警報推播",
        "type": "HTTP Request / Email",
        "desc_tpl": "當偵測到{trigger_condition}時，立即推播警報",
        "default_trigger_condition": "異常情況",
    },
    "自動報表": {
        "name": "自動產出報表",
        "type": "Google Sheets / Code Node",
        "desc_tpl": "將{content}自動整理成結構化報表",
        "default_content": "分析結果",
    },
    "Google Sheets": {
        "name": "寫入 Google Sheets",
        "type": "Google Sheets",
        "desc_tpl": "將{content}自動寫入 Google Sheets 追蹤表",
        "default_content": "處理結果",
    },
    "資料儲存": {
        "name": "結果存入資料庫",
        "type": "Postgres / MySQL",
        "desc_tpl": "將{content}永久儲存至資料庫",
        "default_content": "分析結果",
    },
    "自動回覆": {
        "name": "自動回覆 / Chatbot",
        "type": "HTTP Request / Webhook Response",
        "desc_tpl": "自動產生{content}回覆給{recipient}",
        "default_content": "智慧回覆",
        "default_recipient": "客戶",
    },
    "觸發流程": {
        "name": "觸發後續流程",
        "type": "Execute Workflow / Webhook",
        "desc_tpl": "自動觸發後續{action}流程",
        "default_action": "處理",
    },
    "產出文件": {
        "name": "自動產出文件",
        "type": "Code Node / PDF Generator",
        "desc_tpl": "自動產生{doc_type}文件",
        "default_doc_type": "分析報告",
    },
}

LOG_NODE = {
    "name": "執行紀錄追蹤",
    "type": "Google Sheets / Database",
    "desc_tpl": "記錄每次{action}的執行結果，方便後續追蹤與優化",
}


# ══════════════════════════════════════════════════════════
#  動態組合邏輯
# ══════════════════════════════════════════════════════════

def compose_workflow(analysis, industry="", pain_text=""):
    """
    根據痛點分析結果，動態組裝 n8n 工作流。

    Parameters
    ----------
    analysis : dict   — pain_analyzer.analyze_pain_point() 的回傳
    industry : str
    pain_text : str   — 原始痛點描述

    Returns
    -------
    dict with: name, description, nodes
    """
    keywords = analysis.get("keywords", [])
    sources = analysis.get("data_sources", [])
    actions = analysis.get("actions", [])
    outputs = analysis.get("outputs", [])
    focus = analysis.get("industry_focus", "")

    # ── 決定主題名詞（注入到模板裡）──
    target = _extract_target(keywords, pain_text, focus)

    nodes = []

    # 1. 觸發器
    trigger = _select_trigger(analysis)
    nodes.append(trigger)

    # 2. 資料源節點（最多 2 個）
    for src in sources[:2]:
        node_tpl = DATA_SOURCE_NODES.get(src)
        if node_tpl:
            desc = node_tpl["desc_tpl"].format(
                data_desc=_contextualize(node_tpl["default_data_desc"], target, focus)
            )
            nodes.append({
                "name": node_tpl["name"],
                "type": node_tpl["type"],
                "desc": desc,
            })

    # 3. 處理節點（最多 2 個）
    for act in actions[:2]:
        proc_tpl = PROCESS_NODES.get(act)
        if proc_tpl:
            nodes.append({
                "name": proc_tpl["name"],
                "type": proc_tpl["type"],
                "desc": proc_tpl["desc_tpl"].format(target=target),
            })

    # 4. 條件分流（如果有分類/判斷/風險類動作）
    needs_decision = any(a in actions for a in ["分類判斷", "風險評估", "異常偵測", "預測分析"])
    if needs_decision:
        criteria = _build_criteria(actions, target)
        nodes.append({
            "name": DECISION_NODE["name"],
            "type": DECISION_NODE["type"],
            "desc": DECISION_NODE["desc_tpl"].format(criteria=criteria),
        })

    # 5. 輸出節點（最多 2 個）
    for out in outputs[:2]:
        out_tpl = OUTPUT_NODES.get(out)
        if out_tpl:
            desc = out_tpl["desc_tpl"].format(
                content=target + "分析結果",
                recipient=out_tpl.get("default_recipient", "負責人"),
                trigger_condition=f"{target}出現異常",
                action=target + "處理",
                doc_type=target + "報告",
            )
            nodes.append({
                "name": out_tpl["name"],
                "type": out_tpl["type"],
                "desc": desc,
            })

    # 6. 日誌節點
    nodes.append({
        "name": LOG_NODE["name"],
        "type": LOG_NODE["type"],
        "desc": LOG_NODE["desc_tpl"].format(action=target + "分析"),
    })

    # ── 工作流名稱 & 描述 ──
    wf_name = _generate_wf_name(target, actions, industry)
    wf_desc = _generate_wf_desc(target, actions, outputs, industry, pain_text)

    return {
        "name": wf_name,
        "description": wf_desc,
        "nodes": nodes,
    }


def compose_difficulty(analysis, node_count):
    """
    動態計算困難度與理由。

    Returns
    -------
    tuple: (score: int, reasons: list[str])
    """
    score = 1  # 基礎分
    reasons = []

    sources = analysis.get("data_sources", [])
    actions = analysis.get("actions", [])
    complexity = analysis.get("complexity", [])

    # 資料源數量
    if len(sources) >= 2:
        score += 1
        reasons.append(f"需要整合 {len(sources)} 個資料來源（{'、'.join(sources)}），增加串接工作量")
    elif len(sources) == 1:
        reasons.append(f"資料來源為 {sources[0]}，串接難度適中")

    # 處理複雜度
    complex_actions = {"影像辨識", "預測分析", "風險評估", "推薦引擎", "排程優化"}
    hard_actions = [a for a in actions if a in complex_actions]
    if hard_actions:
        score += 1
        reasons.append(f"涉及進階 AI 能力（{'、'.join(hard_actions)}），需要調校模型參數與 Prompt")

    simple_actions = {"統計彙總", "資料比對"}
    if all(a in simple_actions for a in actions):
        reasons.append("處理邏輯以統計與比對為主，邏輯相對單純")

    # 複雜度因素
    if "即時處理" in complexity:
        score += 1
        reasons.append("需要即時處理能力，對系統延遲有較高要求")
    if "大量資料" in complexity:
        score += 1
        reasons.append("涉及大量資料處理，需考慮分頁與效能優化")
    if "多系統整合" in complexity:
        score += 1
        reasons.append("需跨多個系統整合資料，API 相容性是主要挑戰")
    if "合規/安全" in complexity:
        score += 1
        reasons.append("涉及合規或安全要求，需額外注意資料處理規範")
    if "跨部門協作" in complexity:
        score += 1
        reasons.append("需要跨部門協作推動，組織溝通成本較高")
    if "機器學習" in complexity:
        score += 1
        reasons.append("需要機器學習模型，訓練與維護成本較高")

    # 節點數量
    if node_count >= 7:
        score += 1
        reasons.append(f"工作流包含 {node_count} 個節點，流程較長，測試與除錯需要更多時間")

    # 封頂
    score = min(score, 5)

    # 如果沒有特別難的因素，補一條正面的
    if score <= 2 and len(reasons) < 3:
        reasons.append("整體而言是入門級 n8n 工作流，適合初次使用者")

    return score, reasons


def compose_steps(analysis, workflow_nodes, difficulty):
    """
    根據工作流節點和分析結果，產出客製化實施步驟。

    Returns
    -------
    list[dict]: each with step, title, desc, duration
    """
    keywords = analysis.get("keywords", [])
    sources = analysis.get("data_sources", [])
    actions = analysis.get("actions", [])
    target = _extract_target(keywords, "", analysis.get("industry_focus", ""))

    steps = []
    step_num = 1

    # Step 1: 需求確認
    steps.append({
        "step": step_num,
        "title": "需求確認與資料盤點",
        "desc": f"盤點「{target}」相關數據的來源與格式，確認可用的 {'、'.join(sources[:2]) if sources else '資料接口'}，並定義預期的自動化目標。",
        "duration": "1~2 天",
    })
    step_num += 1

    # Step 2: 資料源串接
    if sources:
        src_text = '、'.join(sources[:2])
        steps.append({
            "step": step_num,
            "title": f"串接資料來源（{src_text}）",
            "desc": f"在 n8n 中設定 {src_text} 的連線，測試資料讀取是否正確，確認欄位對應。",
            "duration": "2~3 天" if len(sources) >= 2 else "1~2 天",
        })
        step_num += 1

    # Step 3: 核心處理邏輯
    if actions:
        act_text = '、'.join(actions[:2])
        steps.append({
            "step": step_num,
            "title": f"建構核心邏輯（{act_text}）",
            "desc": f"在 n8n 中建立「{target}」的{act_text}處理節點，撰寫必要的 Prompt 或計算邏輯，並以小量測試資料驗證。",
            "duration": "3~5 天" if any(a in actions for a in ["預測分析", "影像辨識", "風險評估"]) else "2~3 天",
        })
        step_num += 1

    # Step 4: 條件與分流
    needs_decision = any(a in actions for a in ["分類判斷", "風險評估", "異常偵測", "預測分析"])
    if needs_decision:
        steps.append({
            "step": step_num,
            "title": "設定條件分流與閾值",
            "desc": f"設定 IF/Switch 節點的判斷閾值（例如：風險高/中/低），確保「{target}」分流邏輯準確。",
            "duration": "1~2 天",
        })
        step_num += 1

    # Step 5: 輸出通道
    outputs = analysis.get("outputs", [])
    if outputs:
        out_text = '、'.join(outputs[:2])
        steps.append({
            "step": step_num,
            "title": f"設定輸出通道（{out_text}）",
            "desc": f"設定{out_text}節點，確保「{target}」處理結果能正確送達通知對象。",
            "duration": "1~2 天",
        })
        step_num += 1

    # Step 6: 測試
    steps.append({
        "step": step_num,
        "title": "端到端測試與微調",
        "desc": f"用真實資料執行完整工作流，驗證從資料匯入到結果輸出的全流程，微調{target}相關參數。",
        "duration": "2~3 天",
    })
    step_num += 1

    # Step 7: 上線
    steps.append({
        "step": step_num,
        "title": "正式上線與監控",
        "desc": f"啟用排程或觸發條件，監控前 1~2 週的執行紀錄，處理邊界情況或例外。",
        "duration": "持續",
    })

    return steps


# ══════════════════════════════════════════════════════════
#  輔助函式
# ══════════════════════════════════════════════════════════

def _extract_target(keywords, pain_text, focus):
    """從關鍵字中提取最核心的主題名詞"""
    # 優先用產業焦點
    if focus:
        return focus

    # 過濾掉太通用的詞
    stop = {"我們", "公司", "系統", "問題", "希望", "可以", "因為", "目前", "常常",
            "太多", "太高", "太低", "很多", "一直", "經常", "需要", "想要", "如何",
            "怎麼", "不知道", "沒有", "無法", "進行"}
    filtered = [kw for kw in keywords if kw not in stop and len(kw) >= 2]

    return filtered[0] if filtered else "業務數據"


def _select_trigger(analysis):
    """根據分析結果選擇觸發器"""
    complexity = analysis.get("complexity", [])
    outputs = analysis.get("outputs", [])

    if "即時處理" in complexity:
        tpl = TRIGGER_NODES["Webhook 觸發"]
        return {
            "name": "Webhook 觸發",
            "type": tpl["type"],
            "desc": "接收即時事件通知，立即啟動處理流程",
        }

    if "自動回覆" in outputs:
        tpl = TRIGGER_NODES["Webhook 觸發"]
        return {
            "name": "Webhook 觸發",
            "type": tpl["type"],
            "desc": "收到客戶請求時即時啟動工作流",
        }

    # 預設排程
    return {
        "name": "排程觸發",
        "type": "Schedule Trigger",
        "desc": "每日定時自動執行工作流",
    }


def _contextualize(default_desc, target, focus):
    """根據 target 替換預設描述"""
    if not default_desc:
        return f"{target}相關資料"
    return default_desc


def _build_criteria(actions, target):
    """建立分流條件描述"""
    if "風險評估" in actions or "預測分析" in actions:
        return f"{target}風險評分"
    if "異常偵測" in actions:
        return f"{target}異常偵測"
    if "分類判斷" in actions:
        return f"{target}分類"
    return f"{target}分析"


def _generate_wf_name(target, actions, industry):
    """產出工作流名稱"""
    act_name = actions[0] if actions else "自動分析"
    prefix = f"{industry}" if industry else ""
    return f"{prefix}{target}{act_name}自動化"


def _generate_wf_desc(target, actions, outputs, industry, pain_text):
    """產出工作流描述"""
    act_parts = '與'.join(actions[:2]) if actions else "資料處理"
    out_parts = '與'.join(outputs[:2]) if outputs else "結果輸出"

    desc = f"針對「{target}」問題，自動進行 {act_parts}，"
    desc += f"並透過 {out_parts} 將結果即時傳達給相關人員。"

    return desc
