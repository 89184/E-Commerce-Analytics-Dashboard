import mysql.connector
import pandas as pd

DB_CONFIG = {
    'host': 'localhost',
    'user': 'ecommerce_user',       # New user
    'password': 'ecommerce123',     # New password
    'database': 'ecommerce_analytics'
}

def run_queries():
    """Run all analysis queries."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
    except mysql.connector.Error as e:
        print(f"❌ Connection error: {e}")
        print("\n💡 Make sure you have created the user and database:")
        print("   sudo mysql -u root -p")
        print("   CREATE USER 'ecommerce_user'@'localhost' IDENTIFIED BY 'ecommerce123';")
        print("   GRANT ALL PRIVILEGES ON ecommerce_analytics.* TO 'ecommerce_user'@'localhost';")
        return
    
    print("=" * 60)
    print("📊 E-COMMERCE ANALYTICS - MYSQL QUERIES")
    print("=" * 60)
    
    # Check if data exists
    cursor.execute("SELECT COUNT(*) FROM transactions")
    count = cursor.fetchone()[0]
    
    if count == 0:
        print("\n⚠️ No data found in transactions table!")
        print("Please load data first:")
        print("  python sql/load_data_to_mysql.py")
        return
    
    print(f"\n📊 Analyzing {count:,} records...")
    
    # 1. Total Revenue
    cursor.execute("SELECT SUM(total_amount) FROM transactions")
    result = cursor.fetchone()
    print(f"\n💰 Total Revenue: ₹{result[0]:,.2f}" if result[0] else "No data")
    
    # 2. Revenue by Category
    print("\n🏷️ REVENUE BY CATEGORY:")
    cursor.execute("""
        SELECT category, ROUND(SUM(total_amount), 2) as revenue
        FROM transactions
        GROUP BY category
        ORDER BY revenue DESC
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]}: ₹{row[1]:,.2f}")
    
    # 3. Monthly Revenue
    print("\n📈 MONTHLY REVENUE (First 6 months):")
    cursor.execute("""
        SELECT DATE_FORMAT(transaction_date, '%Y-%m') as month,
               ROUND(SUM(total_amount), 2) as revenue
        FROM transactions
        GROUP BY month
        ORDER BY month
        LIMIT 6
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]}: ₹{row[1]:,.2f}")
    
    # 4. Payment Methods
    print("\n💳 PAYMENT METHODS:")
    cursor.execute("""
        SELECT payment_method, 
               COUNT(*) as order_count,
               ROUND(SUM(total_amount), 2) as revenue
        FROM transactions
        GROUP BY payment_method
        ORDER BY revenue DESC
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} orders, ₹{row[2]:,.2f} revenue")
    
    # 5. Top Products
    print("\n🏆 TOP 5 PRODUCTS BY REVENUE:")
    cursor.execute("""
        SELECT product_name, ROUND(SUM(total_amount), 2) as revenue
        FROM transactions
        GROUP BY product_name
        ORDER BY revenue DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]}: ₹{row[1]:,.2f}")
    
    # 6. Customer Stats
    cursor.execute("""
        SELECT 
            COUNT(DISTINCT customer_id) as unique_customers,
            ROUND(AVG(total_amount), 2) as avg_order_value
        FROM transactions
    """)
    row = cursor.fetchone()
    print(f"\n👥 Customer Stats:")
    print(f"  - Unique Customers: {row[0]:,}")
    print(f"  - Avg Order Value: ₹{row[1]:,.2f}")
    
    # 7. City Performance
    print("\n📍 TOP 5 CITIES BY REVENUE:")
    cursor.execute("""
        SELECT customer_city, ROUND(SUM(total_amount), 2) as revenue
        FROM transactions
        GROUP BY customer_city
        ORDER BY revenue DESC
        LIMIT 5
    """)
    for row in cursor.fetchall():
        print(f"  - {row[0]}: ₹{row[1]:,.2f}")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    print("✅ QUERIES COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    run_queries()