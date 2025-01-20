from typing import Dict, List, Any
from smolagents import tool
from msgraph.core import GraphClient
from azure.identity import ClientSecretCredential
from core.config import Config

# Initialize Graph client
credentials = ClientSecretCredential(
    tenant_id=Config.AZURE_TENANT_ID,
    client_id=Config.AZURE_CLIENT_ID,
    client_secret=Config.AZURE_CLIENT_SECRET
)
graph_client = GraphClient(credential=credentials)

@tool
def create_user(display_name: str, user_principal_name: str, password: str) -> str:
    """
    Creates a new user in Azure AD.
    
    Args:
        display_name: Full name of the user (e.g., 'John Doe')
        user_principal_name: Email/UPN of the user (must end with tenant domain)
        password: Initial password for the user
    """
    try:
        user = {
            "accountEnabled": True,
            "displayName": display_name,
            "userPrincipalName": user_principal_name,
            "passwordProfile": {
                "forceChangePasswordNextSignIn": True,
                "password": password
            }
        }
        
        response = graph_client.post('/users', json=user)
        return f"Successfully created user: {display_name} with UPN: {user_principal_name}"
    except Exception as e:
        return f"Error creating user: {str(e)}"

@tool
def get_security_alerts(severity: str = None) -> str:
    """
    Gets security alerts from Azure Security Center.
    
    Args:
        severity: Optional filter for alert severity ('high', 'medium', 'low')
    """
    try:
        endpoint = '/security/alerts'
        if severity:
            endpoint += f"?$filter=alertSeverity eq '{severity}'"
        
        response = graph_client.get(endpoint)
        alerts = response.json().get('value', [])
        
        if not alerts:
            return "No security alerts found."
        
        alert_summary = []
        for alert in alerts:
            alert_summary.append(
                f"- {alert['title']} (Severity: {alert['alertSeverity']})"
            )
        
        return "Security Alerts:\n" + "\n".join(alert_summary)
    except Exception as e:
        return f"Error getting security alerts: {str(e)}"

@tool
def create_vm(resource_group: str, name: str, size: str, location: str) -> str:
    """
    Creates a virtual machine in Azure.
    
    Args:
        resource_group: Name of the resource group
        name: Name of the VM
        size: VM size (e.g., 'Standard_D2s_v3')
        location: Azure region (e.g., 'eastus')
    """
    try:
        body = {
            "location": location,
            "properties": {
                "hardwareProfile": {
                    "vmSize": size
                },
                "osProfile": {
                    "computerName": name,
                    "adminUsername": "azureuser",
                    "adminPassword": "ComplexPass123!"  # Should use Key Vault in production
                }
            }
        }
        
        endpoint = f'/subscriptions/{Config.SUBSCRIPTION_ID}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{name}'
        response = graph_client.put(endpoint, json=body)
        return f"Successfully initiated VM creation: {name} in {resource_group}"
    except Exception as e:
        return f"Error creating VM: {str(e)}"

@tool
def get_cost_summary(timeframe: str = "LastMonth") -> str:
    """
    Gets Azure cost summary.
    
    Args:
        timeframe: Time period for cost analysis ('LastMonth', 'LastWeek', 'Custom')
    """
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
        
        endpoint = f'/subscriptions/{Config.SUBSCRIPTION_ID}/providers/Microsoft.CostManagement/query'
        response = graph_client.post(endpoint, json=body)
        data = response.json()
        
        total_cost = sum(row[0] for row in data.get('rows', []))
        return f"Total cost for {timeframe}: ${total_cost:.2f}"
    except Exception as e:
        return f"Error getting cost summary: {str(e)}"
