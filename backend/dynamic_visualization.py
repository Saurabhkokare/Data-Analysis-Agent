"""
Dynamic Visualization Module - Uses Plotly for interactive charts
Generates static PNG images from Plotly figures for reports
"""
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import pandas as pd
import uuid
import os
import traceback
import json

# Set default template for consistent styling
pio.templates.default = "plotly_dark"


def execute_plot_code(df: pd.DataFrame, code: str) -> str:
    """
    Executes the provided Python code to generate a Plotly plot.
    The code must use the variable 'df' which is the dataframe.
    The code should create a Plotly figure and assign it to 'fig'.
    
    Args:
        df (pd.DataFrame): The dataframe to analyze.
        code (str): The Python code to execute (should create 'fig' variable).
        
    Returns:
        str: The path to the saved image file, or an error message.
    """
    try:
        # Create output directory if it doesn't exist
        output_dir = os.path.join(os.getcwd(), "outputs", "graphs")
        os.makedirs(output_dir, exist_ok=True)
        
        # Create a unique filename
        filename = f"plot_{uuid.uuid4().hex[:8]}.png"
        filepath = os.path.join(output_dir, filename)
        
        # Prepare the execution environment with Plotly
        local_vars = {
            "df": df,
            "px": px,
            "go": go,
            "pd": pd,
            "fig": None
        }
        
        # Execute the code
        exec(code, {}, local_vars)
        
        # Get the figure from local vars
        fig = local_vars.get("fig")
        
        if fig is None:
            return "Error: Code must create a 'fig' variable with a Plotly figure"
        
        # Update layout for better export
        fig.update_layout(
            paper_bgcolor='rgba(15, 23, 42, 1)',
            plot_bgcolor='rgba(30, 41, 59, 1)',
            font=dict(color='#e2e8f0'),
            margin=dict(l=60, r=30, t=60, b=60)
        )
        
        # Save the plot as PNG
        fig.write_image(filepath, width=1200, height=700, scale=2)
        
        return filepath
    except Exception as e:
        return f"Error executing plot code: {str(e)}\nTraceback: {traceback.format_exc()}"


def create_bar_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "Bar Chart") -> str:
    """Create a bar chart and save as PNG."""
    output_dir = os.path.join(os.getcwd(), "outputs", "graphs")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"bar_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(output_dir, filename)
    
    fig = px.bar(df, x=x_col, y=y_col, title=title,
                 color_discrete_sequence=['#6366f1'])
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 1)',
        plot_bgcolor='rgba(30, 41, 59, 1)',
        font=dict(color='#e2e8f0')
    )
    fig.write_image(filepath, width=1200, height=700, scale=2)
    return filepath


def create_line_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "Line Chart") -> str:
    """Create a line chart and save as PNG."""
    output_dir = os.path.join(os.getcwd(), "outputs", "graphs")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"line_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(output_dir, filename)
    
    fig = px.line(df, x=x_col, y=y_col, title=title,
                  color_discrete_sequence=['#10b981'])
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 1)',
        plot_bgcolor='rgba(30, 41, 59, 1)',
        font=dict(color='#e2e8f0')
    )
    fig.write_image(filepath, width=1200, height=700, scale=2)
    return filepath


def create_pie_chart(df: pd.DataFrame, names_col: str, values_col: str, title: str = "Pie Chart") -> str:
    """Create a pie chart and save as PNG."""
    output_dir = os.path.join(os.getcwd(), "outputs", "graphs")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"pie_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(output_dir, filename)
    
    fig = px.pie(df, names=names_col, values=values_col, title=title,
                 color_discrete_sequence=['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6'])
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 1)',
        font=dict(color='#e2e8f0')
    )
    fig.write_image(filepath, width=1200, height=700, scale=2)
    return filepath


def create_histogram(df: pd.DataFrame, col: str, title: str = "Histogram") -> str:
    """Create a histogram and save as PNG."""
    output_dir = os.path.join(os.getcwd(), "outputs", "graphs")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"hist_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(output_dir, filename)
    
    fig = px.histogram(df, x=col, title=title,
                       color_discrete_sequence=['#f59e0b'])
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 1)',
        plot_bgcolor='rgba(30, 41, 59, 1)',
        font=dict(color='#e2e8f0')
    )
    fig.write_image(filepath, width=1200, height=700, scale=2)
    return filepath


def create_scatter_chart(df: pd.DataFrame, x_col: str, y_col: str, title: str = "Scatter Plot") -> str:
    """Create a scatter plot and save as PNG."""
    output_dir = os.path.join(os.getcwd(), "outputs", "graphs")
    os.makedirs(output_dir, exist_ok=True)
    filename = f"scatter_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(output_dir, filename)
    
    fig = px.scatter(df, x=x_col, y=y_col, title=title,
                     color_discrete_sequence=['#ec4899'])
    fig.update_layout(
        paper_bgcolor='rgba(15, 23, 42, 1)',
        plot_bgcolor='rgba(30, 41, 59, 1)',
        font=dict(color='#e2e8f0')
    )
    fig.write_image(filepath, width=1200, height=700, scale=2)
    return filepath
