from agents.base import BaseAzureAgent
from core.tools.cost_tool import CostManagementTool

class CostManagementAgent(BaseAzureAgent):
    """Agent for managing Azure costs."""
    
    def __init__(self):
        super().__init__()
        self.cost_tool = CostManagementTool()
    
    def process(self, query: str) -> str:
        """Process cost management requests."""
        enhanced_query = f"""
        Process the following Azure cost management request: {query}
        
        Available actions:
        1. Get cost summaries
        2. Analyze costs by resource
        3. Check budget alerts
        4. Generate cost reports
        
        Use the provided tools to complete the task. Make sure to:
        - Include relevant time periods
        - Break down costs by service
        - Highlight cost anomalies
        - Suggest optimization opportunities
        """
        
        response = self.agent.run(enhanced_query)
        return response
    
    def get_characteristics(self) -> dict:
        return {
            "name": "cost_management",
            "description": "Expert in Azure cost management, analyzing costs and providing optimization recommendations",
            "capabilities": [
                "analyze_costs",
                "monitor_budgets",
                "generate_cost_reports",
                "suggest_cost_optimizations"
            ],
            "example_queries": [
                "Show me last month's total costs",
                "Which resources are costing the most?",
                "Are we over budget this month?",
                "Generate a cost report for Q1"
            ]
        }
