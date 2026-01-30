# Database Investigation Summary

## Overview
This document summarizes the investigation of the `rawdataDec15` and `features` tables in the `mcda5580` MySQL database.

---

## 1. Schema Analysis

### rawdataDec15 Table
- **Total Rows**: 665,435
- **Columns**:
  - `id` (INTEGER, nullable) - Unique identifier for each record
  - `user_id` (INTEGER, nullable) - User identifier (3,159 unique users)
  - `milestone_name` (VARCHAR, nullable) - Name of the milestone/action (112 unique milestones)
  - `date` (DATE, not null) - Date of the event (151 distinct dates)
  - `time` (VARCHAR, not null) - Time of the event (84,628 unique timestamps)

### features Table
- **Total Rows**: 231,355
- **Columns**:
  - `id` (INTEGER, nullable) - Unique identifier for each record
  - `user_id` (INTEGER, nullable) - User identifier (1,744 unique users)
  - `milestone` (VARCHAR, nullable) - Name of the milestone/action (78 unique milestones)
  - `time` (VARCHAR, nullable) - Combined date/time (45,683 unique timestamps)

### Key Differences
1. **Column naming**: `milestone_name` vs `milestone`
2. **Date/Time format**: 
   - rawdataDec15: Separate `date` (DATE) and `time` (VARCHAR) columns
   - features: Combined `time` (VARCHAR) column in format "M/D/YYYY HH:MM"
3. **Data completeness**: rawdataDec15 has ~3x more records

---

## 2. Relationship Analysis

### User Coverage
- **rawdataDec15**: 3,159 unique users
- **features**: 1,744 unique users
- **Overlap**: All 1,744 users in features exist in rawdataDec15 (100% subset)

### Milestone Coverage
- **rawdataDec15**: 112 distinct milestones
- **features**: 78 distinct milestones
- **Common milestones**: 78 (all milestones in features exist in rawdataDec15)
- **Only in rawdataDec15**: 34 milestones (e.g., DeleteAccountSet, testTest, CrossMarketerCon, SaveAutoresponde, SaveCrossMarkete)

### ID Matching
- **Records with matching IDs**: 231,355 (100% of features table)
- **Conclusion**: The `features` table is a **perfect subset** of `rawdataDec15` based on ID matching

### Date Range
- **rawdataDec15**: 2015-07-20 to 2015-12-17 (151 distinct dates)
- **features**: 7/20/2015 18:34 to 9/9/2015 9:57
- **Observation**: features table covers a shorter time period (July-September vs July-December)

### Top Milestones

**rawdataDec15 (Top 10)**:
1. ProjPreview - 60,468
2. ManageTab - 43,652
3. CaptionedImages - 37,556
4. ReEditProj - 30,868
5. SendNow - 30,055
6. TxtFontSizeColor - 26,100
7. SEDragResize - 24,480
8. ReportsTab - 23,721
9. TxtBIUS - 20,561
10. InsertLinkAnchor - 20,338

**features (Top 10)**:
1. ProjPreview - 22,263
2. ManageTab - 15,872
3. CaptionedImages - 12,628
4. ReEditProj - 11,224
5. SendNow - 10,725
6. TxtFontSizeColor - 9,050
7. SEDragResize - 8,921
8. ReportsTab - 8,423
9. TxtBIUS - 7,091
10. InsertTableImage - 6,924

---

## 3. Join Strategies

### Strategy 1: JOIN ON ID (Exact Record Matching)
```sql
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
```
- **Result**: Perfect match for all 231,355 records in features
- **Use case**: When you need exact record-level correspondence

### Strategy 2: JOIN ON user_id AND milestone
```sql
SELECT 
    r.user_id,
    r.milestone_name,
    COUNT(*) as match_count
FROM mysql_db.rawdataDec15 r
INNER JOIN mysql_db.features f 
    ON r.user_id = f.user_id 
    AND r.milestone_name = f.milestone
GROUP BY r.user_id, r.milestone_name
```
- **Result**: 59,536,850 matches (many-to-many relationship)
- **Use case**: When analyzing user-milestone patterns across both tables

