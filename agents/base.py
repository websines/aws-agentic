from typing import Dict, Any, List
import boto3
import os
import aiohttp
from dotenv import load_dotenv

load_dotenv()

class BaseAWSAgent:
    """Base agent class for AWS operations"""
    
    def __init__(self, session: boto3.Session = None):
        self.session = session or boto3.Session()
        self.characteristics = self._get_characteristics()
        self.ollama_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        self.model = os.getenv('LLM_MODEL', 'phi-2')
    
    def _get_characteristics(self) -> Dict[str, Any]:
        """Get the characteristics of this agent"""
        return {
            "name": "base_aws_agent",
            "description": "Base agent for AWS operations",
            "capabilities": [
                "manage AWS resources",
                "handle AWS services",
                "automate AWS tasks"
            ],
            "example_queries": [
                "List all EC2 instances",
                "Create an S3 bucket",
                "Check IAM roles"
            ]
        }
    
    async def _query_ollama(self, prompt: str) -> str:
        """Query the local Ollama API"""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False
                }
            ) as response:
                result = await response.json()
                return result.get('response', '')
    
    async def handle_query(self, query: str) -> Dict[str, Any]:
        """Handle a user query"""
        prompt = f"""You are an AWS agent specialized in {self.characteristics.get('description', 'AWS operations')}.
        Your capabilities include: {', '.join(self.characteristics.get('capabilities', []))}
        
        Query: {query}
        
        Analyze the query and determine which AWS actions to take. Return a JSON object with:
        1. actions: list of actions to take
        2. tools: list of tools needed
        3. parameters: parameters for each tool
        """
        
        response = await self._query_ollama(prompt)
        # Process response and execute AWS actions
        return {"response": response, "agent": self.characteristics.get("name")}
    
    def assume_role(self, role_arn: str, session_name: str = "agent-session"):
        """Assume an IAM role for cross-account access"""
        sts = self.session.client('sts')
        response = sts.assume_role(
            RoleArn=role_arn,
            RoleSessionName=session_name
        )
        credentials = response['Credentials']
        
        # Create new session with assumed role credentials
        self.session = boto3.Session(
            aws_access_key_id=credentials['AccessKeyId'],
            aws_secret_access_key=credentials['SecretAccessKey'],
            aws_session_token=credentials['SessionToken']
        )
