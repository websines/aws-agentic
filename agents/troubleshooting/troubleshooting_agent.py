from typing import Dict, Any, List
import boto3
from ..base import BaseAWSAgent

class TroubleshootingAgent(BaseAWSAgent):
    """Agent for troubleshooting AWS issues and checking resource status"""
    
    def _get_characteristics(self) -> Dict[str, Any]:
        return {
            "name": "troubleshooting_agent",
            "description": "Agent for troubleshooting AWS issues",
            "capabilities": [
                "check resource status",
                "diagnose AWS errors",
                "verify AWS configurations",
                "test AWS connectivity",
                "monitor resource health"
            ],
            "example_queries": [
                "Check if EC2 instance is running",
                "Why did my S3 upload fail?",
                "Test VPC connectivity",
                "Verify IAM permissions"
            ]
        }
    
    async def handle_query(self, query: str) -> Dict[str, Any]:
        """Handle troubleshooting queries"""
        # Get troubleshooting instructions from LLM
        prompt = f"""You are an AWS troubleshooting expert. Analyze this issue and provide:
        1. Diagnostic steps
        2. Common causes
        3. Required AWS permissions
        4. Solutions to try
        
        Issue: {query}
        """
        
        analysis = await self._query_ollama(prompt)
        
        # Perform actual AWS checks
        try:
            results = await self._check_resources(query)
            return {
                "response": f"Troubleshooting Analysis:\n{analysis}\n\nResource Status:\n{results}",
                "agent": self.characteristics["name"],
                "actions": self._get_required_actions(query)
            }
        except Exception as e:
            return {
                "response": f"Error during troubleshooting: {str(e)}\n\nTroubleshooting Steps:\n{analysis}",
                "agent": self.characteristics["name"],
                "error": True
            }
    
    async def _check_resources(self, query: str) -> str:
        """Check relevant AWS resources based on the query"""
        results = []
        
        # EC2 checks
        if "ec2" in query.lower():
            ec2 = self.session.client('ec2')
            instances = ec2.describe_instances()
            results.append("\nEC2 Instances Status:")
            for reservation in instances['Reservations']:
                for instance in reservation['Instances']:
                    results.append(f"- Instance {instance['InstanceId']}: {instance['State']['Name']}")
        
        # S3 checks
        if "s3" in query.lower():
            s3 = self.session.client('s3')
            buckets = s3.list_buckets()
            results.append("\nS3 Buckets Status:")
            for bucket in buckets['Buckets']:
                results.append(f"- Bucket {bucket['Name']}: Available")
        
        # IAM checks
        if "iam" in query.lower() or "permission" in query.lower():
            iam = self.session.client('iam')
            user = iam.get_user()
            results.append("\nIAM Status:")
            results.append(f"- Current User: {user['User']['UserName']}")
            results.append("- Permissions: Checking...")
            
            try:
                policies = iam.list_attached_user_policies(UserName=user['User']['UserName'])
                for policy in policies['AttachedPolicies']:
                    results.append(f"  - {policy['PolicyName']}")
            except Exception as e:
                results.append(f"  - Error checking policies: {str(e)}")
        
        return "\n".join(results) if results else "No specific resource checks performed"
    
    def _get_required_actions(self, query: str) -> List[str]:
        """Determine required actions based on the query"""
        actions = []
        
        if "ec2" in query.lower():
            actions.extend([
                "Check EC2 instance status",
                "Verify security group rules",
                "Check VPC connectivity"
            ])
        
        if "s3" in query.lower():
            actions.extend([
                "Verify bucket permissions",
                "Check bucket policy",
                "Test bucket access"
            ])
        
        if "iam" in query.lower() or "permission" in query.lower():
            actions.extend([
                "Check IAM policies",
                "Verify role permissions",
                "Test AWS credentials"
            ])
        
        return actions
