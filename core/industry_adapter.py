"""
industry_adapter.py — 產業適配器

根據用戶輸入的產業名稱，從 industry_mapping.json 動態解析
對應的部門、AI 維度與維度權重，供 matcher 加權使用。
"""

import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_industry_mapping():
    """載入產業對應表"""
    with open(os.path.join(DATA_DIR, "industry_mapping.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["industries"]


def get_supported_industries():
    """取得所有支援的產業列表"""
    mapping = load_industry_mapping()
    return list(mapping.keys())


def get_industry_info(industry_name):
    """
    根據產業名稱取得完整的產業資訊。

    Parameters
    ----------
    industry_name : str
        產業名稱 (如 '零售', '製造', '金融')

    Returns
    -------
    dict or None
        產業資訊，包含英文名、部門清單等。找不到時回傳 None。
    """
    mapping = load_industry_mapping()
    return mapping.get(industry_name)


def get_departments(industry_name):
    """
    取得指定產業下的所有部門名稱。

    Returns
    -------
    list[str]
        部門名稱列表
    """
    info = get_industry_info(industry_name)
    if not info:
        return []
    return list(info["departments"].keys())


def get_department_info(industry_name, department_name):
    """
    取得指定產業、指定部門的詳細資訊。

    Returns
    -------
    dict or None
        部門資訊，包含 description, primary_dimensions, dimension_weights 等。
    """
    info = get_industry_info(industry_name)
    if not info:
        return None
    return info["departments"].get(department_name)


def compute_dimension_weights(industry_name, department_name=None):
    """
    計算產業（和可選部門）的維度權重。

    若指定部門，直接使用該部門的維度權重。
    若未指定部門，取該產業所有部門權重的平均值。

    Parameters
    ----------
    industry_name : str
        產業名稱
    department_name : str, optional
        部門名稱

    Returns
    -------
    dict
        格式如 {"perception": 0.2, "cognition": 0.3, "prediction": 0.3, "automation": 0.2}
    """
    info = get_industry_info(industry_name)
    if not info:
        # 預設均等權重
        return {"perception": 0.25, "cognition": 0.25, "prediction": 0.25, "automation": 0.25}

    if department_name and department_name in info["departments"]:
        return info["departments"][department_name]["dimension_weights"]

    # 計算所有部門的平均權重
    all_weights = {"perception": 0, "cognition": 0, "prediction": 0, "automation": 0}
    dept_count = len(info["departments"])
    for dept in info["departments"].values():
        for dim, w in dept["dimension_weights"].items():
            all_weights[dim] += w
    for dim in all_weights:
        all_weights[dim] = round(all_weights[dim] / dept_count, 4)

    return all_weights


def get_industry_context_text(industry_name, department_name=None):
    """
    產生產業情境文字，用於增強 TF-IDF 匹配時的語境。

    Returns
    -------
    str
        包含部門描述與典型痛點的文字片段。
    """
    info = get_industry_info(industry_name)
    if not info:
        return ""

    context_parts = []

    if department_name and department_name in info["departments"]:
        dept = info["departments"][department_name]
        context_parts.append(dept["description"])
        context_parts.extend(dept["typical_pain_points"])
    else:
        for dept_name, dept in info["departments"].items():
            context_parts.append(dept_name)
            context_parts.append(dept["description"])
            context_parts.extend(dept["typical_pain_points"])

    return " ".join(context_parts)
