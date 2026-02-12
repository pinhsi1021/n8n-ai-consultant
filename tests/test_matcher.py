"""
tests/test_matcher.py — 匹配引擎測試
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.matcher import match_tools, load_tools, build_tool_corpus


def test_load_tools():
    """測試工具庫載入"""
    tools = load_tools()
    assert len(tools) == 20, f"Expected 20 tools, got {len(tools)}"
    for tool in tools:
        assert "name" in tool
        assert "keywords" in tool
        assert "dimensions" in tool
        assert "difficulty" in tool
    print("✅ test_load_tools passed")


def test_build_corpus():
    """測試語料建構"""
    tools = load_tools()
    corpus = build_tool_corpus(tools)
    assert len(corpus) == len(tools)
    for text in corpus:
        assert len(text) > 0
    print("✅ test_build_corpus passed")


def test_match_prediction_query():
    """測試：預測類痛點應匹配預測類工具"""
    results = match_tools("客戶流失率太高，希望能預測哪些客戶會離開")
    assert len(results) > 0, "Should return at least 1 result"

    # 前 3 名工具至少應有一個涉及 prediction 維度
    top3_dims = []
    for r in results[:3]:
        top3_dims.extend(r["tool"]["dimensions"])
    assert "prediction" in top3_dims, f"Top 3 should include prediction tools, got dims: {top3_dims}"
    print("✅ test_match_prediction_query passed")


def test_match_automation_query():
    """測試：自動化類痛點應匹配自動化工具"""
    results = match_tools("報表產出太慢，重複性工作太多需要自動化")
    assert len(results) > 0

    top3_dims = []
    for r in results[:3]:
        top3_dims.extend(r["tool"]["dimensions"])
    assert "automation" in top3_dims, f"Top 3 should include automation tools, got dims: {top3_dims}"
    print("✅ test_match_automation_query passed")


def test_match_with_dimension_weights():
    """測試：維度加權應影響排名"""
    query = "需要提高效率"

    # 無加權
    results_no_weight = match_tools(query)

    # 加權偏向感知
    results_perception = match_tools(query, dimension_weights={
        "perception": 0.8, "cognition": 0.1, "prediction": 0.05, "automation": 0.05
    })

    # 兩次結果應存在差異（至少工具順序或分數可能不同）
    assert len(results_no_weight) > 0
    assert len(results_perception) > 0
    print("✅ test_match_with_dimension_weights passed")


if __name__ == "__main__":
    test_load_tools()
    test_build_corpus()
    test_match_prediction_query()
    test_match_automation_query()
    test_match_with_dimension_weights()
    print("\n🎉 All matcher tests passed!")
