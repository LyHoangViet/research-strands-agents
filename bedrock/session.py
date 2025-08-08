"""AWS Session management for Bedrock services"""

import boto3
import os
from typing import Optional, Dict, Any
from botocore.exceptions import ClientError, NoCredentialsError
import logging

logger = logging.getLogger(__name__)

class AWSSession:
    """AWS Session manager for Bedrock services"""
    
    def __init__(self):
        self.session = None
        self.bedrock_client = None
        self.bedrock_runtime_client = None
    
    def create_session(
        self,
        access_key_id: Optional[str] = None,
        secret_access_key: Optional[str] = None,
        session_token: Optional[str] = None,
        region_name: str = "us-east-1",
        profile_name: Optional[str] = None
    ) -> boto3.Session:
        """
        Tạo AWS session với access key hoặc profile
        
        Args:
            access_key_id: AWS Access Key ID
            secret_access_key: AWS Secret Access Key
            session_token: AWS Session Token (cho temporary credentials)
            region_name: AWS region (default: us-east-1)
            profile_name: AWS profile name (alternative to access keys)
        
        Returns:
            boto3.Session: AWS session object
        """
        try:
            # Nếu có profile name, sử dụng profile
            if profile_name:
                self.session = boto3.Session(
                    profile_name=profile_name,
                    region_name=region_name
                )
                logger.info(f"Created session with profile: {profile_name}")
            
            # Nếu có access keys, sử dụng credentials trực tiếp
            elif access_key_id and secret_access_key:
                self.session = boto3.Session(
                    aws_access_key_id=access_key_id,
                    aws_secret_access_key=secret_access_key,
                    aws_session_token=session_token,
                    region_name=region_name
                )
                logger.info("Created session with access keys")
            
            # Sử dụng default credentials (environment variables, IAM role, etc.)
            else:
                self.session = boto3.Session(region_name=region_name)
                logger.info("Created session with default credentials")
            
            # Test session bằng cách gọi STS get-caller-identity
            self._validate_session()
            
            return self.session
            
        except NoCredentialsError:
            logger.error("No AWS credentials found")
            raise ValueError("AWS credentials not found. Please provide access keys or configure AWS credentials.")
        
        except ClientError as e:
            logger.error(f"AWS client error: {e}")
            raise ValueError(f"Failed to create AWS session: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error creating session: {e}")
            raise ValueError(f"Failed to create AWS session: {e}")
    
    def _validate_session(self):
        """Validate session by calling STS get-caller-identity"""
        try:
            sts_client = self.session.client('sts')
            identity = sts_client.get_caller_identity()
            logger.info(f"Session validated for account: {identity.get('Account')}")
            logger.info(f"User ARN: {identity.get('Arn')}")
        except Exception as e:
            logger.error(f"Session validation failed: {e}")
            raise ValueError(f"Invalid AWS credentials: {e}")
    
    def get_bedrock_client(self):
        """Get Bedrock client for model management"""
        if not self.session:
            raise ValueError("Session not created. Call create_session() first.")
        
        if not self.bedrock_client:
            self.bedrock_client = self.session.client('bedrock')
            logger.info("Created Bedrock client")
        
        return self.bedrock_client
    
    def get_bedrock_runtime_client(self):
        """Get Bedrock Runtime client for model inference"""
        if not self.session:
            raise ValueError("Session not created. Call create_session() first.")
        
        if not self.bedrock_runtime_client:
            self.bedrock_runtime_client = self.session.client('bedrock-runtime')
            logger.info("Created Bedrock Runtime client")
        
        return self.bedrock_runtime_client
    
    def list_available_models(self) -> Dict[str, Any]:
        """List available foundation models in Bedrock"""
        try:
            bedrock_client = self.get_bedrock_client()
            response = bedrock_client.list_foundation_models()
            
            models = []
            for model in response.get('modelSummaries', []):
                models.append({
                    'modelId': model.get('modelId'),
                    'modelName': model.get('modelName'),
                    'providerName': model.get('providerName'),
                    'inputModalities': model.get('inputModalities', []),
                    'outputModalities': model.get('outputModalities', [])
                })
            
            logger.info(f"Found {len(models)} available models")
            return {'models': models}
            
        except Exception as e:
            logger.error(f"Error listing models: {e}")
            raise ValueError(f"Failed to list models: {e}")
    
    def get_session_info(self) -> Dict[str, Any]:
        """Get current session information"""
        if not self.session:
            return {"status": "No active session"}
        
        try:
            sts_client = self.session.client('sts')
            identity = sts_client.get_caller_identity()
            
            return {
                "status": "Active",
                "account_id": identity.get('Account'),
                "user_arn": identity.get('Arn'),
                "user_id": identity.get('UserId'),
                "region": self.session.region_name
            }
        except Exception as e:
            logger.error(f"Error getting session info: {e}")
            return {"status": "Error", "error": str(e)}


# Convenience functions
def create_aws_session_from_keys(
    access_key_id: str,
    secret_access_key: str,
    region_name: str = "us-east-1",
    session_token: Optional[str] = None
) -> AWSSession:
    """
    Tạo AWS session từ access keys
    
    Args:
        access_key_id: AWS Access Key ID
        secret_access_key: AWS Secret Access Key
        region_name: AWS region
        session_token: AWS Session Token (optional)
    
    Returns:
        AWSSession: Configured AWS session
    """
    aws_session = AWSSession()
    aws_session.create_session(
        access_key_id=access_key_id,
        secret_access_key=secret_access_key,
        session_token=session_token,
        region_name=region_name
    )
    return aws_session


def create_aws_session_from_profile(
    profile_name: str,
    region_name: str = "us-east-1"
) -> AWSSession:
    """
    Tạo AWS session từ AWS profile
    
    Args:
        profile_name: AWS profile name
        region_name: AWS region
    
    Returns:
        AWSSession: Configured AWS session
    """
    aws_session = AWSSession()
    aws_session.create_session(
        profile_name=profile_name,
        region_name=region_name
    )
    return aws_session
