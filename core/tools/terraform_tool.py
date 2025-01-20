import os
import json
from typing import Dict, Any
from .base_tool import AzureGraphTool

class TerraformTool:
    """Tool for managing Azure infrastructure using Terraform."""
    
    def __init__(self, working_dir: str = "terraform"):
        self.working_dir = working_dir
        os.makedirs(working_dir, exist_ok=True)
    
    def _write_tf_file(self, content: str, filename: str = "main.tf") -> str:
        """Write terraform configuration to file."""
        filepath = os.path.join(self.working_dir, filename)
        with open(filepath, "w") as f:
            f.write(content)
        print(f"Created Terraform configuration: {filepath}")
        return filepath
    
    def create_resource_group(self, name: str, location: str) -> str:
        """Creates a resource group using Terraform."""
        tf_content = f"""
        resource "azurerm_resource_group" "{name}" {{
            name     = "{name}"
            location = "{location}"
            
            tags = {{
                environment = "production"
                managed-by  = "terraform"
            }}
        }}
        """
        return self._write_tf_file(tf_content, f"{name}_rg.tf")
    
    def create_virtual_network(self, rg_name: str, name: str, address_space: str) -> str:
        """Creates a virtual network using Terraform."""
        tf_content = f"""
        resource "azurerm_virtual_network" "{name}" {{
            name                = "{name}"
            location            = azurerm_resource_group.{rg_name}.location
            resource_group_name = azurerm_resource_group.{rg_name}.name
            address_space       = ["{address_space}"]
            
            tags = {{
                environment = "production"
                managed-by  = "terraform"
            }}
        }}
        """
        return self._write_tf_file(tf_content, f"{name}_vnet.tf")
    
    def create_virtual_machine(self, rg_name: str, name: str, size: str, image: Dict[str, str]) -> str:
        """Creates a virtual machine using Terraform."""
        tf_content = f"""
        resource "azurerm_virtual_machine" "{name}" {{
            name                  = "{name}"
            location             = azurerm_resource_group.{rg_name}.location
            resource_group_name  = azurerm_resource_group.{rg_name}.name
            vm_size             = "{size}"
            
            storage_image_reference {{
                publisher = "{image['publisher']}"
                offer     = "{image['offer']}"
                sku       = "{image['sku']}"
                version   = "{image['version']}"
            }}
            
            storage_os_disk {{
                name              = "{name}-osdisk"
                caching           = "ReadWrite"
                create_option     = "FromImage"
                managed_disk_type = "Standard_LRS"
            }}
            
            os_profile {{
                computer_name  = "{name}"
                admin_username = "azureuser"
                admin_password = "Password1234!"  # Note: Use Azure Key Vault in production
            }}
            
            tags = {{
                environment = "production"
                managed-by  = "terraform"
            }}
        }}
        """
        return self._write_tf_file(tf_content, f"{name}_vm.tf")
    
    def create_storage_account(self, rg_name: str, name: str, tier: str = "Standard") -> str:
        """Creates a storage account using Terraform."""
        tf_content = f"""
        resource "azurerm_storage_account" "{name}" {{
            name                     = "{name}"
            resource_group_name      = azurerm_resource_group.{rg_name}.name
            location                 = azurerm_resource_group.{rg_name}.location
            account_tier             = "{tier}"
            account_replication_type = "LRS"
            
            tags = {{
                environment = "production"
                managed-by  = "terraform"
            }}
        }}
        """
        return self._write_tf_file(tf_content, f"{name}_storage.tf")
    
    def generate_backend_config(self, storage_account: str, container: str, key: str) -> str:
        """Generates backend configuration for Terraform state."""
        tf_content = f"""
        terraform {{
            backend "azurerm" {{
                storage_account_name = "{storage_account}"
                container_name      = "{container}"
                key                = "{key}"
            }}
        }}
        """
        return self._write_tf_file(tf_content, "backend.tf")
    
    def generate_provider_config(self) -> str:
        """Generates Azure provider configuration."""
        tf_content = """
        terraform {
            required_providers {
                azurerm = {
                    source  = "hashicorp/azurerm"
                    version = "~> 2.0"
                }
            }
        }

        provider "azurerm" {
            features {}
        }
        """
        return self._write_tf_file(tf_content, "provider.tf")
