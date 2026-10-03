# visualizations.py
from typing import List, Dict
from models import Transaction
from services import calculate_spending_by_category, calculate_spending_by_date
from utils import show_or_save_plot, ensure_matplotlib_tk_icons

def visualize_spending(transactions: List[Transaction]) -> None:
    """Show pie chart of spending by category."""
    if not transactions:
        print("No transactions found yet.")
        return
    
    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt
        
        category_totals = calculate_spending_by_category(transactions)
        
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

def visualize_trends(transactions: List[Transaction]) -> None:
    """Show line chart of spending over time."""
    if not transactions:
        print("No transactions found yet.")
        return
    
    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt
        
        date_totals = calculate_spending_by_date(transactions)
        
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

def visualize_budgets_vs_spending(
    transactions: List[Transaction], 
    budgets: Dict[str, float]
) -> None:
    """Show bar chart comparing budgets vs actual spending."""
    if not budgets:
        print("No saved category budgets found yet.")
        return
    
    if not transactions:
        print("No transactions found yet.")
        return
    
    try:
        ensure_matplotlib_tk_icons()
        import matplotlib.pyplot as plt
        
        category_totals = calculate_spending_by_category(transactions)
        
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
        plt.bar([i+0.4 for i in x], spent, width=0.4, label="Actual Spending", color=colors, align="center")
        
        plt.xticks([i+0.2 for i in x], categories, rotation=45)
        plt.ylabel("Amount")
        plt.title("Budgets vs. Spending by Category")
        plt.legend()
        plt.tight_layout()
        show_or_save_plot(plt, "budgets_vs_spending.png")
    
    except Exception as e:
        print(f"Visualization failed: {e}")