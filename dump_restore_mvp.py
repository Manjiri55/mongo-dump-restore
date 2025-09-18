import configparser
import subprocess
import argparse
import sys

def build_dump_cmds(db_host, db_port, db_user, db_pass, auth_db, dbs, collections, dump_path):
    cmds = []

    if dbs:
        for db in dbs:
            if collections:
                # Run one command per collection per DB
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
                # Dump all collections in the DB
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
    else:
        # Dump all databases
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

    return cmds


def build_restore_cmd(db_host, db_port, db_user, db_pass, auth_db, dbs, collections, restore_path):
    cmd = [
        "mongorestore",
        f"--host={db_host}",
        f"--port={db_port}",
        f"--username={db_user}",
        f"--password={db_pass}",
        f"--authenticationDatabase={auth_db}",
        "--drop"
    ]

    if dbs:
        for db in dbs:
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
    parser.add_argument("--db", action="append", help="Specify database(s). Can be used multiple times.")
    parser.add_argument("--collection", action="append", help="Specify collection(s). Requires --db")
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

    if args.collection and not args.db:
        print("You must specify --db when using --collection.")
        sys.exit(1)

    if args.dump:
        print("Running mongodump...")
        dump_cmds = build_dump_cmds(
            db_host, db_port, db_user, db_pass, auth_db,
            args.db if not args.all else None,
            args.collection if not args.all else None,
            dump_path
        )
        for dump_cmd in dump_cmds:
            print("Command:", " ".join(dump_cmd))
            subprocess.run(dump_cmd, check=True)

    if args.restore:
        print("Running mongorestore...")
        restore_cmd = build_restore_cmd(
            db_host, db_port, db_user, db_pass, auth_db,
            args.db if not args.all else None,
            args.collection if not args.all else None,
            restore_path
        )
        print("Command:", " ".join(restore_cmd))
        subprocess.run(restore_cmd, check=True)

    if not (args.dump or args.restore):
        print("No action selected. Use --dump or --restore.")


if __name__ == "__main__":
    main()
