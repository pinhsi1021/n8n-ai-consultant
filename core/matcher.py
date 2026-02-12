"""
matcher.py — TF-IDF 痛點匹配引擎

使用 scikit-learn 的 TfidfVectorizer 將用戶描述的痛點
與 n8n_solutions.json 中的解決方案進行向量化匹配。
"""

import json
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def load_solutions():
    """載入 n8n 解決方案庫"""
    with open(os.path.join(DATA_DIR, "n8n_solutions.json"), "r", encoding="utf-8") as f:
        data = json.load(f)
    return data["solutions"]


def build_solution_corpus(solutions):
    """
    為每個解決方案建立文本語料，組合 name + keywords + pain_points + workflow description。
    回傳 corpus list，索引與 solutions 一致。
    """
    corpus = []
    for sol in solutions:
        text_parts = [
            sol.get("name", ""),
            sol.get("workflow", {}).get("description", ""),
            " ".join(sol.get("keywords", [])),
            " ".join(sol.get("pain_points", [])),
        ]
        corpus.append(" ".join(text_parts))
    return corpus


def match_solutions(user_query, top_n=3):
    """
    將用戶痛點描述與 n8n 解決方案庫進行 TF-IDF + cosine similarity 匹配。

    Parameters
    ----------
    user_query : str
        用戶描述的業務痛點。
    top_n : int
        回傳的方案數量。

    Returns
    -------
    list[dict]
        排序後的匹配結果，每項包含 solution 物件與 similarity 分數。
    """
    solutions = load_solutions()
    corpus = build_solution_corpus(solutions)

    # 加入用戶查詢作為最後一項
    corpus.append(user_query)

    # TF-IDF 向量化（支援中英文混合）
    vectorizer = TfidfVectorizer(
        analyzer="char_wb",   # 字元級分詞，對中文友好
        ngram_range=(2, 4),   # 2~4 字元 n-gram
        max_features=5000,
        sublinear_tf=True,
    )
    tfidf_matrix = vectorizer.fit_transform(corpus)

    # 計算用戶查詢（最後一項）與所有方案的相似度
    query_vector = tfidf_matrix[-1]
    solution_vectors = tfidf_matrix[:-1]
    similarities = cosine_similarity(query_vector, solution_vectors).flatten()

    # 排序並取 Top-N
    ranked_indices = similarities.argsort()[::-1][:top_n]

    results = []
    for idx in ranked_indices:
        if similarities[idx] > 0:
            results.append({
                "solution": solutions[idx],
                "similarity": round(float(similarities[idx]), 4),
            })

    return results


# ── 保留舊函數名稱以兼容測試 ──
def load_tools():
    """向後兼容"""
    return load_solutions()

def match_tools(user_query, dimension_weights=None, top_n=5):
    """向後兼容"""
    return match_solutions(user_query, top_n=top_n)
