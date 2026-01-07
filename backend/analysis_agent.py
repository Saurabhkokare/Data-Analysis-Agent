"""
Analysis Agent - Orchestrator that routes requests to specialized agents
With conversation history and query caching for consistent responses
"""
import os
import asyncio
import hashlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from llama_index.core import Settings
from llama_index.llms.groq import Groq
import pandas as pd
from typing import Dict, List, Tuple, Optional

# Import router and specialized agents
from agent_router import AgentRouter, AgentType
from agents.pdf_agent import PDFReportAgent
from agents.ppt_agent import PPTAgent
from agents.dashboard_agent import DashboardAgent
from agents.data_analysis_agent import DataAnalysisGraphAgent

# Thread pool for CPU-bound tasks
executor = ThreadPoolExecutor(max_workers=4)


class ConversationHistory:
    """Manages conversation history and query caching for consistent responses."""
    
    def __init__(self, max_history: int = 50):
        self.history: List[Dict] = []  # List of {query, response, timestamp, agent_type}
        self.cache: Dict[str, Dict] = {}  # hash -> {response, timestamp, agent_type}
        self.max_history = max_history
    
    def _hash_query(self, query: str) -> str:
        """Create a normalized hash of the query for caching."""
        # Normalize: lowercase, strip whitespace, remove extra spaces
        normalized = ' '.join(query.lower().strip().split())
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def get_cached_response(self, query: str) -> Optional[Dict]:
        """Check if we have a cached response for this query."""
        query_hash = self._hash_query(query)
        if query_hash in self.cache:
            cached = self.cache[query_hash]
            print(f"DEBUG: Cache HIT for query hash {query_hash[:8]}...")
            return cached
        print(f"DEBUG: Cache MISS for query hash {query_hash[:8]}...")
        return None
    
    def add_to_history(self, query: str, response: str, agent_type: str) -> None:
        """Add a query-response pair to history and cache."""
        timestamp = datetime.now().isoformat()
        
        # Add to history
        entry = {
            "query": query,
            "response": response,
            "timestamp": timestamp,
            "agent_type": agent_type
        }
        self.history.append(entry)
        
        # Trim history if too long
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
        
        # Add to cache
        query_hash = self._hash_query(query)
        self.cache[query_hash] = {
            "response": response,
            "timestamp": timestamp,
            "agent_type": agent_type
        }
        print(f"DEBUG: Added to cache with hash {query_hash[:8]}...")
    
    def get_recent_context(self, n: int = 5) -> str:
        """Get recent conversation context for the agent."""
        if not self.history:
            return ""
        
        recent = self.history[-n:]
        context_parts = []
        for entry in recent:
            context_parts.append(f"User: {entry['query'][:100]}...")
            context_parts.append(f"Assistant: {entry['response'][:200]}...")
        
        return "\n".join(context_parts)
    
    def clear_cache(self) -> None:
        """Clear the query cache (but keep history)."""
        self.cache.clear()
        print("DEBUG: Cache cleared")
    
    def clear_all(self) -> None:
        """Clear both history and cache."""
        self.history.clear()
        self.cache.clear()
        print("DEBUG: History and cache cleared")
    
    def get_stats(self) -> Dict:
        """Get statistics about the history and cache."""
        return {
            "history_count": len(self.history),
            "cache_count": len(self.cache),
            "max_history": self.max_history
        }


