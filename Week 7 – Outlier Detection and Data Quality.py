"""
=====================================================================
IDX Exchange Data Analyst Internship - Week 7
Script: week7_listings.py
Purpose: Statistical Outlier Detection & Data Quality (Listings Pipeline)

---------------------------------------------------------------------
EXECUTION RESULTS LOG
---------------------------------------------------------------------
--- [STEP 1] BASELINE AUDIT ---
Loaded File: /Users/samikshadubey/Downloads/IDX Code/Files/listings_engineered.csv
Initial Rows: 591,472 | Initial Columns: 87

--- [STEP 2] TARGET COLUMNS FOR IQR OUTLIER DETECTION ---
Analyzing: ['ListPrice', 'LivingArea', 'DaysOnMarket']

--- [STEP 3] CALCULATING IQR BOUNDS & ADDING FLAGS ---
[ListPrice] Q1: 582,990.00 | Q3: 1,385,000.00 | IQR: 802,010.00
       Lower Bound: -620,025.00 | Upper Bound: 2,588,015.00
       Flagged Outliers: 49,711 rows

[LivingArea] Q1: 1,248.00 | Q3: 2,303.00 | IQR: 1,055.00
       Lower Bound: -334.50 | Upper Bound: 3,885.50
       Flagged Outliers: 29,213 rows

[DaysOnMarket] Q1: 5.00 | Q3: 21.00 | IQR: 16.00
       Lower Bound: -19.00 | Upper Bound: 45.00
       Flagged Outliers: 49,123 rows

Total Rows Flagged as Outlier in ANY Category: 101,720

--- [STEP 4] EXPORT STATUS ---
Full Flagged Dataset Saved: /Users/samikshadubey/Downloads/IDX Code/Files/listings_flagged.csv
Clean Filtered Dataset Saved: /Users/samikshadubey/Downloads/IDX Code/Files/listings_outliers_removed.csv

--- [STEP 5] BEFORE VS. AFTER METRIC COMPARISON ---
Row Count: Before = 591,472 | After = 489,752 | Removed = 101,720 (17.20%)

Median Values Comparison:
  ListPrice: Before = 849,000.00 | After = 798,050.00
  LivingArea: Before = 1,672.00 | After = 1,586.00
  DaysOnMarket: Before = 11.00 | After = 9.00
=====================================================================
"""

import pandas as pd
import numpy as np

# =====================================================================
# STEP 1: LOAD DATASET & LOG BASELINE COUNTS
# =====================================================================
input_path = "/Users/samikshadubey/Downloads/IDX Code/Files/listings_engineered.csv"
output_flagged_path = "/Users/samikshadubey/Downloads/IDX Code/Files/listings_flagged.csv"
output_clean_path = "/Users/samikshadubey/Downloads/IDX Code/Files/listings_outliers_removed.csv"

try:
    df = pd.read_csv(input_path, low_memory=False)
except FileNotFoundError:
    input_path = "/Users/samikshadubey/Downloads/IDX Code/Files/listings_cleaned.csv"
    df = pd.read_csv(input_path, low_memory=False)

before_rows, before_cols = df.shape
print(f"--- [STEP 1] BASELINE AUDIT ---")
print(f"Loaded File: {input_path}")
print(f"Initial Rows: {before_rows:,} | Initial Columns: {before_cols}\n")

# =====================================================================
# STEP 2: DEFINE NUMERIC FIELDS FOR IQR OUTLIER CHECKS
# =====================================================================
target_cols = ['ListPrice', 'LivingArea', 'DaysOnMarket']
target_cols = [col for col in target_cols if col in df.columns]

print(f"--- [STEP 2] TARGET COLUMNS FOR IQR OUTLIER DETECTION ---")
print(f"Analyzing: {target_cols}\n")

# =====================================================================
# STEP 3: CALCULATE IQR BOUNDARIES AND ADD OUTLIER FLAGS
# =====================================================================
print(f"--- [STEP 3] CALCULATING IQR BOUNDS & ADDING FLAGS ---")

outlier_flag_cols = []

