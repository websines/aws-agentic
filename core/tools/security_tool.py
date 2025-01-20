from typing import Dict, List, Any
from .base_tool import AzureGraphTool

class SecurityTool(AzureGraphTool):
    """Tool for managing Azure security."""
    
    def get_security_alerts(self, resource_group: str = None) -> List[Dict[str, Any]]:
        """Gets security alerts, optionally filtered by resource group."""
        try:
            endpoint = '/security/alerts'
            if resource_group:
                endpoint += f"?$filter=resourceGroup eq '{resource_group}'"
            
            response = self._client.get(endpoint)
            alerts = response.json().get('value', [])
            print(f"Retrieved {len(alerts)} security alerts")
            return alerts
        except Exception as e:
            return self._handle_error(e, "get_security_alerts")
    
    def get_security_score(self) -> Dict[str, Any]:
        """Gets the tenant's secure score."""
        try:
            response = self._client.get('/security/secureScores')
            scores = response.json().get('value', [])
            print(f"Retrieved secure score information")
            return scores[0] if scores else {}
        except Exception as e:
            return self._handle_error(e, "get_security_score")
    
    def get_security_recommendations(self) -> List[Dict[str, Any]]:
        """Gets security recommendations for the tenant."""
        try:
            response = self._client.get('/security/assessments')
            recommendations = response.json().get('value', [])
            print(f"Retrieved {len(recommendations)} security recommendations")
            return recommendations
        except Exception as e:
            return self._handle_error(e, "get_security_recommendations")
