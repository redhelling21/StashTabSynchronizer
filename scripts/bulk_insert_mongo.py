import os
import json
from pymongo import MongoClient

# Step 1: Get the list of JSON files in the folder
folder_path = "D:/Work/stash-tabs-exporter/dist/data"
json_files = [f for f in os.listdir(folder_path) if f.endswith(".json")]
print(json_files)

# Step 2: Connect to MongoDB
username = "mongoadmin"
password = "bdung"
host = "localhost"  # Replace with your MongoDB host address
port = 27017  # Replace with your MongoDB port
client = MongoClient(f"mongodb://{username}:{password}@{host}:{port}/")
db = client["test_mongo"]
collection = db["stashes"]
collection.delete_many({})
# Step 3 and 4: Read and insert each JSON file into MongoDB
for file_name in json_files:
    file_path = os.path.join(folder_path, file_name)

    with open(file_path, "r") as file:
        data = json.load(file)
        if data:
            collection.insert_many(data)

# Step 5: Close the MongoDB connection
client.close()
