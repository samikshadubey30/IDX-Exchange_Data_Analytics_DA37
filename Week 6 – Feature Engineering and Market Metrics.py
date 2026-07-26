"""
===============================================================================
WEEK 6: FEATURE ENGINEERING & MARKET METRICS (LISTINGS DATASET)
Author: Samiksha Dubey
Project: IDX Exchange Data Analytics Pipeline

FINAL OUTCOMES & METRICS AUDIT SUMMARY:
-------------------------------------------------------------------------------
1. Dataset Ingestion & Processing:
   - Input File: listings_cleaned.csv (591,472 records, 80 initial columns)
   - Output File: listings_engineered.csv

2. Engineered Feature Deliverables:
   - Price Ratio (List Price / Original List Price): Handles zero-division safety.
   - Price Per Sq Ft (List Price / Living Area): Normalized pricing ($700.04/sqft avg).
   - Time Granularities: Year, Month, YrMo (YYYY-MM string format for Tableau).
   - Speed Metrics: ListingToContractDays & DaysOnMarket (18.5 days avg DOM).

3. Geospatial Point-in-Polygon Join (School Districts):
   - Spatial Map Source: California Unified School District Areas 2024-25 GeoJSON
   - Total Properties Processed: 591,472
   - Mapped to Unified School Districts: 393,460 properties (66.5%)
   - Unmapped / Non-Unified Areas: 198,012 properties (33.5%)
   - Top Mapped District: Los Angeles Unified (66,192 properties)

4. Segment Analysis Highlights:
   - Residential Inventory Median Price: $849,000
   - Market Leader (List Office): Compass (42,471 active listings | $1.38M median)
===============================================================================
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import os

# Set exact folder directory path
folder_path = "/Users/samikshadubey/Downloads/IDX Code/Files"

# Define full paths for input and output files
listings_input = os.path.join(folder_path, "listings_cleaned.csv")
geojson_input = os.path.join(folder_path, "california_school_districts.geojson")
output_csv = os.path.join(folder_path, "listings_engineered.csv")

# ==========================================
# STEP 1: Load Data & Format Dates
# ==========================================
print("Step 1: Loading data...")
df = pd.read_csv(listings_input, low_memory=False)

# Convert text date columns to proper datetime format
date_columns = ["ListingContractDate", "PurchaseContractDate", "ModificationTimestamp"]
for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

print("Step 1 Complete: Loaded dataset with shape", df.shape)

# ==========================================
# STEP 2: Engineer Financial & Price Ratio Metrics
# ==========================================
print("Step 2: Engineering financial metrics...")

# Calculate Price Ratio with zero-division safety
if "ListPrice" in df.columns and "OriginalListPrice" in df.columns:
    df["PriceRatio"] = np.where(
        df["OriginalListPrice"] > 0, 
        df["ListPrice"] / df["OriginalListPrice"], 
        np.nan
    )

# Calculate Price Per Square Foot with zero-division safety
if "ListPrice" in df.columns and "LivingArea" in df.columns:
    df["PricePerSqFt"] = np.where(
        df["LivingArea"] > 0, 
        df["ListPrice"] / df["LivingArea"], 
        np.nan
    )

print("Step 2 Complete: Created PriceRatio and PricePerSqFt.")

# ==========================================
# STEP 3: Engineer Time-Series & Speed Metrics
# ==========================================
print("Step 3: Engineering time-series & speed metrics...")

# Extract Year, Month, and Year-Month string
if "ListingContractDate" in df.columns:
    df["Year"] = df["ListingContractDate"].dt.year
    df["Month"] = df["ListingContractDate"].dt.month
    df["YrMo"] = df["ListingContractDate"].dt.to_period("M").astype(str)

# Calculate days between listing and contract
if "PurchaseContractDate" in df.columns and "ListingContractDate" in df.columns:
    df["ListingToContractDays"] = (df["PurchaseContractDate"] - df["ListingContractDate"]).dt.days

# Fill DaysOnMarket if missing
if "DaysOnMarket" not in df.columns and "ListingContractDate" in df.columns:
    df["DaysOnMarket"] = (pd.Timestamp.now() - df["ListingContractDate"]).dt.days

print("Step 3 Complete: Created time-series and speed metrics.")

# ==========================================
# STEP 4: Spatial Join for School Districts
# ==========================================
print("Step 4: Mapping school districts...")

try:
    # Load school district map
    districts_gdf = gpd.read_file(geojson_input)
    
    # Keep only Unified school districts
    if "DistrictType" in districts_gdf.columns:
        unified_districts = districts_gdf[districts_gdf["DistrictType"] == "Unified"].copy()
    else:
        unified_districts = districts_gdf.copy()
        
    # Drop rows missing coordinates
    coords_df = df.dropna(subset=["Latitude", "Longitude"]).copy()
    
    # Convert latitude/longitude to spatial points
    properties_gdf = gpd.GeoDataFrame(
        coords_df,
        geometry=gpd.points_from_xy(coords_df["Longitude"], coords_df["Latitude"]),
        crs="EPSG:4326"
    )
    
    # Align spatial reference systems
    if unified_districts.crs != properties_gdf.crs:
        unified_districts = unified_districts.to_crs(properties_gdf.crs)
        
    # Perform spatial point-in-polygon join
    joined_gdf = gpd.sjoin(properties_gdf, unified_districts, how="left", predicate="within")
    
    # Assign District Name column to main dataset
    district_col = "DistrictName" if "DistrictName" in joined_gdf.columns else ("NAME" if "NAME" in joined_gdf.columns else joined_gdf.columns[0])
    df["SchoolDistrict"] = joined_gdf[district_col]
    print("Step 4 Complete: School districts mapped successfully.")

except Exception as e:
    print("Step 4 Notice: Spatial join skipped or failed ->", e)
    df["SchoolDistrict"] = np.nan

# ==========================================
# STEP 5: Segment Analysis (Summaries)
# ==========================================
print("Step 5: Generating segment summaries...")

# Group by Property Type
summary_property_type = df.groupby("PropertyType").agg(
    Active_Listings=("ListPrice", "count"),
    Median_List_Price=("ListPrice", "median"),
    Avg_PPSF=("PricePerSqFt", "mean"),
    Avg_Price_Ratio=("PriceRatio", "mean"),
    Avg_DOM=("DaysOnMarket", "mean")
).reset_index()

# Group by County
summary_county = df.groupby("CountyOrParish").agg(
    Active_Listings=("ListPrice", "count"),
    Median_List_Price=("ListPrice", "median"),
    Avg_PPSF=("PricePerSqFt", "mean"),
    Avg_Price_Ratio=("PriceRatio", "mean")
).reset_index()

# Group by Listing Office
summary_list_office = df.groupby("ListOfficeName").agg(
    Active_Listings=("ListPrice", "count"),
    Median_List_Price=("ListPrice", "median")
).sort_values(by="Active_Listings", ascending=False).reset_index()

print("Step 5 Complete: Summary tables generated.")

# ==========================================
# STEP 6: Display Results & Verification Checks
# ==========================================
sample_cols = [
    "ListPrice", "OriginalListPrice", "PriceRatio", 
    "PricePerSqFt", "YrMo", "DaysOnMarket", 
    "ListingToContractDays", "SchoolDistrict"
]

print("\n--- SAMPLE OUTPUT TABLE ---")
print(df[[c for c in sample_cols if c in df.columns]].head(10))

print("\n--- SUMMARY BY PROPERTY TYPE ---")
print(summary_property_type)

print("\n--- TOP LISTING OFFICES ---")
print(summary_list_office.head(10))

print("\n--- TOP 10 SCHOOL DISTRICTS BY PROPERTY COUNT ---")
print(df["SchoolDistrict"].value_counts().head(10))

print("\n--- SAMPLE MAPPED SCHOOL DISTRICTS ---")
preview_cols = ["City", "Latitude", "Longitude", "SchoolDistrict"]
sample_display = df[df["SchoolDistrict"].notna()][preview_cols].head(10)
print(sample_display.to_string(index=False))

print("\n--- SCHOOL DISTRICT MAPPING STATS ---")
total_rows = len(df)
mapped_count = df["SchoolDistrict"].notna().sum()
missing_count = df["SchoolDistrict"].isna().sum()
print(f"Total Properties: {total_rows}")
print(f"Mapped to School District: {mapped_count} ({mapped_count/total_rows:.1%})")
print(f"Unmapped / Missing: {missing_count} ({missing_count/total_rows:.1%})")

# Save final engineered file
df.to_csv(output_csv, index=False)
print(f"\nStep 6 Complete: Saved output to {output_csv}")





SOLD DATASET:

"""
===============================================================================
WEEK 6: FEATURE ENGINEERING & MARKET METRICS (SOLD DATASET)
Author: Samiksha Dubey
Project: IDX Exchange Data Analytics Pipeline

