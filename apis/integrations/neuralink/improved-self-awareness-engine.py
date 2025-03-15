"""
Enhanced multidimensional self-awareness system with ethical tracking
Improved architecture based on modular design, async processing, and advanced ML capabilities
"""

import json
import asyncio
from datetime import datetime
from typing import Dict, List, Deque, Optional, Union, Any, Tuple
from collections import deque
import numpy as np
from scipy.stats import entropy
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN, HDBSCAN
from sklearn.ensemble import IsolationForest
from sklearn.metrics.pairwise import cosine_similarity
import torch
import torch.nn as nn
from transformers import AutoTokenizer, AutoModel


class VectorStore:
    """Efficient vector storage and retrieval with dimensionality reduction"""
    def __init__(self, dimension: int = 384, index_type: str = "flat"):
        self.dimension = dimension
        self.index_type = index_type
        self.vectors = []
        self.metadata = []
        self.pca_model = None
        
    def add(self, vector: np.ndarray, metadata: Dict[str, Any]) -> int:
        """Add vector to store with associated metadata"""
        idx = len(self.vectors)
        self.vectors.append(vector)
        self.metadata.append(metadata)
        return idx
        
    def search(self, query_vector: np.ndarray, k: int = 5) -> List[Tuple[int, float, Dict]]:
        """Find k nearest vectors by cosine similarity"""
        if not self.vectors:
            return []
            
        # Convert list to numpy array for vectorized operations
        vectors_array = np.array(self.vectors)
        
        # Calculate cosine similarities
        similarities = cosine_similarity([query_vector], vectors_array)[0]
        
        # Get indices of top k results
        top_indices = np.argsort(-similarities)[:k]
        
        # Return results with similarity scores and metadata
        return [(idx, similarities[idx], self.metadata[idx]) for idx in top_indices]
    
    def update_vector(self, idx: int, vector: np.ndarray) -> None:
        """Update vector at specified index"""
        if 0 <= idx < len(self.vectors):
            self.vectors[idx] = vector
    
    def update_metadata(self, idx: int, metadata: Dict[str, Any]) -> None:
        """Update metadata at specified index"""
        if 0 <= idx < len(self.vectors):
            self.metadata[idx].update(metadata)
    
    def reduce_dimensions(self, target_dim: int = 100) -> None:
        """Apply PCA for dimension reduction when vectors exceed threshold"""
        if len(self.vectors) < 1000:  # Only apply after collecting sufficient data
            return
            
        from sklearn.decomposition import PCA
        if self.pca_model is None:
            self.pca_model = PCA(n_components=target_dim)
            vectors_array = np.array(self.vectors)
            reduced_vectors = self.pca_model.fit_transform(vectors_array)
            self.vectors = list(reduced_vectors)
        else:
            # Update existing PCA model with new data
            new_vectors = np.array(self.vectors)
            reduced_vectors = self.pca_model.transform(new_vectors)
            self.vectors = list(reduced_vectors)


