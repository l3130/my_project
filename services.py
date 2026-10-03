# services.py
from typing import List, Dict
from models import Transaction

def calculate_spending_by_category(transactions: List[Transaction]) -> Dict[str, float]:
    """Group spending by category."""
    category_totals = {}
    for t in transactions:
        category_totals[t.category] = category_totals.get(t.category, 0) + t.amount
    return category_totals

def calculate_spending_by_date(transactions: List[Transaction]) -> Dict[str, float]:
    """Group spending by date."""
    date_totals = {}
    for t in transactions:
        date_totals[t.date] = date_totals.get(t.date, 0) + t.amount
    return date_totals

def calculate_total_spending(transactions: List[Transaction]) -> float:
    """Calculate total spending."""
    return sum(t.amount for t in transactions)

def check_budget_status(total_spending: float, budget_limit: float) -> str:
    """Check if spending is within budget."""
    if total_spending >= budget_limit:
        return "exceeded"
    elif total_spending >= 0.8 * budget_limit:
        return "warning"
    else:
        return "safe"

def check_category_budget_status(spent: float, limit: float) -> str:
    """Check category budget status."""
    if spent >= limit:
        return "exceeded"
    elif spent >= 0.8 * limit:
        return "warning"
    else:
        return "safe"