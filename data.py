import json
import os

DATA_FILE = "expenses.json"

def load():
    if not os.path.exists(DATA_FILE):
        return {"expenses": [], "budgets": {}, "next_id": 1}
    with open(DATA_FILE) as f:
        return json.load(f)

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
