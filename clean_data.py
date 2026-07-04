"""
clean_data.py
Description: Cleans the raw customer churn dataset and prepares it for SQL database import and analysis.
Major cleaning steps:
1. Rename columns to snake_case.
2. Convert total_charges from text to numeric, replacing blanks with 0 for new customers (tenure = 0).
3. Standardize text columns and verify data types.
"""

import os
import pandas as pd

def clean_dataset():
    # Paths
    raw_path = os.path.join("data", "raw", "customer_churn_raw.csv")
    cleaned_dir = os.path.join("data", "processed")
    cleaned_path = os.path.join(cleaned_dir, "customer_churn_clean.csv")
    
    # Read raw data
    print(f"Loading raw data from {raw_path}...")
    df = pd.read_csv(raw_path)
    
    print(f"Original shape: {df.shape}")
    
    # 1. Rename columns to lowercase snake_case for easy SQL usage
    rename_dict = {
        "customerID": "customer_id",
        "gender": "gender",
        "SeniorCitizen": "senior_citizen",
        "Partner": "partner",
        "Dependents": "dependents",
        "tenure": "tenure",
        "PhoneService": "phone_service",
        "MultipleLines": "multiple_lines",
        "InternetService": "internet_service",
        "OnlineSecurity": "online_security",
        "OnlineBackup": "online_backup",
        "DeviceProtection": "device_protection",
        "TechSupport": "tech_support",
        "StreamingTV": "streaming_tv",
        "StreamingMovies": "streaming_movies",
        "Contract": "contract",
        "PaperlessBilling": "paperless_billing",
        "PaymentMethod": "payment_method",
        "MonthlyCharges": "monthly_charges",
        "TotalCharges": "total_charges",
        "Churn": "churn"
    }
    df = df.rename(columns=rename_dict)
    
    # 2. Clean 'total_charges' column
    # Some total_charges values are empty spaces (representing customers with tenure = 0)
    # We strip spaces first
    df['total_charges'] = df['total_charges'].astype(str).str.strip()
    
    # Find how many rows have blank/empty total_charges
    blank_mask = df['total_charges'] == ''
    num_blanks = blank_mask.sum()
    print(f"Found {num_blanks} rows with blank 'total_charges'.")
    
    # For these blank rows, verify their tenure is indeed 0
    if num_blanks > 0:
        tenures_for_blanks = df.loc[blank_mask, 'tenure'].unique()
        print(f"Tenures for blank total_charges rows: {tenures_for_blanks}")
        
        # Replace empty strings with 0.0
        df.loc[blank_mask, 'total_charges'] = '0.0'
        print("Replaced blank 'total_charges' values with 0.0 (since tenure = 0).")
    
    # Convert 'total_charges' to float
    df['total_charges'] = pd.to_numeric(df['total_charges'])
    
    # 3. Basic validation checks
    # Check for missing values in any column
    missing_counts = df.isnull().sum()
    print("Missing values after cleaning:")
    print(missing_counts[missing_counts > 0])
    if missing_counts.sum() == 0:
        print("No missing values remain.")
        
    # Check data types
    print("\nData Types after cleaning:")
    print(df.dtypes)
    
    # Calculate initial churn statistics
    churn_counts = df['churn'].value_counts()
    churn_rate = (churn_counts.get('Yes', 0) / len(df)) * 100
    print(f"\nInitial Churn Statistics:")
    print(f"Active Customers: {churn_counts.get('No', 0)}")
    print(f"Churned Customers: {churn_counts.get('Yes', 0)}")
    print(f"Churn Rate: {churn_rate:.2f}%")
    
    # Save cleaned dataset
    os.makedirs(cleaned_dir, exist_ok=True)
    df.to_csv(cleaned_path, index=False)
    print(f"\nCleaned dataset saved successfully to {cleaned_path}")
    print(f"Processed shape: {df.shape}")

if __name__ == "__main__":
    clean_dataset()
