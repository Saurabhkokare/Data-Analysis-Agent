"""
PPT Agent - Specialized agent for generating PowerPoint presentations
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from llama_index.core.tools import FunctionTool, QueryEngineTool, ToolMetadata
from llama_index.experimental.query_engine import PandasQueryEngine
from llama_index.llms.groq import Groq
from llama_index.core.agent import FunctionAgent
import report_generator
import dynamic_visualization
from typing import List
import pandas as pd


class PPTAgent:
    """
    Specialized agent for generating PowerPoint presentations.
    Focuses on visual storytelling, slide design, and presentation flow.
    """
    
    def __init__(self, df: pd.DataFrame, llm: Groq):
        self.df = df
        self.llm = llm
        
        # Data Analysis Tool (optional for data-driven PPTs)
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
                description="Query the dataframe for statistics and insights to include in presentation slides."
            )
        )
        
        # Chart Generation for slides
        def generate_slide_chart(code: str) -> str:
            """
            Generate a chart for presentation slides using Plotly.
            Code must create a 'fig' variable with a Plotly figure.
            Use: px (plotly.express), go (plotly.graph_objects), df (dataframe)
            Example: fig = px.pie(df, names='Category', values='Sales', title='Sales Distribution')
            """
            return dynamic_visualization.execute_plot_code(self.df, code)
        
        # Data-driven PPT Generation
        def generate_data_ppt(summary_text: str, image_filenames: List[str]) -> str:
            """
            Generate a PowerPoint presentation from data analysis with charts.
            
            Args:
                summary_text: Content for slides organized as clear sections
                image_filenames: List of chart/image paths to include
            
            Returns:
                Path to the generated PPTX file
            """
            return report_generator.create_ppt_report(summary_text, image_filenames)
        
        # Text-based PPT Generation (no data required)
        def generate_text_ppt(content: str, title: str = "Presentation") -> str:
            """
            Generate a PowerPoint presentation from TEXT CONTENT only.
            Use when user provides text/content directly and wants slides created.
            
            Args:
                content: The text content - each major point becomes a slide
                title: Title for the presentation
            
            Returns:
                Path to the generated PPTX file
            """
            return report_generator.create_ppt_report(content, [], None, title)
        
        tools = [
            data_tool,
            FunctionTool.from_defaults(fn=generate_slide_chart, name="generate_slide_chart"),
            FunctionTool.from_defaults(fn=generate_data_ppt, name="generate_data_ppt"),
            FunctionTool.from_defaults(fn=generate_text_ppt, name="generate_text_ppt"),
        ]
        
        self.agent = FunctionAgent(
            tools=tools,
            llm=self.llm,
            system_prompt="""You are an EXPERT POWERPOINT PRESENTATION DESIGNER.
You create professional, visually stunning presentations from ANY content - paragraphs, bullet points, or topics.

=== YOUR CORE TASK ===
When user provides content (paragraph, text, or points) and mentions PPT/presentation/slides:
1. ANALYZE the entire content thoroughly
2. EXTRACT logical sections and key information
3. GENERATE a professional PPT using generate_text_ppt tool

**CONVERSATION MODE** only for vague requests like "help me with a powerpoint presentation"
- Ask what metrics matter most
- Ask about the purpose of the powerpoint presentation
- Suggest visualization types
- Normal conversation


=== PARAGRAPH PARSING (CRITICAL) ===

When user provides a PARAGRAPH, you must:

**STEP 1: READ THE ENTIRE CONTENT**
- Understand the main topic and purpose
- Identify the overall theme for the presentation title

**STEP 2: IDENTIFY SLIDE HEADERS**
Look for these patterns to create slide titles:
- Topic sentences (first sentence of each paragraph)
- Key concepts and main ideas
- Natural topic transitions (when subject changes)
- Questions being answered
- Subheadings or emphasized phrases
- Numbered or bulleted sections

**STEP 3: EXTRACT IMPORTANT CONTENT FOR EACH SLIDE**
For each identified section:
- Pull out 8-12 key points as bullet points
- Keep each bullet point concise (max 2 lines)
- Include statistics, facts, examples
- Preserve important details and explanations
- Convert complex sentences into simple bullets

**STEP 4: STRUCTURE THE PRESENTATION**
Create this format for generate_text_ppt:

```
1. Introduction
- Overview of [main topic]
- Why this matters
- Key objectives

2. [First Major Concept]
- Point extracted from paragraph
- Supporting detail
- Example or statistic

3. [Second Major Concept]
- Point extracted from paragraph
- Key information
- Important detail

... (continue for all sections)

N. Conclusion
- Summary of key points
- Main takeaways
- Call to action
```

=== SLIDE REQUIREMENTS ===
- MINIMUM 7 slides, MAXIMUM 15 slides
- Each slide has a UNIQUE, descriptive title
- 8-12 bullet points per content slide
- Title slide + content slides + conclusion slide

=== TITLE EXTRACTION ===
- Look for "about [topic]" → use [topic]
- First sentence often reveals the main topic
- Create meaningful title that captures the essence
- NEVER leave title empty

=== EXAMPLE ===

If user provides:
"Machine learning is a subset of AI that enables computers to learn from data. There are three types: supervised learning uses labeled data, unsupervised learning finds patterns, and reinforcement learning learns from feedback. Applications include healthcare diagnostics, financial fraud detection, and autonomous vehicles."

You should create:
Title: "Machine Learning Overview"
Slides:
1. Introduction to Machine Learning
2. What is Machine Learning?
3. Types of Machine Learning
4. Supervised Learning
5. Unsupervised Learning
6. Reinforcement Learning
7. Applications of ML
8. Healthcare Applications
9. Finance Applications
10. Conclusion

=== RESPONSE FORMAT ===
- Say: "I have created your PowerPoint presentation titled '[TITLE]' with X slides covering: [list main topics]."
- NEVER include file paths
- The UI will automatically show a PPT download button
"""
        )
        # Store base system prompt for dynamic augmentation
        self.base_system_prompt = self.agent.system_prompt
    
    async def run(self, query: str) -> str:
        """Execute the PPT generation task with user query context."""
        # Get data summary to include in prompt
        data_info = {
            "columns": list(self.df.columns),
            "row_count": len(self.df),
        }
        
        # Check if we have real data or empty placeholder
        has_real_data = len(self.df) > 1 or 'info' not in self.df.columns
        
        # Augment system prompt with data context and user request
        if has_real_data:
            data_context = f"""
=== DATA IS ALREADY LOADED ===
The user has uploaded data with:
- Columns: {', '.join(data_info['columns'])}
- Total Rows: {data_info['row_count']}

You can use this data to create data-driven presentations if relevant.
"""
        else:
            data_context = """
=== WORKING WITH TEXT CONTENT ===
No data file uploaded. Create the presentation from the text content provided.
"""
        
        context_prompt = f"""
{self.base_system_prompt}

{data_context}

=== USER'S REQUEST ===
"{query}"

=== REQUIRED ACTION ===
Analyze the user's content and IMMEDIATELY create the PowerPoint presentation.
Use generate_text_ppt(content, title) with properly formatted content.
DO NOT ask questions - generate the PPT now.
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
