import csv
import base64
import os
import sys
from pathlib import Path

# Use Tk so visualizations open in a separate interactive window.
import matplotlib
matplotlib.use('TkAgg')

APP_NAME = "FinanceTracker"
PLOT_MODE = "save" if "--save-plots" in sys.argv else "show"

TK_ICON_PNG = (
    "iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAJUlEQVR4nGOUL9/"
    "yn4ECwESJ5lEDIICJgULANGoAw2gYMFAeBgCHAgJprYo/ugAAAABJRU5ErkJggg=="
)


def ensure_matplotlib_tk_icons():
    """Provide Tk window icons missing from recent matplotlib distributions."""
    image_dir = Path(matplotlib.get_data_path()) / "images"
    filenames = (
        "matplotlib.png",
        "matplotlib_large.png",
        "home.png",
        "back.png",
        "forward.png",
        "move.png",
        "zoom_to_rect.png",
        "subplots.png",
        "filesave.png",
    )
    for filename in filenames:
        icon_path = image_dir / filename
        if icon_path.exists():
            continue
        try:
            image_dir.mkdir(parents=True, exist_ok=True)
            icon_path.write_bytes(base64.b64decode(TK_ICON_PNG))
        except OSError:
            pass

# ---------- Data path helpers ----------

def get_project_root():
    cwd = Path(os.getcwd())
    if (cwd / "data").exists() or (cwd / "main.py").exists():
        return cwd

    module_file = getattr(sys.modules[__name__], "__file__", None)
    if module_file:
        module_path = Path(module_file).resolve()
        for base in [module_path.parent, module_path.parent.parent]:
            if (base / "data").exists() or (base / "main.py").exists():
                return base

    executable = getattr(sys, "executable", None)
    if executable:
        exe_dir = Path(executable).resolve().parent
        if (exe_dir / "data").exists() or (exe_dir / "main.py").exists():
            return exe_dir

    return cwd


def get_writable_data_dir():
    """Return the project data root for CSV and plot files."""
    return get_project_root()


