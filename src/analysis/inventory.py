"""
Inventory Optimization Module
-------------------------------
Identifies underperforming products for inventory optimization.
"""

import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


def analyze_inventory(df: pd.DataFrame) -> dict:
    """
    Analyze inventory performance and identify optimization opportunities.
    
    Args:
        df: Transaction DataFrame
    
    Returns:
        Dictionary with inventory analysis results
    """
    logger.info("Analyzing inventory performance...")
    
    # Product performance
    product_perf = df.groupby(['category', 'product_name']).agg({
        'transaction_id': 'count',
        'quantity': 'sum',
        'total_amount': 'sum'
    }).rename(columns={
        'transaction_id': 'units_sold',
        'quantity': 'total_quantity',
        'total_amount': 'total_revenue'
    }).reset_index()
    
    # Calculate performance metrics
    product_perf['avg_price'] = product_perf['total_revenue'] / product_perf['total_quantity']
    product_perf['revenue_per_unit'] = product_perf['total_revenue'] / product_perf['units_sold']
    
    # Performance score (normalized)
    product_perf['performance_score'] = (
        (product_perf['units_sold'] / product_perf['units_sold'].max()) * 0.4 +
        (product_perf['total_revenue'] / product_perf['total_revenue'].max()) * 0.4 +
        (product_perf['avg_price'] / product_perf['avg_price'].max()) * 0.2
    )
    
    # Performance tier
    product_perf['performance_tier'] = pd.cut(
        product_perf['performance_score'],
        bins=[0, 0.2, 0.4, 0.6, 0.8, 1.0],
        labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
    )
    
    # Identify underperforming products
    underperforming = product_perf[product_perf['performance_tier'].isin(['Very Low', 'Low'])]
    
    results = {
        'total_products': len(product_perf),
        'underperforming_count': len(underperforming),
        'underperforming_share': len(underperforming) / len(product_perf) * 100,
        'optimization_target': 0.20,  # 20% reduction recommendation
        'underperforming_products': underperforming.to_dict('records'),
        'product_performance': product_perf
    }
    
    logger.info(f"Found {len(underperforming)} underperforming products")
    return results


def get_inventory_recommendations(analysis_results: dict) -> list:
    """
    Generate inventory optimization recommendations.
    
    Args:
        analysis_results: Results from analyze_inventory
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    underperforming = analysis_results['underperforming_products']
    optimization_target = analysis_results['optimization_target']
    
    if underperforming:
        recommendations.append(
            f"Consider reducing stock of {len(underperforming)} underperforming products "
            f"({analysis_results['underperforming_share']:.1f}% of inventory)"
        )
        
        # Top 5 underperformers
        top_underperformers = sorted(underperforming, key=lambda x: x['performance_score'])[:5]
        for product in top_underperformers:
            recommendations.append(
                f"  - {product['product_name']} ({product['category']}): "
                f"{product['units_sold']} units sold, ₹{product['total_revenue']:,.2f} revenue"
            )
        
        recommendations.append(
            f"Potential inventory reduction: {optimization_target * 100:.0f}% of slow-moving stock"
        )
    
    return recommendations