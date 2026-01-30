"""
Schema Investigation Script
This script investigates the structure of rawdataDec15 and features tables
to understand their relationship and how to join them.
"""

import os
import duckdb
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Build the DuckDB-specific MySQL connection string
mysql_config = (
    f"host={os.getenv('DB_HOST')} "
    f"user={os.getenv('DB_USER')} "
    f"password={os.getenv('DB_PWD')} "
    f"database={os.getenv('DB_NAME')} "
    f"port={os.getenv('DB_PORT')}"
)

# Initialize DuckDB and attach MySQL
con = duckdb.connect()
con.execute("INSTALL mysql; LOAD mysql;")
con.execute(f"ATTACH '{mysql_config}' AS mysql_db (TYPE MYSQL);")

print("=" * 80)
print("INVESTIGATION: Schema and Relationship Analysis")
print("=" * 80)

# 1. Check schema of rawdataDec15
print("\n1. Schema of rawdataDec15:")
print("-" * 80)
rawdata_schema = con.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'mysql_db' 
    AND table_name = 'rawdataDec15'
    ORDER BY ordinal_position
""").df()
print(rawdata_schema.to_string(index=False))

# 2. Check schema of features
print("\n2. Schema of features:")
print("-" * 80)
features_schema = con.execute("""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_schema = 'mysql_db' 
    AND table_name = 'features'
    ORDER BY ordinal_position
""").df()
print(features_schema.to_string(index=False))

# 3. Preview the features table
print("\n3. Preview of features table (first 10 rows):")
print("-" * 80)
features_preview = con.execute("""
    SELECT * FROM mysql_db.features LIMIT 10
""").df()
print(features_preview.to_string(index=False))

# 4. Preview the rawdataDec15 table
print("\n4. Preview of rawdataDec15 table (first 10 rows):")
print("-" * 80)
rawdata_preview = con.execute("""
    SELECT * FROM mysql_db.rawdataDec15 LIMIT 10
""").df()
print(rawdata_preview.to_string(index=False))

# 5. Find common column names between the two tables
print("\n5. Common columns between rawdataDec15 and features:")
print("-" * 80)
rawdata_cols = set(rawdata_schema['column_name'].tolist())
features_cols = set(features_schema['column_name'].tolist())
common_cols = rawdata_cols.intersection(features_cols)
print(f"Common columns: {common_cols if common_cols else 'None found'}")

# 6. Check row counts
print("\n6. Row counts:")
print("-" * 80)
rawdata_count = con.execute("SELECT COUNT(*) as count FROM mysql_db.rawdataDec15").fetchone()[0]
features_count = con.execute("SELECT COUNT(*) as count FROM mysql_db.features").fetchone()[0]
print(f"rawdataDec15: {rawdata_count:,} rows")
print(f"features: {features_count:,} rows")

# 7. Check for potential join keys (user_id, session_id, milestone_id)
print("\n7. Checking for potential join keys:")
print("-" * 80)
potential_keys = ['user_id', 'session_id', 'milestone_id', 'date']
for key in potential_keys:
    in_rawdata = key in rawdata_cols
    in_features = key in features_cols
    print(f"{key:15} - rawdataDec15: {in_rawdata:5} | features: {in_features:5}")

print("\n" + "=" * 80)
print("Investigation complete!")
print("=" * 80)

# Close connection
con.close()
