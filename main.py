# main.py
import csv
import shutil
from pathlib import Path
from datetime import datetime
from models import Transaction, Budget
from repository import (
    load_transactions,
    save_transactions,
    load_category_budgets,
    save_category_budgets,
)
from utils import resolve_data_path, show_or_save_plot, ensure_matplotlib_tk_icons, normalize_date


def get_choice():
    choice = input(
        "\nPlease select an option:\n"
        "1. Add transaction\n"
        "2. View transactions\n"
        "3. Show summary\n"
        "4. Exit\n"
        "5. Backup transactions\n"
        "6. Visualize spending\n"
        "7. Visualize trends\n"
        "8. Export summary\n"
        "9. Check budget limit\n"
        "10. Check category budgets\n"
        "11. Update category budgets\n"
        "12. Visualize budgets vs spending\n"
        "13. Reset transactions\n"
        "14. Clear transactions\n"
        "15. Archive transactions\n"
        "Enter option number: "
    ).strip()

    return choice if choice else None


def add_transaction():
    try:
        amount = float(input("Enter transaction amount: ").strip())
        category = input("Enter category: ").strip()
        date = input("Enter date (YYYY-MM-DD, YYYYMMDD, or other formats): ").strip()

        # Transaction validates and normalizes date
        transaction = Transaction(amount=amount, category=category, date=date)

        transactions = load_transactions()
        transactions.append(transaction)
        save_transactions(transactions)

        print("✅ Transaction added successfully!")

    except ValueError as e:
        print(f"❌ Error: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


def view_transactions():
    transactions = load_transactions()
    if not transactions:
        print("No transactions found yet.")
        return

    print("\n--- Transactions ---")
    for idx, t in enumerate(transactions, start=1):
        print(f"{idx}. {t.date} | {t.category} | {t.amount}")


def show_summary():
    transactions = load_transactions()
    if not transactions:
        print("No transactions found yet.")
        return

    total = sum(t.amount for t in transactions)
    print("\n--- Summary ---")
    print(f"Total transactions: {len(transactions)}")
    print(f"Total spending: {total}")


def backup_transactions():
    try:
        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
        backup_path = resolve_data_path("data/transactions_backup.csv", writable=True)

        if not transactions_path.exists():
            print("No transactions file found yet.")
            return

        shutil.copy(transactions_path, backup_path)
        print(f"✅ Backup created at {backup_path}")
    except Exception as e:
        print(f"❌ Backup failed: {e}")


def export_summary():
    try:
        transactions = load_transactions()
        if not transactions:
            print("No transactions found yet.")
            return

        total = sum(t.amount for t in transactions)
        export_path = resolve_data_path("data/summary.txt", writable=True)

        with open(export_path, mode="w", encoding="utf-8") as f:
            f.write(f"Total transactions: {len(transactions)}\n")
            f.write(f"Total spending: {total}\n")

        print(f"✅ Summary exported to {export_path}")
    except Exception as e:
        print(f"❌ Failed to export summary: {e}")


def reset_transactions():
    transactions_path = resolve_data_path("data/transactions.csv", writable=True)
    if transactions_path.exists():
        transactions_path.unlink()
        print("✅ All transactions have been reset (file deleted).")
    else:
        print("No transactions file found to reset.")


def clear_transactions():
    confirm = input("⚠️ Are you sure you want to clear all transactions? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("❌ Clear cancelled.")
        return

    transactions_path = resolve_data_path("data/transactions.csv", writable=True)
    transactions_path.parent.mkdir(parents=True, exist_ok=True)
    with open(transactions_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["amount", "category", "date"])

    print("✅ Transactions cleared (file emptied).")


def archive_transactions():
    try:
        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
        archive_path = resolve_data_path("data/transactions_archive.csv", writable=True)

        if not transactions_path.exists():
            print("No transactions file found to archive.")
            return

        shutil.move(transactions_path, archive_path)
        print(f"✅ Transactions archived to {archive_path}")
    except Exception as e:
        print(f"❌ Archiving failed: {e}")


def visualize_spending():
    transactions = load_transactions()

    if not transactions:
        print("No transactions found yet.")
        return

    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt

        category_totals = {}
        for t in transactions:
            category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

        if not category_totals:
            print("No valid transactions to visualize.")
            return

        labels = list(category_totals.keys())
        sizes = list(category_totals.values())

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
        plt.title("Spending by Category")
        show_or_save_plot(plt, "spending_pie.png")
        plt.close()

    except Exception as e:
        print(f"❌ Visualization failed: {e}")


def visualize_trends():
    transactions = load_transactions()

    if not transactions:
        print("No transactions found yet.")
        return

    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt

        date_totals = {}
        for t in transactions:
            date_totals[t.date] = date_totals.get(t.date, 0) + t.amount

        if not date_totals:
            print("No valid transactions to visualize.")
            return

        sorted_dates = sorted(date_totals.keys())
        amounts = [date_totals[d] for d in sorted_dates]

        plt.figure(figsize=(10, 6))
        plt.plot(sorted_dates, amounts, marker="o", linestyle="-", color="blue", linewidth=2)
        plt.xticks(rotation=45, ha='right')
        plt.xlabel("Date")
        plt.ylabel("Total Spending")
        plt.title("Spending Over Time")
        plt.tight_layout()
        show_or_save_plot(plt, "trends.png")
        plt.close()

    except Exception as e:
        print(f"❌ Visualization failed: {e}")


def visualize_budgets_vs_spending():
    budgets = load_category_budgets()
    if not budgets:
        print("No saved category budgets found yet.")
        return

    transactions = load_transactions()
    if not transactions:
        print("No transactions found yet.")
        return

    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt

        category_totals = {}
        for t in transactions:
            category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

        categories = list(budgets.keys())
        limits = [budgets[cat] for cat in categories]
        spent = [category_totals.get(cat, 0) for cat in categories]

        colors = []
        print("\n--- Budget Status ---")
        for cat, limit, actual in zip(categories, limits, spent):
            if actual >= limit:
                colors.append("red")
                print(f"⚠️ {cat}: spent {actual}, limit {limit} → OVERSPENT")
            elif actual >= 0.8 * limit:
                colors.append("yellow")
                print(f"⚠️ {cat}: spent {actual}, limit {limit} → CLOSE TO LIMIT")
            else:
                colors.append("green")
                print(f"✅ {cat}: spent {actual}, limit {limit} → SAFE")

        x = range(len(categories))
        plt.figure(figsize=(8, 5))
        plt.bar(x, limits, width=0.4, label="Budget Limit", color="lightblue", align="center")
        plt.bar([i + 0.4 for i in x], spent, width=0.4, label="Actual Spending", color=colors, align="center")

        plt.xticks([i + 0.2 for i in x], categories, rotation=45)
        plt.ylabel("Amount")
        plt.title("Budgets vs. Spending by Category")
        plt.legend()
        plt.tight_layout()
        show_or_save_plot(plt, "budgets_vs_spending.png")
        plt.close()

    except Exception as e:
        print(f"❌ Visualization failed: {e}")


def get_budget_limit():
    while True:
        try:
            limit = float(input("Enter your budget limit: ").strip())
            if limit > 0:
                return limit
            print("Budget limit must be a positive number.")
        except ValueError:
            print("Please enter a valid numeric budget limit.")


def check_budget(limit):
    transactions = load_transactions()
    if not transactions:
        print("No transactions found yet.")
        return

    total = sum(t.amount for t in transactions)

    print(f"\n--- Budget Check ---")
    print(f"Budget Limit: {limit}")
    print(f"Total Spending: {total}")

    if total >= limit:
        print("⚠️ You have exceeded your budget!")
    elif total >= 0.8 * limit:
        print("⚠️ Warning: You are close to your budget limit.")
    else:
        print("✅ You are within your budget.")


def check_category_budgets(budgets):
    transactions = load_transactions()
    if not transactions:
        print("No transactions found yet.")
        return

    category_totals = {}
    for t in transactions:
        category_totals[t.category] = category_totals.get(t.category, 0) + t.amount

    print("\n--- Category Budget Check ---")
    for category, limit in budgets.items():
        spent = category_totals.get(category, 0)
        print(f"{category}: spent {spent}, limit {limit}")

        if spent >= limit:
            print(f"⚠️ {category} budget exceeded!")
        elif spent >= 0.8 * limit:
            print(f"⚠️ {category} budget close to limit.")
        else:
            print(f"✅ {category} budget is fine.")


def update_category_budgets():
    budgets = load_category_budgets()
    print("\n--- Update Category Budgets ---")
    print(f"Current budgets: {budgets if budgets else 'None'}")

    while True:
        category = input("Enter category name (or 'done' to finish): ").strip()
        if category.lower() == "done":
            break

        if not category:
            print("❌ Category cannot be empty.")
            continue

        try:
            limit = float(input(f"Enter budget limit for {category}: ").strip())

            # Budget validation happens in dataclass
            budget = Budget(category=category, limit=limit)
            budgets[category] = budget.limit

            print(f"✅ Budget for {category} set to {budget.limit}")

        except ValueError as e:
            print(f"❌ Error: {e}")

    if budgets:
        save_category_budgets(budgets)
        print("✅ Budgets saved.")
    else:
        print("No budgets to save.")


def main():
    print("=" * 60)
    print("Welcome to FinanceTracker!")
    print("=" * 60)

    while True:
        choice = get_choice()

        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_transactions()
        elif choice == "3":
            show_summary()
        elif choice == "4":
            print("Goodbye!")
            break
        elif choice == "5":
            backup_transactions()
        elif choice == "6":
            visualize_spending()
        elif choice == "7":
            visualize_trends()
        elif choice == "8":
            export_summary()
        elif choice == "9":
            limit = get_budget_limit()
            if limit > 0:
                check_budget(limit)
        elif choice == "10":
            budgets = load_category_budgets()
            if not budgets:
                print("No budgets saved. Please use option 11 to set budgets.")
            else:
                check_category_budgets(budgets)
        elif choice == "11":
            update_category_budgets()
        elif choice == "12":
            visualize_budgets_vs_spending()
        elif choice == "13":
            reset_transactions()
        elif choice == "14":
            clear_transactions()
        elif choice == "15":
            archive_transactions()
        else:
            if choice:
                print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()