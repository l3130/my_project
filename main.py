import csv
import matplotlib.pyplot as plt

# ---------- Helpers for file-based input ----------

def get_choice():
    try:
        with open("config.txt") as f:
            for line in f:
                if line.startswith("choice="):
                    return line.split("=")[1].strip()
    except FileNotFoundError:
        return "4"  # default: exit
    return "4"

def get_budget_limit():
    try:
        with open("budget.txt") as f:
            for line in f:
                if line.startswith("limit="):
                    return float(line.split("=")[1].strip())
    except:
        return 0
    return 0

def load_category_budgets(filename="data/category_budget.csv"):
    budgets = {}
    try:
        with open(filename, newline="") as f:
            reader = csv.DictReader(f)
            for row in reader:
                budgets[row["category"]] = float(row["limit"])
    except FileNotFoundError:
        pass
    return budgets

def save_category_budgets(budgets, filename="data/category_budget.csv"):
    with open(filename, mode="w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["category", "limit"])
        for cat, limit in budgets.items():
            writer.writerow([cat, limit])

def resolve_data_path(filename):
    return filename

# ---------- Core functions ----------

def add_transaction():
    print("Add transaction logic here (reads/writes to transactions.csv).")

def view_transactions():
    print("View transactions logic here.")

def show_summary():
    print("Show summary logic here.")

def backup_transactions():
    print("Backup transactions logic here.")

def export_summary():
    print("Export summary logic here.")

def visualize_spending():
    try:
        transactions_path = resolve_data_path("data/transactions.csv")
        with open(transactions_path, mode="r") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            category_totals = {}
            for row in transactions:
                amount = float(row[0])
                category = row[1]
                category_totals[category] = category_totals.get(category, 0) + amount

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
        transactions_path = resolve_data_path("data/transactions.csv")
        with open(transactions_path, mode="r") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            date_totals = {}
            for row in transactions:
                amount = float(row[0])
                date = row[2]
                date_totals[date] = date_totals.get(date, 0) + amount

            sorted_dates = sorted(date_totals.keys())
            amounts = [date_totals[d] for d in sorted_dates]

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
        transactions_path = resolve_data_path("data/transactions.csv")
        with open(transactions_path, mode="r") as file:
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
        transactions_path = resolve_data_path("data/transactions.csv")
        with open(transactions_path, mode="r") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

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

def update_category_budgets(filename="data/category_budget.csv"):
    budgets = load_category_budgets(filename)
    if not budgets:
        print("No budgets saved yet. Please edit category_budget.csv manually.")
    save_category_budgets(budgets, filename)

def visualize_budgets_vs_spending():
    budgets = load_category_budgets()
    if not budgets:
        print("No saved category budgets found yet.")
        return

    try:
        transactions_path = resolve_data_path("data/transactions.csv")
        with open(transactions_path, mode="r") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            category_totals = {}
            for row in transactions:
                amount = float(row[0])
                category = row[1]
                category_totals[category] = category_totals.get(category, 0) + amount

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
            plt.figure(figsize=(8,5))
            plt.bar(x, limits, width=0.4, label="Budget Limit", color="lightblue", align="center")
            plt.bar([i+0.4 for i in x], spent, width=0.4, label="Actual Spending", color=colors, align="center")

            plt.xticks([i+0.2 for i in x], categories, rotation=45)
            plt.ylabel("Amount")
            plt.title("Budgets vs. Spending by Category")
            plt.legend()
            plt.tight_layout()
            plt.show()

    except FileNotFoundError:
        print("No transactions file found yet.")

# ---------- Main loop ----------

def main():
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
            if limit <= 0:
                print("Budget limit must be positive.")
                continue
            check_budget(limit)
        elif choice == "10":
            budgets = load_category_budgets()
            if not budgets:
                print("No budgets saved. Please edit category_budget.csv.")
            check_category_budgets(budgets)
        elif choice == "11":
            update_category_budgets()
        elif choice == "12":
            visualize_budgets_vs_spending()
        else:
            print("Invalid choice in config.txt. Please update it.")
            break

if __name__ == "__main__":
    main()
