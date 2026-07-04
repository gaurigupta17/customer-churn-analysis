# Customer Churn Analysis & Retention Dashboard (MNC Telecom)

An end-to-end data analytics project to clean, store, analyze, and visualize customer churn for a traditional Telecom MNC. This repository establishes a database pipeline in SQLite, queries core churn drivers, and hosts an interactive Streamlit dashboard featuring a custom Churn Risk Calculator.

## 📌 Business Case & Problem Statement

Customer churn represents subscribers ending their services, which directly impacts recurring revenue and raises customer acquisition costs. 

For this Telecom MNC:
* **The Headcount Problem**: **26.54%** of the customer base has churned (1,869 out of 7,043).
* **The Revenue Leak**: Monthly recurring revenue lost to churn is **$139,130.85** out of **$456,116.60** total potential monthly charges. **30.5%** of the company's monthly revenue is leaking.
* **The High-Value Defection**: Churned customers are higher-spending, with an average monthly bill of **$74.44** vs. **$61.27** for retained customers (a **21.5%** increase). 

The goal of this project is to identify the root causes of this leakage and build an interactive calculator for account managers to estimate churn risk on individual customer profiles before they disconnect.

---

## 🛠️ Technology Stack & Project Structure

- **Database**: SQLite (SQL) for storing and querying the datasets.
- **Languages**: Python (Pandas) for data ingestion and cleaning.
- **Visualization & Application**: Streamlit & Plotly (Python) for building the user interface and interactive charts.

### Project Structure
```text
├── data/
│   ├── raw/                  # Sourced raw CSV from IBM Github
│   ├── processed/            # Cleaned CSV output
│   └── churn_analysis.db     # SQLite local database
├── sql/
│   ├── schema.sql            # Table DDL definitions
│   └── analysis_queries.sql  # SQL queries for churn metrics
├── scripts/
│   ├── download_data.py      # Python ingestion script
│   ├── clean_data.py         # Python cleaning script
│   ├── import_data.py        # Python SQLite loader script
│   └── run_queries.py        # SQL query execution script
├── dashboard/
│   ├── app.py                # Streamlit Web App
│   └── screenshots/          # Exported dashboard verification views
├── README.md                 # Case study write-up (This file)
└── INTERVIEW_PREP.md         # Portfolio Q&A preparation guide
```

---

## 🔍 Data Pipeline & Cleaning Methodology

1. **Ingestion (`scripts/download_data.py`)**: Automatically pulls the raw IBM Telco Customer Churn dataset (7,043 rows) from a public Github repository.
2. **Standardization (`scripts/clean_data.py`)**:
   - Converted all 21 columns to lowercase `snake_case` (e.g., `customerID` $\rightarrow$ `customer_id`, `MonthlyCharges` $\rightarrow$ `monthly_charges`) for cleaner SQL syntax.
   - Checked for nulls. Identified **11 rows** in `total_charges` that were blank spaces. 
   - Found that these rows had a `tenure` of `0` months (new accounts that hadn't finished a billing cycle). Replaced these blanks with `0.0` rather than dropping the rows to maintain dataset integrity.
3. **Database Loader (`scripts/import_data.py`)**: Connects to the local SQLite database, drops/re-creates the schema using `sql/schema.sql`, and commits the cleaned records.

---

## 📊 Key Analytical Insights (SQL Queries)

* **Month-to-month contracts** are the primary source of churn, showing an alarming **42.71%** churn rate. In contrast, One-year contracts have **11.27%** churn, and Two-year contracts show only **2.83%** churn.
* **Early Lifecycle Churn**: Churn is extremely front-loaded. Customers in their first 6 months have a **52.94%** churn rate. If a customer stays past 12 months, the rate drops below **28%**.
* **Payment Methods**: Customers paying by **Electronic Check** show a **45.29%** churn rate, while Mailed Checks (19.11%), Bank Transfers (16.71%), and Credit Cards (15.24%) have far lower churn. This suggests billing friction or payment failures might be driving churn.
* **Support & Service Package**: Customers who do *not* have Tech Support churn at **41.64%**, whereas those with Tech Support churn at only **15.17%**.
* **Profile Demographics**: **Senior Citizens** churn at a high rate of **41.68%**, compared to only **23.61%** for non-seniors.

---

## 💻 Running the Application Locally

To replicate the project, run the following commands in order:

### 1. Install Dependencies
```bash
python3 -m pip install pandas streamlit plotly tabulate
```

### 2. Ingest and Clean Data
```bash
python3 scripts/download_data.py
python3 scripts/clean_data.py
```

### 3. Build and Verify SQLite Database
```bash
python3 scripts/import_data.py
python3 scripts/run_queries.py
```

### 4. Run the Streamlit Dashboard
```bash
python3 -m streamlit run dashboard/app.py
```

---

## 🖼️ Dashboard Preview

### Executive Summary Tab
Contains the high-level KPIs and tenure analysis showing early-lifecycle risk.
![Executive Summary](dashboard/screenshots/executive_summary.png)
![Charts view](dashboard/screenshots/charts.png)

### Churn Drivers Tab
Visualizes the correlation between churn rate and contracts, internet service, support, and billing methods.
![Churn Drivers](dashboard/screenshots/churn_drivers.png)

### Customer Explorer Tab
Enables customer search and exports list data for targeting marketing campaigns.
![Customer Explorer](dashboard/screenshots/customer_explorer.png)
