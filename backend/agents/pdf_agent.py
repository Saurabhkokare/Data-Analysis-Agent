"""
PDF Report Agent - Specialized agent for generating professional PDF reports
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_index.core.tools import FunctionTool, QueryEngineTool, ToolMetadata
from llama_index.experimental.query_engine import PandasQueryEngine
from llama_index.core import Settings
from llama_index.llms.groq import Groq
from llama_index.core.agent import FunctionAgent
import report_generator
import dynamic_visualization
from typing import List
import pandas as pd


class PDFReportAgent:
    """
    Specialized agent for generating professional PDF reports.
    Focuses on structured content, data insights, and visual presentation.
    """
    
    def __init__(self, df: pd.DataFrame, llm: Groq):
        self.df = df
        self.llm = llm
        
        # Data Analysis Tool
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
                description="Query the dataframe for statistics, counts, averages, and insights for the report."
            )
        )
        
        # Visualization Tool for report images
        def generate_report_chart(code: str) -> str:
            """
            Generate a chart for the PDF report using Plotly.
            Code must create a 'fig' variable with a Plotly figure.
            Use: px (plotly.express), go (plotly.graph_objects), df (dataframe)
            Example: fig = px.bar(df, x='Category', y='Value', title='Sales by Category')
            """
            return dynamic_visualization.execute_plot_code(self.df, code)
        
        # PDF Generation Tool
        def generate_pdf_report(summary_text: str, image_filenames: List[str]) -> str:
            """
            Generate a professional PDF report with the provided summary and images.
            
            Args:
                summary_text: Comprehensive report content with sections like:
                    - Executive Summary
                    - Data Overview
                    - Key Findings
                    - Recommendations
                image_filenames: List of image file paths to include in the report
            
            Returns:
                Path to the generated PDF file
            """
            return report_generator.create_pdf_report(summary_text, image_filenames)
        
        tools = [
            data_tool,
            FunctionTool.from_defaults(fn=generate_report_chart, name="generate_report_chart"),
            FunctionTool.from_defaults(fn=generate_pdf_report, name="generate_pdf_report"),
        ]
        
        self.agent = FunctionAgent(
            tools=tools,
            llm=self.llm,
            system_prompt="""You are a PROFESSIONAL PDF REPORT GENERATOR.
You create comprehensive, polished PDF reports from data.

=== YOUR CORE TASK ===
When user has uploaded data and mentions PDF/report:
1. IMMEDIATELY ANALYZE the data - do not ask questions
2. GENERATE charts with descriptive names
3. CREATE the PDF report with all sections
4. Use generate_pdf_report tool

**CONVERSATION MODE** only for vague requests like "help me with a Report Generation"
- Ask what metrics matter most
- Ask about the purpose of the Report generation
- Suggest visualization types
- Normal conversation


=== NEVER ASK QUESTIONS WHEN DATA IS PROVIDED ===
If user has uploaded data (CSV, Excel, etc.), GENERATE the report directly!

=== REPORT GENERATION PROCESS ===

**STEP 1: ANALYZE DATA**
- Identify key columns and metrics
- Calculate statistics (totals, averages, trends)
- Find patterns and insights

**STEP 2: CREATE VISUALIZATIONS** (CRITICAL)
For each chart, use DESCRIPTIVE NAMES:
- BAD: "chart_1.png" 
- GOOD: "sales_by_region_bar_chart.png"
- GOOD: "monthly_revenue_trend_line.png"
- GOOD: "product_category_distribution_pie.png"

Create 3-5 charts covering:
- Distribution/breakdown charts (pie, bar)
- Trend analysis (line charts if time data exists)
- Comparison charts (grouped bar)
- Top/Bottom performers

**STEP 3: WRITE CONTENT**
Before writing, mentally review for:
- Spelling correctness
- Grammar accuracy  
- Professional tone
- Clear and concise language

STRUCTURE:
1. Executive Summary (2-3 paragraphs)
   - Key findings overview
   - Most important insights
   - Include chart: [Overview visualization]

2. Data Overview
   - Dataset description (rows, columns, date range)
   - Key variables analyzed

3. Detailed Analysis
   - For each major finding:
     * Written analysis with numbers
     * Include chart: [Relevant visualization with description]
     * Explain what the chart shows

4. Key Findings (5-8 bullet points)
   - Finding with specific numbers
   - Include supporting chart reference

5. Recommendations
   - Actionable next steps
   - Based on data insights

**STEP 4: INTEGRATE CHARTS**
Each chart must have:
- Descriptive title matching its content
- Brief description explaining insights
- Proper placement in relevant section

=== WRITING QUALITY ===
- Use professional business language
- Include SPECIFIC numbers and percentages
- Check all text for spelling and grammar
- Explain significance of findings
- NO markdown formatting - plain text only

=== CHART NAMING CONVENTION ===
Format: [subject]_[metric]_[chart_type].png
Examples:
- "revenue_by_quarter_line_chart"
- "top_10_products_bar_chart"
- "customer_segment_pie_chart"
- "price_vs_quantity_scatter_plot"

=== RESPONSE FORMAT ===
- Say: "I have generated your PDF report titled '[TITLE]' containing [X sections] and [Y visualizations]."
- List the main findings briefly
- NEVER include file paths
- The UI will automatically show download buttons
"""
        )
        # Store base system prompt for dynamic augmentation
        self.base_system_prompt = self.agent.system_prompt
    
    async def run(self, query: str) -> str:
        """Execute the PDF report generation task with user query context."""
        # Get data summary to include in prompt
        data_info = {
            "columns": list(self.df.columns),
            "row_count": len(self.df),
            "sample": self.df.head(3).to_dict()
        }
        
        # Augment system prompt with data context and user request
        context_prompt = f"""
{self.base_system_prompt}

=== DATA IS ALREADY LOADED - GENERATE REPORT NOW ===

The user has uploaded data with:
- Columns: {', '.join(data_info['columns'])}
- Total Rows: {data_info['row_count']}
- Sample Data: {data_info['sample']}

IMPORTANT: Data is already loaded! DO NOT ask the user to upload data.
You MUST analyze this data and generate the PDF report immediately.

=== USER'S REQUEST ===
"{query}"

=== YOUR IMMEDIATE ACTIONS ===
1. Use data_analysis_tool to get statistics and insights
2. Use generate_report_chart to create 3-5 visualizations with descriptive titles
3. Use generate_pdf_report to create the final PDF with all content and charts

DO NOT ask any questions. GENERATE THE REPORT NOW.
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