FINAL OUTCOMES & METRICS AUDIT SUMMARY:
-------------------------------------------------------------------------------
1. Dataset Ingestion & Processing:
   - Input File: sold_cleaned.csv (430,234 records, 79 initial columns)
   - Output File: sold_engineered.csv

2. Engineered Feature Deliverables:
   - Close Price Ratio (Close Price / Original List Price): Zero-division protected.
   - Price Per Sq Ft (Close Price / Living Area): Normalized pricing ($647.98/sqft avg).
   - Time Granularities: Year, Month, YrMo (YYYY-MM string format derived from CloseDate).
   - Speed Metrics: 
     * DaysOnMarket (37.3 days avg DOM)
     * ListingToContractDays (45.1 days avg time to accepted offer)
     * ContractToCloseDays (31.6 days avg escrow period)

3. Geospatial Point-in-Polygon Join (School Districts):
   - Spatial Map Source: California Unified School District Areas 2024-25 GeoJSON
   - Total Properties Processed: 430,234
   - Mapped to Unified School Districts: 314,492 properties (73.1%)
   - Unmapped / Non-Unified Areas: 115,742 properties (26.9%)
   - Top Mapped District: Los Angeles Unified (43,711 transactions)

4. Segment Analysis Highlights:
   - Residential Closed Sales Volume: 430,232 transactions | Median Close Price: $825,000
   - Buy-Side Market Leader (Buyer Office): Compass (28,354 sales | $1.33M median)
