# SAMIKSHA DUBEY

# LISTINGS DATASET

# 2-3 WEEK CONTINUED

import pandas as pd
import os

# Pointing to my actual directory where the v2 file lives
data_folder = "/Users/samikshadubey/Downloads/IDX Code/Files"
input_path = os.path.join(data_folder, "listings_cleaned_v2.csv")

print("=== STARTING LISTINGS PIPELINE MORTGAGE RATE ENRICHMENT ===")

# 1: Fetch live data from FRED API
print("\n[Step 1] Fetching live data from FRED API...")
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

# 2: Resampling weekly rates to monthly averages
print("[Step 2] Resampling weekly rates to monthly averages...")
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)

# 3. Loading the Cleaned Version 2 Dataset
print(f"\n[Step 3] Loading internal cleaned v2 data from: {input_path}")
if not os.path.exists(input_path):
    raise FileNotFoundError(f"Could not find the v2 file at {input_path}. Please check your folder.")

listings = pd.read_csv(input_path)
print(f"-> Successfully loaded {listings.shape[0]} active listing rows from Version 2.")

# 4 Aligning timelines and merge
print("\n[Step 4] Aligning timelines and creating matching join keys...")
listings['year_month'] = pd.to_datetime(listings['ListingContractDate']).dt.to_period('M')

print("[Step 5] Performing left join with macro indicators...")
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left')

# 5. Data Quality Audit Check
print("\n[Step 6] Running validation and data quality checks...")
null_counts = listings_with_rates['rate_30yr_fixed'].isnull().sum()
print(f"-> Unmatched rows (missing rate values): {null_counts}")

if null_counts == 0:
    print(" Audit Passed: 100% of rows successfully matched to a monthly rate!")
else:
    print(" Audit Warning: Some rows did not find a match. Double check your contract dates.")

# 6. Exporting the finalised enriched production file
output_path = os.path.join(data_folder, "listings_v3.csv")
listings_with_rates.to_csv(output_path, index=False)
print(f"\n Pipeline Finished! Enriched file exported to: {output_path}")


# SOLD DATASET

# 2-3 WEEK CONTINUED



import pandas as pd
import os

# Pointing to my actual directory where the v2 file lives
data_folder = "/Users/samikshadubey/Downloads/IDX Code/Files"
input_path = os.path.join(data_folder, "sold_cleaned_v2.csv")

print("=== STARTING SOLD PIPELINE MORTGAGE RATE ENRICHMENT ===")

# 1: Fetch live macroeconomic data from FRED API
print("\n[Step 1] Fetching live data from FRED API...")
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

# 2: Resampling weekly rates to monthly averages
print("[Step 2] Resampling weekly rates to monthly averages...")
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)

# 3: Loading the Cleaned Version 2 Sold Dataset
print(f"\n[Step 3] Loading internal cleaned v2 data from: {input_path}")
if not os.path.exists(input_path):
    raise FileNotFoundError(f"Could not find the v2 file at {input_path}. Please check your folder path.")

sold = pd.read_csv(input_path)
print(f"-> Successfully loaded {sold.shape[0]} transaction rows from Version 2.")

# 4: Aligning timelines and merge
print("\n[Step 4] Aligning timelines and creating matching join keys...")
# For sold data, we always anchor the tracking key off CloseDate
sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')

print("[Step 5] Performing left join with macro indicators...")
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')

# 5: Data Quality Audit Check
print("\n[Step 6] Running validation and data quality checks...")
null_counts = sold_with_rates['rate_30yr_fixed'].isnull().sum()
print(f"-> Unmatched rows (missing rate values): {null_counts}")

if null_counts == 0:
    print("Audit Passed: 100% of rows successfully matched to a monthly rate!")
else:
    print("Audit Warning: Some rows did not find a match. Double check your transaction close dates.")

# 6: Exporting the finalized enriched production file as V3
output_path = os.path.join(data_folder, "sold_v3.csv")
sold_with_rates.to_csv(output_path, index=False)
print(f"\n Pipeline Finished! Enriched file exported to: {output_path}")

