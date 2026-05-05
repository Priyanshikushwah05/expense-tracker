#  Expense Tracker CLI

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=flat&logo=python&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat)

A command-line expense tracking application with budget alerts, visual analytics, and PDF/CSV report export — built entirely in Python.

---

##  Demo

> **Bar chart + pie chart + daily trend — all generated from the CLI**

![Chart Demo](screenshots/chart.png)

> **Auto-generated PDF report**

![PDF Demo](screenshots/pdf.png)

---

##  Features

- **Add & manage expenses** — log transactions with category, amount, and description
- **Budget alerts** — get warned at 80% and notified when you exceed a category budget
- **Visual analytics** — pie chart (category share), bar chart (amounts), line chart (daily trend)
- **PDF reports** — export a formatted monthly report with full transaction table
- **CSV export** — dump any month's data to CSV for use in Excel/Sheets
- **Filter & search** — view expenses by category or month

---

##  Project Structure

```
expense_tracker/
├── tracker.py       # CLI entry point — all commands defined here
├── data.py          # Data layer — load/save JSON storage
├── analytics.py     # Analytics — charts, summary, PDF & CSV export
├── expenses.json    # Auto-created on first run (your data)
└── README.md
```

**Architecture:** 3-layer design — CLI layer (`tracker.py`) → Logic/Analytics layer (`analytics.py`) → Data layer (`data.py`). Each layer has a single responsibility and is independently testable.

---

##  Setup

**Requirements:** Python 3.8+

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/expense-tracker.git
cd expense-tracker

# 2. Install dependencies
pip install matplotlib fpdf2

# 3. Run your first command
python tracker.py add 150 Food "Lunch at canteen"
```

---

##  Usage

### Add an expense
```bash
python tracker.py add <amount> <category> "<description>"

# Examples
python tracker.py add 150 Food "Lunch at canteen"
python tracker.py add 499 Entertainment "Netflix subscription"
python tracker.py add 1200 Transport "Monthly bus pass"
```

### List expenses
```bash
python tracker.py list                          # All expenses
python tracker.py list --category Food          # Filter by category
python tracker.py list --month 2024-05          # Filter by month
```

### Delete an expense
```bash
python tracker.py delete 3                      # Delete expense with ID #3
```

### Set & view budgets
```bash
python tracker.py budget set Food 3000          # Set ₹3000/month for Food
python tracker.py budget set Transport 1500
python tracker.py budget list                   # View budget vs actual
```

### Monthly summary (text)
```bash
python tracker.py summary                       # Current month
python tracker.py summary --month 2024-04       # Specific month
```

### Charts (opens a window)
```bash
python tracker.py chart                         # Current month
python tracker.py chart --month 2024-04
```

### Export
```bash
python tracker.py export csv                    # → expenses_2024-05.csv
python tracker.py export pdf                    # → report_2024-05.pdf
python tracker.py export pdf --month 2024-04    # Specific month
```

---

##  Sample Output

**`python tracker.py summary`**
```
=============================================
  Monthly Summary — 2024-05
=============================================

Category           Amount    Share
----------------------------------------
Food             ₹3,200.00  42.1%  ████████
Transport        ₹1,500.00  19.7%  ███
Entertainment    ₹1,200.00  15.8%  ███
Utilities        ₹  900.00  11.8%  ██
Misc             ₹  800.00  10.5%  ██
----------------------------------------
TOTAL            ₹7,600.00

Daily average : ₹380.00 (20 active days)
Transactions  : 34

  Budget Status
----------------------------------------
  Food            106.7% of ₹3000  [EXCEEDED]
  Transport       100.0% of ₹1500  [EXCEEDED]
  Entertainment    80.0% of ₹1500  [WARNING]
```

---

##  Tech Stack

| Tool | Purpose |
|------|---------|
| Python 3.8+ | Core language |
| `argparse` | CLI interface |
| `json` | Local data storage |
| `matplotlib` | Charts & visualizations |
| `fpdf2` | PDF report generation |
| `csv` | Data export |

---

##  What I Learned

- Designing a **modular CLI application** with clean separation of concerns
- Using `argparse` subparsers to build a multi-command CLI (similar to how `git` works)
- Generating **multi-panel Matplotlib figures** with GridSpec
- Creating **formatted PDF reports** programmatically with fpdf2
- Handling **persistent local storage** using JSON without a database

---

##  Possible Extensions

- [ ] SQLite backend instead of JSON (for larger datasets)
- [ ] Web dashboard using Flask/Streamlit
- [ ] Recurring expense scheduling
- [ ] Multi-user support with login

---

##  License

MIT License — free to use and modify.
