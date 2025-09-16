import subprocess
import sys
import argparse
from pymongo import MongoClient

CONFIG_FILE = "config.cfg"

# Define test databases/collections
DATABASES = {
    "testdb1": ["users", "orders", "products"],
    "testdb2": ["employees", "departments", "salaries", "projects"],
    "testdb3": ["students", "courses", "enrollments"]
}

def run_command(cmd):
    """Run a shell command and exit if it fails."""
    print(f"\n>>> Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError:
        print(f"Command failed: {cmd}")
        sys.exit(1)

def get_collection_count(db_name, coll_name):
    """Return count of docs in a collection."""
    client = MongoClient("mongodb://admin:secret@localhost:27017/?authSource=admin")
    return client[db_name][coll_name].count_documents({})

def verify_data(databases, expected_count=5):
    """Verify that each collection has the expected number of docs."""
    all_ok = True
    for db_name, collections in databases.items():
        for coll in collections:
            count = get_collection_count(db_name, coll)
            print(f"Check {db_name}.{coll}: {count} docs")
            if count != expected_count:
                print(f"Mismatch in {db_name}.{coll}, expected {expected_count}, found {count}")
                all_ok = False
    return all_ok

def drop_databases(databases):
    """Drop all given databases."""
    client = MongoClient("mongodb://admin:secret@localhost:27017/?authSource=admin")
    for db_name in databases.keys():
        client.drop_database(db_name)
        print(f"Dropped {db_name}")

def test_full_dump_restore():
    print("\n=== TEST 1: FULL DUMP & RESTORE ===")
    run_command("python3 populateMultipleDbs.py")

    print("\nVerifying population...")
    assert verify_data(DATABASES), "Population verification failed"

    run_command(f"python3 dump_restore.py {CONFIG_FILE} --dump --all")

    print("\nDropping DBs...")
    drop_databases(DATABASES)

    print("\nVerifying DBs are empty...")
    assert verify_data(DATABASES, expected_count=0), "Databases not empty after drop"

    run_command(f"python3 dump_restore.py {CONFIG_FILE} --restore --all")

    print("\nVerifying restore...")
    assert verify_data(DATABASES), "Restore verification failed"
    print("Full dump/restore passed!")

def test_partial_dump_restore():
    print("\n=== TEST 2: PARTIAL DUMP & RESTORE ===")
    run_command("python3 populateMultipleDbs.py")

    print("\nVerifying population...")
    assert verify_data(DATABASES), "Population verification failed"

    # Example: only dump testdb1 (all collections) and employees from testdb2
    run_command(f"python3 dump_restore.py {CONFIG_FILE} --dump --db testdb1 --db testdb2:employees")

    print("\nDropping DBs...")
    drop_databases(DATABASES)

    print("\nVerifying DBs are empty...")
    assert verify_data(DATABASES, expected_count=0), "Databases not empty after drop"

    run_command(f"python3 dump_restore.py {CONFIG_FILE} --restore --db testdb1 --db testdb2:employees")

    print("\nVerifying restore...")
    # Expected: testdb1.* all restored, testdb2.employees restored, others empty
    assert verify_data({"testdb1": DATABASES["testdb1"], "testdb2": ["employees"]}), "Partial restore failed"

    # Double-check excluded collections are empty
    for coll in ["departments", "salaries", "projects"]:
        assert get_collection_count("testdb2", coll) == 0, f"{coll} should not have been restored"

    for coll in DATABASES["testdb3"]:
        assert get_collection_count("testdb3", coll) == 0, f"{coll} should not have been restored"

    print("Partial dump/restore passed!")

def main():
    parser = argparse.ArgumentParser(description="Automated tests for MongoDB dump/restore")
    parser.add_argument("--test", choices=["full", "partial", "all"], default="all",
                        help="Which test to run (default: all)")
    args = parser.parse_args()

    if args.test in ("full", "all"):
        test_full_dump_restore()
    if args.test in ("partial", "all"):
        test_partial_dump_restore()

    print("\nALL SELECTED TESTS PASSED!")

if __name__ == "__main__":
    main()
