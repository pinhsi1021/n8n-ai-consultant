"""
roadmap_generator.py — n8n 導入路徑圖產生器

根據匹配到的 n8n 解決方案，產出包含：
  1. 最佳 n8n 解決方案說明
  2. n8n 工作流設計（節點圖）
  3. 困難度評分 + 評分理由
  4. 從第一步到完成的實施步驟指南
"""

import json


def _stars(n):
    """將數字轉為星號"""
    return "★" * n + "☆" * (5 - n)


def generate_roadmap(matched_solutions, industry_name, department_name=None, user_query=""):
    """
    產生 n8n 導入路徑圖。

    Parameters
    ----------
    matched_solutions : list[dict]
        matcher.match_solutions() 的回傳結果
    industry_name : str
        營業項目/產業名稱
    department_name : str, optional
        部門名稱
    user_query : str
        用戶的原始痛點描述

    Returns
    -------
    dict
        包含 solution, workflow, difficulty, difficulty_reasons, steps
    """
    if not matched_solutions:
        return _empty_roadmap(industry_name, department_name, user_query)

    # 取最佳匹配方案
    best = matched_solutions[0]
    sol = best["solution"]

    roadmap = {
        "industry": industry_name,
        "department": department_name or "全部門",
        "user_query": user_query,
        "match_score": best["similarity"],

        # ── 解決方案 ──
        "solution_name": sol["name"],
        "solution_id": sol["id"],

        # ── n8n 工作流 ──
        "workflow": sol["workflow"],

        # ── 困難度 ──
        "difficulty": sol["difficulty"],
        "difficulty_display": _stars(sol["difficulty"]),
        "difficulty_reasons": sol["difficulty_reasons"],

        # ── 實施步驟 ──
        "steps": sol["steps"],

        # ── 其他候選方案（如有）──
        "alternatives": [],
    }

    # 加入替代方案
    for alt in matched_solutions[1:]:
        alt_sol = alt["solution"]
        roadmap["alternatives"].append({
            "name": alt_sol["name"],
            "match_score": alt["similarity"],
            "difficulty": alt_sol["difficulty"],
            "difficulty_display": _stars(alt_sol["difficulty"]),
        })

    # ── 產出格式化報告 ──
    roadmap["full_report"] = _format_report(roadmap)

    return roadmap


def _empty_roadmap(industry, department, query):
    """無匹配結果時的空路徑圖"""
    return {
        "industry": industry,
        "department": department or "全部門",
        "user_query": query,
        "match_score": 0,
        "solution_name": "未找到匹配的解決方案",
        "solution_id": "none",
        "workflow": {"name": "N/A", "description": "請嘗試用更具體的痛點描述重新分析", "nodes": []},
        "difficulty": 0,
        "difficulty_display": "☆☆☆☆☆",
        "difficulty_reasons": ["無法評估——請補充更多痛點細節"],
        "steps": [{"step": 1, "title": "重新描述痛點", "desc": "請用更具體的業務場景重新描述您的痛點", "duration": "N/A"}],
        "alternatives": [],
        "full_report": "未找到匹配的解決方案，請嘗試更具體的描述。",
    }


def _format_report(roadmap):
    """格式化為可印出的文字報告"""
    lines = []
    lines.append("")
    lines.append("=" * 70)
    lines.append("         🤖 n8n AI 導入路徑圖 — Implementation Roadmap")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"  📌 營業項目：{roadmap['industry']}")
    lines.append(f"  📌 部門：{roadmap['department']}")
    lines.append(f"  📌 痛點描述：{roadmap['user_query']}")
    lines.append("")

    lines.append("-" * 70)
    lines.append(f"  🎯 推薦解決方案：{roadmap['solution_name']}")
    lines.append("-" * 70)
    wf = roadmap["workflow"]
    lines.append(f"  工作流名稱：{wf['name']}")
    lines.append(f"  說明：{wf['description']}")
    lines.append("")
    lines.append("  n8n 節點設計：")
    for i, node in enumerate(wf.get("nodes", []), 1):
        lines.append(f"    [{i}] {node['name']} ({node['type']})")
        lines.append(f"        {node['desc']}")

    lines.append("")
    lines.append("-" * 70)
    lines.append(f"  📊 困難度：{roadmap['difficulty_display']}  ({roadmap['difficulty']}/5)")
    lines.append("-" * 70)
    lines.append("  評分理由：")
    for i, reason in enumerate(roadmap["difficulty_reasons"], 1):
        lines.append(f"    {i}. {reason}")

    lines.append("")
    lines.append("-" * 70)
    lines.append("  📋 實施步驟")
    lines.append("-" * 70)
    for s in roadmap["steps"]:
        lines.append(f"    Step {s['step']}：{s['title']}（{s.get('duration', '')}）")
        lines.append(f"        {s['desc']}")
    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)
