from typing import Dict, List, Any
from .base_tool import AzureGraphTool

class CostManagementTool(AzureGraphTool):
    """Tool for managing Azure costs."""
    
    def get_cost_summary(self, timeframe: str = "LastMonth") -> Dict[str, Any]:
        """Gets cost summary for the specified timeframe."""
        try:
            body = {
                "type": "Usage",
                "timeframe": timeframe,
                "dataset": {
                    "granularity": "Daily",
                    "aggregation": {
                        "totalCost": {
                            "name": "Cost",
                            "function": "Sum"
                        }
                    }
                }
            }
            response = self._client.post(
                f'/subscriptions/{self.subscription_id}/providers/Microsoft.CostManagement/query',
                json=body
            )
            print(f"Retrieved cost summary for {timeframe}")
            return response.json()
        except Exception as e:
            return self._handle_error(e, "get_cost_summary")
    
    def get_cost_by_resource(self, timeframe: str = "LastMonth") -> List[Dict[str, Any]]:
        """Gets cost breakdown by resource."""
        try:
            body = {
                "type": "Usage",
                "timeframe": timeframe,
                "dataset": {
                    "granularity": "None",
                    "grouping": [
                        {
                            "type": "Dimension",
                            "name": "ResourceId"
                        }
                    ],
                    "aggregation": {
                        "totalCost": {
                            "name": "Cost",
                            "function": "Sum"
                        }
                    }
                }
            }
            response = self._client.post(
                f'/subscriptions/{self.subscription_id}/providers/Microsoft.CostManagement/query',
                json=body
            )
            print(f"Retrieved cost breakdown by resource for {timeframe}")
            return response.json().get('rows', [])
        except Exception as e:
            return self._handle_error(e, "get_cost_by_resource")
    
    def get_budget_alerts(self) -> List[Dict[str, Any]]:
        """Gets budget alerts."""
        try:
            response = self._client.get(
                f'/subscriptions/{self.subscription_id}/providers/Microsoft.Consumption/budgets'
            )
            budgets = response.json().get('value', [])
            print(f"Retrieved {len(budgets)} budget alerts")
            return budgets
        except Exception as e:
            return self._handle_error(e, "get_budget_alerts")
