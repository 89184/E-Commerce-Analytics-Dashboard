"""
Feature Engineering Module
---------------------------
Builds features for analysis and modeling.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def build_rfm_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build RFM (Recency, Frequency, Monetary) features.
    
    Args:
        df: Transaction DataFrame
    
    Returns:
        DataFrame with RFM features
    """
    logger.info("Building RFM features...")
    
    latest_date = df['date'].max()
    
    rfm = df.groupby('customer_id').agg({
        'date': lambda x: (latest_date - x.max()).days,
        'transaction_id': 'count',
        'total_amount': 'sum'
    }).rename(columns={
        'date': 'recency',
        'transaction_id': 'frequency',
        'total_amount': 'monetary'
    })
    
    # Assign RFM scores (1-5)
    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['f_score'] = pd.qcut(rfm['frequency'], 5, labels=[1, 2, 3, 4, 5])
    rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])
    
    # Calculate RFM score
    rfm['rfm_score'] = rfm['r_score'].astype(int) + rfm['f_score'].astype(int) + rfm['m_score'].astype(int)
    
    # Segment customers
    def get_segment(score):
        if score >= 13:
            return 'Champions'
        elif score >= 10:
            return 'Loyal Customers'
        elif score >= 7:
            return 'Potential Loyalists'
        elif score >= 4:
            return 'At Risk'
        else:
            return 'Need Attention'
    
    rfm['segment'] = rfm['rfm_score'].apply(get_segment)
    
    logger.info(f"RFM features built for {len(rfm)} customers")
    return rfm


def build_product_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Build product performance features.
    
    Args:
        df: Transaction DataFrame
    
    Returns:
        DataFrame with product features
    """
    logger.info("Building product features...")
    
    product_features = df.groupby(['category', 'product_name']).agg({
        'transaction_id': 'count',
        'quantity': 'sum',
        'total_amount': 'sum',
        'unit_price': 'mean'
    }).rename(columns={
        'transaction_id': 'units_sold',
        'quantity': 'total_quantity',
        'total_amount': 'total_revenue',
        'unit_price': 'avg_price'
    }).reset_index()
    
    # Calculate performance metrics
    product_features['revenue_per_unit'] = product_features['total_revenue'] / product_features['total_quantity']
    product_features['turnover_rate'] = product_features['total_quantity'] / product_features['total_quantity'].max()
    
    # Performance tier
    product_features['performance_tier'] = pd.cut(
        product_features['turnover_rate'],
        bins=[0, 0.25, 0.5, 0.75, 1.0],
        labels=['Low', 'Medium', 'High', 'Very High']
    )
    
    logger.info(f"Product features built for {len(product_features)} products")
    return product_features