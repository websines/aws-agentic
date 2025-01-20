from typing import Dict, Any, List
import json
from ..base import BaseAWSAgent

class SecurityAgent(BaseAWSAgent):
    """Agent for handling AWS security, IAM, and permissions"""
    
    def _get_characteristics(self) -> Dict[str, Any]:
        return {
            "name": "security_agent",
            "description": "Agent for managing AWS security and permissions",
            "capabilities": [
                "manage IAM roles and policies",
                "handle security groups",
                "configure resource permissions",
                "audit security settings"
            ],
            "example_queries": [
                "Create IAM role for EC2",
                "Add permissions to user",
                "Create security group",
                "Check user permissions"
            ]
        }
    
    async def handle_query(self, query: str) -> Dict[str, Any]:
        """Handle security-related queries"""
        prompt = f"""You are an AWS security expert. For this query:
        1. Determine the security action needed
        2. Extract required parameters
        3. Return a JSON object with exact values
        
        Query: {query}
        
        Return format:
        {{
            "service": "iam/ec2",
            "action": "create_policy/etc",
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
                "response": "Error: Could not parse security action plan",
                "agent": self.characteristics["name"],
                "error": True
            }
        except Exception as e:
            return {
                "response": f"Error executing security action: {str(e)}",
                "agent": self.characteristics["name"],
                "error": True
            }
    
    async def _execute_action(self, action_plan: Dict[str, Any]) -> str:
        """Execute security actions"""
        service = action_plan["service"].lower()
        action = action_plan["action"].lower()
        params = action_plan.get("parameters", {})
        
        if service == "iam":
            iam = self.session.client('iam')
            
            if action == "create_policy":
                try:
                    policy_name = params.get("PolicyName", "EC2FullAccess")
                    policy_document = {
                        "Version": "2012-10-17",
                        "Statement": [
                            {
                                "Effect": "Allow",
                                "Action": [
                                    "ec2:*"
                                ],
                                "Resource": "*"
                            }
                        ]
                    }
                    
                    response = iam.create_policy(
                        PolicyName=policy_name,
                        PolicyDocument=json.dumps(policy_document)
                    )
                    
                    policy_arn = response['Policy']['Arn']
                    
                    # Attach policy to user
                    try:
                        iam.attach_user_policy(
                            UserName=params.get("UserName", "agent-test"),
                            PolicyArn=policy_arn
                        )
                        return f"Created and attached policy {policy_name} to user"
                    except Exception as e:
                        return f"Created policy {policy_name} but failed to attach: {str(e)}"
                
                except Exception as e:
                    return f"Failed to create IAM policy: {str(e)}"
            
            elif action == "check_permissions":
                try:
                    user = params.get("UserName", "agent-test")
                    response = iam.list_attached_user_policies(UserName=user)
                    policies = [p['PolicyName'] for p in response['AttachedPolicies']]
                    return f"User {user} has the following policies: {', '.join(policies)}"
                except Exception as e:
                    return f"Failed to check permissions: {str(e)}"
        
        elif service == "ec2":
            ec2 = self.session.client('ec2')
            
            if action == "create_security_group":
                try:
                    group_name = params.get("GroupName", "default-ec2-sg")
                    description = params.get("Description", "Security group for EC2 instances")
                    vpc_id = params.get("VpcId")
                    
                    # Create security group
                    response = ec2.create_security_group(
                        GroupName=group_name,
                        Description=description,
                        VpcId=vpc_id
                    )
                    
                    group_id = response['GroupId']
                    
                    # Add inbound rules
                    ec2.authorize_security_group_ingress(
                        GroupId=group_id,
                        IpPermissions=[
                            {
                                'IpProtocol': 'tcp',
                                'FromPort': 22,
                                'ToPort': 22,
                                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                            },
                            {
                                'IpProtocol': 'tcp',
                                'FromPort': 80,
                                'ToPort': 80,
                                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]
                            }
                        ]
                    )
                    
                    return f"Created security group {group_name} ({group_id}) with basic rules"
                except Exception as e:
                    return f"Failed to create security group: {str(e)}"
        
        return f"Unsupported security service or action: {service}.{action}"
