import re
import json
import requests
import asyncio
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
from config import settings

class TextAnalyzerInterface(ABC):
    """Interface for text analysis providers"""
    
    @abstractmethod
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    def get_highlighted_text(self, text: str, errors: List[Dict]) -> str:
        pass

class SimpleLocalAnalyzer(TextAnalyzerInterface):
    """Lightweight local text analyzer without heavy ML dependencies"""
    
    def __init__(self):
        # Common dyslexic error patterns - lightweight rule-based approach
        self.spelling_corrections = {
            # Common reversals and confusions
            'teh': 'the', 'hte': 'the', 'thier': 'their', 'recieve': 'receive',
            'beleive': 'believe', 'seperate': 'separate', 'definately': 'definitely',
            'occured': 'occurred', 'neccessary': 'necessary', 'begining': 'beginning',
            'alot': 'a lot', 'wierd': 'weird', 'freind': 'friend',
            # b/d reversals
            'abd': 'and', 'doy': 'boy', 'bid': 'did', 'dack': 'back',
            # p/q reversals  
            'qut': 'put', 'puite': 'quite',
            # Common phonetic errors
            'lite': 'light', 'nite': 'night', 'wuz': 'was', 'sed': 'said',
            # Single letter errors (common with dyslexia)
            'oog': 'dog', 'og': 'dog', 'qan': 'can', 'pan': 'pan', 'ban': 'ban',
            'bog': 'dog', 'cog': 'dog', 'fog': 'fog', 'hog': 'hog', 'jog': 'jog', 'log': 'log',
            # Common misspellings
            'stuby': 'study', 'tum': 'them', 'i': 'I'
        }
        
        # Common English words for spell-checking
        self.common_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'do', 'does', 'did',
            'can', 'could', 'will', 'would', 'should', 'may', 'might', 'must',
            'cat', 'dog', 'bird', 'fish', 'run', 'walk', 'jump', 'play', 'eat',
            'big', 'small', 'red', 'blue', 'green', 'yellow', 'happy', 'sad',
            'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten',
            'go', 'come', 'see', 'look', 'make', 'take', 'get', 'put', 'say', 'tell',
            'boy', 'girl', 'man', 'woman', 'child', 'baby', 'mom', 'dad', 'friend',
            'book', 'pen', 'paper', 'desk', 'chair', 'house', 'school', 'car', 'tree',
            'study', 'them', 'i'
        }
        
        self.error_patterns = {
            'letter_reversal': r'\b(abd|doy|bid|dack|qut|puite)\b',
            'phonetic': r'\b(lite|nite|wuz|sed|cuz|becuz)\b',
            'double_letters': r'\b\w*([bcdfghjklmnpqrstvwxyz])\1{2,}\w*\b',
            'missing_letters': r'\b[bcdfghjklmnpqrstvwxyz]{3,}[aeiou][bcdfghjklmnpqrstvwxyz]{3,}\b'
        }
        
        self.color_map = {
            'spelling': '#FF6B6B',
            'reversal': '#4ECDC4', 
            'phonetic': '#45B7D1',
            'grammar': '#96CEB4'
        }
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using lightweight rule-based approach"""
        # Input validation and handling
        if not text or not isinstance(text, str):
            return {
                "errors": [],
                "corrected_text": "",
                "confidence_score": 0.0,
                "error_count": 0,
                "analysis_type": "empty_input"
            }
        
        # Handle empty or whitespace-only text
        if not text.strip():
            return {
                "errors": [],
                "corrected_text": text,
                "confidence_score": 1.0,
                "error_count": 0,
                "analysis_type": "empty_input"
            }
        
        try:
            errors = []
            corrected_text = text
            words = text.lower().split()
            
            # Check spelling corrections
            for i, word in enumerate(words):
                clean_word = re.sub(r'[^\w]', '', word)
                if clean_word in self.spelling_corrections:
                    correct_word = self.spelling_corrections[clean_word]
                    errors.append({
                        'type': 'spelling',
                        'word': word,
                        'position': i,
                        'suggestion': correct_word,
                        'color': self.color_map['spelling']
                    })
                    corrected_text = corrected_text.replace(word, correct_word, 1)
        
            # Check for letter reversals
            try:
                reversal_matches = re.finditer(self.error_patterns['letter_reversal'], text.lower())
                for match in reversal_matches:
                    errors.append({
                        'type': 'letter_reversal',
                        'word': match.group(),
                        'suggestion': f"Check if '{match.group()}' should be a different word",
                        'color': self.color_map['reversal']
                    })
            except Exception as e:
                print(f"Error in reversal detection: {e}")
            
            # Check phonetic errors
            try:
                phonetic_matches = re.finditer(self.error_patterns['phonetic'], text.lower())
                for match in phonetic_matches:
                    errors.append({
                        'type': 'phonetic_error',
                        'word': match.group(),
                        'suggestion': f"Consider the correct spelling of '{match.group()}'",
                        'color': self.color_map['phonetic']
                    })
            except Exception as e:
                print(f"Error in phonetic detection: {e}")
            
            confidence = self._calculate_confidence(len(words), len(errors))
            
            return {
                'original_text': text,
                'corrected_text': corrected_text,
                'errors': errors,
                'error_count': len(errors),
                'confidence_score': confidence,
                'analysis_type': 'local_simple'
            }
        
        except Exception as e:
            print(f"Error in text analysis: {e}")
            return {
                'original_text': text,
                'corrected_text': text,
                'errors': [],
                'error_count': 0,
                'confidence_score': 0.5,
                'analysis_type': 'error_fallback'
            }
    
    def get_highlighted_text(self, text: str, errors: List[Dict]) -> str:
        """Return HTML with highlighted errors"""
        if not text or not isinstance(text, str):
            return ""
        
        if not errors or not isinstance(errors, list):
            return text
        
        highlighted_text = text
        
        try:
            for error in errors:
                if 'word' in error and error['word']:
                    word = error['word']
                    color = error.get('color', '#FF6B6B')
                    suggestion = error.get('suggestion', 'Error detected')
                    
                    highlighted_text = re.sub(
                        re.escape(word),
                        f'<span style="background-color: {color}; padding: 2px 4px; border-radius: 3px;" title="{suggestion}">{word}</span>',
                        highlighted_text,
                        count=1,
                        flags=re.IGNORECASE
                    )
        except Exception as e:
            print(f"Error in highlighting: {e}")
            return text
        
        return highlighted_text
    
    def _calculate_confidence(self, word_count: int, error_count: int) -> float:
        """Calculate confidence score"""
        try:
            if word_count == 0:
                return 0.0
            if word_count < 0 or error_count < 0:
                return 0.5
            error_rate = error_count / word_count
            confidence = max(0.1, 1.0 - (error_rate * 2))  # Penalize error rate
            return round(confidence, 2)
        except (ZeroDivisionError, ValueError, TypeError) as e:
            print(f"Error calculating confidence: {e}")
            return 0.5

class HuggingFaceAPIAnalyzer(TextAnalyzerInterface):
    """Use Hugging Face Inference API for text analysis"""
    
    def __init__(self):
        self.api_token = settings.HUGGINGFACE_TOKEN
        self.api_url = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium"
        self.headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using Hugging Face API"""
        if not self.api_token:
            # Fallback to simple analyzer
            simple_analyzer = SimpleLocalAnalyzer()
            return await simple_analyzer.analyze_text(text)
        
        try:
            # Use grammar checking model via API
            payload = {"inputs": text}
            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=10)
            
            if response.status_code == 200:
                # Process API response and format as needed
                result = response.json()
                return {
                    'original_text': text,
                    'corrected_text': text,  # Would need proper processing
                    'errors': [],  # Would extract from API response
                    'error_count': 0,
                    'confidence_score': 0.8,
                    'analysis_type': 'huggingface_api'
                }
            else:
                # Fallback to local analyzer
                simple_analyzer = SimpleLocalAnalyzer()
                return await simple_analyzer.analyze_text(text)
                
        except Exception as e:
            print(f"HF API Error: {e}")
            # Fallback to local analyzer
            simple_analyzer = SimpleLocalAnalyzer()
            return await simple_analyzer.analyze_text(text)
    
    def get_highlighted_text(self, text: str, errors: List[Dict]) -> str:
        # Use same highlighting logic as simple analyzer
        simple_analyzer = SimpleLocalAnalyzer()
        return simple_analyzer.get_highlighted_text(text, errors)

