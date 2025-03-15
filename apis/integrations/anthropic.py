"""
Anthropic Claude API Client with AWS Bedrock & Google Vertex AI Support
Supports Claude 3 Haiku, Sonnet, Opus, and Claude 3.5 Sonnet
"""

import os
import base64
import json
import logging
import mimetypes
from typing import List, Dict, Union, Generator, Optional
from dataclasses import dataclass
import boto3
from google.auth.transport.requests import Request
from google.oauth2 import credentials
from anthropic import Anthropic, AsyncAnthropic
from botocore.exceptions import ClientError

logger = logging.getLogger("AnthropicClient")
logger.setLevel(logging.INFO)

@dataclass
class ClaudeModel:
    name: str
    context_window: int
    modalities: List[str]
    cloud_providers: List[str]

class AnthropicClient:
    SUPPORTED_MODELS = {
        "claude-3-haiku-20240307": ClaudeModel(
            "claude-3-haiku-20240307", 200_000, ["text", "image"], ["aws", "google"]
        ),
        "claude-3-sonnet-20240229": ClaudeModel(
            "claude-3-sonnet-20240229", 200_000, ["text", "image"], ["aws", "google"]
        ),
        "claude-3-opus-20240229": ClaudeModel(
            "claude-3-opus-20240229", 200_000, ["text", "image"], ["aws", "google"]
        ),
        "claude-3.5-sonnet-20240620": ClaudeModel(
            "claude-3.5-sonnet-20240620", 1_000_000, ["text", "image", "code"], ["aws", "google"]
        )
    }

    def __init__(self, cloud_provider: str = "aws", **kwargs):
        """
        Initialize Claude client for specified cloud provider
        
        Args:
            cloud_provider: 'aws' or 'google'
            aws_region: AWS region (required for AWS)
            google_project: Google Cloud project ID (required for Google)
        """
        self.cloud_provider = cloud_provider
        self.models = self.SUPPORTED_MODELS
        
        if cloud_provider == "aws":
            self.aws_region = kwargs.get("aws_region", "us-west-2")
            self.bedrock = boto3.client(
                service_name="bedrock-runtime",
                region_name=self.aws_region
            )
        elif cloud_provider == "google":
            self.google_project = kwargs.get("google_project")
            self.credentials = self._authenticate_google()
            self.client = AnthropicVertex(credentials=self.credentials, project_id=self.google_project)
        else:
            raise ValueError("Unsupported cloud provider. Choose 'aws' or 'google'")

    def _authenticate_google(self):
        """Authenticate with Google Cloud credentials"""
        creds = credentials.ApplicationDefault()
        creds.refresh(Request())
        return creds

    def _encode_image(self, image_path: str) -> Dict:
        """Encode image for multimodal requests"""
        with open(image_path, "rb") as image_file:
            return {
                "type": "base64",
                "media_type": mimetypes.guess_type(image_path)[0],
                "data": base64.b64encode(image_file.read()).decode("utf-8")
            }

    def create_message(
        self,
        model: str,
        messages: List[Dict],
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        stream: bool = False
    ) -> Union[Dict, Generator]:
        """
        Create message with Claude API
        
        Args:
            model: Model ID from SUPPORTED_MODELS
            messages: Conversation history
            system: System prompt
            max_tokens: Maximum response length
            temperature: Creativity parameter (0-1)
            stream: Enable streaming response
        """
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(f"Unsupported model. Choose from: {list(self.SUPPORTED_MODELS.keys())}")

        if self.cloud_provider == "aws":
            return self._aws_request(model, messages, system, max_tokens, temperature, stream)
        else:
            return self._google_request(model, messages, system, max_tokens, temperature, stream)

    def _aws_request(self, model, messages, system, max_tokens, temperature, stream):
        """Handle AWS Bedrock API request"""
        params = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature
        }

        if system:
            params["system"] = system

        try:
            if stream:
                response = self.bedrock.invoke_model_with_response_stream(
                    modelId=model,
                    body=json.dumps(params)
                )
                return self._handle_aws_stream(response)
            else:
                response = self.bedrock.invoke_model(
                    modelId=model,
                    body=json.dumps(params)
                )
                return json.loads(response["body"].read())
        except ClientError as e:
            logger.error(f"AWS API error: {e.response['Error']['Message']}")
            raise

    def _google_request(self, model, messages, system, max_tokens, temperature, stream):
        """Handle Google Vertex AI request"""
        params = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": messages,
            "temperature": temperature,
            "system": system
        }

        try:
            if stream:
                return self.client.messages.stream(**params)
            else:
                return self.client.messages.create(**params)
        except Exception as e:
            logger.error(f"Google API error: {str(e)}")
            raise

    def _handle_aws_stream(self, response):
        """Process AWS Bedrock streaming response"""
        for event in response.get("body"):
            chunk = json.loads(event["chunk"]["bytes"])
            if chunk["type"] == "content_block_delta":
                yield chunk["delta"]["text"]

    def validate_message_structure(self, messages: List[Dict]) -> bool:
        """Validate conversation history format"""
        required_keys = {"role", "content"}
        valid_roles = {"user", "assistant"}
        
        for idx, message in enumerate(messages):
            if not all(key in message for key in required_keys):
                return False
            if message["role"] not in valid_roles:
                return False
            if idx == 0 and message["role"] != "user":
                return False
        return True

    async def async_create_message(self, **kwargs):
        """Async message creation"""
        aclient = AsyncAnthropic()
        return await aclient.messages.create(**kwargs)

class AnthropicVertex(Anthropic):
    """Google Vertex AI integration"""
    def __init__(self, credentials, project_id: str, region: str = "us-central1"):
        base_url = f"https://{region}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{region}/publishers/anthropic/models"
        super().__init__(
            api_key="unused",
            base_url=base_url,
            auth_headers={"Authorization": f"Bearer {credentials.token}"}
        )

# Example Usage
if __name__ == "__main__":
    # AWS Example
    aws_client = AnthropicClient(cloud_provider="aws", aws_region="us-west-2")
    
    response = aws_client.create_message(
        model="claude-3.5-sonnet-20240620",
        messages=[{
            "role": "user",
            "content": [
                {"type": "text", "text": "Describe this image"},
                {"type": "image", "source": aws_client._encode_image("photo.jpg")}
            ]
        }],
        max_tokens=1000,
        temperature=0.7
    )
    
    print(response["content"][0]["text"])
    
    # Google Example
    google_client = AnthropicClient(
        cloud_provider="google", 
        google_project="your-google-project"
    )
    
    stream_response = google_client.create_message(
        model="claude-3-sonnet-20240229",
        messages=[{
            "role": "user",
            "content": "Write a short poem about technology"
        }],
        stream=True
    )
    
    # Process streaming response
    for chunk in stream_response:
        print(chunk, end="", flush=True)
    
    # Async example
    import asyncio
    
    async def run_async_example():
        client = AnthropicClient()
        response = await client.async_create_message(
            model="claude-3-opus-20240229",
            messages=[{
                "role": "user",
                "content": "Explain quantum computing in simple terms"
            }],
            max_tokens=500
        )
        print(response.content[0].text)
    
    # Uncomment to run async example
    # asyncio.run(run_async_example())
