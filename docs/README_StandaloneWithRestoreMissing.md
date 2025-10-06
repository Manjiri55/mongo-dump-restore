# MongoDB Dump & Restore Utility

**Script:** `dumpRestoreStandaloneWithRestoreMissingDocs.py`

This Python utility provides flexible backup (dump) and restore operations for MongoDB databases — with advanced features like timestamped dumps, granular collection selection, and document-level restore (`restoreMissing`).
This is an improved version of the first version (dump_restore_standalone.py)

---

## Project Structure
```
project/
├── dumpRestoreStandaloneWithRestoreMissingDocs.py # Main script
├── config.cfg # Configuration file
├── docs/
│   └── README_StandaloneWithRestoreMissing.md 
└── README.md # This file

```
---

## Features

- Dump entire MongoDB instance or selected DBs/collections  
- Restore entire DBs, specific collections, or only missing documents  
- Automatically creates timestamped backup directories  
- Prevents accidental multi-restore from parent directory  
- Supports config + CLI overrides for all parameters  
- Seamless integration with MongoDB command-line tools

## Enhancements and improvements to the first version (dump_restore_standalone.py)

1. Configuration (via .cfg file or CLI):

The script allows you to specify various MongoDB connection details like the database host, port, username, password, and authentication database either from a configuration file (.cfg) or via command-line arguments.
This makes it flexible and customizable to run on different environments with different connection parameters.

2. Restore Missing Documents (--restoreMissing):

This functionality is useful when you only want to restore missing documents (i.e., documents that don’t exist in the target MongoDB collections).
The script performs the following steps:
Walks through the BSON backup files and converts them into JSON format using bsondump.
Checks the existing documents in the target MongoDB collection.
Inserts only the missing documents (those not already present in the collection).
This ensures that existing data isn’t overwritten, and only new documents are restored.

3. Additional Features:

Timestamped Dump Folders: When dumping data, it creates a subfolder named dump_YYYY_MM_DD_HH_MM_SS (based on the current timestamp) to store the dump files, which helps with organizing and differentiating backups.
Handling Multiple Databases and Collections: You can specify multiple databases and collections either in the configuration file or through CLI arguments. For example, you can back up testdb1:orders,users while excluding others.
Error Handling: The script performs validation checks, such as ensuring there are no conflicting dump directories during restore and verifying that the correct paths are provided.

4. Command-Line Arguments:

--dump: Run a backup of specified database(s)/collection(s).
--restore: Restore a backup to the MongoDB instance.
--restoreMissing: Only restore missing documents from a previous backup, preventing overwriting of existing data.
--latest: Use the most recently modified dump directory for restore operations.
--db: Specify which databases or collections to include/exclude in the dump or restore operation.
--all: Include all databases for the dump or restore operations.

5. Dump Operation (--dump):

When the --dump flag is provided, the script runs mongodump to back up the database(s) or collection(s) to a specified directory (with a timestamped subfolder).
You can select which collections to back up by specifying them with the --db argument.
If no specific collections are given, the entire database will be dumped.
The backup command is generated dynamically and includes:
Host, port, username, password, authentication database, and collections (if specified).
The backup is stored in a subdirectory with a timestamp to organize dumps.

6. Restore Operation (--restore):

When the --restore flag is used, it triggers the mongorestore operation, which restores a MongoDB backup from a specified directory.
The script ensures that the restore operation only applies to the desired databases and collections, based on the specified arguments.
It has an option to use the latest dump if the --latest flag is passed, in which case it automatically selects the most recently modified dump directory.


---

## Configuration File — `config.cfg`

Example:

```ini
[database]
host = localhost
port = 27017
username = admin
password = secret
auth_db = admin

[backup]
dump_path = /home/manjiri/dump
restore_path = /home/manjiri/dump

```

## Notes:

dump_path: Base directory for all new timestamped dumps

restore_path: Base or specific directory to restore from

Use --latest to automatically select the most recent dump

If multiple dumps exist and --latest is not provided, a warning prevents restoring from all

## Command-Line Overview

```
python dumpRestoreStandaloneWithRestoreMissingDocs.py config.cfg [options]
```

## General Options

| Flag               | Description                                                      |
| ------------------ | ---------------------------------------------------------------- |
| `--dump`           | Run `mongodump` (creates timestamped backup folder)              |
| `--restore`        | Run `mongorestore`                                               |
| `--restoreMissing` | Restore only missing documents from dump                         |
| `--latest`         | Use the latest timestamped dump for restore                      |
| `--all`            | Include all databases                                            |
| `--db`             | Specify databases/collections (e.g. `--db testdb1:users,orders`) |


