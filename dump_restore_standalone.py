import configparser
import subprocess
import argparse
import sys


def parse_db_args(db_args):
    """
    Parse --db arguments into { db_name: [collections] } mapping.
    Example:
      ["testdb1", "testdb2:employees,projects"]
      → { "testdb1": [], "testdb2": ["employees", "projects"] }
    """
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
        # Dump all DBs
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
        # Restore all DBs
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


def main():
    parser = argparse.ArgumentParser(description="MongoDB dump/restore script with .cfg config")
    parser.add_argument("config", help="Path to .cfg file")
    parser.add_argument("--dump", action="store_true", help="Run mongodump")
    parser.add_argument("--restore", action="store_true", help="Run mongorestore")
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

    # Build db -> collections mapping
    if args.all:
        db_collections = None
    elif args.db:
        db_collections = parse_db_args(args.db)
    else:
        db_collections = {}

    if args.dump:
        print("Running mongodump...")
        dump_cmds = build_dump_cmds(
            db_host, db_port, db_user, db_pass, auth_db,
            db_collections,
            dump_path
        )
        for dump_cmd in dump_cmds:
            print("Command:", " ".join(dump_cmd))
            subprocess.run(dump_cmd, check=True)

    if args.restore:
        print("Running mongorestore...")
        restore_cmd = build_restore_cmd(
            db_host, db_port, db_user, db_pass, auth_db,
            db_collections,
            restore_path
        )
        print("Command:", " ".join(restore_cmd))
        subprocess.run(restore_cmd, check=True)

    if not (args.dump or args.restore):
        print("No action selected. Use --dump or --restore.")


if __name__ == "__main__":
    main()
