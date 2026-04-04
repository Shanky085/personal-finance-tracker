import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide",
)

# ── CONSTANTS ────────────────────────────────────────────────────────────────
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CSV_FILE = os.path.join(DATA_DIR, "transactions.csv")

EXPENSE_CATEGORIES = [
    "Food", "Transport", "Shopping", "Entertainment",
    "Health", "Education", "Rent", "Bills", "Other",
]
INCOME_CATEGORIES = ["Salary", "Freelance", "Investment", "Gift", "Other"]

COLUMNS = ["Date", "Type", "Category", "Amount", "Description"]


# ── DATA HELPERS ─────────────────────────────────────────────────────────────
def load_data() -> pd.DataFrame:
    """Load transactions from CSV, creating file & directory if needed."""
    os.makedirs(DATA_DIR, exist_ok=True)

    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        # Backward-compat: add Type column if missing (legacy expenses.csv)
        if "Type" not in df.columns:
            df["Type"] = "Expense"
        df["Date"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")
        df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
        df["Category"] = df["Category"].astype(str)
        df["Description"] = df["Description"].astype(str)
        df["Type"] = df["Type"].astype(str)
        df = df.dropna(subset=["Date", "Amount"])
        return df[COLUMNS]

    # First run — return empty DataFrame
    empty = pd.DataFrame({c: pd.Series(dtype="str") for c in COLUMNS})
    empty["Amount"] = pd.Series(dtype="float")
    empty["Date"] = pd.Series(dtype="datetime64[ns]")
    return empty


def save_data(df: pd.DataFrame) -> None:
    """Persist DataFrame to CSV."""
    os.makedirs(DATA_DIR, exist_ok=True)
    df.to_csv(CSV_FILE, index=False)


def add_transaction(df: pd.DataFrame, date, txn_type, category, amount, description) -> pd.DataFrame:
    """Append a single transaction and save."""
    new_row = pd.DataFrame([{
        "Date": pd.to_datetime(date),
        "Type": txn_type,
        "Category": category,
        "Amount": float(amount),
        "Description": description,
    }])
    df = pd.concat([df, new_row], ignore_index=True)
    save_data(df)
    return df


# ── MIGRATE LEGACY CSV ───────────────────────────────────────────────────────
def _migrate_legacy_csv():
    """One-time migration: move root expenses.csv → data/transactions.csv."""
    legacy = os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.csv")
    if os.path.exists(legacy) and not os.path.exists(CSV_FILE):
        os.makedirs(DATA_DIR, exist_ok=True)
        legacy_df = pd.read_csv(legacy)
        if "Type" not in legacy_df.columns:
            legacy_df["Type"] = "Expense"
        legacy_df.to_csv(CSV_FILE, index=False)


_migrate_legacy_csv()

# ── LOAD DATA ────────────────────────────────────────────────────────────────
df = load_data()

# ── CUSTOM STYLING ───────────────────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 16px 20px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 14px rgba(102,126,234,.35);
    }
    [data-testid="stMetric"] label { color: rgba(255,255,255,.85) !important; }
    [data-testid="stMetric"] [data-testid="stMetricValue"] { color: #fff !important; }
    div[data-testid="stTabs"] button[data-baseweb="tab"] {
        font-size: 1.05rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# ── HEADER ───────────────────────────────────────────────────────────────────
st.title("💰 Personal Finance Tracker")
st.caption("Track your income & expenses smartly")

# ── TABS ─────────────────────────────────────────────────────────────────────
tab_overview, tab_add, tab_transactions, tab_charts, tab_import = st.tabs([
    "📊 Overview",
    "➕ Add Transaction",
    "📋 Transactions",
    "📈 Charts",
    "🏦 Import",
])

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    if df.empty:
        st.info("No transactions yet. Head over to **Add Transaction** to get started!")
    else:
        total_income = df.loc[df["Type"] == "Income", "Amount"].sum()
        total_expenses = df.loc[df["Type"] == "Expense", "Amount"].sum()
        balance = total_income - total_expenses

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("💵 Total Income", f"₹{total_income:,.2f}")
        with col2:
            st.metric("💸 Total Expenses", f"₹{total_expenses:,.2f}")
        with col3:
            st.metric("🏦 Current Balance", f"₹{balance:,.2f}",
                       delta=f"₹{balance:,.2f}",
                       delta_color="normal" if balance >= 0 else "inverse")

        st.markdown("---")

        # Quick stats row
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("🔢 Transactions", len(df))
        with c2:
            exp_df = df[df["Type"] == "Expense"]
            if not exp_df.empty:
                st.metric("📈 Highest Expense", f"₹{exp_df['Amount'].max():,.2f}")
            else:
                st.metric("📈 Highest Expense", "—")
        with c3:
            if not exp_df.empty:
                top_cat = exp_df.groupby("Category")["Amount"].sum().idxmax()
                st.metric("🏆 Top Category", top_cat)
            else:
                st.metric("🏆 Top Category", "—")
        with c4:
            latest = df.sort_values("Date", ascending=False).iloc[0]
            st.metric("🕐 Latest", f"₹{latest['Amount']:,.2f} ({latest['Category']})")

        st.markdown("---")

        # Recent transactions preview
        st.subheader("🕑 Recent Transactions")
        recent = df.sort_values("Date", ascending=False).head(5).copy()
        recent["Date"] = recent["Date"].dt.strftime("%Y-%m-%d")
        st.dataframe(recent, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — ADD TRANSACTION
# ═══════════════════════════════════════════════════════════════════════════════
with tab_add:
    st.header("➕ Add New Transaction")

    col_left, col_right = st.columns(2)

    with col_left:
        txn_type = st.radio("Type", ["Expense", "Income"], horizontal=True)
        date = st.date_input("Date")
        categories = EXPENSE_CATEGORIES if txn_type == "Expense" else INCOME_CATEGORIES
        category = st.selectbox("Category", categories)

    with col_right:
        amount = st.number_input("Amount (₹)", min_value=0.01, format="%.2f")
        description = st.text_input("Description", placeholder="e.g. Lunch at canteen")

    if st.button("Add Transaction", type="primary", use_container_width=True):
        if amount <= 0:
            st.error("Amount must be greater than zero!")
        elif not description.strip():
            st.error("Please enter a description!")
        else:
            df = add_transaction(df, date, txn_type, category, amount, description.strip())
            st.success(f"{txn_type} of ₹{amount:,.2f} added successfully! ✅")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — TRANSACTIONS TABLE + DELETE
# ═══════════════════════════════════════════════════════════════════════════════
with tab_transactions:
    st.header("📋 All Transactions")

    if df.empty:
        st.info("No transactions added yet.")
    else:
        # Filters
        fcol1, fcol2 = st.columns(2)
        with fcol1:
            filter_type = st.multiselect("Filter by Type", ["Income", "Expense"], default=["Income", "Expense"])
        with fcol2:
            all_cats = sorted(df["Category"].unique().tolist())
            filter_cats = st.multiselect("Filter by Category", all_cats, default=all_cats)

        view_df = df[df["Type"].isin(filter_type) & df["Category"].isin(filter_cats)].copy()
        view_df["Date"] = view_df["Date"].dt.strftime("%Y-%m-%d")
        st.dataframe(view_df, use_container_width=True, hide_index=True)

        total_filtered = view_df["Amount"].sum()
        st.metric(label="💰 Filtered Total", value=f"₹{total_filtered:,.2f}")

        # Delete section
        st.markdown("---")
        st.subheader("🗑️ Delete a Transaction")

        labels = (
            df["Date"].dt.strftime("%Y-%m-%d") + " | " +
            df["Type"] + " | " +
            df["Category"] + " | ₹" +
            df["Amount"].astype(str) + " | " +
            df["Description"]
        )
        selected = st.selectbox("Select transaction to delete", labels)

        if st.button("Delete Transaction", type="secondary"):
            idx = labels[labels == selected].index[0]
            df = df.drop(index=idx).reset_index(drop=True)
            save_data(df)
            st.success("Transaction deleted! ✅")
            st.rerun()

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — CHARTS
# ═══════════════════════════════════════════════════════════════════════════════
with tab_charts:
    st.header("📈 Financial Charts")

    if df.empty:
        st.info("Add some transactions to see charts!")
    else:
        chart_col1, chart_col2 = st.columns(2)

        # ── Pie chart: Expenses by Category ──────────────────────────────────
        with chart_col1:
            st.subheader("🍩 Expenses by Category")
            exp_df = df[df["Type"] == "Expense"]
            if exp_df.empty:
                st.info("No expenses recorded yet.")
            else:
                cat_totals = exp_df.groupby("Category")["Amount"].sum().reset_index()
                fig_pie = px.pie(
                    cat_totals,
                    names="Category",
                    values="Amount",
                    hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Set3,
                )
                fig_pie.update_traces(textinfo="percent+label", pull=[0.03] * len(cat_totals))
                fig_pie.update_layout(
                    margin=dict(t=30, b=0, l=0, r=0),
                    legend=dict(orientation="h", y=-0.15),
                    height=420,
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        # ── Bar chart: Income vs Expenses over time ──────────────────────────
        with chart_col2:
            st.subheader("📊 Income vs Expenses Over Time")
            chart_df = df.copy()
            chart_df["Month"] = chart_df["Date"].dt.to_period("M").astype(str)
            monthly = (
                chart_df.groupby(["Month", "Type"])["Amount"]
                .sum()
                .reset_index()
            )

            color_map = {"Income": "#2ecc71", "Expense": "#e74c3c"}
            fig_bar = px.bar(
                monthly,
                x="Month",
                y="Amount",
                color="Type",
                barmode="group",
                color_discrete_map=color_map,
                text_auto=",.0f",
            )
            fig_bar.update_layout(
                xaxis_title="Month",
                yaxis_title="Amount (₹)",
                margin=dict(t=30, b=0, l=0, r=0),
                legend=dict(orientation="h", y=-0.2),
                height=420,
            )
            st.plotly_chart(fig_bar, use_container_width=True)

        # ── Cumulative balance line chart ─────────────────────────────────────
        st.markdown("---")
        st.subheader("📉 Balance Trend")

        trend_df = df.sort_values("Date").copy()
        trend_df["Signed"] = trend_df.apply(
            lambda r: r["Amount"] if r["Type"] == "Income" else -r["Amount"], axis=1
        )
        trend_df["Balance"] = trend_df["Signed"].cumsum()

        fig_line = px.area(
            trend_df,
            x="Date",
            y="Balance",
            color_discrete_sequence=["#667eea"],
        )
        fig_line.update_layout(
            xaxis_title="Date",
            yaxis_title="Cumulative Balance (₹)",
            margin=dict(t=30, b=0, l=0, r=0),
            height=350,
        )
        st.plotly_chart(fig_line, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
#  TAB 5 — IMPORT PAYTM PDF
# ═══════════════════════════════════════════════════════════════════════════════
with tab_import:
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

                        date_match = re.match(
                            r"^(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))",
                            line,
                        )

                        if date_match:
                            date_str = date_match.group(1)
                            description = ""
                            tag = "Other"
                            amount_str = ""

                            for j in range(i + 1, min(i + 8, len(lines))):
                                next_line = lines[j].strip()

                                if any(kw in next_line for kw in ("Paid to", "Received from", "Money sent")):
                                    description = next_line

                                tag_match = re.search(r"#\s*(\w+)", next_line)
                                if tag_match:
                                    raw_tag = tag_match.group(1).strip()
                                    tag_map = {
                                        "Food": "Food", "Groceries": "Food", "Grocery": "Food",
                                        "Transport": "Transport", "Taxi": "Transport",
                                        "Shopping": "Shopping", "Medical": "Health",
                                        "Education": "Education", "Rent": "Rent",
                                        "MoneyTransfer": "Other", "MoneyReceived": "Other",
                                        "Miscellaneous": "Other",
                                    }
                                    tag = tag_map.get(raw_tag, "Other")

                                amount_match = re.search(
                                    r"([+-])\s*Rs\.([0-9,]+(?:\.\d+)?)", next_line
                                )
                                if amount_match:
                                    amount_str = amount_match.group(2).replace(",", "")

                            if amount_str and description:
                                try:
                                    amount_val = float(amount_str)
                                    transactions.append({
                                        "Date": f"{date_str} 2026",
                                        "Type": "Expense",
                                        "Category": tag,
                                        "Amount": amount_val,
                                        "Description": description,
                                    })
                                except ValueError:
                                    pass

                        i += 1

            if transactions:
                st.success(f"Found {len(transactions)} transactions!")

                preview_df = pd.DataFrame(transactions)
                st.subheader("Preview:")
                st.dataframe(preview_df, use_container_width=True, hide_index=True)

                total_import = preview_df["Amount"].sum()
                st.metric("Total to Import", f"₹{total_import:,.2f}")

                if st.button("Import All Transactions"):
                    new_df = pd.DataFrame(transactions)
                    df = pd.concat([df, new_df], ignore_index=True)
                    save_data(df)
                    st.success(f"Successfully imported {len(transactions)} transactions! ✅")
                    st.rerun()
            else:
                st.warning("No transactions found. Make sure it's a Paytm UPI statement PDF.")

        except ImportError:
            st.error("Please install pdfplumber: `pip install pdfplumber`")
        except Exception as e:
            st.error(f"Error processing PDF: {e}")

# ── FOOTER ───────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:gray;'>Personal Finance Tracker | "
    "Built with Python & Streamlit</p>",
    unsafe_allow_html=True,
)