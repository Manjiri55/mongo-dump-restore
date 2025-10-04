import configparser
import subprocess
import argparse
import sys
import os
from pymongo import MongoClient
from bson import json_util

def parse_db_args(db_args):
    db_collections = {}
    for arg in db_args:
        if ":" in arg:
            db, cols = arg.split(":", 1)
            db_collections[db] = cols.split(",")
        else:
            db_collections[arg] = []
    return db_collections

def build_dump_cmds(db_host, db_port, db_user, db_pass, auth_db, db_collections, dump_path):
    cmds = []
    if db_collections is None:
        cmd = [
            "mongodump",
            f"--host={db_host}",
            f"--port={db_port}",
            f"--username={db_user}",
            f"--password={db_pass}",
            f"--authenticationDatabase={auth_db}",
            f"--out={dump_path}"
        ]
        cmds.append(cmd)
    else:
        for db, collections in db_collections.items():
            if collections:
                for coll in collections:
                    cmd = [
                        "mongodump",
                        f"--host={db_host}",
                        f"--port={db_port}",
                        f"--username={db_user}",
                        f"--password={db_pass}",
                        f"--authenticationDatabase={auth_db}",
                        f"--out={dump_path}",
                        f"--db={db}",
                        f"--collection={coll}"
                    ]
                    cmds.append(cmd)
            else:
                cmd = [
                    "mongodump",
                    f"--host={db_host}",
                    f"--port={db_port}",
                    f"--username={db_user}",
                    f"--password={db_pass}",
                    f"--authenticationDatabase={auth_db}",
                    f"--out={dump_path}",
                    f"--db={db}"
                ]
                cmds.append(cmd)
    return cmds

def build_restore_cmd(db_host, db_port, db_user, db_pass, auth_db, db_collections, restore_path):
    cmd = [
        "mongorestore",
        f"--host={db_host}",
        f"--port={db_port}",
        f"--username={db_user}",
        f"--password={db_pass}",
        f"--authenticationDatabase={auth_db}",
        "--drop"
    ]
    if db_collections is None:
        cmd.append(restore_path)
        return cmd
    for db, collections in db_collections.items():
        if collections:
            for coll in collections:
                cmd.extend([f"--nsInclude={db}.{coll}"])
        else:
            cmd.extend([f"--nsInclude={db}.*"])
    cmd.append(restore_path)
    return cmd

def restore_missing(db_host, db_port, db_user, db_pass, auth_db, db_collections, restore_path):
    """Restore only missing documents from bsondump JSON exports."""
    uri = f"mongodb://{db_user}:{db_pass}@{db_host}:{db_port}/?authSource={auth_db}"
    client = MongoClient(uri)

    # Traverse the dump folder
    for root, dirs, files in os.walk(restore_path):
        for file in files:
            if not file.endswith(".bson"):
                continue
            coll_file = os.path.join(root, file)
            db_name = os.path.basename(os.path.dirname(coll_file))
            coll_name = file.replace(".bson", "")

            # Apply filters (db_collections)
            if db_collections is not None:
                if db_name not in db_collections:
                    continue
                if db_collections[db_name] and coll_name not in db_collections[db_name]:
                    continue

            # Convert bson -> json using bsondump
            json_file = coll_file.replace(".bson", ".json")
            subprocess.run(["bsondump", coll_file], stdout=open(json_file, "w"), check=True)

            print(f"Checking {db_name}.{coll_name} against export {json_file}...")

            coll = client[db_name][coll_name]
            existing_ids = set(doc["_id"] for doc in coll.find({}, {"_id": 1}))
            print(f"Found {len(existing_ids)} existing docs in {db_name}.{coll_name}")

            missing_docs = []
            inserted_total = 0

            with open(json_file, "r") as f:
                for line in f:
                    if not line.strip():
                        continue
                    doc = json_util.loads(line)
                    if doc["_id"] not in existing_ids:
                        missing_docs.append(doc)

                    if len(missing_docs) >= 1000:
                        coll.insert_many(missing_docs, ordered=False)
                        inserted_total += len(missing_docs)
                        print(f"Inserted {len(missing_docs)} docs...")
                        missing_docs.clear()

            if missing_docs:
                coll.insert_many(missing_docs, ordered=False)
                inserted_total += len(missing_docs)
                print(f"Inserted {len(missing_docs)} docs (final batch).")

            print(f"Completed {db_name}.{coll_name} — {inserted_total} docs inserted.")

def main():
    parser = argparse.ArgumentParser(description="MongoDB dump/restore script with .cfg config")
    parser.add_argument("config", help="Path to .cfg file")
    parser.add_argument("--dump", action="store_true", help="Run mongodump")
    parser.add_argument("--restore", action="store_true", help="Run mongorestore")
    parser.add_argument("--restoreMissing", action="store_true", help="Restore only missing documents from bsondump JSON")
    parser.add_argument("--all", action="store_true", help="Include all databases")
    parser.add_argument("--db", action="append",
                        help="Specify database(s). Optionally include collections with a colon.\n"
                             "Examples:\n"
                             "  --db testdb1                (all collections)\n"
                             "  --db testdb2:users,orders   (specific collections)")
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(args.config)

    db_host = config["database"]["host"]
    db_port = config["database"]["port"]
    db_user = config["database"]["username"]
    db_pass = config["database"]["password"]
    auth_db = config["database"].get("auth_db", "admin")

    dump_path = config["backup"]["dump_path"]
    restore_path = config["backup"]["restore_path"]

    if args.all:
        db_collections = None
    elif args.db:
        db_collections = parse_db_args(args.db)
    else:
        db_collections = {}

    if args.dump:
        print("Running mongodump...")
        dump_cmds = build_dump_cmds(db_host, db_port, db_user, db_pass, auth_db, db_collections, dump_path)
        for dump_cmd in dump_cmds:
            print("Command:", " ".join(dump_cmd))
            subprocess.run(dump_cmd, check=True)

    if args.restore:
        print("Running mongorestore...")
        restore_cmd = build_restore_cmd(db_host, db_port, db_user, db_pass, auth_db, db_collections, restore_path)
        print("Command:", " ".join(restore_cmd))
        subprocess.run(restore_cmd, check=True)

    if args.restoreMissing:
        print("Running restoreMissing...")
        restore_missing(db_host, db_port, db_user, db_pass, auth_db, db_collections, restore_path)

    if not (args.dump or args.restore or args.restoreMissing):
        print("No action selected. Use --dump, --restore, or --restoreMissing.")

if __name__ == "__main__":
    main()
