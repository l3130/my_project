# repository.py
import csv
from pathlib import Path
from typing import List, Dict
from models import Transaction, Budget
from utils import resolve_data_path

def load_transactions(filename="data/transactions.csv") -> List[Transaction]:
    """Load transactions from CSV and return as Transaction objects."""
    file_path = resolve_data_path(filename, writable=True)
    
    if not file_path.exists():
        return []  # Return empty list if file doesn't exist
    
    transactions = []
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                # Skip empty rows or header row
                if not row or row[0].strip().lower() == "amount":
                    continue
                
                try:
                    amount = float(row[0])
                    category = row[1].strip()
                    date = row[2].strip()
                    
                    # Create Transaction object
                    transaction = Transaction(amount=amount, category=category, date=date)
                    transactions.append(transaction)
                except (IndexError, ValueError):
                    # Skip malformed rows
                    continue
    except FileNotFoundError:
        return []
    
    return transactions

def save_transactions(transactions: List[Transaction], filename="data/transactions.csv") -> None:
    """Save Transaction objects to CSV."""
    file_path = resolve_data_path(filename, writable=True)
    
    # Create directory if needed
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            
            # Write header
            writer.writerow(["amount", "category", "date"])
            
            # Write each transaction
            for t in transactions:
                writer.writerow([t.amount, t.category, t.date])
    except Exception as e:
        print(f"❌ Failed to save transactions: {e}")

def load_category_budgets(filename="data/category_budgets.csv") -> Dict[str, float]:
    """Load category budgets from CSV."""
    file_path = resolve_data_path(filename, writable=True)
    
    if not file_path.exists():
        return {}  # Return empty dict if file doesn't exist
    
    budgets = {}
    try:
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                # Skip empty rows or header
                if not row or row[0].strip().lower().startswith("category"):
                    continue
                
                try:
                    category = row[0].strip()
                    limit = float(row[1])
                    budgets[category] = limit
                except (IndexError, ValueError):
                    # Skip malformed rows
                    continue
    except FileNotFoundError:
        return {}
    
    return budgets

def save_category_budgets(budgets: Dict[str, float], filename="data/category_budgets.csv") -> None:
    """Save category budgets to CSV."""
    file_path = resolve_data_path(filename, writable=True)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(file_path, mode="w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["category", "limit"])
            for category, limit in budgets.items():
                writer.writerow([category, limit])
    except Exception as e:
        print(f"❌ Failed to save budgets: {e}")