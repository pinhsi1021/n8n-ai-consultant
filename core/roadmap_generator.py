"""
roadmap_generator.py — n8n 導入路徑圖產生器（動態版）

使用 pain_analyzer + dynamic_composer 動態產出：
  1. 客製化 n8n 工作流設計
  2. 動態困難度評分 + 客製理由
  3. 根據痛點量身打造的實施步驟
"""

from core.pain_analyzer import analyze_pain_point
from core.dynamic_composer import compose_workflow, compose_difficulty, compose_steps


def _stars(n):
    """將數字轉為星號"""
    return "★" * n + "☆" * (5 - n)


def generate_roadmap(matched_solutions, industry_name, department_name=None, user_query=""):
    """
    產生 n8n 導入路徑圖。

    流程：
    1. pain_analyzer 分析痛點文字
    2. dynamic_composer 動態組裝工作流
    3. dynamic_composer 動態計算困難度
    4. dynamic_composer 動態產出實施步驟
    5. TF-IDF 匹配結果作為替代方案

    Returns
    -------
    dict
    """
    # ── 1. 分析痛點 ──
    analysis = analyze_pain_point(user_query, industry_name, department_name or "")

    # ── 2. 動態組裝工作流 ──
    workflow = compose_workflow(analysis, industry_name, user_query)

    # ── 3. 動態計算困難度 ──
    difficulty, difficulty_reasons = compose_difficulty(analysis, len(workflow["nodes"]))

    # ── 4. 動態產出步驟 ──
    steps = compose_steps(analysis, workflow["nodes"], difficulty)

    # ── 5. 組裝結果 ──
    roadmap = {
        "industry": industry_name,
        "department": department_name or "全部門",
        "user_query": user_query,
        "match_score": matched_solutions[0]["similarity"] if matched_solutions else 0,

        # 動態產出的方案
        "solution_name": workflow["name"],

        # 痛點分析摘要 ★ 新增
        "pain_summary": analysis["pain_summary"],
        "detected_keywords": analysis["keywords"][:6],
        "detected_sources": analysis["data_sources"],
        "detected_actions": analysis["actions"],
        "detected_outputs": analysis["outputs"],
        "detected_complexity": analysis["complexity"],

        # 動態工作流
        "workflow": workflow,

        # 動態困難度
        "difficulty": difficulty,
        "difficulty_display": _stars(difficulty),
        "difficulty_reasons": difficulty_reasons,

        # 動態步驟
        "steps": steps,

        # TF-IDF 匹配作為替代方案
        "alternatives": [],
    }

    # 替代方案（來自靜態庫的 TF-IDF 匹配結果）
    for alt in matched_solutions[:3]:
        alt_sol = alt["solution"]
        roadmap["alternatives"].append({
            "name": alt_sol["name"],
            "match_score": alt["similarity"],
            "difficulty": alt_sol["difficulty"],
            "difficulty_display": _stars(alt_sol["difficulty"]),
        })

    return roadmap
