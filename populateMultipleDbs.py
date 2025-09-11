from pymongo import MongoClient
import random

def main():
    # Connection (adjust if needed)
    client = MongoClient("mongodb://admin:secret@localhost:27017/?authSource=admin")

    # Define databases and collections
    databases = {
        "testdb1": ["users", "orders", "products"],
        "testdb2": ["employees", "departments", "salaries", "projects"],
        "testdb3": ["students", "courses", "enrollments"]
    }

    # Populate each database and collection
    for db_name, collections in databases.items():
        db = client[db_name]
        for coll_name in collections:
            coll = db[coll_name]

            # Insert 5 sample documents
            docs = []
            for i in range(5):
                docs.append({
                    "id": i,
                    "collection": coll_name,
                    "db": db_name,
                    "value": random.randint(1, 100),
                })
            result = coll.insert_many(docs)
            print(f"Inserted {len(result.inserted_ids)} docs into {db_name}.{coll_name}")

    print("Databases populated successfully.")

if __name__ == "__main__":
    main()