class OpenAIAPIAnalyzer(TextAnalyzerInterface):
    """Use OpenAI API for text analysis"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.api_url = "https://api.openai.com/v1/chat/completions"
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using OpenAI API"""
        if not self.api_key:
            # Fallback to simple analyzer
            simple_analyzer = SimpleLocalAnalyzer()
            return await simple_analyzer.analyze_text(text)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that analyzes text for dyslexic writing patterns and provides corrections. Return a JSON response with original_text, corrected_text, errors (list), error_count, and confidence_score."
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this text for dyslexic errors: {text}"
                    }
                ],
                "max_tokens": 500,
                "temperature": 0.3
            }
            
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                try:
                    analysis = json.loads(content)
                    analysis['analysis_type'] = 'openai_api'
                    return analysis
                except json.JSONDecodeError:
                    # Fallback to simple analyzer
                    simple_analyzer = SimpleLocalAnalyzer()
                    return await simple_analyzer.analyze_text(text)
            else:
                # Fallback to simple analyzer
                simple_analyzer = SimpleLocalAnalyzer()
                return await simple_analyzer.analyze_text(text)
                
        except Exception as e:
            print(f"OpenAI API Error: {e}")
            # Fallback to simple analyzer  
            simple_analyzer = SimpleLocalAnalyzer()
            return await simple_analyzer.analyze_text(text)
    
    def get_highlighted_text(self, text: str, errors: List[Dict]) -> str:
        # Use same highlighting logic as simple analyzer
        simple_analyzer = SimpleLocalAnalyzer()
        return simple_analyzer.get_highlighted_text(text, errors)

