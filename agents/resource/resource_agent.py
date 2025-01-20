from typing import Dict, Any, List
import json
from ..base import BaseAWSAgent

class ResourceAgent(BaseAWSAgent):
    """Agent for managing AWS resources like EC2, S3, etc."""
    
    def _get_characteristics(self) -> Dict[str, Any]:
        return {
            "name": "resource_agent",
            "description": "Agent for managing AWS resources",
            "capabilities": [
                "create and manage EC2 instances",
                "manage S3 buckets",
                "handle AWS resources",
                "automate resource creation"
            ],
            "example_queries": [
                "Create an EC2 instance",
                "List all S3 buckets",
                "Start EC2 instance i-1234567890abcdef0"
            ]
        }
    
    async def handle_query(self, query: str) -> Dict[str, Any]:
        """Handle resource management queries"""
        # First, analyze the query using LLM
        prompt = f"""You are an AWS resource management expert. For this query:
        1. Determine the AWS service and action
        2. Extract required parameters
        3. Return a JSON object with exact values (no placeholders)
        
        Query: {query}
        
        Return format:
        {{
            "service": "ec2/s3/etc",
            "action": "create_instance/etc",
            "parameters": {{
                "param1": "value1"
            }}
        }}
        """
        
        analysis = await self._query_ollama(prompt)
        
        try:
            # Parse the LLM response
            action_plan = json.loads(analysis)
            
            # Execute the action
            result = await self._execute_action(action_plan)
            
            return {
                "response": f"Action executed successfully:\n{result}",
                "agent": self.characteristics["name"],
                "actions": [f"{action_plan['service']}.{action_plan['action']}"],
                "result": result
            }
        except json.JSONDecodeError:
            return {
                "response": "Error: Could not parse action plan. Please try again with more specific details.",
                "agent": self.characteristics["name"],
                "error": True
            }
        except Exception as e:
            return {
                "response": f"Error executing action: {str(e)}",
                "agent": self.characteristics["name"],
                "error": True
            }
    
    async def _execute_action(self, action_plan: Dict[str, Any]) -> str:
        """Execute AWS actions based on the plan"""
        service = action_plan["service"].lower()
        action = action_plan["action"].lower()
        params = action_plan.get("parameters", {})
        
        if service == "ec2":
            ec2 = self.session.client('ec2')
            
            if action in ["create_instance", "run_instances"]:
                try:
                    # Set default values for missing parameters
                    instance_params = {
                        "ImageId": params.get("ImageId", "ami-0c55b159cbfafe1f0"),  # Amazon Linux 2
                        "InstanceType": params.get("InstanceType", "t2.micro"),
                        "MinCount": params.get("MinCount", 1),
                        "MaxCount": params.get("MaxCount", 1)
                    }
                    
                    # Add optional parameters if provided
                    if "KeyName" in params:
                        instance_params["KeyName"] = params["KeyName"]
                    if "SecurityGroupIds" in params:
                        instance_params["SecurityGroupIds"] = params["SecurityGroupIds"]
                    if "SubnetId" in params:
                        instance_params["SubnetId"] = params["SubnetId"]
                    
                    # First check permissions
                    try:
                        ec2.describe_instances(MaxResults=5)
                    except Exception as e:
                        if "UnauthorizedOperation" in str(e):
                            return f"Error: Insufficient permissions. Please ensure your AWS credentials have the following permissions:\n- ec2:RunInstances\n- ec2:DescribeInstances\nError details: {str(e)}"
                    
                    # Try to launch the instance
                    response = ec2.run_instances(**instance_params)
                    instance_id = response['Instances'][0]['InstanceId']
                    return f"Successfully created EC2 instance: {instance_id}"
                except Exception as e:
                    return f"Failed to create EC2 instance: {str(e)}\n\nPlease ensure:\n1. You have sufficient permissions\n2. The AMI ID is valid\n3. The instance type is available in your region\n4. Your VPC and subnet configurations are correct"
            
            elif action == "list_instances":
                try:
                    response = ec2.describe_instances()
                    instances = []
                    for reservation in response['Reservations']:
                        for instance in reservation['Instances']:
                            instances.append({
                                'id': instance['InstanceId'],
                                'state': instance['State']['Name'],
                                'type': instance['InstanceType']
                            })
                    return f"Found {len(instances)} instances:\n" + "\n".join(
                        f"- {i['id']} ({i['type']}): {i['state']}" for i in instances
                    )
                except Exception as e:
                    return f"Failed to list EC2 instances: {str(e)}"
        
        elif service == "s3":
            s3 = self.session.client('s3')
            
            if action == "create_bucket":
                try:
                    bucket_name = params.get("Bucket")
                    if not bucket_name:
                        return "Error: Bucket name is required"
                    
                    create_params = {"Bucket": bucket_name}
                    if "LocationConstraint" in params:
                        create_params["CreateBucketConfiguration"] = {
                            "LocationConstraint": params["LocationConstraint"]
                        }
                    
                    response = s3.create_bucket(**create_params)
                    return f"Created S3 bucket: {bucket_name}"
                except Exception as e:
                    return f"Failed to create S3 bucket: {str(e)}"
            
            elif action == "list_buckets":
                try:
                    response = s3.list_buckets()
                    buckets = [b['Name'] for b in response['Buckets']]
                    return f"Found {len(buckets)} buckets:\n" + "\n".join(f"- {b}" for b in buckets)
                except Exception as e:
                    return f"Failed to list S3 buckets: {str(e)}"
        
        return f"Unsupported service or action: {service}.{action}"
