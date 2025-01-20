from typing import Dict, Any
import boto3
from ..base import BaseAWSAgent

class ECSAgent(BaseAWSAgent):
    """Agent for AWS ECS and container operations"""
    
    def __init__(self, session: boto3.Session = None):
        super().__init__(session=session)
        self.characteristics = {
            "name": "ecs_agent",
            "description": "Agent for AWS ECS and container management",
            "capabilities": [
                "manage ECS clusters",
                "handle task definitions",
                "manage services and tasks",
                "configure auto scaling",
                "handle container insights",
                "manage ECR repositories"
            ],
            "example_queries": [
                "Create an ECS cluster with Fargate",
                "Deploy a new container service",
                "Scale ECS service to 5 tasks",
                "Push image to ECR repository"
            ]
        }