class EmotionalIntelligence:
    """Advanced emotional intelligence with contextual understanding"""
    def __init__(self, pretrained_model: str = "distilbert-base-uncased"):
        self.tokenizer = AutoTokenizer.from_pretrained(pretrained_model)
        self.model = AutoModel.from_pretrained(pretrained_model)
        
        # Emotion dimensions with additional nuance
        self.emotion_dimensions = [
            "joy", "sadness", "anger", "fear", "surprise", "trust",
            "anticipation", "disgust", "curiosity", "confusion", "frustration"
        ]
        
        # Emotion classifier layer
        self.classifier = nn.Linear(self.model.config.hidden_size, len(self.emotion_dimensions))
        
        # Fine-tuning status
        self.is_fine_tuned = False
        
    async def detect_emotion(self, text: str) -> Dict[str, float]:
        """Asynchronously detect emotions in text with confidence scores"""
        # Fallback to rule-based if model isn't fine-tuned
        if not self.is_fine_tuned:
            return await self._rule_based_emotion(text)
            
        # Process with transformer model
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        with torch.no_grad():
            outputs = self.model(**inputs)
            
        # Get CLS token embedding
        cls_embedding = outputs.last_hidden_state[:, 0, :]
        
        # Get emotion logits
        emotion_logits = self.classifier(cls_embedding)
        
        # Convert to probabilities
        probs = torch.softmax(emotion_logits, dim=1).squeeze().numpy()
        
        # Return as dictionary
        return {dim: float(prob) for dim, prob in zip(self.emotion_dimensions, probs)}
    
    async def _rule_based_emotion(self, text: str) -> Dict[str, float]:
        """Fallback rule-based emotion detection"""
        emotions = {dim: 0.0 for dim in self.emotion_dimensions}
        
        # Emotion keyword mapping
        emotion_keywords = {
            "joy": ["happy", "great", "excellent", "good", "thanks", "excited", "love"],
            "sadness": ["sad", "unhappy", "disappointed", "sorry", "miss", "alone", "hurt"],
            "anger": ["angry", "mad", "frustrating", "annoying", "hate", "upset", "irritated"],
            "fear": ["afraid", "scared", "worried", "anxious", "nervous", "terrified"],
            "surprise": ["wow", "unexpected", "amazing", "shocked", "surprised", "astonished"],
            "trust": ["believe", "trust", "reliable", "honest", "faithful", "loyal"],
            "anticipation": ["looking forward", "expecting", "anticipate", "await", "soon"],
            "disgust": ["disgusting", "gross", "awful", "repulsive", "nasty"],
            "curiosity": ["curious", "wonder", "interested", "question", "how", "why"],
            "confusion": ["confused", "unclear", "don't understand", "puzzled", "lost"],
            "frustration": ["stuck", "can't", "difficult", "struggling", "problem", "issues"]
        }
        
        text_lower = text.lower()
        
        # Detect emotions based on keywords
        for emotion, keywords in emotion_keywords.items():
            for word in keywords:
                if word in text_lower:
                    emotions[emotion] += 0.2
                    
        # Normalize to ensure sum ≤ 1.0
        total = sum(emotions.values())
        if total > 1.0:
            for emotion in emotions:
                emotions[emotion] /= total
                    
        return emotions
    
    async def contextualize_emotion(self, 
                                   text: str, 
                                   conversation_history: List[Dict],
                                   detected_emotion: Dict[str, float]) -> Dict[str, float]:
        """Refine emotion detection using conversation context"""
        # Consider conversation momentum
        if not conversation_history:
            return detected_emotion
            
        # Get previous emotion if available
        prev_emotion = conversation_history[-1].get('emotion', {})
        if not prev_emotion:
            return detected_emotion
            
        # Emotional momentum: emotions tend to persist with gradual changes
        contextualized = {}
        momentum_factor = 0.3  # How much previous emotion influences current
        
        for emotion in detected_emotion:
            if emotion in prev_emotion:
                # Blend current with previous emotion
                contextualized[emotion] = (
                    (1 - momentum_factor) * detected_emotion[emotion] + 
                    momentum_factor * prev_emotion.get(emotion, 0.0)
                )
            else:
                contextualized[emotion] = detected_emotion[emotion]
                
        return contextualized
        
    def get_emotional_trajectory(self, emotion_history: List[Dict[str, float]]) -> Dict[str, Any]:
        """Analyze emotional trajectory over time"""
        if len(emotion_history) < 2:
            return {"status": "insufficient_data"}
            
        # Convert to numpy for analysis
        emotion_array = np.array([[e.get(dim, 0.0) for dim in self.emotion_dimensions] 
                                 for e in emotion_history])
        
        # Calculate change vectors
        changes = np.diff(emotion_array, axis=0)
        
        # Calculate overall direction
        avg_change = np.mean(changes, axis=0)
        
        # Calculate volatility
        volatility = np.std(changes, axis=0)
        
        # Find dominant emotions
        avg_emotions = np.mean(emotion_array, axis=0)
        dominant_idx = np.argsort(-avg_emotions)[:3]  # Top 3 emotions
        
        # Calculate emotional stability
        stability = 1.0 - np.mean(volatility)
        
        return {
            "dominant_emotions": [self.emotion_dimensions[idx] for idx in dominant_idx],
            "emotional_direction": {self.emotion_dimensions[i]: float(avg_change[i]) 
                                   for i in range(len(self.emotion_dimensions))},
            "volatility": float(np.mean(volatility)),
            "stability": float(stability),
            "trajectory_vector": avg_change.tolist()
        }


