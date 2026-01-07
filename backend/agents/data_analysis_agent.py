"""
Data Analysis & Graph Agent - Specialized agent for data analysis and visualization
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_index.core.tools import FunctionTool, QueryEngineTool, ToolMetadata
from llama_index.experimental.query_engine import PandasQueryEngine
from llama_index.llms.groq import Groq
from llama_index.core.agent import FunctionAgent
import dynamic_visualization
import pandas as pd


class DataAnalysisGraphAgent:
    """
    Specialized agent for data analysis and graph/chart generation.
    Focuses on insights, statistics, and beautiful Plotly visualizations.
    """
    
    def __init__(self, df: pd.DataFrame, llm: Groq):
        self.df = df
        self.llm = llm
        
        # Primary Data Analysis Tool
        self.pandas_query_engine = PandasQueryEngine(
            df=self.df,
            llm=self.llm,
            verbose=True,
            synthesize_response=True
        )
        data_tool = QueryEngineTool(
            query_engine=self.pandas_query_engine,
            metadata=ToolMetadata(
                name="data_analysis_tool",
                description="Query the dataframe for statistics, counts, averages, correlations, and any data-related questions."
            )
        )
        
        # Custom Plotly Chart Generation
        def generate_custom_chart(code: str) -> str:
            """
            Generate a custom interactive Plotly chart.
            
            The code MUST:
            - Use 'df' variable (the pandas DataFrame)
            - Use 'px' (plotly.express) or 'go' (plotly.graph_objects)
            - Create a 'fig' variable with the Plotly figure
            - NOT include plt.show() or fig.show()
            
            Examples:
            - Bar: fig = px.bar(df, x='Category', y='Value', title='Sales by Category', color='Category')
            - Line: fig = px.line(df, x='Date', y='Sales', title='Sales Trend')
            - Scatter: fig = px.scatter(df, x='Price', y='Quantity', title='Price vs Quantity')
            - Pie: fig = px.pie(df, names='Category', values='Sales', title='Sales Distribution')
            - Histogram: fig = px.histogram(df, x='Price', title='Price Distribution')
            """
            return dynamic_visualization.execute_plot_code(self.df, code)
        
        # Pre-built Chart Functions
        def create_bar_chart(x_column: str, y_column: str, title: str = "Bar Chart") -> str:
            """Create a bar chart comparing categories."""
            return dynamic_visualization.create_bar_chart(self.df, x_column, y_column, title)
        
        def create_line_chart(x_column: str, y_column: str, title: str = "Line Chart") -> str:
            """Create a line chart showing trends."""
            return dynamic_visualization.create_line_chart(self.df, x_column, y_column, title)
        
        def create_pie_chart(names_column: str, values_column: str, title: str = "Pie Chart") -> str:
            """Create a pie chart showing distribution."""
            return dynamic_visualization.create_pie_chart(self.df, names_column, values_column, title)
        
        def create_histogram(column: str, title: str = "Histogram") -> str:
            """Create a histogram showing distribution of values."""
            return dynamic_visualization.create_histogram(self.df, column, title)
        
        def create_scatter_plot(x_column: str, y_column: str, title: str = "Scatter Plot") -> str:
            """Create a scatter plot showing correlation between two variables."""
            return dynamic_visualization.create_scatter_chart(self.df, x_column, y_column, title)
        
        tools = [
            data_tool,
            FunctionTool.from_defaults(fn=generate_custom_chart, name="generate_custom_chart"),
            FunctionTool.from_defaults(fn=create_bar_chart, name="create_bar_chart"),
            FunctionTool.from_defaults(fn=create_line_chart, name="create_line_chart"),
            FunctionTool.from_defaults(fn=create_pie_chart, name="create_pie_chart"),
            FunctionTool.from_defaults(fn=create_histogram, name="create_histogram"),
            FunctionTool.from_defaults(fn=create_scatter_plot, name="create_scatter_plot"),
        ]
        
        self.agent = FunctionAgent(
            tools=tools,
            llm=self.llm,
            system_prompt="""You are a DATA ANALYSIS & VISUALIZATION ASSISTANT.
You help users analyze data and create beautiful, informative charts.

=== YOUR BEHAVIOR ===

**ALWAYS ANALYZE AND CREATE** when user has data and asks questions
- Query the data to answer their question
- Provide detailed insights with numbers
- Create relevant charts automatically when visualization helps
- Use appropriate chart types for the data

**CONVERSATION MODE** only for:
- Very vague requests like "help me analyze"
- When you need clarification about what to analyze
- Normal conversation

=== WHEN ANALYZING ===

1. UNDERSTAND THE QUESTION
   - What specific insight does the user want?
   - What data columns are relevant?
   - What type of analysis is needed?

2. PROVIDE COMPREHENSIVE ANSWERS
   - Start with the KEY FINDING in the first sentence
   - Include specific NUMBERS and PERCENTAGES
   - List 3-5 supporting points
   - Highlight TRENDS and PATTERNS
   - Mention any ANOMALIES or interesting observations

3. CREATE VISUALIZATIONS
   - Always create a chart if it helps illustrate the answer
   - BAR: For categorical comparisons (sales by region, counts by category)
   - LINE: For time-series trends (monthly sales, growth over time)
   - PIE: For composition breakdown (market share, percentages)
   - SCATTER: For correlations between two numeric variables
   - HISTOGRAM: For distribution of values

4. CHART QUALITY
   - Use professional color palettes
   - Include descriptive titles
   - Label axes clearly
   - Add hover information

=== RESPONSE FORMAT ===
- Lead with the KEY INSIGHT
- Use bullet points for supporting details
- Include specific numbers (e.g., "Sales increased by 23%")
- When creating charts: "I have generated a [chart type] showing [what it displays]."
- NEVER include file paths
- The UI will automatically display charts
"""
        )
        # Store base system prompt for dynamic augmentation
        self.base_system_prompt = self.agent.system_prompt
    
    async def run(self, query: str) -> str:
        """Execute the data analysis or graph generation task with user query context."""
        # Get data summary to include in prompt
        data_info = {
            "columns": list(self.df.columns),
            "row_count": len(self.df),
            "numeric_cols": list(self.df.select_dtypes(include=['number']).columns),
            "categorical_cols": list(self.df.select_dtypes(include=['object']).columns),
            "sample": self.df.head(3).to_dict()
        }
        
        # Augment system prompt with data context and user request
        context_prompt = f"""
{self.base_system_prompt}

=== DATA IS ALREADY LOADED - ANALYZE NOW ===

The user has uploaded data with:
- Columns: {', '.join(data_info['columns'])}
- Total Rows: {data_info['row_count']}
- Numeric Columns: {', '.join(data_info['numeric_cols']) or 'None'}
- Categorical Columns: {', '.join(data_info['categorical_cols']) or 'None'}
- Sample Data: {data_info['sample']}

IMPORTANT: Data is already loaded! DO NOT ask the user to share data.
You MUST analyze this data and create visualizations immediately.

=== USER'S REQUEST ===
"{query}"

=== YOUR IMMEDIATE ACTIONS ===
1. Use data_analysis_tool to get statistics and insights about the data
2. Create 2-4 visualizations using chart functions (bar, line, pie, histogram, scatter)
3. Provide key findings and insights

DO NOT ask any questions. ANALYZE THE DATA NOW and create charts!
"""
        # Create a new agent instance with augmented prompt for this request
        from llama_index.core.agent import FunctionAgent
        augmented_agent = FunctionAgent(
            tools=self.agent.tools,
            llm=self.llm,
            system_prompt=context_prompt
        )
        response = await augmented_agent.run(user_msg=query)
        return str(response)
