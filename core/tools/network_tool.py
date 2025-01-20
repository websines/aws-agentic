from typing import Dict, List, Any
from .base_tool import AzureGraphTool

class NetworkTool(AzureGraphTool):
    """Tool for managing Azure networking."""
    
    def create_vnet(self, resource_group: str, name: str, address_space: str) -> Dict[str, Any]:
        """Creates a virtual network."""
        try:
            body = {
                "location": "eastus",  # Default location
                "properties": {
                    "addressSpace": {
                        "addressPrefixes": [address_space]
                    }
                }
            }
            response = self._client.put(
                f'/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks/{name}',
                json=body
            )
            print(f"Successfully created VNet: {name}")
            return response.json()
        except Exception as e:
            return self._handle_error(e, "create_vnet")
    
    def create_subnet(self, resource_group: str, vnet_name: str, subnet_name: str, address_prefix: str) -> Dict[str, Any]:
        """Creates a subnet in a virtual network."""
        try:
            body = {
                "properties": {
                    "addressPrefix": address_prefix
                }
            }
            response = self._client.put(
                f'/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/virtualNetworks/{vnet_name}/subnets/{subnet_name}',
                json=body
            )
            print(f"Successfully created subnet: {subnet_name}")
            return response.json()
        except Exception as e:
            return self._handle_error(e, "create_subnet")
    
    def get_network_security_groups(self, resource_group: str) -> List[Dict[str, Any]]:
        """Lists network security groups in a resource group."""
        try:
            response = self._client.get(
                f'/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Network/networkSecurityGroups'
            )
            nsgs = response.json().get('value', [])
            print(f"Retrieved {len(nsgs)} network security groups")
            return nsgs
        except Exception as e:
            return self._handle_error(e, "get_network_security_groups")
