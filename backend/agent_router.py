"""
Agent Router - Smart routing logic to select the appropriate specialized agent
based on user input keywords
"""
import re
from enum import Enum
from typing import Tuple


class AgentType(Enum):
    """Enumeration of available specialized agents"""
    PDF = "pdf"
    PPT = "ppt"
    DASHBOARD = "dashboard"
    DATA_ANALYSIS = "data_analysis"


# Keyword mappings for each agent type
AGENT_KEYWORDS = {
    AgentType.PPT: [
        'ppt', 'powerpoint', 'presentation', 'slides', 'slide deck',
        'create slides', 'make slides', 'generate ppt', 'pptx'
    ],
    AgentType.PDF: [
        'pdf', 'report', 'document', 'pdf report', 'generate report',
        'create report', 'written report', 'formal report'
    ],
    AgentType.DASHBOARD: [
        'dashboard', 'interactive', 'power bi', 'tableau', 
        'interactive view', 'visual summary', 'kpi', 'metrics dashboard'
    ],
    AgentType.DATA_ANALYSIS: [
        'graph', 'chart', 'plot', 'visualiz', 'analyze', 'analysis',
        'bar chart', 'line chart', 'pie chart', 'histogram', 'scatter',
        'statistics', 'insight', 'trend', 'correlation', 'compare'
    ]
}


class AgentRouter:
    """
    Routes user requests to the appropriate specialized agent based on
    keyword detection in the user's input.
    """
    
    def __init__(self):
        self.agent_keywords = AGENT_KEYWORDS
    
    def detect_agent_type(self, user_input: str) -> Tuple[AgentType, float]:
        """
        Analyze user input and determine which agent should handle the request.
        
        Args:
            user_input: The user's query or command
            
        Returns:
            Tuple of (AgentType, confidence_score)
            confidence_score is 0.0 to 1.0 indicating match strength
        """
        user_input_lower = user_input.lower()
        
        # Count keyword matches for each agent type
        scores = {}
        
        for agent_type, keywords in self.agent_keywords.items():
            match_count = 0
            for keyword in keywords:
                # Check for exact word boundaries for short keywords
                if len(keyword) <= 4:
                    pattern = r'\b' + re.escape(keyword) + r'\b'
                    if re.search(pattern, user_input_lower):
                        match_count += 1
                else:
                    # For longer keywords, partial match is okay
                    if keyword in user_input_lower:
                        match_count += 1
            
            # Normalize score by number of keywords
            scores[agent_type] = match_count / len(keywords) if keywords else 0
        
        # Find the best matching agent
        best_agent = max(scores, key=scores.get)
        best_score = scores[best_agent]
        
        # If no strong match, default to Data Analysis agent
        if best_score < 0.05:
            return AgentType.DATA_ANALYSIS, 0.5
        
        return best_agent, min(1.0, best_score * 5)  # Scale up the score
    
    def route(self, user_input: str) -> AgentType:
        """
        Simple routing - returns just the agent type.
        
        Args:
            user_input: The user's query
            
        Returns:
            AgentType enum value
        """
        agent_type, _ = self.detect_agent_type(user_input)
        return agent_type
    
    def get_agent_name(self, agent_type: AgentType) -> str:
        """Get human-readable name for the agent type."""
        names = {
            AgentType.PDF: "PDF Report Agent",
            AgentType.PPT: "PowerPoint Presentation Agent",
            AgentType.DASHBOARD: "Interactive Dashboard Agent",
            AgentType.DATA_ANALYSIS: "Data Analysis & Visualization Agent"
        }
        return names.get(agent_type, "Unknown Agent")
    
    def explain_routing(self, user_input: str) -> str:
        """
        Explain why a particular agent was selected.
        Useful for debugging and transparency.
        """
        user_input_lower = user_input.lower()
        agent_type, confidence = self.detect_agent_type(user_input)
        
        matched_keywords = []
        for keyword in self.agent_keywords.get(agent_type, []):
            if keyword in user_input_lower:
                matched_keywords.append(keyword)
        
        explanation = f"Selected: {self.get_agent_name(agent_type)}\n"
        explanation += f"Confidence: {confidence:.2f}\n"
        if matched_keywords:
            explanation += f"Matched keywords: {', '.join(matched_keywords)}"
        else:
            explanation += "No specific keywords matched - defaulting to data analysis"
        
        return explanation


# Convenience function for quick routing
def route_to_agent(user_input: str) -> AgentType:
    """Quick helper function to route user input to an agent type."""
    router = AgentRouter()
    return router.route(user_input)
