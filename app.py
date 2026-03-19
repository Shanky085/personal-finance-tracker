import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# ── PAGE CONFIG ──────────────────────────
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide"
)

# ── TITLE ────────────────────────────────
st.title("💰 Personal Finance Tracker")
st.subheader("Track your daily expenses smartly")

# ── CSV FILE SETUP ───────────────────────
CSV_FILE = "expenses.csv"

def load_data():
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Fix column dtypes on load
        df["Date"] = df["Date"].astype(str)
        df["Category"] = df["Category"].astype(str)
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df["Description"] = df["Description"].astype(str)
        return df
    else:
        df = pd.DataFrame({
            "Date": pd.Series(dtype="str"),
            "Category": pd.Series(dtype="str"),
            "Amount": pd.Series(dtype="float"),
            "Description": pd.Series(dtype="str")
        })
        df.to_csv(CSV_FILE, index=False)
        return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# Load data at start
df = load_data()
# ── SUMMARY CARDS ────────────────────────
if not df.empty:
    st.markdown("---")
    col1, col2, col3, col4 = st.columns(4)
    
    total_spent = df["Amount"].sum()
    total_transactions = len(df)
    highest = df["Amount"].max()
    top_category = df.groupby("Category")["Amount"].sum().idxmax()
    
    with col1:
        st.metric("💸 Total Spent", f"₹{total_spent:.2f}")
    with col2:
        st.metric("🔢 Transactions", total_transactions)
    with col3:
        st.metric("📈 Highest Expense", f"₹{highest:.2f}")
    with col4:
        st.metric("🏆 Top Category", top_category)
# ── ADD EXPENSE SECTION ──────────────────
st.markdown("---")
st.header("➕ Add New Expense")

col1, col2 = st.columns(2)

with col1:
    date = st.date_input("Date")
    category = st.selectbox("Category", [
        "Food",
        "Transport",
        "Shopping",
        "Entertainment",
        "Health",
        "Education",
        "Rent",
        "Other"
    ])

with col2:
    amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
    description = st.text_input("Description", placeholder="e.g. Lunch at canteen")

if st.button("Add Expense"):
    if amount == 0:
        st.error("Amount cannot be zero!")
    elif description == "":
        st.error("Please enter a description!")
    else:
        new_row = pd.DataFrame([{
            "Date": str(date),
            "Category": str(category),
            "Amount": float(amount),
            "Description": str(description)
        }])
        df = pd.concat([df, new_row], ignore_index=True)
        save_data(df)
        st.success("Expense added successfully! ✅")
        st.rerun()
# ── DISPLAY EXPENSES ─────────────────────
st.markdown("---")
st.header("📋 All Expenses")

if df.empty:
    st.info("No expenses added yet. Add your first expense above!")
else:
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Show total at bottom
    total = df["Amount"].sum()
    st.metric(label="💰 Total Spent", value=f"₹{total:.2f}")
# ── DELETE EXPENSE ───────────────────────
st.markdown("---")
st.header("🗑️ Delete Expense")

if df.empty:
    st.info("No expenses to delete!")
else:
    # Create a readable label for each expense
    df["Label"] = df["Date"] + " | " + df["Category"] + " | ₹" + df["Amount"].astype(str) + " | " + df["Description"]
    
    selected = st.selectbox("Select expense to delete", df["Label"])
    
    if st.button("Delete Expense"):
        # Find the index of selected row
        index_to_delete = df[df["Label"] == selected].index[0]
        df = df.drop(index=index_to_delete).reset_index(drop=True)
        
        # Remove label column before saving
        df = df.drop(columns=["Label"])
        save_data(df)
        st.success("Expense deleted successfully! ✅")
        st.rerun()
# ── PIE CHART ────────────────────────────
st.markdown("---")
st.header("📊 Category Wise Breakdown")

if df.empty:
    st.info("Add some expenses to see the chart!")
else:
    # Group by category and sum amounts
    category_data = df.groupby("Category")["Amount"].sum()

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(
        category_data.values,
        labels=category_data.index,
        autopct="%1.1f%%",
        startangle=90,
        colors=plt.cm.Set3.colors
    )
    ax.set_title("Spending by Category", fontsize=14, fontweight="bold")
    
    # Center the chart
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.pyplot(fig)
# ── BAR GRAPH ────────────────────────────
st.markdown("---")
st.header("📈 Monthly Summary")

