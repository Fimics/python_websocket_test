from flask import Flask, request, jsonify

app = Flask(__name__)


@app.route('/postendpoint', methods=['POST'])
def handle_post():
    # 检查请求是否包含 JSON 数据
    if request.is_json:
        # 获取 JSON 数据
        data = request.get_json()
        print("Received JSON data:", data)
        # 可以在这里添加代码处理数据

        # 返回一个响应
        return jsonify({"message": "JSON received!", "yourData": data}), 200
    else:
        return jsonify({"error": "Request must be JSON"}), 400


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
