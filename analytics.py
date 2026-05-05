import os
import csv
from datetime import date
from data import load

def _get_month(month):
    return month if month else str(date.today())[:7]

def _filter_by_month(expenses, month):
    return [e for e in expenses if e["date"].startswith(month)]

def show_summary(month=None):
    month = _get_month(month)
    data = load()
    expenses = _filter_by_month(data["expenses"], month)

    if not expenses:
        print(f"\nNo expenses found for {month}.")
        return

    print(f"\n{'='*45}")
    print(f"  Monthly Summary — {month}")
    print(f"{'='*45}")

    # Category breakdown
    categories = {}
    for e in expenses:
        categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]

    total = sum(categories.values())
    print(f"\n{'Category':<18} {'Amount':>10}  {'Share':>7}")
    print("-" * 40)
    for cat, amt in sorted(categories.items(), key=lambda x: -x[1]):
        pct = amt / total * 100
        bar = "█" * int(pct / 5)
        print(f"{cat:<18} ₹{amt:>8.2f}  {pct:>5.1f}%  {bar}")
    print("-" * 40)
    print(f"{'TOTAL':<18} ₹{total:>8.2f}")

    # Daily average
    days_in_data = len(set(e["date"] for e in expenses))
    print(f"\nDaily average : ₹{total/days_in_data:.2f} ({days_in_data} active days)")
    print(f"Transactions  : {len(expenses)}")

    # Budget status
    budgets = data.get("budgets", {})
    if budgets:
        print(f"\n  Budget Status")
        print("-" * 40)
        for cat, budget in budgets.items():
            spent = categories.get(cat, 0)
            pct = spent / budget * 100 if budget > 0 else 0
            flag = "EXCEEDED" if pct >= 100 else ("WARNING" if pct >= 80 else "OK")
            print(f"  {cat:<15} {pct:>5.1f}% of ₹{budget:.0f}  [{flag}]")

def show_chart(month=None):
    try:
        import matplotlib.pyplot as plt
        import matplotlib.gridspec as gridspec
    except ImportError:
        print("Install matplotlib: pip install matplotlib")
        return

    month = _get_month(month)
    data = load()
    expenses = _filter_by_month(data["expenses"], month)

    if not expenses:
        print(f"\nNo expenses for {month} to chart.")
        return

    # Category totals
    categories = {}
    for e in expenses:
        categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]

    # Daily totals
    daily = {}
    for e in expenses:
        daily[e["date"]] = daily.get(e["date"], 0) + e["amount"]
    daily_sorted = sorted(daily.items())

    fig = plt.figure(figsize=(13, 5))
    fig.suptitle(f"Expense Report — {month}", fontsize=14, fontweight="bold", y=1.01)
    gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.4)

    # 1. Pie chart
    ax1 = fig.add_subplot(gs[0])
    colors = ["#4A90D9", "#E67E22", "#2ECC71", "#E74C3C", "#9B59B6", "#1ABC9C", "#F39C12"]
    wedges, texts, autotexts = ax1.pie(
        categories.values(), labels=categories.keys(),
        autopct="%1.1f%%", colors=colors[:len(categories)],
        pctdistance=0.8, startangle=140
    )
    for t in autotexts:
        t.set_fontsize(9)
    ax1.set_title("Spending by Category", fontsize=11)

    # 2. Bar chart
    ax2 = fig.add_subplot(gs[1])
    cats = list(categories.keys())
    vals = list(categories.values())
    bars = ax2.bar(cats, vals, color=colors[:len(cats)], edgecolor="white", linewidth=0.5)
    ax2.set_title("Category Amounts", fontsize=11)
    ax2.set_ylabel("Amount (₹)")
    ax2.tick_params(axis="x", rotation=30, labelsize=9)
    for bar, val in zip(bars, vals):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(vals)*0.01,
                 f"₹{val:.0f}", ha="center", va="bottom", fontsize=8)

    # 3. Line chart — daily trend
    ax3 = fig.add_subplot(gs[2])
    dates = [d[5:] for d, _ in daily_sorted]  # show MM-DD
    amounts = [a for _, a in daily_sorted]
    ax3.plot(dates, amounts, marker="o", color="#4A90D9", linewidth=2, markersize=5)
    ax3.fill_between(range(len(dates)), amounts, alpha=0.15, color="#4A90D9")
    ax3.set_xticks(range(len(dates)))
    ax3.set_xticklabels(dates, rotation=45, fontsize=8)
    ax3.set_title("Daily Spending Trend", fontsize=11)
    ax3.set_ylabel("Amount (₹)")

    plt.tight_layout()
    filename = f"chart_{month}.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    plt.show()
    print(f"\n✓ Chart saved as '{filename}'")