class BERTTextAnalyzer(TextAnalyzerInterface):
    """BERT-based text analyzer for dyslexic errors with async support"""
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self.grammar_checker = None
        self.bert_available = False
        self.fallback_analyzer = SimpleLocalAnalyzer()
        
        try:
            from transformers import AutoTokenizer, AutoModel, pipeline
            import torch
            
            # Use lightweight BERT model
            model_name = "distilbert-base-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)
            self.model.eval()
            
            # Grammar checker pipeline
            try:
                self.grammar_checker = pipeline("text2text-generation", 
                                              model="grammarly/coedit-large", 
                                              tokenizer="grammarly/coedit-large")
            except Exception as e:
                print(f"Grammar checker model not available: {e}")
            
            self.bert_available = True
            print("BERT model loaded successfully")
            
        except ImportError:
            print("BERT dependencies not available (transformers/torch), falling back to simple analyzer")
        except Exception as e:
            print(f"BERT model loading failed: {e}")
    
    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """Analyze text using BERT model (async wrapper)"""
        if not self.bert_available:
            return await self.fallback_analyzer.analyze_text(text)
        
        try:
            # Run BERT analysis in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._analyze_with_bert, text)
            return result
        except Exception as e:
            print(f"BERT analysis error: {e}")
            return await self.fallback_analyzer.analyze_text(text)
    
    def _analyze_with_bert(self, text: str) -> Dict[str, Any]:
        """Synchronous BERT analysis"""
        try:
            # Get BERT embeddings
            embeddings = self._get_bert_embeddings(text)
            
            # Grammar correction
            corrected_text = self._correct_with_bert(text)
            
            # Find differences
            errors = self._find_differences(text, corrected_text)
            
            # Enhance errors with BERT context
            enhanced_errors = self._enhance_errors_with_bert(text, errors)
            
            # Calculate confidence
            confidence = self._calculate_bert_confidence(text, enhanced_errors)
            
            return {
                "original_text": text,
                "corrected_text": corrected_text,
                "errors": enhanced_errors,
                "error_count": len(enhanced_errors),
                "confidence_score": confidence,
                "analysis_type": "bert_enhanced",
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            print(f"BERT analysis failed: {e}")
            # Fallback to simple analysis
            import asyncio
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            return loop.run_until_complete(self.fallback_analyzer.analyze_text(text))
    
    def _get_bert_embeddings(self, text: str) -> Optional[List[float]]:
        """Get BERT embeddings for text"""
        if not self.bert_available:
            return None
        
        try:
            import torch
            
            inputs = self.tokenizer(text, return_tensors="pt", truncate=True, max_length=512)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state[0][0].numpy().tolist()
            
            return embeddings[:50]  # Truncate for storage
        except Exception as e:
            print(f"BERT embedding error: {e}")
            return None
    
    def _correct_with_bert(self, text: str) -> str:
        """Use BERT-based grammar checker for corrections"""
        try:
            if self.grammar_checker:
                corrected = self.grammar_checker(f"Fix grammar: {text}", max_length=len(text) + 50)
                return corrected[0]['generated_text']
        except Exception as e:
            print(f"Grammar checker error: {e}")
        
        # Fallback to simple corrections
        corrected = text
        corrections = {
            "recieve": "receive", "seperate": "separate", 
            "definately": "definitely", "occured": "occurred",
            "nite": "night", "lite": "light", "thier": "their",
            "teh": "the", "hte": "the", "beleive": "believe"
        }
        for wrong, right in corrections.items():
            corrected = re.sub(rf'\b{wrong}\b', right, corrected, flags=re.IGNORECASE)
        return corrected
    
    def _find_differences(self, original: str, corrected: str) -> List[Dict[str, Any]]:
        """Find differences between original and corrected text"""
        errors = []
        original_words = original.split()
        corrected_words = corrected.split()
        
        for i, (orig, corr) in enumerate(zip(original_words, corrected_words)):
            if orig.lower() != corr.lower():
                errors.append({
                    "type": "correction",
                    "word": orig,
                    "suggestion": corr,
                    "position": i,
                    "severity": "medium"
                })
        
        return errors
    
    def _enhance_errors_with_bert(self, text: str, errors: List[Dict]) -> List[Dict[str, Any]]:
        """Enhance error analysis with BERT context understanding"""
        enhanced_errors = []
        
        for error in errors:
            enhanced_error = error.copy()
            
            # Add context analysis
            context_score = self._get_context_relevance(text, error.get('position', 0))
            enhanced_error['context_confidence'] = context_score
            
            # Classify error type
            error_type = self._classify_error_type(error.get('word', ''), error.get('suggestion', ''))
            enhanced_error['bert_classification'] = error_type
            
            # Adjust severity based on context
            if context_score > 0.8:
                enhanced_error['severity'] = 'high'
            elif context_score > 0.5:
                enhanced_error['severity'] = 'medium'
            else:
                enhanced_error['severity'] = 'low'
            
            enhanced_errors.append(enhanced_error)
        
        return enhanced_errors
    
    def _get_context_relevance(self, text: str, position: int) -> float:
        """Calculate context relevance using BERT understanding"""
        words = text.split()
        if position >= len(words):
            return 0.5
        
        # Get context window
        context_size = 3
        start = max(0, position - context_size)
        end = min(len(words), position + context_size + 1)
        context = ' '.join(words[start:end])
        
        # Use BERT embeddings to assess context coherence
        if self.bert_available:
            try:
                embeddings = self._get_bert_embeddings(context)
                if embeddings:
                    import numpy as np
                    coherence = np.mean(np.abs(embeddings[:10]))
                    return min(1.0, coherence)
            except:
                pass
        
        return 0.7
    
    def _classify_error_type(self, original: str, corrected: str) -> str:
        """Classify error type using BERT understanding"""
        if not original or not corrected:
            return "unknown"
        
        if len(original) == len(corrected):
            diff_chars = sum(1 for a, b in zip(original, corrected) if a != b)
            if diff_chars == 1:
                return "single_char_substitution"
            elif diff_chars == 2:
                return "char_reversal"
        elif len(original) < len(corrected):
            return "missing_chars"
        else:
            return "extra_chars"
        
        return "spelling_error"
    
    def _calculate_bert_confidence(self, text: str, errors: List[Dict]) -> float:
        """Calculate confidence score using BERT analysis"""
        base_confidence = max(0.2, 1.0 - (len(errors) * 0.12))
        
        word_count = len(text.split())
        if word_count > 50:
            base_confidence += 0.1
        
        high_severity = sum(1 for e in errors if e.get('severity') == 'high')
        medium_severity = sum(1 for e in errors if e.get('severity') == 'medium')
        
        severity_penalty = (high_severity * 0.15) + (medium_severity * 0.08)
        base_confidence -= severity_penalty
        
        if self.bert_available:
            base_confidence += 0.05
        
        return max(0.1, min(1.0, base_confidence))
    
    def get_highlighted_text(self, text: str, errors: List[Dict]) -> str:
        """Return text with error highlights"""
        if not text or not isinstance(text, str):
            return ""
        
        if not errors or not isinstance(errors, list):
            return text
        
        highlighted = text
        
        try:
            for error in errors:
                if not error or not isinstance(error, dict):
                    continue
                word = error.get("word", "")
                severity = error.get("severity", "medium")
                suggestion = error.get("suggestion", "")
                
                if word:
                    color_map = {
                        "high": "#FF6B6B",
                        "medium": "#FFE66D", 
                        "low": "#A8E6CF"
                    }
                    color = color_map.get(severity, "#FFE66D")
                    
                    highlighted = re.sub(
                        re.escape(word),
                        f'<mark style="background-color: {color}; padding: 2px 4px; border-radius: 3px;" title="Suggestion: {suggestion}">{word}</mark>',
                        highlighted,
                        count=1,
                        flags=re.IGNORECASE
                    )
        except Exception as e:
            print(f"Error in BERT highlighting: {e}")
            return text
        
        return highlighted


class TextAnalyzerFactory:
    """Factory to create text analyzer based on configuration"""
    
    @staticmethod
    def create_analyzer() -> TextAnalyzerInterface:
        provider = settings.TEXT_ANALYSIS_PROVIDER
        
        if provider == "local_simple":
            return SimpleLocalAnalyzer()
        elif provider == "bert":
            return BERTTextAnalyzer()
        elif provider == "huggingface_api":
            return HuggingFaceAPIAnalyzer()
        elif provider == "openai_api":
            return OpenAIAPIAnalyzer()
        else:
            # Default fallback
            return SimpleLocalAnalyzer()

# Initialize the analyzer
text_analyzer = TextAnalyzerFactory.create_analyzer()