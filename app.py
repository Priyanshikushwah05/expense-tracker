from flask import Flask, jsonify, request
from flask_cors import CORS
import json, os
from datetime import date

app = Flask(__name__)
CORS(app)

DATA_FILE = "expenses.json"

def load():
    if not os.path.exists(DATA_FILE):
        return {"expenses": [], "budgets": {}, "next_id": 1}
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/api/expenses", methods=["GET"])
def get_expenses():
    data = load()
    month = request.args.get("month")
    category = request.args.get("category")
    expenses = data["expenses"]
    if month:
        expenses = [e for e in expenses if e["date"].startswith(month)]
    if category:
        expenses = [e for e in expenses if e["category"].lower() == category.lower()]
    return jsonify(expenses)

@app.route("/api/expenses", methods=["POST"])
def add_expense():
    body = request.json
    data = load()
    entry = {
        "id": data["next_id"],
        "date": str(date.today()),
        "amount": float(body["amount"]),
        "category": body["category"].capitalize(),
        "description": body["description"]
    }
    data["expenses"].append(entry)
    data["next_id"] += 1
    save(data)
    # budget alert
    alert = None
    budgets = data.get("budgets", {})
    cat = entry["category"]
    if cat in budgets:
        month = str(date.today())[:7]
        spent = sum(e["amount"] for e in data["expenses"] if e["category"] == cat and e["date"].startswith(month))
        budget = budgets[cat]
        pct = spent / budget * 100
        if pct >= 100:
            alert = {"type": "exceeded", "message": f"You have exceeded your {cat} budget! (₹{spent:.0f} / ₹{budget:.0f})"}
        elif pct >= 80:
            alert = {"type": "warning", "message": f"{pct:.0f}% of your {cat} budget used (₹{spent:.0f} / ₹{budget:.0f})"}
    return jsonify({"expense": entry, "alert": alert}), 201

@app.route("/api/expenses/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    data = load()
    data["expenses"] = [e for e in data["expenses"] if e["id"] != expense_id]
    save(data)
    return jsonify({"success": True})

@app.route("/api/budgets", methods=["GET"])
def get_budgets():
    data = load()
    month = str(date.today())[:7]
    expenses = [e for e in data["expenses"] if e["date"].startswith(month)]
    result = []
    for cat, budget in data.get("budgets", {}).items():
        spent = sum(e["amount"] for e in expenses if e["category"] == cat)
        pct = spent / budget * 100 if budget > 0 else 0
        result.append({"category": cat, "budget": budget, "spent": spent, "percent": round(pct, 1)})
    return jsonify(result)

@app.route("/api/budgets", methods=["POST"])
def set_budget():
    body = request.json
    data = load()
    data["budgets"][body["category"].capitalize()] = float(body["amount"])
    save(data)
    return jsonify({"success": True})

@app.route("/api/summary", methods=["GET"])
def get_summary():
    month = request.args.get("month", str(date.today())[:7])
    data = load()
    expenses = [e for e in data["expenses"] if e["date"].startswith(month)]
    categories = {}
    daily = {}
    for e in expenses:
        categories[e["category"]] = categories.get(e["category"], 0) + e["amount"]
        daily[e["date"]] = daily.get(e["date"], 0) + e["amount"]
    total = sum(categories.values())
    return jsonify({
        "month": month,
        "total": total,
        "count": len(expenses),
        "categories": [{"name": k, "amount": v, "percent": round(v/total*100, 1) if total else 0}
                       for k, v in sorted(categories.items(), key=lambda x: -x[1])],
        "daily": [{"date": k, "amount": v} for k, v in sorted(daily.items())]
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)
