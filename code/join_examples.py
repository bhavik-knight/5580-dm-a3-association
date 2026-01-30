"""
Join Query Examples
Demonstrates various ways to join rawdataDec15 and features tables
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
print("JOIN QUERY EXAMPLES")
print("=" * 80)

# Join Strategy 1: Join on ID (if they share the same ID space)
print("\n1. JOIN ON ID:")
print("-" * 80)
print("Query:")
join_on_id_query = """
    SELECT 
        r.id,
        r.user_id,
        r.milestone_name,
        r.date,
        r.time as rawdata_time,
        f.milestone as features_milestone,
        f.time as features_time
    FROM mysql_db.rawdataDec15 r
    INNER JOIN mysql_db.features f ON r.id = f.id
    LIMIT 10
"""
print(join_on_id_query)

try:
    result_id = con.execute(join_on_id_query).df()
    print(f"\nResult: {len(result_id)} rows")
    if len(result_id) > 0:
        print(result_id.to_string(index=False))
    else:
        print("No matching records found.")
except Exception as e:
    print(f"Error: {e}")

# Join Strategy 2: Join on user_id and milestone
print("\n" + "=" * 80)
print("\n2. JOIN ON user_id AND milestone:")
print("-" * 80)
print("Query:")
join_on_user_milestone_query = """
    SELECT 
        r.user_id,
        r.milestone_name,
        COUNT(*) as match_count,
        COUNT(DISTINCT r.date) as distinct_dates_in_rawdata,
        COUNT(DISTINCT f.time) as distinct_times_in_features
    FROM mysql_db.rawdataDec15 r
    INNER JOIN mysql_db.features f 
        ON r.user_id = f.user_id 
        AND r.milestone_name = f.milestone
    GROUP BY r.user_id, r.milestone_name
    ORDER BY match_count DESC
    LIMIT 10
"""
print(join_on_user_milestone_query)

try:
    result_user_milestone = con.execute(join_on_user_milestone_query).df()
    print(f"\nResult: {len(result_user_milestone)} rows")
    if len(result_user_milestone) > 0:
        print(result_user_milestone.to_string(index=False))
    else:
        print("No matching records found.")
except Exception as e:
    print(f"Error: {e}")

# Join Strategy 3: Left join to see what's in rawdata but not in features
print("\n" + "=" * 80)
print("\n3. LEFT JOIN (rawdata LEFT JOIN features on user_id):")
print("-" * 80)
print("Query:")
left_join_query = """
    SELECT 
        r.user_id,
        COUNT(DISTINCT r.milestone_name) as milestones_in_rawdata,
        COUNT(DISTINCT f.milestone) as milestones_in_features,
        COUNT(DISTINCT r.id) as total_rawdata_records,
        COUNT(DISTINCT f.id) as total_features_records
    FROM mysql_db.rawdataDec15 r
    LEFT JOIN mysql_db.features f ON r.user_id = f.user_id
    GROUP BY r.user_id
    ORDER BY total_rawdata_records DESC
    LIMIT 10
"""
print(left_join_query)

try:
    result_left = con.execute(left_join_query).df()
    print(f"\nResult: {len(result_left)} rows")
    if len(result_left) > 0:
        print(result_left.to_string(index=False))
except Exception as e:
    print(f"Error: {e}")

# Join Strategy 4: Enriching user baskets with features
print("\n" + "=" * 80)
print("\n4. ENRICHED USER BASKETS (combining both tables):")
print("-" * 80)
print("Query:")
enriched_baskets_query = """
    WITH user_milestones AS (
        SELECT 
            user_id,
            milestone_name as milestone,
            'rawdata' as source
        FROM mysql_db.rawdataDec15
        
        UNION ALL
        
        SELECT 
            user_id,
            milestone,
            'features' as source
        FROM mysql_db.features
    )
    SELECT 
        user_id,
        list_distinct(list(milestone)) as all_milestones,
        COUNT(*) as total_events,
        SUM(CASE WHEN source = 'rawdata' THEN 1 ELSE 0 END) as rawdata_events,
        SUM(CASE WHEN source = 'features' THEN 1 ELSE 0 END) as features_events
    FROM user_milestones
    GROUP BY user_id
    ORDER BY total_events DESC
    LIMIT 10
"""
print(enriched_baskets_query)

try:
    result_enriched = con.execute(enriched_baskets_query).df()
    print(f"\nResult: {len(result_enriched)} rows")
    if len(result_enriched) > 0:
        print(result_enriched.to_string(index=False))
except Exception as e:
    print(f"Error: {e}")

# Join Strategy 5: Session-level baskets with features
print("\n" + "=" * 80)
print("\n5. SESSION-LEVEL BASKETS (date-based from rawdata only):")
print("-" * 80)
print("Query:")
session_baskets_query = """
    SELECT 
        r.user_id,
        r.date,
        list_distinct(list(r.milestone_name)) as session_basket,
        COUNT(*) as events_in_session
    FROM mysql_db.rawdataDec15 r
    GROUP BY r.user_id, r.date
    ORDER BY events_in_session DESC
    LIMIT 10
"""
print(session_baskets_query)

try:
    result_session = con.execute(session_baskets_query).df()
    print(f"\nResult: {len(result_session)} rows")
    if len(result_session) > 0:
        print(result_session.to_string(index=False))
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS:")
print("=" * 80)
print("""
Based on the analysis, here are the recommended join strategies:

1. **If ID columns match**: Use JOIN ON id for exact record matching
   
2. **For user-level analysis**: Use JOIN ON user_id to combine user data
   
3. **For milestone analysis**: Use JOIN ON user_id AND milestone_name = milestone
   
4. **For basket analysis**: Consider using UNION ALL to combine both tables
   and create comprehensive user/session baskets
   
5. **For association rules**: Focus on rawdataDec15 table which has more
   complete data (665K rows vs 231K rows) and includes date information
   for session-level analysis
""")

print("\n" + "=" * 80)
print("Join examples complete!")
print("=" * 80)

con.close()
