"""
MBTI 星图档案馆 — 后端服务
============================
提供 MBTI 测试页面的静态服务 + 结果收集 API。
数据存储在 results.json 文件中（JSON 数组），无需数据库。
"""

import json
import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__, static_folder=".", static_url_path="")

RESULTS_FILE = "results.json"


def load_results():
    """从 results.json 加载所有结果，文件不存在时返回空列表"""
    if not os.path.exists(RESULTS_FILE):
        return []
    try:
        with open(RESULTS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except (json.JSONDecodeError, IOError):
        return []


def save_results(results):
    """保存结果列表到 results.json"""
    with open(RESULTS_FILE, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)


# ============================================================
#  静态页面
# ============================================================

@app.route("/")
def index():
    """提供 MBTI 测试页面"""
    return send_from_directory(".", "mbti.html")


# ============================================================
#  API 接口
# ============================================================

@app.route("/api/results", methods=["POST"])
def add_result():
    """保存一份测试结果"""
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "无效的请求数据"}), 400

    required = ("type", "name", "scores")
    if not all(k in data for k in required):
        return jsonify({"error": "缺少必要字段: type, name, scores"}), 400

    results = load_results()
    record = {
        "type": data["type"],
        "name": data["name"],
        "scores": data["scores"],
        "date": data.get("date", datetime.now().strftime("%Y-%m-%d")),
        "time": data.get("time", datetime.now().strftime("%H:%M:%S")),
    }
    results.append(record)

    # 最多保留 1000 条
    if len(results) > 1000:
        results = results[-1000:]

    save_results(results)
    return jsonify({"ok": True, "total": len(results)})


@app.route("/api/results", methods=["GET"])
def get_results():
    """获取所有结果（供统计图表使用）"""
    results = load_results()
    return jsonify({"total": len(results), "results": results})


if __name__ == "__main__":
    print(" 星图档案馆后端启动")
    print(" 本地访问: http://localhost:5000")
    print(" API 接口: POST/GET /api/results")
    app.run(host="0.0.0.0", port=5000, debug=True)
