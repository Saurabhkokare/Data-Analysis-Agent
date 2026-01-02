import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import os
import uuid

def save_plot(filename_prefix="plot"):
    """Saves the current plot to a file and clears the figure."""
    filename = f"{filename_prefix}_{uuid.uuid4().hex[:8]}.png"
    filepath = os.path.join(os.getcwd(), filename)
    plt.savefig(filepath, bbox_inches='tight')
    plt.close()
    return filepath

def generate_histogram(df, column, title=None, bins=10):
    """Generates a histogram for a specific column."""
    plt.figure(figsize=(10, 6))
    sns.histplot(df[column], bins=bins, kde=True)
    plt.title(title or f"Histogram of {column}")
    plt.xlabel(column)
    plt.ylabel("Frequency")
    return save_plot("histogram")

def generate_scatter_plot(df, x_column, y_column, title=None):
    """Generates a scatter plot."""
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x=x_column, y=y_column)
    plt.title(title or f"Scatter Plot: {x_column} vs {y_column}")
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    return save_plot("scatter")

def generate_line_plot(df, x_column, y_column, title=None):
    """Generates a line plot."""
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=df, x=x_column, y=y_column)
    plt.title(title or f"Line Plot: {x_column} vs {y_column}")
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    return save_plot("line")

def generate_bar_plot(df, x_column, y_column, title=None):
    """Generates a bar plot."""
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x=x_column, y=y_column)
    plt.title(title or f"Bar Plot: {x_column} vs {y_column}")
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.xticks(rotation=45)
    return save_plot("bar")

def generate_correlation_heatmap(df, title=None):
    """Generates a correlation heatmap for numeric columns."""
    plt.figure(figsize=(12, 10))
    numeric_df = df.select_dtypes(include=['number'])
    if numeric_df.empty:
        return "No numeric columns for correlation heatmap."
    sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', fmt=".2f")
    plt.title(title or "Correlation Heatmap")
    return save_plot("heatmap")
