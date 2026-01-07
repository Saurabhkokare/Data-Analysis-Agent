"""
Dashboard Agent - Specialized agent for generating interactive HTML dashboards
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_index.core.tools import FunctionTool, QueryEngineTool, ToolMetadata
from llama_index.experimental.query_engine import PandasQueryEngine
from llama_index.llms.groq import Groq
from llama_index.core.agent import FunctionAgent
import dashboard_generator
import pandas as pd


class DashboardAgent:
    """
    Specialized agent for generating interactive HTML dashboards.
    Creates Power BI/Tableau-like interactive visualizations.
    """
    
    def __init__(self, df: pd.DataFrame, llm: Groq):
        self.df = df
        self.llm = llm
        
        # Data Analysis Tool for understanding the data
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
                description="Query the dataframe to understand data structure and key metrics for the dashboard."
            )
        )
        
        # Dashboard Generation Tool
        def create_interactive_dashboard(title: str = "Data Analysis Dashboard") -> str:
            """
            Generate an interactive HTML dashboard with automatic chart selection.
            
            The dashboard automatically includes:
            - KPI cards at the top (key metrics)
            - Multiple chart types based on data (bar, line, pie, histogram)
            - Data preview table
            - Interactive Plotly.js visualizations
            
            Args:
                title: Title for the dashboard header
            
            Returns:
                Path to the generated HTML dashboard file
            """
            return dashboard_generator.create_dashboard_from_data(self.df, title)
        
        # Custom Dashboard with specific config
        def create_custom_dashboard(title: str, chart_types: str) -> str:
            """
            Generate a dashboard with specific chart type preferences.
            
            Args:
                title: Dashboard title
                chart_types: Comma-separated chart preferences (bar, line, pie, histogram, scatter)
            
            Returns:
                Path to the generated HTML dashboard file
            """
            config = f'{{"title": "{title}", "preferred_charts": "{chart_types}"}}'
            return dashboard_generator.create_dashboard_from_data(self.df, config)
        
        tools = [
            data_tool,
            FunctionTool.from_defaults(fn=create_interactive_dashboard, name="create_interactive_dashboard"),
            FunctionTool.from_defaults(fn=create_custom_dashboard, name="create_custom_dashboard"),
        ]
        
        self.agent = FunctionAgent(
            tools=tools,
            llm=self.llm,
            system_prompt="""You are an INTERACTIVE DASHBOARD ASSISTANT.
You help users create beautiful, interactive HTML dashboards like Power BI or Tableau.

=== YOUR BEHAVIOR ===

**ALWAYS GENERATE DASHBOARD** when user has data loaded and mentions dashboard/visualization
- Analyze the data to identify key metrics
- Create comprehensive dashboard with KPIs and charts
- Use generate_dashboard tool with proper title

**CONVERSATION MODE** only for vague requests like "help me with a dashboard"
- Ask what metrics matter most
- Ask about the purpose of the dashboard
- Suggest visualization types
- Normal conversation

=== WHEN GENERATING ===

1. DASHBOARD TITLE (CRITICAL)
   - If user mentions "about [topic]" → use [topic] as title
   - If analyzing data → use "[Data Topic] Dashboard"
   - NEVER leave title empty - create meaningful one

2. KPI SECTION (Top of Dashboard)
   - 3-5 Key Performance Indicators
   - Totals, averages, counts of important metrics
   - Highlight critical numbers prominently

3. CHART VARIETY (Minimum 4 Charts)
   - BAR CHART: For categorical comparisons
   - LINE CHART: For trends over time
   - PIE CHART: For composition/distribution
   - HISTOGRAM: For numerical distribution
   - Additional charts based on data type

4. DATA TABLE
   - Preview of underlying data
   - First 10-20 rows shown

5. INTERACTIVITY
   - Hover tooltips on all charts
   - Zoom and pan capabilities
   - Responsive layout

=== RESPONSE FORMAT ===
- Say: "I have created your interactive dashboard titled '[TITLE]' with [X KPIs] and [Y charts]."
- NEVER include file paths
- The UI will automatically show a Dashboard button
"""
        )
        # Store base system prompt for dynamic augmentation
        self.base_system_prompt = self.agent.system_prompt
    
    async def run(self, query: str) -> str:
        """Execute the dashboard generation task with user query context."""
        # Get data summary to include in prompt
        data_info = {
            "columns": list(self.df.columns),
            "row_count": len(self.df),
            "numeric_cols": list(self.df.select_dtypes(include=['number']).columns),
            "categorical_cols": list(self.df.select_dtypes(include=['object']).columns),
        }
        
        # Augment system prompt with data context and user request
        context_prompt = f"""
{self.base_system_prompt}

=== DATA IS ALREADY LOADED - GENERATE DASHBOARD NOW ===

The user has uploaded data with:
- Columns: {', '.join(data_info['columns'])}
- Total Rows: {data_info['row_count']}
- Numeric Columns (for KPIs/charts): {', '.join(data_info['numeric_cols']) or 'None'}
- Categorical Columns (for groups): {', '.join(data_info['categorical_cols']) or 'None'}

IMPORTANT: Data is already loaded! DO NOT ask the user to upload data.
You MUST analyze this data and generate the dashboard immediately.

=== USER'S REQUEST ===
"{query}"

=== YOUR IMMEDIATE ACTIONS ===
1. Use generate_dashboard tool to create the interactive dashboard
2. Include 3-5 KPIs from numeric columns
3. Create 4+ charts (bar, line, pie, histogram)
4. Add data table preview

DO NOT ask any questions. GENERATE THE DASHBOARD NOW.
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
