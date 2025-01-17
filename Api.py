from flask import Flask, jsonify
import json

app = Flask(__name__)

@app.route('/api/helloWorld', methods=['GET'])
def hello_world():
    return "Hello World"

@app.route('/api/json', methods=['GET'])
def get_json():
    try:
        with open('ex5_updated.json', 'r') as file:
            data = json.load(file)
        return jsonify(data)
    except FileNotFoundError:
        return jsonify({"error": "ex5_updated.json file not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
