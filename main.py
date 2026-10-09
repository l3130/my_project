import csv
import shutil
from pathlib import Path

from models import Transaction
from repository import (
    load_transactions,
    save_transactions,
    load_category_budgets,
    save_category_budgets,
)
from services import calculate_total_spending, calculate_spending_by_category
from visualizations import (
    visualize_spending,
    visualize_trends,
    visualize_budgets_vs_spending,
)
from utils import resolve_data_path


def print_header():
    print("\n" + "=" * 70)
    print("FinanceTracker - Personal Budget Manager")
    print("=" * 70)


def print_menu():
    print("\nMain Menu")
    print("-" * 70)
    print("1.  Add transaction")
    print("2.  View transactions")
    print("3.  Show summary")
    print("4.  Backup transactions")
    print("5.  Visualize spending by category")
    print("6.  Visualize spending trends")
    print("7.  Export summary to file")
    print("8.  Check overall budget")
    print("9.  Check category budgets")
    print("10. Update category budgets")
    print("11. Visualize budgets vs spending")
    print("12. Reset transactions")
    print("13. Clear transactions")
    print("14. Archive transactions")
    print("15. Exit")
    print("-" * 70)


def print_success(message):
    print(f"✅ {message}")


def print_error(message):
    print(f"❌ {message}")


def get_valid_float(prompt):
    while True:
        value = input(prompt).strip()
        try:
            number = float(value)
            return number
        except ValueError:
            print_error("Please enter a valid number.")


