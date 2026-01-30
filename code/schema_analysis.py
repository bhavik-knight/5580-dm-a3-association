"""
Enhanced Schema Analysis
This script uses alternative methods to get detailed schema information
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
print("ENHANCED SCHEMA ANALYSIS")
print("=" * 80)

# Method 1: Use DESCRIBE directly on the attached tables
print("\n1. DESCRIBE rawdataDec15 (using DuckDB DESCRIBE):")
print("-" * 80)
try:
    rawdata_desc = con.execute("DESCRIBE mysql_db.rawdataDec15").df()
    print(rawdata_desc.to_string(index=False))
except Exception as e:
    print(f"Error: {e}")

print("\n2. DESCRIBE features (using DuckDB DESCRIBE):")
print("-" * 80)
try:
    features_desc = con.execute("DESCRIBE mysql_db.features").df()
    print(features_desc.to_string(index=False))
except Exception as e:
    print(f"Error: {e}")

# Method 2: Infer schema from actual data
print("\n3. Schema inferred from data (rawdataDec15):")
print("-" * 80)
sample_rawdata = con.execute("SELECT * FROM mysql_db.rawdataDec15 LIMIT 1").df()
for col in sample_rawdata.columns:
    dtype = sample_rawdata[col].dtype
    print(f"  {col:20} -> {dtype}")

print("\n4. Schema inferred from data (features):")
print("-" * 80)
sample_features = con.execute("SELECT * FROM mysql_db.features LIMIT 1").df()
for col in sample_features.columns:
    dtype = sample_features[col].dtype
    print(f"  {col:20} -> {dtype}")

# Method 3: Check for NULL values and unique counts
print("\n5. Data quality check - rawdataDec15:")
print("-" * 80)
for col in sample_rawdata.columns:
    null_count = con.execute(f"SELECT COUNT(*) FROM mysql_db.rawdataDec15 WHERE {col} IS NULL").fetchone()[0]
    unique_count = con.execute(f"SELECT COUNT(DISTINCT {col}) FROM mysql_db.rawdataDec15").fetchone()[0]
    total_count = con.execute(f"SELECT COUNT(*) FROM mysql_db.rawdataDec15").fetchone()[0]
    print(f"  {col:20} - Nulls: {null_count:8,} | Unique: {unique_count:8,} | Total: {total_count:8,}")

print("\n6. Data quality check - features:")
print("-" * 80)
for col in sample_features.columns:
    null_count = con.execute(f"SELECT COUNT(*) FROM mysql_db.features WHERE {col} IS NULL").fetchone()[0]
    unique_count = con.execute(f"SELECT COUNT(DISTINCT {col}) FROM mysql_db.features").fetchone()[0]
    total_count = con.execute(f"SELECT COUNT(*) FROM mysql_db.features").fetchone()[0]
    print(f"  {col:20} - Nulls: {null_count:8,} | Unique: {unique_count:8,} | Total: {total_count:8,}")

# Method 4: Check distinct values for key columns
print("\n7. Sample distinct values:")
print("-" * 80)
print("\nrawdataDec15 - milestone_name (top 10):")
milestone_counts = con.execute("""
    SELECT milestone_name, COUNT(*) as count 
    FROM mysql_db.rawdataDec15 
    GROUP BY milestone_name 
    ORDER BY count DESC 
    LIMIT 10
""").df()
print(milestone_counts.to_string(index=False))

print("\nfeatures - milestone (top 10):")
milestone_counts_features = con.execute("""
    SELECT milestone, COUNT(*) as count 
    FROM mysql_db.features 
    GROUP BY milestone 
    ORDER BY count DESC 
    LIMIT 10
""").df()
print(milestone_counts_features.to_string(index=False))

print("\n" + "=" * 80)
print("Schema analysis complete!")
print("=" * 80)

con.close()
