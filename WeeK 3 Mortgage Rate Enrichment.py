# ==============================================================================
# IDX Exchange Data Analyst Internship
# Purpose: Enrich the cleaned listings residential dataset with the national 
#          30 year fixed mortgage rate from the St. Louis Federal Reserve (FRED),
#          resampled from a weekly baseline to a calendar monthly average baseline.
#
# Execution & Audit Ledger Results:
# - Data Source Ingested: listings_cleaned_v2.csv
# - Listings Ingested Volume: 591,890 active residential rows loaded from V2
# - Timeline Alignment Key: Year-Month format derived from 'ListingContractDate'
# - Target Data Quality Validation: 0 unmatched macro rate rows (100% matched)
# - Master Export Layer: Safely saved as 'listings_v3.csv'
# ==============================================================================

# LISTING DATASET

import pandas as pd
import os

data_folder = "/Users/samikshadubey/Downloads/IDX Code/Files"
input_file = os.path.join(data_folder, "listings_cleaned_v2.csv")
output_file = os.path.join(data_folder, "listings_v3.csv")


def add_mortgage_rates(df):
    print(f"Columns before merge: {df.shape[1]}")

    # Download mortgage rate data
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
    mortgage = pd.read_csv(url, parse_dates=["observation_date"])
    mortgage.columns = ["date", "rate_30yr_fixed"]

    # Create monthly averages
    mortgage["year_month"] = mortgage["date"].dt.to_period("M")
    monthly_rates = (
        mortgage.groupby("year_month", as_index=False)["rate_30yr_fixed"]
        .mean()
    )

    # Aligning Timelines and Merge
    df["year_month"] = pd.to_datetime(
        df["ListingContractDate"], errors="coerce"
    ).dt.to_period("M")

    df = df.merge(monthly_rates, on="year_month", how="left")

    print(f"Columns after merge: {df.shape[1]}")
    print(f"Unmatched rows: {df['rate_30yr_fixed'].isna().sum()}")

    return df


# Load data
listings = pd.read_csv(input_file, low_memory=False)

# Enrich dataset
listings_v3 = add_mortgage_rates(listings)

# Save output
listings_v3.to_csv(output_file, index=False)

print(f"Saved as: {output_file}")


# SOLD DATASET

# 2-3 WEEK CONTINUED


import pandas as pd
import os

data_folder = "/Users/samikshadubey/Downloads/IDX Code/Files"
input_file = os.path.join(data_folder, "sold_cleaned_v2.csv")
output_file = os.path.join(data_folder, "sold_v3.csv")


def add_mortgage_rates(df):
    print(f"Columns before merge: {df.shape[1]}")

    # Download mortgage rate data
    url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
    mortgage = pd.read_csv(url, parse_dates=["observation_date"])
    mortgage.columns = ["date", "rate_30yr_fixed"]

    # Create monthly averages
    mortgage["year_month"] = mortgage["date"].dt.to_period("M")
    monthly_rates = (
        mortgage.groupby("year_month", as_index=False)["rate_30yr_fixed"]
        .mean()
    )

    # Alignning timeline and Merge
    df["year_month"] = pd.to_datetime(
        df["CloseDate"], errors="coerce"
    ).dt.to_period("M")

    df = df.merge(monthly_rates, on="year_month", how="left")

    print(f"Columns after merge: {df.shape[1]}")
    print(f"Unmatched rows: {df['rate_30yr_fixed'].isna().sum()}")

    return df


# Load data
sold = pd.read_csv(input_file, low_memory=False)

# Enrich dataset
sold_v3 = add_mortgage_rates(sold)

# Save output
sold_v3.to_csv(output_file, index=False)

print(f"Saved as: {output_file}")


