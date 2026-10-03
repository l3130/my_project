# tests/test_repository.py
import pytest
import csv
from pathlib import Path
from tempfile import TemporaryDirectory

from repository import load_transactions, save_transactions, load_category_budgets, save_category_budgets
from models import Transaction, Budget
from utils import resolve_data_path


class TestLoadTransactions:
    """Test loading transactions from CSV."""

    def test_load_transactions_empty_file(self):
        """Test loading from a non-existent file returns empty list."""
        transactions = load_transactions("data/nonexistent.csv")
        assert transactions == []

    def test_load_transactions_with_header_only(self):
        """Test loading a file with only header row."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_transactions.csv", writable=True)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["amount", "category", "date"])
        
        transactions = load_transactions("data/test_transactions.csv")
        assert transactions == []
        
        # Cleanup
        file_path.unlink()

    def test_load_transactions_single_valid_row(self):
        """Test loading a single valid transaction."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_transactions.csv", writable=True)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["amount", "category", "date"])
            writer.writerow(["50.0", "Food", "2026-09-29"])
        
        transactions = load_transactions("data/test_transactions.csv")
        
        assert len(transactions) == 1
        assert transactions[0].amount == 50.0
        assert transactions[0].category == "Food"
        assert transactions[0].date == "2026-09-29"
        
        # Cleanup
        file_path.unlink()

    def test_load_transactions_multiple_rows(self):
        """Test loading multiple transactions."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_transactions.csv", writable=True)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["amount", "category", "date"])
            writer.writerow(["50.0", "Food", "2026-09-29"])
            writer.writerow(["20.0", "Transport", "2026-09-30"])
            writer.writerow(["100.0", "Rent", "2026-10-01"])
        
        transactions = load_transactions("data/test_transactions.csv")
        
        assert len(transactions) == 3
        assert transactions[0].category == "Food"
        assert transactions[1].category == "Transport"
        assert transactions[2].category == "Rent"
        
        # Cleanup
        file_path.unlink()

    def test_load_transactions_skips_malformed_rows(self):
        """Test that malformed rows are skipped."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_transactions.csv", writable=True)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["amount", "category", "date"])
            writer.writerow(["50.0", "Food", "2026-09-29"])
            writer.writerow(["invalid", "Transport", "2026-09-30"])  # invalid amount
            writer.writerow(["100.0", "Rent"])  # missing date
            writer.writerow(["75.0", "Entertainment", "2026-10-02"])
        
        transactions = load_transactions("data/test_transactions.csv")
        
        # Should only load the 2 valid rows
        assert len(transactions) == 2
        assert transactions[0].category == "Food"
        assert transactions[1].category == "Entertainment"
        
        # Cleanup
        file_path.unlink()


class TestSaveTransactions:
    """Test saving transactions to CSV."""

    def test_save_transactions_creates_file(self):
        """Test that save_transactions creates a new file."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_save.csv", writable=True)
        
        # Cleanup if it exists
        if file_path.exists():
            file_path.unlink()
        
        transactions = [
            Transaction(amount=50.0, category="Food", date="2026-09-29"),
            Transaction(amount=20.0, category="Transport", date="2026-09-30")
        ]
        
        save_transactions(transactions, "data/test_save.csv")
        
        assert file_path.exists()
        
        # Verify content
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert rows[0] == ["amount", "category", "date"]
        assert rows[1] == ["50.0", "Food", "2026-09-29"]
        assert rows[2] == ["20.0", "Transport", "2026-09-30"]
        
        # Cleanup
        file_path.unlink()

    def test_save_transactions_overwrites_existing(self):
        """Test that save_transactions overwrites existing file."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_overwrite.csv", writable=True)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create initial file
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["old", "data"])
        
        # Save new transactions
        transactions = [
            Transaction(amount=100.0, category="Food", date="2026-09-29")
        ]
        
        save_transactions(transactions, "data/test_overwrite.csv")
        
        # Verify it was overwritten
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert len(rows) == 2  # header + 1 transaction
        assert rows[0] == ["amount", "category", "date"]
        
        # Cleanup
        file_path.unlink()


class TestLoadCategoryBudgets:
    """Test loading category budgets from CSV."""

    def test_load_category_budgets_empty_file(self):
        """Test loading from non-existent file returns empty dict."""
        budgets = load_category_budgets("data/nonexistent_budgets.csv")
        assert budgets == {}

    def test_load_category_budgets_single_budget(self):
        """Test loading a single budget."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_budgets.csv", writable=True)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["category", "limit"])
            writer.writerow(["Food", "100.0"])
        
        budgets = load_category_budgets("data/test_budgets.csv")
        
        assert budgets == {"Food": 100.0}
        
        # Cleanup
        file_path.unlink()

    def test_load_category_budgets_multiple_budgets(self):
        """Test loading multiple budgets."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_budgets.csv", writable=True)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["category", "limit"])
            writer.writerow(["Food", "100.0"])
            writer.writerow(["Transport", "50.0"])
            writer.writerow(["Entertainment", "75.0"])
        
        budgets = load_category_budgets("data/test_budgets.csv")
        
        assert len(budgets) == 3
        assert budgets["Food"] == 100.0
        assert budgets["Transport"] == 50.0
        assert budgets["Entertainment"] == 75.0
        
        # Cleanup
        file_path.unlink()

    def test_load_category_budgets_skips_malformed_rows(self):
        """Test that malformed budget rows are skipped."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_budgets.csv", writable=True)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["category", "limit"])
            writer.writerow(["Food", "100.0"])
            writer.writerow(["Transport", "invalid"])  # invalid limit
            writer.writerow(["Entertainment", "75.0"])
        
        budgets = load_category_budgets("data/test_budgets.csv")
        
        assert len(budgets) == 2
        assert "Food" in budgets
        assert "Entertainment" in budgets
        assert "Transport" not in budgets
        
        # Cleanup
        file_path.unlink()


class TestSaveCategoryBudgets:
    """Test saving category budgets to CSV."""

    def test_save_category_budgets_creates_file(self):
        """Test that save_category_budgets creates a new file."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_save_budgets.csv", writable=True)
        
        # Cleanup if it exists
        if file_path.exists():
            file_path.unlink()
        
        budgets = {
            "Food": 100.0,
            "Transport": 50.0
        }
        
        save_category_budgets(budgets, "data/test_save_budgets.csv")
        
        assert file_path.exists()
        
        # Verify content
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert rows[0] == ["category", "limit"]
        assert len(rows) == 3  # header + 2 budgets
        
        # Cleanup
        file_path.unlink()

    def test_save_category_budgets_overwrites_existing(self):
        """Test that save_category_budgets overwrites existing file."""
        from utils import resolve_data_path
        
        file_path = resolve_data_path("data/test_overwrite_budgets.csv", writable=True)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create initial file
        with open(file_path, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["old", "data"])
        
        # Save new budgets
        budgets = {"Food": 100.0}
        
        save_category_budgets(budgets, "data/test_overwrite_budgets.csv")
        
        # Verify it was overwritten
        with open(file_path, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)
        
        assert rows[0] == ["category", "limit"]
        
        # Cleanup
        file_path.unlink()