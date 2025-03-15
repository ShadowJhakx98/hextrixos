"""
Perplexity AI API Client with Streaming Support
Compatible with OpenAI SDK format
"""

import os
from openai import OpenAI, APIError
from typing import Generator, Union

class PerplexityClient:
    def __init__(self, api_key: str = None):
        """
        Initialize Perplexity client
        
        Args:
            api_key (str): Perplexity API key. Defaults to os.environ["PERPLEXITY_API_KEY"]
        """
        self.api_key = api_key or os.getenv("PERPLEXITY_API_KEY")
        if not self.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.perplexity.ai"
        )
        
        self.supported_models = [
            "mistral-7b-instruct",
            "llama-2-13b-chat",
            "llama-2-70b-chat",
            "codellama-34b-instruct",
            "pplx-7b-online",
            "pplx-70b-online",
            "pplx-7b-chat",
            "pplx-70b-chat",
            "mixtral-8x7b-instruct"
        ]

    def generate(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> Union[str, Generator]:
        """
        Generate completion from Perplexity API
        
        Args:
            model (str): Model name from supported_models
            messages (list): List of message dictionaries
            temperature (float): Creativity parameter (0-1)
            max_tokens (int): Maximum response length
            stream (bool): Enable streaming response
            
        Returns:
            Union[str, Generator]: Full response or streaming generator
        """
        try:
            if model not in self.supported_models:
                raise ValueError(f"Unsupported model. Choose from: {self.supported_models}")

            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )

            if stream:
                return self._stream_response(response)
            else:
                return response.choices[0].message.content

        except APIError as e:
            print(f"API Error: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _stream_response(self, response_stream) -> Generator:
        """
        Handle streaming responses
        
        Args:
            response_stream: Streaming response object
            
        Yields:
            str: Response chunks
        """
        try:
            for chunk in response_stream:
                content = chunk.choices[0].delta.content
                if content:
                    yield content
        except Exception as e:
            print(f"Stream Error: {e}")
            yield ""

if __name__ == "__main__":
    # Example usage
    client = PerplexityClient()
    
    # Regular completion
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is quantum computing?"}
    ]
    
    response = client.generate(
        model="mistral-7b-instruct",
        messages=messages
    )
    print("Regular Response:")
    print(response)
    
    # Streaming completion
    print("\nStreaming Response:")
    stream = client.generate(
        model="llama-2-70b-chat",
        messages=messages,
        stream=True
    )
    
    for chunk in stream:
        print(chunk, end="", flush=True)
