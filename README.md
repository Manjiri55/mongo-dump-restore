
# MongoDB Dump & Restore Utility

This project provides Python scripts to backup (dump) and restore MongoDB databases and collections using the official **mongodump** and **mongorestore** tools.  
It supports both **standalone MongoDB instances** and **replica sets** (with optional oplog support for consistent cluster-wide backups).

---

## Project Structure


```
project/
├── dump_restore_standalone.py # Dump/restore script for standalone MongoDb instance
├── dump_restore_replicaset.py # Dump/restore script for MongoDB is running as a replica set (with oplog support)
├── populateMultipleDbsStandalone.py # Script to populate test data for dump_restore_standalone.py
├── populateMultipleDbsReplicaSet.py # Script to populate test data for dump_restore_replicaset.py
├── config.cfg # Configuration file (DB connection settings)
├── README.md # Project documentation
└── test_automation.py (This script tests the main dump_restore.py + populateMultipleDbs.py flow)
```
-------------------------------

# Features

Config-driven: Connection details and backup paths stored in config.cfg.

Flexible scope:

Dump/restore all databases (--all)
Dump/restore specific databases (--db dbname)
Dump/restore specific collections (--db dbname:coll1,coll2)

Oplog support (replica sets only):

--oplog → Include oplog during dump (requires --all)
--oplogReplay → Replay oplog during restore (requires --all)

Safe restore: Uses --drop to replace existing data.

Verbose: Prints the exact mongodump / mongorestore commands being executed.
--------------------------
# Requirements

Python 3.x

pymongo (pip install pymongo)

MongoDB Database Tools (mongodump, mongorestore) installed and available in PATH

----------------------------

# Configuration (config.cfg)

Create a .cfg file with the following structure:

[database]
host = localhost
port = 27017
username = <username>
password = <password>
auth_db = admin

[backup]
dump_path = /path/to/backup/folder
restore_path = /path/to/backup/folder

- auth_db defaults to admin if not provided.
- dump_path is where dumps will be stored.
- restore_path is where data will be restored from.

--------------------------
# Populate Test Databases:

Before testing the dump/restore script, you can populate MongoDB with sample data using the provided populateMultipleDbs script.

Steps:

Make sure MongoDB is running and accessible with the credentials in your config (admin:secret on localhost:27017).

Run the script:

Standalone:
python populateMultipleDbsStandalone.py

Replica Set:
python populateMultipleDbsReplicaSet.py

The script will create 3 test databases with collections and sample documents:

Database	Collections
testdb1	    users, orders, products
testdb2	    employees, departments, salaries, projects
testdb3	    students, courses, enrollments
----------------------------

# Usage

Dump & Restore Script

python dump_restore.py config.cfg [--dump] [--restore] [--all] [--db DB[:COL1,COL2,...]] [--oplog] [--oplogReplay]

-> Arguments

config.cfg : Path to the configuration file.

--dump : Run mongodump.

--restore : Run mongorestore.

--all : Include all databases. Required if using --oplog.

--db : Specify database(s) and optionally collections:
    --db testdb1 → all collections of testdb1
    --db testdb2:employees,projects → only employees and projects collections

--oplog : Add --oplog for consistent backup (only valid with --all).

--oplogReplay : Replay oplog during restore.
-------------------------------------------------------------------------

-> Examples:
   General Dump/Restore (Standalone or Replica Set). 
   Replace the generic name dump_restore.py used in the below examples with dump_restore_standalone.py or dump_restore_replicaset.py as needed.
   Run the script with one of the following options.

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
  

-> Oplog-Supported Dump/Restore (Replica Set Only)

    1 Dump all databases with oplog

      python dump_restore_replicaset.py config.cfg --dump --all --oplog


    2 Restore all with oplog replay

      python dump_restore_replicaset.py config.cfg --restore --all --oplogReplay



--oplog and --oplogReplay are only valid for replica sets, and only when dumping/restoring all databases (--all).
For single DBs or collections in replica sets, omit oplog options.

 Standalone (dump_restore_standalone.py)                                        Replica Set (dump_restore_replicaset.py)
 -----------------------------------------                                      -----------------------------------------

 **Dump all databases**           

python dump_restore_standalone.py config.cfg --dump --all                       python dump_restore_replicaset.py config.cfg --dump --all [--oplog]

 
 **Restore all databases**        

python dump_restore_standalone.py config.cfg --restore --all                  python dump_restore_replicaset.py config.cfg --restore --all [--oplogReplay]

 

# Notes

1 Ensure MongoDB user has read/write access to the databases being dumped/restored.
2 When using --restore, the script adds --drop so existing data will be replaced.
3 If neither --dump nor --restore is specified, the script does nothing.
4 Use --all OR --db, but not both.
5 Always verify dump_path and restore_path in config.cfg before running.
6 The --oplog option is only supported for full cluster dumps (--all).It is not supported for single databases or single collections.

Dump target	--oplog allowed?

All databases (--all)	                       Yes
Single database (--db testdb2)	               No
Single collection (--db testdb2:employees)	   No 

Why?
The oplog ensures cluster-wide consistency across all databases and collections. MongoDB does not allow using it for partial dumps.
-----------------------------------------

# Automation Testing

This project includes `test_automation.py` to verify dump & restore workflows.

Run all tests
python test_automation.py

Run only full dump & restore test
python test_automation.py --test full

Run only partial dump & restore test
python test_automation.py --test partial

-------------------------------------------
