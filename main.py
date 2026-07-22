import csv
import shutil
import os
import matplotlib.pyplot as plt
from datetime import datetime
from tabulate import tabulate


def backup_transactions():
    if os.path.exists('data/transactions.csv'):
        shutil.copy('data/transactions.csv', 'data/transactions_backup.csv')
        print("Backup created successfully!")
    else:
        print("No transactions file found to back up.")


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


def export_summary():
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

            summary_lines = [
                "Finance Summary",
                f"Total Spending: {total}",
                "Category Breakdown:",
            ]
            for category, amount in category_totals.items():
                summary_lines.append(f"{category}: {amount}")

            os.makedirs("data", exist_ok=True)
            with open("data/summary_export.txt", mode="w") as output_file:
                output_file.write("\n".join(summary_lines))

            print("Summary exported to data/summary_export.txt")

    except FileNotFoundError:
        print("No transactions file found yet.")


def main():
    while True:
        print("\nWelcome to Personal Finance Tracker!")
        print("1. Add Transaction")
        print("2. View Transactions")
        print("3. Show Summary")
        print("4. Exit")
        print("5. Backup Transactions")
        print("6. Visualize Spending")
        print("7. Visualize Trends") 
        print("8. Export Summary")
        print("9. Check Budget")
        print("10. Check Category Budgets")  # <-- Added



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
        elif choice == "5":
            backup_transactions()
        elif choice == "6":  # <-- Added this branch
            visualize_spending()
        elif choice == "7":  # <-- Added this branch
            visualize_trends()
        elif choice == "8": 
            export_summary()
        elif choice == "9":
        
            try:
                limit = float(input("Enter your budget limit: "))
                if limit <= 0:
                    print("Budget limit must be positive.")
                    continue
                check_budget(limit)
            except ValueError:
                print("Invalid input. Please enter a number.")


        elif choice == "10":
            budgets = {}
            while True:
                cat = input("Enter category name (or press Enter to stop): ").strip()
                if not cat:
                    break
                try:
                    limit = float(input(f"Enter budget limit for {cat}: "))
                    if limit <= 0:
                        print("Limit must be positive.")
                        continue
                    budgets[cat] = limit
                except ValueError:
                    print("Invalid input. Please enter a number.")
            if budgets:
                check_category_budgets(budgets)
        else:
            print("Invalid choice. Please try again.")

        
def visualize_spending():
    try:
        with open("data/transactions.csv", mode="r") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            # Aggregate totals by category
            category_totals = {}
            for row in transactions:
                amount = float(row[0])
                category = row[1]
                category_totals[category] = category_totals.get(category, 0) + amount

            # Create pie chart
            labels = category_totals.keys()
            sizes = category_totals.values()

            plt.figure(figsize=(6,6))
            plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
            plt.title("Spending by Category")
            plt.show()

    except FileNotFoundError:
        print("No transactions file found yet.")


def visualize_trends():
    try:
        with open("data/transactions.csv", mode="r") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            # Aggregate totals by date
            date_totals = {}
            for row in transactions:
                amount = float(row[0])
                date = row[2]
                date_totals[date] = date_totals.get(date, 0) + amount

            # Sort by date
            sorted_dates = sorted(date_totals.keys())
            amounts = [date_totals[d] for d in sorted_dates]

            # Plot line chart
            plt.figure(figsize=(8,5))
            plt.plot(sorted_dates, amounts, marker="o", linestyle="-", color="blue")
            plt.xticks(rotation=45)
            plt.xlabel("Date")
            plt.ylabel("Total Spending")
            plt.title("Spending Over Time")
            plt.tight_layout()
            plt.show()

    except FileNotFoundError:
        print("No transactions file found yet.")


def check_budget(limit):
    try:
        with open("data/transactions.csv", mode="r") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            total = sum(float(row[0]) for row in transactions)

            print(f"\n--- Budget Check ---")
            print(f"Budget Limit: {limit}")
            print(f"Total Spending: {total}")

            if total >= limit:
                print("⚠️ You have exceeded your budget!")
            elif total >= 0.8 * limit:
                print("⚠️ Warning: You are close to your budget limit.")
            else:
                print("✅ You are within your budget.")

    except FileNotFoundError:
        print("No transactions file found yet.")


def check_category_budgets(budgets):
    try:
        with open("data/transactions.csv", mode="r") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            # Aggregate totals by category
            category_totals = {}
            for row in transactions:
                amount = float(row[0])
                category = row[1]
                category_totals[category] = category_totals.get(category, 0) + amount

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

    except FileNotFoundError:
        print("No transactions file found yet.")



if __name__ == "__main__":
    main()
