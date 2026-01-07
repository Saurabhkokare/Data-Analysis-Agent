# Multi-Agent System - Specialized Agents
# Each agent is optimized for a specific output type

from .pdf_agent import PDFReportAgent
from .ppt_agent import PPTAgent
from .dashboard_agent import DashboardAgent
from .data_analysis_agent import DataAnalysisGraphAgent

__all__ = [
    'PDFReportAgent',
    'PPTAgent', 
    'DashboardAgent',
    'DataAnalysisGraphAgent'
]
