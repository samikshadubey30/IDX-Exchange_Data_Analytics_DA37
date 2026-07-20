"""

IDX Exchange Data Analyst Internship
Script: data_cleaning_listings.py
Purpose: Weeks 4–5 - Data Cleaning and Preparation Pipeline for Listings Dataset

================================================================================
EXECUTION RESULTS & SUMMARY AUDIT LEDGER (LISTINGS DATASET)
================================================================================
--- [STEP 1] BASELINE AUDIT ---
Loaded File: /Users/samikshadubey/Downloads/IDX Code/Files/listings_v3.csv
Initial Rows: 591,890 | Initial Columns: 73

--- [STEP 2] DATATYPE CONFIRMATION ---
CloseDate                   datetime64[us]
ContractStatusChangeDate    datetime64[us]
PurchaseContractDate        datetime64[us]
ListingContractDate         datetime64[us]
dtype: object
Date columns successfully transformed into datetime64[ns]

--- [STEP 3] NUMERIC BOUNDS ENFORCEMENT ---
Removed 418 records containing impossible/negative physical values.

--- [STEP 4] DATE CHRONOLOGY LOGIC AUDIT ---
Total 'listing_after_close_flag' Violations: 79
Total 'purchase_after_close_flag' Violations: 266
Total 'negative_timeline_flag' Violations: 556

--- [STEP 5] GEOGRAPHIC QUALITY AUDIT SUMMARY ---
Records missing coordinates entirely: 80,728
Records stuck at (0,0) sentinel values: 69
Records with illegal positive longitudes: 80
Records detected out-of-state/implausible: 306

--- [STEP 6] FINAL SEAMLESS LAYER EXPORT ---
Cleaned master exported to: /Users/samikshadubey/Downloads/IDX Code/Files/listings_cleaned.csv
Final Count Matrix: Rows: 591,472 (Net Drop: 418) | Columns: 76
================================================================================
"""

import pandas as pd
import numpy as np

# =====================================================================
# STEP 1: LOAD DATASET & LOG BASELINE COUNTS
# =====================================================================
input_path = "/Users/samikshadubey/Downloads/IDX Code/Files/listings_v3.csv"
output_path = "/Users/samikshadubey/Downloads/IDX Code/Files/listings_cleaned.csv"

# Load the mortgage-enriched v3 dataset safely
df = pd.read_csv(input_path, low_memory=False)

# Store initial properties for the deliverable report
before_rows, before_cols = df.shape
print(f"--- [STEP 1] BASELINE AUDIT ---")
print(f"Loaded File: {input_path}")
print(f"Initial Rows: {before_rows:,} | Initial Columns: {before_cols}\n")


# =====================================================================
# STEP 2: CONVERT DATE FIELDS TO DATETIME FORMAT
# =====================================================================
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']

# Iterate and convert existing date columns safely (errors='coerce' turns bad formats to NaT)
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

print(f"--- [STEP 2] DATATYPE CONFIRMATION ---")
print(df[df.columns[df.columns.isin(date_cols)]].dtypes)
print("Date columns successfully transformed into datetime64[ns]\n")


# =====================================================================
# STEP 3: REMOVING STRUCUTURALLY INVALID NUMERIC VALUES
# =====================================================================
# Real estate analytics requires filtering out physical and transactional impossibilities
initial_numeric_rows = len(df)

# Drop rows matching invalid parameters
if 'ClosePrice' in df.columns:
    df = df[~(df['ClosePrice'] <= 0)]
if 'ListPrice' in df.columns:
    df = df[~(df['ListPrice'] <= 0)]
if 'LivingArea' in df.columns:
    df = df[~(df['LivingArea'] <= 0)]
if 'DaysOnMarket' in df.columns:
    df = df[~(df['DaysOnMarket'] < 0)]
if 'Bedrooms' in df.columns:
    df = df[~(df['Bedrooms'] < 0)]
