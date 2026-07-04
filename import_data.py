"""
import_data.py
Description: Sets up the SQLite database, executes the schema, and imports the cleaned customer churn data.
"""

import os
import sqlite3
import pandas as pd

def import_to_sqlite():
    # File paths
    db_path = os.path.join("data", "churn_analysis.db")
    schema_path = os.path.join("sql", "schema.sql")
    csv_path = os.path.join("data", "processed", "customer_churn_clean.csv")
    
    # 1. Establish SQLite Connection
    print(f"Connecting to SQLite database at {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 2. Execute SQL Schema DDL
    print(f"Executing schema from {schema_path}...")
    try:
        with open(schema_path, 'r') as schema_file:
            schema_sql = schema_file.read()
        cursor.executescript(schema_sql)
        print("Database schema created successfully.")
    except Exception as e:
        print(f"Error executing schema: {e}")
        conn.close()
        return
        
    # 3. Load Cleaned CSV Data
    print(f"Loading cleaned CSV from {csv_path}...")
    try:
        df = pd.read_csv(csv_path)
        print(f"CSV loaded. Found {len(df)} records to import.")
    except Exception as e:
        print(f"Error loading CSV: {e}")
        conn.close()
        return
        
    # 4. Insert data into the SQLite customer_churn table
    print("Importing records into 'customer_churn' table...")
    try:
        # Use pandas to write directly to SQLite
        # if_exists='append' because the table has already been created by schema.sql
        df.to_sql("customer_churn", conn, if_exists="append", index=False)
        conn.commit()
        print("Data import committed successfully.")
    except Exception as e:
        print(f"Error inserting records: {e}")
        conn.rollback()
        conn.close()
        return
        
    # 5. Verify the insertion
    try:
        cursor.execute("SELECT COUNT(*) FROM customer_churn;")
        row_count = cursor.fetchone()[0]
        print(f"Verification complete: Table 'customer_churn' contains {row_count} rows.")
    except Exception as e:
        print(f"Error during verification: {e}")
        
    # Close connection
    conn.close()
    print("Database connection closed.")

if __name__ == "__main__":
    import_to_sqlite()
