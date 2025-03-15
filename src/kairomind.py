"""
jarvis.py

Implements the "JARVIS" class that integrates everything:
 - GeminiMode (for real-time streaming to Gemini 2.0)
 - LocalNoGeminiMode fallback
 - UIAutomator for Android
 - CodeImprover
 - PlannerAgent
 - SpecializedSubAgent
 - VectorDatabase
 - GeminiAPIDocReference
 - Optionally JARVISAlexaSkill usage

Plus streaming commands for audio/video. No duplication.
"""

import logging
import wave
import spacy
import pyttsx3
import openai

from anthropic import Anthropic
from ethics import EthicalFramework
from emotions import EmotionSystem
from mem_drive import MemoryDriveManager
from code_chunking import CodeChunker
from self_awareness import SelfAwareness
# Modules for your advanced features (split out into separate files):
from ui_automator import UIAutomator
from code_improver import CodeImprover
from planner_agent import PlannerAgent
from specialized_sub_agent import SpecializedSubAgent
from vector_database import VectorDatabase
from gemini_api_doc_reference import GeminiAPIDocReference

# The streaming logic is in these two:
from gemini_mode import GeminiMode
from local_mode import LocalNoGeminiMode

logger = logging.getLogger("JARVIS")
logger.setLevel(logging.INFO)

