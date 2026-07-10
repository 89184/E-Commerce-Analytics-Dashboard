import sqlite3
import pandas as pd
import os

# ============================================
# SQLITE DATABASE SETUP
# ============================================

DB_PATH = 'ecommerce_analytics.db'

def create_connection():
    """Create a database connection."""
    conn = sqlite3.connect(DB_PATH)
    return conn

def create_tables(conn):
    """Create all tables."""
    cursor = conn.cursor()
    
    # Create transactions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            transaction_id TEXT PRIMARY KEY,
            transaction_date DATE,
            customer_id TEXT,
            category TEXT,
            product_name TEXT,
            quantity INTEGER,
            unit_price REAL,
            total_amount REAL,
            payment_method TEXT,
            customer_age INTEGER,
            customer_city TEXT,
            year INTEGER,
            month INTEGER,
            quarter INTEGER,
            weekday TEXT
        )
    ''')
    
    # Create customer dimension
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dim_customers (
            customer_id TEXT PRIMARY KEY,
            customer_age INTEGER,
            customer_city TEXT,
            first_purchase_date DATE,
            total_spent REAL,
            order_count INTEGER
        )
    ''')
    
    conn.commit()
    print(" Tables created successfully")

def load_data_from_csv(conn, csv_path='data/processed/clean_transactions.csv'):
    """Load data from CSV into SQLite."""
    if not os.path.exists(csv_path):
        print(f" CSV file not found: {csv_path}")
        print("Please run: python -m src.main first")
        return
    
    df = pd.read_csv(csv_path)
    df['transaction_date'] = pd.to_datetime(df['date'])
    
    # Insert into transactions
    df.to_sql('transactions', conn, if_exists='replace', index=False)
    print(f" Loaded {len(df)} records into transactions table")
    
    # Create customer dimension
    customer_dim = df.groupby('customer_id').agg({
        'customer_age': 'first',
        'customer_city': 'first',
        'transaction_date': 'min',
        'total_amount': 'sum',
        'transaction_id': 'count'
    }).reset_index()
    
    customer_dim.columns = ['customer_id', 'customer_age', 'customer_city', 
                            'first_purchase_date', 'total_spent', 'order_count']
    customer_dim.to_sql('dim_customers', conn, if_exists='replace', index=False)
    print(f" Loaded {len(customer_dim)} records into dim_customers")

def run_queries(conn):
    """Run sample queries."""
    cursor = conn.cursor()
    
    # Query 1: Total Revenue
    cursor.execute("SELECT SUM(total_amount) FROM transactions")
    result = cursor.fetchone()
    print(f"\n Total Revenue: ₹{result[0]:,.2f}")
    
    # Query 2: Revenue by Category
    cursor.execute('''
        SELECT category, SUM(total_amount) as revenue
        FROM transactions
        GROUP BY category
        ORDER BY revenue DESC
        LIMIT 5
    ''')
    print("\n Top 5 Categories:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: ₹{row[1]:,.2f}")
    
    # Query 3: Monthly Revenue
    cursor.execute('''
        SELECT strftime('%Y-%m', transaction_date) as month,
               SUM(total_amount) as revenue
        FROM transactions
        GROUP BY month
        ORDER BY month
    ''')
    print("\n Monthly Revenue (First 3 months):")
    for row in cursor.fetchall()[:3]:
        print(f"  - {row[0]}: ₹{row[1]:,.2f}")
    
    # Query 4: Payment Methods
    cursor.execute('''
        SELECT payment_method, COUNT(*) as count, SUM(total_amount) as revenue
        FROM transactions
        GROUP BY payment_method
        ORDER BY revenue DESC
    ''')
    print("\n Payment Methods:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} orders, ₹{row[2]:,.2f} revenue")

def main():
    """Main function to set up and run SQLite database."""
    print("=" * 60)
    print("SQLITE DATABASE SETUP")
    print("=" * 60)
    
    # Create connection
    conn = create_connection()
    
    # Create tables
    create_tables(conn)
    
    # Load data
    load_data_from_csv(conn)
    
    # Run queries
    run_queries(conn)
    
    # Close connection
    conn.close()
    print("\nDatabase setup complete!")
    print(f"Database file: {DB_PATH}")

if __name__ == "__main__":
    main()