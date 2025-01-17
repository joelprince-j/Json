from flask import Flask, request, jsonify
import json
import os

app = Flask(__name__)
JSON_FILE = "ex5.json"
# Function to read JSON data
def read_json():
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, "r") as file:
            return json.load(file)
    return []
# Function to write JSON data
def write_json(data):
    with open(JSON_FILE, "w") as file:
        json.dump(data, file, indent=4)

# function to generate new ID
def generate_new_id(data):
    ids = [int(item["id"]) for item in data]
    return str(max(ids) + 1).zfill(4) if ids else "0001"

# Fetch an item by ID
@app.route("/api/json/<id>", methods=["GET"])
def get_by_id(id):
    data = read_json()
    for item in data:
        if item["id"] == id:
            return jsonify(item), 200
    return jsonify({"error": "Item not found"}), 404

# Delete an item by ID
@app.route("/api/json/del/<id>", methods=["DELETE"])
def delete_by_id(id):
    data = read_json()
    for item in data:
        if item["id"] == id:
            data.remove(item)
            write_json(data)
            return jsonify({"message": f"Item with id {id} deleted successfully"}), 200
    return jsonify({"error": "Item not found"}), 404

# Update an item by ID
@app.route("/api/json/update/<id>", methods=["PUT"])
def update_by_id(id):
    data = read_json()
    updated_data = request.json
    for item in data:
        if item["id"] == id:
            item.update(updated_data)
            write_json(data)
            return jsonify({"message": f"Item with id {id} updated successfully"}), 200
    return jsonify({"error": "Item not found"}), 404

# Create a new entry
@app.route("/api/json/create", methods=["POST"])
def create_entry():
    data = read_json()
    new_data = request.json

    # Basic validation
    if "name" not in new_data or "type" not in new_data:
        return jsonify({"error": "Missing required fields: 'name' and 'type'"}), 400

    new_id = generate_new_id(data)  # Generate a new ID
    new_data["id"] = new_id
    data.append(new_data)
    write_json(data)
    return jsonify({"message": "New item created", "item": new_data}), 201

if __name__ == "__main__":
    app.run(debug=True)
