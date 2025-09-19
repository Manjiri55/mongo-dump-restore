MongoDB Dump & Restore Utility

This Python script provides a convenient way to backup (dump) and restore MongoDB databases and collections using mongodump and mongorestore.
It supports both full database dumps and selective dumps of specific collections, all configurable via command-line arguments and a .cfg file.

---------------------------
# Project Structure

project/
├── dump_restore.py # Main script to dump and restore
├── dump_restore_mvp.py # Dump/restore script (basic MVP version)
├── dump_restore_oplog.py # Dump/restore script with oplog support
├── populateMultipleDbs.py # Script to populate test data
├── populateMultipleDbs_mvp.py # Populate test databases (for basic MVP)
├── populateMultipleDbsForOplog.py # Populate test databases for oplog
├── config.cfg # Configuration file (DB connection settings)
└── README.md # Project documentation

-------------------------------
# Features

Config-driven: Database connection details and backup paths are stored in a .cfg file.

Scope:
Dump/restore all databases (--all)
Dump/restore specific databases (--db dbname)
Dump/restore specific collections (--db dbname:coll1,coll2)

Automatic restore with --drop (replaces existing data).

Prints the exact mongodump / mongorestore commands being run.

--------------------------
# Requirements

Python 3.x

MongoDB tools (mongodump, mongorestore) installed and available in PATH.

----------------------------

# Configuration (config.cfg)

Create a .cfg file with the following structure:

[database]
host = localhost
port = 27017
username = admin
password = secret
auth_db = admin

[backup]
dump_path = /path/to/backup/folder
restore_path = /path/to/backup/folder

- auth_db defaults to admin if not provided.
- dump_path is where dumps will be stored.
- restore_path is where data will be restored from.

--------------------------
# Populate Test Databases:

Before testing the dump/restore script, you can populate MongoDB with sample data using the provided populateMultipleDbs.py script.

Steps:

Make sure MongoDB is running and accessible with the credentials in your config (admin:secret on localhost:27017).

Run the script:

python populateMultipleDbs.py

The script will create 3 test databases with collections and sample documents:

Database	Collections
testdb1	    users, orders, products
testdb2	    employees, departments, salaries, projects
testdb3	    students, courses, enrollments
----------------------------

# Usage

Run the script with one of the following options:

1 Dump all databases
  python dump_restore.py config.cfg --dump --all

2 Dump a single database
  python dump_restore.py config.cfg --dump --db testdb1

3 Dump specific collections from a database
  python dump_restore.py config.cfg --dump --db testdb2:employees,projects

4 Restore all databases from dump
  python dump_restore.py config.cfg --restore --all

5 Restore a single database
  python dump_restore.py config.cfg --restore --db testdb1

6 Restore specific collections from a database
  python dump_restore.py config.cfg --restore --db testdb2:employees,projects


 --More Examples

1 Dump/restore two databases:
  python dump_restore.py config.cfg --dump --db testdb1 --db testdb2
  python dump_restore.py config.cfg --restore --db testdb1 --db testdb2


2 Dump/restore a database and a specific collection:
  python dump_restore.py config.cfg --dump --db testdb1 --db testdb2:employees
  python dump_restore.py config.cfg --restore --db testdb1 --db testdb2:employees


3 Dump/restore for a multi-DB / multi-collection
  python dump_restore.py config.cfg --dump --db testdb2:employees,projects --db testdb1:products
  python dump_restore.py config.cfg --restore --db testdb2:employees,projects --db testdb1:products


# Notes

1 When using --restore, the script adds --drop so existing data will be replaced.
2 If neither --dump nor --restore is specified, the script does nothing.
3 Use --all OR --db, but not both.
4 Always verify dump_path and restore_path in config.cfg before running.
-----------------------------------------

# Developer notes:

Mapping of the actual mongo shell command to the script command:

1. Dump all databases

python dump_restore.py config.cfg --dump --all

Mongo command run by script:

mongodump --host=localhost --port=27017 --username=admin --password=secret \  --authenticationDatabase=admin --out=/home/manjiri/dump/d0919_744

2. Dump a single database

python dump_restore.py config.cfg --dump --db testdb1

Mongo command run by script:

mongodump --host=localhost --port=27017 --username=admin --password=secret \  --authenticationDatabase=admin --out=/home/manjiri/dump/d0919_744 --db=testdb1

3. Dump specific collections from a database

python dump_restore.py config.cfg --dump --db testdb2:employees,projects

