Updated Documentation Structure
Files Overview

    main.py: Central control file for the Flask app.
    planner_agent.py: Task planning and intent recognition.
    mem_drive.py: Memory and context management.
    specialized_sub_agent.py: Handles OCR, screen capture, and multimodal tasks.
    ui_automator.py: Voice handling and user interface automation.
    gemini_api_doc_reference.py: Documentation for Gemini API integration.
    emotions.py: Sentiment and emotion analysis.
    discord_bot.py: Manages Discord bot interactions.
    ocr_module.py: Dedicated OCR processing.
    tts_module.py: Text-to-speech integration.
    stt_module.py: Speech-to-text integration.
    image_processing.py: Image handling and description.
    gesture_recognition.py: Handles real-time gesture-based interactions.
    lighting_control.py: RGB lighting control for ASUS Aura Sync and Razer Chroma.
    multimodal_manager.py: Multimodal input/output processing.
    audio_streaming.py: Manages real-time audio streaming.
    config.py: Configuration and environment settings.
    logging_utils.py: Centralized logging utilities.
    developer_notes.md: Tips for extending and customizing the system.

Detailed Usage Examples for Each File
1. main.py

Purpose: Central control file managing Flask endpoints and app initialization.

Usage Example:

    Run the Flask app:

python main.py

Query AI:

    curl -X POST http://localhost:5000/query -H "Content-Type: application/json" -d '{"query": "Tell me a joke."}'

2. planner_agent.py

Purpose: Handles task planning and intent recognition.

Usage Example:

from planner_agent import RuleBasedNLU, TaskPlanner

nlu = RuleBasedNLU()
intent = nlu.analyze("Take a screenshot")
print(intent)  # Output: capture_screen

task_planner = TaskPlanner()
tasks = task_planner.plan_task(intent.intent, {})
print(tasks)  # Output: [{'tool': 'capture_screen'}]

3. mem_drive.py

Purpose: Manages conversation memory.

Usage Example:

from mem_drive import MemoryManager

memory = MemoryManager()
memory.add_message("user", "Hello!")
memory.add_message("assistant", "Hi!")
context = memory.get_context()
print(context)

4. specialized_sub_agent.py

Purpose: Handles OCR, screen capture, and other tasks.

Usage Example:

from specialized_sub_agent import ScreenCapture, OCR

# Capture screen
capture = ScreenCapture(config)
screenshot = capture.capture("output.png")

# OCR
ocr = OCR()
text = ocr.extract_text("output.png")
print(text)

5. ui_automator.py

Purpose: Manages TTS and STT.

Usage Example:

from ui_automator import VoiceHandler

voice = VoiceHandler(config)
voice.text_to_speech("Hello, world!")
speech = voice.speech_to_text()
print(speech)

6. gemini_api_doc_reference.py

Purpose: Gemini API documentation and integration reference.

Usage Example:

    Refer to diagrams and examples in the file for real-time API usage.

7. emotions.py

Purpose: Detects emotional states.

Usage Example:

from emotions import detect_emotion

emotion = detect_emotion("I'm so happy today!")
print(emotion)  # Output: happy

8. discord_bot.py

Purpose: Discord bot functionality.

Usage Example:

    Start the bot:

    python discord_bot.py

    Interact via Discord using commands like !join, !leave.

9. ocr_module.py

Purpose: OCR operations.

Usage Example:

from ocr_module import OCR

ocr = OCR()
text = ocr.extract_text("image.jpg")
print(text)

10. tts_module.py

Purpose: Text-to-speech functionality.

Usage Example:

from tts_module import TTS

tts = TTS()
tts.speak("Welcome to the system!")

11. stt_module.py

Purpose: Speech-to-text functionality.

Usage Example:

from stt_module import SpeechRecognizer

stt = SpeechRecognizer()
text = stt.recognize()
print(text)

12. image_processing.py

Purpose: Image handling.

Usage Example:

from image_processing import ImageProcessor

processor = ImageProcessor()
desc = processor.describe("sample.png")
print(desc)

13. gesture_recognition.py

Purpose: Gesture recognition.

Usage Example:

from gesture_recognition import GestureHandler

handler = GestureHandler()
gesture = handler.detect()
print(gesture)

14. lighting_control.py

Purpose: RGB lighting control.

Usage Example:

from lighting_control import RGBController

controller = RGBController()
controller.set_color("happy")

15. multimodal_manager.py

Purpose: Manages multimodal input.

Usage Example:

from multimodal_manager import MultimodalManager

manager = MultimodalManager()
response = manager.process_input(text="Hello!", image="image.png")
print(response)

16. audio_streaming.py

Purpose: Handles real-time audio streaming.

Usage Example:

from audio_streaming import AudioStreamer

streamer = AudioStreamer(config)
streamer.start()

17. config.py

Purpose: Manages configurations.

Usage Example:

    Update environment variables and settings as needed in this file.

18. logging_utils.py

Purpose: Centralized logging.

Usage Example:

from logging_utils import setup_logger

logger = setup_logger()
logger.info("Starting the application.")
