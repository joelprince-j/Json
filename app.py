from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId  # For working with MongoDB ObjectIds

app = Flask(__name__)

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  # MongoDB URI
db = client["task_db"]
collection = db["task"]
counter_collection = db["counter"]  # Counter collection for custom IDs

# Helper function to generate unique IDs
def generate_id(type_prefix):
    try:
        # Increment the counter for the given type_prefix
        counter_doc = counter_collection.find_one_and_update(
            {"type": type_prefix},
            {"$inc": {"count": 1}},
            upsert=True,  # Create the document if it doesn't exist
            return_document=True
        )
        # Get the updated count value
        count = counter_doc["count"]
        return f'{type_prefix}-{str(count).zfill(4)}'
    except Exception as e:
        raise RuntimeError(f"Error generating ID: {str(e)}")

# Create a new entry
@app.route("/api/json", methods=["POST"])
def create_entry():
    try:
        new_data = request.json

        # Basic validation for required fields
        if "name" not in new_data or "type" not in new_data:
            return jsonify({"error": "Missing required fields: 'name' and 'type'"}), 400

        # Generate a new ID using the counter collection
        new_id = generate_id("item")  # Prefix "item" for the IDs
        new_data["id"] = new_id

        # Insert into MongoDB
        result = collection.insert_one(new_data)
        new_data["_id"] = str(result.inserted_id)  # Add the MongoDB _id to the response

        return jsonify({"message": "New item created", "item": new_data}), 201
    except Exception as e:
        return jsonify({"error": f"Error creating item: {str(e)}"}), 500

# Fetch, Update, and Delete an item by custom `id`
@app.route("/api/json/<id>", methods=["GET", "PUT", "DELETE"])
def handle_item(id):
    try:
        # Handle GET request
        if request.method == "GET":
            item = collection.find_one({"id": id})  # Search by the 'id'
            if item:
                item["_id"] = str(item["_id"])  # Convert _id field to a string for JSON serialization
                return jsonify(item), 200
            return jsonify({"error": "Item not found"}), 404

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

if __name__ == "__main__":
    app.run(debug=True)
