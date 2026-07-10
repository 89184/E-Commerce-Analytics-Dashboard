"""
Data Loading and Generation Module
-----------------------------------
Handles loading raw data and generating synthetic sample data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import logging

logger = logging.getLogger(__name__)


def generate_sample_data(n_records: int = 50000, random_seed: int = 42) -> pd.DataFrame:
    """Generate synthetic e‑commerce transaction data."""
    logger.info(f"Generating {n_records} synthetic transactions...")
    np.random.seed(random_seed)
    
    categories = ['Electronics', 'Clothing', 'Home & Kitchen', 'Books', 'Toys',
                  'Sports', 'Beauty', 'Automotive', 'Grocery', 'Furniture']
    products = {
        'Electronics': ['iPhone', 'Samsung TV', 'Laptop', 'Headphones', 'Smartwatch'],
        'Clothing': ['T-Shirt', 'Jeans', 'Jacket', 'Sneakers', 'Dress'],
        'Home & Kitchen': ['Blender', 'Microwave', 'Vacuum', 'Knife Set', 'Cookware'],
        'Books': ['Fiction Novel', 'Textbook', 'Cookbook', 'Biography', 'Sci-Fi'],
        'Toys': ['LEGO Set', 'Doll', 'Action Figure', 'Board Game', 'Puzzle'],
        'Sports': ['Football', 'Tennis Racket', 'Yoga Mat', 'Dumbbell', 'Bicycle'],
        'Beauty': ['Lipstick', 'Foundation', 'Perfume', 'Skincare', 'Hair Dryer'],
        'Automotive': ['Tire', 'Battery', 'Oil Filter', 'Car Cover', 'Dash Cam'],
        'Grocery': ['Rice', 'Flour', 'Sugar', 'Oil', 'Cereal'],
        'Furniture': ['Sofa', 'Chair', 'Table', 'Bed', 'Wardrobe']
    }
    
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    dates = [start_date + timedelta(days=np.random.randint(0, 365)) for _ in range(n_records)]
    
    cities = ['Mumbai', 'Delhi', 'Bangalore', 'Chennai', 'Hyderabad',
              'Kolkata', 'Pune', 'Ahmedabad', 'Surat', 'Jaipur']
    payment_methods = ['Credit Card', 'Debit Card', 'UPI', 'Net Banking', 'COD']
    
    data = {
        'transaction_id': [f'TXN{str(i).zfill(6)}' for i in range(1, n_records + 1)],
        'date': dates,
        'customer_id': [f'CUST{str(np.random.randint(1, 5001)).zfill(4)}' for _ in range(n_records)],
        'category': [np.random.choice(categories) for _ in range(n_records)],
        'product_name': [np.random.choice(products[np.random.choice(categories)]) for _ in range(n_records)],
        'quantity': np.random.randint(1, 10, n_records),
        'unit_price': np.round(np.random.uniform(5, 500, n_records), 2),
        'payment_method': np.random.choice(payment_methods, n_records),
        'customer_age': np.random.randint(18, 70, n_records),
        'customer_city': np.random.choice(cities, n_records),
    }
    
    df = pd.DataFrame(data)
    df['total_amount'] = df['quantity'] * df['unit_price']
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['quarter'] = df['date'].dt.quarter
    df['weekday'] = df['date'].dt.day_name()
    
    # Add some nulls
    null_indices = np.random.choice(df.index, size=int(0.02 * n_records), replace=False)
    df.loc[null_indices, 'customer_age'] = np.nan
    
    logger.info(f"Generated {len(df)} records")
    return df


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from CSV file with encoding fallback.
    
    Args:
        file_path: Path to CSV file
    
    Returns:
        DataFrame with loaded data, or None if file cannot be read
    """
    logger.info(f"Loading data from {file_path}")
    
    if not os.path.exists(file_path):
        logger.warning(f"File not found: {file_path}")
        return None
    
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']
    
    for encoding in encodings:
        try:
            sample = pd.read_csv(file_path, nrows=0, encoding=encoding)
            has_date = 'date' in sample.columns
            df = pd.read_csv(file_path, parse_dates=['date'] if has_date else None, encoding=encoding)
            logger.info(f"Loaded {len(df)} records with encoding {encoding}")
            return df
        except (UnicodeDecodeError, pd.errors.ParserError) as e:
            logger.warning(f"Failed with encoding {encoding}: {e}")
            continue
    
    logger.error("Could not read CSV file with any encoding.")
    return None


def save_data(df: pd.DataFrame, file_path: str) -> None:
    """Save DataFrame to CSV. If file_path is a directory, add default name."""
    # If path ends with slash, treat as directory and add default filename
    if file_path.endswith('/'):
        file_path = os.path.join(file_path, 'clean_transactions.csv')
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    df.to_csv(file_path, index=False)
    logger.info(f"Saved data to {file_path}")