"""
Power BI Export Module
-----------------------
Exports processed data for Power BI dashboard.
"""

import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)


def export_for_powerbi(df: pd.DataFrame, rfm_df: pd.DataFrame, 
                       product_df: pd.DataFrame, output_dir: str = 'powerbi/'):
    """
    Export data for Power BI dashboard.
    
    Args:
        df: Cleaned transaction DataFrame
        rfm_df: RFM analysis DataFrame (must have 'customer_id' column)
        product_df: Product performance DataFrame
        output_dir: Output directory
    """
    logger.info("Exporting data for Power BI...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # 1. Fact table: Transactions
    fact = df.copy()
    fact['year_month'] = fact['date'].dt.to_period('M').astype(str)
    fact['quarter'] = fact['date'].dt.quarter
    fact['year'] = fact['date'].dt.year
    fact['month_name'] = fact['date'].dt.month_name()
    fact['day_name'] = fact['date'].dt.day_name()
    fact.to_csv(os.path.join(output_dir, 'fact_transactions.csv'), index=False)
    logger.info(f"  - Exported: fact_transactions.csv ({len(fact)} rows)")
    
    # 2. Dimension: Date
    date_dim = pd.DataFrame({
        'date': pd.date_range(df['date'].min(), df['date'].max(), freq='D')
    })
    date_dim['year'] = date_dim['date'].dt.year
    date_dim['month'] = date_dim['date'].dt.month
    date_dim['month_name'] = date_dim['date'].dt.month_name()
    date_dim['quarter'] = date_dim['date'].dt.quarter
    date_dim['day_of_week'] = date_dim['date'].dt.day_name()
    date_dim['is_weekend'] = date_dim['date'].dt.dayofweek >= 5
    date_dim.to_csv(os.path.join(output_dir, 'dim_date.csv'), index=False)
    logger.info(f"  - Exported: dim_date.csv ({len(date_dim)} rows)")
    
    # 3. Dimension: Customer
    customer_dim = df.groupby('customer_id').agg({
        'customer_age': 'first',
        'customer_city': 'first'
    }).reset_index()
    
    # Add first purchase date
    first_purchase = df.groupby('customer_id')['date'].min().reset_index()
    customer_dim = customer_dim.merge(first_purchase, on='customer_id', how='left')
    customer_dim = customer_dim.rename(columns={'date': 'first_purchase_date'})
    
    # Add total spent and order count
    customer_metrics = df.groupby('customer_id').agg({
        'total_amount': 'sum',
        'transaction_id': 'count'
    }).reset_index().rename(columns={
        'total_amount': 'total_spent',
        'transaction_id': 'order_count'
    })
    customer_dim = customer_dim.merge(customer_metrics, on='customer_id', how='left')
    
    # Add RFM segments - ensure customer_id exists in rfm_df
    if 'customer_id' in rfm_df.columns:
        customer_dim = customer_dim.merge(
            rfm_df[['customer_id', 'segment', 'rfm_score']],
            on='customer_id',
            how='left'
        )
    else:
        logger.warning("RFM DataFrame missing 'customer_id' column. Skipping RFM merge.")
        # Add default values
        customer_dim['segment'] = 'Unknown'
        customer_dim['rfm_score'] = 0
    
    customer_dim.to_csv(os.path.join(output_dir, 'dim_customer.csv'), index=False)
    logger.info(f"  - Exported: dim_customer.csv ({len(customer_dim)} rows)")
    
    # 4. Dimension: Product
    product_dim = product_df.copy()
    product_dim.to_csv(os.path.join(output_dir, 'dim_product.csv'), index=False)
    logger.info(f"  - Exported: dim_product.csv ({len(product_dim)} rows)")
    
    # 5. Inventory metrics
    inventory_metrics = df.groupby(['category', 'product_name']).agg({
        'quantity': 'sum',
        'total_amount': 'sum',
        'transaction_id': 'count'
    }).rename(columns={
        'quantity': 'units_sold',
        'total_amount': 'revenue',
        'transaction_id': 'order_count'
    }).reset_index()
    
    inventory_metrics['avg_price'] = inventory_metrics['revenue'] / inventory_metrics['units_sold']
    inventory_metrics['turnover_rate'] = inventory_metrics['units_sold'] / inventory_metrics['units_sold'].max()
    inventory_metrics['performance_tier'] = pd.cut(
        inventory_metrics['turnover_rate'],
        bins=[0, 0.25, 0.5, 0.75, 1.0],
        labels=['Low', 'Medium', 'High', 'Very High']
    )
    inventory_metrics.to_csv(os.path.join(output_dir, 'inventory_metrics.csv'), index=False)
    logger.info(f"  - Exported: inventory_metrics.csv ({len(inventory_metrics)} rows)")
    
    logger.info(f"Power BI export complete! Files saved to {output_dir}")