from typing import Dict, List, Any
from .base_tool import AzureGraphTool

class ComputeTool(AzureGraphTool):
    """Tool for managing Azure compute resources."""
    
    def create_vm(self, resource_group: str, name: str, size: str, image: str) -> Dict[str, Any]:
        """Creates a virtual machine."""
        try:
            body = {
                "location": "eastus",  # Default location
                "properties": {
                    "hardwareProfile": {
                        "vmSize": size
                    },
                    "storageProfile": {
                        "imageReference": self._parse_image_reference(image)
                    }
                }
            }
            response = self._client.put(
                f'/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{name}',
                json=body
            )
            print(f"Successfully initiated VM creation: {name}")
            return response.json()
        except Exception as e:
            return self._handle_error(e, "create_vm")
    
    def list_vms(self, resource_group: str = None) -> List[Dict[str, Any]]:
        """Lists virtual machines, optionally filtered by resource group."""
        try:
            endpoint = '/virtualMachines'
            if resource_group:
                endpoint = f'/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines'
            
            response = self._client.get(f'/subscriptions/{self.subscription_id}{endpoint}')
            vms = response.json().get('value', [])
            print(f"Retrieved {len(vms)} virtual machines")
            return vms
        except Exception as e:
            return self._handle_error(e, "list_vms")
    
    def start_vm(self, resource_group: str, name: str) -> None:
        """Starts a virtual machine."""
        try:
            response = self._client.post(
                f'/subscriptions/{self.subscription_id}/resourceGroups/{resource_group}/providers/Microsoft.Compute/virtualMachines/{name}/start'
            )
            print(f"Successfully initiated VM start: {name}")
            return response.status_code
        except Exception as e:
            return self._handle_error(e, "start_vm")
    
    def _parse_image_reference(self, image: str) -> Dict[str, str]:
        """Parses image string into reference object."""
        parts = image.split(':')
        if len(parts) != 4:
            raise ValueError("Image should be in format: publisher:offer:sku:version")
        
        return {
            "publisher": parts[0],
            "offer": parts[1],
            "sku": parts[2],
            "version": parts[3]
        }
