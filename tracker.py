import json
import os
import argparse
from datetime import date, datetime
from data import load, save
from analytics import show_summary, show_chart, export_pdf, export_csv

def add_expense(amount, category, description):
    data = load()
    data["expenses"].append({
        "id": data["next_id"],
        "date": str(date.today()),
        "amount": float(amount),
        "category": category.capitalize(),
        "description": description
    })
    data["next_id"] += 1
    save(data)
    print(f"\n✓ Added ₹{float(amount):.2f} under '{category.capitalize()}'")
    _check_budget_alert(data, category.capitalize())

def delete_expense(expense_id):
    data = load()
    before = len(data["expenses"])
    data["expenses"] = [e for e in data["expenses"] if e["id"] != int(expense_id)]
    if len(data["expenses"]) < before:
        save(data)
        print(f"✓ Deleted expense #{expense_id}")
    else:
        print(f"✗ No expense found with ID #{expense_id}")

def list_expenses(category=None, month=None):
    data = load()
    expenses = data["expenses"]
    if category:
        expenses = [e for e in expenses if e["category"].lower() == category.lower()]
    if month:
        expenses = [e for e in expenses if e["date"].startswith(month)]
    if not expenses:
        print("\nNo expenses found.")
        return
    print(f"\n{'ID':<5} {'Date':<12} {'Category':<15} {'Amount':>10}  Description")
    print("-" * 65)
    total = 0
    for e in expenses:
        print(f"#{e['id']:<4} {e['date']:<12} {e['category']:<15} ₹{e['amount']:>8.2f}  {e['description']}")
        total += e["amount"]
    print("-" * 65)
    print(f"{'TOTAL':>34} ₹{total:>8.2f}")

def set_budget(category, amount):
    data = load()
    data["budgets"][category.capitalize()] = float(amount)
    save(data)
    print(f"✓ Budget for '{category.capitalize()}' set to ₹{float(amount):.2f}/month")

def list_budgets():
    data = load()
    budgets = data.get("budgets", {})
    if not budgets:
        print("\nNo budgets set. Use: python tracker.py budget set <category> <amount>")
        return
    today = str(date.today())[:7]
    expenses = [e for e in data["expenses"] if e["date"].startswith(today)]
    print(f"\n{'Category':<15} {'Budget':>10} {'Spent':>10} {'Remaining':>12} {'Status'}")
    print("-" * 60)
    for cat, budget in budgets.items():
        spent = sum(e["amount"] for e in expenses if e["category"] == cat)
        remaining = budget - spent
        pct = (spent / budget * 100) if budget > 0 else 0
        if pct >= 100:
            status = "EXCEEDED"
        elif pct >= 80:
            status = "WARNING"
        else:
            status = "OK"
        print(f"{cat:<15} ₹{budget:>8.2f} ₹{spent:>8.2f} ₹{remaining:>10.2f}  {status}")

def _check_budget_alert(data, category):
    budgets = data.get("budgets", {})
    if category not in budgets:
        return
    today = str(date.today())[:7]
    spent = sum(e["amount"] for e in data["expenses"]
                if e["category"] == category and e["date"].startswith(today))
    budget = budgets[category]
    pct = spent / budget * 100 if budget > 0 else 0
    if pct >= 100:
        print(f"  ⚠ ALERT: You have EXCEEDED your {category} budget! (₹{spent:.0f} / ₹{budget:.0f})")
    elif pct >= 80:
        print(f"  ⚠ WARNING: {pct:.0f}% of your {category} budget used (₹{spent:.0f} / ₹{budget:.0f})")

def main():
    parser = argparse.ArgumentParser(
        description="Expense Tracker — manage your finances from the terminal",
        formatter_class=argparse.RawTextHelpFormatter
    )
    sub = parser.add_subparsers(dest="cmd", metavar="command")

    # add
    p_add = sub.add_parser("add", help="Add a new expense")
    p_add.add_argument("amount", help="Amount in ₹")
    p_add.add_argument("category", help="Category (Food, Travel, etc.)")
    p_add.add_argument("description", help="Short description")

    # list
    p_list = sub.add_parser("list", help="List expenses")
    p_list.add_argument("--category", help="Filter by category")
    p_list.add_argument("--month", help="Filter by month (YYYY-MM)")

    # delete
    p_del = sub.add_parser("delete", help="Delete an expense by ID")
    p_del.add_argument("id", help="Expense ID")

    # budget
    p_bud = sub.add_parser("budget", help="Manage budgets")
    bud_sub = p_bud.add_subparsers(dest="bud_cmd")
    p_bud_set = bud_sub.add_parser("set", help="Set budget for a category")
    p_bud_set.add_argument("category")
    p_bud_set.add_argument("amount")
    bud_sub.add_parser("list", help="View budget status")

    # summary
    p_sum = sub.add_parser("summary", help="Show monthly analytics")
    p_sum.add_argument("--month", help="Month (YYYY-MM), defaults to current")

    # chart
    p_chart = sub.add_parser("chart", help="Show spending charts")
    p_chart.add_argument("--month", help="Month (YYYY-MM), defaults to current")

    # export
    p_exp = sub.add_parser("export", help="Export report")
    p_exp.add_argument("format", choices=["csv", "pdf"], help="Export format")
    p_exp.add_argument("--month", help="Month (YYYY-MM), defaults to current")

    args = parser.parse_args()

    if args.cmd == "add":
        add_expense(args.amount, args.category, args.description)
    elif args.cmd == "list":
        list_expenses(category=args.category, month=args.month)
    elif args.cmd == "delete":
        delete_expense(args.id)
    elif args.cmd == "budget":
        if args.bud_cmd == "set":
            set_budget(args.category, args.amount)
        elif args.bud_cmd == "list":
            list_budgets()
        else:
            p_bud.print_help()
    elif args.cmd == "summary":
        show_summary(args.month)
    elif args.cmd == "chart":
        show_chart(args.month)
    elif args.cmd == "export":
        if args.format == "csv":
            export_csv(args.month)
        elif args.format == "pdf":
            export_pdf(args.month)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
