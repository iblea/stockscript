from flask import Flask, request, jsonify
from werkzeug.serving import WSGIRequestHandler

# from msg import msg_queue, safe_string
from msg import safe_string
from futures import future_alert_1, get_data_hdd, set_data_hdd

from stock_data import save_stockdata_in_memory

import json

app = Flask(__name__)

# favicon 요청 무시
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content 응답


@app.route('/')
def index():
    return jsonify({"message": "Hello, World!"})


@app.route('/tradingview/stock_data', methods=['POST'])
def tradingview_stock_data():

    json_data = None
    content_type = request.headers.get('Content-Type')
    print(content_type)

    try:
        if content_type.startswith('application/json'):
            # JSON 데이터 가져오기
            json_data = request.get_json(force=True)
        else:
            # JSON 데이터가 아닌 경우, raw 데이터 가져오기
            print(f"This is not JSON content type. [{content_type}]")
            json_data = request.get_data(as_text=True, parse_form_data=False)
            json_data = json.loads(json_data)
        print(json_data)
    except Exception as e:
        print("Error: request.get_data()")
        print(e)
        json_data = None

    if json_data is None:
        print("Error: json_data is None")
        return jsonify({
            "status": "error",
            "message": "json_data is None"
        }), 400

    save_stockdata_in_memory(json_data)
    return jsonify({
        "status": "success",
        "message": "Stock data received successfully."
    }), 200


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

    content_type = request.headers.get('Content-Type')
    print(content_type)

    data: dict|None = None
    raw_data: str = ""
    message: str = ""

    try:
        raw_data = request.get_data(as_text=True, parse_form_data=False)
    except Exception as e:
        print("Error: request.get_data()")
        print(e)
        message = "Error: request.get_data()\n" + str(e) + "\n"
        try:
            raw_data = request.data.decode()
        except Exception as e:
            print("Error: request.data.decode()")
            print(e)
            message = "Error: request.data.decode()\n" + str(e) + "\n"
            raw_data = "None"

    if content_type.startswith('application/json'):
        # JSON 데이터 가져오기
        try:
            data = request.get_json()
        except Exception as e:
            raw_data = request.data.decode()
            print("Error: JSON Decode Error")
            print(e)
            message = "Error: JSON Decode Error, " + str(e) + "\n" + raw_data
            data = None

        if data is None:
            print("Error: data is None")
            message = "Error: data is None\n" + raw_data

        message: str = future_alert_1(data)
    else:
        # JSON 데이터가 아닌 경우, raw 데이터 가져오기
        print(f"This is not JSON content type. [{content_type}]")
        message = raw_data
        # print(f"raw_data: '{raw_data}'")

    # print(f"message: '{message}'")
    if message is None or len(message) == 0:
        print("Error: Wrong message! (None or empty)")
        return jsonify({
            "status": "error",
            "message": "메시지 내용이 없습니다."
        }), 400

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
