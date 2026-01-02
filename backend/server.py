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

@app.post("/analyze")
async def analyze(
    file: Optional[UploadFile] = File(None),
    prompt: str = Form(...)
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

    # 2. Check if agent is initialized - if not and user provides text content for PPT, handle it
    if active_agent is None:
        # Check if user wants to create PPT from text content (no file needed)
        ppt_keywords = ['ppt', 'presentation', 'powerpoint', 'slides']
        is_ppt_request = any(kw in prompt.lower() for kw in ppt_keywords)
        
        if is_ppt_request and len(prompt) > 100:  # Has content to make PPT from
            # Create PPT directly from text without needing data
            import report_generator
            try:
                # Extract title and content from prompt
                lines = prompt.strip().split('\n')
                title = "Presentation"
                content = prompt
                
                # Try to find title in prompt
                for kw in ['title:', 'about:', 'on:']:
                    for line in lines:
                        if kw in line.lower():
                            title = line.split(kw, 1)[-1].strip()[:60]
                            break
                
                ppt_path = report_generator.create_ppt_report(content, [], None, title)
                filename = os.path.basename(ppt_path)
                
                return {
                    "response": f"I have created a PowerPoint presentation titled '{title}' for you.",
                    "image_paths": [],
                    "pdf_path": None,
                    "ppt_path": f"http://localhost:8000/download/{filename}",
                    "dashboard_path": None
                }
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error creating PPT: {str(e)}")
        else:
            raise HTTPException(status_code=400, detail="No data loaded. Please upload a file first, or provide text content to create a PPT.")

    # 3. Run Analysis
    try:
        response_text = await active_agent.analyze(prompt)
        
        # 4. Extract Artifacts (Images/PDFs) from response text using parallel processing
        loop = asyncio.get_event_loop()
        
        def extract_paths(response: str):
            """Extract file paths from response text - runs in thread pool"""
            result = {
                "image_paths": [],
                "pdf_path": None,
                "ppt_path": None,
                "dashboard_path": None
            }
            
            # Find all pngs
            png_matches = re.findall(r'(?:[\w:\\/.-]+\.png)', response)
            for match in png_matches:
                if os.path.exists(match):
                    filename = os.path.basename(match)
                    result["image_paths"].append(f"http://localhost:8000/download/{filename}")
            
            # Find pdf
            pdf_matches = re.findall(r'(?:[\w:\\/.-]+\.pdf)', response)
            if pdf_matches:
                last_pdf = pdf_matches[-1]
                if os.path.exists(last_pdf):
                    filename = os.path.basename(last_pdf)
                    result["pdf_path"] = f"http://localhost:8000/download/{filename}"
            
            # Find pptx
            pptx_matches = re.findall(r'(?:[\w:\\/.-]+\.pptx)', response)
            if pptx_matches:
                last_pptx = pptx_matches[-1]
                if os.path.exists(last_pptx):
                    filename = os.path.basename(last_pptx)
                    result["ppt_path"] = f"http://localhost:8000/download/{filename}"
            
            # Find html dashboards
            html_matches = re.findall(r'(?:[\w:\\/.-]+dashboard[\w:\\/.-]*\.html)', response)
            if html_matches:
                last_html = html_matches[-1]
                if os.path.exists(last_html):
                    filename = os.path.basename(last_html)
                    result["dashboard_path"] = f"http://localhost:8000/download/{filename}"
            
            return result
        
        # Run path extraction in thread pool for non-blocking I/O
        extracted = await loop.run_in_executor(executor, extract_paths, response_text)

        return {
            "response": response_text,
            "image_paths": extracted["image_paths"],
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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
