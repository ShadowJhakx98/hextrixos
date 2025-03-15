import os
from typing import Dict, Any, Optional, Union, List

# Import all the clients
from apis.integrations.anthropic import AnthropicClient
from apis.integrations.gemini import GeminiClient
from apis.integrations.openai import OpenAIClient
from apis.integrations.perplexity import PerplexityClient
from apis.integrations.google import MedicalImagingAPI, LensAPI
from apis.content_validator import app as content_validator_app
import httpx
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("APIManager")

class APIManager:
    """
    Unified API Manager for managing different AI service clients
    """
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the API Manager
        
        Args:
            config_path: Optional path to config file with API keys
        """
        # Load credentials from environment or config file
        self.credentials = self._load_credentials(config_path)
        self.clients = {}
        self.default_models = {
            'anthropic': 'claude-3.5-sonnet-20240620',
            'openai': 'gpt-4o',
            'gemini': '2.0-flash',
            'perplexity': 'pplx-70b-online'
        }
        self._content_validator_url = os.getenv('CONTENT_VALIDATOR_URL', 'http://localhost:8000')
        
    def _load_credentials(self, config_path: Optional[str]) -> Dict[str, str]:
        """Load credentials from environment variables or config file"""
        if config_path:
            try:
                import json
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Failed to load config from {config_path}: {e}")
                
        # Fall back to environment variables
        return {
            'google': os.getenv('GOOGLE_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY'),
            'perplexity': os.getenv('PERPLEXITY_API_KEY'),
            'aws_region': os.getenv('AWS_REGION', 'us-west-2'),
            'google_project': os.getenv('GOOGLE_PROJECT_ID')
        }
    
    def get_client(self, service_name: str, **kwargs) -> Any:
        """
        Get or create a client for the specified service
        
        Args:
            service_name: Name of the service ('anthropic', 'openai', 'gemini', 'perplexity')
            **kwargs: Additional arguments for client initialization
            
        Returns:
            Initialized client instance
        """
        if service_name not in self.clients:
            if service_name == 'anthropic':
                # Handle cloud provider selection for Anthropic
                cloud_provider = kwargs.get('cloud_provider', 'aws')
                self.clients[service_name] = AnthropicClient(
                    cloud_provider=cloud_provider,
                    aws_region=self.credentials.get('aws_region'),
                    google_project=self.credentials.get('google_project')
                )
            elif service_name == 'openai':
                self.clients[service_name] = OpenAIClient(
                    api_key=self.credentials.get('openai'),
                    organization=kwargs.get('organization'),
                    project=kwargs.get('project')
                )
            elif service_name == 'gemini':
                self.clients[service_name] = GeminiClient(
                    credentials_path=kwargs.get('credentials_path')
                )
            elif service_name == 'perplexity':
                self.clients[service_name] = PerplexityClient(
                    api_key=self.credentials.get('perplexity')
                )
            elif service_name == 'medical_imaging':
                self.clients[service_name] = MedicalImagingAPI(
                    project_id=self.credentials.get('google_project')
                )
            elif service_name == 'lens':
                self.clients[service_name] = LensAPI()
            else:
                raise ValueError(f"Unsupported service: {service_name}")
                
        return self.clients[service_name]
    
    async def generate(
        self, 
        service_name: str, 
        prompt: Union[str, List[Dict[str, Any]]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False,
        **kwargs
    ) -> Any:
        """
        Unified interface for generating content across different services
        
        Args:
            service_name: Name of the service to use
            prompt: Text prompt or message list
            model: Model name (defaults to service's default model)
            temperature: Temperature parameter for generation
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional service-specific parameters
            
        Returns:
            Generated content in the format of the service
        """
        client = self.get_client(service_name)
        model = model or self.default_models.get(service_name)
        
        # Convert simple string prompts to message format if needed
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt
            
        if service_name == 'anthropic':
            system = kwargs.get('system')
            return client.create_message(
                model=model,
                messages=messages,
                system=system,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream
            )
        elif service_name == 'openai':
            return client.generate(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
        elif service_name == 'gemini':
            # Handle Gemini's different input format
            inputs = [m.get('content') for m in messages if m.get('role') == 'user']
            return await client.generate_content(
                model=model,
                inputs=inputs,
                temperature=temperature,
                stream=stream,
                **kwargs
            )
        elif service_name == 'perplexity':
            return client.generate(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
        else:
            raise ValueError(f"Generation not supported for service: {service_name}")
    
    async def validate_content(self, file_path: str) -> Dict[str, Any]:
        """
        Validate content using the content validator API
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Validation results
        """
        async with httpx.AsyncClient() as client:
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f)}
                response = await client.post(
                    f"{self._content_validator_url}/validate", 
                    files=files
                )
                return response.json()
    
    def get_supported_models(self, service_name: str) -> List[str]:
        """Get list of supported models for a service"""
        client = self.get_client(service_name)
        
        if service_name == 'anthropic':
            return list(client.SUPPORTED_MODELS.keys())
        elif service_name == 'openai':
            return client.get_supported_models()
        elif service_name == 'gemini':
            return list(client.models.keys())
        elif service_name == 'perplexity':
            return client.supported_models
        else:
            return []
    
    def create_multi_service_chat(self, services: List[str] = None):
        """
        Create a multi-service chat that can dynamically switch between services
        
        Args:
            services: List of services to include
            
        Returns:
            MultiServiceChat instance
        """
        if not services:
            services = ['anthropic', 'openai', 'gemini', 'perplexity']
        
        return MultiServiceChat(self, services)

class MultiServiceChat:
    """
    Chat interface that can dynamically switch between different AI services
    """
    def __init__(self, api_manager: APIManager, services: List[str]):
        self.api_manager = api_manager
        self.services = services
        self.current_service = services[0]
        self.conversation_history = []
        self.service_histories = {service: [] for service in services}
    
    def set_service(self, service_name: str):
        """Switch to a different service"""
        if service_name in self.services:
            self.current_service = service_name
        else:
            raise ValueError(f"Service {service_name} not configured")
    
    async def send_message(
        self, 
        message: str, 
        service_name: Optional[str] = None,
        model: Optional[str] = None,
        stream: bool = False
    ) -> Any:
        """
        Send a message to the current or specified service
        
        Args:
            message: Message text
            service_name: Optional service to use (overrides current)
            model: Optional model to use
            stream: Whether to stream the response
            
        Returns:
            Response from the service
        """
        service = service_name or self.current_service
        
        # Add to conversation history
        self.conversation_history.append({"role": "user", "content": message})
        self.service_histories[service].append({"role": "user", "content": message})
        
        # Get response
        response = await self.api_manager.generate(
            service_name=service,
            prompt=self.service_histories[service],
            model=model,
            stream=stream
        )
        
        # Add response to history if not streaming
        if not stream:
            response_text = self._extract_response_text(service, response)
            self.conversation_history.append({"role": "assistant", "content": response_text})
            self.service_histories[service].append({"role": "assistant", "content": response_text})
        
        return response
    
    def _extract_response_text(self, service_name: str, response: Any) -> str:
        """Extract text from service-specific response formats"""
        if service_name == 'anthropic':
            return response.get('content', [{}])[0].get('text', '')
        elif service_name == 'openai':
            return response.choices[0].message.content
        elif service_name == 'gemini':
            return response.get('candidates', [{}])[0].get('content', {}).get('parts', [{}])[0].get('text', '')
        elif service_name == 'perplexity':
            return response if isinstance(response, str) else ''
        return str(response)
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get full conversation history across all services"""
        return self.conversation_history
    
    def clear_history(self, service_name: Optional[str] = None):
        """
        Clear conversation history
        
        Args:
            service_name: Optional service to clear (if None, clears all)
        """
        if service_name:
            if service_name in self.service_histories:
                self.service_histories[service_name] = []
        else:
            self.conversation_history = []
            self.service_histories = {service: [] for service in self.services}

# Example usage
async def main():
    # Initialize API manager
    api_manager = APIManager()
    
    # Generate with different services
    openai_response = await api_manager.generate(
        service_name='openai',
        prompt="Explain quantum computing",
        model="gpt-4o"
    )
    
    anthropic_response = await api_manager.generate(
        service_name='anthropic',
        prompt=[{"role": "user", "content": "Explain quantum computing"}],
        model="claude-3.5-sonnet-20240620"
    )
    
    # Multi-service chat example
    chat = api_manager.create_multi_service_chat(['openai', 'anthropic'])
    response = await chat.send_message("What are the latest advancements in AI?")
    
    # Switch service
    chat.set_service('anthropic')
    response = await chat.send_message("Continue explaining the advancements in AI")
    
    print(f"Conversation history: {chat.get_conversation_history()}")

if __name__ == "__main__":
    asyncio.run(main())