Mongo commands run (one per collection):

mongodump --host=localhost --port=27017 --username=admin --password=secret \  --authenticationDatabase=admin --out=/home/manjiri/dump/d0919_744 --db=testdb2 --collection=employees

mongodump --host=localhost --port=27017 --username=admin --password=secret \  --authenticationDatabase=admin --out=/home/manjiri/dump/d0919_744 --db=testdb2 --collection=projects


4. Restore all databases from dump

python dump_restore.py config.cfg --restore --all

Mongo command run by the script:

mongorestore --host=localhost --port=27017 --username=admin --password=secret \  --authenticationDatabase=admin --drop /home/manjiri/dump/d0919_744


5. Restore a single database

python dump_restore.py config.cfg --restore --db testdb1

Command run:

mongorestore --host=localhost --port=27017 --username=admin --password=secret \  --authenticationDatabase=admin --drop --nsInclude=testdb1.* /home/manjiri/dump/d0919_744


6. Restore specific collections from a database

python dump_restore.py config.cfg --restore --db testdb2:employees,projects


Mongo command run:

mongorestore --host=localhost --port=27017 --username=admin --password=secret \
  --authenticationDatabase=admin --drop \
  --nsInclude=testdb2.employees --nsInclude=testdb2.projects \
  /home/manjiri/dump/d0919_744


# How It Works Internally-
The script is structured into clear functions:

1. parse_db_args(db_args)

Converts CLI --db arguments into a mapping of { database_name: [collections] }.

Example:
["testdb1", "testdb2:employees,projects"]
→ { "testdb1": [], "testdb2": ["employees", "projects"] }

2. build_dump_cmds(...)

Constructs one or more mongodump commands depending on user input:

If --all, dumps all databases.
If --db dbname, dumps the whole database.
If --db dbname:coll1,coll2, dumps specific collections.

3. build_restore_cmd(...)

Constructs a single mongorestore command:

Adds --nsInclude filters for specific DBs/collections.
Always includes --drop to overwrite existing data.

Restores either:
All databases (--all), or
Only specified DBs/collections.

4. main()

Loads config file.
Parses command-line arguments.
Decides whether to run dump or restore.
Prints and executes the generated MongoDB commands using subprocess.run.

# Example flow:
Tracing the full flow: from --db arguments → Python mapping → actual mongodump commands that this script runs.

db_collections drives the commands in build_dump_cmds().

1. CLI Input

Example command:

python dump_restore.py config.cfg --dump --db testdb1 --db testdb2:employees,projects

2. Parsed Arguments → db_collections

Inside the script:

db_args = ["testdb1", "testdb2:employees,projects"]
db_collections = parse_db_args(db_args)


Result:

db_collections = {
    "testdb1": [],                        # means all collections
    "testdb2": ["employees", "projects"]  # only these collections
}

3. Passing into build_dump_cmds

build_dump_cmds looks like this (simplified):

for db, collections in db_collections.items():
    if collections:  # specific collections
        for coll in collections:
            cmd = [
                "mongodump",
                f"--db={db}",
                f"--collection={coll}",
                f"--out={dump_path}"
            ]
    else:  # no collections -> dump full DB
        cmd = [
            "mongodump",
            f"--db={db}",
            f"--out={dump_path}"
        ]

4. Generated Commands

Using the mapping above, we will get 3 separate mongodump calls:

For testdb1 (all collections):

mongodump --host=localhost --port=27017 --username=admin --password=secret --authenticationDatabase=admin --out=/path/to/backup --db=testdb1


For testdb2:employees:

mongodump --host=localhost --port=27017 --username=admin --password=secret --authenticationDatabase=admin --out=/path/to/backup --db=testdb2 --collection=employees


For testdb2:projects:

mongodump --host=localhost --port=27017 --username=admin --password=secret --authenticationDatabase=admin --out=/path/to/backup --db=testdb2 --collection=projects

5. Execution

Finally, the script loops through the commands:

for dump_cmd in dump_cmds:
    print("Command:", " ".join(dump_cmd))
    subprocess.run(dump_cmd, check=True)


So:

It prints each command (for visibility/logging).w get 
Then executes it with subprocess.run.

Summary:

--db testdb1 → [] → dumps entire DB.

--db testdb2:employees,projects → ["employees","projects"] → dumps specific collections.

Script builds multiple mongodump commands, one per DB/collection, and runs them sequentially.