"""
jarvis_alexa_skill.py

Contains the JARVISAlexaSkill class for Alexa skill integration.
"""

import asyncio
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_model import Response

# We assume your 'JARVIS' is in jarvis.py. 
# You can do a forward reference or import if needed:
# from jarvis import JARVIS

class JARVISAlexaSkill(AbstractRequestHandler):
    """Basic Alexa skill integration for JARVIS."""
    def can_handle(self, handler_input: HandlerInput) -> bool:
        return True

    def handle(self, handler_input: HandlerInput) -> Response:
        # In practice, you'd reference a global or pass JARVIS instance around
        # or re-instantiate it:
        from jarvis import JARVIS  # to avoid circular import
        jarvis = JARVIS({})
        intent_name = handler_input.request_envelope.request.intent.name
        speech_text = asyncio.run(jarvis.process_alexa_command(intent_name))
        return handler_input.response_builder.speak(speech_text).response
