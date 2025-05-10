# from flask import Flask, jsonify, request

# import os


# app = Flask(__name__)
# received_data = []

# def store_received_data(data):
#     received_data.append(data)

# def create_response(message, data=None, status="success"):
#     return jsonify({
#         "message": message,
#         "data": data,
#         "status": status
#     })

# def get_request_data():
#     try:
#         return request.get_json(force=True)
#     except Exception:
#         return None

# @app.route('/')
# def home():
#     return "Flask API is running with HTTPS!"

# @app.route('/api', methods=['GET', 'POST'])
# def api_handler():
#     if request.method == 'GET':
#         return create_response("GET request received", received_data)
#     elif request.method == 'POST':
#         data = get_request_data()
#         if data is None:
#             return create_response("Invalid or missing JSON data", status="error"), 400
#         store_received_data(data)
#         return create_response("POST request received", data)

# if __name__ == '__main__':
#     # context = ('cert.pem', 'key.pem')  
#     # app.run(host='0.0.0.0', port=8000, debug=True, ssl_context=context)

#     # 证书路径--相对
#     BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#     context = (
#         os.path.join(BASE_DIR, 'cert.pem'),
#         os.path.join(BASE_DIR, 'key.pem')
#     )

#     app.run(host='0.0.0.0', port=8000, debug=True, ssl_context=context)

'''
from flask import Flask, jsonify, request
import os

app = Flask(__name__)

# 数据容器
received_data = []

# ---------------- 工具函数 ----------------
def store_received_data(data):
    received_data.append(data)

def create_response(message, data=None, status="success"):
    return jsonify({
        "message": message,
        "data": data,
        "status": status
    })

def get_request_data():
    try:
        return request.get_json(force=True)
    except Exception:
        return None

# ---------------- 路由 ----------------
@app.route('/')
def home():
    return "✅ Flask HTTPS 服务正常运行中！"

@app.route('/api', methods=['GET', 'POST'])
def api_handler():
    if request.method == 'GET':
        return create_response("✅ GET 收到", received_data)
    elif request.method == 'POST':
        data = get_request_data()
        if data is None:
            return create_response("❌ 请求数据无效", status="error"), 400
        store_received_data(data)
        return create_response("✅ POST 成功", data)

# ---------------- 启动 HTTPS 服务 ----------------
if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(BASE_DIR, 'cert.pem')
    key_path = os.path.join(BASE_DIR, 'key.pem')

    # 使用自签名证书启动 HTTPS 服务
    context = (cert_path, key_path)
    app.run(host='0.0.0.0', port=8000, debug=True, ssl_context=context)

    





from flask import Flask, jsonify, request
import os
import traceback

app = Flask(__name__)
received_data = []

# ---------------- 工具函数 ----------------
def store_received_data(data):
    received_data.append(data)

def create_response(message, data=None, status="success"):
    return jsonify({
        "status": status,
        "message": message,
        "data": data
    })

def get_request_data():
    try:
        if not request.is_json:
            app.logger.warning("❌ 请求 Content-Type 不是 application/json")
            return None
        return request.get_json(force=True)
    except Exception as e:
        app.logger.error("❌ 解析 JSON 出错: %s", traceback.format_exc())
        return None

# ---------------- 路由 ----------------
@app.route('/')
def home():
    return "✅ Flask HTTPS 服务正常运行中！"

@app.route('/api', methods=['GET', 'POST'])
def api_handler():
    try:
        if request.method == 'GET':
            app.logger.info("✅ 收到 GET 请求")
            return create_response("✅ GET 请求成功", received_data)
        
        elif request.method == 'POST':
            data = get_request_data()
            if data is None:
                return create_response("❌ 无效 JSON 或 Content-Type 错误", status="error"), 400
            store_received_data(data)
            app.logger.info(f"✅ 收到 POST 数据: {data}")
            return create_response("✅ POST 数据成功接收", data)
    except Exception as e:
        app.logger.error("❌ 处理请求出错: %s", traceback.format_exc())
        return create_response("❌ 服务内部错误", status="error"), 500

# ---------------- 启动 HTTPS 服务 ----------------
if __name__ == '__main__':
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    cert_path = os.path.join(BASE_DIR, 'cert.pem')
    key_path = os.path.join(BASE_DIR, 'key.pem')

    # 检查证书文件是否存在
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print(f"❌ 证书文件未找到:\n  cert.pem = {cert_path}\n  key.pem = {key_path}")
        exit(1)

    context = (cert_path, key_path)
    print("🚀 启动 HTTPS 服务: https://127.0.0.1:8000")
    app.run(host='0.0.0.0', port=8000, debug=True, ssl_context=context)
'''


































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
    timestamped = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "data": data
    }
    received_data.append(timestamped)

def create_response(message, data=None, status="success", code=200):
    return jsonify({
        "status": status,
        "message": message,
        "data": data
    }), code

def get_request_data():
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


