# # from flask import Flask, jsonify, request

# # app = Flask(__name__)

# # # 存储接收到的数据
# # received_data = []

# # # 监听根路由
# # @app.route('/')
# # def home():
# #     return "Hello, World!"

# # # 监听 /api 路由，支持 GET 和 POST 方法
# # @app.route('/api', methods=['GET', 'POST'])
# # def api():
# #     if request.method == 'GET':
# #         # 处理 GET 请求
# #         return jsonify({"message": "This is a GET response", "data": received_data})
# #     elif request.method == 'POST':
# #         # 处理 POST 请求
# #         data = request.get_json()  # 获取 JSON 数据
# #         print("Received POST data:", data)  # 打印接收到的数据
        
# #         # 存储接收到的数据
# #         received_data.append(data)
        
# #         # 构造响应
# #         response_data = {
# #             "message": "This is a POST response",
# #             "received_data": data,
# #             "status": "success"
# #         }
        
# #         return jsonify(response_data)

# # # 启动服务器
# # if __name__ == '__main__':
# #     app.run(host='0.0.0.0', port=8000, debug=True)

# # ##########################################



# from flask import Flask, jsonify, request

# app = Flask(__name__)

# # 存储接收到的数据
# received_data = []

# # 监听根路由
# @app.route('/')
# def home():
#     return "Hello, World!"

# # 监听 /api 路由，支持 GET 和 POST 方法
# @app.route('/api', methods=['GET', 'POST'])
# def api():
#     global received_data  # 使用 global 关键字来修改全局变量
#     if request.method == 'GET':
#         # 处理 GET 请求
#         return jsonify({
#             "message": "This is a GET response",
#             "data": received_data
#         })
#     elif request.method == 'POST':
#         # 处理 POST 请求
#         data = request.get_json()  # 获取 JSON 数据
#         if data is None:
#             return jsonify({"error": "Invalid JSON data"}), 400
        
#         print("Received POST data:", data)  # 打印接收到的数据
        
#         # 存储接收到的数据
#         received_data.append(data)
        
#         # 构造响应
#         response_data = {
#             "message": "This is a POST response",
#             "received_data": data,
#             "status": "success"
#         }
        
#         return jsonify(response_data)

# # 启动服务器
# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=8000, debug=True)




from flask import Flask, jsonify, request

app = Flask(__name__)

# 数据存储容器
received_data = []

# ---------------------- 工具函数 ----------------------

def store_received_data(data):
    """存储客户端发送的数据"""
    received_data.append(data)

def create_response(message, data=None, status="success"):
    """统一格式构建 JSON 响应"""
    return jsonify({
        "message": message,
        "data": data,
        "status": status
    })

def get_request_data():
    """安全获取 JSON 数据，返回 None 或 dict"""
    try:
        return request.get_json(force=True)
    except Exception:
        return None

# ---------------------- 路由函数 ----------------------

@app.route('/')
def home():
    return "Flask API is running!"

@app.route('/api', methods=['GET', 'POST'])
def api_handler():
    if request.method == 'GET':
        return create_response("GET request received", received_data)
    
    elif request.method == 'POST':
        data = get_request_data()
        if data is None:
            return create_response("Invalid or missing JSON data", status="error"), 400
        
        store_received_data(data)
        return create_response("POST request received", data)

# ---------------------- 启动服务 ----------------------

if __name__ == '__main__':
    # debug=True 开启自动 reload，方便虚拟机开发测试
    app.run(host='0.0.0.0', port=8000, debug=True)


