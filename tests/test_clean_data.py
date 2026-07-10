import pytest
import pandas as pd
import numpy as np
from src.data.clean_data import clean_transactions, validate_data

def test_validate_data():
    df = pd.DataFrame({
        'transaction_id': ['TXN001', 'TXN002'],
        'date': ['2024-01-01', '2024-01-02'],
        'unit_price': [100, 200],
        'quantity': [1, 2]
    })
    report = validate_data(df)
    assert report['total_rows'] == 2
    assert report['duplicates'] == 0

def test_clean_transactions():
    df = pd.DataFrame({
        'transaction_id': ['TXN001', 'TXN002', 'TXN001'],
        'date': ['2024-01-01', '2024-01-02', '2024-01-03'],
        'unit_price': [100, -50, 200],
        'quantity': [1, 2, -1],
        'total_amount': [100, -100, -200]
    })
    cleaned = clean_transactions(df)
    assert len(cleaned) > 0
    assert (cleaned['unit_price'] > 0).all()
    assert (cleaned['quantity'] > 0).all()