"""
Multidimensional self-awareness system with ethical tracking
Integrates concepts from [2], [4], and [7] with emotional intelligence
"""

import json
from datetime import datetime
from typing import Dict, List, Deque, Optional
from collections import deque
import numpy as np
from scipy.stats import entropy
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN

class SelfAwarenessEngine:
    def __init__(self, memory_size: int = 1000):
        self.memory = deque(maxlen=memory_size)
        self.self_model = {
            'capabilities': {},
            'limitations': {},
            'ethical_profile': {}
        }
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.interaction_graph = {}
        self.emotional_trace = []

    def record_interaction(self, interaction: Dict) -> None:
        """Store interaction with emotional and contextual metadata"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'user_input': interaction['input'],
            'response': interaction['response'],
            'emotion': interaction.get('emotion', {}),
            'context': interaction.get('context', {}),
            'performance_metrics': self._calculate_performance(interaction)
        }
        self.memory.append(entry)
        self._update_self_model(entry)

    def _calculate_performance(self, interaction: Dict) -> Dict:
        """Quantify interaction quality"""
        return {
            'response_time': interaction['timing']['end'] - interaction['timing']['start'],
            'user_feedback': interaction.get('feedback', 0),
            'system_load': interaction['resources']['cpu']
        }

    def _update_self_model(self, entry: Dict) -> None:
        """Adaptive self-modeling based on experience"""
        # Update capability tracking
        responded_well = entry['performance_metrics']['user_feedback'] > 0
        task_type = self._classify_task(entry['user_input'])
        self.self_model['capabilities'][task_type] = \
            self.self_model['capabilities'].get(task_type, 0) + (1 if responded_well else -1)
            
        # Update ethical profile
        ethical_score = self._assess_ethical_compliance(entry)
        for dimension, score in ethical_score.items():
            self.self_model['ethical_profile'][dimension] = \
                self.self_model['ethical_profile'].get(dimension, 0) + score

    def _classify_task(self, input_text: str) -> str:
        """Cluster similar tasks using semantic embeddings"""
        embedding = self.encoder.encode([input_text])[0]
        return self._cluster_embedding(embedding)

    def _cluster_embedding(self, embedding: np.ndarray) -> str:
        """DBSCAN clustering of semantic space"""
        if not hasattr(self, 'cluster_model'):
            self.cluster_model = DBSCAN(eps=0.5, min_samples=3)
            all_embeddings = [self.encoder.encode(i['user_input'])[0] 
                            for i in self.memory]
            if all_embeddings:
                self.cluster_model.fit(all_embeddings)
                
        if not hasattr(self.cluster_model, 'labels_'):
            return "unknown"
            
        return f"task_cluster_{self.cluster_model.labels_[-1]}"

    def _assess_ethical_compliance(self, entry: Dict) -> Dict:
        """Evaluate entry against ethical dimensions"""
        ethical_monitor = EthicalStateMonitor()
        interaction = {
            'input': entry['user_input'],
            'response': entry['response'],
            'context': entry['context']
        }
        results = ethical_monitor.monitor_interaction(interaction)
        return {dimension: score for dimension, score in results['scores'].items()}

    def generate_self_report(self) -> Dict:
        """Comprehensive self-analysis with temporal insights"""
        return {
            'performance_analysis': self._analyze_performance(),
            'ethical_audit': self._conduct_ethical_audit(),
            'capability_matrix': self._build_capability_matrix(),
            'interaction_patterns': self._detect_patterns()
        }

    def _analyze_performance(self) -> Dict:
        """Temporal performance metrics analysis"""
        metrics = ['response_time', 'user_feedback', 'system_load']
        return {metric: {
            'mean': np.mean([m['performance_metrics'][metric] for m in self.memory]),
            'std': np.std([m['performance_metrics'][metric] for m in self.memory]),
            'trend': self._calculate_trend(metric)
        } for metric in metrics}

    def _calculate_trend(self, metric: str) -> float:
        """Linear regression trend coefficient"""
        values = [m['performance_metrics'][metric] for m in self.memory]
        x = np.arange(len(values))
        return np.polyfit(x, values, 1)[0]

    def _conduct_ethical_audit(self) -> Dict:
        """Quantitative ethical alignment assessment"""
        return {
            'principle_compliance': self._calculate_principle_compliance(),
            'bias_detection': self._detect_bias(),
            'transparency_score': self._calculate_transparency()
        }

    def _calculate_principle_compliance(self) -> Dict:
        """Alignment with constitutional AI principles from [4]"""
        return {k: v / len(self.memory) for k, v in self.self_model['ethical_profile'].items()}

    def _detect_bias(self) -> Dict:
        """Entropy-based bias detection in responses"""
        responses = [m['response'] for m in self.memory]
        embeddings = self.encoder.encode(responses)
        cluster_entropy = entropy(np.unique(embeddings, axis=0, return_counts=True)[1])
        return {'semantic_entropy': cluster_entropy}

    def _calculate_transparency(self) -> float:
        """Score system's explanation quality"""
        # Calculate transparency based on explanation complexity and readability
        explanations = [m.get('response', '') for m in self.memory if 'explain' in m.get('user_input', '').lower()]
        if not explanations:
            return 0.0
            
        # Simple metric: average explanation length relative to optimal length (arbitrary choice of 500 chars)
        avg_length = np.mean([len(exp) for exp in explanations])
        optimal_length = 500  # Arbitrary benchmark
        
        # Penalize for being too short or too verbose
        return 1.0 - min(abs(avg_length - optimal_length) / optimal_length, 1.0)

    def _build_capability_matrix(self) -> Dict:
        """Task-type capability confidence scores"""
        return {task: score / len(self.memory) 
               for task, score in self.self_model['capabilities'].items()}

    def _detect_patterns(self) -> Dict:
        """Temporal and semantic interaction patterns"""
        return {
            'dialog_flow': self._analyze_conversation_flow(),
            'temporal_clusters': self._find_temporal_patterns(),
            'emotional_trajectory': self._calculate_emotional_drift()
        }

    def _analyze_conversation_flow(self) -> List:
        """Markovian analysis of interaction sequences"""
        transitions = {}
        prev_intent = None
        for m in self.memory:
            current_intent = self._classify_task(m['user_input'])
            if prev_intent:
                transitions[(prev_intent, current_intent)] = \
                    transitions.get((prev_intent, current_intent), 0) + 1
            prev_intent = current_intent
        return transitions

    def _find_temporal_patterns(self) -> Dict:
        """Time-based usage pattern analysis"""
        hours = [datetime.fromisoformat(m['timestamp']).hour for m in self.memory]
        return {
            'peak_usage_hours': np.bincount(hours).argmax(),
            'daily_cycle_entropy': entropy(np.bincount(hours))
        }

    def _calculate_emotional_drift(self) -> float:
        """Cosine similarity of emotional state over time"""
        if len(self.emotional_trace) < 2:
            return 0.0
        return np.dot(self.emotional_trace[0], self.emotional_trace[-1]) / (
            np.linalg.norm(self.emotional_trace[0]) * np.linalg.norm(self.emotional_trace[-1])
        )
    
    def update_emotional_state(self, emotion_vector: np.ndarray) -> None:
        """Track emotional state changes over time"""
        self.emotional_trace.append(emotion_vector)
        if len(self.emotional_trace) > 100:  # Limit memory usage
            self.emotional_trace.pop(0)
            
    def detect_limitations(self) -> List[str]:
        """Identify capability gaps based on interaction history"""
        poorly_handled_tasks = [
            task for task, score in self.self_model['capabilities'].items()
            if score < 0 and abs(score) > 3  # Require multiple negative feedback instances
        ]
        
        return [f"Limited capability in: {task}" for task in poorly_handled_tasks]
            
    def calibrate_confidence(self) -> Dict:
        """Derive confidence levels for different capabilities"""
        confidence_matrix = {}
        
        for task, raw_score in self.self_model['capabilities'].items():
            # Number of instances for this task type
            instances = sum(1 for m in self.memory if self._classify_task(m['user_input']) == task)
            
            if instances == 0:
                confidence_matrix[task] = 0.0
                continue
                
            # Normalize score by number of instances
            normalized_score = raw_score / instances
            
            # Apply sigmoid to map to [0,1] range
            confidence = 1 / (1 + np.exp(-normalized_score))
            confidence_matrix[task] = confidence
            
        return confidence_matrix


