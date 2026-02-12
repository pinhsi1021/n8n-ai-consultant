"""
roadmap_generator.py — n8n 導入路徑圖產生器（動態版 + 社群整合）

雙引擎：
  1. n8n 社群搜尋 — 從 7,888+ 社群模板找真實工作流
  2. 本地動態分析 — jieba + dynamic_composer 自訂組裝
"""

from core.pain_analyzer import analyze_pain_point
from core.pain_analyzer import analyze_pain_point
from core.dynamic_composer import compose_workflow, compose_difficulty, compose_steps, compose_cost
from core.n8n_community import search_and_enrich


def _stars(n):
    """將數字轉為星號"""
    return "★" * n + "☆" * (5 - n)


def generate_roadmap(matched_solutions, industry_name, department_name=None, user_query=""):
    """
    產生 n8n 導入路徑圖（雙引擎）。

    Returns
    -------
    dict with: local_analysis + community_results
    """
    # ── 1. 本地痛點分析 ──
    analysis = analyze_pain_point(user_query, industry_name, department_name or "")

    # ── 2. 本地動態工作流 ──
    workflow = compose_workflow(analysis, industry_name, user_query)
    difficulty, difficulty_reasons = compose_difficulty(analysis, len(workflow["nodes"]))
    steps = compose_steps(analysis, workflow["nodes"], difficulty)
    cost_estimate = compose_cost(len(workflow["nodes"]), difficulty)

    # ── 3. n8n 社群搜尋 ──
    keywords = analysis.get("keywords", [])
    community_results = []
    try:
        community_results = search_and_enrich(keywords, industry_name, max_results=5)
    except Exception as e:
        print(f"[roadmap] Community search failed: {e}")

    # ── 4. 組裝結果 ──
    roadmap = {
        "industry": industry_name,
        "department": department_name or "全部門",
        "user_query": user_query,

        # 痛點分析
        "pain_summary": analysis["pain_summary"],
        "detected_keywords": analysis["keywords"][:6],
        "detected_sources": analysis["data_sources"],
        "detected_actions": analysis["actions"],
        "detected_outputs": analysis["outputs"],
        "detected_complexity": analysis["complexity"],

        # ── 本地 AI 分析 ──
        "local": {
            "solution_name": workflow["name"],
            "workflow": workflow,
            "difficulty": difficulty,
            "difficulty_display": _stars(difficulty),
            "difficulty_reasons": difficulty_reasons,
            "steps": steps,
            "estimated_cost": cost_estimate,
            "match_score": matched_solutions[0]["similarity"] if matched_solutions else 0,
            "alternatives": [],
        },

        # ── n8n 社群方案 ──
        "community": community_results,
    }

    # TF-IDF 替代方案
    for alt in matched_solutions[:3]:
        alt_sol = alt["solution"]
        roadmap["local"]["alternatives"].append({
            "name": alt_sol["name"],
            "match_score": alt["similarity"],
            "difficulty": alt_sol["difficulty"],
            "difficulty_display": _stars(alt_sol["difficulty"]),
        })

    return roadmap
