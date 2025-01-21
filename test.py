from pymongo import MongoClient
from tqdm import tqdm  # For progress bar

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')  
db = client["task_db"] # Database name
collection = db["task"] # Collection name
counter_collection = db["counter"] # Counter collection for max ids

# Generate unique IDs for records
def generate_id(type_prefix):
    try:
        # Increment the counter for the given type_prefix
        counter_doc = counter_collection.find_one_and_update(
            {"type": type_prefix},
            {"$inc": {"count": 1}},
            upsert=True,
            return_document=True    
        )
        # Get the updated count value
        count = counter_doc["count"]
        return f'{type_prefix}-{str(count).zfill(6)}'
    except Exception as e:
        raise RuntimeError(f"Error generating ID: {str(e)}")

# Insert 1 million records
def insert_records():
    records = []
    for _ in tqdm(range(1_000_000), desc="Inserting records"):
        record = {
            "id": generate_id("item"),
            "name": "Sample Name",
            "type": "Sample Type",
            "data": "Some sample data"
        }
        records.append(record)
        # Insert in batches of 10,000 for better performance
        if len(records) >= 10_000:
            collection.insert_many(records)
            records = []
    # Insert remaining records
    if records:
        collection.insert_many(records)

# Delete the latest 10 records based on the `id` field
def delete_latest_records():
    latest_records = collection.find().sort("id", -1).limit(10)
    latest_ids = [record["id"] for record in latest_records]
    result = collection.delete_many({"id": {"$in": latest_ids}})
    print(f"Deleted {result.deleted_count} records.")

if __name__ == "__main__":
    print("Starting insertion of 1 million records...")
    insert_records()
    print("Finished inserting records.")
    
    print("Deleting the latest 10 records...")
    delete_latest_records()
    print("Deletion complete.")
