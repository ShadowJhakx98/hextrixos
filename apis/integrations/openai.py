"""
OpenAI API Client with Full Model Support (GPT-3.5 to O3/Omni)
"""

import os
import json
from typing import Generator, Union, Optional
from openai import OpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
import httpx

class OpenAIClient:
    def __init__(self, api_key: str = None, organization: str = None, project: str = None):
        """
        Initialize OpenAI client with enhanced model support
        
        Args:
            api_key: OpenAI API key (default: OPENAI_API_KEY environment variable)
            organization: Organization ID for usage tracking
            project: Project ID for usage tracking
        """
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            organization=organization,
            project=project,
            timeout=httpx.Timeout(30.0, connect=60.0)
        )
        self.async_client = AsyncOpenAI(api_key=api_key)
        
        # Model configurations from search results
        self.models = {
            'gpt-3.5-turbo': {
                'context_window': 16_385,
                'modalities': ['text'],
                'streaming': True
            },
            'gpt-4': {
                'context_window': 128_000,
                'modalities': ['text', 'image'],
                'streaming': True
            },
            'gpt-4o': {
                'context_window': 1_000_000,
                'modalities': ['text', 'image', 'audio', 'video'],
                'streaming': True
            },
            'gpt-4o-mini': {
                'context_window': 256_000,
                'modalities': ['text', 'image'],
                'streaming': True
            },
            'o1-mini': {
                'context_window': 512_000,
                'modalities': ['text', 'code'],
                'streaming': True
            },
            'o3': {
                'context_window': 2_000_000,
                'modalities': ['text', 'image', 'audio', 'video', 'code'],
                'streaming': True
            },
            'gpt-omni': {
                'context_window': 4_000_000,
                'modalities': ['text', 'image', 'audio', 'video', '3d'],
                'streaming': True
            }
        }

    def get_supported_models(self) -> list:
        """Return list of supported models"""
        return list(self.models.keys())

    def generate(
        self,
        model: str,
        messages: list,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        stream: bool = False
    ) -> Union[ChatCompletion, Generator]:
        """
        Unified generation interface for all models
        
        Args:
            model: Model name from supported_models
            messages: List of message dictionaries
            temperature: Creativity parameter (0-2)
            max_tokens: Maximum response length
            stream: Enable streaming response
            
        Returns:
            ChatCompletion or stream generator
        """
        if model not in self.models:
            raise ValueError(f"Unsupported model. Choose from: {self.get_supported_models()}")

        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }

        if stream:
            return self._handle_stream(self.client.chat.completions.create(**params))
        else:
            return self.client.chat.completions.create(**params)

    def _handle_stream(self, stream) -> Generator:
        """Process streaming responses"""
        try:
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            raise OpenAIError(f"Stream error: {str(e)}") from e

    async def async_generate(self, model: str, messages: list, **kwargs) -> ChatCompletion:
        """Async generation interface"""
        return await self.async_client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs
        )

    def create_speech(
        self,
        text: str,
        model: str = "tts-1-hd",
        voice: str = "alloy",
        speed: float = 1.0
    ) -> bytes:
        """
        Convert text to speech
        
        Args:
            text: Input text (max 4096 chars)
            model: tts-1 or tts-1-hd
            voice: alloy, echo, fable, onyx, nova, shimmer
            speed: 0.25 to 4.0
            
        Returns:
            Audio bytes in MP3 format
        """
        response = self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text,
            speed=speed
        )
        return response.content

    def create_transcription(
        self,
        audio_file: Union[str, bytes],
        model: str = "whisper-1",
        language: str = "en"
    ) -> str:
        """
        Transcribe audio to text
        
        Args:
            audio_file: Path to audio file or bytes
            model: whisper-1
            language: ISO 639-1 language code
            
        Returns:
            Transcribed text
        """
        if isinstance(audio_file, str):
            audio_file = open(audio_file, "rb")
            
        return self.client.audio.transcriptions.create(
            file=audio_file,
            model=model,
            language=language
        ).text

    def get_rate_limits(self) -> dict:
        """Get current rate limit status"""
        return {
            'requests_remaining': self.client._retrieve_headers().get('x-ratelimit-remaining-requests'),
            'tokens_remaining': self.client._retrieve_headers().get('x-ratelimit-remaining-tokens'),
            'reset_time': self.client._retrieve_headers().get('x-ratelimit-reset')
        }

    def validate_model(self, model: str, modality: str) -> bool:
        """Check if model supports specific modality"""
        return modality in self.models.get(model, {}).get('modalities', [])

class OpenAIError(Exception):
    """Custom exception for OpenAI API errors"""
    def __init__(self, message: str, status_code: int = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

# Example Usage
if __name__ == "__main__":
    client = OpenAIClient()
    
    # Text Generation
    response = client.generate(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Explain quantum computing"}]
    )
    print(response.choices[0].message.content)
    
    # Streaming
    stream = client.generate(
        model="gpt-4o",
        messages=[{"role": "user", "content": "Tell me a story"}],
        stream=True
    )
    for chunk in stream:
        print(chunk, end="", flush=True)
    
    # Audio Generation
    speech = client.create_speech("Hello world!")
    with open("hello.mp3", "wb") as f:
        f.write(speech)
    
    # Transcription
    text = client.create_transcription("audio.mp3")
    print(f"Transcribed: {text}")
