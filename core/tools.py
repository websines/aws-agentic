from typing import List, Dict, Any
from msgraph.core import GraphClient
from core.graph import get_graph_client

class AzureGraphTool:
    """Base class for Azure Graph API tools."""
    
    def __init__(self):
        self._client = get_graph_client()
        
    def _handle_error(self, e: Exception, context: str) -> str:
        error_msg = f"Error in {context}: {str(e)}"
        print(f"Tool execution failed - {error_msg}")  # Logging for LLM
        raise ValueError(error_msg)

class UserManagementTool(AzureGraphTool):
    """Tool for managing users in Azure AD."""
    
    def create_user(self, display_name: str, user_principal_name: str, password: str) -> Dict[str, Any]:
        """
        Creates a new user in Azure AD.
        
        Args:
            display_name: Full name of the user
            user_principal_name: Email/UPN of the user (must end with tenant domain)
            password: Initial password for the user
            
        Returns:
            Dict containing the created user information
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
            
            response = self._client.post('/users', json=user)
            print(f"Successfully created user: {display_name}")
            return response.json()
            
        except Exception as e:
            return self._handle_error(e, "create_user")
    
    def assign_license(self, user_id: str, sku_id: str) -> Dict[str, Any]:
        """
        Assigns a license to a user.
        
        Args:
            user_id: Object ID of the user
            sku_id: SKU ID of the license to assign
            
        Returns:
            Dict containing the license assignment result
        """
        try:
            license_body = {
                "addLicenses": [{"skuId": sku_id}],
                "removeLicenses": []
            }
            
            response = self._client.post(f'/users/{user_id}/assignLicense', json=license_body)
            print(f"Successfully assigned license {sku_id} to user {user_id}")
            return response.json()
            
        except Exception as e:
            return self._handle_error(e, "assign_license")

class ComplianceTool(AzureGraphTool):
    """Tool for checking compliance status in Azure."""
    
    def get_device_compliance(self, user_id: str = None) -> List[Dict[str, Any]]:
        """
        Gets compliance status for devices.
        
        Args:
            user_id: Optional user ID to filter devices
            
        Returns:
            List of device compliance states
        """
        try:
            endpoint = '/deviceManagement/managedDevices'
            if user_id:
                endpoint += f"?$filter=userId eq '{user_id}'"
                
            response = self._client.get(endpoint)
            devices = response.json().get('value', [])
            print(f"Retrieved compliance status for {len(devices)} devices")
            return devices
            
        except Exception as e:
            return self._handle_error(e, "get_device_compliance")
    
    def get_conditional_access_policies(self) -> List[Dict[str, Any]]:
        """Gets all conditional access policies."""
        try:
            response = self._client.get('/identity/conditionalAccess/policies')
            policies = response.json().get('value', [])
            print(f"Retrieved {len(policies)} conditional access policies")
            return policies
            
        except Exception as e:
            return self._handle_error(e, "get_conditional_access_policies")
