import csv
from datetime import datetime
from tabulate import tabulate

def add_transaction():
    try:
        amount = float(input("Enter amount: "))
        if amount <= 0:
            print("Amount must be positive.")
            return

        category = input("Enter category: ").strip()
        if not category:
            print("Category cannot be empty.")
            return

        date_str = input("Enter date (YYYY-MM-DD): ").strip()
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format. Use YYYY-MM-DD.")
            return

        # Save to CSV
        with open("data/transactions.csv", mode="a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([amount, category, date_str])

        print("Transaction added successfully!")

    except ValueError:
        print("Invalid amount. Please enter a number.")

def view_transactions():
    try:
        with open("data/transactions.csv", mode="r") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            headers = ["Amount", "Category", "Date"]
            print("\n--- Transactions ---")
            print(tabulate(transactions, headers=headers, tablefmt="grid"))

    except FileNotFoundError:
        print("No transactions file found yet.")

def show_summary():
    try:
        with open("data/transactions.csv", mode="r") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            total = 0
            category_totals = {}

            for row in transactions:
                amount = float(row[0])
                category = row[1]
                total += amount
                category_totals[category] = category_totals.get(category, 0) + amount

            # Display summary
            print("\n--- Summary ---")
            print(f"Total Spending: {total}")

            # Category breakdown in table
            headers = ["Category", "Total Spent"]
            table = [(cat, amt) for cat, amt in category_totals.items()]
            print(tabulate(table, headers=headers, tablefmt="grid"))

            # Top 3 categories
            top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:3]
            print("\nTop 3 Expense Categories:")
            for category, amt in top_categories:
                print(f"{category}: {amt}")

    except FileNotFoundError:
        print("No transactions file found yet.")


def main():
    while True:
        print("\nWelcome to Personal Finance Tracker!")
        print("1. Add Transaction")
        print("2. View Transactions")
        print("3. Show Summary")
        print("4. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_transaction()
        elif choice == "2":
            view_transactions()
        elif choice == "3":
            show_summary()
        elif choice == "4":
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
