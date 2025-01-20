from flask import Flask, request, jsonify
from pymongo import MongoClient
import json

app = Flask(__name__)

# Connect to MongoDB 
client = MongoClient('mongodb://localhost:27017/')  # MongoDB URI
db = client["task_db"]  
collection = db["task"] 

# Fetch, Update, and Delete an item by custom `id`
@app.route("/api/json/<id>", methods=["GET", "PUT", "DELETE"])
def handle_item(id):
    try:
        
        if request.method == "GET":
           item = collection.find_one({"id": id})  # Search by the 'id' 

        if item:
            # Convert _id field to a string for JSON serialization
            item["_id"] = str(item["_id"])  
            return jsonify(item), 200

        return jsonify({"error": "Item not found"}), 404
    except Exception as e:
        return jsonify({"error": f"Error handling item: {str(e)}"}), 500

        # Handle PUT request
        if request.method == "PUT":
            updated_data = request.json
            result = collection.update_one({"id": id}, {"$set": updated_data})
            if result.matched_count == 1:
                return jsonify({"message": f"Item with id {id} updated successfully"}), 200
            return jsonify({"error": "Item not found"}), 404

        # Handle DELETE request
        if request.method == "DELETE":
            result = collection.delete_one({"id": id})
            if result.deleted_count == 1:
                return jsonify({"message": f"Item with id {id} deleted successfully"}), 200
            return jsonify({"error": "Item not found"}), 404

    except Exception as e:
        return jsonify({"error": f"Error handling item: {str(e)}"}), 500

# Create a new entry
@app.route("/api/json", methods=["POST"])
def create_entry():
    try:
        new_data = request.json

        # Basic validation for required fields
        if "name" not in new_data or "type" not in new_data:
            return jsonify({"error": "Missing required fields: 'name' and 'type'"}), 400

        # Generate a custom ID
        existing_ids = [item["id"] for item in collection.find({}, {"id": 1})]
        new_id = str(int(max(existing_ids) or 0) + 1).zfill(4)

        new_data["id"] = new_id

        # Insert into MongoDB
        result = collection.insert_one(new_data)
        new_data["_id"] = str(result.inserted_id)  # Add the MongoDB _id to the response

        return jsonify({"message": "New item created", "item": new_data}), 201
    except Exception as e:
        return jsonify({"error": f"Error creating item: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
