"""
Data Visualization Module for Personal Finance Tracker v2.0

This module abstracts the heavy lifting for generating interactive analytical figures.
We use Plotly Express to create dynamic, hoverable glassmorphic-styled charts.
"""

import pandas as pd
import plotly.express as px
import streamlit as st

@st.cache_data
def plot_category_pie(df: pd.DataFrame):
    """
    Generate an interactive pie chart representing total expenses structurally categorized.
    
    This function isolates 'Expense' typed transactions, aggregates their amounts,
    and constructs a Plotly pie chart customized with a dark/transparent theme 
    to visually match the Streamlit dashboard aesthetic.
    
    Args:
        df (pd.DataFrame): The active operational DataFrame encompassing all transactions.
        
    Returns:
        plotly.graph_objs._figure.Figure or None: 
            A populated Plotly Express Figure object ready to be rendered in Streamlit.
            Returns None if there are absolutely no expenses logged.
            
    Example:
        >>> fig = plot_category_pie(transaction_dataframe)
        >>> if fig: st.plotly_chart(fig)
    """
    # Isolate strictly expenses for categorization mapping
    chart_df = df[df["Type"] == "Expense"] if "Type" in df.columns else df
    
    if chart_df.empty:
        return None
        
    category_data = chart_df.groupby("Category", as_index=False)["Amount"].sum()
    
    try:
        # PLOTLY CUSTOMIZATION:
        # 1. We use a defined color sequence (px.colors.qualitative.Pastel) for bright, appealing contrast against dark modes.
        # 2. hole=0.4 creates a modern 'donut' chart aesthetic instead of a flat pie.
        fig = px.pie(
            category_data,
            names="Category",
            values="Amount",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        
        # PLOTLY CUSTOMIZATION: Update layout hides the opaque background forcing transparency
        # to perfectly overlay on our Streamlit custom CSS gradient background.
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(t=40, b=40, l=0, r=0)
        )
        
        return fig
    except Exception as e:
        st.error(f"⚠️ Render Error (Pie Chart): The graphics engine encountered a localized failure.")
        return None


@st.cache_data
def plot_monthly_bar(df: pd.DataFrame):
    """
    Generate an interactive bar chart summarizing total transaction amounts historically by month.
    
    This abstracts parsing of datetime strings natively into months, groups data collectively, 
    and returns a Plotly bar chart heavily formatted with tooltips and transparent UI.
    
    Args:
        df (pd.DataFrame): The active operational DataFrame encompassing all transactions.
        
    Returns:
        plotly.graph_objs._figure.Figure or None: 
            A populated Plotly Express Figure object. Returns None if date parsing fails locally
            or if the DataFrame strictly lacks chronological elements.
            
    Example:
        >>> fig = plot_monthly_bar(transaction_dataframe)
        >>> if fig: st.plotly_chart(fig)
    """
    chart_df2 = df.copy()
    
    # Intelligently convert ambiguous dates dynamically extracting strictly Year-Month layout
    chart_df2["Month"] = pd.to_datetime(chart_df2["Date"], format='mixed', errors='coerce').dt.strftime("%b %Y")
    chart_df2 = chart_df2.dropna(subset=["Month"])
    
    if chart_df2.empty:
        return None
        
    monthly_data = chart_df2.groupby("Month", as_index=False)["Amount"].sum()
    
    try:
        # PLOTLY CUSTOMIZATION:
        # 1. Bar charts natively support hover_data. Using text_auto allows amounts to snap directly to the bar.
        fig = px.bar(
            monthly_data,
            x="Month",
            y="Amount",
            text_auto="$.2s",
            color="Month",
            color_discrete_sequence=px.colors.diverging.Spectral
        )
        
        # PLOTLY CUSTOMIZATION:
        # 1. Hiding the legend to save screen real estate.
        # 2. Applying strict margins and transparent background mapping for seamless HTML blending.
        fig.update_layout(
            showlegend=False,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            xaxis_title="Timeline",
            yaxis_title="Total Transactions (₹)",
            margin=dict(t=20, b=20, l=20, r=20)
        )
        
        return fig
    except Exception as e:
        st.error(f"⚠️ Render Error (Bar Chart): Failed to synthesize timeline mapping.")
        return None
