# tests/test_services.py
import pytest

from models import Transaction
from services import calculate_total_spending, calculate_spending_by_category


def test_calculate_total_spending():
    transactions = [
        Transaction(amount=50.0, category="Food", date="2026-09-29"),
        Transaction(amount=20.0, category="Transport", date="2026-09-30"),
        Transaction(amount=10.0, category="Food", date="2026-10-01"),
    ]

    total = calculate_total_spending(transactions)
    assert total == 80.0


def test_calculate_spending_by_category():
    transactions = [
        Transaction(amount=50.0, category="Food", date="2026-09-29"),
        Transaction(amount=20.0, category="Transport", date="2026-09-30"),
        Transaction(amount=10.0, category="Food", date="2026-10-01"),
    ]

    result = calculate_spending_by_category(transactions)

    assert result["Food"] == 60.0
    assert result["Transport"] == 20.0


def test_calculate_total_spending_empty_list():
    transactions = []
    assert calculate_total_spending(transactions) == 0.0


def test_calculate_spending_by_category_empty_list():
    transactions = []
    assert calculate_spending_by_category(transactions) == {}