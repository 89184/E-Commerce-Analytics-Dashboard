"""
Visualization Module
----------------------
Generates charts and plots for analysis.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)


def set_style():
    """Set consistent plotting style."""
    sns.set_style('darkgrid')
    sns.set_palette('husl')
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['font.size'] = 10


def plot_monthly_revenue(df: pd.DataFrame, output_path: str = None):
    """
    Plot monthly revenue trend.
    
    Args:
        df: Transaction DataFrame
        output_path: Path to save figure
    """
    logger.info("Plotting monthly revenue...")
    set_style()
    
    monthly_revenue = df.groupby(df['date'].dt.to_period('M'))['total_amount'].sum()
    
    fig, ax = plt.subplots(figsize=(12, 6))
    monthly_revenue.plot(kind='bar', ax=ax, color='skyblue', edgecolor='navy')
    
    ax.set_title('Monthly Revenue Trend', fontsize=14, fontweight='bold')
    ax.set_xlabel('Month', fontsize=12)
    ax.set_ylabel('Total Revenue (₹)', fontsize=12)
    ax.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
    
    return fig


def plot_category_revenue(df: pd.DataFrame, output_path: str = None):
    """
    Plot revenue by category.
    
    Args:
        df: Transaction DataFrame
        output_path: Path to save figure
    """
    logger.info("Plotting category revenue...")
    set_style()
    
    category_revenue = df.groupby('category')['total_amount'].sum().sort_values()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    category_revenue.plot(kind='barh', ax=ax, color='lightcoral', edgecolor='darkred')
    
    ax.set_title('Revenue by Category', fontsize=14, fontweight='bold')
    ax.set_xlabel('Total Revenue (₹)', fontsize=12)
    ax.set_ylabel('Category', fontsize=12)
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
    
    return fig


def plot_transaction_distribution(df: pd.DataFrame, output_path: str = None):
    """
    Plot transaction value distribution.
    
    Args:
        df: Transaction DataFrame
        output_path: Path to save figure
    """
    logger.info("Plotting transaction distribution...")
    set_style()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.hist(df['total_amount'], bins=50, color='purple', alpha=0.7, edgecolor='black')
    ax.axvline(df['total_amount'].mean(), color='red', linestyle='dashed',
               linewidth=2, label=f'Mean: ₹{df["total_amount"].mean():.2f}')
    ax.axvline(df['total_amount'].median(), color='blue', linestyle='dashed',
               linewidth=2, label=f'Median: ₹{df["total_amount"].median():.2f}')
    
    ax.set_title('Transaction Value Distribution', fontsize=14, fontweight='bold')
    ax.set_xlabel('Transaction Amount (₹)', fontsize=12)
    ax.set_ylabel('Frequency', fontsize=12)
    ax.legend()
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
    
    return fig


def plot_payment_methods(df: pd.DataFrame, output_path: str = None):
    """
    Plot payment method distribution.
    
    Args:
        df: Transaction DataFrame
        output_path: Path to save figure
    """
    logger.info("Plotting payment methods...")
    set_style()
    
    payment_counts = df['payment_method'].value_counts()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    colors = ['#66b3ff', '#99ff99', '#ffcc99', '#ff9999', '#c2c2f0']
    payment_counts.plot(kind='pie', ax=ax, autopct='%1.1f%%', colors=colors)
    
    ax.set_title('Payment Method Distribution', fontsize=14, fontweight='bold')
    ax.set_ylabel('')
    
    plt.tight_layout()
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved: {output_path}")
    
    return fig


def generate_all_plots(df: pd.DataFrame, output_dir: str = 'outputs/figures/'):
    """
    Generate all visualization plots.
    
    Args:
        df: Transaction DataFrame
        output_dir: Output directory for figures
    """
    logger.info("Generating all plots...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    plot_monthly_revenue(df, os.path.join(output_dir, 'monthly_revenue.png'))
    plot_category_revenue(df, os.path.join(output_dir, 'category_revenue.png'))
    plot_transaction_distribution(df, os.path.join(output_dir, 'transaction_distribution.png'))
    plot_payment_methods(df, os.path.join(output_dir, 'payment_methods.png'))
    
    logger.info(f"All plots saved to {output_dir}")