def resolve_data_path(relative_path, writable=False):
    """Resolve a data file path for source runs and packaged executables."""
    relative_path = Path(relative_path)
    project_root = get_project_root()

    if writable:
        return project_root / relative_path

    if getattr(sys, "frozen", False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidate = Path(meipass) / relative_path
            if candidate.exists():
                return candidate

    candidate = project_root / relative_path
    if candidate.exists():
        return candidate

    cwd_candidate = Path.cwd() / relative_path
    if cwd_candidate.exists():
        return cwd_candidate

    return candidate


def show_or_save_plot(plt, filename):
    """Display a plot in a popup window, saving a PNG only when GUI display is unavailable."""
    out_path = resolve_data_path(f"data/{filename}", writable=True)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if PLOT_MODE != "save":
        try:
            ensure_matplotlib_tk_icons()
            print("✅ Chart window opened. Close it to return to the menu.")
            plt.show()
            return
        except Exception as error:
            print(f"Could not open chart window: {error}")

    try:
        plt.savefig(out_path, dpi=100, bbox_inches='tight')
        print(f"✅ Plot saved to: {out_path}")
    except Exception as e:
        print(f"❌ Failed to save plot: {e}")


def get_budget_limit():
    while True:
        try:
            limit = float(input("Enter your budget limit: ").strip())
            if limit > 0:
                return limit
            print("Budget limit must be a positive number.")
        except ValueError:
            print("Please enter a valid numeric budget limit.")


def load_category_budgets(filename="data/category_budgets.csv"):
    path = resolve_data_path(filename, writable=True)
    if not path.exists():
        return {}

    budgets = {}
    try:
        with open(path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                if not row or row[0].strip().lower().startswith("category"):
                    continue
                try:
                    category = row[0].strip()
                    limit = float(row[1])
                    budgets[category] = limit
                except (IndexError, ValueError):
                    continue
    except FileNotFoundError:
        return {}

    return budgets


def save_category_budgets(budgets, filename="data/category_budgets.csv"):
    path = resolve_data_path(filename, writable=True)
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(["category", "limit"])
        for category, limit in budgets.items():
            writer.writerow([category, limit])


# ---------- Helpers for interactive input ----------

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

    if not choice:
        print("⚠️ No input detected, please try again.")
        return None
    return choice


# ---------- Core functions ----------

def add_transaction():
    try:
        amount = float(input("Enter transaction amount: ").strip())
        category = input("Enter category: ").strip()
        date = input("Enter date (YYYY-MM-DD): ").strip()

        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
        transactions_path.parent.mkdir(parents=True, exist_ok=True)

        with open(transactions_path, mode="a", encoding="utf-8", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([amount, category, date])

        print("✅ Transaction added successfully!")
        print(f"Transaction saved to: {transactions_path}")

    except ValueError:
        print("Please enter a valid numeric amount.")


def view_transactions():
    try:
        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
        with open(transactions_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            print("\n--- Transactions ---")
            for idx, row in enumerate(transactions, start=1):
                amount, category, date = row
                print(f"{idx}. {date} | {category} | {amount}")

    except FileNotFoundError:
        print("No transactions file found yet.")


def show_summary():
    try:
        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
        with open(transactions_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            transactions = list(reader)

            if not transactions:
                print("No transactions found yet.")
                return

            total = sum(float(row[0]) for row in transactions)
            print("\n--- Summary ---")
            print(f"Total transactions: {len(transactions)}")
            print(f"Total spending: {total}")

    except FileNotFoundError:
        print("No transactions file found yet.")


def backup_transactions():
    try:
        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
        backup_path = resolve_data_path("data/transactions_backup.csv", writable=True)

        if not transactions_path.exists():
            print("No transactions file found yet.")
            return

        import shutil
        shutil.copy(transactions_path, backup_path)
        print(f"✅ Backup created at {backup_path}")

    except Exception as e:
        print(f"Backup failed: {e}")


def export_summary():
    try:
        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
        export_path = resolve_data_path("data/summary.txt", writable=True)
        print(f"Checking transaction file for export: {transactions_path}")
        print(f"File exists: {transactions_path.exists()}")

        with open(transactions_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            transactions = list(reader)

        if not transactions:
            print("No transactions found yet.")
            return

        total = sum(float(row[0]) for row in transactions)

        with open(export_path, mode="w", encoding="utf-8") as f:
            f.write(f"Total transactions: {len(transactions)}\n")
            f.write(f"Total spending: {total}\n")

        print(f"✅ Summary exported to {export_path}")

    except FileNotFoundError:
        print("No transactions file found yet.")



def reset_transactions():
    transactions_path = resolve_data_path("data/transactions.csv", writable=True)
    if transactions_path.exists():
        transactions_path.unlink()  # delete the file
        print("✅ All transactions have been reset (file deleted).")
    else:
        print("No transactions file found to reset.")





def clear_transactions():
    transactions_path = resolve_data_path("data/transactions.csv", writable=True)
    transactions_path.parent.mkdir(parents=True, exist_ok=True)
    with open(transactions_path, mode="w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file)
        # optional: write header row
        writer.writerow(["amount", "category", "date"])
    print("✅ Transactions cleared (file emptied).")






def archive_transactions():
    try:
        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
        archive_path = resolve_data_path("data/transactions_archive.csv", writable=True)

        if not transactions_path.exists():
            print("No transactions file found to archive.")
            return

        import shutil
        shutil.move(transactions_path, archive_path)
        print(f"✅ Transactions archived to {archive_path}")

    except Exception as e:
        print(f"Archiving failed: {e}")



def visualize_spending():
    transactions_path = resolve_data_path("data/transactions.csv", writable=True)

    try:
        with open(transactions_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            transactions = list(reader)
    except FileNotFoundError:
        print("No transactions file found yet.")
        return
    except Exception as e:
        print(f"Failed to read transactions: {e}")
        return

    if not transactions:
        print("No transactions found yet.")
        return

    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt
        
        category_totals = {}
        for row in transactions:
            try:
                amount = float(row[0])
                category = row[1]
                category_totals[category] = category_totals.get(category, 0) + amount
            except (IndexError, ValueError):
                continue

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
        print(f"Visualization failed: {e}")


def visualize_trends():
    transactions_path = resolve_data_path("data/transactions.csv", writable=True)

    try:
        with open(transactions_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            transactions = list(reader)
    except FileNotFoundError:
        print("No transactions file found yet.")
        return
    except Exception as e:
        print(f"Failed to read transactions: {e}")
        return

    if not transactions:
        print("No transactions found yet.")
        return

    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt
        
        date_totals = {}
        for row in transactions:
            try:
                amount = float(row[0])
                date = row[2]
                date_totals[date] = date_totals.get(date, 0) + amount
            except (IndexError, ValueError):
                continue

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
        print(f"Visualization failed: {e}")

def check_budget(limit):
    try:
        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
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
        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
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

def update_category_budgets(filename="data/category_budgets.csv"):
    budgets = load_category_budgets(filename)
    print("\n--- Update Category Budgets ---")
    print(f"Current budgets: {budgets if budgets else 'None'}")
    
    while True:
        category = input("Enter category name (or 'done' to finish): ").strip()
        if category.lower() == 'done':
            break
        
        try:
            limit = float(input(f"Enter budget limit for {category}: ").strip())
            if limit > 0:
                budgets[category] = limit
                print(f"✅ Budget for {category} set to {limit}")
            else:
                print("Budget must be positive.")
        except ValueError:
            print("Please enter a valid number.")
    
    if budgets:
        save_category_budgets(budgets, filename)
        print(f"✅ Budgets saved.")
    else:
        print("No budgets to save.")

def visualize_budgets_vs_spending():
    budgets = load_category_budgets()
    if not budgets:
        print("No saved category budgets found yet.")
        return

    try:
        try:
            ensure_matplotlib_tk_icons()
            import matplotlib.pyplot as plt
        except Exception:
            print("Visualization requires matplotlib with a GUI backend. Install/configure matplotlib to enable plots.")
            return
        transactions_path = resolve_data_path("data/transactions.csv", writable=True)
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
            show_or_save_plot(plt, "budgets_vs_spending.png")

    except FileNotFoundError:
        print("No transactions file found yet.")

# ---------- Main loop ----------

def main():
    print("="*60)
    print("Welcome to FinanceTracker!")
    print("="*60)
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
            print("Invalid choice in config.txt. Please update it.")
            break

if __name__ == "__main__":
    main()
