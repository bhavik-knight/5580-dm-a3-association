# Investigation Complete! 🎉

## Summary of Findings

### ✅ What We Discovered

#### 1. **Table Relationship**
- `features` table is a **100% subset** of `rawdataDec15`
- All 231,355 records in `features` have matching IDs in `rawdataDec15`
- All 1,744 users in `features` exist in `rawdataDec15`
- All 78 milestones in `features` exist in `rawdataDec15`

#### 2. **Schema Details**

**rawdataDec15** (Primary Table - RECOMMENDED)
```
├── id (INTEGER) - 665,435 unique records
├── user_id (INTEGER) - 3,159 unique users
├── milestone_name (VARCHAR) - 112 unique milestones
├── date (DATE) - 151 distinct dates (2015-07-20 to 2015-12-17)
└── time (VARCHAR) - 84,628 unique timestamps
```

**features** (Subset Table)
```
├── id (INTEGER) - 231,355 unique records
├── user_id (INTEGER) - 1,744 unique users
├── milestone (VARCHAR) - 78 unique milestones
└── time (VARCHAR) - 45,683 unique timestamps (7/20/2015 to 9/9/2015)
```

#### 3. **Key Statistics**

**Session Statistics** (from rawdataDec15):
- Total sessions: **24,713**
- Average events per session: **26.93**
- Median events per session: **11**
- Q1: 4 events | Q3: 30 events
- Average unique milestones per session: **7**

**Top Milestone Pairs** (Co-occurrence):
1. ManageTab + SendNow: 10,002 sessions
2. ManageTab + ProjPreview: 7,884 sessions
3. ManageTab + ReEditProj: 7,331 sessions
4. ProjPreview + SendNow: 6,947 sessions
5. ProjPreview + ReEditProj: 6,771 sessions

---

## 📁 Files Created

### Analysis Scripts
1. **`code/investigation.py`** - Initial exploration
2. **`code/schema_analysis.py`** - Detailed schema with DESCRIBE
3. **`code/relationship_analysis.py`** - Table relationship analysis
4. **`code/join_examples.py`** - Multiple join strategies
5. **`code/quick_reference.py`** - Ready-to-use queries for association mining

### Documentation
6. **`INVESTIGATION_SUMMARY.md`** - Comprehensive findings report
7. **`README_INVESTIGATION.md`** - This quick summary (you are here!)

---

## 🚀 Recommended Next Steps for Association Rule Mining

### Step 1: Choose Your Basket Level
```python
# Option A: User-Level Baskets (overall user behavior)
user_baskets = con.execute("""
    SELECT user_id, list_distinct(list(milestone_name)) as basket
    FROM mysql_db.rawdataDec15
    GROUP BY user_id
""").df()

# Option B: Session-Level Baskets (daily behavior - RECOMMENDED)
session_baskets = con.execute("""
    SELECT user_id, date, list_distinct(list(milestone_name)) as basket
    FROM mysql_db.rawdataDec15
    GROUP BY user_id, date
""").df()
```

### Step 2: Filter Low-Activity Sessions
```python
# Keep sessions with at least 5 events (median is 11)
filtered_sessions = con.execute("""
    SELECT user_id, date, list_distinct(list(milestone_name)) as basket
    FROM mysql_db.rawdataDec15
    GROUP BY user_id, date
    HAVING COUNT(*) >= 5
""").df()
```

### Step 3: Convert to One-Hot Encoded Format
```python
from mlxtend.preprocessing import TransactionEncoder

# Extract baskets as list of lists
baskets = filtered_sessions['basket'].tolist()

# One-hot encode
te = TransactionEncoder()
te_ary = te.fit(baskets).transform(baskets)
df_encoded = pd.DataFrame(te_ary, columns=te.columns_)
```

### Step 4: Run Apriori Algorithm
```python
from mlxtend.frequent_patterns import apriori, association_rules

# Find frequent itemsets
frequent_itemsets = apriori(df_encoded, min_support=0.01, use_colnames=True)

# Generate association rules
rules = association_rules(frequent_itemsets, metric="confidence", min_threshold=0.5)
```

### Step 5: Analyze Results
```python
# Sort by lift to find interesting patterns
rules_sorted = rules.sort_values('lift', ascending=False)

# Filter for strong rules
strong_rules = rules[
    (rules['support'] >= 0.02) & 
    (rules['confidence'] >= 0.6) & 
    (rules['lift'] > 1.5)
]
```

---

## 📊 Recommended Parameters

Based on the statistics:

| Parameter | Recommended Value | Reasoning |
|-----------|------------------|-----------|
| **min_support** | 0.01 - 0.05 | 1-5% of 24,713 sessions = 247-1,236 sessions |
| **min_confidence** | 0.5 - 0.7 | 50-70% for meaningful rules |
| **min_lift** | > 1.5 | Indicates positive correlation |
| **Session filter** | ≥ 5 events | Filters out 25% of low-activity sessions |
| **Basket level** | Session (user+date) | Better for temporal patterns |

---

## 💡 Key Insights

1. **Use `rawdataDec15` as your primary table** - it's more complete
2. **Session-level analysis is recommended** - better for discovering temporal patterns
3. **Filter sessions** - median is 11 events, consider filtering sessions with < 5 events
4. **Top milestones to watch**:
   - ProjPreview (60K occurrences)
   - ManageTab (44K occurrences)
   - CaptionedImages (38K occurrences)
5. **Strong co-occurrences** already visible:
   - ManageTab often appears with SendNow, ProjPreview, and ReEditProj

---

## 🔍 How to Join Tables (if needed)

### Perfect ID Match
```sql
-- All features records match rawdata by ID
SELECT r.*, f.time as features_time
FROM mysql_db.rawdataDec15 r
INNER JOIN mysql_db.features f ON r.id = f.id
```

### User-Level Join
```sql
-- Combine user data from both tables
SELECT r.user_id, r.milestone_name, f.milestone
FROM mysql_db.rawdataDec15 r
LEFT JOIN mysql_db.features f ON r.user_id = f.user_id
```

**But honestly**: You probably don't need to join them. Just use `rawdataDec15`! 🎯

---

## ✨ Quick Start Command

To run any of the analysis scripts:
```bash
uv run python code/investigation.py
uv run python code/schema_analysis.py
uv run python code/relationship_analysis.py
uv run python code/join_examples.py
uv run python code/quick_reference.py
```

---

**Investigation Date**: 2026-01-30  
**Database**: mcda5580  
**Tables**: rawdataDec15 (primary), features (subset)  
**Total Records Analyzed**: 665,435 events across 3,159 users
