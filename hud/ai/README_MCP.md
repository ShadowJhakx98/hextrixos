# Model Context Protocol (MCP) Integration

This module integrates various external services into the Hextrix HUD through the Model Context Protocol framework.

## Features

- **Trieve RAG**: Semantic search using the Trieve Retrieval Augmented Generation system
- **Perplexity API**: Deep research capabilities with realtime web information
- **Google Search**: Web search functionality via SerpAPI
- **News API**: News search and retrieval
- **File System Operations**: Local file search and management
- **App Management**: Native, Windows, and Android app control (when available)

## Setup

1. Install required dependencies:

```bash
pip install requests logging openai
```

2. Set up API keys in `credentials2.json` file located in the `hud` directory:

```json
{
  "api_keys": {
    "trieve_api_key": "YOUR_TRIEVE_API_KEY_HERE",
    "trieve_dataset_id": "YOUR_TRIEVE_DATASET_ID_HERE",
    "perplexity": "YOUR_PERPLEXITY_API_KEY_HERE",
    "serp": "YOUR_SERPAPI_API_KEY_HERE",
    "newsapi_api_key": "YOUR_NEWSAPI_API_KEY_HERE"
  }
}
```

## API Key Registration

- **Trieve**: Sign up at [https://trieve.ai](https://trieve.ai)
- **Perplexity**: Get API access at [https://docs.perplexity.ai](https://docs.perplexity.ai)
- **SerpAPI**: Register at [https://serpapi.com](https://serpapi.com)
- **NewsAPI**: Register at [https://newsapi.org](https://newsapi.org)

## Usage

### In the MCP Panel

Use special prefixes for advanced search:

- `news:` - Search news articles (e.g., `news:climate change`)
- `web:` - Search the web (e.g., `web:python tutorials`)
- `research:` - Deep research on a topic (e.g., `research:quantum computing`)
- `rag:` - Search knowledge base with RAG (e.g., `rag:company policies`)

### Voice Commands

The system also supports natural language voice commands:

- "Find news about [topic]"
- "Search the web for [query]"
- "Research [topic]"
- "Use RAG to search for [query]"

## Troubleshooting

- Check that API keys are correctly set in `credentials2.json`
- Ensure internet connectivity for external service access
- Look for error messages in the application logs 