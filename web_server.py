#!/usr/bin/env python3
"""
web_server.py — n8n AI 導入顧問系統 Web 介面

輕量級 HTTP Server，純 Python 標準庫，無需 Flask。
提供 JSON API 供前端 AJAX 呼叫。
"""

import json
import os
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs

from core.industry_adapter import (
    get_supported_industries,
    get_departments,
    get_department_info,
    compute_dimension_weights,
    get_industry_context_text,
)
from core.matcher import match_solutions
from core.roadmap_generator import generate_roadmap

PORT = 8080


class ConsultantHandler(SimpleHTTPRequestHandler):
    """自訂 HTTP Handler，處理靜態檔案與 API 路由"""

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            self.path = "/web/index.html"
            return SimpleHTTPRequestHandler.do_GET(self)
        elif self.path.startswith("/web/"):
            return SimpleHTTPRequestHandler.do_GET(self)
        elif self.path == "/api/industries":
            self._send_json({"industries": get_supported_industries()})
        elif self.path.startswith("/api/departments?"):
            qs = parse_qs(self.path.split("?", 1)[1])
            industry = qs.get("industry", [""])[0]
            departments = get_departments(industry)
            dept_details = {}
            for d in departments:
                info = get_department_info(industry, d)
                if info:
                    dept_details[d] = {
                        "description": info["description"],
                        "primary_dimensions": info["primary_dimensions"],
                    }
            self._send_json({"departments": departments, "details": dept_details})
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path == "/api/analyze":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            data = json.loads(body)

            industry = data.get("industry", "")
            department = data.get("department", "")
            pain_point = data.get("pain_point", "")

            if not pain_point:
                self._send_json({"error": "缺少痛點描述"}, status=400)
                return

            # 取得產業上下文增強查詢
            context = get_industry_context_text(industry, department or None)
            enhanced_query = f"{pain_point} {context}"

            # 匹配 n8n 解決方案
            matched = match_solutions(enhanced_query, top_n=3)

            # 產生路徑圖
            roadmap = generate_roadmap(
                matched_solutions=matched,
                industry_name=industry,
                department_name=department or None,
                user_query=pain_point,
            )

            # 回傳 JSON（排除 full_report 純文字）
            result = {
                "industry": roadmap["industry"],
                "department": roadmap["department"],
                "user_query": roadmap["user_query"],
                "match_score": roadmap["match_score"],
                "solution_name": roadmap["solution_name"],
                "workflow": roadmap["workflow"],
                "difficulty": roadmap["difficulty"],
                "difficulty_display": roadmap["difficulty_display"],
                "difficulty_reasons": roadmap["difficulty_reasons"],
                "steps": roadmap["steps"],
                "alternatives": roadmap["alternatives"],
            }
            self._send_json(result)
        else:
            self.send_error(404)

    def _send_json(self, data, status=200):
        response = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(response)))
        self.end_headers()
        self.wfile.write(response)

    def log_message(self, format, *args):
        """簡化日誌"""
        print(f"  [{self.client_address[0]}] {args[0]}")


if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    server = HTTPServer(("0.0.0.0", PORT), ConsultantHandler)
    print(f"\n  🤖 n8n AI 導入顧問系統 — Web Server")
    print(f"  🌐 http://localhost:{PORT}")
    print(f"  📂 Serving from: {os.getcwd()}")
    print(f"  ⏹  Press Ctrl+C to stop\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  👋 Server stopped.")
        server.server_close()