### Strategy 3: LEFT JOIN (Finding gaps)
```sql
SELECT 
    r.user_id,
    COUNT(DISTINCT r.milestone_name) as milestones_in_rawdata,
    COUNT(DISTINCT f.milestone) as milestones_in_features
FROM mysql_db.rawdataDec15 r
LEFT JOIN mysql_db.features f ON r.user_id = f.user_id
GROUP BY r.user_id
```
- **Use case**: Identifying users with data only in rawdataDec15

### Strategy 4: UNION ALL (Enriched Baskets)
```sql
WITH user_milestones AS (
    SELECT user_id, milestone_name as milestone, 'rawdata' as source
    FROM mysql_db.rawdataDec15
    UNION ALL
    SELECT user_id, milestone, 'features' as source
    FROM mysql_db.features
)
SELECT 
    user_id,
    list_distinct(list(milestone)) as all_milestones,
    COUNT(*) as total_events
FROM user_milestones
GROUP BY user_id
```
- **Use case**: Creating comprehensive user baskets combining both tables

### Strategy 5: Session-Level Baskets (Recommended for Association Rules)
```sql
SELECT 
    r.user_id,
    r.date,
    list_distinct(list(r.milestone_name)) as session_basket,
    COUNT(*) as events_in_session
FROM mysql_db.rawdataDec15 r
GROUP BY r.user_id, r.date
ORDER BY events_in_session DESC
```
- **Use case**: Association rule mining at session level
- **Advantage**: Uses the more complete rawdataDec15 table with proper date separation

---

## 4. Recommendations

### For Association Rule Mining:

1. **Primary Table**: Use `rawdataDec15` as your primary data source
   - More complete data (665K vs 231K rows)
   - Better date/time separation for session definition
   - Covers longer time period (July-December vs July-September)

2. **Session Definition**: Use `date` column to define sessions
   - Each user-date combination represents one session
   - Creates natural transaction boundaries for association rules

3. **Basket Creation**: Use DuckDB's `list_distinct()` function
   ```sql
   -- User-level baskets
   SELECT user_id, list_distinct(list(milestone_name)) as basket
   FROM mysql_db.rawdataDec15
   GROUP BY user_id
   
   -- Session-level baskets
   SELECT user_id, date, list_distinct(list(milestone_name)) as basket
   FROM mysql_db.rawdataDec15
   GROUP BY user_id, date
   ```

4. **When to Use features Table**:
   - Only if you need to focus on the July-September 2015 period
   - When you need the specific subset of users/milestones it contains
   - Generally, rawdataDec15 is more comprehensive

### Data Quality Notes:
- ✅ No NULL values in any table
- ✅ All IDs are unique within their respective tables
- ✅ Perfect subset relationship (features ⊂ rawdataDec15)
- ✅ Consistent milestone naming between tables

---

## 5. Example Session Baskets

Top session by activity (user 6232442 on 2015-11-09, 905 events):
```
[SendNow, EditDefaultStyle, SEBackColors, ProjPreview, SEDragMove, 
 ReEditProj, ImageProperties, PrevMobileVersio, SEPadding, 
 MultiImageProper, TxtFontSizeColor, TxtBIUS, UploadImage, 
 InsertTableImage, SEDeleteElement, SEDragIn, TxtIndentJustify, 
 TxtStylesFormats, TestSend, AddImage, InsertLinkAnchor, 
 CaptionedImages, ManageTab, SEBorders, SocialFollowElem, 
 ConditionalEleme, SEDragResize, MultiImageElemen]
```

This shows a very active user session with 28 distinct milestone types across 905 total events.

---

## Files Created

1. **investigation.py** - Initial schema and relationship exploration
2. **schema_analysis.py** - Detailed schema analysis with DESCRIBE and data quality checks
3. **relationship_analysis.py** - Comprehensive relationship analysis between tables
4. **join_examples.py** - Multiple join strategies with examples
5. **INVESTIGATION_SUMMARY.md** - This summary document

---

**Generated**: 2026-01-30
**Database**: mcda5580
**Tables Analyzed**: rawdataDec15, features