## Database Connection & Path Overrides
All parameters in config.cfg can be overridden from the command line:

| CLI Flag        | Overrides Config Key    | Example                                              |
| --------------- | ----------------------- | ---------------------------------------------------- |
| `--host`        | `[database] host`       | `--host mymongo`                                     |
| `--port`        | `[database] port`       | `--port 28017`                                       |
| `--username`    | `[database] username`   | `--username admin`                                   |
| `--password`    | `[database] password`   | `--password secret`                                  |
| `--authdb`      | `[database] auth_db`    | `--authdb admin`                                     |
| `--dumpPath`    | `[backup] dump_path`    | `--dumpPath /data/dumps`                             |
| `--restorePath` | `[backup] restore_path` | `--restorePath /data/dumps/dump_2025_10_04_09_15_32` |


## Usage Examples

1. Full dump of all databases
```
python dumpRestoreStandaloneWithRestoreMissingDocs.py config.cfg --dump --all
```
Creates /home/manjiri/dump/dump_YYYY_MM_DD_HH_MM_SS/

2. Dump a specific database
```
python dumpRestoreStandaloneWithRestoreMissingDocs.py config.cfg --dump --db testdb1
```

3. Dump selected collections
```
python dumpRestoreStandaloneWithRestoreMissingDocs.py config.cfg --dump --db testdb1:users,orders
```

4. Restore from the latest dump
```
python dumpRestoreStandaloneWithRestoreMissingDocs.py config.cfg --restore --latest
```

5. Restore only one collection
```
python dumpRestoreStandaloneWithRestoreMissingDocs.py config.cfg --restore --latest --db testdb1:orders
```

6. Restore only missing documents

Restore accidentally deleted documents without overwriting new ones:
```
python dumpRestoreStandaloneWithRestoreMissingDocs.py config.cfg --restoreMissing --latest --db testdb1:orders
```

7. Restore from a specific dump

Edit your config file:

```
restore_path = /home/manjiri/dump/dump_2025_10_01_07_30_00
```
Then run:

```
python dumpRestoreStandaloneWithRestoreMissingDocs.py config.cfg --restore --db testdb1:orders
```
8. Validation safeguard

If you set:

```
restore_path = /home/manjiri/dump
```

and run without --latest:
```
python dumpRestoreStandaloneWithRestoreMissingDocs.py config.cfg --restore --db testdb1:orders
```
you’ll get:
```
The restore path '/home/manjiri/dump' contains multiple dump directories:
   dump_2025_10_04_09_15_32, dump_2025_09_28_08_00_00
Please specify a specific dump subfolder or use --latest.
```
## Timestamped Dump Folders

Each dump automatically creates a folder:
```
dump_YYYY_MM_DD_HH_MM_SS
```

Example:

```
/home/manjiri/dump/dump_2025_10_04_09_15_32/testdb1/orders.bson
```
This prevents overwriting previous backups and simplifies version tracking.

## Cleanup (optional)

You can safely delete old backups:

```
rm -rf /home/manjiri/dump/dump_2025_09_28_*
```

## Common Test Commands

| Purpose                       | Command                                         |
| ----------------------------- | ----------------------------------------------- |
| Full dump                     | `--dump --all`                                  |
| Dump one DB                   | `--dump --db testdb1`                           |
| Dump specific collections     | `--dump --db testdb1:users,orders`              |
| Restore latest                | `--restore --latest`                            |
| Restore specific              | `--restore --restorePath /path/to/dump_folder`  |
| RestoreMissing latest         | `--restoreMissing --latest`                     |
| RestoreMissing one collection | `--restoreMissing --latest --db testdb1:orders` |


## Requirements

Python 3.7+

## MongoDB tools installed (mongodump, mongorestore, bsondump)
```
mongodump --version
mongorestore --version
bsondump --version
```

## Python dependencies:
```
pip install pymongo
```
## Example Workflow

1. Populate sample data

2. Run --dump --all to create backup

3. Accidentally delete some records

4. Run --restoreMissing --latest to restore deleted ones

5. Repeat weekly — timestamped folders prevent overwrites


## Error Handling

| Scenario                                               | Behavior                                                  |
| ------------------------------------------------------ | --------------------------------------------------------- |
| Multiple dumps under `restore_path` without `--latest` | Script aborts with clear warning                          |
| Invalid credentials                                    | MongoDB authentication error                              |
| Missing bsondump/mongodump                             | Python `FileNotFoundError` (ensure MongoDB tools in PATH) |
| Empty restore folder                                   | Graceful “no files found” error                           |