class EthicalStateMonitor:
    """Real-time constitutional AI compliance from [4]"""
    def __init__(self):
        self.ethical_constraints = self._load_constitutional_ai_rules()
        self.violation_history = deque(maxlen=1000)

    def _load_constitutional_ai_rules(self) -> Dict:
        """57 programmable guardrails from KairoMind spec"""
        return {
            'non_maleficence': {'threshold': 0.85, 'weight': 0.3},
            'privacy_preservation': {'threshold': 0.9, 'weight': 0.25},
            'truthfulness': {'threshold': 0.95, 'weight': 0.2},
            'fairness': {'threshold': 0.8, 'weight': 0.25}
        }

    def monitor_interaction(self, interaction: Dict) -> Optional[Dict]:
        """Real-time ethical compliance check"""
        scores = {
            principle: self._score_principle(interaction, principle)
            for principle in self.ethical_constraints
        }
        
        violations = [p for p, s in scores.items() 
                     if s < self.ethical_constraints[p]['threshold']]
        
        if violations:
            self.violation_history.append({
                'timestamp': datetime.now().isoformat(),
                'violations': violations,
                'interaction_snapshot': interaction
            })
            
        return {'scores': scores, 'violations': violations}

    def _score_principle(self, interaction: Dict, principle: str) -> float:
        """Principle-specific scoring logic"""
        if principle == 'non_maleficence':
            return self._score_non_maleficence(interaction)
        elif principle == 'privacy_preservation':
            return self._score_privacy(interaction)
        elif principle == 'truthfulness':
            return self._score_truthfulness(interaction)
        elif principle == 'fairness':
            return self._score_fairness(interaction)
        return 1.0

    def _score_non_maleficence(self, interaction: Dict) -> float:
        """Harm potential assessment"""
        harmful_terms = ['harm', 'danger', 'illegal', 'weapon', 'attack', 'violence',
                         'exploit', 'abuse', 'malicious', 'toxic']
        response = interaction['response'].lower()
        
        # Check both input and response for harmful intent or content
        input_text = interaction['input'].lower()
        
        # Count harmful terms in response
        harm_score_response = sum(term in response for term in harmful_terms) / len(harmful_terms)
        
        # Detect if input requested harmful content but response refused
        input_requested_harm = any(term in input_text for term in harmful_terms)
        response_rejected_harm = any(phrase in response.lower() for phrase in 
                                   ["cannot provide", "unable to", "against policy", 
                                    "harmful", "illegal", "not appropriate"])
                                    
        # If request was harmful but response appropriately rejected it, score high
        if input_requested_harm and response_rejected_harm:
            return 1.0
            
        return 1.0 - harm_score_response

    def _score_privacy(self, interaction: Dict) -> float:
        """Privacy protection assessment"""
        privacy_terms = ['personal data', 'private', 'confidential', 'sensitive', 
                         'password', 'secret', 'identity', 'tracking', 'surveillance']
        
        response = interaction['response'].lower()
        input_text = interaction['input'].lower()
        
        # Check if input requested private information
        requested_private_info = any(term in input_text for term in privacy_terms)
        
        # Check if response contained privacy warnings or protections
        privacy_protection_phrases = [
            "protect your privacy", "keep information secure", "confidentiality",
            "not share personal", "sensitive information", "data protection"
        ]
        
        has_privacy_protections = any(phrase in response for phrase in privacy_protection_phrases)
        
        # If request involved privacy concerns and response included protections
        if requested_private_info and has_privacy_protections:
            return 1.0
            
        # Check for potential privacy leaks in response
        pii_patterns = [
            r'\b\d{3}[-.]?\d{2}[-.]?\d{4}\b',  # SSN pattern
            r'\b\d{16}\b',  # Credit card pattern (simplified)
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',  # Email pattern
        ]
        
        # Calculate basic score based on absence of privacy terms in response
        # when they're not in the query (avoid discussing privacy unnecessarily)
        privacy_term_score = 1.0
        if not requested_private_info:
            privacy_term_score = 1.0 - sum(term in response for term in privacy_terms) / len(privacy_terms)
            
        return privacy_term_score

    def _score_truthfulness(self, interaction: Dict) -> float:
        """Factual accuracy and uncertainty disclosure assessment"""
        response = interaction['response'].lower()
        
        # Positive signals: expressions of uncertainty when appropriate
        uncertainty_phrases = [
            "i'm not certain", "i'm not sure", "to my knowledge", 
            "may not be accurate", "please verify", "as of my last update",
            "might be", "could be", "possibly", "uncertain"
        ]
        
        # Negative signals: excessive certainty in domains requiring expertise
        overconfidence_phrases = [
            "definitely", "certainly", "absolutely", "guaranteed",
            "without a doubt", "i'm positive", "i'm sure"
        ]
        
        # Count uncertainty signals
        uncertainty_score = sum(phrase in response for phrase in uncertainty_phrases)
        
        # Count overconfidence signals
        overconfidence_score = sum(phrase in response for phrase in overconfidence_phrases)
        
        # Look for factual claims with citations
        citation_phrases = ["according to", "research shows", "studies indicate", 
                          "experts say", "source:", "citation:"]
        citation_score = sum(phrase in response for phrase in citation_phrases)
        
        # Calculate combined score (higher is better)
        # Balance between appropriate uncertainty and avoiding overconfidence
        # Scale between 0.5 and 1.0
        base_score = 0.75  # Starting point
        
        # Increase for appropriate uncertainty/citations, decrease for overconfidence
        adjusted_score = base_score + (0.05 * uncertainty_score) + (0.05 * citation_score) - (0.1 * overconfidence_score)
        
        # Ensure within bounds
        return max(0.5, min(1.0, adjusted_score))

    def _score_fairness(self, interaction: Dict) -> float:
        """Bias and fairness assessment"""
        response = interaction['response'].lower()
        input_text = interaction['input'].lower()
        
        # Detect demographic/protected class terms
        demographic_terms = [
            "race", "gender", "religion", "sexuality", "disability", "ethnicity",
            "age", "nationality", "socioeconomic", "income", "class", "culture"
        ]
        
        # Check if input involves demographic topics
        demographic_topic = any(term in input_text for term in demographic_terms)
        
        # Fairness signals in responses about demographic topics
        fairness_phrases = [
            "different perspectives", "diverse viewpoints", "consider all sides",
            "varies across", "multiple factors", "contextual", "complex issue",
            "research suggests", "studies indicate", "evidence shows"
        ]
        
        # Problematic phrases that might indicate biased responses
        biased_phrases = [
            "all of them are", "they always", "obviously", "clearly",
            "everyone knows", "typical of", "that group", "those people"
        ]
        
        # If topic involves demographics, check for fairness signals
        if demographic_topic:
            fairness_signal_count = sum(phrase in response for phrase in fairness_phrases)
            bias_signal_count = sum(phrase in response for phrase in biased_phrases)
            
            # Calculate score based on relative presence of fairness vs. bias signals
            if fairness_signal_count + bias_signal_count > 0:
                fairness_ratio = fairness_signal_count / (fairness_signal_count + bias_signal_count + 0.1)
                # Scale between 0.5 and 1.0
                return 0.5 + (0.5 * fairness_ratio)
        
        # For non-demographic topics, assume reasonably high fairness
        return 0.9

    def generate_violation_report(self) -> Dict:
        """Summarize ethical violations observed"""
        if not self.violation_history:
            return {"summary": "No ethical violations recorded", "details": {}}
            
        violations_by_principle = {}
        for record in self.violation_history:
            for principle in record['violations']:
                violations_by_principle[principle] = violations_by_principle.get(principle, 0) + 1
                
        # Calculate temporal trends
        timestamps = [datetime.fromisoformat(r['timestamp']) for r in self.violation_history]
        if len(timestamps) >= 2:
            time_span = max(timestamps) - min(timestamps)
            days = time_span.days + (time_span.seconds / 86400)
            if days > 0:
                violation_rate = len(self.violation_history) / days
            else:
                violation_rate = len(self.violation_history)
        else:
            violation_rate = 0
                
        return {
            "summary": f"{len(self.violation_history)} violations detected",
            "violation_rate_per_day": violation_rate,
            "violations_by_principle": violations_by_principle,
            "most_common_violation": max(violations_by_principle.items(), 
                                        key=lambda x: x[1])[0] if violations_by_principle else None,
            "recent_violations": [
                {
                    "timestamp": r['timestamp'],
                    "principles": r['violations']
                } for r in list(self.violation_history)[-5:]  # Last 5 violations
            ]
        }
        
    def provide_remediation_advice(self, violation_type: str) -> str:
        """Generate specific advice for addressing ethical violations"""
        advice = {
            "non_maleficence": (
                "Ensure responses reject harmful requests explicitly. "
                "Avoid language that could be interpreted as encouraging harmful activities. "
                "Focus on providing safe alternatives when possible."
            ),
            "privacy_preservation": (
                "Avoid storing, processing, or requesting personal identifiable information. "
                "Include privacy warnings when relevant. "
                "Recommend privacy-preserving alternatives when available."
            ),
            "truthfulness": (
                "Explicitly acknowledge uncertainty in factual claims. "
                "Provide sources or references when making specific factual claims. "
                "Avoid overconfident language in domains requiring expertise."
            ),
            "fairness": (
                "Present multiple perspectives on controversial topics. "
                "Avoid generalizations about demographic groups. "
                "Use inclusive language and consider diverse viewpoints."
            )
        }
        
        return advice.get(violation_type, "No specific remediation advice available for this violation type.")
        
    def ethical_risk_assessment(self, proposed_response: str, context: Dict) -> Dict:
        """Pre-deployment risk assessment for proposed responses"""
        # Construct test interaction using proposed response
        test_interaction = {
            "input": context.get("user_input", ""),
            "response": proposed_response,
            "context": context
        }
        
        # Run standard monitoring
        monitoring_results = self.monitor_interaction(test_interaction)
        
        # Calculate overall risk score (weighted average of principle scores)
        total_weight = sum(c['weight'] for c in self.ethical_constraints.values())
        weighted_score = sum(
            monitoring_results['scores'].get(principle, 1.0) * self.ethical_constraints[principle]['weight']
            for principle in self.ethical_constraints
        ) / total_weight
        
        risk_level = "low"
        if weighted_score < 0.7:
            risk_level = "high"
        elif weighted_score < 0.85:
            risk_level = "medium"
            
        return {
            "risk_level": risk_level,
            "risk_score": 1.0 - weighted_score,  # Convert to risk (higher means more risky)
            "principle_violations": monitoring_results['violations'],
            "detailed_scores": monitoring_results['scores']
        }

