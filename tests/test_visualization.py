# visualizations.py
from typing import List, Dict

from models import Transaction
from utils import ensure_matplotlib_tk_icons, show_or_save_plot


def visualize_spending(transactions: List[Transaction]):
    """Show a pie chart by category."""
    if not transactions:
        print("No transactions found yet.")
        return

    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt

        category_totals = {}
        for t in transactions:
            category_totals[t.category] = category_totals.get(t.category, 0.0) + t.amount

        labels = list(category_totals.keys())
        sizes = list(category_totals.values())

        plt.figure(figsize=(8, 6))
        plt.pie(sizes, labels=labels, autopct="%1.1f%%", startangle=140)
        plt.title("Spending by Category")
        show_or_save_plot(plt, "spending_pie.png")
        plt.close()

    except Exception as e:
        print(f"❌ Visualization failed: {e}")


def visualize_trends(transactions: List[Transaction]):
    """Show spending over time."""
    if not transactions:
        print("No transactions found yet.")
        return

    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt

        date_totals = {}
        for t in transactions:
            date_totals[t.date] = date_totals.get(t.date, 0.0) + t.amount

        dates = sorted(date_totals.keys())
        amounts = [date_totals[d] for d in dates]

        plt.figure(figsize=(10, 6))
        plt.plot(dates, amounts, marker="o", linestyle="-", color="blue", linewidth=2)
        plt.xticks(rotation=45, ha="right")
        plt.xlabel("Date")
        plt.ylabel("Total Spending")
        plt.title("Spending Over Time")
        plt.tight_layout()
        show_or_save_plot(plt, "trends.png")
        plt.close()

    except Exception as e:
        print(f"❌ Visualization failed: {e}")


def visualize_budgets_vs_spending(transactions: List[Transaction], budgets: Dict[str, float]):
    """Show budget limits vs actual spending by category."""
    if not budgets:
        print("No saved category budgets found yet.")
        return

    if not transactions:
        print("No transactions found yet.")
        return

    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt

        category_totals = {}
        for t in transactions:
            category_totals[t.category] = category_totals.get(t.category, 0.0) + t.amount

        categories = list(budgets.keys())
        limits = [budgets[cat] for cat in categories]
        spent = [category_totals.get(cat, 0.0) for cat in categories]

        colors = []
        for cat, limit, actual in zip(categories, limits, spent):
            if actual >= limit:
                colors.append("red")
            elif actual >= 0.8 * limit:
                colors.append("yellow")
            else:
                colors.append("green")

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