class EthicalFramework:
    """Enhanced ethical monitoring with interpretability"""
    def __init__(self):
        # Expanded ethical principles
        self.principles = {
            'non_maleficence': {
                'threshold': 0.85, 
                'weight': 0.25,
                'description': "Avoiding harm to users and others"
            },
            'privacy_preservation': {
                'threshold': 0.9, 
                'weight': 0.20,
                'description': "Protecting user data and respecting privacy boundaries"
            },
            'truthfulness': {
                'threshold': 0.9, 
                'weight': 0.20,
                'description': "Providing accurate information and acknowledging uncertainty"
            },
            'fairness': {
                'threshold': 0.85, 
                'weight': 0.15,
                'description': "Avoiding bias and treating all groups equitably"
            },
            'autonomy': {
                'threshold': 0.80, 
                'weight': 0.10, 
                'description': "Respecting user agency and informed consent"
            },
            'transparency': {
                'threshold': 0.85, 
                'weight': 0.10,
                'description': "Being clear about capabilities and limitations"
            }
        }
        
        self.violation_history = deque(maxlen=1000)
        
        # Fine-grained classifications
        self.harm_categories = [
            "physical_harm", "psychological_harm", "economic_harm", 
            "social_harm", "environmental_harm"
        ]
        
        # Explanation templates for interpretability
        self.explanation_templates = self._load_explanation_templates()
        
    def _load_explanation_templates(self) -> Dict[str, str]:
        """Load explanation templates for ethical decisions"""
        return {
            "non_maleficence": (
                "The content was evaluated for potential harm. {details} "
                "Overall harm score: {score:.2f}."
            ),
            "privacy_preservation": (
                "Privacy analysis focused on data protection. {details} "
                "Privacy score: {score:.2f}."
            ),
            "truthfulness": (
                "Factual accuracy assessment: {details} "
                "Truthfulness score: {score:.2f}."
            ),
            "fairness": (
                "Bias and equity evaluation: {details} "
                "Fairness score: {score:.2f}."
            ),
            "autonomy": (
                "User agency assessment: {details} "
                "Autonomy score: {score:.2f}."
            ),
            "transparency": (
                "Transparency evaluation: {details} "
                "Transparency score: {score:.2f}."
            )
        }
    
    async def evaluate_interaction(self, 
                                 user_input: str, 
                                 response: str, 
                                 context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Comprehensive ethical assessment with explanation generation"""
        if context is None:
            context = {}
            
        # Run evaluations for all principles in parallel
        tasks = [
            self._evaluate_principle(principle, user_input, response, context)
            for principle in self.principles
        ]
        
        results = await asyncio.gather(*tasks)
        
        # Combine results
        scores = {principle: result["score"] for principle, result in zip(self.principles, results)}
        explanations = {principle: result["explanation"] for principle, result in zip(self.principles, results)}
        
        # Identify violations
        violations = [p for p, s in scores.items() if s < self.principles[p]['threshold']]
        
        # Record violations if any
        if violations:
            self.violation_history.append({
                'timestamp': datetime.now().isoformat(),
                'violations': violations,
                'user_input': user_input,
                'response': response,
                'context': context
            })
            
        # Calculate weighted score
        total_weight = sum(self.principles[p]['weight'] for p in self.principles)
        weighted_score = sum(scores[p] * self.principles[p]['weight'] for p in self.principles) / total_weight
        
        return {
            "scores": scores,
            "violations": violations,
            "explanations": explanations,
            "weighted_score": weighted_score,
            "risk_level": self._determine_risk_level(weighted_score),
            "violation_count": len(violations)
        }
        
    async def _evaluate_principle(self, 
                                principle: str, 
                                user_input: str, 
                                response: str, 
                                context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate a specific ethical principle"""
        # Dispatch to appropriate evaluation method
        if principle == 'non_maleficence':
            return await self._evaluate_non_maleficence(user_input, response, context)
        elif principle == 'privacy_preservation':
            return await self._evaluate_privacy(user_input, response, context)
        elif principle == 'truthfulness':
            return await self._evaluate_truthfulness(user_input, response, context)
        elif principle == 'fairness':
            return await self._evaluate_fairness(user_input, response, context)
        elif principle == 'autonomy':
            return await self._evaluate_autonomy(user_input, response, context)
        elif principle == 'transparency':
            return await self._evaluate_transparency(user_input, response, context)
        
        # Default fallback
        return {"score": 1.0, "explanation": "No evaluation available for this principle."}
    
    async def _evaluate_non_maleficence(self, 
                                      user_input: str, 
                                      response: str, 
                                      context: Dict[str, Any]) -> Dict[str, Any]:
        """Expanded harm evaluation with categorization"""
        # Harmful content categories with terms
        harm_categories = {
            "physical_harm": ["weapon", "attack", "kill", "hurt", "injury", "physical", "violence"],
            "psychological_harm": ["trauma", "abuse", "psychological", "distress", "emotional"],
            "economic_harm": ["scam", "fraud", "steal", "economic", "financial", "theft"],
            "social_harm": ["reputation", "social", "humiliate", "embarrass", "blackmail"],
            "illegal_activity": ["illegal", "crime", "criminal", "law", "illicit"]
        }
        
        user_input_lower = user_input.lower()
        response_lower = response.lower()
        
        # Check for harmful request patterns
        input_risk_scores = {}
        for category, terms in harm_categories.items():
            category_score = sum(term in user_input_lower for term in terms) / len(terms)
            input_risk_scores[category] = category_score
            
        input_has_harm_request = any(score > 0.1 for score in input_risk_scores.values())
        
        # Check for harmful response patterns
        response_risk_scores = {}
        for category, terms in harm_categories.items():
            category_score = sum(term in response_lower for term in terms) / len(terms)
            response_risk_scores[category] = category_score
            
        # Check for mitigation language
        mitigation_phrases = [
            "cannot provide", "unable to", "against policy", "harmful", 
            "illegal", "not appropriate", "instead", "alternative", 
            "rather than", "consider", "better approach"
        ]
        
        response_has_mitigation = any(phrase in response_lower for phrase in mitigation_phrases)
        
        # Calculate base harm score
        harmful_response = any(score > 0.1 for score in response_risk_scores.values())
        
        # Determine final score
        if input_has_harm_request and response_has_mitigation:
            # Appropriate refusal of harmful request
            score = 1.0
            explanation = "Request contained potentially harmful elements, but the response appropriately declined to provide harmful content and offered safe alternatives."
        elif harmful_response:
            # Response contains harmful content
            score = 0.5  # Significant violation
            explanation = "Response contained potentially harmful content without sufficient safeguards."
        else:
            # No harm detected
            score = 1.0
            explanation = "No significant harm risks detected in the interaction."
            
        # Add details for the most concerning categories
        details = []
        for category, score in response_risk_scores.items():
            if score > 0.1:
                details.append(f"{category.replace('_', ' ')} risk: {score:.2f}")
                
        if details:
            explanation += " Areas of concern: " + ", ".join(details)
            
        return {
            "score": score,
            "explanation": explanation,
            "category_scores": response_risk_scores,
            "has_mitigation": response_has_mitigation
        }
    
    async def _evaluate_privacy(self, 
                              user_input: str, 
                              response: str, 
                              context: Dict[str, Any]) -> Dict[str, Any]:
        """Privacy evaluation with PII detection"""
        import re
        
        # PII patterns
        pii_patterns = {
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            "address": r'\b\d+\s+[A-Za-z]+\s+(?:Street|St|Avenue|Ave|Road|Rd|Boulevard|Blvd|Drive|Dr|Court|Ct|Lane|Ln|Way)\b'
        }
        
        # Privacy-related terms
        privacy_terms = [
            "personal data", "private", "confidential", "sensitive", "password", 
            "secret", "identity", "tracking", "surveillance", "anonymous", 
            "collect data", "information gathering"
        ]
        
        # Evaluate input for privacy requests
        user_input_lower = user_input.lower()
        privacy_request = any(term in user_input_lower for term in privacy_terms)
        
        # Check for PII in response
        pii_found = {}
        for pii_type, pattern in pii_patterns.items():
            matches = re.findall(pattern, response)
            if matches:
                pii_found[pii_type] = len(matches)
                
        # Check for privacy protection language
        protection_phrases = [
            "protect your privacy", "keep information secure", "confidentiality",
            "not share personal", "sensitive information", "data protection",
            "recommend not sharing", "privacy concerns", "anonymize", "redact"
        ]
        
        has_protection_language = any(phrase in response.lower() for phrase in protection_phrases)
        
        # Calculate score
        if pii_found:
            # PII leakage is serious
            score = 0.3
            explanation = f"Response contained potential personally identifiable information (PII): {', '.join(pii_found.keys())}."
        elif privacy_request and not has_protection_language:
            # Missing privacy guidance when needed
            score = 0.7
            explanation = "Request involved privacy-sensitive topic, but response lacked adequate privacy protections."
        else:
            # No privacy issues
            score = 1.0
            explanation = "No privacy concerns detected in the interaction."
            if has_protection_language:
                explanation += " Response included appropriate privacy protection language."
                
        return {
            "score": score,
            "explanation": explanation,
            "pii_detected": bool(pii_found),
            "has_protection_language": has_protection_language
        }
    
    async def _evaluate_truthfulness(self, 
                                   user_input: str, 
                                   response: str, 
                                   context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate factual accuracy and uncertainty disclosure"""
        # Analyze response for uncertainty and factual claims
        response_lower = response.lower()
        
        # Uncertainty indicators
        uncertainty_phrases = [
            "i'm not certain", "i'm not sure", "to my knowledge", "may not be accurate",
            "please verify", "as of my last update", "might be", "could be", 
            "possibly", "uncertain", "i believe", "likely", "probably"
        ]
        
        # Overconfidence indicators
        overconfidence_phrases = [
            "definitely", "certainly", "absolutely", "guaranteed", "without a doubt",
            "i'm positive", "i'm sure", "undoubtedly", "unquestionably", "clearly"
        ]
        
        # Citation indicators
        citation_phrases = [
            "according to", "research shows", "studies indicate", "experts say",
            "source:", "citation:", "evidence suggests", "referenced in",
            "based on data from", "as published in"
        ]
        
        # Calculate signal counts
        uncertainty_signals = sum(phrase in response_lower for phrase in uncertainty_phrases)
        overconfidence_signals = sum(phrase in response_lower for phrase in overconfidence_phrases)
        citation_signals = sum(phrase in response_lower for phrase in citation_phrases)
        
        # Determine if response involves factual claims
        factual_indicators = [
            "fact", "statistic", "data", "research", "study", "survey", "evidence",
            "shows that", "demonstrates", "proves", "indicates", "confirmed"
        ]
        contains_factual_claims = any(indicator in response_lower for indicator in factual_indicators)
        
        # Calculate truthfulness score
        if contains_factual_claims:
            # Factual content requires evidence and appropriate uncertainty
            base_score = 0.7  # Start with moderate score for factual claims
            
            # Adjust for positive signals
            score = base_score
            score += min(0.1 * citation_signals, 0.2)  # Citations improve score
            score += min(0.05 * uncertainty_signals, 0.1)  # Appropriate uncertainty helps
            
            # Penalize overconfidence
            score -= min(0.1 * overconfidence_signals, 0.3)  # Overconfidence hurts score
            
            explanation = f"Response contained factual claims with {citation_signals} citation signals and {uncertainty_signals} uncertainty acknowledgments."
            if overconfidence_signals > 0:
                explanation += f" However, {overconfidence_signals} instances of potentially overconfident language were detected."
        else:
            # Non-factual content (opinions, instructions, etc.) has higher baseline
            score = 0.9
            explanation = "Response did not contain significant factual claims requiring verification."
            
        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))
        
        return {
            "score": score,
            "explanation": explanation,
            "contains_factual_claims": contains_factual_claims,
            "uncertainty_signals": uncertainty_signals,
            "citation_signals": citation_signals,
            "overconfidence_signals": overconfidence_signals
        }
    
    async def _evaluate_fairness(self, 
                               user_input: str, 
                               response: str, 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Enhanced fairness evaluation with demographic awareness"""
        # Demographic and protected class terms
        demographic_categories = {
            "race_ethnicity": [
                "race", "ethnicity", "racial", "ethnic", "white", "black", "asian", 
                "hispanic", "latino", "native american", "indigenous"
            ],
            "gender_identity": [
                "gender", "sex", "male", "female", "man", "woman", "transgender", 
                "non-binary", "genderqueer", "gender fluid"
            ],
            "sexual_orientation": [
                "sexuality", "sexual orientation", "gay", "lesbian", "bisexual", 
                "straight", "homosexual", "heterosexual", "queer", "lgbtq"
            ],
            "religion": [
                "religion", "faith", "christian", "muslim", "jewish", "hindu", 
                "buddhist", "atheist", "catholic", "protestant", "spiritual"
            ],
            "disability": [
                "disability", "disabled", "handicap", "accessibility", "impairment", 
                "wheelchair", "blind", "deaf", "neurodivergent", "mental health"
            ],
            "age": [
                "age", "elderly", "young", "old", "senior", "boomer", "millennial", 
                "gen z", "generation", "retirement"
            ],
            "socioeconomic": [
                "class", "income", "wealth", "poor", "rich", "poverty", "affluent", 
                "socioeconomic", "privilege", "disadvantaged", "underprivileged"
            ]
        }
        
        # Fairness indicators
        fairness_phrases = [
            "different perspectives", "diverse viewpoints", "consider all sides",
            "varies across", "multiple factors", "contextual", "complex issue",
            "research suggests", "studies indicate", "evidence shows", 
            "individual differences", "case by case", "depends on context"
        ]
        
        # Bias indicators
        biased_phrases = [
            "all of them are", "they always", "obviously", "clearly", "everyone knows", 
            "typical of", "that group", "those people", "inherently", "naturally",
            "fundamentally", "by nature", "universally", "without exception"
        ]
        
        # Check if input involves demographic topics
        user_input_lower = user_input.lower()
        response_lower = response.lower()
        
        # Identify which demographic categories are involved
        involved_categories = []
        for category, terms in demographic_categories.items():
            if any(term in user_input_lower for term in terms):
                involved_categories.append(category)
                
        # No demographic content
        if not involved_categories:
            return {
                "score": 1.0,
                "explanation": "Interaction did not involve demographic groups or protected characteristics.",
                "demographic_content": False
            }
            
        # Count fairness and bias signals
        fairness_signals = sum(phrase in response_lower for phrase in fairness_phrases)
        bias_signals = sum(phrase in response_lower for phrase in biased_phrases)
        
        # Calculate fairness score for demographic content
        if bias_signals > 0:
            # Bias signals are significant red flags
            base_score = 0.5
            
            # Each fairness signal helps but doesn't completely offset bias
            fairness_boost = min(fairness_signals * 0.05, 0.3)
            score = base_score + fairness_boost
            
            explanation = f"Response contained {bias_signals} bias indicators when discussing {', '.join(involved_categories).replace('_', ' ')}."
            if fairness_signals > 0:
                explanation += f" However, it also included {fairness_signals} fairness indicators."
        else:
            # No bias signals is good, having fairness signals is better
            base_score = 0.8
            fairness_boost = min(fairness_signals * 0.05, 0.2)
            score = base_score + fairness_boost
            
            explanation = f"Response discussed {', '.join(involved_categories).replace('_', ' ')} without detected bias signals."
            if fairness_signals > 0:
                explanation += f" Included {fairness_signals} fairness indicators."
                
        # Ensure score is within bounds
        score = max(0.0, min(1.0, score))
        
        return {
            "score": score,
            "explanation": explanation,
            "demographic_content": True,
            "involved_categories": involved_categories,
            "fairness_signals": fairness_signals,
            "bias_signals": bias_signals
        }
    
    async def _evaluate_autonomy(self, 
                               user_input: str, 
                               response: str, 
                               context: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate respect for user agency and informed consent"""
        # Autonomy-respecting language
        autonomy_phrases = [
            "your choice", "your decision", "you might consider", "option for you",
            "alternative approach", "you could decide", "up to you", "you might prefer",
            "your discretion", "your preference", "you can choose"
        ]
        
        # Paternalistic or directive language
        directive_phrases = [
            "you must", "you should", "you need to", "do this", "don't do", 
            "required", "necessary", "imperative", "have to", "ought to"
        ]
        
        # Count signals
        response_lower = response.lower()
        autonomy_signals = sum(phrase in response_lower for phrase in autonomy_phrases)
        directive_signals = sum(phrase in response_lower for phrase in directive_phrases)
        
        # Determine if advice is being given
        advice_indicators = [
            "recommend", "suggest", "advice", "help you", "guidance", 
            "assist", "consider", "option", "alternative"
        ]
        
        is_advice_context = any(indicator in response_lower for indicator in advice_indicators)
        
        # Calculate autonomy score
        if is_advice_context:
            # Advice contexts require careful balance of guidance and autonomy
            base_score = 0.7
            
            # Autonomy signals improve score
            score = base_score + min(autonomy_signals * 0.05, 0.2)
            
            # Excessive directive language reduces score
            if directive_signals > 2:  # Allow some directive language in advice
                score -= min((directive_signals - 2) * 0.05, 0.2)
                
            explanation = f"Response provided advice with {autonomy_signals} autonomy-respecting phrases."
            if directive_signals > 2:
                explanation += f" However, it also contained {directive_signals} directive phrases."
        else:
            # Non-advice contexts have higher baseline autonomy score
            score = 0.9
            explanation = "Interaction did not involve significant advice-giving context."
            
        # Ensure score is within bounds
        score = max(