#!/usr/bin/env python3
"""简单的词库状态管理API服务器"""

import json
import os
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

SCRIPTS_DIR = Path(__file__).parent
PROJECT_DIR = SCRIPTS_DIR.parent
WORDS_FILE = PROJECT_DIR / "data" / "words.json"
DOCS_DIR = PROJECT_DIR / "docs"


class APIHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """处理CORS预检请求"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        """处理POST请求"""
        if self.path == "/api/word-status":
            content_length = int(self.headers.get("Content-Length", 0))
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode("utf-8"))

            word_id = data.get("wordId")
            new_status = data.get("newStatus")

            if not word_id or not new_status:
                self.send_json({"success": False, "message": "缺少必要参数"})
                return

            # 读取词汇数据
            try:
                with open(WORDS_FILE, "r", encoding="utf-8") as f:
                    words = json.load(f)
            except Exception as e:
                self.send_json(
                    {"success": False, "message": f"读取词汇文件失败: {str(e)}"}
                )
                return

            # 查找并更新词汇
            word = None
            for w in words:
                if w["id"] == word_id:
                    word = w
                    break

            if not word:
                self.send_json({"success": False, "message": "找不到指定词汇"})
                return

            # 更新状态
            word["status"] = new_status

            # 根据状态设置相应参数
            from datetime import date, timedelta

            if new_status == "new":
                word["next_review"] = date.today().isoformat()
                word["review_count"] = 0
            elif new_status == "learning":
                word["next_review"] = (date.today() + timedelta(days=1)).isoformat()
                word["review_count"] = 1
            elif new_status == "mastered":
                word["next_review"] = "2099-12-31"
                word["review_count"] = 6

            # 保存词汇数据
            try:
                with open(WORDS_FILE, "w", encoding="utf-8") as f:
                    json.dump(words, f, ensure_ascii=False, indent=2)

                self.send_json({"success": True, "message": "状态更新成功"})
            except Exception as e:
                self.send_json({"success": False, "message": f"保存失败: {str(e)}"})
        else:
            self.send_json({"success": False, "message": "无效的API路径"}, 404)

    def send_json(self, data, status=200):
        """发送JSON响应"""
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode("utf-8"))


def run_server(port=8888):
    """启动API服务器"""
    server = HTTPServer(("localhost", port), APIHandler)
    print(f"🚀 词库状态管理API启动在 http://localhost:{port}")
    print("📡 支持的API端点:")
    print("   POST /api/word-status - 更新词汇状态")
    print('   参数: {"wordId": "gen_001", "newStatus": "mastered"}')
    print("   支持的状态: new, learning, mastered")
    print("🔗 在开发环境中可以从前端调用此API")
    print("⚠️  注意：这只是开发环境API，生产环境需要更robust的解决方案")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✅ API服务器已停止")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="词库状态管理API服务器")
    parser.add_argument("--port", type=int, default=8888, help="服务器端口")
    args = parser.parse_args()
    run_server(args.port)
