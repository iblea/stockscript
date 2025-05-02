from flask import Flask, request, jsonify
from werkzeug.serving import WSGIRequestHandler

# from msg import msg_queue, safe_string
from msg import safe_string
from futures import future_alert_1, get_data_hdd, set_data_hdd

app = Flask(__name__)

# favicon 요청 무시
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content 응답


@app.route('/')
def index():
    return jsonify({"message": "Hello, World!"})


@app.route('/tradingview/chk', methods=['GET'])
def tradingview_check():
    # global msg_queue
    global safe_string

    safe_string.set_value("")

    # 성공 응답
    return jsonify({
        "status": "success",
    }), 200


@app.route('/tradingview/alert', methods=['POST'])
def tradingview_alert():
    # global msg_queue
    global safe_string
    # POST 요청의 JSON 데이터 가져오기
    data = request.get_json()

    if not data:
        return jsonify({"error": "데이터가 없습니다"}), 400

    message: str = future_alert_1(data)
    print(message)
    safe_string.append(message)

    # stat = msg_queue.push(message)
    # if not stat:
    #     print("Error: msg_queue.push()")
    #     return jsonify({"error": "메시지 전달 실패"}), 500

    # 성공 응답
    return jsonify({
        "status": "success"
    }), 200

    # return jsonify({
    #     "status": "success",
    #     "received_data": data
    # }), 200