if 'Bathrooms' in df.columns:
    df = df[~(df['Bathrooms'] < 0)]

removed_numeric_rows = initial_numeric_rows - len(df)
print(f"--- [STEP 3] NUMERIC BOUNDS ENFORCEMENT ---")
print(f"Removed {removed_numeric_rows:,} records containing impossible/negative physical values.\n")


# =====================================================================
# STEP 4: TIMELINE AND DATE CONSISTENCY LOGIC CHECKS
# =====================================================================
print(f"--- [STEP 4] DATE CHRONOLOGY LOGIC AUDIT ---")

# Listing Contract must occur before Purchase Contract, which must occur before Closing
if 'ListingContractDate' in df.columns and 'CloseDate' in df.columns:
    df['listing_after_close_flag'] = df['ListingContractDate'] > df['CloseDate']
else:
    df['listing_after_close_flag'] = False

if 'PurchaseContractDate' in df.columns and 'CloseDate' in df.columns:
    df['purchase_after_close_flag'] = df['PurchaseContractDate'] > df['CloseDate']
else:
    df['purchase_after_close_flag'] = False

# Composite rule tracking if any chronological order was completely broken
if 'ListingContractDate' in df.columns and 'PurchaseContractDate' in df.columns and 'CloseDate' in df.columns:
    df['negative_timeline_flag'] = (df['PurchaseContractDate'] < df['ListingContractDate']) | \
                                   (df['CloseDate'] < df['PurchaseContractDate'])
else:
    df['negative_timeline_flag'] = False

# Print anomaly summaries for submission report
print(f"Total 'listing_after_close_flag' Violations: {df['listing_after_close_flag'].sum():,}")
print(f"Total 'purchase_after_close_flag' Violations: {df['purchase_after_close_flag'].sum():,}")
print(f"Total 'negative_timeline_flag' Violations: {df['negative_timeline_flag'].sum():,}\n")


# =====================================================================
# STEP 5: GEOGRAPHIC INTEGRITY AND REGIONAL BOUNDARY AUDITS
# =====================================================================
print(f"--- [STEP 5] GEOGRAPHIC QUALITY AUDIT SUMMARY ---")

# 1. Flag absolute null coordinates
df['missing_coords_flag'] = df['Latitude'].isnull() | df['Longitude'].isnull()

# 2. Flag coordinate placement system defaults (Sentinel zero bugs)
df['sentinel_zero_flag'] = (df['Latitude'] == 0) | (df['Longitude'] == 0)

# 3. California coordinates must sit completely in western negative longitudes
df['positive_longitude_flag'] = df['Longitude'] > 0

# 4. Out-of-state check (Strict California bounding box envelope: Lat 32-42, Lon -125 to -114)
df['out_of_state_flag'] = (~df['missing_coords_flag']) & (
    (df['Latitude'] < 32) | (df['Latitude'] > 42) | 
    (df['Longitude'] < -125) | (df['Longitude'] > -114)
)

print(f"Records missing coordinates entirely: {df['missing_coords_flag'].sum():,}")
print(f"Records stuck at (0,0) sentinel values: {df['sentinel_zero_flag'].sum():,}")
print(f"Records with illegal positive longitudes: {df['positive_longitude_flag'].sum():,}")
print(f"Records detected out-of-state/implausible: {df['out_of_state_flag'].sum():,}\n")


# =====================================================================
# STEP 6: PRUNE REDUNDANT LAYERS & FINAL AUDIT
# =====================================================================
# List any meta-columns or system hashes identified in your EDA to be removed (if present)
redundant_cols = ['UnnecessarySystemID', 'InternalBatchID'] 
df = df.drop(columns=[col for col in redundant_cols if col in df.columns])

# Save the final cleaned master output
df.to_csv(output_path, index=False)

