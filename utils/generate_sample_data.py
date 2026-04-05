import pandas as pd
from datetime import datetime, timedelta
import random
import os

def generate_sample_data(num_transactions=100):
    """Generate realistic sample financial data for demo purposes"""

    # Date range: last 6 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=180)

    # Sample data lists
    expense_categories = ["🍔 Food", "🚗 Transport", "🛍️ Shopping", "🎮 Entertainment", "🏥 Health", "📚 Education", "🏠 Rent", "📄 Bills"]
    income_categories = ["💼 Salary", "💻 Freelance", "📈 Investment", "🎁 Gift"]

    expense_amounts = {
        "🍔 Food": (100, 1500),
        "🚗 Transport": (50, 800),
        "🛍️ Shopping": (500, 5000),
        "🎮 Entertainment": (200, 2000),
        "🏥 Health": (500, 5000),
        "📚 Education": (1000, 10000),
        "🏠 Rent": (10000, 15000),
        "📄 Bills": (500, 3000)
    }

    income_amounts = {
        "💼 Salary": (40000, 60000),
        "💻 Freelance": (5000, 20000),
        "📈 Investment": (2000, 10000),
        "🎁 Gift": (500, 5000)
    }

    descriptions_expense = [
        "Dinner at restaurant", "Grocery shopping", "Online shopping", 
        "Movie tickets", "Fuel", "Electricity bill", "Medicine",
        "Course subscription", "Monthly rent", "Internet bill"
    ]

    descriptions_income = [
        "Monthly salary", "Project payment", "Stock dividend",
        "Birthday gift", "Bonus", "Freelance work"
    ]

    # Generate transactions
    transactions = []

    for i in range(num_transactions):
        # 70% expenses, 30% income
        trans_type = "Expense" if random.random() < 0.7 else "Income"
        
        # Random date
        random_date = start_date + timedelta(days=random.randint(0, 180))
        
        if trans_type == "Expense":
            category = random.choice(expense_categories)
            min_amt, max_amt = expense_amounts[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            description = random.choice(descriptions_expense)
        else:
            category = random.choice(income_categories)
            min_amt, max_amt = income_amounts[category]
            amount = round(random.uniform(min_amt, max_amt), 2)
            description = random.choice(descriptions_income)
        
        transactions.append({
            'Date': random_date.strftime("%Y-%m-%d"),
            'Type': trans_type,
            'Category': category,
            'Amount': amount,
            'Description': description
        })

    # Create DataFrame and sort by date
    df = pd.DataFrame(transactions)
    df = df.sort_values('Date').reset_index(drop=True)

    return df

if __name__ == "__main__":
    # Generate and save sample data
    os.makedirs('data', exist_ok=True)
    sample_df = generate_sample_data(150)
    sample_df.to_csv('data/sample_transactions.csv', index=False)
    print(f"Success! Generated {len(sample_df)} sample transactions")
    print(f"\nSummary:")
    print(f"Total Income: {sample_df[sample_df['Type']=='Income']['Amount'].sum():,.2f}")
    print(f"Total Expenses: {sample_df[sample_df['Type']=='Expense']['Amount'].sum():,.2f}")
