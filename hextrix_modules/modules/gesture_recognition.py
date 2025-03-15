"""
Multimodal Gesture Recognition with AR Feedback and Emotion Fusion
"""
import cv2
import mediapipe as mp
import numpy as np
from typing import Dict, Tuple
from collections import deque
from scipy.spatial.transform import Rotation

class ARGestureFeedback:
    def __init__(self):
        self.emoji_mapping = {
            'thumbs_up': '👍',
            'wave': '👋',
            'point': '👉',
            'raised_hand': '✋'
        }
        self.feedback_history = deque(maxlen=10)
        self.emotion_state = {'valence': 0.5, 'arousal': 0.5}

    def _project_3d_to_2d(self, point_3d: np.ndarray, frame: np.ndarray) -> Tuple[int, int]:
        """Convert 3D gesture space to 2D screen coordinates"""
        height, width = frame.shape[:2]
        x = int((point_3d[0] + 0.5) * width)
        y = int((1 - (point_3d[1] + 0.5)) * height)
        return (x, y)

    def draw_ar_overlay(self, frame: np.ndarray, gesture: Dict, landmarks: np.ndarray):
        """Augmented reality feedback system"""
        # Base visual elements
        cv2.putText(frame, f"{self.emoji_mapping.get(gesture['action'], '❓')} {gesture['action'].replace('_', ' ').title()}",
                   (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        # 3D trajectory visualization
        if len(landmarks) >= 5:
            wrist_3d = landmarks[0]
            screen_pos = self._project_3d_to_2d(wrist_3d, frame)
            cv2.circle(frame, screen_pos, 15, (0, 255, 255), -1)
            
            # Emotional state indicator
            emotion_color = (0, int(255 * self.emotion_state['valence']), 
                           int(255 * self.emotion_state['arousal']))
            cv2.rectangle(frame, (0, 0), (int(200 * self.emotion_state['valence']), 10), 
                        emotion_color, -1)

        # Force field effect for active gestures
        if gesture['confidence'] > 0.8:
            center = (frame.shape[1]//2, frame.shape[0]//2)
            cv2.circle(frame, center, 50, (0, 0, 255), 3, lineType=cv2.LINE_AA)

        return frame

class EmotionFuser:
    def __init__(self, audio_weight=0.6, gesture_weight=0.4):
        self.weights = {'audio': audio_weight, 'gesture': gesture_weight}
        self.temporal_window = deque(maxlen=15)
        
    def fuse_modalities(self, audio_emotion: Dict, gesture_emotion: Dict) -> Dict:
        """Multi-modal emotion fusion with temporal smoothing"""
        fused = {
            'valence': (audio_emotion['valence'] * self.weights['audio'] +
                       gesture_emotion['valence'] * self.weights['gesture']),
            'arousal': (audio_emotion['arousal'] * self.weights['audio'] +
                       gesture_emotion['arousal'] * self.weights['gesture'])
        }
        self.temporal_window.append(fused)
        
        # Apply exponential moving average
        smoothed = {'valence': 0.0, 'arousal': 0.0}
        for i, state in enumerate(reversed(self.temporal_window)):
            decay = 0.9 ** i
            smoothed['valence'] += state['valence'] * decay
            smoothed['arousal'] += state['arousal'] * decay
            
        total_weight = sum(0.9 ** i for i in range(len(self.temporal_window)))
        smoothed['valence'] /= total_weight
        smoothed['arousal'] /= total_weight
        
        return smoothed

class GestureEmotionAnalyzer:
    def __init__(self):
        self.pose_model = mp.solutions.pose.Pose(
            min_detection_confidence=0.7, 
            min_tracking_confidence=0.7
        )
        
    def analyze_posture(self, frame: np.ndarray) -> Dict:
        """Estimate emotional state from body language"""
        results = self.pose_model.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        
        if not results.pose_landmarks:
            return {'valence': 0.5, 'arousal': 0.5}
            
        # Calculate posture metrics
        shoulders = self._get_joint_angles(results, [11, 12, 13, 14])
        head_angle = self._calculate_head_orientation(results)
        
        # Emotional inference rules
        valence = 0.5 + 0.3 * np.sin(head_angle[1])  # Pitch affects valence
        arousal = 0.5 + 0.2 * np.mean(shoulders)     # Shoulder tension
        
        return {'valence': np.clip(valence, 0, 1), 
                'arousal': np.clip(arousal, 0, 1)}
                
    def _calculate_head_orientation(self, results) -> Rotation:
        """Estimate head pose using rotation matrix"""
        landmarks = results.pose_landmarks.landmark
        nose = [landmarks[0].x, landmarks[0].y, landmarks[0].z]
        left_ear = [landmarks[7].x, landmarks[7].y, landmarks[7].z]
        right_ear = [landmarks[8].x, landmarks[8].y, landmarks[8].z]
        
        # Calculate rotation vectors
        forward = np.array(nose) - (np.array(left_ear) + np.array(right_ear))/2
        up = np.array([0, -1, 0])  # Assuming upright posture
        right = np.cross(forward, up)
        
        return Rotation.from_matrix(np.column_stack((right, up, forward)))
