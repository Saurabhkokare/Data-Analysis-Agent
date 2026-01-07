import os
import shutil
import uvicorn
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import re

# Import existing modules
import data_loader
from analysis_agent import AnalysisAgent
from dotenv import load_dotenv

load_dotenv()

# Thread pool for CPU-bound tasks (visualizations, PDF/PPT generation)
executor = ThreadPoolExecutor(max_workers=4)

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variable to store the active agent
active_agent: Optional[AnalysisAgent] = None

class AnalyzeRequest(BaseModel):
    prompt: str
    agent_type: Optional[str] = None  # pdf, ppt, dashboard, data_analysis, or auto

@app.post("/analyze")
async def analyze(
    file: Optional[UploadFile] = File(None),
    prompt: str = Form(...),
    agent_type: Optional[str] = Form(None)  # Optional: force specific agent
):
    global active_agent
    
    # 1. Handle File Upload
    if file and file.filename:
        try:
            # Save file temporarily
            file_location = f"temp_{file.filename}"
            with open(file_location, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Load data
            df = data_loader.load_data(file_location)
            
            if df is None:
                raise HTTPException(status_code=400, detail="Failed to load data from file.")
            
            # Initialize Agent
            # Get API Key from env
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                 raise HTTPException(status_code=500, detail="GROQ_API_KEY not found in environment variables.")

            active_agent = AnalysisAgent(df, api_key=api_key)
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")

    # 2. Check if agent is initialized
    if active_agent is None:
        # Determine if this is a request that can work without data
        ppt_keywords = ['ppt', 'presentation', 'powerpoint', 'slides', 'create ppt', 'make ppt', 'generate ppt']
        pdf_keywords = ['pdf', 'report', 'document']
        is_ppt_request = any(kw in prompt.lower() for kw in ppt_keywords) or agent_type == 'ppt'
        is_pdf_request = any(kw in prompt.lower() for kw in pdf_keywords) or agent_type == 'pdf'
        
        # For PPT/PDF requests with text content, create agent with empty dataframe to enable agent conversation
        if is_ppt_request or (is_pdf_request and len(prompt) > 100):
            import pandas as pd
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise HTTPException(status_code=500, detail="GROQ_API_KEY not found in environment variables.")
            
            # Create agent with empty dataframe to enable conversation
            # The agent will still work for text-based content
            empty_df = pd.DataFrame({'info': ['No data file uploaded. Working with text content.']})
            active_agent = AnalysisAgent(empty_df, api_key=api_key)
            
            # Mark that we're working without real data
            print("DEBUG: Created agent without data file for text-based request")
        else:
            # Return a helpful conversational response
            helpful_message = """Hello! I'm your Data Analysis Assistant. 

To get started, please **upload a data file** (CSV, Excel, JSON, or TXT) using the upload button.

Once you upload a file, I can help you with:
• **Data Analysis** - Insights, statistics, and patterns
• **Visualizations** - Charts and graphs
• **PDF Reports** - Comprehensive analysis reports  
• **PowerPoint Presentations** - Slide decks from your data
• **Interactive Dashboards** - Power BI-style dashboards

**Tip:** You can also create a PPT from text by selecting "📑 PowerPoint" from the dropdown and providing your content!"""
            
            return {
                "response": helpful_message,
                "images": [],
                "image_paths": [],
                "pdf_path": None,
                "ppt_path": None,
                "dashboard_path": None
            }

    # 3. Run Analysis with optional forced agent type
    try:
        # Pass agent_type for forced routing (if user selected specific agent)
        response_text = await active_agent.analyze(prompt, agent_type=agent_type)
        
        # 4. Extract Artifacts (Images/PDFs) from response text using parallel processing
        loop = asyncio.get_event_loop()
        
        def extract_paths(response: str):
            """Extract file paths from response text or check outputs folder - runs in thread pool"""
            import glob
            import time
            
            result = {
                "images": [],  # Changed to include descriptions
                "image_paths": [],  # Keep for backward compatibility
                "pdf_path": None,
                "ppt_path": None,
                "dashboard_path": None
            }
            
            outputs_dir = os.path.join(os.path.dirname(__file__), "outputs")
            current_time = time.time()
            
            # Find all pngs with context for descriptions
            # Match paths like: D:\path\to\file.png or /path/to/file.png
            png_matches = re.findall(r'[A-Za-z]:[\\\/][^\s]+\.png|\/[^\s]+\.png', response)
            for i, match in enumerate(png_matches):
                if os.path.exists(match):
                    filename = os.path.basename(match)
                    url = f"http://localhost:8000/download/{filename}"
                    result["image_paths"].append(url)
                    
                    # Generate description from filename
                    chart_type = "Chart"
                    if "bar" in filename.lower():
                        chart_type = "Bar Chart"
                    elif "line" in filename.lower():
                        chart_type = "Line Chart"
                    elif "pie" in filename.lower():
                        chart_type = "Pie Chart"
                    elif "hist" in filename.lower():
                        chart_type = "Histogram"
                    elif "scatter" in filename.lower():
                        chart_type = "Scatter Plot"
                    elif "plot" in filename.lower():
                        chart_type = "Visualization"
                    
                    result["images"].append({
                        "url": url,
                        "title": f"{chart_type} {i+1}",
                        "description": f"Generated {chart_type.lower()} based on data analysis"
                    })
            
            # Find pdf - first check response, then check outputs folder
            pdf_matches = re.findall(r'[A-Za-z]:[\\\/][^\s]+\.pdf|\/[^\s]+\.pdf', response)
            if pdf_matches:
                last_pdf = pdf_matches[-1]
                if os.path.exists(last_pdf):
                    filename = os.path.basename(last_pdf)
                    result["pdf_path"] = f"http://localhost:8000/download/{filename}"
            
            # If not found in response, check outputs/pdfs folder for recent files
            if not result["pdf_path"]:
                pdf_folder = os.path.join(outputs_dir, "pdfs")
                if os.path.exists(pdf_folder):
                    pdf_files = glob.glob(os.path.join(pdf_folder, "*.pdf"))
                    # Get files modified in last 60 seconds
                    recent_pdfs = [f for f in pdf_files if current_time - os.path.getmtime(f) < 60]
                    if recent_pdfs:
                        latest_pdf = max(recent_pdfs, key=os.path.getmtime)
                        filename = os.path.basename(latest_pdf)
                        result["pdf_path"] = f"http://localhost:8000/download/{filename}"
            
            # Find pptx - first check response, then check outputs folder
            pptx_matches = re.findall(r'[A-Za-z]:[\\\/][^\s]+\.pptx|\/[^\s]+\.pptx', response)
            if pptx_matches:
                last_pptx = pptx_matches[-1]
                if os.path.exists(last_pptx):
                    filename = os.path.basename(last_pptx)
                    result["ppt_path"] = f"http://localhost:8000/download/{filename}"
            
            # If not found in response, check outputs/ppts folder for recent files
            if not result["ppt_path"]:
                ppt_folder = os.path.join(outputs_dir, "ppts")
                if os.path.exists(ppt_folder):
                    ppt_files = glob.glob(os.path.join(ppt_folder, "*.pptx"))
                    # Get files modified in last 60 seconds
                    recent_ppts = [f for f in ppt_files if current_time - os.path.getmtime(f) < 60]
                    if recent_ppts:
                        latest_ppt = max(recent_ppts, key=os.path.getmtime)
                        filename = os.path.basename(latest_ppt)
                        result["ppt_path"] = f"http://localhost:8000/download/{filename}"
            
            # Find html dashboards - first check response, then outputs folder
            html_matches = re.findall(r'[A-Za-z]:[\\\/][^\s]*dashboard[^\s]*\.html|\/[^\s]*dashboard[^\s]*\.html', response)
            if html_matches:
                last_html = html_matches[-1]
                if os.path.exists(last_html):
                    filename = os.path.basename(last_html)
                    result["dashboard_path"] = f"http://localhost:8000/download/{filename}"
            
            # If not found in response, check outputs/dashboards folder for recent files
            if not result["dashboard_path"]:
                dashboard_folder = os.path.join(outputs_dir, "dashboards")
                if os.path.exists(dashboard_folder):
                    html_files = glob.glob(os.path.join(dashboard_folder, "*.html"))
                    # Get files modified in last 60 seconds
                    recent_htmls = [f for f in html_files if current_time - os.path.getmtime(f) < 60]
                    if recent_htmls:
                        latest_html = max(recent_htmls, key=os.path.getmtime)
                        filename = os.path.basename(latest_html)
                        result["dashboard_path"] = f"http://localhost:8000/download/{filename}"
            
            # Also check outputs/graphs for recent images
            if not result["image_paths"]:
                graphs_folder = os.path.join(outputs_dir, "graphs")
                if os.path.exists(graphs_folder):
                    graph_files = glob.glob(os.path.join(graphs_folder, "*.png"))
                    recent_graphs = [f for f in graph_files if current_time - os.path.getmtime(f) < 60]
                    for i, graph_path in enumerate(sorted(recent_graphs, key=os.path.getmtime, reverse=True)[:5]):
                        filename = os.path.basename(graph_path)
                        url = f"http://localhost:8000/download/{filename}"
                        result["image_paths"].append(url)
                        
                        chart_type = "Chart"
                        if "bar" in filename.lower():
                            chart_type = "Bar Chart"
                        elif "line" in filename.lower():
                            chart_type = "Line Chart"
                        elif "pie" in filename.lower():
                            chart_type = "Pie Chart"
                        elif "hist" in filename.lower():
                            chart_type = "Histogram"
                        
                        result["images"].append({
                            "url": url,
                            "title": f"{chart_type} {i+1}",
                            "description": f"Generated visualization"
                        })
            
            return result
        
        # Run path extraction in thread pool for non-blocking I/O
        extracted = await loop.run_in_executor(executor, extract_paths, response_text)

        return {
            "response": response_text,
            "images": extracted["images"],  # New: array with title/description
            "image_paths": extracted["image_paths"],  # Keep for backward compatibility
            "pdf_path": extracted["pdf_path"],
            "ppt_path": extracted["ppt_path"],
            "dashboard_path": extracted["dashboard_path"]
        }

    except Exception as e:
        import traceback
        error_msg = f"Analysis failed: {str(e)}"
        print(error_msg)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/download/{filename}")
async def download_file(filename: str):
    # Check in all output directories
    output_dirs = [
        os.path.join(os.getcwd(), "outputs", "graphs"),
        os.path.join(os.getcwd(), "outputs", "pdfs"),
        os.path.join(os.getcwd(), "outputs", "ppts"),
        os.path.join(os.getcwd(), "outputs", "dashboards"),
        os.getcwd()  # Fallback to root
    ]
    
    for output_dir in output_dirs:
        file_path = os.path.join(output_dir, filename)
        if os.path.exists(file_path):
            return FileResponse(file_path)
    
    raise HTTPException(status_code=404, detail="File not found")


@app.get("/history")
async def get_history():
    """Get conversation history and cache statistics."""
    global active_agent
    
    if active_agent is None:
        return {
            "history": [],
            "stats": {"history_count": 0, "cache_count": 0}
        }
    
    return {
        "history": active_agent.get_conversation_history(),
        "stats": active_agent.conversation.get_stats()
    }


@app.delete("/history")
async def clear_history():
    """Clear conversation history and cache."""
    global active_agent
    
    if active_agent is not None:
        active_agent.clear_history()
        return {"message": "History and cache cleared successfully"}
    
    return {"message": "No active session to clear"}


@app.get("/agent-info")
async def get_agent_info():
    """Get information about available agents."""
    global active_agent
    
    if active_agent is None:
        return {"error": "No active agent. Upload a file first."}
    
    return active_agent.get_agent_info()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
