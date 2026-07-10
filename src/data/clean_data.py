"""
Data Cleaning Module
---------------------
Handles data validation, cleaning, and preprocessing.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def validate_data(df: pd.DataFrame) -> dict:
    """
    Validate data quality and return validation report.
    
    Args:
        df: Input DataFrame
    
    Returns:
        Dictionary with validation metrics
    """
    logger.info("Validating data...")
    
    report = {
        'total_rows': len(df),
        'duplicates': df.duplicated(subset=['transaction_id']).sum(),
        'missing_values': df.isnull().sum().to_dict(),
        'negative_prices': (df['unit_price'] < 0).sum(),
        'negative_quantities': (df['quantity'] < 0).sum(),
        'invalid_dates': 0
    }
    
    # Check date validity
    if 'date' in df.columns:
        report['invalid_dates'] = df[pd.to_datetime(df['date'], errors='coerce').isna()].shape[0]
    
    logger.info(f"Validation complete: {report['total_rows']} rows")
    return report


def clean_transactions(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean transaction data.
    
    Args:
        df: Raw DataFrame
    
    Returns:
        Cleaned DataFrame
    """
    logger.info("Cleaning transaction data...")
    initial_rows = len(df)
    
    # Make a copy
    df_clean = df.copy()
    
    # Remove duplicates
    df_clean = df_clean.drop_duplicates(subset=['transaction_id'])
    logger.info(f"Removed duplicates: {initial_rows - len(df_clean)} rows")
    
    # Convert date to datetime
    if 'date' in df_clean.columns:
        df_clean['date'] = pd.to_datetime(df_clean['date'], errors='coerce')
        df_clean = df_clean.dropna(subset=['date'])
    
    # Handle missing values
    if 'customer_age' in df_clean.columns:
        df_clean['customer_age'] = df_clean['customer_age'].fillna(
            df_clean['customer_age'].median()
        )
    
    # Remove outliers (extreme prices - 99th percentile)
    if 'total_amount' in df_clean.columns:
        price_upper = df_clean['total_amount'].quantile(0.99)
        df_clean = df_clean[df_clean['total_amount'] <= price_upper]
        logger.info(f"Removed price outliers above 99th percentile")
    
    # Ensure no negative values
    if 'quantity' in df_clean.columns:
        df_clean = df_clean[df_clean['quantity'] > 0]
    
    if 'unit_price' in df_clean.columns:
        df_clean = df_clean[df_clean['unit_price'] > 0]
    
    # Add time features if not present
    if 'date' in df_clean.columns:
        df_clean['year'] = df_clean['date'].dt.year
        df_clean['month'] = df_clean['date'].dt.month
        df_clean['quarter'] = df_clean['date'].dt.quarter
        df_clean['weekday'] = df_clean['date'].dt.day_name()
        df_clean['year_month'] = df_clean['date'].dt.to_period('M').astype(str)
    
    logger.info(f"Cleaning complete: {len(df_clean)} rows (removed {initial_rows - len(df_clean)})")
    return df_clean


def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add derived features for analysis.
    
    Args:
        df: Cleaned DataFrame
    
    Returns:
        DataFrame with additional features
    """
    logger.info("Adding derived features...")
    
    df = df.copy()
    
    # Customer metrics
    customer_metrics = df.groupby('customer_id').agg({
        'transaction_id': 'count',
        'total_amount': 'sum'
    }).rename(columns={
        'transaction_id': 'customer_order_count',
        'total_amount': 'customer_total_spent'
    })
    
    df = df.merge(customer_metrics, on='customer_id', how='left')
    
    # Product metrics
    product_metrics = df.groupby(['category', 'product_name']).agg({
        'transaction_id': 'count',
        'total_amount': 'sum',
        'quantity': 'sum'
    }).rename(columns={
        'transaction_id': 'product_units_sold',
        'total_amount': 'product_revenue',
        'quantity': 'product_total_quantity'
    }).reset_index()
    
    df = df.merge(product_metrics, on=['category', 'product_name'], how='left')
    
    return df