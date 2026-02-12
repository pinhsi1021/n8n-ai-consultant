"""
tests/test_industry_adapter.py — 產業適配器測試
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from core.industry_adapter import (
    get_supported_industries,
    get_industry_info,
    get_departments,
    compute_dimension_weights,
    get_industry_context_text,
)


def test_supported_industries():
    """測試支援的產業列表"""
    industries = get_supported_industries()
    assert len(industries) == 5
    expected = {"零售", "製造", "金融", "醫療", "物流"}
    assert set(industries) == expected, f"Got {industries}"
    print("✅ test_supported_industries passed")


def test_get_departments():
    """測試取得部門"""
    departments = get_departments("零售")
    assert len(departments) == 4
    assert "採購" in departments
    assert "行銷" in departments
    print("✅ test_get_departments passed")


def test_dimension_weights_specific_dept():
    """測試指定部門的維度權重"""
    weights = compute_dimension_weights("金融", "風控")
    assert "prediction" in weights
    assert weights["prediction"] > weights["perception"], \
        "Risk dept should have higher prediction weight"
    assert abs(sum(weights.values()) - 1.0) < 0.01, "Weights should sum to ~1.0"
    print("✅ test_dimension_weights_specific_dept passed")


def test_dimension_weights_all_dept():
    """測試全部門平均權重"""
    weights = compute_dimension_weights("製造")
    assert len(weights) == 4
    assert abs(sum(weights.values()) - 1.0) < 0.02
    print("✅ test_dimension_weights_all_dept passed")


def test_unknown_industry_default():
    """測試未知產業回傳預設均等權重"""
    weights = compute_dimension_weights("不存在的產業")
    assert weights == {"perception": 0.25, "cognition": 0.25, "prediction": 0.25, "automation": 0.25}
    print("✅ test_unknown_industry_default passed")


def test_context_text():
    """測試情境文字產生"""
    text = get_industry_context_text("零售", "客服")
    assert "客服" in text or "回覆" in text
    assert len(text) > 10
    print("✅ test_context_text passed")


if __name__ == "__main__":
    test_supported_industries()
    test_get_departments()
    test_dimension_weights_specific_dept()
    test_dimension_weights_all_dept()
    test_unknown_industry_default()
    test_context_text()
    print("\n🎉 All industry adapter tests passed!")