class JARVIS:
    """
    A single, unified JARVIS class that:

     1) Has real-time streaming commands for Gemini or local fallback
     2) Imports advanced modules (UIAutomator, CodeImprover, PlannerAgent, etc.)
     3) Provides a `process_command()` entry point
    """

    def __init__(self, config: dict):
        self.config = config

        # Set up spacy, TTS, etc.
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        if voices:
            self.engine.setProperty('voice', voices[0].id)
        self.nlp = spacy.load("en_core_web_sm")

        # Gemini or local fallback
        self.gemini_key = config.get("GEMINI_API_KEY", "")
        self.gemini_mode = GeminiMode(api_key=self.gemini_key)
        self.local_mode = LocalNoGeminiMode()

        # Other advanced modules
        self.ui_automator = UIAutomator()
        self.ui_automator.load_device()
        try:
            self.ui_automator.load_snippet()
        except Exception as e:
            logger.warning(f"UIAutomator snippet load failed: {e}")

        self.code_improver = CodeImprover([])
        self.planner_agent = PlannerAgent()
        self.sub_agents = [
            SpecializedSubAgent("DevAgent", "Software Development"),
            SpecializedSubAgent("MusicAgent", "Music Composition"),
            SpecializedSubAgent("HomeAgent", "Home Automation"),
        ]
        self.vector_db = VectorDatabase()
        self.gemini_doc_ref = GeminiAPIDocReference()

        # Optionally some Claude usage
        self.anthropic = Anthropic(api_key=config.get("CLAUDE_API_KEY", ""))

        # (Home Assistant, HomeKit, Alexa, etc. could go here)

        # Merge all commands (including streaming) into one dict
        self.command_handlers = {
            # Streaming logic from old partial jarvis
            "stream audio gemini": self.cmd_stream_audio_gemini,
            "stream video gemini": self.cmd_stream_video_gemini,
            "stream audio local": self.cmd_stream_audio_local,
            "stream video local": self.cmd_stream_video_local,
            "gemini text": self.cmd_gemini_text,
            "local text": self.cmd_local_text,

            # Additional example command for docs
            "docs gemini": self.show_gemini_docs,
            # ... any others ...
        }
        # Ethics
        self.ethics = EthicalFramework(self)
        # Emotions
        self.emotions = EmotionSystem()
        # Memory drive
        self.mem_drive = MemoryDriveManager()
        self.mem_drive.initialize_memory()
        self.mem_drive.initialize_drive_service()
        # Code chunking
        self.chunker = CodeChunker()
        # Self awareness
        self.self_awareness = SelfAwareness(self)
    def speak(self, text: str):
        print(f"JARVIS: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
    def introspect(self):
        # return the source code of JARVIS
        import inspect
        return inspect.getsource(self.__class__)


    async def process_command(self, command: str) -> str:
        """
        Called by your main loop or Alexa or whoever. 
        We look up command in self.command_handlers. 
        """
        cmd_lower = command.lower().strip()
        for key, handler in self.command_handlers.items():
            if key in cmd_lower:
                return await handler(command)
        return f"I am not sure how to handle: {command}"

    ########################################
    # The streaming commands from your old partial jarvis
    ########################################

    async def cmd_stream_audio_gemini(self, _cmd):
        """
        Real-time streaming from mic to Gemini:
         - Print partial text
         - Write partial audio to wave file
        """
        out_wave = wave.open("gemini_partial_output.wav", "wb")
        out_wave.setnchannels(1)
        out_wave.setsampwidth(2)  # 16-bit
        out_wave.setframerate(24000)

        try:
            async for partial in self.gemini_mode.audio_stream(response_modalities=["TEXT", "AUDIO"]):
                if isinstance(partial, str):
                    print("Gemini partial text:", partial)
                else:
                    # partial is raw PCM from the model
                    out_wave.writeframes(partial)
        finally:
            out_wave.close()
        return "Finished streaming audio to Gemini."

    async def cmd_stream_video_gemini(self, _cmd):
        """
        Streams webcam to Gemini, prints partial text from model.
        """
        async for partial_text in self.gemini_mode.video_stream(response_modalities=["TEXT"]):
            print("Gemini partial text from video:", partial_text)
        return "Finished streaming video to Gemini."

    async def cmd_stream_audio_local(self, _cmd):
        """
        Just read local mic chunks, store them in a wave file, no LLM usage.
        """
        out_wave = wave.open("local_mic_record.wav", "wb")
        out_wave.setnchannels(1)
        out_wave.setsampwidth(2)
        out_wave.setframerate(16000)

        async for chunk in self.local_mode.local_audio_stream():
            out_wave.writeframes(chunk)
        out_wave.close()
        return "Recorded local mic to local_mic_record.wav"

    async def cmd_stream_video_local(self, _cmd):
        """
        Reads local webcam, stores frames as images for demonstration.
        """
        idx = 0
        async for frame in self.local_mode.local_video_stream():
            with open(f"local_frame_{idx}.jpg", "wb") as f:
                f.write(frame)
            idx += 1
            if idx > 10:
                break
        return "Stored 10 frames from local webcam to local_frame_x.jpg"

    ########################################
    # Also from old partial jarvis: text-based calls
    ########################################

    async def cmd_gemini_text(self, cmd):
        prompt = cmd.replace("gemini text", "").strip()
        result = await self.gemini_mode.text_to_text(prompt)
        return f"Gemini says: {result}"

    async def cmd_local_text(self, cmd):
        prompt = cmd.replace("local text", "").strip()
        result = await self.local_mode.text_to_text(prompt)
        return f"Local GPT-2 says: {result}"

    ########################################
    # Example command for referencing the doc snippet
    ########################################

    async def show_gemini_docs(self, _cmd):
        docs = self.gemini_doc_ref.show_docs()
        return docs

    ########################################
    # If you want Alexa logic
    ########################################
    async def process_alexa_command(self, intent_name: str) -> str:
        return f"Got Alexa intent: {intent_name}"
#placeholder implement later
# jarvis.py
# from toy_web_search import toy_web_search
# from toy_text_gen import ToyTextGenerator
# from toy_text_to_image import ToyTextToImage
# from toy_tts import ToyTTS

# # Then in JARVIS, create or store references:
# class JARVIS:
#     def __init__(self, config):
#         # ...
#         self.web_searcher = toy_web_search
#         self.text_gen = ToyTextGenerator()
#         self.text_to_image = ToyTextToImage()
#         self.tts = ToyTTS()
#         # Possibly also load your advanced CIFAR-10 model here
#         # etc.

#     def process_command(self, command):
#         cmd_lower = command.lower()
#         if "search" in cmd_lower:
#             query = cmd_lower.replace("search","").strip()
#             results = self.web_searcher(query)
#             return results
#         elif "generate text" in cmd_lower:
#             seed = cmd_lower.replace("generate text","").strip()
#             return self.text_gen.generate_text(seed, 5)
#         elif "generate image" in cmd_lower:
#             prompt = cmd_lower.replace("generate image","").strip()
#             out = self.text_to_image.text_to_image(prompt)
#             return f"Generated image shape: {out.shape}"
#         elif "speak" in cmd_lower:
#             text = cmd_lower.replace("speak","").strip()
#             self.tts.speak(text)
#             return "Spoke your text (toy)."
#         elif "classify image" in cmd_lower:
#             # integrate your CIFAR-10 model calls
#             return "Use advanced image classification logic"
#         else:
#             return "Unknown command"
