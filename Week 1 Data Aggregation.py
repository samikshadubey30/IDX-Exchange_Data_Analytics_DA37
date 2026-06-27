# Week 1 - Monthly Dataset Aggregation
# IDX Exchange Data Analyst Internship
# Author: Samiksha Dubey
# Date: 2026-06-24
#
# This script:
# 1. Loads all available monthly CRMLSListing files
# 2. Concatenates them into two combined datasets
# 3. Filters contactenated files to PropertyType == 'Residential' only
# 4. Saves the filtered datasets as listings.csv

# Listings files start from 202401 (January, 2024) till 202605 (May 2026)


import glob
import os
import pandas as pd

# 1. Directory Setup
data_folder = "/Users/samikshadubey/Downloads/IDX Code/Files"
listing_files = sorted(glob.glob(os.path.join(data_folder, "CRMLSListing*.csv")))

print(f"Found {len(listing_files)} Listing files to process.\n")
print("--- Individual File Row Counts (Before Concatenation) ---")

# 2. Read files and track individual row counts
listing_dfs = []
for file_path in listing_files:
    df = pd.read_csv(file_path, low_memory=False)
    print(f"{os.path.basename(file_path)}: {len(df):,} rows")
    listing_dfs.append(df)

# 3. Concatenate and Filter
listings_master = pd.concat(listing_dfs, ignore_index=True)
listings_residential = listings_master[
    listings_master["PropertyType"] == "Residential"
]

# 4. Final Validation Logs
print("\n--- Final Summary Logs ---")
print(f"Total Rows Combined (Before Filter): {len(listings_master):,} rows")
print(f"Total Rows Kept (After Residential Filter): {len(listings_residential):,} rows")

# 5. Export
output_path = os.path.join(data_folder, "listings.csv")
listings_residential.to_csv(output_path, index=False)
print(f"\nDone! Master file saved successfully to: {output_path}")



# Week 1 - Monthly Dataset Aggregation
# IDX Exchange Data Analyst Internship
# Author: Samiksha Dubey
# Date: 2026-06-22
#
# This script:
# 1. Loads all available monthly CRMLSListing and CRMLSSold CSV files
# 2. Concatenates them into two combined datasets
# 3. Filters both to PropertyType == 'Residential' only
# 4. Saves the filtered datasets as listings.csv and sold.csv

# Sold files start from 202401 (January, 2024) till 202605 (May 2026)


import glob
import os
import pandas as pd

# 1. Directory Setup
data_folder = "/Users/samikshadubey/Downloads/IDX Code/Files"
sold_files = sorted(glob.glob(os.path.join(data_folder, "CRMLSSold*.csv")))

print(f"Found {len(sold_files)} Sold files to process.\n")
print("--- Individual File Row Counts (Before Concatenation) ---")

# 2. Read files and track individual row counts
sold_dfs = []
for file_path in sold_files:
    df = pd.read_csv(file_path, low_memory=False)
    print(f"{os.path.basename(file_path)}: {len(df):,} rows")
    sold_dfs.append(df)

# 3. Concatenate and Filter
sold_master = pd.concat(sold_dfs, ignore_index=True)
sold_residential = sold_master[sold_master["PropertyType"] == "Residential"]

# 4. Final Validation Logs
print("\n--- Final Summary Logs ---")
print(f"Total Rows Combined (Before Filter): {len(sold_master):,} rows")
print(f"Total Rows Kept (After Residential Filter): {len(sold_residential):,} rows")

# 5. Export
output_path = os.path.join(data_folder, "sold.csv")
sold_residential.to_csv(output_path, index=False)
print(f"\nDone! Master file saved successfully to: {output_path}")

