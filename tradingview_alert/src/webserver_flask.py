from flask import Flask, request, jsonify
from werkzeug.serving import WSGIRequestHandler

from msg import msg_queue


app = Flask(__name__)

# favicon 요청 무시
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content 응답


@app.route('/')
def index():
    return jsonify({"message": "Hello, World!"})


@app.route('/tradingview/alert', methods=['POST'])
def tradingview_alert():
    global msg_queue
    # POST 요청의 JSON 데이터 가져오기
    data = request.get_json()

    if not data:
        return jsonify({"error": "데이터가 없습니다"}), 400

    # 여기서 받은 데이터 처리
    # print("받은 데이터:", data)

    stat = msg_queue.push(str(data))
    if not stat:
        print("Error: msg_queue.push()")
        return jsonify({"error": "메시지 전달 실패"}), 500

    # 성공 응답
    return jsonify({
        "status": "success",
        "received_data": data
    }), 200
