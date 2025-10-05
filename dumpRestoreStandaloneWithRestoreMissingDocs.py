import configparser
import subprocess
import argparse
import sys
import os
import datetime
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
        cmds.append([
            "mongodump",
            f"--host={db_host}",
            f"--port={db_port}",
            f"--username={db_user}",
            f"--password={db_pass}",
            f"--authenticationDatabase={auth_db}",
            f"--out={dump_path}"
        ])
    else:
        for db, collections in db_collections.items():
            if collections:
                for coll in collections:
                    cmds.append([
                        "mongodump",
                        f"--host={db_host}",
                        f"--port={db_port}",
                        f"--username={db_user}",
                        f"--password={db_pass}",
                        f"--authenticationDatabase={auth_db}",
                        f"--out={dump_path}",
                        f"--db={db}",
                        f"--collection={coll}"
                    ])
            else:
                cmds.append([
                    "mongodump",
                    f"--host={db_host}",
                    f"--port={db_port}",
                    f"--username={db_user}",
                    f"--password={db_pass}",
                    f"--authenticationDatabase={auth_db}",
                    f"--out={dump_path}",
                    f"--db={db}"
                ])
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


def get_latest_subdir(base_path):
    """Return the most recently modified dump directory."""
    subdirs = [
        os.path.join(base_path, d)
        for d in os.listdir(base_path)
        if os.path.isdir(os.path.join(base_path, d)) and d.startswith("dump_")
    ]
    if not subdirs:
        raise FileNotFoundError(f"No dump subdirectories found under {base_path}")
    return max(subdirs, key=os.path.getmtime)


def validate_restore_path(restore_path):
    """Ensure restore_path is not a parent dir containing multiple dump folders."""
    subdirs = [
        d for d in os.listdir(restore_path)
        if os.path.isdir(os.path.join(restore_path, d)) and d.startswith("dump_")
    ]
    if subdirs:
        raise ValueError(
            f"\nThe restore path '{restore_path}' contains multiple dump directories:\n"
            f"   {', '.join(subdirs[:5])}{'...' if len(subdirs) > 5 else ''}\n"
            f"Please specify a specific dump subfolder or use --latest.\n"
        )


def restore_missing(db_host, db_port, db_user, db_pass, auth_db, db_collections, restore_path):
    """Restore only missing documents from bsondump JSON exports."""
    uri = f"mongodb://{db_user}:{db_pass}@{db_host}:{db_port}/?authSource={auth_db}"
    client = MongoClient(uri)

    for root, dirs, files in os.walk(restore_path):
        for file in files:
            if not file.endswith(".bson"):
                continue
            coll_file = os.path.join(root, file)
            db_name = os.path.basename(os.path.dirname(coll_file))
            coll_name = file.replace(".bson", "")

            if db_collections is not None:
                if db_name not in db_collections:
                    continue
                if db_collections[db_name] and coll_name not in db_collections[db_name]:
                    continue

            json_file = coll_file.replace(".bson", ".json")
            subprocess.run(["bsondump", coll_file], stdout=open(json_file, "w"), check=True)

            print(f"Checking {db_name}.{coll_name} against export {json_file}...")
            coll = client[db_name][coll_name]
            existing_ids = set(doc["_id"] for doc in coll.find({}, {"_id": 1}))
            print(f"Found {len(existing_ids)} existing docs in {db_name}.{coll_name}")

            missing_docs, inserted_total = [], 0
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
    parser = argparse.ArgumentParser(description="MongoDB dump/restore script with .cfg config and CLI overrides")
    parser.add_argument("config", help="Path to .cfg file")
    parser.add_argument("--dump", action="store_true", help="Run mongodump")
    parser.add_argument("--restore", action="store_true", help="Run mongorestore")
    parser.add_argument("--restoreMissing", action="store_true", help="Restore only missing documents")
    parser.add_argument("--latest", action="store_true", help="Use latest dump directory for restore operations")
    parser.add_argument("--all", action="store_true", help="Include all databases")
    parser.add_argument("--db", action="append", help="Specify database(s) (e.g. testdb1 or testdb2:users,orders)")
    # CLI overrides for config
    parser.add_argument("--host")
    parser.add_argument("--port")
    parser.add_argument("--username")
    parser.add_argument("--password")
    parser.add_argument("--authdb")
    parser.add_argument("--dumpPath")
    parser.add_argument("--restorePath")

    args = parser.parse_args()

    # Load config
    config = configparser.ConfigParser()
    config.read(args.config)

    # Merge config + CLI overrides
    db_host = args.host or config["database"]["host"]
    db_port = args.port or config["database"]["port"]
    db_user = args.username or config["database"]["username"]
    db_pass = args.password or config["database"]["password"]
    auth_db = args.authdb or config["database"].get("auth_db", "admin")
    base_dump_path = args.dumpPath or config["backup"]["dump_path"]
    restore_path = args.restorePath or config["backup"]["restore_path"]

    # Timestamped dump subdirectory
    if args.dump:
        timestamp = datetime.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
        dump_path = os.path.join(base_dump_path.rstrip("/"), f"dump_{timestamp}")
        os.makedirs(dump_path, exist_ok=True)
        print(f"Created new dump directory: {dump_path}")
    else:
        dump_path = base_dump_path

    # Latest restore directory
    if args.latest:
        restore_path = get_latest_subdir(base_dump_path)
        print(f"Using latest dump directory for restore: {restore_path}")
    else:
        if (args.restore or args.restoreMissing) and os.path.isdir(restore_path):
            validate_restore_path(restore_path)

    # Parse db args
    if args.all:
        db_collections = None
    elif args.db:
        db_collections = parse_db_args(args.db)
    else:
        db_collections = {}

    # Actions
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