for col in target_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    flag_col = f"outlier_{col}"
    outlier_flag_cols.append(flag_col)
    
    df[flag_col] = (df[col] < lower_bound) | (df[col] > upper_bound)
    
    print(f"[{col}] Q1: {Q1:,.2f} | Q3: {Q3:,.2f} | IQR: {IQR:,.2f}")
    print(f"       Lower Bound: {lower_bound:,.2f} | Upper Bound: {upper_bound:,.2f}")
    print(f"       Flagged Outliers: {df[flag_col].sum():,} rows\n")

df['is_outlier_any'] = df[outlier_flag_cols].any(axis=1)
print(f"Total Rows Flagged as Outlier in ANY Category: {df['is_outlier_any'].sum():,}\n")

# =====================================================================
# STEP 4: CREATE FILTERED DATASET & EXPORT TWO CSV FILES
# =====================================================================
df.to_csv(output_flagged_path, index=False)

df_clean = df[df['is_outlier_any'] == False].copy()
df_clean.to_csv(output_clean_path, index=False)

after_rows, after_cols = df_clean.shape
print(f"--- [STEP 4] EXPORT STATUS ---")
print(f"Full Flagged Dataset Saved: {output_flagged_path}")
print(f"Clean Filtered Dataset Saved: {output_clean_path}\n")

# =====================================================================
# STEP 5: COMPARISON LEDGER (BEFORE VS. AFTER FILTERING)
# =====================================================================
print(f"--- [STEP 5] BEFORE VS. AFTER METRIC COMPARISON ---")
print(f"Row Count: Before = {before_rows:,} | After = {after_rows:,} | Removed = {before_rows - after_rows:,} ({(before_rows - after_rows)/before_rows*100:.2f}%)")

print("\nMedian Values Comparison:")
for col in target_cols:
    med_before = df[col].median()
    med_after = df_clean[col].median()
    print(f"  {col}: Before = {med_before:,.2f} | After = {med_after:,.2f}")











"""
=====================================================================
IDX Exchange Data Analyst Internship - Week 7
Script: week7_sold.py
Purpose: Statistical Outlier Detection & Data Quality (Sold Pipeline)

---------------------------------------------------------------------
EXECUTION RESULTS LOG
---------------------------------------------------------------------
--- [STEP 1] BASELINE AUDIT ---
Loaded File: /Users/samikshadubey/Downloads/IDX Code/Files/sold_engineered.csv
Initial Rows: 430,234 | Initial Columns: 88

--- [STEP 2] TARGET COLUMNS FOR IQR OUTLIER DETECTION ---
Analyzing: ['ClosePrice', 'LivingArea', 'DaysOnMarket']

--- [STEP 3] CALCULATING IQR BOUNDS & ADDING FLAGS ---
[ClosePrice] Q1: 575,000.00 | Q3: 1,300,000.00 | IQR: 725,000.00
       Lower Bound: -512,500.00 | Upper Bound: 2,387,500.00
       Flagged Outliers: 32,052 rows

[LivingArea] Q1: 1,248.00 | Q3: 2,222.00 | IQR: 974.00
       Lower Bound: -213.00 | Upper Bound: 3,683.00
       Flagged Outliers: 18,845 rows

[DaysOnMarket] Q1: 8.00 | Q3: 48.00 | IQR: 40.00
       Lower Bound: -52.00 | Upper Bound: 108.00
       Flagged Outliers: 32,960 rows

Total Rows Flagged as Outlier in ANY Category: 67,580

--- [STEP 4] EXPORT STATUS ---
Full Flagged Dataset Saved: /Users/samikshadubey/Downloads/IDX Code/Files/sold_flagged.csv
Clean Filtered Dataset Saved: /Users/samikshadubey/Downloads/IDX Code/Files/sold_outliers_removed.csv

--- [STEP 5] BEFORE VS. AFTER METRIC COMPARISON ---
Row Count: Before = 430,234 | After = 362,654 | Removed = 67,580 (15.71%)

Median Values Comparison:
  ClosePrice: Before = 825,000.00 | After = 785,000.00
  LivingArea: Before = 1,645.00 | After = 1,570.00
  DaysOnMarket: Before = 18.00 | After = 16.00
=====================================================================
"""

