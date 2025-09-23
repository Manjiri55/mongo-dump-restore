from pymongo import MongoClient
import random

def main():
    # Connection (adjust if needed)
    client = MongoClient("mongodb://admin:secret@localhost:27017/?authSource=admin&replicaSet=rs0")

    # Define databases and collections
    databases = {
        "testdb1": ["users", "orders", "products"],
        "testdb2": ["employees", "departments", "salaries", "projects"],
        "testdb3": ["students", "courses", "enrollments"]
    }

    for db_name, collections in databases.items():
        db = client[db_name]
        for coll_name in collections:
            coll = db[coll_name]

            # Cleanup first
            coll.delete_many({})

            docs = []
            for i in range(5):
                if coll_name == "users":
                    doc = {
                        "username": f"user{i}",
                        "age": random.randint(18, 60),
                        "email": f"user{i}@example.com"
                    }
                elif coll_name == "orders":
                    doc = {
                        "order_id": f"O{i}{random.randint(100,999)}",
                        "amount": random.randint(20, 500),
                        "status": random.choice(["pending", "shipped", "delivered"])
                    }
                elif coll_name == "products":
                    doc = {
                        "product_name": f"Product{i}",
                        "price": random.randint(10, 300),
                        "stock": random.randint(0, 50)
                    }
                elif coll_name == "employees":
                    doc = {
                        "name": f"Employee{i}",
                        "role": random.choice(["Engineer", "Manager", "HR", "Analyst"]),
                        "salary": random.randint(30000, 90000)
                    }
                elif coll_name == "departments":
                    doc = {
                        "dept_id": i,
                        "dept_name": random.choice(["HR", "Finance", "Engineering", "Sales"])
                    }
                elif coll_name == "salaries":
                    doc = {
                        "emp_id": i,
                        "base": random.randint(30000, 80000),
                        "bonus": random.randint(1000, 10000)
                    }
                elif coll_name == "projects":
                    doc = {
                        "project_name": f"Project{i}",
                        "budget": random.randint(5000, 50000),
                        "status": random.choice(["ongoing", "completed", "on-hold"])
                    }
                elif coll_name == "students":
                    doc = {
                        "student_id": f"S{i}{random.randint(100,999)}",
                        "name": f"Student{i}",
                        "grade": random.choice(["A", "B", "C", "D"])
                    }
                elif coll_name == "courses":
                    doc = {
                        "course_id": f"C{i}{random.randint(100,999)}",
                        "title": f"Course{i}",
                        "credits": random.randint(1, 5)
                    }
                elif coll_name == "enrollments":
                    doc = {
                        "student_id": f"S{i}{random.randint(100,999)}",
                        "course_id": f"C{i}{random.randint(100,999)}",
                        "status": random.choice(["active", "completed", "dropped"])
                    }
                else:
                    doc = {"id": i, "value": random.randint(1, 100)}

                docs.append(doc)

            # Insert batch
            result = coll.insert_many(docs)
            print(f"Inserted {len(result.inserted_ids)} docs into {db_name}.{coll_name}")

    print("Databases populated successfully.")

if __name__ == "__main__":
    main()