if df.empty:
    st.info("Add some expenses to see the chart!")
else:
    # Extract month from date
    df["Month"] = pd.to_datetime(df["Date"], format='mixed', errors='coerce').dt.strftime("%Y-%m")
    df = df.dropna(subset=["Month"])
    
    # Group by month and sum amounts
    monthly_data = df.groupby("Month")["Amount"].sum()

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(
        monthly_data.index,
        monthly_data.values,
        color=plt.cm.Set2.colors[:len(monthly_data)],
        edgecolor="white",
        width=0.4
    )
    
    # Add amount on top of each bar
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height + 5,
            f"₹{height:.0f}",
            ha="center",
            va="bottom",
            fontweight="bold",
            fontsize=10
        )
    
    ax.set_title("Monthly Spending Summary", fontsize=14, fontweight="bold")
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Total Amount (₹)", fontsize=11)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    
    st.pyplot(fig)
    
    # Clean up Month column
    df = df.drop(columns=["Month"])
# # ── PAYTM PDF UPLOAD ─────────────────────
st.markdown("---")
st.header("🏦 Import Paytm Statement")

st.info("Upload your Paytm UPI Statement PDF to auto-import transactions!")

uploaded_file = st.file_uploader("Choose Paytm PDF", type=["pdf"])

if uploaded_file is not None:
    try:
        import pdfplumber
        import re

        transactions = []

        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if not text:
                    continue

                lines = text.split("\n")
                i = 0
                while i < len(lines):
                    line = lines[i].strip()

                    # Match date line like "19 Mar" or "19 Mar 5:27 PM"
                    date_match = re.match(
                        r"^(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))",
                        line
                    )

                    if date_match:
                        date_str = date_match.group(1)

                        # Look ahead for description, tag and amount
                        description = ""
                        tag = "Other"
                        amount_str = ""

                        for j in range(i+1, min(i+8, len(lines))):
                            next_line = lines[j].strip()

                            # Get description (Paid to / Received from)
                            if ("Paid to" in next_line or
                                "Received from" in next_line or
                                "Money sent" in next_line):
                                description = next_line

                            # Get tag
                            tag_match = re.search(r"#\s*(\w+)", next_line)
                            if tag_match:
                                raw_tag = tag_match.group(1).strip()
                                # Map Paytm tags to our categories
                                tag_map = {
                                    "Food": "Food",
                                    "Groceries": "Food",
                                    "Grocery": "Food",
                                    "Transport": "Transport",
                                    "Taxi": "Transport",
                                    "Shopping": "Shopping",
                                    "Medical": "Health",
                                    "Education": "Education",
                                    "Rent": "Rent",
                                    "MoneyTransfer": "Other",
                                    "MoneyReceived": "Other",
                                    "Miscellaneous": "Other"
                                }
                                tag = tag_map.get(raw_tag, "Other")

                            # Get amount
                            amount_match = re.search(
                                r"([+-])\s*Rs\.([0-9,]+(?:\.\d+)?)",
                                next_line
                            )
                            if amount_match:
                                sign = amount_match.group(1)
                                amount_str = amount_match.group(2).replace(",", "")

                        # Only import payments (minus transactions)
                        if amount_str and description:
                            try:
                                amount_val = float(amount_str)
                                # Skip received money
                                transactions.append({
                                    "Date": f"{date_str} 2026",
                                    "Category": tag,
                                    "Amount": amount_val,
                                    "Description": description
                                })
                            except:
                                pass

                    i += 1

        if transactions:
            st.success(f"Found {len(transactions)} transactions!")

            preview_df = pd.DataFrame(transactions)
            st.subheader("Preview:")
            st.dataframe(preview_df, use_container_width=True, hide_index=True)

            # Show total
            total_import = preview_df["Amount"].sum()
            st.metric("Total to Import", f"₹{total_import:.2f}")

            if st.button("Import All Transactions"):
                new_df = pd.DataFrame(transactions)
                df = pd.concat([df, new_df], ignore_index=True)
                save_data(df)
                st.success(f"Successfully imported {len(transactions)} transactions! ✅")
                st.rerun()
        else:
            st.warning("No transactions found. Make sure it's a Paytm UPI statement PDF.")

    except Exception as e:
        st.error(f"Error: {e}")
# ── FOOTER ───────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>Personal Finance Tracker | "
    "Built with Python & Streamlit</p>",
    unsafe_allow_html=True
)