after_rows, after_cols = df.shape
print(f"--- [STEP 6] FINAL SEAMLESS LAYER EXPORT ---")
print(f"Cleaned master exported to: {output_path}")
print(f"Final Count Matrix: Rows: {after_rows:,} (Net Drop: {before_rows - after_rows:,}) | Columns: {after_cols}")






# SOLD DATASET


"""

--- [STEP 1] BASELINE AUDIT ---
Loaded File: /Users/samikshadubey/Downloads/IDX Code/Files/listings_v3.csv
Initial Rows: 591,890 | Initial Columns: 73

--- [STEP 2] DATATYPE CONFIRMATION ---
CloseDate                   datetime64[us]
ContractStatusChangeDate    datetime64[us]
PurchaseContractDate        datetime64[us]
ListingContractDate         datetime64[us]
dtype: object
Date columns successfully transformed into datetime64[ns]

--- [STEP 3] NUMERIC BOUNDS ENFORCEMENT ---
Removed 418 records containing impossible/negative physical values.

--- [STEP 4] DATE CHRONOLOGY LOGIC AUDIT ---
Total 'listing_after_close_flag' Violations: 79
Total 'purchase_after_close_flag' Violations: 266
Total 'negative_timeline_flag' Violations: 556

--- [STEP 5] GEOGRAPHIC QUALITY AUDIT SUMMARY ---
Records missing coordinates entirely: 80,728
Records stuck at (0,0) sentinel values: 69
Records with illegal positive longitudes: 80
Records detected out-of-state/implausible: 306

--- [STEP 6] FINAL SEAMLESS LAYER EXPORT ---
Cleaned master exported to: /Users/samikshadubey/Downloads/IDX Code/Files/listings_cleaned.csv
Final Count Matrix: Rows: 591,472 (Net Drop: 418) | Columns: 76
================================================================================
"""

import pandas as pd
import numpy as np

# =====================================================================
# STEP 1: LOAD DATASET & LOG BASELINE COUNTS
# =====================================================================
input_path = "/Users/samikshadubey/Downloads/IDX Code/Files/listings_v3.csv"
output_path = "/Users/samikshadubey/Downloads/IDX Code/Files/listings_cleaned.csv"

# Load the mortgage-enriched v3 dataset safely
df = pd.read_csv(input_path, low_memory=False)

# Store initial properties for the deliverable report
before_rows, before_cols = df.shape
print(f"--- [STEP 1] BASELINE AUDIT ---")
print(f"Loaded File: {input_path}")
print(f"Initial Rows: {before_rows:,} | Initial Columns: {before_cols}\n")


# =====================================================================
# STEP 2: CONVERT DATE FIELDS TO DATETIME FORMAT
# =====================================================================
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']

# Iterate and convert existing date columns safely (errors='coerce' turns bad formats to NaT)
for col in date_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')

print(f"--- [STEP 2] DATATYPE CONFIRMATION ---")
print(df[df.columns[df.columns.isin(date_cols)]].dtypes)
print("Date columns successfully transformed into datetime64[ns]\n")


# =====================================================================
# STEP 3: REMOVING STRUCUTURALLY INVALID NUMERIC VALUES
# =====================================================================
# Real estate analytics requires filtering out physical and transactional impossibilities
initial_numeric_rows = len(df)

# Drop rows matching invalid parameters
if 'ClosePrice' in df.columns:
    df = df[~(df['ClosePrice'] <= 0)]
if 'ListPrice' in df.columns:
    df = df[~(df['ListPrice'] <= 0)]
if 'LivingArea' in df.columns:
    df = df[~(df['LivingArea'] <= 0)]
if 'DaysOnMarket' in df.columns:
    df = df[~(df['DaysOnMarket'] < 0)]
if 'Bedrooms' in df.columns:
    df = df[~(df['Bedrooms'] < 0)]
if 'Bathrooms' in df.columns:
    df = df[~(df['Bathrooms'] < 0)]

