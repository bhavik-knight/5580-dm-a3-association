"""
Quick Reference: Association Rule Mining Queries
Ready-to-use queries for your association rule mining project
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
print("ASSOCIATION RULE MINING - QUICK REFERENCE QUERIES")
print("=" * 80)

# Query 1: User-Level Baskets (for user behavior patterns)
print("\n1. USER-LEVEL BASKETS")
print("-" * 80)
user_baskets_query = """
SELECT 
    user_id,
    list_distinct(list(milestone_name)) as basket,
    COUNT(*) as total_events,
    COUNT(DISTINCT milestone_name) as unique_milestones,
    COUNT(DISTINCT date) as active_days
FROM mysql_db.rawdataDec15
GROUP BY user_id
ORDER BY total_events DESC
"""

df_user_baskets = con.execute(user_baskets_query).df()
print(f"Generated {len(df_user_baskets):,} user baskets")
print("\nSample (top 5 users by activity):")
print(df_user_baskets.head().to_string(index=False))

# Query 2: Session-Level Baskets (for daily behavior patterns)
print("\n" + "=" * 80)
print("\n2. SESSION-LEVEL BASKETS (User + Date)")
print("-" * 80)
session_baskets_query = """
SELECT 
    user_id,
    date,
    list_distinct(list(milestone_name)) as basket,
    COUNT(*) as events_in_session,
    COUNT(DISTINCT milestone_name) as unique_milestones
FROM mysql_db.rawdataDec15
GROUP BY user_id, date
ORDER BY events_in_session DESC
"""

df_session_baskets = con.execute(session_baskets_query).df()
print(f"Generated {len(df_session_baskets):,} session baskets")
print("\nSample (top 5 sessions by activity):")
print(df_session_baskets.head().to_string(index=False))

# Query 3: Filtered Baskets (minimum support threshold)
print("\n" + "=" * 80)
print("\n3. FILTERED SESSION BASKETS (min 5 events per session)")
print("-" * 80)
filtered_baskets_query = """
SELECT 
    user_id,
    date,
    list_distinct(list(milestone_name)) as basket,
    COUNT(*) as events_in_session,
    COUNT(DISTINCT milestone_name) as unique_milestones
FROM mysql_db.rawdataDec15
GROUP BY user_id, date
HAVING COUNT(*) >= 5
ORDER BY events_in_session DESC
"""

df_filtered_baskets = con.execute(filtered_baskets_query).df()
print(f"Generated {len(df_filtered_baskets):,} filtered session baskets")
print(f"Filtered out {len(df_session_baskets) - len(df_filtered_baskets):,} sessions with < 5 events")
print("\nSample (top 5):")
print(df_filtered_baskets.head().to_string(index=False))

# Query 4: Milestone Co-occurrence Matrix (for initial pattern discovery)
print("\n" + "=" * 80)
print("\n4. MILESTONE CO-OCCURRENCE (top pairs)")
print("-" * 80)
cooccurrence_query = """
WITH session_milestones AS (
    SELECT 
        user_id,
        date,
        milestone_name
    FROM mysql_db.rawdataDec15
)
SELECT 
    a.milestone_name as milestone_1,
    b.milestone_name as milestone_2,
    COUNT(DISTINCT a.user_id || '_' || a.date) as sessions_together,
    COUNT(DISTINCT a.user_id) as users_together
FROM session_milestones a
JOIN session_milestones b 
    ON a.user_id = b.user_id 
    AND a.date = b.date 
    AND a.milestone_name < b.milestone_name
GROUP BY a.milestone_name, b.milestone_name
ORDER BY sessions_together DESC
LIMIT 20
"""

df_cooccurrence = con.execute(cooccurrence_query).df()
print(f"Top 20 milestone pairs by co-occurrence:")
print(df_cooccurrence.to_string(index=False))

# Query 5: Export baskets for mlxtend or other libraries
print("\n" + "=" * 80)
print("\n5. EXPORT-READY FORMAT (for mlxtend)")
print("-" * 80)

# Create a one-hot encoded format
export_query = """
WITH session_baskets AS (
    SELECT 
        ROW_NUMBER() OVER () as transaction_id,
        user_id,
        date,
        milestone_name
    FROM mysql_db.rawdataDec15
)
SELECT 
    transaction_id,
    user_id,
    date,
    milestone_name
FROM session_baskets
ORDER BY transaction_id, milestone_name
LIMIT 100
"""

df_export = con.execute(export_query).df()
print("Sample export format (first 100 records):")
print(df_export.head(20).to_string(index=False))

# Create one-hot encoded version
print("\nConverting to one-hot encoded format...")
basket_df = df_export.groupby(['transaction_id', 'milestone_name'])['milestone_name'].count().unstack(fill_value=0)
basket_df = (basket_df > 0).astype(int)
print(f"\nOne-hot encoded shape: {basket_df.shape}")
print("Sample (first 5 transactions, first 10 milestones):")
print(basket_df.iloc[:5, :10].to_string())

# Query 6: Statistics for parameter tuning
print("\n" + "=" * 80)
print("\n6. STATISTICS FOR PARAMETER TUNING")
print("-" * 80)

stats_query = """
WITH session_stats AS (
    SELECT 
        user_id,
        date,
        COUNT(*) as events,
        COUNT(DISTINCT milestone_name) as unique_milestones
    FROM mysql_db.rawdataDec15
    GROUP BY user_id, date
)
SELECT 
    COUNT(*) as total_sessions,
    AVG(events) as avg_events_per_session,
    MIN(events) as min_events,
    MAX(events) as max_events,
    AVG(unique_milestones) as avg_unique_milestones,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY events) as q1_events,
    PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY events) as median_events,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY events) as q3_events
FROM session_stats
"""

df_stats = con.execute(stats_query).df()
print("Session statistics:")
for col in df_stats.columns:
    print(f"  {col:30} {df_stats[col].iloc[0]:,.2f}")

print("\n" + "=" * 80)
print("RECOMMENDATIONS FOR ASSOCIATION RULE MINING:")
print("=" * 80)
print("""
Based on the statistics above:

1. **Minimum Support**: Start with 0.01-0.05 (1-5% of sessions)
   - Adjust based on total_sessions count

2. **Minimum Confidence**: Start with 0.5-0.7 (50-70%)
   - Higher confidence = stronger rules

3. **Session Filtering**: Consider filtering sessions with:
   - Minimum events: Use Q1 or median as threshold
   - Minimum unique milestones: At least 2-3 for meaningful patterns

4. **Basket Level**: 
   - Use SESSION-level for temporal patterns (recommended)
   - Use USER-level for overall user behavior patterns

5. **Libraries to use**:
   - mlxtend.frequent_patterns.apriori
   - mlxtend.frequent_patterns.association_rules
   - Or implement custom Apriori/FP-Growth

6. **Next Steps**:
   a. Export session baskets to CSV
   b. Convert to one-hot encoded format
   c. Run Apriori algorithm
   d. Generate association rules
   e. Filter and interpret results
""")

print("\n" + "=" * 80)
print("Quick reference complete!")
print("=" * 80)

con.close()
