import logging
from gtts import gTTS
from IPython.display import Audio

logger = logging.getLogger(__name__)

class TTSHandler:
    """Handles text-to-speech functionalities."""
    def __init__(self, output_dir: str, voice: str = "en"):
        self.output_dir = output_dir
        self.voice = voice

    def text_to_speech(self, text: str):
        """Converts text to speech and plays it using gTTS."""
        try:
            tts = gTTS(text=text, lang=self.voice)
            temp_mp3_file = f"{self.output_dir}/temp_speech.mp3"
            tts.save(temp_mp3_file)
            Audio(filename=temp_mp3_file, autoplay=True)
            logger.info("Text-to-speech processing complete.")
        except Exception as e:
            logger.error(f"Error during text-to-speech processing: {e}")
            raise
