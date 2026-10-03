# models.py
from dataclasses import dataclass
from utils import normalize_date

@dataclass
class Transaction:
    amount: float
    category: str
    date: str
    
    def __post_init__(self):
        """Validate and normalize the transaction data."""
        # Validate amount
        if self.amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Validate category
        self.category = self.category.strip()
        if not self.category:
            raise ValueError("Category cannot be empty")
        
        # Normalize date to YYYY-MM-DD
        try:
            self.date = normalize_date(self.date)
        except ValueError as e:
            raise ValueError(f"Invalid date: {e}")

@dataclass
class Budget:
    category: str
    limit: float
    
    def __post_init__(self):
        """Validate the budget data."""
        # Validate category
        self.category = self.category.strip()
        if not self.category:
            raise ValueError("Category cannot be empty")
        
        # Validate limit
        if self.limit <= 0:
            raise ValueError("Budget limit must be positive")