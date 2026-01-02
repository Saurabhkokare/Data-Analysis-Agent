"""
Dashboard Generator - Creates interactive HTML dashboards similar to Power BI/Tableau
Uses Plotly.js for dynamic visualizations
"""
import os
import uuid
import json
from datetime import datetime
import pandas as pd


def generate_dashboard(df: pd.DataFrame, title: str = "Data Analysis Dashboard", 
                       chart_configs: list = None) -> str:
    """
    Generates an interactive HTML dashboard with multiple charts and KPIs.
    
    Args:
        df: The DataFrame to visualize
        title: Dashboard title
        chart_configs: Optional list of chart configurations
        
    Returns:
        str: Path to the generated HTML dashboard
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.getcwd(), "outputs", "dashboards")
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate unique filename
    filename = f"dashboard_{uuid.uuid4().hex[:8]}.html"
    filepath = os.path.join(output_dir, filename)
    
    # Analyze data for automatic insights
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    # Generate KPI cards
    kpis = []
    if len(numeric_cols) > 0:
        for col in numeric_cols[:4]:  # Max 4 KPIs
            kpis.append({
                'title': col.replace('_', ' ').title(),
                'value': f"{df[col].mean():,.2f}",
                'subtitle': f"Avg of {len(df)} records"
            })
    
    if not kpis:
        kpis = [{'title': 'Total Records', 'value': str(len(df)), 'subtitle': 'Rows in dataset'}]
    
    # Generate chart data
    charts_html = []
    chart_id = 0
    
    # Chart 1: Bar chart of first numeric column by first categorical
    if numeric_cols and categorical_cols:
        col_num = numeric_cols[0]
        col_cat = categorical_cols[0]
        grouped = df.groupby(col_cat)[col_num].mean().head(10)
        charts_html.append(generate_bar_chart(f'chart_{chart_id}', grouped.index.tolist(), 
                                               grouped.values.tolist(), 
                                               f'{col_num} by {col_cat}', col_cat, col_num))
        chart_id += 1
    
    # Chart 2: Line chart if multiple numeric columns
    if len(numeric_cols) >= 2:
        x_data = list(range(min(50, len(df))))
        y_data = df[numeric_cols[1]].head(50).tolist()
        charts_html.append(generate_line_chart(f'chart_{chart_id}', x_data, y_data,
                                                f'{numeric_cols[1]} Trend', 'Index', numeric_cols[1]))
        chart_id += 1
    
    # Chart 3: Pie chart for categorical distribution
    if categorical_cols:
        col = categorical_cols[0]
        dist = df[col].value_counts().head(8)
        charts_html.append(generate_pie_chart(f'chart_{chart_id}', dist.index.tolist(),
                                               dist.values.tolist(), f'{col} Distribution'))
        chart_id += 1
    
    # Chart 4: Histogram of numeric data
    if numeric_cols:
        col = numeric_cols[0]
        charts_html.append(generate_histogram(f'chart_{chart_id}', df[col].dropna().tolist(),
                                               f'{col} Distribution', col))
        chart_id += 1
    
    # Generate HTML
    html_content = generate_dashboard_html(title, kpis, charts_html, df)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return filepath


def generate_bar_chart(chart_id: str, x_data: list, y_data: list, title: str, 
                       x_label: str, y_label: str) -> str:
    """Generate a bar chart configuration."""
    return f"""
    <div class="chart-container" id="{chart_id}_container">
        <div id="{chart_id}"></div>
        <script>
            Plotly.newPlot('{chart_id}', [{{
                x: {json.dumps([str(x) for x in x_data])},
                y: {json.dumps(y_data)},
                type: 'bar',
                marker: {{
                    color: 'rgba(99, 102, 241, 0.8)',
                    line: {{ color: 'rgba(99, 102, 241, 1)', width: 1 }}
                }}
            }}], {{
                title: '{title}',
                xaxis: {{ title: '{x_label}' }},
                yaxis: {{ title: '{y_label}' }},
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: {{ color: '#e2e8f0' }},
                margin: {{ t: 50, r: 30, b: 50, l: 60 }}
            }}, {{responsive: true}});
        </script>
    </div>
    """


def generate_line_chart(chart_id: str, x_data: list, y_data: list, title: str,
                        x_label: str, y_label: str) -> str:
    """Generate a line chart configuration."""
    return f"""
    <div class="chart-container" id="{chart_id}_container">
        <div id="{chart_id}"></div>
        <script>
            Plotly.newPlot('{chart_id}', [{{
                x: {json.dumps(x_data)},
                y: {json.dumps(y_data)},
                type: 'scatter',
                mode: 'lines+markers',
                line: {{ color: 'rgba(16, 185, 129, 1)', width: 2 }},
                marker: {{ color: 'rgba(16, 185, 129, 1)', size: 6 }}
            }}], {{
                title: '{title}',
                xaxis: {{ title: '{x_label}' }},
                yaxis: {{ title: '{y_label}' }},
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: {{ color: '#e2e8f0' }},
                margin: {{ t: 50, r: 30, b: 50, l: 60 }}
            }}, {{responsive: true}});
        </script>
    </div>
    """


def generate_pie_chart(chart_id: str, labels: list, values: list, title: str) -> str:
    """Generate a pie chart configuration."""
    colors = ['#6366f1', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899', '#14b8a6', '#f97316']
    return f"""
    <div class="chart-container" id="{chart_id}_container">
        <div id="{chart_id}"></div>
        <script>
            Plotly.newPlot('{chart_id}', [{{
                labels: {json.dumps([str(l) for l in labels])},
                values: {json.dumps([int(v) if isinstance(v, (int, float)) else v for v in values])},
                type: 'pie',
                marker: {{ colors: {json.dumps(colors[:len(labels)])} }},
                textinfo: 'label+percent',
                textfont: {{ color: '#fff' }}
            }}], {{
                title: '{title}',
                paper_bgcolor: 'rgba(0,0,0,0)',
                font: {{ color: '#e2e8f0' }},
                margin: {{ t: 50, r: 30, b: 30, l: 30 }},
                showlegend: true,
                legend: {{ font: {{ color: '#e2e8f0' }} }}
            }}, {{responsive: true}});
        </script>
    </div>
    """


def generate_histogram(chart_id: str, data: list, title: str, x_label: str) -> str:
    """Generate a histogram configuration."""
    return f"""
    <div class="chart-container" id="{chart_id}_container">
        <div id="{chart_id}"></div>
        <script>
            Plotly.newPlot('{chart_id}', [{{
                x: {json.dumps(data)},
                type: 'histogram',
                marker: {{
                    color: 'rgba(245, 158, 11, 0.7)',
                    line: {{ color: 'rgba(245, 158, 11, 1)', width: 1 }}
                }}
            }}], {{
                title: '{title}',
                xaxis: {{ title: '{x_label}' }},
                yaxis: {{ title: 'Frequency' }},
                paper_bgcolor: 'rgba(0,0,0,0)',
                plot_bgcolor: 'rgba(0,0,0,0)',
                font: {{ color: '#e2e8f0' }},
                margin: {{ t: 50, r: 30, b: 50, l: 60 }}
            }}, {{responsive: true}});
        </script>
    </div>
    """


def generate_dashboard_html(title: str, kpis: list, charts: list, df: pd.DataFrame) -> str:
    """Generate the complete dashboard HTML."""
    kpi_cards = ""
    for kpi in kpis:
        kpi_cards += f"""
        <div class="kpi-card">
            <div class="kpi-title">{kpi['title']}</div>
            <div class="kpi-value">{kpi['value']}</div>
            <div class="kpi-subtitle">{kpi['subtitle']}</div>
        </div>
        """
    
    
    charts_html = "\n".join(charts)
    
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        html, body {{
            height: 100vh;
            overflow: hidden;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
            height: 100vh;
            color: #e2e8f0;
            display: flex;
            flex-direction: column;
        }}
        
        .dashboard-header {{
            background: rgba(30, 41, 59, 0.9);
            backdrop-filter: blur(10px);
            padding: 12px 30px;
            border-bottom: 1px solid rgba(99, 102, 241, 0.3);
            display: flex;
            justify-content: space-between;
            align-items: center;
            flex-shrink: 0;
        }}
        
        .dashboard-title {{
            font-size: 22px;
            font-weight: 700;
            background: linear-gradient(90deg, #6366f1, #8b5cf6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .dashboard-date {{
            color: #94a3b8;
            font-size: 12px;
        }}
        
        .dashboard-container {{
            flex: 1;
            padding: 15px;
            display: flex;
            flex-direction: column;
            gap: 15px;
            overflow: hidden;
        }}
        
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            flex-shrink: 0;
        }}
        
        .kpi-card {{
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 12px 16px;
            border: 1px solid rgba(99, 102, 241, 0.2);
            text-align: center;
        }}
        
        .kpi-title {{
            font-size: 11px;
            color: #94a3b8;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
        }}
        
        .kpi-value {{
            font-size: 24px;
            font-weight: 700;
            background: linear-gradient(90deg, #6366f1, #10b981);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        
        .kpi-subtitle {{
            font-size: 10px;
            color: #64748b;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 12px;
            flex: 1;
            min-height: 0;
        }}
        
        .chart-container {{
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            border-radius: 12px;
            padding: 10px;
            border: 1px solid rgba(99, 102, 241, 0.2);
            display: flex;
            flex-direction: column;
            min-height: 0;
        }}
        
        .chart-container > div {{
            flex: 1;
            min-height: 0;
        }}
        
        @media (max-width: 1000px) {{
            .kpi-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            .charts-grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <header class="dashboard-header">
        <h1 class="dashboard-title">📊 {title}</h1>
        <span class="dashboard-date">Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}</span>
    </header>
    
    <main class="dashboard-container">
        <div class="kpi-grid">
            {kpi_cards}
        </div>
        
        <div class="charts-grid">
            {charts_html}
        </div>
    </main>
</body>
</html>"""


def create_dashboard_from_data(df: pd.DataFrame, dashboard_config: str = None) -> str:
    """
    Main entry point for the dashboard tool.
    
    Args:
        df: DataFrame to visualize
        dashboard_config: Optional JSON string with dashboard configuration
        
    Returns:
        str: Path to the generated HTML dashboard file
    """
    title = "Data Analysis Dashboard"
    
    if dashboard_config:
        try:
            config = json.loads(dashboard_config)
            title = config.get('title', title)
        except json.JSONDecodeError:
            pass
    
    return generate_dashboard(df, title)
