"""
Unified Emotional Context Manager
"""
from typing import Deque, Dict
from collections import deque
import numpy as np

class EmotionalContext:
    def __init__(self, window_size=30):
        self.modalities = {
            'audio': deque(maxlen=window_size),
            'gesture': deque(maxlen=window_size),
            'fusion': deque(maxlen=window_size)
        }
        self.weights = {
            'audio': 0.6,
            'gesture': 0.4
        }

    def update_modality(self, modality: str, state: Dict):
        """Update emotional state for a specific modality"""
        self.modalities[modality].append(state)
        self._update_fusion()

    def _update_fusion(self):
        """Temporal fusion of emotional states"""
        audio_states = np.array([s['valence'] for s in self.modalities['audio']])
        gesture_states = np.array([s['valence'] for s in self.modalities['gesture']])
        
        if len(audio_states) == 0 or len(gesture_states) == 0:
            return
            
        # Align temporal windows
        min_len = min(len(audio_states), len(gesture_states))
        fused_valence = (self.weights['audio'] * audio_states[-min_len:] +
                       self.weights['gesture'] * gesture_states[-min_len:])
        
        # Apply exponential smoothing
        smoothed = np.zeros(min_len)
        alpha = 0.2
        for i in range(min_len):
            smoothed[i] = alpha * fused_valence[i] + (1-alpha) * smoothed[i-1]

        self.modalities['fusion'].extend(
            [{'valence': v, 'arousal': 0.5} for v in smoothed]
        )

    def get_current_state(self) -> Dict:
        """Get fused emotional state with temporal context"""
        if not self.modalities['fusion']:
            return {'valence': 0.5, 'arousal': 0.5}
            
        return {
            'valence': np.mean([s['valence'] for s in self.modalities['fusion']]),
            'arousal': np.mean([s['arousal'] for s in self.modalities['fusion']])
        }