import pandas as pd
import numpy as np

# =====================================================================
# STEP 1: LOAD DATASET & LOG BASELINE COUNTS
# =====================================================================
input_path = "/Users/samikshadubey/Downloads/IDX Code/Files/sold_engineered.csv"
output_flagged_path = "/Users/samikshadubey/Downloads/IDX Code/Files/sold_flagged.csv"
output_clean_path = "/Users/samikshadubey/Downloads/IDX Code/Files/sold_outliers_removed.csv"

try:
    df = pd.read_csv(input_path, low_memory=False)
except FileNotFoundError:
    input_path = "/Users/samikshadubey/Downloads/IDX Code/Files/sold_cleaned.csv"
    df = pd.read_csv(input_path, low_memory=False)

before_rows, before_cols = df.shape
print(f"--- [STEP 1] BASELINE AUDIT ---")
print(f"Loaded File: {input_path}")
print(f"Initial Rows: {before_rows:,} | Initial Columns: {before_cols}\n")

# =====================================================================
# STEP 2: DEFINE NUMERIC FIELDS FOR IQR OUTLIER CHECKS
# =====================================================================
target_cols = ['ClosePrice', 'LivingArea', 'DaysOnMarket']
target_cols = [col for col in target_cols if col in df.columns]

print(f"--- [STEP 2] TARGET COLUMNS FOR IQR OUTLIER DETECTION ---")
print(f"Analyzing: {target_cols}\n")

# =====================================================================
# STEP 3: CALCULATE IQR BOUNDARIES AND ADD OUTLIER FLAGS
# =====================================================================
print(f"--- [STEP 3] CALCULATING IQR BOUNDS & ADDING FLAGS ---")

outlier_flag_cols = []

for col in target_cols:
    Q1 = df[col].quantile(0.25)
    Q3 = df[col].quantile(0.75)
    IQR = Q3 - Q1
    
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    
    flag_col = f"outlier_{col}"
    outlier_flag_cols.append(flag_col)
    
    df[flag_col] = (df[col] < lower_bound) | (df[col] > upper_bound)
    
    print(f"[{col}] Q1: {Q1:,.2f} | Q3: {Q3:,.2f} | IQR: {IQR:,.2f}")
    print(f"       Lower Bound: {lower_bound:,.2f} | Upper Bound: {upper_bound:,.2f}")
    print(f"       Flagged Outliers: {df[flag_col].sum():,} rows\n")

df['is_outlier_any'] = df[outlier_flag_cols].any(axis=1)
print(f"Total Rows Flagged as Outlier in ANY Category: {df['is_outlier_any'].sum():,}\n")

# =====================================================================
# STEP 4: CREATE FILTERED DATASET & EXPORT TWO CSV FILES
# =====================================================================
df.to_csv(output_flagged_path, index=False)

df_clean = df[df['is_outlier_any'] == False].copy()
df_clean.to_csv(output_clean_path, index=False)

after_rows, after_cols = df_clean.shape
print(f"--- [STEP 4] EXPORT STATUS ---")
print(f"Full Flagged Dataset Saved: {output_flagged_path}")
print(f"Clean Filtered Dataset Saved: {output_clean_path}\n")

# =====================================================================
# STEP 5: COMPARISON LEDGER (BEFORE VS. AFTER FILTERING)
# =====================================================================
print(f"--- [STEP 5] BEFORE VS. AFTER METRIC COMPARISON ---")
print(f"Row Count: Before = {before_rows:,} | After = {after_rows:,} | Removed = {before_rows - after_rows:,} ({(before_rows - after_rows)/before_rows*100:.2f}%)")

print("\nMedian Values Comparison:")
for col in target_cols:
    med_before = df[col].median()
    med_after = df_clean[col].median()
    print(f"  {col}: Before = {med_before:,.2f} | After = {med_after:,.2f}")
