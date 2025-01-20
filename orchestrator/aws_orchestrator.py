from typing import Dict, Any, List, Tuple
import boto3
import json
import aiohttp
from dotenv import load_dotenv
import os

from agents.base import BaseAWSAgent
from agents.security.security_agent import SecurityAgent
from agents.resource.resource_agent import ResourceAgent
from agents.vpc.vpc_agent import VPCAgent
from agents.troubleshooting.troubleshooting_agent import TroubleshootingAgent

load_dotenv()

class AWSOrchestrator:
    """Orchestrator for AWS agents using local Ollama API"""
    
    def __init__(self):
        self.session = boto3.Session()
        self.agents = self._initialize_agents()
        self.ollama_url = os.getenv('OLLAMA_API_URL', 'http://localhost:11434')
        self.model = os.getenv('LLM_MODEL', 'hf.co/Mazino0/phi4-azure:latest')
    
    def _initialize_agents(self) -> Dict[str, BaseAWSAgent]:
        """Initialize all AWS agents"""
        return {
            "security": SecurityAgent(self.session),
            "resource": ResourceAgent(self.session),
            "vpc": VPCAgent(self.session),
            "troubleshoot": TroubleshootingAgent(self.session)
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
    
    async def _analyze_query(self, query: str) -> Tuple[List[str], Dict[str, Any]]:
        """Analyze query to determine required agents and extract action details"""
        prompt = f"""You are an AWS expert. Analyze this query and provide:
1. Required agents in order of execution
2. Action details in JSON format

Query: {query}

Available agents and their responsibilities:
- resource: Creates and manages AWS resources (EC2, S3, etc.)
- security: Handles IAM permissions and security groups
- vpc: Manages VPC, subnets, networking
- troubleshoot: Diagnoses issues and monitors status

For EC2 instance creation, the flow should be:
1. security (check/create permissions)
2. vpc (check/create network)
3. resource (create EC2)
4. troubleshoot (verify creation)

Return EXACTLY in this format (no other text):
AGENTS=resource,security,vpc
ACTION={{
    "service": "ec2",
    "action": "create_instance",
    "parameters": {{
        "ImageId": "ami-xyz",
        "InstanceType": "t2.micro"
    }}
}}
"""
        response = await self._query_ollama(prompt)
        
        # Parse response
        agents = []
        actions = {}
        
        for line in response.split('\n'):
            if line.startswith('AGENTS='):
                agents = [a.strip() for a in line.replace('AGENTS=', '').strip().split(',')]
            elif line.startswith('ACTION='):
                try:
                    actions = json.loads(line.replace('ACTION=', '').strip())
                except:
                    actions = {}
        
        # Ensure we have the right agents for EC2 creation
        if 'create' in query.lower() and 'ec2' in query.lower():
            agents = ['security', 'vpc', 'resource', 'troubleshoot']
            if not actions:
                actions = {
                    "service": "ec2",
                    "action": "create_instance",
                    "parameters": {
                        "ImageId": "ami-0c55b159cbfafe1f0",
                        "InstanceType": "t2.micro"
                    }
                }
        
        return agents, actions
    
    async def process_request(self, query: str) -> Dict[str, Any]:
        """Process a user request using the appropriate agent(s)"""
        required_agents, action_plan = await self._analyze_query(query)
        
        if not required_agents:
            required_agents = ["resource"]  # Default to resource agent
        
        results = {}
        error_encountered = False
        context = {}  # Store context from previous agents
        
        # Execute agents in sequence
        for agent_name in required_agents:
            if error_encountered:
                break
                
            agent = self.agents.get(agent_name)
            if not agent:
                continue
            
            # Build context-aware query
            modified_query = query
            if context:
                modified_query += "\nContext from previous agents:\n"
                for ctx_key, ctx_value in context.items():
                    modified_query += f"{ctx_key}: {ctx_value}\n"
            
            # Add action plan if available
            if action_plan:
                modified_query += f"\nAction plan: {json.dumps(action_plan, indent=2)}"
            
            # Execute agent
            result = await agent.handle_query(modified_query)
            results[agent_name] = result
            
            # Update context based on agent response
            if isinstance(result, dict):
                response_text = result.get('response', '')
                
                # Extract useful information from response
                if agent_name == 'security':
                    if 'policy' in response_text.lower():
                        context['iam_policy'] = response_text
                    if 'security group' in response_text.lower():
                        context['security_group'] = response_text
                
                elif agent_name == 'vpc':
                    if 'vpc' in response_text.lower():
                        context['vpc'] = response_text
                    if 'subnet' in response_text.lower():
                        context['subnet'] = response_text
                
                elif agent_name == 'resource':
                    if 'instance' in response_text.lower():
                        context['instance'] = response_text
                
                # Check for errors
                if result.get('error'):
                    error_encountered = True
                    
                    # Handle specific error cases
                    if 'permission' in response_text.lower() or 'unauthorized' in response_text.lower():
                        # Try to fix permissions automatically
                        security_result = await self.agents['security'].handle_query(
                            f"Fix permissions for: {response_text}"
                        )
                        results['security_fix'] = security_result
                        
                        if not security_result.get('error'):
                            # Retry the failed agent
                            retry_result = await agent.handle_query(modified_query)
                            results[agent_name] = retry_result
                            error_encountered = retry_result.get('error', False)
                            continue
                    
                    elif 'vpc' in response_text.lower() or 'subnet' in response_text.lower():
                        # Try to fix networking automatically
                        vpc_result = await self.agents['vpc'].handle_query(
                            f"Fix networking for: {response_text}"
                        )
                        results['vpc_fix'] = vpc_result
                        
                        if not vpc_result.get('error'):
                            # Retry the failed agent
                            retry_result = await agent.handle_query(modified_query)
                            results[agent_name] = retry_result
                            error_encountered = retry_result.get('error', False)
                            continue
        
        return self._combine_results(results)
    
    def _combine_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Combine results from multiple agents into a coherent response"""
        if not results:
            return {
                "success": False,
                "error": "No agents were able to process the request",
                "responses": {}
            }
        
        combined = {
            "success": True,
            "actions": [],
            "responses": {}
        }
        
        error_messages = []
        
        for agent_name, result in results.items():
            combined["responses"][agent_name] = result
            if isinstance(result, dict):
                if "actions" in result:
                    combined["actions"].extend(result["actions"])
                if result.get("error", False):
                    combined["success"] = False
                    if "response" in result:
                        error_messages.append(f"{agent_name}: {result['response']}")
        
        if error_messages:
            combined["error"] = "\n".join(error_messages)
        
        return combined
