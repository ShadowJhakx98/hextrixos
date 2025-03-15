"""
Multidimensional emotional state tracking with dynamic contagion modeling
"""
import numpy as np
from scipy.integrate import odeint
from typing import Dict, List
from datetime import datetime

class EmotionalVector:
    def __init__(self):
        self.base_emotions = {
            'joy': 0.5,
            'sadness': 0.5, 
            'anger': 0.5,
            'fear': 0.5,
            'disgust': 0.5,
            'surprise': 0.5
        }
        self.mood = 0.0  # [-1,1] scale
        self.valence = 0.0
        self.arousal = 0.0
        self.stability = 1.0
        
    def normalize(self):
        """Constrain emotions to valid ranges"""
        for k in self.base_emotions:
            self.base_emotions[k] = np.clip(self.base_emotions[k], 0, 1)
        self.mood = np.clip(self.mood, -1, 1)
        self.valence = np.clip(self.valence, -1, 1)
        self.arousal = np.clip(self.arousal, 0, 1)
        self.stability = np.clip(self.stability, 0, 1)

class EmotionEngine:
    def __init__(self):
        self.current_state = EmotionalVector()
        self.history = []
        self.decay_rates = {
            'joy': 0.95,
            'sadness': 0.90,
            'anger': 0.85,
            'fear': 0.92,
            'disgust': 0.88,
            'surprise': 0.75
        }
        self.social_contagion_factors = self._init_contagion_model()
        
    def _init_contagion_model(self) -> Dict[str, float]:
        return {
            'emotional_congruence': 0.65,
            'social_proximity': 0.80,
            'authority_bias': 0.70,
            'group_dynamics': 0.75
        }
        
    def update_emotion(self, stimulus: Dict):
        """Process emotional stimulus using differential equations"""
        self.history.append((datetime.now(), self.current_state))
        
        # Convert stimulus to emotion delta
        delta = self._stimulus_to_delta(stimulus)
        
        # Solve emotional dynamics ODE
        t = np.linspace(0, 1, 10)
        y0 = list(self.current_state.base_emotions.values()) + \
            [self.current_state.mood, 
             self.current_state.valence,
             self.current_state.arousal]
             
        solution = odeint(self._emotion_ode, y0, t, args=(delta,))
        
        # Update state with new values
        self._apply_ode_solution(solution[-1])
        self.current_state.normalize()
        
    def _stimulus_to_delta(self, stimulus: Dict) -> np.ndarray:
        """Convert stimulus description to emotion deltas"""
        delta = np.zeros(9)
        emotion_map = {
            'joy': 0,
            'sadness': 1,
            'anger': 2,
            'fear': 3,
            'disgust': 4,
            'surprise': 5,
            'mood': 6,
            'valence': 7,
            'arousal': 8
        }
        
        for k, v in stimulus.items():
            if k in emotion_map:
                delta[emotion_map[k]] = v * 0.1  # Scale stimulus impact
                
        return delta
        
    def _emotion_ode(self, y, t, delta):
        """Differential equations governing emotional dynamics"""
        dydt = np.zeros_like(y)
        
        # Base emotion dynamics
        for i in range(6):
            dydt[i] = (delta[i] - y[i]) * (1 - self.decay_rates[list(
                self.current_state.base_emotions.keys())[i]])
            
        # Mood dynamics
        dydt[6] = (np.mean(y[:6]) - 0.5) * 0.1 + delta[6]
        
        # Valence-arousal dynamics
        dydt[7] = (y[6] * 0.8 + delta[7]) * 0.5
        dydt[8] = (np.std(y[:6]) * 1.2 + delta[8]) * 0.3
        
        return dydt
        
    def _apply_ode_solution(self, solution: np.ndarray):
        """Map ODE solution back to emotional state"""
        self.current_state.base_emotions = {
            'joy': solution[0],
            'sadness': solution[1],
            'anger': solution[2],
            'fear': solution[3],
            'disgust': solution[4],
            'surprise': solution[5]
        }
        self.current_state.mood = solution[6]
        self.current_state.valence = solution[7]
        self.current_state.arousal = solution[8]
        
    def apply_contagion(self, external_emotion: Dict, social_params: Dict):
        """Model emotional contagion from external sources"""
        contagion_effect = np.zeros(6)
        weights = [
            social_params.get('proximity', 0.5),
            social_params.get('authority', 0.3),
            social_params.get('similarity', 0.4)
        ]
        total_weight = sum(weights)
        
        for i, emotion in enumerate(self.current_state.base_emotions.keys()):
            external_val = external_emotion.get(emotion, 0.5)
            difference = external_val - self.current_state.base_emotions[emotion]
            contagion_effect[i] = difference * total_weight * 0.1
            
        self.update_emotion({emotion: contagion_effect[i] 
                           for i, emotion in enumerate(
                            self.current_state.base_emotions.keys())})

    def get_emotional_synergy(self, other_emotion: Dict) -> float:
        """Calculate emotional alignment with another entity"""
        vec_self = np.array(list(self.current_state.base_emotions.values()))
        vec_other = np.array([other_emotion.get(k, 0.5) 
                            for k in self.current_state.base_emotions.keys()])
        return np.dot(vec_self, vec_other) / (np.linalg.norm(vec_self) * 
                                             np.linalg.norm(vec_other))

class EmotionalMemory:
    def __init__(self, decay_rate=0.95):
        self.memory_traces = []
        self.decay_rate = decay_rate
        
    def add_experience(self, emotion_state: EmotionalVector, context: Dict):
        """Store emotional experience with context"""
        self.memory_traces.append({
            'timestamp': datetime.now(),
            'emotion': emotion_state,
            'context': context,
            'strength': 1.0
        })
        
    def decay_memories(self):
        """Apply temporal decay to emotional memories"""
        for trace in self.memory_traces:
            age = (datetime.now() - trace['timestamp']).total_seconds() / 3600
            trace['strength'] *= self.decay_rate ** age
            
        # Remove faded memories
        self.memory_traces = [t for t in self.memory_traces 
                            if t['strength'] > 0.1]
