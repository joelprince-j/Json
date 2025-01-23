import os
import json
import pymongo
from bson.objectid import ObjectId
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

# MongoDB Atlas URI (replace with your actual MongoDB Atlas credentials)
MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION")

# Create MongoDB client and connect to MongoDB Atlas
client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
db = client[MONGO_DB]
collection = db[MONGO_COLLECTION]
counter_collection = db["counters"]

# Helper function to generate unique IDs
def generate_id(type_prefix):
    try:
        counter_doc = counter_collection.find_one_and_update(
            {"type": type_prefix},
            {"$inc": {"count": 1}},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER
        )
        count = counter_doc["count"]
        return f'{type_prefix}-{str(count).zfill(4)}'
    except Exception as e:
        raise RuntimeError(f"Error generating ID: {str(e)}")

# Lambda handler for managing requests (POST, GET, PUT, DELETE)
def lambda_handler(event, context):
    http_method = event["httpMethod"]
    
    # Handle item creation (POST request)
    if http_method == "POST" and "pathParameters" not in event:
        return create_entry(event, context)
    
    # Handle item operations (GET, PUT, DELETE)
    if "pathParameters" in event and "id" in event["pathParameters"]:
        return handle_item(event, context)
        
    return {
        "statusCode": 400,
        "body": json.dumps({"error": "Invalid request"})
    }

# Lambda handler for creating a new entry (POST)
def create_entry(event, context):
    try:
        body = json.loads(event["body"])

        if "name" not in body or "type" not in body:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Missing required fields: 'name' and 'type'"})
            }

        # Generate a new unique ID
        new_id = generate_id("item")
        body["id"] = new_id
        result = collection.insert_one(body)
        body["_id"] = str(result.inserted_id)

        return {
            "statusCode": 201,
            "body": json.dumps({"message": "New item created", "item": body})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Error creating item: {str(e)}"})
        }

# Lambda handler for fetching, updating, or deleting an item (GET, PUT, DELETE)
def handle_item(event, context):
    try:
        id = event["pathParameters"]["id"]
        method = event["httpMethod"]

        if method == "GET":
            item = collection.find_one({"id": id})
            if item:
                item["_id"] = str(item["_id"])  # Convert ObjectId to string
                return {
                    "statusCode": 200,
                    "body": json.dumps(item)
                }
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Item not found"})
            }

        if method == "PUT":
            updated_data = json.loads(event["body"])
            result = collection.update_one({"id": id}, {"$set": updated_data})
            if result.matched_count == 1:
                return {
                    "statusCode": 200,
                    "body": json.dumps({"message": f"Item with id {id} updated successfully"})
                }
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Item not found"})
            }

        if method == "DELETE":
            result = collection.delete_one({"id": id})
            if result.deleted_count == 1:
                return {
                    "statusCode": 200,
                    "body": json.dumps({"message": f"Item with id {id} deleted successfully"})
                }
            return {
                "statusCode": 404,
                "body": json.dumps({"error": "Item not found"})
            }

        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Error handling item: {str(e)}"})
        }
