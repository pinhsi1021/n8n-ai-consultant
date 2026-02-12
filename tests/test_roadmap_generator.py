"""
tests/test_roadmap_generator.py — 路徑圖產生器測試
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.matcher import match_tools
from core.industry_adapter import compute_dimension_weights, get_industry_context_text
from core.roadmap_generator import generate_roadmap


def test_full_pipeline_retail():
    """測試完整流程 — 零售業客戶流失"""
    industry = "零售"
    department = "行銷"
    pain_point = "客戶流失率太高，希望能預測哪些客戶會離開"

    dim_weights = compute_dimension_weights(industry, department)
    context = get_industry_context_text(industry, department)
    enhanced_query = f"{pain_point} {context}"

    matched = match_tools(enhanced_query, dimension_weights=dim_weights, top_n=5)
    roadmap = generate_roadmap(matched, industry, department, pain_point)

    # 結構驗證
    assert "top3_tools" in roadmap
    assert len(roadmap["top3_tools"]) == 3
    assert "difficulty" in roadmap
    assert 1 <= roadmap["difficulty"] <= 5
    assert "workflow_draft" in roadmap
    assert "full_report" in roadmap
    assert "nodes" in roadmap["workflow_draft"]

    # 內容驗證
    for tool in roadmap["top3_tools"]:
        assert "name" in tool
        assert "rank" in tool
        assert "similarity_score" in tool
        assert "reason" in tool
        assert "difficulty_display" in tool

    print("✅ test_full_pipeline_retail passed")
    print(f"   Top3: {[t['name'] for t in roadmap['top3_tools']]}")
    print(f"   Difficulty: {roadmap['difficulty_display']}")


def test_full_pipeline_manufacturing():
    """測試完整流程 — 製造業品質檢測"""
    industry = "製造"
    department = "品質管控"
    pain_point = "瑕疵檢測目前靠人工目視，效率低且容易漏檢"

    dim_weights = compute_dimension_weights(industry, department)
    context = get_industry_context_text(industry, department)
    enhanced_query = f"{pain_point} {context}"

    matched = match_tools(enhanced_query, dimension_weights=dim_weights, top_n=5)
    roadmap = generate_roadmap(matched, industry, department, pain_point)

    assert len(roadmap["top3_tools"]) == 3
    assert roadmap["difficulty"] >= 1

    # 品質管控的主維度應偏向感知
    top_dims = []
    for t in roadmap["top3_tools"]:
        top_dims.extend(t["dimensions"])
    # "感知" should appear at least once for visual inspection use case
    assert "感知" in top_dims or "認知" in top_dims, \
        f"QC should match perception/cognition tools, got: {top_dims}"

    print("✅ test_full_pipeline_manufacturing passed")
    print(f"   Top3: {[t['name'] for t in roadmap['top3_tools']]}")


def test_full_pipeline_finance():
    """測試完整流程 — 金融業風控"""
    industry = "金融"
    department = "風控"
    pain_point = "欺詐偵測不夠即時，信用風險評估模型老舊"

    dim_weights = compute_dimension_weights(industry, department)
    context = get_industry_context_text(industry, department)
    enhanced_query = f"{pain_point} {context}"

    matched = match_tools(enhanced_query, dimension_weights=dim_weights, top_n=5)
    roadmap = generate_roadmap(matched, industry, department, pain_point)

    assert len(roadmap["top3_tools"]) == 3
    # 金融業難度應有修正
    assert roadmap["difficulty"] >= 2

    print("✅ test_full_pipeline_finance passed")
    print(f"   Top3: {[t['name'] for t in roadmap['top3_tools']]}")
    print(f"   Difficulty: {roadmap['difficulty_display']}")


def test_report_format():
    """測試報告格式包含必要段落"""
    industry = "物流"
    department = "運輸配送"
    pain_point = "配送路線不最佳化，車輛調度困難"

    dim_weights = compute_dimension_weights(industry, department)
    context = get_industry_context_text(industry, department)
    enhanced_query = f"{pain_point} {context}"

    matched = match_tools(enhanced_query, dimension_weights=dim_weights, top_n=5)
    roadmap = generate_roadmap(matched, industry, department, pain_point)

    report = roadmap["full_report"]
    assert "AI 轉型路徑圖" in report
    assert "Top 3 推薦工具" in report
    assert "n8n 自動化工作流草案" in report
    assert "導入難度" in report or "★" in report
    assert "建議下一步" in report

    print("✅ test_report_format passed")


if __name__ == "__main__":
    test_full_pipeline_retail()
    test_full_pipeline_manufacturing()
    test_full_pipeline_finance()
    test_report_format()
    print("\n🎉 All roadmap generator tests passed!")
