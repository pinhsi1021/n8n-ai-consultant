#!/usr/bin/env python3
"""
main.py — 通用 AI 導入顧問系統 CLI

互動式命令列介面，引導用戶完成：
  1. 選擇產業
  2. 選擇部門（可選）
  3. 描述業務痛點
  4. 產出 AI 轉型路徑圖
"""

import sys
from core.industry_adapter import (
    get_supported_industries,
    get_departments,
    compute_dimension_weights,
    get_industry_context_text,
)
from core.matcher import match_tools
from core.roadmap_generator import generate_roadmap


BANNER = r"""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         🤖  通用 AI 導入顧問系統                             ║
║         Universal AI Adoption Consultant                     ║
║                                                              ║
║         輕量級 · 無 LLM · 純 Python 驅動                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
"""


def select_industry():
    """讓用戶選擇產業"""
    industries = get_supported_industries()
    print("\n📂 請選擇您的產業：")
    for i, name in enumerate(industries, 1):
        print(f"   [{i}] {name}")
    print(f"   [0] 自行輸入其他產業")

    while True:
        choice = input("\n👉 請輸入編號：").strip()
        if choice == "0":
            custom = input("   請輸入產業名稱：").strip()
            if custom:
                return custom
        elif choice.isdigit() and 1 <= int(choice) <= len(industries):
            return industries[int(choice) - 1]
        print("   ⚠️  輸入無效，請重新選擇。")


def select_department(industry_name):
    """讓用戶選擇部門"""
    departments = get_departments(industry_name)
    if not departments:
        print(f"\n   ℹ️  產業「{industry_name}」不在預設對應表中，將使用均等維度權重。")
        return None

    print(f"\n📋 「{industry_name}」產業的部門：")
    for i, name in enumerate(departments, 1):
        print(f"   [{i}] {name}")
    print(f"   [0] 不指定 (全部門分析)")

    while True:
        choice = input("\n👉 請輸入編號：").strip()
        if choice == "0":
            return None
        elif choice.isdigit() and 1 <= int(choice) <= len(departments):
            return departments[int(choice) - 1]
        print("   ⚠️  輸入無效，請重新選擇。")


def get_pain_point():
    """讓用戶描述痛點"""
    print("\n💬 請描述您目前面臨的業務痛點：")
    print("   (例如：客戶流失率太高、報表產出太慢、品質檢測靠人工...)")
    while True:
        query = input("\n👉 痛點描述：").strip()
        if len(query) >= 4:
            return query
        print("   ⚠️  描述太短，請至少輸入 4 個字。")


def run_interactive():
    """執行互動式流程"""
    print(BANNER)

    # Step 1: 選擇產業
    industry = select_industry()
    print(f"\n   ✅ 已選擇產業：{industry}")

    # Step 2: 選擇部門
    department = select_department(industry)
    if department:
        print(f"   ✅ 已選擇部門：{department}")
    else:
        print("   ✅ 分析範圍：全部門")

    # Step 3: 描述痛點
    user_query = get_pain_point()

    # ── 計算與匹配 ──────────────────────────────────────────
    print("\n⏳ 正在分析，請稍候...")

    # 取得維度權重
    dim_weights = compute_dimension_weights(industry, department)

    # 加入產業情境文字到查詢中增強匹配
    context = get_industry_context_text(industry, department)
    enhanced_query = f"{user_query} {context}"

    # 執行 TF-IDF 匹配
    matched = match_tools(enhanced_query, dimension_weights=dim_weights, top_n=5)

    if not matched:
        print("\n❌ 很抱歉，未能找到匹配的工具。請嘗試用不同方式描述您的痛點。")
        return

    # ── 產生路徑圖 ──────────────────────────────────────────
    roadmap = generate_roadmap(
        matched_tools=matched,
        industry_name=industry,
        department_name=department,
        user_query=user_query,
    )

    # 輸出報告
    print(roadmap["full_report"])

    # ── 詢問是否匯出 ──────────────────────────────────────
    export = input("📥 是否匯出 JSON 格式的路徑圖？(y/n) ").strip().lower()
    if export == "y":
        import json
        import datetime
        filename = f"roadmap_{industry}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        export_data = {
            "industry": roadmap["industry"],
            "department": roadmap["department"],
            "user_query": roadmap["user_query"],
            "difficulty": roadmap["difficulty"],
            "primary_dimension": roadmap["primary_dimension"],
            "top3_tools": roadmap["top3_tools"],
            "workflow_draft": roadmap["workflow_draft"],
        }
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        print(f"\n   ✅ 已匯出至：{filename}")

    print("\n👋 感謝使用 AI 導入顧問系統！祝您的 AI 轉型之路順利！")


def run_non_interactive(industry, department, pain_point):
    """非互動模式（供測試或批次使用）"""
    dim_weights = compute_dimension_weights(industry, department)
    context = get_industry_context_text(industry, department)
    enhanced_query = f"{pain_point} {context}"
    matched = match_tools(enhanced_query, dimension_weights=dim_weights, top_n=5)
    roadmap = generate_roadmap(
        matched_tools=matched,
        industry_name=industry,
        department_name=department,
        user_query=pain_point,
    )
    return roadmap


if __name__ == "__main__":
    if len(sys.argv) == 4:
        # 非互動模式: python main.py <產業> <部門> <痛點>
        roadmap = run_non_interactive(sys.argv[1], sys.argv[2], sys.argv[3])
        print(roadmap["full_report"])
    else:
        run_interactive()
