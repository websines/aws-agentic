from agents.base import BaseAzureAgent
from core.tools.resource_tool import ResourceManagementTool

class TerraformAgent(BaseAzureAgent):
    """Agent for managing Azure infrastructure using Terraform."""
    
    def __init__(self):
        super().__init__()
        self.resource_tool = ResourceManagementTool()
    
    def process(self, query: str) -> str:
        """Process infrastructure-as-code requests."""
        enhanced_query = f"""
        Process the following Azure infrastructure request using Terraform: {query}
        
        Available actions:
        1. Generate Terraform configurations for:
           - Resource Groups
           - Virtual Networks
           - Storage Accounts
           - Virtual Machines
        2. Set up backend configuration
        3. Configure Azure provider
        
        Use the provided tools to complete the task. Make sure to:
        - Follow Terraform best practices
        - Use proper resource naming
        - Add appropriate tags
        - Configure backend state
        - Log all generated files
        """
        
        response = self.agent.run(enhanced_query)
        return response
    
    def get_characteristics(self) -> dict:
        return {
            "name": "terraform",
            "description": "Expert in Azure infrastructure-as-code using Terraform",
            "capabilities": [
                "generate_terraform_configs",
                "manage_infrastructure_as_code",
                "setup_terraform_backend",
                "configure_azure_provider"
            ],
            "example_queries": [
                "Create Terraform config for a new web app environment",
                "Generate infrastructure code for a three-tier application",
                "Set up Terraform backend with Azure storage",
                "Create a VM with networking using Terraform"
            ]
        }
