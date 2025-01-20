from typing import Dict, Any, List
import json
from ..base import BaseAWSAgent

class VPCAgent(BaseAWSAgent):
    """Agent for managing AWS VPC and networking"""
    
    def _get_characteristics(self) -> Dict[str, Any]:
        return {
            "name": "vpc_agent",
            "description": "Agent for managing AWS VPC and networking",
            "capabilities": [
                "manage VPCs",
                "configure subnets",
                "handle route tables",
                "manage network ACLs",
                "configure internet gateways"
            ],
            "example_queries": [
                "Create VPC",
                "Add subnet to VPC",
                "Configure internet gateway",
                "Set up route table"
            ]
        }
    
    async def handle_query(self, query: str) -> Dict[str, Any]:
        """Handle VPC and networking queries"""
        prompt = f"""You are an AWS networking expert. For this query:
        1. Determine the networking action needed
        2. Extract required parameters
        3. Return a JSON object with exact values
        
        Query: {query}
        
        Return format:
        {{
            "service": "vpc",
            "action": "create_vpc/create_subnet/etc",
            "parameters": {{
                "param1": "value1"
            }}
        }}
        """
        
        analysis = await self._query_ollama(prompt)
        
        try:
            action_plan = json.loads(analysis)
            result = await self._execute_action(action_plan)
            
            return {
                "response": result,
                "agent": self.characteristics["name"],
                "actions": [f"{action_plan['service']}.{action_plan['action']}"]
            }
        except json.JSONDecodeError:
            return {
                "response": "Error: Could not parse networking action plan",
                "agent": self.characteristics["name"],
                "error": True
            }
        except Exception as e:
            return {
                "response": f"Error executing networking action: {str(e)}",
                "agent": self.characteristics["name"],
                "error": True
            }
    
    async def _execute_action(self, action_plan: Dict[str, Any]) -> str:
        """Execute VPC and networking actions"""
        service = action_plan["service"].lower()
        action = action_plan["action"].lower()
        params = action_plan.get("parameters", {})
        
        if service == "vpc":
            ec2 = self.session.client('ec2')
            
            if action == "create_vpc":
                try:
                    cidr_block = params.get("CidrBlock", "10.0.0.0/16")
                    vpc_name = params.get("Name", "default-vpc")
                    
                    # Create VPC
                    response = ec2.create_vpc(CidrBlock=cidr_block)
                    vpc_id = response['Vpc']['VpcId']
                    
                    # Add name tag
                    ec2.create_tags(
                        Resources=[vpc_id],
                        Tags=[{'Key': 'Name', 'Value': vpc_name}]
                    )
                    
                    # Enable DNS hostnames
                    ec2.modify_vpc_attribute(
                        VpcId=vpc_id,
                        EnableDnsHostnames={'Value': True}
                    )
                    
                    return f"Created VPC {vpc_name} ({vpc_id}) with CIDR {cidr_block}"
                except Exception as e:
                    return f"Failed to create VPC: {str(e)}"
            
            elif action == "create_subnet":
                try:
                    vpc_id = params.get("VpcId")
                    if not vpc_id:
                        return "Error: VPC ID is required"
                    
                    cidr_block = params.get("CidrBlock", "10.0.1.0/24")
                    subnet_name = params.get("Name", "default-subnet")
                    
                    # Create subnet
                    response = ec2.create_subnet(
                        VpcId=vpc_id,
                        CidrBlock=cidr_block
                    )
                    subnet_id = response['Subnet']['SubnetId']
                    
                    # Add name tag
                    ec2.create_tags(
                        Resources=[subnet_id],
                        Tags=[{'Key': 'Name', 'Value': subnet_name}]
                    )
                    
                    return f"Created subnet {subnet_name} ({subnet_id}) in VPC {vpc_id}"
                except Exception as e:
                    return f"Failed to create subnet: {str(e)}"
            
            elif action == "create_internet_gateway":
                try:
                    vpc_id = params.get("VpcId")
                    if not vpc_id:
                        return "Error: VPC ID is required"
                    
                    # Create internet gateway
                    response = ec2.create_internet_gateway()
                    igw_id = response['InternetGateway']['InternetGatewayId']
                    
                    # Attach to VPC
                    ec2.attach_internet_gateway(
                        InternetGatewayId=igw_id,
                        VpcId=vpc_id
                    )
                    
                    return f"Created and attached internet gateway {igw_id} to VPC {vpc_id}"
                except Exception as e:
                    return f"Failed to create/attach internet gateway: {str(e)}"
            
            elif action == "create_route_table":
                try:
                    vpc_id = params.get("VpcId")
                    if not vpc_id:
                        return "Error: VPC ID is required"
                    
                    # Create route table
                    response = ec2.create_route_table(VpcId=vpc_id)
                    route_table_id = response['RouteTable']['RouteTableId']
                    
                    # Add internet gateway route if specified
                    igw_id = params.get("InternetGatewayId")
                    if igw_id:
                        ec2.create_route(
                            RouteTableId=route_table_id,
                            DestinationCidrBlock='0.0.0.0/0',
                            GatewayId=igw_id
                        )
                    
                    return f"Created route table {route_table_id} for VPC {vpc_id}"
                except Exception as e:
                    return f"Failed to create route table: {str(e)}"
        
        return f"Unsupported networking service or action: {service}.{action}"