def get_valid_date(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print_error("Date cannot be empty.")


def add_transaction():
    try:
        amount = get_valid_float("Enter transaction amount: ")
        if amount <= 0:
            raise ValueError("Amount must be greater than zero.")

        category = input("Enter category: ").strip()
        if not category:
            raise ValueError("Category cannot be empty.")

        date = get_valid_date("Enter date (YYYY-MM-DD or YYYYMMDD): ")

        transaction = Transaction(amount=amount, category=category, date=date)
        transactions = load_transactions()
        transactions.append(transaction)
        save_transactions(transactions)

        print_success(f"Transaction added: {transaction.category} - ${transaction.amount:.2f} - {transaction.date}")

    except ValueError as exc:
        print_error(str(exc))
    except Exception as exc:
        print_error(f"Could not add transaction: {exc}")


def view_transactions():
    transactions = load_transactions()

    if not transactions:
        print("No transactions found.")
        return

    print("\nTransactions:")
    for idx, transaction in enumerate(transactions, start=1):
        print(f"{idx}. {transaction.date} | {transaction.category:<20} | ${transaction.amount:.2f}")


def show_summary():
    transactions = load_transactions()

    if not transactions:
        print("No transactions found.")
        return

    total = calculate_total_spending(transactions)
    by_category = calculate_spending_by_category(transactions)

    print("\nSummary")
    print("-" * 50)
    print(f"Total transactions: {len(transactions)}")
    print(f"Total spending: ${total:.2f}")
    print("")
    print("Spending by category:")
    for category, amount in sorted(by_category.items()):
        print(f"  - {category}: ${amount:.2f}")


def backup_transactions():
    try:
        transactions_file = resolve_data_path("data/transactions.csv", writable=True)
        backup_file = resolve_data_path("data/transactions_backup.csv", writable=True)

        if not transactions_file.exists():
            print("No transactions file found.")
            return

        shutil.copy2(transactions_file, backup_file)
        print_success(f"Backup created: {backup_file}")

    except Exception as exc:
        print_error(f"Backup failed: {exc}")


def export_summary():
    try:
        transactions = load_transactions()

        if not transactions:
            print("No transactions found.")
            return

        total = calculate_total_spending(transactions)
        by_category = calculate_spending_by_category(transactions)

        export_path = resolve_data_path("data/summary.txt", writable=True)
        export_path.parent.mkdir(parents=True, exist_ok=True)

        lines = [
            "Finance Summary",
            "================",
            f"Total transactions: {len(transactions)}",
            f"Total spending: ${total:.2f}",
            "",
            "Spending by category:",
        ]

        for category, amount in sorted(by_category.items()):
            lines.append(f"{category}: ${amount:.2f}")

        with open(export_path, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        print_success(f"Summary exported to: {export_path}")

    except Exception as exc:
        print_error(f"Export failed: {exc}")


def check_budget():
    try:
        limit = get_valid_float("Enter overall budget limit: ")
        if limit <= 0:
            raise ValueError("Budget limit must be greater than zero.")

        transactions = load_transactions()
        total = calculate_total_spending(transactions)

        print("\nBudget Check")
        print("-" * 50)
        print(f"Budget limit: ${limit:.2f}")
        print(f"Current total: ${total:.2f}")

        if total > limit:
            print_error("You have exceeded your budget.")
        elif total >= 0.8 * limit:
            print("⚠️ You are close to your budget limit.")
        else:
            print_success("You are within your budget.")

    except ValueError as exc:
        print_error(str(exc))


def check_category_budgets():
    budgets = load_category_budgets()

    if not budgets:
        print("No category budgets found. Use option 10 to add budgets.")
        return

    transactions = load_transactions()
    spent_by_category = calculate_spending_by_category(transactions)

    print("\nCategory Budget Check")
    print("-" * 50)

    for category, limit in sorted(budgets.items()):
        spent = spent_by_category.get(category, 0.0)
        print(f"{category:<20} spent ${spent:.2f} / limit ${limit:.2f}")

        if spent > limit:
            print_error("  Budget exceeded")
        elif spent >= 0.8 * limit:
            print("  Warning: close to limit")
        else:
            print("  Within budget")


def update_category_budgets():
    budgets = load_category_budgets()

    print("\nUpdate Category Budgets")
    print("Type 'done' when finished.")
    print("-" * 50)

    while True:
        category = input("Category name: ").strip()

        if not category:
            print_error("Category cannot be empty.")
            continue

        if category.lower() == "done":
            break

        try:
            limit = get_valid_float(f"Budget limit for '{category}': ")
            if limit <= 0:
                raise ValueError("Budget limit must be greater than zero.")

            budgets[category] = limit
            print_success(f"Budget saved: {category} = ${limit:.2f}")

        except ValueError as exc:
            print_error(str(exc))

    save_category_budgets(budgets)
    print_success("Category budgets saved.")


def reset_transactions():
    transactions_file = resolve_data_path("data/transactions.csv", writable=True)

    if not transactions_file.exists():
        print("No transactions file found.")
        return

    try:
        transactions_file.unlink()
        print_success("Transactions reset.")
    except Exception as exc:
        print_error(f"Reset failed: {exc}")


def clear_transactions():
    confirm = input("Are you sure you want to clear all transactions? (yes/no): ").strip().lower()
    if confirm != "yes":
        print("Clear cancelled.")
        return

    try:
        transactions_file = resolve_data_path("data/transactions.csv", writable=True)
        transactions_file.parent.mkdir(parents=True, exist_ok=True)

        with open(transactions_file, "w", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["amount", "category", "date"])

        print_success("Transactions cleared.")

    except Exception as exc:
        print_error(f"Clear failed: {exc}")


def archive_transactions():
    try:
        transactions_file = resolve_data_path("data/transactions.csv", writable=True)
        archive_file = resolve_data_path("data/transactions_archive.csv", writable=True)

        if not transactions_file.exists():
            print("No transactions file found.")
            return

        shutil.move(str(transactions_file), str(archive_file))
        print_success(f"Transactions archived to: {archive_file}")

    except Exception as exc:
        print_error(f"Archive failed: {exc}")


def handle_menu_choice(choice):
    options = {
        "1": add_transaction,
        "2": view_transactions,
        "3": show_summary,
        "4": backup_transactions,
        "5": lambda: visualize_spending(load_transactions()),
        "6": lambda: visualize_trends(load_transactions()),
        "7": export_summary,
        "8": check_budget,
        "9": check_category_budgets,
        "10": update_category_budgets,
        "11": lambda: visualize_budgets_vs_spending(load_transactions(), load_category_budgets()),
        "12": reset_transactions,
        "13": clear_transactions,
        "14": archive_transactions,
    }

    handler = options.get(choice)

    if handler is None:
        print_error("Invalid option. Please choose a number from 1 to 15.")
        return

    handler()


def main():
    print_header()

    while True:
        print_menu()
        choice = input("\nSelect an option (1-15): ").strip()

        if choice == "15":
            print("Goodbye!")
            break

        handle_menu_choice(choice)
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()