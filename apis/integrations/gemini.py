"""
Google Gemini API Client (v1.5-2.0) with Full Multimodal Support
"""

import os
import json
import websockets
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from typing import Union, Generator, AsyncGenerator
import base64
import mimetypes

class GeminiClient:
    def __init__(self, credentials_path: str = None):
        self.credentials = self._authenticate(credentials_path)
        self.base_url = "https://generativelanguage.googleapis.com/v2beta"
        self.live_api_url = "wss://generativelanguage.googleapis.com/v2beta/models/{model}:streamGenerateContent"
        
        # Model configurations from search results
        self.models = {
            '2.0-flash': {
                'id': 'gemini-2.0-flash',
                'modes': ['text', 'image', 'audio', 'video'],
                'max_input_tokens': 1_000_000,
                'max_output_tokens': 8_000,
                'supports_live': True
            },
            '2.0-pro': {
                'id': 'gemini-2.0-pro-exp-02-05',
                'modes': ['text', 'code', 'knowledge'],
                'max_input_tokens': 2_000_000,
                'max_output_tokens': 8_192,
                'supports_live': False
            },
            '1.5-flash': {
                'id': 'gemini-1.5-flash',
                'modes': ['text', 'image', 'audio'],
                'max_input_tokens': 128_000,
                'max_output_tokens': 4_096,
                'supports_live': False
            },
            '1.5-pro': {
                'id': 'gemini-1.5-pro',
                'modes': ['text', 'code', 'reasoning'],
                'max_input_tokens': 1_000_000,
                'max_output_tokens': 8_192,
                'supports_live': False
            }
        }

    def _authenticate(self, credentials_path: str) -> Credentials:
        """Authenticate using service account credentials"""
        scopes = ['https://www.googleapis.com/auth/cloud-platform']
        credentials = Credentials.from_service_account_file(
            credentials_path or os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=scopes
        )
        if not credentials.valid:
            credentials.refresh(Request())
        return credentials

    def _build_content(self, content: Union[str, bytes], mime_type: str) -> dict:
        """Convert content to Gemini API format"""
        if isinstance(content, str):
            if mime_type.startswith('text'):
                return {'text': content}
            elif mime_type.startswith('image'):
                with open(content, 'rb') as f:
                    data = base64.b64encode(f.read()).decode('utf-8')
                return {'mime_type': mime_type, 'data': data}
        elif isinstance(content, bytes):
            return {'mime_type': mime_type, 'data': base64.b64encode(content).decode('utf-8')}
        return {}

    async def generate_content(
        self,
        model: str = '2.0-flash',
        inputs: list = None,
        tools: list = None,
        stream: bool = False,
        search: bool = False,
        **kwargs
    ) -> Union[dict, AsyncGenerator]:
        """
        Generate content with Gemini models
        
        Args:
            model: Model version (2.0-flash, 2.0-pro, 1.5-flash, 1.5-pro)
            inputs: List of input content (text, images, audio, video)
            tools: List of function tools to use
            stream: Enable streaming response
            search: Enable Google Search grounding
        """
        model_config = self.models.get(model)
        if not model_config:
            raise ValueError(f"Invalid model. Choose from: {list(self.models.keys())}")

        payload = {
            'contents': [{
                'parts': [self._build_content(inp, mimetypes.guess_type(str(inp))[0]) 
                         for inp in inputs]
            }],
            'generationConfig': {
                'maxOutputTokens': model_config['max_output_tokens'],
                **kwargs
            }
        }

        if tools:
            payload['tools'] = tools
        if search:
            payload['groundingConfig'] = {'sources': ['google-search']}

        if stream and model_config['supports_live']:
            return self._stream_live_api(model_config['id'], payload)
        else:
            return await self._make_request(model_config['id'], payload, stream)

    async def _make_request(self, model_id: str, payload: dict, stream: bool) -> dict:
        """Handle standard API requests"""
        headers = {
            'Authorization': f'Bearer {self.credentials.token}',
            'Content-Type': 'application/json'
        }
        
        params = {'alt': 'json'}
        if stream:
            params['alt'] = 'media'

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/models/{model_id}:generateContent",
                headers=headers,
                params=params,
                json=payload
            )
            return response.json() if not stream else self._handle_stream(response)

    async def _stream_live_api(self, model_id: str, payload: dict) -> AsyncGenerator:
        """Handle Multimodal Live API WebSocket connection"""
        url = self.live_api_url.format(model=model_id)
        headers = {'Authorization': f'Bearer {self.credentials.token}'}
        
        async with websockets.connect(url, extra_headers=headers) as ws:
            await ws.send(json.dumps(payload))
            async for message in ws:
                yield json.loads(message)

    def _handle_stream(self, response):
        """Handle streaming response chunks"""
        for chunk in response.iter_bytes():
            yield json.loads(chunk.decode('utf-8'))

    # Additional features from search results
    async def generate_image(self, prompt: str, resolution: str = '1024x1024'):
        """Use Gemini 2.0 Flash's native image generation"""
        return await self.generate_content(
            model='2.0-flash',
            inputs=[prompt],
            output_mime='image/png',
            image_generation_config={
                'resolution': resolution,
                'guidance_scale': 7.5
            }
        )

    async def text_to_speech(self, text: str, language: str = 'en-US'):
        """Convert text to speech using 2.0 Flash TTS"""
        return await self.generate_content(
            model='2.0-flash',
            inputs=[text],
            output_mime='audio/mpeg',
            tts_config={
                'language': language,
                'voice_preset': 'neutral'
            }
        )

# Usage Example
async def main():
    client = GeminiClient(credentials_path="service-account.json")
    
    # Text generation example
    response = await client.generate_content(
        model='2.0-flash',
        inputs=["Explain quantum computing in simple terms"],
        temperature=0.7
    )
    print(response['candidates'][0]['content']['parts'][0]['text'])
    
    # Live API streaming example
    async for chunk in client.generate_content(
        model='2.0-flash',
        inputs=["Describe a sunset in real time"],
        stream=True
    ):
        print(chunk['text'], end='', flush=True)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
