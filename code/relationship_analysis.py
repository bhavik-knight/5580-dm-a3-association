"""
Table Relationship Analysis
Analyzes the relationship between rawdataDec15 and features tables
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
print("TABLE RELATIONSHIP ANALYSIS")
print("=" * 80)

# 1. Check if features is a subset of rawdataDec15
print("\n1. Checking if features table is a subset of rawdataDec15:")
print("-" * 80)

# Get unique users in each table
users_rawdata = con.execute("SELECT COUNT(DISTINCT user_id) FROM mysql_db.rawdataDec15").fetchone()[0]
users_features = con.execute("SELECT COUNT(DISTINCT user_id) FROM mysql_db.features").fetchone()[0]

print(f"Unique users in rawdataDec15: {users_rawdata:,}")
print(f"Unique users in features:     {users_features:,}")

# Check if all feature users exist in rawdata
users_only_in_features = con.execute("""
    SELECT COUNT(DISTINCT f.user_id)
    FROM mysql_db.features f
    LEFT JOIN mysql_db.rawdataDec15 r ON f.user_id = r.user_id
    WHERE r.user_id IS NULL
""").fetchone()[0]

print(f"Users only in features (not in rawdata): {users_only_in_features:,}")

# 2. Check milestone name matching
print("\n2. Milestone name comparison:")
print("-" * 80)

# Get distinct milestones from each table
milestones_rawdata = con.execute("""
    SELECT DISTINCT milestone_name 
    FROM mysql_db.rawdataDec15 
    ORDER BY milestone_name
""").df()

milestones_features = con.execute("""
    SELECT DISTINCT milestone 
    FROM mysql_db.features 
    ORDER BY milestone
""").df()

print(f"Distinct milestones in rawdataDec15: {len(milestones_rawdata)}")
print(f"Distinct milestones in features:     {len(milestones_features)}")

# Check for exact matches
milestones_raw_set = set(milestones_rawdata['milestone_name'])
milestones_feat_set = set(milestones_features['milestone'])

common_milestones = milestones_raw_set.intersection(milestones_feat_set)
only_in_rawdata = milestones_raw_set - milestones_feat_set
only_in_features = milestones_feat_set - milestones_raw_set

print(f"\nCommon milestones: {len(common_milestones)}")
print(f"Only in rawdataDec15: {len(only_in_rawdata)}")
print(f"Only in features: {len(only_in_features)}")

if only_in_rawdata:
    print(f"\nSample milestones only in rawdataDec15 (first 5):")
    for m in list(only_in_rawdata)[:5]:
        print(f"  - {m}")

if only_in_features:
    print(f"\nSample milestones only in features (first 5):")
    for m in list(only_in_features)[:5]:
        print(f"  - {m}")

# 3. Time/Date comparison
print("\n3. Time/Date format comparison:")
print("-" * 80)

sample_rawdata = con.execute("""
    SELECT user_id, milestone_name, date, time 
    FROM mysql_db.rawdataDec15 
    LIMIT 5
""").df()

sample_features = con.execute("""
    SELECT user_id, milestone, time 
    FROM mysql_db.features 
    LIMIT 5
""").df()

print("\nrawdataDec15 sample:")
print(sample_rawdata.to_string(index=False))

print("\nfeatures sample:")
print(sample_features.to_string(index=False))

# 4. Check if we can match records between tables
print("\n4. Attempting to match records between tables:")
print("-" * 80)

# Try matching on user_id and milestone
match_query = """
    SELECT 
        COUNT(*) as total_features,
        SUM(CASE WHEN r.user_id IS NOT NULL THEN 1 ELSE 0 END) as matched_on_user_milestone
    FROM mysql_db.features f
    LEFT JOIN mysql_db.rawdataDec15 r 
        ON f.user_id = r.user_id 
        AND f.milestone = r.milestone_name
"""

match_results = con.execute(match_query).df()
print(match_results.to_string(index=False))

# 5. Check ID relationship
print("\n5. ID column analysis:")
print("-" * 80)

# Check if IDs overlap
id_overlap = con.execute("""
    SELECT COUNT(*) as overlapping_ids
    FROM mysql_db.features f
    INNER JOIN mysql_db.rawdataDec15 r ON f.id = r.id
""").fetchone()[0]

print(f"Records with matching IDs: {id_overlap:,}")

# Sample matching IDs
if id_overlap > 0:
    print("\nSample records with matching IDs:")
    matching_sample = con.execute("""
        SELECT 
            f.id, 
            f.user_id as f_user_id, 
            r.user_id as r_user_id,
            f.milestone as f_milestone,
            r.milestone_name as r_milestone_name,
            f.time as f_time,
            r.date as r_date,
            r.time as r_time
        FROM mysql_db.features f
        INNER JOIN mysql_db.rawdataDec15 r ON f.id = r.id
        LIMIT 5
    """).df()
    print(matching_sample.to_string(index=False))

# 6. Date range comparison
print("\n6. Date range comparison:")
print("-" * 80)

rawdata_date_range = con.execute("""
    SELECT 
        MIN(date) as min_date, 
        MAX(date) as max_date,
        COUNT(DISTINCT date) as distinct_dates
    FROM mysql_db.rawdataDec15
""").df()

print("\nrawdataDec15 date range:")
print(rawdata_date_range.to_string(index=False))

# For features, try to extract date from time column
features_time_range = con.execute("""
    SELECT 
        MIN(time) as min_time, 
        MAX(time) as max_time
    FROM mysql_db.features
""").df()

print("\nfeatures time range:")
print(features_time_range.to_string(index=False))

print("\n" + "=" * 80)
print("Relationship analysis complete!")
print("=" * 80)

con.close()
