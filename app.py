"""
Personal Finance Tracker v2.0
=============================

A comprehensive Streamlit Dashboard for local personal financial tracking.
Features an AI-powered financial advisor, visually stunning glassmorphism 
UI components, and dynamically generated Plotly analytical figures.

Author: Shank
Date: 2026-04-05
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv

# Load from .env for local, st.secrets for cloud
load_dotenv()
from utils.data_handler import load_data, save_data, EXPENSE_CATEGORIES, INCOME_CATEGORIES
from utils.charts import plot_category_pie, plot_monthly_bar

# ── PAGE CONFIG ──────────────────────────
st.set_page_config(
    page_title="Personal Finance Tracker",
    page_icon="💰",
    layout="wide"
)

st.markdown("""
<style>
.metric-container {
    background: rgba(255, 255, 255, 0.08);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 1.5rem;
    border: 1px solid rgba(255, 255, 255, 0.15);
    text-align: center;
    transition: all 0.5s cubic-bezier(0.23, 1, 0.32, 1);
}

.metric-container:hover {
    transform: translateY(-10px);
    box-shadow: 0 25px 50px rgba(102, 126, 234, 0.5);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.8; }
}

.metric-label {
    color: rgba(255, 255, 255, 0.7);
    font-size: 0.9rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 0.5rem;
}

