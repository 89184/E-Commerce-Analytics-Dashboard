"""
Exploratory Data Analysis Module
----------------------------------
Performs EDA on transaction data.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def calculate_kpis(df: pd.DataFrame) -> dict:
    """
    Calculate key performance indicators.
    
    Args:
        df: Transaction DataFrame
    
    Returns:
        Dictionary of KPIs
    """
    logger.info("Calculating KPIs...")
    
    total_revenue = df['total_amount'].sum()
    total_orders = len(df)
    unique_customers = df['customer_id'].nunique()
    avg_order_value = df['total_amount'].mean()
    
    # Repeat purchase rate
    repeat_customers = df.groupby('customer_id')['transaction_id'].count()
    repeat_rate = len(repeat_customers[repeat_customers > 1]) / len(repeat_customers) * 100
    
    # Customer lifetime value
    clv = total_revenue / unique_customers if unique_customers > 0 else 0
    
    kpis = {
        'total_revenue': float(total_revenue),
        'total_orders': int(total_orders),
        'unique_customers': int(unique_customers),
        'avg_order_value': float(avg_order_value),
        'repeat_purchase_rate': float(repeat_rate),
        'customer_lifetime_value': float(clv)
    }
    
    logger.info(f"KPIs calculated: {kpis}")
    return kpis


def analyze_category_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze performance by category.
    
    Args:
        df: Transaction DataFrame
    
    Returns:
        DataFrame with category performance metrics
    """
    logger.info("Analyzing category performance...")
    
    # Use named aggregation to avoid duplicate column names
    category_perf = df.groupby('category').agg(
        order_count=('transaction_id', 'count'),
        total_units_sold=('quantity', 'sum'),
        total_revenue=('total_amount', 'sum'),
        avg_order_value=('total_amount', 'mean')
    ).reset_index()
    
    # Calculate revenue share
    category_perf['revenue_share'] = (category_perf['total_revenue'] / category_perf['total_revenue'].sum()) * 100
    
    logger.info(f"Analyzed {len(category_perf)} categories")
    return category_perf.sort_values('total_revenue', ascending=False)


def analyze_time_trends(df: pd.DataFrame) -> dict:
    """
    Analyze time-based trends.
    
    Args:
        df: Transaction DataFrame
    
    Returns:
        Dictionary with time trend analysis
    """
    logger.info("Analyzing time trends...")
    
    # Ensure date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # Monthly revenue
    monthly_revenue = df.groupby(df['date'].dt.to_period('M'))['total_amount'].sum()
    
    # Weekly patterns
    weekly_avg = df.groupby(df['date'].dt.dayofweek)['total_amount'].mean()
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekly_pattern = dict(zip(days, weekly_avg.values))
    
    # Best and worst months
    monthly_avg = df.groupby(df['date'].dt.month)['total_amount'].mean()
    
    results = {
        'monthly_revenue': monthly_revenue.to_dict(),
        'weekly_pattern': weekly_pattern,
        'best_month': int(monthly_avg.idxmax()) if not monthly_avg.empty else None,
        'worst_month': int(monthly_avg.idxmin()) if not monthly_avg.empty else None,
        'avg_monthly_revenue': float(monthly_avg.mean()) if not monthly_avg.empty else 0.0,
        'growth_rate': float(monthly_revenue.pct_change().mean() * 100) if len(monthly_revenue) > 1 else 0.0
    }
    
    logger.info("Time trend analysis complete")
    return results