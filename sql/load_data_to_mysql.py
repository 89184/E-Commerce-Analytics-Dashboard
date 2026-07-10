import mysql.connector
import pandas as pd
import os

DB_CONFIG = {
    'host': 'localhost',
    'user': 'ecommerce_user',
    'password': 'ecommerce123',
    'database': 'ecommerce_analytics'
}

def load_data():
    """Load data from CSV into MySQL."""
    csv_path = 'data/processed/clean_transactions.csv'
    
    if not os.path.exists(csv_path):
        print(f" CSV file not found: {csv_path}")
        print("Please run: python -m src.main first")
        return False
    
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except mysql.connector.Error as e:
        print(f" Connection error: {e}")
        return False
    
    # Read CSV
    df = pd.read_csv(csv_path)
    df['transaction_date'] = pd.to_datetime(df['date'])
    
    print(f" Loading {len(df)} records into MySQL...")
    
    # Clear existing data
    cursor.execute("TRUNCATE TABLE transactions")
    
    # Insert data
    inserted = 0
    for _, row in df.iterrows():
        try:
            cursor.execute("""
                INSERT INTO transactions 
                (transaction_id, transaction_date, customer_id, category, product_name, 
                 quantity, unit_price, total_amount, payment_method, customer_age, 
                 customer_city, year, month, quarter, weekday)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                row['transaction_id'],
                row['transaction_date'].date(),
                row['customer_id'],
                row['category'],
                row['product_name'],
                int(row['quantity']),
                float(row['unit_price']),
                float(row['total_amount']),
                row['payment_method'],
                int(row['customer_age']) if pd.notna(row['customer_age']) else None,
                row['customer_city'],
                int(row['year']),
                int(row['month']),
                int(row['quarter']),
                row['weekday']
            ))
            inserted += 1
            if inserted % 5000 == 0:
                print(f"  Inserted {inserted} records...")
        except Exception as e:
            print(f" Error inserting {row['transaction_id']}: {e}")
    
    conn.commit()
    print(f" Loaded {inserted} records into transactions table")
    
    cursor.close()
    conn.close()
    return True

if __name__ == "__main__":
    print("=" * 60)
    print(" LOADING DATA INTO MYSQL")
    print("=" * 60)
    load_data()