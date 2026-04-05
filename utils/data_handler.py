"""
Data Handler Module for Personal Finance Tracker v2.0

This module abstracts CSV-based persistent storage operations. It offers utilities
to load and save transaction data recursively, mapping schema differences smoothly.
Specifically, it provides guaranteed backward compatibility mapping for older
v1.0 `expenses.csv` structures.
"""

import os
import pandas as pd
import streamlit as st

# ── FILE PATHS ──────────────────────────────
CSV_PRIMARY = os.path.join("data", "transactions.csv")
CSV_FALLBACK = "expenses.csv"  # v1.0 backward compatibility

# ── CATEGORY LISTS ──────────────────────────
EXPENSE_CATEGORIES = [
    "🍔 Food",
    "🚗 Transport",
    "🛍️ Shopping",
    "🎮 Entertainment",
    "🏥 Health",
    "📚 Education",
    "🏠 Rent",
    "📄 Bills",
    "📦 Other"
]

INCOME_CATEGORIES = [
    "💼 Salary",
    "💻 Freelance",
    "📈 Investment",
    "🎁 Gift",
    "📦 Other"
]

# ── COLUMN DEFINITIONS ─────────────────────
COLUMNS = ["Date", "Category", "Amount", "Description", "Type"]


@st.cache_data
def load_data():
    """
    Load transaction data dynamically from the persistent CSV datastore.
    
    This function checks optimal file paths sequentially. If the modern 
    'data/transactions.csv' format is missing, it falls back to parsing 
    the legacy 'expenses.csv' file logic. Missing columns like 'Type' 
    are intelligently populated to maintain modern dashboard integrity.
    
    Returns:
        pd.DataFrame: A normalized Pandas DataFrame containing all user transactions.
                      If no files exist, an empty initialized DataFrame is returned.
        
    Example:
        >>> df = load_data()
        >>> print(len(df))
    """
    df = None

    # Priority 1: Check if the v2.0 optimized data structure exists
    try:
        if os.path.exists(CSV_PRIMARY):
            df = pd.read_csv(CSV_PRIMARY)
        # Priority 2: Fall back to legacy monolithic path logic
        elif os.path.exists(CSV_FALLBACK):
            df = pd.read_csv(CSV_FALLBACK)
    except Exception as e:
        st.error(f"⚠️ Database Error: Unable to read files correctly. ({str(e)[:50]}...)")
        df = None
    
    if df is not None:
        # Standardizing numerical and datetime primitives iteratively
        df["Date"] = df["Date"].astype(str)
        df["Category"] = df["Category"].astype(str)
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df["Description"] = df["Description"].astype(str)
        
        # BACKWARD COMPATIBILITY CHECK:
        # v1.0 scripts only recorded flat expenses without a Type label.
        # This auto-fills the entire historical dataset contextually to "Expense".
        if "Type" not in df.columns:
            df["Type"] = "Expense"
        
        return df
    else:
        # Initialization contingency: Generate a completely new DB block with correct types
        df = pd.DataFrame({
            "Date": pd.Series(dtype="str"),
            "Category": pd.Series(dtype="str"),
            "Amount": pd.Series(dtype="float"),
            "Description": pd.Series(dtype="str"),
            "Type": pd.Series(dtype="str")
        })
        # Explicitly build missing directories contextually
        os.makedirs(os.path.dirname(CSV_PRIMARY), exist_ok=True)
        df.to_csv(CSV_PRIMARY, index=False)
        return df


def save_data(df):
    """
    Overrides the core transactional CSV datastore with updated user ledger.
    
    Args:
        df (pd.DataFrame): The mutated, modified, or appended DataFrame table
                           holding the final computed state of transactions.
        
    Returns:
        None: Executes filesystem flush contextually without returning artifacts.
        
    Example:
        >>> updated_df = df.drop(index=0)
        >>> save_data(updated_df)
    """
    # Defensive programming: Recursively build the data folder if accidentally purged
    try:
        os.makedirs(os.path.dirname(CSV_PRIMARY), exist_ok=True)
        df.to_csv(CSV_PRIMARY, index=False)
        # Clear the in-memory cache to ensure dashboard immediately reflects new appended entries.
        load_data.clear()
    except Exception as e:
        st.error(f"⚠️ Failed to save transactions permanently to disk: {str(e)[:50]}...")
