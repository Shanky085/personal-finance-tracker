import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

def get_chart_theme():
    """Return consistent theme for all Plotly charts"""
    return dict(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='rgba(255,255,255,0.8)', family='Poppins'),
        margin=dict(l=20, r=20, t=40, b=20),
        legend=dict(
            bgcolor='rgba(255,255,255,0.05)',
            bordercolor='rgba(255,255,255,0.1)',
            borderwidth=1
        )
    )

def create_expense_pie_chart(df):
    """Generate pie chart for expenses by category"""
    expenses_df = df[df['Type'] == 'Expense']

    if expenses_df.empty:
        return None

    category_totals = expenses_df.groupby('Category')['Amount'].sum().reset_index()

    fig = px.pie(
        category_totals,
        values='Amount',
        names='Category',
        hole=0.5,
        color_discrete_sequence=px.colors.sequential.Plasma
    )

    fig.update_layout(**get_chart_theme())
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>₹%{value:,.0f}<extra></extra>'
    )

    return fig

def create_income_vs_expense_chart(df):
    """Generate bar chart comparing income vs expenses by month"""
    if df.empty:
        return None

    # Add Month column
    df_copy = df.copy()
    df_copy['Month'] = df_copy['Date'].dt.to_period('M').astype(str)

    monthly_summary = df_copy.groupby(['Month', 'Type'])['Amount'].sum().reset_index()

    fig = px.bar(
        monthly_summary,
        x='Month',
        y='Amount',
        color='Type',
        barmode='group',
        color_discrete_map={'Income': '#43e97b', 'Expense': '#f5576c'}
    )

    fig.update_layout(**get_chart_theme())
    fig.update_traces(hovertemplate='<b>%{x}</b><br>₹%{y:,.0f}<extra></extra>')

    return fig

def create_balance_trend_chart(df):
    """Generate line chart showing cumulative balance over time"""
    if df.empty:
        return None

    # Calculate daily balance
    daily_df = df.groupby(['Date', 'Type'])['Amount'].sum().unstack(fill_value=0).reset_index()

    if 'Income' not in daily_df.columns:
        daily_df['Income'] = 0
    if 'Expense' not in daily_df.columns:
        daily_df['Expense'] = 0

    daily_df['Balance'] = (daily_df['Income'] - daily_df['Expense']).cumsum()

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=daily_df['Date'],
        y=daily_df['Balance'],
        mode='lines+markers',
        name='Balance',
        line=dict(color='#667eea', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.2)',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>₹%{y:,.0f}<extra></extra>'
    ))

    fig.update_layout(**get_chart_theme(), title="Cumulative Balance Trend")

    return fig
