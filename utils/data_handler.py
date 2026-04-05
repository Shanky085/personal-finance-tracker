import pandas as pd
import os
from datetime import datetime

DATA_FILE = "expenses.csv"

EXPENSE_CATEGORIES = [
    "🍔 Food", "🚗 Transport", "🛍️ Shopping", "🎮 Entertainment",
    "🏥 Health", "📚 Education", "🏠 Rent", "📄 Bills", "📦 Other"
]

INCOME_CATEGORIES = [
    "💼 Salary", "💻 Freelance", "📈 Investment", "🎁 Gift", "📦 Other"
]

def load_data():
    """Load transaction data from CSV file with backward compatibility"""
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)

        # Backward compatibility: add Type column if missing
        if "Type" not in df.columns:
            df["Type"] = "Expense"

        # Parse dates
        df["Date"] = pd.to_datetime(df["Date"], errors='coerce')

        # Ensure Amount is numeric
        df["Amount"] = pd.to_numeric(df["Amount"], errors='coerce').fillna(0)

        return df
    else:
        # Return empty DataFrame with correct schema
        return pd.DataFrame(columns=["Date", "Type", "Category", "Amount", "Description"])

def save_data(df):
    """Save transaction data to CSV file"""
    try:
        df.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        print(f"Error saving data: {e}")
        return False
