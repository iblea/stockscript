from flask import Flask, request, jsonify


app = Flask(__name__)

# favicon 요청 무시
@app.route('/favicon.ico')
def favicon():
    return '', 204  # No Content 응답


@app.route('/')
def index():
    return jsonify({"message": "Hello, World!"})


@app.route('/tradingview/alert')
def tradingview_alert():
    return jsonify({"message": "Hello, World!"})
