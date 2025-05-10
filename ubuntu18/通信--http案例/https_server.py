# app_https_server.py
from flask import Flask, jsonify, request
import os
import traceback
from datetime import datetime

app = Flask(__name__)
received_data = []

# ---------------- 配置 ----------------
PORT = int(os.environ.get("HTTPS_PORT", 8000))
HOST = os.environ.get("HTTPS_HOST", "0.0.0.0")
CERT_FILE = os.environ.get("HTTPS_CERT", "cert.pem")
KEY_FILE = os.environ.get("HTTPS_KEY", "key.pem")

# ---------------- 工具函数 ----------------
def store_received_data(data):
    """存储接收到的 POST 数据，并附加时间戳"""
    timestamped = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": data
    }
    received_data.append(timestamped)

def create_response(message, data=None, status="success", code=200):
    """生成标准化响应"""
    return jsonify({
        "status": status,
        "message": message,
        "data": data
    }), code

def get_request_data():
    """获取请求的 JSON 数据"""
    try:
        if not request.is_json:
            app.logger.warning("❌ 请求 Content-Type 不是 application/json")
            return None
        return request.get_json(force=True)
    except Exception:
        app.logger.error("❌ 解析 JSON 出错:\n%s", traceback.format_exc())
        return None

# ---------------- 路由 ----------------
@app.route('/')
def home():
    return "<h3>✅ Flask HTTPS 服务运行正常</h3>"

@app.route('/api', methods=['GET', 'POST'])
def api_handler():
    """处理 API 请求（GET 和 POST）"""
    try:
        if request.method == 'GET':
            app.logger.info("📥 收到 GET 请求")
            return create_response("✅ GET 请求成功", received_data)

        elif request.method == 'POST':
            data = get_request_data()
            if data is None:
                return create_response("❌ 无效 JSON 或 Content-Type 错误", status="error", code=400)
            store_received_data(data)
            app.logger.info(f"📥 收到 POST 数据: {data}")
            return create_response("✅ POST 数据成功接收", data)

    except Exception:
        app.logger.error("❌ 处理请求出错:\n%s", traceback.format_exc())
        return create_response("❌ 服务内部错误", status="error", code=500)

# ---------------- 启动 HTTPS 服务 ----------------
if __name__ == '__main__':
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    cert_path = os.path.join(BASE_DIR, CERT_FILE)
    key_path = os.path.join(BASE_DIR, KEY_FILE)

    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print(f"❌ 找不到证书文件:\n 证书: {cert_path}\n 密钥: {key_path}")
        exit(1)

    print(f"🚀 启动 HTTPS 服务: https://{HOST}:{PORT}")
    app.run(host=HOST, port=PORT, debug=True, ssl_context=(cert_path, key_path))