===============================================================================
"""

import pandas as pd
import numpy as np
import geopandas as gpd
import os

# Set exact folder directory path
folder_path = "/Users/samikshadubey/Downloads/IDX Code/Files"

# Define full paths for input and output files
sold_input = os.path.join(folder_path, "sold_cleaned.csv")
geojson_input = os.path.join(folder_path, "california_school_districts.geojson")
output_csv = os.path.join(folder_path, "sold_engineered.csv")

# ==========================================
# STEP 1: Load Data & Format Dates
# ==========================================
print("Step 1: Loading sold data...")
df = pd.read_csv(sold_input, low_memory=False)

# Convert text date columns to proper datetime format
date_columns = ["CloseDate", "ListingContractDate", "PurchaseContractDate"]
for col in date_columns:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors="coerce")

print("Step 1 Complete: Loaded dataset with shape", df.shape)

# ==========================================
# STEP 2: Engineer Financial & Price Ratio Metrics
# ==========================================
print("Step 2: Engineering financial metrics...")

# Calculate Price Ratio (ClosePrice / OriginalListPrice) with zero-division safety
if "ClosePrice" in df.columns and "OriginalListPrice" in df.columns:
    df["PriceRatio"] = np.where(
        df["OriginalListPrice"] > 0,
        df["ClosePrice"] / df["OriginalListPrice"],
        np.nan
    )
    df["CloseToOriginalListRatio"] = df["PriceRatio"]

# Calculate Price Per Square Foot (ClosePrice / LivingArea)
if "ClosePrice" in df.columns and "LivingArea" in df.columns:
    df["PricePerSqFt"] = np.where(
        df["LivingArea"] > 0, 
        df["ClosePrice"] / df["LivingArea"], 
        np.nan
    )

print("Step 2 Complete: Created PriceRatio and PricePerSqFt.")

# ==========================================
# STEP 3: Engineer Time-Series & Speed Metrics
# ==========================================
print("Step 3: Engineering time-series & speed metrics...")

# Extract Year, Month, and Year-Month string derived from CloseDate
if "CloseDate" in df.columns:
    df["Year"] = df["CloseDate"].dt.year
    df["Month"] = df["CloseDate"].dt.month
    df["YrMo"] = df["CloseDate"].dt.to_period("M").astype(str)

# Calculate Listing to Contract Days (Offer acceptance duration)
if "PurchaseContractDate" in df.columns and "ListingContractDate" in df.columns:
    df["ListingToContractDays"] = (df["PurchaseContractDate"] - df["ListingContractDate"]).dt.days

# Calculate Contract to Close Days (Escrow duration)
if "CloseDate" in df.columns and "PurchaseContractDate" in df.columns:
    df["ContractToCloseDays"] = (df["CloseDate"] - df["PurchaseContractDate"]).dt.days

# Ensure DaysOnMarket exists or fill with ListingToContractDays if missing
if "DaysOnMarket" not in df.columns and "ListingToContractDays" in df.columns:
    df["DaysOnMarket"] = df["ListingToContractDays"]

print("Step 3 Complete: Created time-series and transaction speed metrics.")

# ==========================================
# STEP 4: Spatial Join for School Districts
# ==========================================
print("Step 4: Mapping school districts...")

try:
    # Load school district map
    districts_gdf = gpd.read_file(geojson_input)
    
    # Keep only Unified school districts
    if "DistrictType" in districts_gdf.columns:
        unified_districts = districts_gdf[districts_gdf["DistrictType"] == "Unified"].copy()
    else:
        unified_districts = districts_gdf.copy()
        
    # Drop rows missing coordinates
    coords_df = df.dropna(subset=["Latitude", "Longitude"]).copy()
    
    # Convert latitude/longitude to spatial points
    properties_gdf = gpd.GeoDataFrame(
        coords_df,
        geometry=gpd.points_from_xy(coords_df["Longitude"], coords_df["Latitude"]),
        crs="EPSG:4326"
    )
    
    # Align spatial reference systems
    if unified_districts.crs != properties_gdf.crs:
        unified_districts = unified_districts.to_crs(properties_gdf.crs)
        
    # Perform spatial point-in-polygon join
    joined_gdf = gpd.sjoin(properties_gdf, unified_districts, how="left", predicate="within")
    
    # Assign District Name column to main dataset
    district_col = "DistrictName" if "DistrictName" in joined_gdf.columns else ("NAME" if "NAME" in joined_gdf.columns else joined_gdf.columns[0])
    df["SchoolDistrict"] = joined_gdf[district_col]
    print("Step 4 Complete: School districts mapped successfully.")

except Exception as e:
    print("Step 4 Notice: Spatial join skipped or failed ->", e)
    df["SchoolDistrict"] = np.nan

# ==========================================
# STEP 5: Segment Analysis (Summaries)
# ==========================================
print("Step 5: Generating segment summaries...")

# Group by Property Type
summary_property_type = df.groupby("PropertyType").agg(
    Sold_Count=("ClosePrice", "count"),
    Median_Close_Price=("ClosePrice", "median"),
    Avg_PPSF=("PricePerSqFt", "mean"),
    Avg_Price_Ratio=("PriceRatio", "mean"),
    Avg_DOM=("DaysOnMarket", "mean"),
    Avg_Listing_To_Contract=("ListingToContractDays", "mean"),
    Avg_Contract_To_Close=("ContractToCloseDays", "mean")
).reset_index()

# Group by County
summary_county = df.groupby("CountyOrParish").agg(
    Sold_Count=("ClosePrice", "count"),
    Median_Close_Price=("ClosePrice", "median"),
    Avg_PPSF=("PricePerSqFt", "mean"),
    Avg_Price_Ratio=("PriceRatio", "mean")
).reset_index()

# Group by Buyer Office (Competitive Intelligence)
summary_buyer_office = df.groupby("BuyerOfficeName").agg(
    Sold_Count=("ClosePrice", "count"),
    Median_Close_Price=("ClosePrice", "median")
).sort_values(by="Sold_Count", ascending=False).reset_index()

print("Step 5 Complete: Summary tables generated.")

# ==========================================
# STEP 6: Display Results & Verification Checks
# ==========================================
sample_cols = [
    "ClosePrice", "OriginalListPrice", "PriceRatio", 
    "PricePerSqFt", "YrMo", "DaysOnMarket", 
    "ListingToContractDays", "ContractToCloseDays", "SchoolDistrict"
]

print("\n--- SAMPLE OUTPUT TABLE ---")
print(df[[c for c in sample_cols if c in df.columns]].head(10))

print("\n--- SUMMARY BY PROPERTY TYPE ---")
print(summary_property_type)

print("\n--- TOP BUYER OFFICES ---")
print(summary_buyer_office.head(10))

print("\n--- TOP 10 SCHOOL DISTRICTS BY PROPERTY COUNT ---")
print(df["SchoolDistrict"].value_counts().head(10))

print("\n--- SAMPLE MAPPED SCHOOL DISTRICTS ---")
preview_cols = ["City", "Latitude", "Longitude", "SchoolDistrict"]
sample_display = df[df["SchoolDistrict"].notna()][preview_cols].head(10)
print(sample_display.to_string(index=False))

print("\n--- SCHOOL DISTRICT MAPPING STATS ---")
total_rows = len(df)
mapped_count = df["SchoolDistrict"].notna().sum()
missing_count = df["SchoolDistrict"].isna().sum()
print(f"Total Properties: {total_rows}")
print(f"Mapped to School District: {mapped_count} ({mapped_count/total_rows:.1%})")
print(f"Unmapped / Missing: {missing_count} ({missing_count/total_rows:.1%})")

# Save final output
df.to_csv(output_csv, index=False)
print(f"\nStep 6 Complete: Saved output to {output_csv}")
