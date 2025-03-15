"""
gemini_api_doc_reference.py

Contains the GeminiAPIDocReference class to store/present 
Gemini 2.0 docs as requested.
"""

GEMINI_DOCS_SNIPPET = r"""
Gemini 2.0 Flash Experimental Docs:
Multimodal Live API, Thinking Mode, bounding box detection, 
speech generation, etc.

(Insert your entire doc snippet from the conversation here.)
"""

class GeminiAPIDocReference:
    """Stores or returns the Gemini 2.0 documentation snippet as needed."""

    def __init__(self):
        self.raw_docs = GEMINI_DOCS_SNIPPET

    def show_docs(self):
        return self.raw_docs
