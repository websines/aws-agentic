from typing import Dict, Any, List
import boto3
from smolagents import tool

class AWSToolBase:
    """Base class for AWS tools"""
    def __init__(self, session: boto3.Session):
        self.session = session

class EC2Tool(AWSToolBase):
    """Tool for EC2 operations"""
    
    @tool
    def create_instance(self, instance_type: str, ami_id: str, key_name: str = None) -> Dict[str, Any]:
        """Create an EC2 instance"""
        ec2 = self.session.client('ec2')
        response = ec2.run_instances(
            ImageId=ami_id,
            InstanceType=instance_type,
            MinCount=1,
            MaxCount=1,
            KeyName=key_name
        )
        return response['Instances'][0]
    
    @tool
    def list_instances(self) -> List[Dict[str, Any]]:
        """List all EC2 instances"""
        ec2 = self.session.client('ec2')
        response = ec2.describe_instances()
        instances = []
        for reservation in response['Reservations']:
            instances.extend(reservation['Instances'])
        return instances

class S3Tool(AWSToolBase):
    """Tool for S3 operations"""
    
    @tool
    def create_bucket(self, bucket_name: str, region: str = None) -> Dict[str, Any]:
        """Create an S3 bucket"""
        s3 = self.session.client('s3')
        if region:
            response = s3.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
        else:
            response = s3.create_bucket(Bucket=bucket_name)
        return response
    
    @tool
    def list_buckets(self) -> List[Dict[str, Any]]:
        """List all S3 buckets"""
        s3 = self.session.client('s3')
        response = s3.list_buckets()
        return response['Buckets']

class IAMTool(AWSToolBase):
    """Tool for IAM operations"""
    
    @tool
    def create_user(self, username: str) -> Dict[str, Any]:
        """Create an IAM user"""
        iam = self.session.client('iam')
        response = iam.create_user(UserName=username)
        return response['User']
    
    @tool
    def list_users(self) -> List[Dict[str, Any]]:
        """List all IAM users"""
        iam = self.session.client('iam')
        response = iam.list_users()
        return response['Users']

class CloudWatchTool(AWSToolBase):
    """Tool for CloudWatch operations"""
    
    @tool
    def create_alarm(self, alarm_name: str, metric_name: str, namespace: str, threshold: float) -> Dict[str, Any]:
        """Create a CloudWatch alarm"""
        cloudwatch = self.session.client('cloudwatch')
        response = cloudwatch.put_metric_alarm(
            AlarmName=alarm_name,
            MetricName=metric_name,
            Namespace=namespace,
            Statistic='Average',
            Period=300,
            EvaluationPeriods=1,
            Threshold=threshold,
            ComparisonOperator='GreaterThanThreshold'
        )
        return response
    
    @tool
    def get_metrics(self, namespace: str, metric_name: str) -> List[Dict[str, Any]]:
        """Get CloudWatch metrics"""
        cloudwatch = self.session.client('cloudwatch')
        response = cloudwatch.get_metric_data(
            MetricDataQueries=[{
                'Id': 'm1',
                'MetricStat': {
                    'Metric': {
                        'Namespace': namespace,
                        'MetricName': metric_name
                    },
                    'Period': 300,
                    'Stat': 'Average'
                }
            }],
            StartTime='2024-01-19T00:00:00Z',
            EndTime='2024-01-20T00:00:00Z'
        )
        return response['MetricDataResults']

class LambdaTool(AWSToolBase):
    """Tool for Lambda operations"""
    
    @tool
    def create_function(self, function_name: str, runtime: str, handler: str, role_arn: str, code: bytes) -> Dict[str, Any]:
        """Create a Lambda function"""
        lambda_client = self.session.client('lambda')
        response = lambda_client.create_function(
            FunctionName=function_name,
            Runtime=runtime,
            Role=role_arn,
            Handler=handler,
            Code={'ZipFile': code}
        )
        return response
    
    @tool
    def list_functions(self) -> List[Dict[str, Any]]:
        """List all Lambda functions"""
        lambda_client = self.session.client('lambda')
        response = lambda_client.list_functions()
        return response['Functions']

class RDSTool(AWSToolBase):
    """Tool for RDS operations"""
    
    @tool
    def create_db_instance(self, db_name: str, instance_class: str, engine: str) -> Dict[str, Any]:
        """Create an RDS instance"""
        rds = self.session.client('rds')
        response = rds.create_db_instance(
            DBInstanceIdentifier=db_name,
            DBInstanceClass=instance_class,
            Engine=engine,
            AllocatedStorage=20,
            MasterUsername='admin',
            MasterUserPassword='temppassword123'  # Should be changed immediately
        )
        return response['DBInstance']
    
    @tool
    def list_db_instances(self) -> List[Dict[str, Any]]:
        """List all RDS instances"""
        rds = self.session.client('rds')
        response = rds.describe_db_instances()
        return response['DBInstances']
