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
