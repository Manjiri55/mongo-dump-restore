
## MongoDB Dump & Restore Utility

1. Scripts: dump_restore_standalone.py,
            dump_restore_replicaset.py

This project provides Python scripts to backup (dump) and restore MongoDB databases and collections using the official **mongodump** and **mongorestore** tools.  
It supports both **standalone MongoDB instances** and **replica sets** (with optional oplog support for consistent cluster-wide backups).

More details about this script are provided in the document at the path below:
```
├── docs/
│   ├── README_StandaloneReplicaSet.md
```

2. Script: dumpRestoreStandaloneWithRestoreMissingDocs.py

This Python utility provides flexible backup (dump) and restore operations for MongoDB databases — with advanced features like timestamped dumps, granular collection selection, and document-level restore (restoreMissing).

More details about this script are provided in the document at the path below:
```
├── docs/ 
│   └── README_StandaloneWithRestoreMissing.md 
```
---

## Project Structure


```
project/

├── dump_restore_standalone.py # Dump/restore script for standalone MongoDb instance
├── dump_restore_replicaset.py # Dump/restore script for MongoDB is running as a replica set (with oplog support)
├── dumpRestoreStandaloneWithRestoreMissingDocs.py
├── populateMultipleDbsStandalone.py # Script to populate test data for dump_restore_standalone.py
├── populateMultipleDbsReplicaSet.py # Script to populate test data for dump_restore_replicaset.py
├── config.cfg # Configuration file (DB connection settings)
├── docs/
│   ├── README_StandaloneReplicaSet.md       
│   └── README_StandaloneWithRestoreMissing.md 
├── README.md # Project documentation
└── test_automation.py (This script tests the main dump_restore.py + populateMultipleDbs.py flow)
```
-------------------------------

