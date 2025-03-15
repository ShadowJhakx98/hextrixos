import speech_recognition as sr
import pyttsx3

class SpeechHandler:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.engine = pyttsx3.init()

    def listen(self):
        with sr.Microphone() as source:
            print("Listening...")
            audio = self.recognizer.listen(source)
        return audio

    def recognize_speech(self, audio):
        try:
            return self.recognizer.recognize_google(audio).lower()
        except sr.UnknownValueError:
            return None

    def speak(self, text):
        print(f"Assistant: {text}")
        self.engine.say(text)
        self.engine.runAndWait()
