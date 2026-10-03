# fix_dates.py (run once, then delete)
from repository import load_transactions, save_transactions
from utils import normalize_date

transactions = load_transactions()

for t in transactions:
    try:
        # Try to normalize the date
        t.date = normalize_date(t.date)
        print(f"✅ Fixed: {t.date}")
    except ValueError as e:
        print(f"❌ Could not fix: {t.date} — {e}")

save_transactions(transactions)
print("\n✅ All dates normalized!")