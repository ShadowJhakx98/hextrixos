class APIManager:
    def __init__(self):
        self.credentials = {
            'google': os.getenv('GOOGLE_API_KEY'),
            'openai': os.getenv('OPENAI_API_KEY'),
            'anthropic': os.getenv('ANTHROPIC_API_KEY')
        }
        
    def get_client(self, service_name):
        if service_name == 'gemini':
            return GeminiClient(self.credentials['google'])
        elif service_name == 'openai':
            return OpenAIClient(self.credentials['openai'])
        # Add other services...
        
class GeminiClient:
    def __init__(self, api_key):
        self.client = GenAI(api_key=api_key)
        
    def generate_content(self, prompt):
        return self.client.generate(prompt)