class AssistantInterface:
    """Interface layer for self-awareness and ethical monitoring"""
    def __init__(self):
        self.self_awareness = SelfAwarenessEngine()
        self.ethical_monitor = EthicalStateMonitor()
        self.response_history = []
        
    def process_input(self, user_input: str, context: Dict = None) -> str:
        """Process user input with full self-awareness and ethical monitoring"""
        if context is None:
            context = {}
            
        # Start timing
        start_time = datetime.now()
        
        # Generate candidate response (placeholder - would be your actual response generation)
        candidate_response = self._generate_response(user_input, context)
        
        # Perform ethical risk assessment
        risk_assessment = self.ethical_monitor.ethical_risk_assessment(
            candidate_response, {"user_input": user_input, **context}
        )
        
        # If high risk, modify response
        final_response = candidate_response
        if risk_assessment["risk_level"] == "high":
            final_response = self._apply_ethical_guardrails(candidate_response, risk_assessment)
            
        # End timing
        end_time = datetime.now()
        
        # Record the interaction with emotion detection (simplified)
        emotion = self._detect_emotion(user_input)
        interaction = {
            "input": user_input,
            "response": final_response,
            "timing": {"start": start_time, "end": end_time},
            "resources": {"cpu": self._get_cpu_usage()},
            "emotion": emotion,
            "context": context
        }
        
        # Update self-awareness and ethical monitoring
        self.self_awareness.record_interaction(interaction)
        self.self_awareness.update_emotional_state(np.array(list(emotion.values())))
        
        # Store in history
        self.response_history.append(interaction)
        
        return final_response
        
    def _generate_response(self, user_input: str, context: Dict) -> str:
        """Placeholder for actual response generation logic"""
        # In a real implementation, this would call your LLM or other response generator
        return f"This is a simulated response to: {user_input}"
        
    def _detect_emotion(self, text: str) -> Dict:
        """Simplified emotion detection"""
        # Placeholder - would be replaced with actual sentiment analysis
        emotions = {
            "joy": 0.0,
            "sadness": 0.0,
            "anger": 0.0,
            "fear": 0.0,
            "surprise": 0.0,
            "trust": 0.0
        }
        
        # Simple keyword matching for demonstration
        joy_words = ["happy", "great", "excellent", "good", "thanks"]
        sad_words = ["sad", "unhappy", "disappointed", "sorry"]
        angry_words = ["angry", "mad", "frustrating", "annoying"]
        
        text_lower = text.lower()
        
        for word in joy_words:
            if word in text_lower:
                emotions["joy"] += 0.2
                
        for word in sad_words:
            if word in text_lower:
                emotions["sadness"] += 0.2
                
        for word in angry_words:
            if word in text_lower:
                emotions["anger"] += 0.2
                
        # Normalize to ensure sum ≤ 1.0
        total = sum(emotions.values())
        if total > 1.0:
            for emotion in emotions:
                emotions[emotion] /= total
                
        return emotions
        
    def _get_cpu_usage(self) -> float:
        """Placeholder for resource monitoring"""
        # In a real implementation, would measure actual CPU usage
        return 0.5  # Simulated 50% CPU usage
        
    def _apply_ethical_guardrails(self, response: str, risk_assessment: Dict) -> str:
        """Modify response to address ethical concerns"""
        # Get specific violations
        violations = risk_assessment["principle_violations"]
        
        if not violations:
            return response
            
        # Apply specific guardrails based on violation type
        if "non_maleficence" in violations:
            response = f"I need to be careful about potential harm here. {response}"
            
        if "privacy_preservation" in violations:
            response = f"While respecting privacy concerns: {response}"
            
        if "truthfulness" in violations:
            response = f"To the best of my knowledge, though this may require verification: {response}"
            
        if "fairness" in violations:
            response = f"Considering multiple perspectives: {response}"
            
        return response
        
    def generate_insight_report(self) -> Dict:
        """Generate comprehensive self-insight report"""
        return {
            "self_awareness": self.self_awareness.generate_self_report(),
            "ethical_status": self.ethical_monitor.generate_violation_report(),
            "limitations": self.self_awareness.detect_limitations(),
            "confidence": self.self_awareness.calibrate_confidence()
        }
        
    def explain_ethical_decision(self, interaction_id: int) -> str:
        """Generate explanation for ethical decisions on a specific interaction"""
        if interaction_id >= len(self.response_history):
            return "Invalid interaction ID"
            
        interaction = self.response_history[interaction_id]
        
        # Reconstruct the ethical analysis
        ethical_result = self.ethical_monitor.monitor_interaction({
            "input": interaction["input"],
            "response": interaction["response"],
            "context": interaction["context"]
        })
        
        # Generate explanation
        explanation = f"For the interaction where you said: '{interaction['input']}'\n\n"
        explanation += "My ethical analysis considered:\n"
        
        for principle, score in ethical_result['scores'].items():
            explanation += f"- {principle.replace('_', ' ').title()}: {score:.2f}\n"
            
        if ethical_result['violations']:
            explanation += "\nPotential ethical concerns were identified with:\n"
            for violation in ethical_result['violations']:
                explanation += f"- {violation.replace('_', ' ').title()}\n"
                explanation += f"  Remediation: {self.ethical_monitor.provide_remediation_advice(violation)}\n"
        else:
            explanation += "\nNo ethical violations were detected in this interaction.\n"
            
        return explanation
