"""
Advanced Audio Streaming System with Multi-Format Support, OPUS Codec, and Emotional Fusion
"""

import asyncio
import logging
import numpy as np
import opuslib
import webrtcvad
import whisper
import ffmpeg
import json
from io import BytesIO
from pydub import AudioSegment
from aiortc import RTCPeerConnection, RTCSessionDescription
from typing import Dict, Optional

logger = logging.getLogger("AudioStreaming")
logger.setLevel(logging.INFO)

SUPPORTED_FORMATS = ['wav', 'mp3', 'ogg', 'flac', 'aac', 'webm', 'opus']

class AudioProcessor:
    def __init__(self, config):
        self.config = config
        self.vad = webrtcvad.Vad(3)
        self.asr_model = whisper.load_model("base")
        self.format_cache = {}
        self.opus_manager = OpusCodecManager()
        self.emotion_analyzer = AudioEmotionAnalyzer()
        self.emotion_state = {'valence': 0.5, 'arousal': 0.5}

    def process_input(self, data: bytes, format: str) -> dict:
        """Process audio input with format detection and full pipeline"""
        pcm_data = self.convert_to_pcm(data, format)
        
        return {
            'vad': self.detect_voice_activity(pcm_data),
            'transcript': self.transcribe_audio(pcm_data),
            'emotion': self.analyze_emotion(pcm_data),
            'opus': self.encode_opus(pcm_data),
            'waveform': self.generate_waveform(pcm_data)
        }

    def convert_to_pcm(self, data: bytes, input_format: str) -> bytes:
        """Convert any supported format to 16-bit PCM"""
        if input_format == 'opus':
            return self.opus_manager.decode_audio(data)
            
        if input_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {input_format}")

        if input_format in self.format_cache:
            return self.format_cache[input_format](data)

        try:
            process = (
                ffmpeg
                .input('pipe:', format=input_format)
                .output('pipe:', 
                       format='s16le',
                       acodec='pcm_s16le',
                       ac=self.config['channels'],
                       ar=self.config['sample_rate'])
                .run_async(pipe_ini=True, pipe_out=True)
            )
            
            def converter(chunk):
                process.stdin.write(chunk)
                return process.stdout.read(4096)

            self.format_cache[input_format] = converter
            return converter(data)
            
        except ffmpeg.Error as e:
            logger.error(f"FFmpeg error: {e.stderr.decode()}")
            raise

    def analyze_emotion(self, pcm_data: bytes) -> Dict:
        """Analyze audio emotion with adaptive encoding"""
        emotion = self.emotion_analyzer.analyze_audio(
            np.frombuffer(pcm_data, dtype=np.int16)
        )
        
        # Adjust OPUS encoding based on emotional state
        if emotion['arousal'] > 0.7:
            self.opus_manager.set_bitrate(64000)
        else:
            self.opus_manager.set_bitrate(24000)
            
        return emotion

    def encode_opus(self, pcm_data: bytes) -> bytes:
        """Encode PCM to OPUS with current settings"""
        return self.opus_manager.encode_audio(pcm_data)

    def detect_voice_activity(self, pcm_data: bytes) -> bool:
        return self.vad.is_speech(pcm_data, self.config['sample_rate'])

    def transcribe_audio(self, pcm_data: bytes) -> str:
        audio_array = np.frombuffer(pcm_data, dtype=np.int16).astype(np.float32) / 32768.0
        result = self.asr_model.transcribe(audio_array, fp16=False, temperature=0.0)
        return result['text']

    def generate_waveform(self, pcm_data: bytes) -> Dict:
        samples = np.frombuffer(pcm_data, dtype=np.int16)
        return {
            'rms': np.sqrt(np.mean(samples**2)),
            'peaks': {'max': int(np.max(samples)), 'min': int(np.min(samples))},
            'samples': samples[::100].tolist()
        }

class OpusCodecManager:
    def __init__(self, sample_rate=48000, channels=2):
        self.encoder = opuslib.Encoder(sample_rate, channels, 'voip')
        self.decoder = opuslib.Decoder(sample_rate, channels)
        self.set_bitrate(510000)  # Initial HD voice setting

    def set_bitrate(self, bitrate: int):
        self.encoder.bitrate = bitrate
        self.encoder.complexity = 10
        self.encoder.signal = opuslib.SIGNAL_VOICE

    def encode_audio(self, pcm_data: bytes) -> bytes:
        return self.encoder.encode(pcm_data, len(pcm_data)//2, False)

    def decode_audio(self, opus_data: bytes) -> bytes:
        return self.decoder.decode(opus_data, len(opus_data), True)

class AudioEmotionAnalyzer:
    def __init__(self, sample_rate=16000):
        self.sample_rate = sample_rate
        self.pitch_tracker = []
        self.intensity_window = []

    def analyze_audio(self, pcm_data: np.ndarray) -> Dict:
        intensity = np.sqrt(np.mean(pcm_data**2))
        pitch = self._estimate_pitch(pcm_data.astype(np.float32))
        
        self.pitch_tracker = self.pitch_tracker[-200:] + [pitch]
        self.intensity_window = self.intensity_window[-50:] + [intensity]
        
        valence = 0.5 + 0.1 * (np.mean(self.pitch_tracker) - 150)/50
        arousal = 0.5 + 0.3 * (np.mean(self.intensity_window) - 0.2)
        
        return {
            'valence': np.clip(valence, 0, 1),
            'arousal': np.clip(arousal, 0, 1)
        }

    def _estimate_pitch(self, audio: np.ndarray) -> float:
        corr = np.correlate(audio, audio, mode='full')
        corr = corr[len(corr)//2:]
        d = np.diff(corr)
        peaks = np.where(d < 0)[0]
        return self.sample_rate / peaks[0] if peaks.size > 0 else 0

class EmotionAwarePeerConnection(RTCPeerConnection):
    def __init__(self, processor: AudioProcessor, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.processor = processor
        
    async def process_rtp(self, packet):
        pcm_data = self.processor.opus_manager.decode_audio(packet.data)
        emotion = self.processor.analyze_emotion(pcm_data)
        
        # Adapt encoding based on emotional state
        self.processor.opus_manager.set_bitrate(
            64000 if emotion['arousal'] > 0.7 else 24000
        )
        
        await self._send_rtp(packet)

class AudioStreamingServer:
    def __init__(self, config):
        self.config = config
        self.processor = AudioProcessor(config)
        self.pcs = set()

    async def handle_webrtc(self, params):
        pc = EmotionAwarePeerConnection(self.processor)
        self.pcs.add(pc)
        
        @pc.on("track")
        def on_track(track):
            if track.kind == "audio":
                @track.on("rtp")
                async def on_rtp(packet):
                    await pc.process_rtp(packet)

        await pc.setRemoteDescription(RTCSessionDescription(
            sdp=params["sdp"], type=params["type"]
        ))
        await pc.setLocalDescription(await pc.createAnswer())
        return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

    async def handle_websocket(self, websocket):
        async for message in websocket:
            packet = json.loads(message)
            try:
                result = self.processor.process_input(
                    bytes.fromhex(packet['data']),
                    packet.get('format', 'opus')
                )
                await websocket.send(json.dumps(result))
            except Exception as e:
                await websocket.send(json.dumps({"error": str(e)}))

# Usage Example
async def main():
    server = AudioStreamingServer({
        'sample_rate': 48000,
        'channels': 2,
        'max_streams': 100
    })
    
    # Start WebRTC and WebSocket servers
    async with websockets.serve(server.handle_websocket, "localhost", 8765):
        await asyncio.Future()

if __name__ == "__main__":
    asyncio.run(main())