def export_csv(month=None):
    month = _get_month(month)
    data = load()
    expenses = _filter_by_month(data["expenses"], month)

    if not expenses:
        print(f"No expenses for {month}.")
        return

    filename = f"expenses_{month}.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["id", "date", "category", "amount", "description"])
        writer.writeheader()
        writer.writerows(expenses)
    print(f"✓ Exported {len(expenses)} expenses to '{filename}'")

def export_pdf(month=None):
    try:
        from fpdf import FPDF
    except ImportError:
        print("Install fpdf2: pip install fpdf2")
        return

    month = _get_month(month)
    data = load()
    expenses = _filter_by_month(data["expenses"], month)

    if not expenses:
        print(f"No expenses for {month}.")
        return

    categories = {}
    for e in expenses:
        categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]
    total = sum(categories.values())

    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_fill_color(44, 62, 80)
    pdf.rect(0, 0, 210, 35, "F")
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_y(8)
    pdf.cell(0, 10, "Expense Report", align="C", ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 8, f"Month: {month}   |   Total: Rs. {total:.2f}", align="C", ln=True)

    pdf.set_y(42)
    pdf.set_text_color(0, 0, 0)

    # Summary table
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "Category Summary", ln=True)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(80, 8, "Category", border=1, fill=True)
    pdf.cell(50, 8, "Amount (Rs.)", border=1, fill=True, align="R")
    pdf.cell(50, 8, "Share %", border=1, fill=True, align="R", ln=True)

    pdf.set_font("Helvetica", "", 10)
    for cat, amt in sorted(categories.items(), key=lambda x: -x[1]):
        pct = amt / total * 100
        pdf.cell(80, 7, cat, border=1)
        pdf.cell(50, 7, f"Rs. {amt:.2f}", border=1, align="R")
        pdf.cell(50, 7, f"{pct:.1f}%", border=1, align="R", ln=True)

    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(44, 62, 80)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(80, 8, "TOTAL", border=1, fill=True)
    pdf.cell(50, 8, f"Rs. {total:.2f}", border=1, fill=True, align="R")
    pdf.cell(50, 8, "100%", border=1, fill=True, align="R", ln=True)

    pdf.set_text_color(0, 0, 0)
    pdf.ln(6)

    # Transactions
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "All Transactions", ln=True)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_fill_color(230, 230, 230)
    for col, w in [("ID", 15), ("Date", 30), ("Category", 45), ("Amount", 35), ("Description", 65)]:
        pdf.cell(w, 7, col, border=1, fill=True)
    pdf.ln()

    pdf.set_font("Helvetica", "", 9)
    for i, e in enumerate(expenses):
        fill = i % 2 == 0
        pdf.set_fill_color(245, 245, 245)
        pdf.cell(15, 6, str(e["id"]), border=1, fill=fill)
        pdf.cell(30, 6, e["date"], border=1, fill=fill)
        pdf.cell(45, 6, e["category"], border=1, fill=fill)
        pdf.cell(35, 6, f"Rs. {e['amount']:.2f}", border=1, fill=fill, align="R")
        desc = e["description"][:30] + "..." if len(e["description"]) > 30 else e["description"]
        pdf.cell(65, 6, desc, border=1, fill=fill, ln=True)

    # Footer
    pdf.set_y(-20)
    pdf.set_font("Helvetica", "I", 8)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, f"Generated by Expense Tracker  |  {date.today()}", align="C")

    filename = f"report_{month}.pdf"
    pdf.output(filename)
    print(f"✓ PDF report saved as '{filename}'")
