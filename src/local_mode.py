"""
local_mode.py

Provides a "LocalNoGeminiMode" fallback class that does NOT depend on Gemini.
Shows minimal streaming logic for local TTS (audio) and a camera read loop,
but does not talk to any LLM. It's purely local demonstration.
"""

import asyncio
import wave
import pyaudio
import cv2
import torch
import pyttsx3
from transformers import GPT2LMHeadModel, GPT2Tokenizer

class LocalNoGeminiMode:
    def __init__(self):
        # GPT-2
        self.gpt2_model = GPT2LMHeadModel.from_pretrained("gpt2")
        self.gpt2_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
        # Basic TTS
        self.engine = pyttsx3.init()

    async def local_audio_stream(self):
        """
        Demonstrate local mic reading, not sending anywhere.
        We just yield raw PCM data for demonstration.
        Could do local speech recognition, etc.
        """
        chunk_size = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 16000
        p = pyaudio.PyAudio()
        stream = p.open(format=format,
                        channels=channels,
                        rate=rate,
                        input=True,
                        frames_per_buffer=chunk_size)
        try:
            while True:
                data = stream.read(chunk_size, exception_on_overflow=False)
                yield data
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()

    async def local_video_stream(self):
        """
        Demonstrate camera usage without sending to an LLM.
        We'll read frames and yield them as raw JPEG bytes or something. 
        """
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Could not open local webcam")

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                ret, buf = cv2.imencode(".jpg", frame)
                if not ret:
                    continue
                data = buf.tobytes()
                yield data
        finally:
            cap.release()

    async def text_to_text(self, prompt: str) -> str:
        """
        Local GPT-2 generation example, synchronous.
        """
        input_ids = self.gpt2_tokenizer.encode(prompt, return_tensors="pt")
        with torch.no_grad():
            output = self.gpt2_model.generate(
                input_ids,
                max_length=100,
                num_return_sequences=1,
                do_sample=True,
                temperature=0.7,
                top_p=0.9
            )
        return self.gpt2_tokenizer.decode(output[0], skip_special_tokens=True)

    def local_tts(self, text: str, outfile="local_tts.wav"):
        """
        Simple local TTS using pyttsx3, saving to a wave file 
        if your engine supports it (not all do). 
        Otherwise, we do a naive approach.
        """
        # Some pyttsx3 backends don't support saving direct to file. 
        # So you might have to do real-time record from output device. 
        # We'll do best effort:
        self.engine.save_to_file(text, outfile)
        self.engine.runAndWait()
        return f"Saved TTS to {outfile}"