removed_numeric_rows = initial_numeric_rows - len(df)
print(f"--- [STEP 3] NUMERIC BOUNDS ENFORCEMENT ---")
print(f"Removed {removed_numeric_rows:,} records containing impossible/negative physical values.\n")


# =====================================================================
# STEP 4: TIMELINE AND DATE CONSISTENCY LOGIC CHECKS
# =====================================================================
print(f"--- [STEP 4] DATE CHRONOLOGY LOGIC AUDIT ---")

# Listing Contract must occur before Purchase Contract, which must occur before Closing
if 'ListingContractDate' in df.columns and 'CloseDate' in df.columns:
    df['listing_after_close_flag'] = df['ListingContractDate'] > df['CloseDate']
else:
    df['listing_after_close_flag'] = False

if 'PurchaseContractDate' in df.columns and 'CloseDate' in df.columns:
    df['purchase_after_close_flag'] = df['PurchaseContractDate'] > df['CloseDate']
else:
    df['purchase_after_close_flag'] = False

# Composite rule tracking if any chronological order was completely broken
if 'ListingContractDate' in df.columns and 'PurchaseContractDate' in df.columns and 'CloseDate' in df.columns:
    df['negative_timeline_flag'] = (df['PurchaseContractDate'] < df['ListingContractDate']) | \
                                   (df['CloseDate'] < df['PurchaseContractDate'])
else:
    df['negative_timeline_flag'] = False

# Print anomaly summaries for submission report
print(f"Total 'listing_after_close_flag' Violations: {df['listing_after_close_flag'].sum():,}")
print(f"Total 'purchase_after_close_flag' Violations: {df['purchase_after_close_flag'].sum():,}")
print(f"Total 'negative_timeline_flag' Violations: {df['negative_timeline_flag'].sum():,}\n")


# =====================================================================
# STEP 5: GEOGRAPHIC INTEGRITY AND REGIONAL BOUNDARY AUDITS
# =====================================================================
print(f"--- [STEP 5] GEOGRAPHIC QUALITY AUDIT SUMMARY ---")

# 1. Flag absolute null coordinates
df['missing_coords_flag'] = df['Latitude'].isnull() | df['Longitude'].isnull()

# 2. Flag coordinate placement system defaults (Sentinel zero bugs)
df['sentinel_zero_flag'] = (df['Latitude'] == 0) | (df['Longitude'] == 0)

# 3. California coordinates must sit completely in western negative longitudes
df['positive_longitude_flag'] = df['Longitude'] > 0

# 4. Out-of-state check (Strict California bounding box envelope: Lat 32-42, Lon -125 to -114)
df['out_of_state_flag'] = (~df['missing_coords_flag']) & (
    (df['Latitude'] < 32) | (df['Latitude'] > 42) | 
    (df['Longitude'] < -125) | (df['Longitude'] > -114)
)

print(f"Records missing coordinates entirely: {df['missing_coords_flag'].sum():,}")
print(f"Records stuck at (0,0) sentinel values: {df['sentinel_zero_flag'].sum():,}")
print(f"Records with illegal positive longitudes: {df['positive_longitude_flag'].sum():,}")
print(f"Records detected out-of-state/implausible: {df['out_of_state_flag'].sum():,}\n")


# =====================================================================
# STEP 6: PRUNE REDUNDANT LAYERS & FINAL AUDIT
# =====================================================================
# List any meta-columns or system hashes identified in your EDA to be removed (if present)
redundant_cols = ['UnnecessarySystemID', 'InternalBatchID'] 
df = df.drop(columns=[col for col in redundant_cols if col in df.columns])

# Save the final cleaned master output
df.to_csv(output_path, index=False)

after_rows, after_cols = df.shape
print(f"--- [STEP 6] FINAL SEAMLESS LAYER EXPORT ---")
print(f"Cleaned master exported to: {output_path}")
print(f"Final Count Matrix: Rows: {after_rows:,} (Net Drop: {before_rows - after_rows:,}) | Columns: {after_cols}")

