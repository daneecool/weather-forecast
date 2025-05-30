from flask import Flask, jsonify
import json
import os

app = Flask(__name__)

@app.route('/')
def home():
    return jsonify({"message": "Flask server is running!"})

@app.route('/api/air_pollution')
def air_pollution():
    json_path = os.path.join(os.path.dirname(__file__), 'src', 'air_pollution.json')
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/api/quake')
def quake():
    json_path = os.path.join(os.path.dirname(__file__), 'src', 'quake.json')
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/api/typhoon_predict')
def typhoon_predict():
    json_path = os.path.join(os.path.dirname(__file__), 'src', 'typhoon_predict.json')
    with open(json_path, encoding='utf-8') as f:
        data = json.load(f)
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