class AnalysisAgent:
    """
    Orchestrator Agent that routes user requests to the appropriate specialized agent.
    
    Features:
    - Smart routing based on keywords
    - Conversation history tracking
    - Query caching for repeated questions (same question = same answer)
    - Lazy agent initialization
    
    Available specialized agents:
    - PDF Report Agent: For generating professional PDF reports
    - PPT Agent: For creating PowerPoint presentations
    - Dashboard Agent: For interactive HTML dashboards
    - Data Analysis Agent: For data analysis and graph generation
    """
    
    def __init__(self, df: pd.DataFrame, api_key: str = None):
        self.df = df
        if api_key:
            os.environ["GROQ_API_KEY"] = api_key
        
        # Initialize LLM - using Groq's tool-use optimized model
        print("DEBUG: Initializing Orchestrator Agent and LLM...")
        self.llm = Groq(
            model="openai/gpt-oss-20b",  # Specifically fine-tuned for function calling
            request_timeout=90.0,
            max_retries=5,  # More retries for rate limiting
        )
        Settings.llm = self.llm
        
        # Prefetch data statistics to reduce LLM calls
        self.data_stats = self._precompute_stats()
        
        # Initialize Router
        self.router = AgentRouter()
        
        # Initialize Conversation History and Cache
        self.conversation = ConversationHistory(max_history=50)
        
        # Lazy initialization of specialized agents (created on demand)
        self._agents = {}
        
        print("DEBUG: Orchestrator Agent initialized successfully")
    
    def _precompute_stats(self) -> Dict:
        """Precompute common statistics to speed up analysis."""
        stats = {
            "shape": self.df.shape,
            "columns": list(self.df.columns),
            "dtypes": {col: str(self.df[col].dtype) for col in self.df.columns},
            "numeric_cols": list(self.df.select_dtypes(include=['number']).columns),
            "categorical_cols": list(self.df.select_dtypes(include=['object']).columns),
            "null_counts": self.df.isnull().sum().to_dict(),
        }
        
        # Add basic stats for numeric columns
        numeric_df = self.df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            stats["numeric_summary"] = numeric_df.describe().to_dict()
        
        # Add value counts for categorical columns (top 5)
        for col in stats["categorical_cols"][:5]:  # Limit to first 5
            stats[f"{col}_top5"] = self.df[col].value_counts().head(5).to_dict()
        
        print(f"DEBUG: Precomputed stats for {len(stats['columns'])} columns")
        return stats
    
    def _get_agent(self, agent_type: AgentType):
        """
        Get or create a specialized agent instance.
        Uses lazy initialization to save resources.
        """
        if agent_type not in self._agents:
            print(f"DEBUG: Creating specialized agent: {agent_type.value}")
            
            if agent_type == AgentType.PDF:
                self._agents[agent_type] = PDFReportAgent(self.df, self.llm)
            elif agent_type == AgentType.PPT:
                self._agents[agent_type] = PPTAgent(self.df, self.llm)
            elif agent_type == AgentType.DASHBOARD:
                self._agents[agent_type] = DashboardAgent(self.df, self.llm)
            elif agent_type == AgentType.DATA_ANALYSIS:
                self._agents[agent_type] = DataAnalysisGraphAgent(self.df, self.llm)
            else:
                # Fallback to data analysis agent
                self._agents[agent_type] = DataAnalysisGraphAgent(self.df, self.llm)
        
        return self._agents[agent_type]
    
    async def analyze(self, query: str, use_cache: bool = True, agent_type: str = None) -> str:
        """
        Main entry point - routes the query to the appropriate specialized agent.
        
        Args:
            query: User's question or command
            use_cache: If True, return cached response for repeated queries
            agent_type: Optional - force a specific agent (pdf, ppt, dashboard, data_analysis)
            
        Returns:
            Response from the specialized agent (or cache)
        """
        # Step 1: Check cache for repeated questions (only if no forced agent)
        if use_cache and not agent_type:
            cached = self.conversation.get_cached_response(query)
            if cached:
                print(f"DEBUG: Returning cached response (agent: {cached['agent_type']})")
                return cached["response"]
        
        # Step 2: Determine which agent should handle this request
        if agent_type and agent_type != 'auto':
            # User forced a specific agent
            agent_type_map = {
                'pdf': AgentType.PDF,
                'ppt': AgentType.PPT,
                'dashboard': AgentType.DASHBOARD,
                'data_analysis': AgentType.DATA_ANALYSIS,
                'analysis': AgentType.DATA_ANALYSIS,
            }
            selected_agent_type = agent_type_map.get(agent_type.lower(), AgentType.DATA_ANALYSIS)
            print(f"DEBUG: User forced agent type: {agent_type} -> {selected_agent_type.value}")
        else:
            # Auto-detect based on keywords
            selected_agent_type = self.router.route(query)
        
        agent_name = self.router.get_agent_name(selected_agent_type)
        
        print(f"DEBUG: Routing to {agent_name}")
        if not agent_type:
            print(f"DEBUG: {self.router.explain_routing(query)}")
        
        # Step 3: Get the appropriate specialized agent
        agent = self._get_agent(selected_agent_type)
        
        # Step 4: Run the query through the specialized agent
        try:
            response = await agent.run(query)
            response_str = str(response)
            
            # Step 5: Store in history and cache
            self.conversation.add_to_history(query, response_str, selected_agent_type.value)
            
            return response_str
        except Exception as e:
            import traceback
            error_msg = f"Error in {agent_name}: {str(e)}"
            print(f"DEBUG: {error_msg}")
            traceback.print_exc()
            
            # Fallback: try data analysis agent if another agent fails
            if selected_agent_type != AgentType.DATA_ANALYSIS:
                print("DEBUG: Falling back to Data Analysis Agent")
                fallback_agent = self._get_agent(AgentType.DATA_ANALYSIS)
                response = await fallback_agent.run(query)
                response_str = str(response)
                self.conversation.add_to_history(query, response_str, "data_analysis_fallback")
                return response_str
            
            raise
    
    def get_conversation_history(self) -> List[Dict]:
        """Get the full conversation history."""
        return self.conversation.history
    
    def clear_history(self) -> None:
        """Clear conversation history and cache."""
        self.conversation.clear_all()
    
    def get_agent_info(self) -> dict:
        """
        Get information about available agents and current state.
        Useful for debugging and monitoring.
        """
        return {
            "orchestrator": "AnalysisAgent",
            "conversation_stats": self.conversation.get_stats(),
            "available_agents": [
                {
                    "type": AgentType.PDF.value,
                    "name": "PDF Report Agent",
                    "keywords": ["pdf", "report", "document"],
                    "initialized": AgentType.PDF in self._agents
                },
                {
                    "type": AgentType.PPT.value,
                    "name": "PPT Agent",
                    "keywords": ["ppt", "powerpoint", "presentation"],
                    "initialized": AgentType.PPT in self._agents
                },
                {
                    "type": AgentType.DASHBOARD.value,
                    "name": "Dashboard Agent",
                    "keywords": ["dashboard", "interactive"],
                    "initialized": AgentType.DASHBOARD in self._agents
                },
                {
                    "type": AgentType.DATA_ANALYSIS.value,
                    "name": "Data Analysis Agent",
                    "keywords": ["graph", "chart", "analyze"],
                    "initialized": AgentType.DATA_ANALYSIS in self._agents
                }
            ],
            "data_shape": {
                "rows": len(self.df),
                "columns": len(self.df.columns),
                "column_names": list(self.df.columns)
            }
        }
