from typing import Dict, List, Any
from .base_tool import AzureGraphTool
from .terraform_tool import TerraformTool

class ResourceManagementTool(AzureGraphTool):
    """Tool for managing Azure resources using both Graph API and Terraform."""
    
    def __init__(self):
        super().__init__()
        self.terraform = TerraformTool()
        
    def create_resource_group(self, name: str, location: str, use_terraform: bool = False) -> Dict[str, Any]:
        """
        Creates a new resource group.
        
        Args:
            name: Name of the resource group
            location: Azure region (e.g., 'eastus')
            use_terraform: If True, generates Terraform config instead of using Graph API
        """
        try:
            if use_terraform:
                tf_file = self.terraform.create_resource_group(name, location)
                print(f"Generated Terraform config at: {tf_file}")
                return {"terraform_file": tf_file}
            
            body = {
                "location": location,
                "tags": {
                    "created-by": "azure-automation"
                }
            }
            response = self._client.put(f'/subscriptions/{self.subscription_id}/resourcegroups/{name}', json=body)
            print(f"Successfully created resource group: {name} in {location}")
            return response.json()
            
        except Exception as e:
            return self._handle_error(e, "create_resource_group")
    
    def list_resources(self, resource_group: str = None) -> List[Dict[str, Any]]:
        """Lists Azure resources, optionally filtered by resource group."""
        try:
            endpoint = '/resources'
            if resource_group:
                endpoint += f"?$filter=resourceGroup eq '{resource_group}'"
            
            response = self._client.get(endpoint)
            resources = response.json().get('value', [])
            print(f"Retrieved {len(resources)} resources")
            return resources
        except Exception as e:
            return self._handle_error(e, "list_resources")
    
    def delete_resource_group(self, name: str) -> None:
        """Deletes a resource group and all its resources."""
        try:
            response = self._client.delete(f'/subscriptions/{self.subscription_id}/resourcegroups/{name}')
            print(f"Successfully initiated deletion of resource group: {name}")
            return response.status_code
        except Exception as e:
            return self._handle_error(e, "delete_resource_group")
            
    def create_infrastructure(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Creates infrastructure using Terraform based on configuration.
        
        Args:
            config: Dictionary containing infrastructure configuration
                Example:
                {
                    "resource_group": {"name": "my-rg", "location": "eastus"},
                    "virtual_network": {"name": "my-vnet", "address_space": "10.0.0.0/16"},
                    "storage_account": {"name": "mystorageacct", "tier": "Standard"}
                }
        """
        try:
            # Generate provider and backend config
            self.terraform.generate_provider_config()
            
            # Create resources
            files = []
            
            if "resource_group" in config:
                rg = config["resource_group"]
                files.append(self.terraform.create_resource_group(rg["name"], rg["location"]))
            
            if "virtual_network" in config:
                vnet = config["virtual_network"]
                files.append(self.terraform.create_virtual_network(
                    config["resource_group"]["name"],
                    vnet["name"],
                    vnet["address_space"]
                ))
            
            if "storage_account" in config:
                storage = config["storage_account"]
                files.append(self.terraform.create_storage_account(
                    config["resource_group"]["name"],
                    storage["name"],
                    storage.get("tier", "Standard")
                ))
            
            print(f"Generated {len(files)} Terraform configuration files")
            return {"terraform_files": files}
            
        except Exception as e:
            return self._handle_error(e, "create_infrastructure")
