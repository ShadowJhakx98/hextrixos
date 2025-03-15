import logging
import speech_recognition as sr

logger = logging.getLogger(__name__)

class STTHandlerError(Exception):
    """Custom exception for STTHandler errors."""
    pass

class STTHandler:
    """Handles speech-to-text functionalities."""
    def __init__(self, language: str = "en-US"):
        self.recognizer = sr.Recognizer()
        self.language = language

    def speech_to_text(self) -> str:
        """Converts speech from the microphone to text."""
        with sr.Microphone() as source:
            logger.info("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, phrase_time_limit=5)
                text = self.recognizer.recognize_google(audio, language=self.language)
                logger.info(f"Recognized text: {text}")
                return text
            except sr.UnknownValueError:
                logger.warning("Google Speech Recognition could not understand the audio.")
                return ""
            except Exception as e:
                logger.error(f"An error occurred in STTHandler: {e}")
                raise STTHandlerError(f"Error during speech-to-text: {e}")
