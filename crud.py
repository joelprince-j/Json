from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
JSON_FILE = "ex5.json"
# Function to read JSON data
def read_json():
    try:
        if os.path.exists(JSON_FILE):
            with open(JSON_FILE, "r") as file:
                return json.load(file)
        return []
    except Exception as e:
        return jsonify({"error": f"Error reading JSON file: {str(e)}"}), 500

# Function to write JSON data
def write_json(data):
    try:
        with open(JSON_FILE, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        return jsonify({"error": f"Error writing JSON file: {str(e)}"}), 500

# Function to generate a new ID
def generate_new_id(data):
    ids = [int(item["id"]) for item in data if item["id"].isdigit()]
    return str(max(ids) + 1).zfill(4) if ids else "0001"

# Fetch, Update, and Delete an item by ID
@app.route("/api/json/<id>", methods=["GET", "PUT", "DELETE"])
def handle_item(id):
    try:
        data = read_json()
        item = next((item for item in data if item["id"] == id), None)
        
        if not item:
            return jsonify({"error": "Item not found"}), 404
        
        if request.method == "GET":
            return jsonify(item), 200

        if request.method == "PUT":
            updated_data = request.json
            item.update(updated_data)
            write_json(data)
            return jsonify({"message": f"Item with id {id} updated successfully"}), 200

        if request.method == "DELETE":
            data.remove(item)
            write_json(data)
            return jsonify({"message": f"Item with id {id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

# Create a new entry
@app.route("/api/json", methods=["POST"])
def create_entry():
    try:
        data = read_json()
        new_data = request.json

        # Basic validation
        if "name" not in new_data or "type" not in new_data:
            return jsonify({"error": "Missing required fields: 'name' and 'type'"}), 400

        new_id = generate_new_id(data)
        new_data["id"] = new_id
        data.append(new_data)
        write_json(data)
        return jsonify({"message": "New item created", "item": new_data}), 201
    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
