"""
download_data.py
Sourced from: IBM Telco Customer Churn Dataset (public repository)
Description: Downloads the raw dataset and saves it to data/raw/customer_churn_raw.csv
"""

import os
import urllib.request

def download_dataset():
    # URL to the raw dataset on GitHub
    url = "https://raw.githubusercontent.com/IBM/telco-customer-churn-on-icp4d/master/data/Telco-Customer-Churn.csv"
    
    # Destination paths
    output_dir = os.path.join("data", "raw")
    output_path = os.path.join(output_dir, "customer_churn_raw.csv")
    
    print(f"Starting download from {url}...")
    try:
        # Fetch the dataset
        urllib.request.urlretrieve(url, output_path)
        print(f"Download complete! Saved to {output_path}")
        
        # Verify file size
        file_size_kb = os.path.getsize(output_path) / 1024
        print(f"File size: {file_size_kb:.2f} KB")
        
    except Exception as e:
        print(f"Error downloading dataset: {e}")

if __name__ == "__main__":
    download_dataset()