.income-metric .metric-value {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.expense-metric .metric-value {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.glass-card {
    background: rgba(128, 128, 128, 0.1);
    backdrop-filter: blur(20px);
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
    border: 1px solid rgba(128, 128, 128, 0.2);
    transition: all 0.3s ease;
}

@media (max-width: 768px) {
    .main-title { font-size: 2rem !important; }
    .metric-container { padding: 1rem !important; }
}
</style>
""", unsafe_allow_html=True)

if 'monthly_budget' not in st.session_state:
    st.session_state.monthly_budget = 50000

# ── TITLE ────────────────────────────────
st.title("💰 Personal Finance Tracker")
st.subheader("Track your income & expenses smartly")

# ── LOAD DATA ────────────────────────────
df = load_data()

# ── CREATE TABS ──────────────────────────
tab_overview, tab_add, tab_history, tab_charts, tab_import = st.tabs([
    "📊 Overview",
    "➕ Add Transaction",
    "📋 Transactions",
    "📈 Charts",
    "🏦 Import"
])

# ══════════════════════════════════════════
# TAB 1: OVERVIEW
# ══════════════════════════════════════════
with tab_overview:
    if df.empty:
        st.info("👋 Welcome! Start by adding your first transaction in the **➕ Add Transaction** tab.")
    else:
        # Calculate income, expense, and balance
        if "Type" in df.columns:
            income_total = df[df["Type"] == "Income"]["Amount"].sum()
            expense_total = df[df["Type"] == "Expense"]["Amount"].sum()
        else:
            income_total = 0.0
            expense_total = df["Amount"].sum()

        balance = income_total - expense_total

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-container income-metric">
                <div class="metric-value">₹{income_total:,.0f}</div>
                <div class="metric-label">💰 Total Income</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col2:
            st.markdown(f"""
            <div class="metric-container expense-metric">
                <div class="metric-value">₹{expense_total:,.0f}</div>
                <div class="metric-label">💸 Total Expenses</div>
            </div>
            """, unsafe_allow_html=True)
            
        with col3:
            balance_class = "income-metric" if balance >= 0 else "expense-metric"
            st.markdown(f"""
            <div class="metric-container {balance_class}">
                <div class="metric-value">₹{balance:,.0f}</div>
                <div class="metric-label">💎 Current Balance</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🎯 Budget Tracker")

        col1, col2 = st.columns([2, 1])

        with col1:
            # Get current month's expenses
            from datetime import datetime
            current_month = datetime.now().month
            current_year = datetime.now().year
            
            # Ensure Date column is in datetime format
            df["_temp_date"] = pd.to_datetime(df["Date"], format="mixed", errors="coerce")
            
            current_month_expenses = df[
                (df['Type'] == 'Expense') & 
                (df['_temp_date'].dt.month == current_month) & 
                (df['_temp_date'].dt.year == current_year)
            ]['Amount'].sum()
            
            # Drop the temporary column
            df = df.drop(columns=["_temp_date"])
            
            # Budget input
            monthly_budget = st.number_input(
                "Set Monthly Budget (₹)", 
                min_value=0, 
                value=st.session_state.monthly_budget, 
                step=1000,
                key="budget_input"
            )
            st.session_state.monthly_budget = monthly_budget
            
            # Calculate remaining
            remaining = monthly_budget - current_month_expenses
            progress = min(current_month_expenses / monthly_budget, 1.0) if monthly_budget > 0 else 0
            
            # Progress bar
            st.progress(float(progress))
            
            # Alert messages
            if remaining < 0:
                st.error(f"⚠️ Over budget by ₹{abs(remaining):,.2f}!")
            elif remaining < monthly_budget * 0.2:
                st.warning(f"⚡ Only ₹{remaining:,.2f} remaining this month ({(remaining/monthly_budget*100):.1f}%)")
            else:
                st.success(f"✅ ₹{remaining:,.2f} remaining this month ({(remaining/monthly_budget*100):.1f}%)")

        with col2:
            st.markdown(f"""
            <div class="glass-card" style="text-align: center;">
                <h4 style="margin: 0;">This Month</h4>
                <h2 style="margin: 0.5rem 0;">₹{current_month_expenses:,.0f}</h2>
                <p style="opacity: 0.7; margin: 0; font-size: 0.9rem;">
                    of ₹{monthly_budget:,.0f} budget
                </p>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📈 Quick Stats")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            transaction_count = len(df)
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; color: #667eea;">📝</div>
                <div style="font-size: 1.5rem; font-weight: 600;">{transaction_count}</div>
                <div style="opacity: 0.7; font-size: 0.8rem;">Total Transactions</div>
            </div>
            """, unsafe_allow_html=True)

        with col2:
            avg_expense = df[df['Type'] == 'Expense']['Amount'].mean() if not df[df['Type'] == 'Expense'].empty else 0
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; color: #f5576c;">📊</div>
                <div style="font-size: 1.5rem; font-weight: 600;">₹{avg_expense:,.0f}</div>
                <div style="opacity: 0.7; font-size: 0.8rem;">Avg. Expense</div>
            </div>
            """, unsafe_allow_html=True)

        with col3:
            if not df[df['Type'] == 'Expense'].empty:
                top_category = df[df['Type'] == 'Expense'].groupby('Category')['Amount'].sum().idxmax()
            else:
                top_category = "N/A"
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; color: #43e97b;">🏆</div>
                <div style="font-size: 1rem; font-weight: 600;">{top_category}</div>
                <div style="opacity: 0.7; font-size: 0.8rem;">Top Spending</div>
            </div>
            """, unsafe_allow_html=True)

        with col4:
            total_income = df[df['Type'] == 'Income']['Amount'].sum() if "Type" in df.columns else 0
            total_expense = df[df['Type'] == 'Expense']['Amount'].sum() if "Type" in df.columns else df["Amount"].sum()
            
            # COMPLEX LOGIC EXPLANATION (Savings Rate)
            # The Savings Rate represents the percentage of unspent income.
            # We explicitly guard against division-by-zero errors (if total_income is 0)
            # and allow the mathematical calculation to dip into negative boundaries
            # gracefully representing a state of financial over-spending.
            savings_rate = ((total_income - total_expense) / total_income * 100) if total_income > 0 else 0
            
            st.markdown(f"""
            <div class="glass-card" style="text-align: center; padding: 1rem;">
                <div style="font-size: 2rem; color: #4facfe;">💹</div>
                <div style="font-size: 1.5rem; font-weight: 600;">{savings_rate:.1f}%</div>
                <div style="opacity: 0.7; font-size: 0.8rem;">Savings Rate</div>
            </div>
            """, unsafe_allow_html=True)

        # Recent transactions preview
        st.markdown("---")
        st.markdown("### 🤖 AI Financial Advisor")
        
        if st.button("💡 Get Personalized Insights", type="primary"):
            try:
                import google.generativeai as genai
                
                try:
                    # Try Streamlit Cloud secrets first
                    GOOGLE_API_KEY = st.secrets["GOOGLE_API_KEY"]
                except (FileNotFoundError, KeyError):
                    # Fall back to .env for local development
                    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
                
                if not GOOGLE_API_KEY:
                    st.error("⚠️ API key not configured. Please set GOOGLE_API_KEY in .env or Streamlit secrets.")
                    st.stop()
                    
                genai.configure(api_key=GOOGLE_API_KEY)
                model = genai.GenerativeModel('gemini-2.5-flash')
                
                # Prepare financial summary
                total_income = df[df['Type'] == 'Income']['Amount'].sum() if "Type" in df.columns else 0
                total_expense = df[df['Type'] == 'Expense']['Amount'].sum() if "Type" in df.columns else df['Amount'].sum()
                
                if "Type" in df.columns and not df[df['Type'] == 'Expense'].empty:
                    top_categories = df[df['Type'] == 'Expense'].groupby('Category')['Amount'].sum().nlargest(3)
                    top_cat_str = ", ".join([f"{cat}: ₹{amt:,.0f}" for cat, amt in top_categories.items()])
                elif "Type" not in df.columns and not df.empty:
                    top_categories = df.groupby('Category')['Amount'].sum().nlargest(3)
                    top_cat_str = ", ".join([f"{cat}: ₹{amt:,.0f}" for cat, amt in top_categories.items()])
                else:
                    top_cat_str = "No expenses recorded"
                
                # Create prompt
                prompt = f"""
                You are a personal finance advisor. Analyze this user's financial data and provide actionable advice:
                
                Financial Summary:
                - Total Income: ₹{total_income:,.0f}
                - Total Expenses: ₹{total_expense:,.0f}
                - Net Savings: ₹{total_income - total_expense:,.0f}
                - Top Spending Categories: {top_cat_str}
                
                Provide:
                1. A brief health assessment of their finances (2-3 sentences)
                2. Three specific, actionable saving tips based on their spending pattern
                3. One warning if they're overspending in any category
                
                Keep the tone friendly and encouraging. Use emojis. Format as bullet points.
                """
                
                # Get AI response
                with st.spinner("🧠 AI analyzing your finances..."):
                    response = model.generate_content(prompt)
                    
                    st.markdown(f"""
                    <div class="glass-card" style="margin-top: 1rem;">
                        {response.text}
                    </div>
                    """, unsafe_allow_html=True)
                    
            except ImportError:
                st.error("❌ google-generativeai not installed. Run: pip install google-generativeai")
            except Exception as e:
                st.warning(f"⚠️ AI feature unavailable: {e}")
                st.info("💡 Add your GOOGLE_API_KEY to Streamlit secrets to enable AI insights.")

        st.markdown("---")
        st.subheader("🕐 Recent Transactions")
        recent = df.tail(5).iloc[::-1]  # Last 5, newest first
        st.dataframe(recent, use_container_width=True, hide_index=True)

# ══════════════════════════════════════════
# TAB 2: ADD TRANSACTION
# ══════════════════════════════════════════
with tab_add:
    st.header("➕ Add New Transaction")

    # NEW: Income/Expense toggle
    transaction_type = st.radio(
        "Transaction Type",
        ["Expense", "Income"],
        horizontal=True
    )

    col1, col2 = st.columns(2)

    with col1:
        date = st.date_input("Date")
        # Conditional category selection based on type
        if transaction_type == "Expense":
            category = st.selectbox("Category", EXPENSE_CATEGORIES)
        else:
            category = st.selectbox("Category", INCOME_CATEGORIES)

    with col2:
        amount = st.number_input("Amount (₹)", min_value=0.0, format="%.2f")
        description = st.text_input("Description", placeholder="e.g. Lunch at canteen")

    if st.button("Add Transaction", type="primary"):
        if amount == 0:
            st.error("Amount cannot be zero!")
        elif description == "":
            st.error("Please enter a description!")
        else:
            new_row = pd.DataFrame([{
                "Date": str(date),
                "Category": str(category),
                "Amount": float(amount),
                "Description": str(description),
                "Type": transaction_type
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            save_data(df)
            st.success(f"{transaction_type} added successfully! ✅")
            st.rerun()

# ══════════════════════════════════════════
# TAB 3: TRANSACTIONS (View + Delete + Filter)
# ══════════════════════════════════════════
with tab_history:
    st.header("📋 All Transactions")

    if df.empty:
        st.info("No transactions added yet. Add your first transaction in the **➕ Add Transaction** tab!")
    else:
        # ── Filter Options (NEW) ─────────────
        # ── Filter Options ─────────────
        st.markdown("### 🔍 Filter Transactions")

        col1, col2, col3 = st.columns(3)

        with col1:
            filter_type = st.selectbox("Filter by Type", ["All", "Income", "Expense"])
            
        with col2:
            all_categories = ["All"] + sorted(list(df['Category'].unique()))
            filter_category = st.selectbox("Filter by Category", all_categories)
            
        with col3:
            sort_order = st.selectbox("Sort by Date", ["Newest First", "Oldest First"])

        # Apply the filters to create a filtered dataframe:
        filtered_df = df.copy()

        # Type filter
        if filter_type != "All":
            filtered_df = filtered_df[filtered_df['Type'] == filter_type]

        # Category filter
        if filter_category != "All":
            filtered_df = filtered_df[filtered_df['Category'] == filter_category]

        # Sort
        ascending = (sort_order == "Oldest First")
        filtered_df = filtered_df.sort_values(by="Date", ascending=ascending).reset_index(drop=True)

        st.markdown("---")
        st.markdown(f"**Showing {len(filtered_df)} of {len(df)} transactions**")

        # Display filtered data
        st.dataframe(
            filtered_df,
            use_container_width=True,
            column_config={
                "Date": st.column_config.DateColumn("📅 Date", format="DD/MM/YYYY"),
                "Type": st.column_config.TextColumn("💱 Type"),
                "Category": st.column_config.TextColumn("📁 Category"),
                "Amount": st.column_config.NumberColumn("💵 Amount", format="₹%.2f"),
                "Description": st.column_config.TextColumn("📝 Description")
            }
        )

        # Show totals
        total = filtered_df["Amount"].sum()
        st.metric(label=f"💰 Total ({filter_type})", value=f"₹{total:,.2f}")

        # ── Delete Section ───────────────────
        st.markdown("---")
        st.subheader("🗑️ Delete Transaction")

        if filtered_df.empty:
            st.info("No matching transactions to delete.")
        else:
            # Create a readable label for each transaction in the filtered view
            df_with_label = filtered_df.copy()
            df_with_label["Label"] = (
                df_with_label["Date"] + " | " +
                df_with_label["Category"] + " | ₹" +
                df_with_label["Amount"].astype(str) + " | " +
                df_with_label["Description"]
            )
            if "Type" in df_with_label.columns:
                df_with_label["Label"] = df_with_label["Label"] + " [" + df_with_label["Type"] + "]"

            selected = st.selectbox("Select transaction to delete", df_with_label["Label"])

            if st.button("Delete Transaction", type="secondary"):
                # Find the index of selected row in the ORIGINAL df
                original_df_labeled = df.copy()
                original_df_labeled["Label"] = (
                    original_df_labeled["Date"] + " | " +
                    original_df_labeled["Category"] + " | ₹" +
                    original_df_labeled["Amount"].astype(str) + " | " +
                    original_df_labeled["Description"]
                )
                if "Type" in original_df_labeled.columns:
                    original_df_labeled["Label"] = original_df_labeled["Label"] + " [" + original_df_labeled["Type"] + "]"
                    
                # Find index to delete
                index_to_delete = original_df_labeled[original_df_labeled["Label"] == selected].index[0]
                df = df.drop(index=index_to_delete).reset_index(drop=True)
                save_data(df)
                st.success("Transaction deleted successfully! ✅")
                st.rerun()
                
        st.markdown("---")
        st.markdown("### 📥 Export & Import")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Export Data")
            from datetime import datetime
            csv = df.to_csv(index=False)
            st.download_button(
                label="📥 Download as CSV",
                data=csv,
                file_name=f'finance_data_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                use_container_width=True
            )

        with col2:
            st.markdown("#### Import Data")
            uploaded_file = st.file_uploader("Upload CSV file", type=['csv'], label_visibility="collapsed")
            
            if uploaded_file is not None:
                try:
                    new_df = pd.read_csv(uploaded_file)
                    
                    # Validate columns
                    required_cols = ['Date', 'Type', 'Category', 'Amount', 'Description']
                    if all(col in new_df.columns for col in required_cols):
                        
                        # Parse dates
                        new_df['Date'] = pd.to_datetime(new_df['Date']).astype(str)
                        
                        # Merge with existing data (avoid duplicates)
                        combined_df = pd.concat([df, new_df]).drop_duplicates(subset=['Date', 'Category', 'Amount', 'Description']).reset_index(drop=True)
                        
                        if st.button("📤 Import Data", type="primary"):
                            save_data(combined_df)
                            st.success(f"✅ Imported {len(new_df)} transactions!")
                            st.rerun()
                    else:
                        st.error(f"❌ Invalid CSV format. Required columns: {required_cols}")
                        
                except Exception as e:
                    st.error(f"❌ Error reading file: {e}")

# ══════════════════════════════════════════
# TAB 4: CHARTS
# ══════════════════════════════════════════

with tab_charts:
    st.header("📈 Analytics")

    if df.empty:
        st.info("Add some transactions to see the charts!")
    else:
        # ── PIE CHART ────────────────────────
        st.subheader("📊 Category Wise Breakdown")
        
        fig_pie = plot_category_pie(df)
        if fig_pie is not None:
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.plotly_chart(fig_pie, use_container_width=True)
        else:
            st.info("No expenses to chart yet!")

        # ── BAR GRAPH ────────────────────────
        st.markdown("---")
        st.subheader("📈 Monthly Summary")

        fig_bar = plot_monthly_bar(df)
        if fig_bar is not None:
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("No valid dates to chart!")

# ══════════════════════════════════════════
# TAB 5: IMPORT
# ══════════════════════════════════════════
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
                                        "Food": "🍔 Food",
                                        "Groceries": "🍔 Food",
                                        "Grocery": "🍔 Food",
                                        "Transport": "🚗 Transport",
                                        "Taxi": "🚗 Transport",
                                        "Shopping": "🛍️ Shopping",
                                        "Medical": "🏥 Health",
                                        "Education": "📚 Education",
                                        "Rent": "🏠 Rent",
                                        "MoneyTransfer": "📦 Other",
                                        "MoneyReceived": "📦 Other",
                                        "Miscellaneous": "📦 Other"
                                    }
                                    tag = tag_map.get(raw_tag, "📦 Other")

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
                                    transactions.append({
                                        "Date": f"{date_str} 2026",
                                        "Category": tag,
                                        "Amount": amount_val,
                                        "Description": description,
                                        "Type": "Expense"
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
                st.metric("Total to Import", f"₹{total_import:,.2f}")

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
    "<p style='text-align:center; color:gray;'>Personal Finance Tracker v2.0 | "
    "Built with Python & Streamlit</p>",
    unsafe_allow_html=True
)