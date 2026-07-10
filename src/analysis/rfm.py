"""
RFM Analysis Module
--------------------
Customer segmentation using Recency, Frequency, Monetary analysis.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def perform_rfm_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """
    Perform complete RFM analysis.
    
    Args:
        df: Transaction DataFrame
    
    Returns:
        DataFrame with RFM scores and segments (customer_id is a column)
    """
    logger.info("Performing RFM analysis...")
    
    latest_date = df['date'].max()
    
    # Calculate RFM metrics
    rfm = df.groupby('customer_id').agg({
        'date': lambda x: (latest_date - x.max()).days,
        'transaction_id': 'count',
        'total_amount': 'sum'
    }).rename(columns={
        'date': 'recency',
        'transaction_id': 'frequency',
        'total_amount': 'monetary'
    })
    
    # Assign scores (1-5)
    rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
    rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    rfm['m_score'] = pd.qcut(rfm['monetary'].rank(method='first'), 5, labels=[1, 2, 3, 4, 5])
    
    # RFM score
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
    
    # Reset index to make customer_id a column
    rfm = rfm.reset_index()
    
    logger.info(f"RFM analysis complete: {len(rfm)} customers segmented")
    return rfm


def get_segment_summary(rfm_df: pd.DataFrame) -> pd.DataFrame:
    """
    Get summary statistics by segment.
    
    Args:
        rfm_df: RFM DataFrame with customer_id as a column
    
    Returns:
        Summary DataFrame
    """
    summary = rfm_df.groupby('segment').agg({
        'customer_id': 'count',
        'recency': 'mean',
        'frequency': 'mean',
        'monetary': 'mean',
        'rfm_score': 'mean'
    }).rename(columns={
        'customer_id': 'customer_count'
    }).reset_index()
    
    summary['percentage'] = (summary['customer_count'] / summary['customer_count'].sum()) * 100
    
    return summary.sort_values('customer_count', ascending=False)