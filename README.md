# IDX-Exchange_Data_Analytics_DA37

This repository contains my internship project work at IDX Exchange, focused on automating the extraction of real estate listing and sold-property data from the CoreLogic Trestle API (CRMLS). The project retrieves MLS data through authenticated API requests and exports the results into structured CSV files for analysis and reporting.
The scripts are designed to support monthly data extraction by allowing date-based filters to be adjusted as needed. The workflow streamlines data collection, transformation, and storage, enabling efficient access to real estate market data for downstream analytics and business insights.


## 📂 Repository Contents & Automation Architecture

### 📜 Extraction Scripts
- **`crmls_sold.py`**: Interfaced with the API to extract closed property records for specified target months. [cite_start]Features logical filters tracking `CloseDate` and automatically routes matching observation matrices directly to a flat CSV format[cite: 1316, 1701].
- **`crmls_listed.py`**: Interfaced with the API to extract property listings entering active inventory loops. [cite_start]Applies strict date-bound segmentations tracking `ListingContractDate` and structural outputs[cite: 1309, 1700].

---

## 🛠️ System Requirements & Dependencies

### 🐍 Python Version
- Python 3.x

### 📦 Dependencies
Install the required network protocol package via your local terminal before execution:
```bash
pip install requests

1. Generating Monthly Closed (Sold) Data
The transaction script isolates and exports records that reached successfully closed milestones within your targeted date configurations. To capture a different calendar month, open the notebook cell and update the date boundaries within the API parameters:

Python
'$filter': f"MlsStatus eq 'Closed' and CloseDate ge {datetime(2026, 1, 1).isoformat(timespec='milliseconds')}Z and CloseDate lt {datetime(2026, 2, 1).isoformat(timespec='milliseconds')}Z",

Note: The first datetime construct defines the beginning boundary of the target month, and the second construct defines the boundary of the following month.
Ensure you explicitly update the matching output target destination file string to avoid overwriting existing historic records:

Python
csv_file = 'CRMLSSold202601.csv'
For example, to extract and log April 2026 records, map csv_file = 'CRMLSSold202604.csv'.

Execute the routine:
Bash
python crmls_sold.py

2. Generating Monthly Active Listing Data
The inventory script programmatically aggregates property logs whose original contract markers match your targeted periods. Update the filter configurations:

Python
'$filter': f"ListingContractDate ge {datetime(2026, 1, 1).isoformat(timespec='milliseconds')}Z and ListingContractDate lt {datetime(2026, 2, 1).isoformat(timespec='milliseconds')}Z",
Modify the parameter strings to match the targeted timeframe. Update the structural export target filename string:

Python
csv_file = 'CRMLSListing202601.csv'
For example, to isolate and log April 2026 active metrics, map csv_file = 'CRMLSListing202604.csv'.
Execute the routine:
Bash
python crmls_listed.py

Pipeline Data Outputs
Upon a successful operational run, the backend scripts parse multi-page API responses and save out flat structural text-stream CSV files containing regional records:
Plaintext
├── CRMLSSold202601.csv
├── CRMLSSold202602.csv
├── CRMLSSold202603.csv
├── CRMLSListing202601.csv
├── CRMLSListing202602.csv
└── CRMLSListing202603.csv
