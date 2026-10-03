# tests/test_models.py
import pytest

from models import Transaction, Budget


class TestTransaction:
    """Test Transaction validation."""

    def test_valid_transaction(self):
        """Test creating a valid transaction."""
        t = Transaction(amount=50.0, category="Food", date="2026-09-29")
        assert t.amount == 50.0
        assert t.category == "Food"
        assert t.date == "2026-09-29"

    def test_negative_amount_raises_error(self):
        """Test that negative amounts are rejected."""
        with pytest.raises(ValueError, match="Amount must be positive"):
            Transaction(amount=-50.0, category="Food", date="2026-09-29")

    def test_zero_amount_raises_error(self):
        """Test that zero amounts are rejected."""
        with pytest.raises(ValueError, match="Amount must be positive"):
            Transaction(amount=0.0, category="Food", date="2026-09-29")

    def test_empty_category_raises_error(self):
        """Test that empty categories are rejected."""
        with pytest.raises(ValueError, match="Category cannot be empty"):
            Transaction(amount=50.0, category="", date="2026-09-29")

    def test_whitespace_category_raises_error(self):
        """Test that whitespace-only categories are rejected."""
        with pytest.raises(ValueError, match="Category cannot be empty"):
            Transaction(amount=50.0, category="   ", date="2026-09-29")

    def test_invalid_date_format_raises_error(self):
        """Test that invalid date formats are rejected."""
        with pytest.raises(ValueError, match="Invalid date"):
            Transaction(amount=50.0, category="Food", date="invalid")

    def test_date_normalization_yyyymmdd(self):
        """Test that YYYYMMDD format is normalized to YYYY-MM-DD."""
        t = Transaction(amount=50.0, category="Food", date="20260929")
        assert t.date == "2026-09-29"

    def test_date_normalization_slash_format(self):
        """Test that YYYY/MM/DD format is normalized."""
        t = Transaction(amount=50.0, category="Food", date="2026/09/29")
        assert t.date == "2026-09-29"

    def test_category_whitespace_stripped(self):
        """Test that category whitespace is stripped."""
        t = Transaction(amount=50.0, category="  Food  ", date="2026-09-29")
        assert t.category == "Food"


class TestBudget:
    """Test Budget validation."""

    def test_valid_budget(self):
        """Test creating a valid budget."""
        b = Budget(category="Food", limit=100.0)
        assert b.category == "Food"
        assert b.limit == 100.0

    def test_negative_limit_raises_error(self):
        """Test that negative limits are rejected."""
        with pytest.raises(ValueError, match="Budget limit must be positive"):
            Budget(category="Food", limit=-100.0)

    def test_zero_limit_raises_error(self):
        """Test that zero limits are rejected."""
        with pytest.raises(ValueError, match="Budget limit must be positive"):
            Budget(category="Food", limit=0.0)

    def test_empty_category_raises_error(self):
        """Test that empty categories are rejected."""
        with pytest.raises(ValueError, match="Category cannot be empty"):
            Budget(category="", limit=100.0)

    def test_category_whitespace_stripped(self):
        """Test that category whitespace is stripped."""
        b = Budget(category="  Food  ", limit=100.0)
        assert b.category == "Food"