import tempfile
import os
import requests
import json
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from config import settings

class SpeechProcessorInterface(ABC):
    """Interface for speech processing providers"""
    
    @abstractmethod
    async def speech_to_text(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def text_to_speech(self, text: str, voice: str = "alloy", language: str = "en") -> Dict[str, Any]:
        pass

class WebSpeechAPIProcessor(SpeechProcessorInterface):
    """Lightweight processor that delegates to browser's Web Speech API"""
    
    async def speech_to_text(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        This method returns instructions for frontend to use Web Speech API
        Since Web Speech API runs in browser, we can't process server-side
        """
        try:
            # Input validation
            if not language or not isinstance(language, str):
                language = "en"
            
            if not audio_file_path:
                audio_file_path = ""
            
            return {
                "success": True,
                "method": "web_speech_api",
                "instructions": {
                    "api_type": "SpeechRecognition",
                    "language": language,
                    "continuous": False,
                    "interim_results": False,
                    "message": "Use browser's SpeechRecognition API on frontend"
                },
                "fallback_available": True
            }
        except Exception as e:
            print(f"Error in web speech API setup: {e}")
            return {
                "success": False,
                "error": str(e),
                "method": "web_speech_api",
                "fallback_available": False
            }
    
    async def text_to_speech(self, text: str, voice: str = "alloy", language: str = "en") -> Dict[str, Any]:
        """
        Returns instructions for frontend to use Web Speech API TTS
        """
        return {
            "success": True,
            "method": "web_speech_api",
            "instructions": {
                "api_type": "SpeechSynthesis",
                "text": text,
                "language": language,
                "voice": voice,
                "message": "Use browser's speechSynthesis API on frontend"
            },
            "fallback_available": True
        }

class LocalWhisperProcessor(SpeechProcessorInterface):
    """Local Whisper processing (heavier but more private)"""
    
    def __init__(self):
        self.whisper_available = False
        try:
            import whisper
            self.model = whisper.load_model("tiny")  # Use smallest model for speed
            self.whisper_available = True
        except ImportError:
            print("Whisper not available - install with: pip install openai-whisper")
    
    async def speech_to_text(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """Convert speech to text using local Whisper"""
        # Input validation
        if not audio_file_path or not isinstance(audio_file_path, str):
            return {
                "success": False,
                "error": "Invalid audio file path",
                "fallback_to": "web_speech_api"
            }
        
        if not self.whisper_available:
            return {
                "success": False,
                "error": "Local Whisper not available - install with: pip install openai-whisper",
                "fallback_to": "web_speech_api"
            }
        
        try:
            if not os.path.exists(audio_file_path):
                return {
                    "success": False,
                    "error": f"Audio file not found: {audio_file_path}",
                    "fallback_to": "web_speech_api"
                }
            
            if not language or not isinstance(language, str):
                language = "en"
            
            result = self.model.transcribe(audio_file_path, language=language)
            
            if result and "text" in result:
                return {
                    "success": True,
                    "text": result["text"],
                    "language": result.get("language", language),
                    "method": "local_whisper",
                    "segments": result.get("segments", [])
                }
            else:
                return {
                    "success": False,
                    "error": "No transcription returned",
                    "fallback_to": "web_speech_api"
                }
        except Exception as e:
            print(f"Whisper transcription error: {e}")
            return {
                "success": False,
                "error": f"Whisper error: {str(e)}",
                "fallback_to": "web_speech_api"
            }
    
    async def text_to_speech(self, text: str, voice: str = "alloy", language: str = "en") -> Dict[str, Any]:
        """Local Whisper doesn't support TTS"""
        return {
            "success": False,
            "error": "Local Whisper doesn't support TTS",
            "fallback_to": "web_speech_api"
        }

class HuggingFaceAPISpeechProcessor(SpeechProcessorInterface):
    """Use Hugging Face Inference API for speech processing"""
    
    def __init__(self):
        self.api_token = settings.HUGGINGFACE_TOKEN
        self.stt_api_url = "https://api-inference.huggingface.co/models/facebook/wav2vec2-base-960h"
        self.tts_api_url = "https://api-inference.huggingface.co/models/facebook/fastspeech2-en-ljspeech"
        self.headers = {"Authorization": f"Bearer {self.api_token}"} if self.api_token else {}
    
    async def speech_to_text(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """Convert speech to text using Hugging Face API"""
        if not self.api_token:
            return {
                "success": False,
                "error": "Hugging Face API token not configured",
                "fallback_to": "web_speech_api"
            }
        
        try:
            with open(audio_file_path, "rb") as audio_file:
                audio_data = audio_file.read()
            
            response = requests.post(
                self.stt_api_url,
                headers=self.headers,
                data=audio_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if isinstance(result, dict) and "text" in result:
                    return {
                        "success": True,
                        "text": result["text"],
                        "language": language,
                        "method": "huggingface_api",
                        "confidence": result.get("confidence", 0.8)
                    }
                elif isinstance(result, list) and len(result) > 0:
                    # Handle array response format
                    return {
                        "success": True,
                        "text": result[0].get("generated_text", ""),
                        "language": language,
                        "method": "huggingface_api"
                    }
            
            return {
                "success": False,
                "error": f"API request failed: {response.status_code}",
                "fallback_to": "web_speech_api"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_to": "web_speech_api"
            }
    
    async def text_to_speech(self, text: str, voice: str = "alloy", language: str = "en") -> Dict[str, Any]:
        """Convert text to speech using Hugging Face API"""
        if not self.api_token:
            return {
                "success": False,
                "error": "Hugging Face API token not configured",
                "fallback_to": "web_speech_api"
            }
        
        try:
            payload = {"inputs": text}
            
            response = requests.post(
                self.tts_api_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                # Save audio to temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
                    temp_file.write(response.content)
                    temp_file_path = temp_file.name
                
                return {
                    "success": True,
                    "audio_file_path": temp_file_path,
                    "text": text,
                    "voice": voice,
                    "language": language,
                    "method": "huggingface_api"
                }
            
            return {
                "success": False,
                "error": f"API request failed: {response.status_code}",
                "fallback_to": "web_speech_api"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_to": "web_speech_api"
            }

class WhisperWebProcessor(SpeechProcessorInterface):
    """Use Whisper via web service (lighter than local deployment)"""
    
    def __init__(self):
        # This could point to a hosted Whisper service
        self.whisper_api_url = "https://api.whisper.com/v1/transcribe"  # Example URL
    
    async def speech_to_text(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """
        Placeholder for Whisper web service
        In production, this would connect to a hosted Whisper instance
        """
        try:
            # Mock response for demonstration
            return {
                "success": True,
                "text": "Mock transcription from Whisper Web Service",
                "language": language,
                "method": "whisper_web",
                "note": "This is a placeholder - connect to actual Whisper service"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback_to": "web_speech_api"
            }
    
    async def text_to_speech(self, text: str, voice: str = "alloy", language: str = "en") -> Dict[str, Any]:
        """
        Whisper is primarily STT, so this falls back to other methods
        """
        return {
            "success": False,
            "error": "Whisper doesn't support TTS",
            "fallback_to": "web_speech_api"
        }

class SpeechAnalyzer:
    """Lightweight speech analysis without heavy ML dependencies"""
    
    def __init__(self):
        pass
    
    async def analyze_speech_errors(self, transcribed_text: str, expected_text: str = None) -> Dict[str, Any]:
        """Analyze speech for pronunciation and fluency errors"""
        errors = []
        
        if expected_text:
            accuracy = self._calculate_accuracy(transcribed_text, expected_text)
            word_errors = self._find_word_differences(transcribed_text, expected_text)
            errors.extend(word_errors)
        else:
            accuracy = 85.0  # Default when no expected text
        
        # Check for common speech patterns
        pattern_errors = self._check_speech_patterns(transcribed_text)
        errors.extend(pattern_errors)
        
        return {
            "success": True,
            "transcribed_text": transcribed_text,
            "expected_text": expected_text,
            "errors": errors,
            "accuracy": accuracy,
            "error_count": len(errors),
            "analysis_type": "lightweight"
        }
    
    def _calculate_accuracy(self, transcribed: str, expected: str) -> float:
        """Calculate word-level accuracy"""
        transcribed_words = transcribed.lower().split()
        expected_words = expected.lower().split()
        
        if not expected_words:
            return 0.0
        
        correct_words = sum(1 for t, e in zip(transcribed_words, expected_words) if t == e)
        return round((correct_words / len(expected_words)) * 100, 2)
    
    def _find_word_differences(self, transcribed: str, expected: str) -> list:
        """Find word-level differences"""
        errors = []
        transcribed_words = transcribed.lower().split()
        expected_words = expected.lower().split()
        
        for i, (trans, exp) in enumerate(zip(transcribed_words, expected_words)):
            if trans != exp:
                errors.append({
                    "type": "pronunciation_error",
                    "position": i,
                    "said": trans,
                    "expected": exp,
                    "suggestion": f"Practice saying '{exp}' instead of '{trans}'"
                })
        
        return errors
    
    def _check_speech_patterns(self, text: str) -> list:
        """Check for common dyslexic speech patterns"""
        import re
        errors = []
        
        # Check for word repetitions
        repetitions = re.findall(r'\b(\w+)\s+\1\b', text.lower())
        for rep in repetitions:
            errors.append({
                "type": "word_repetition",
                "word": rep,
                "suggestion": f"Try saying '{rep}' only once"
            })
        
        # Check for filler words (excessive use)
        fillers = ["um", "uh", "like", "you know"]
        words = text.lower().split()
        filler_count = sum(1 for word in words if word in fillers)
        
        if filler_count > len(words) * 0.1:  # More than 10% fillers
            errors.append({
                "type": "excessive_fillers",
                "count": filler_count,
                "suggestion": "Try to reduce filler words for clearer speech"
            })
        
        return errors

class SpeechProcessorFactory:
    """Factory to create speech processor based on configuration"""
    
    @staticmethod
    def create_processor() -> SpeechProcessorInterface:
        provider = getattr(settings, 'SPEECH_PROVIDER', 'web_speech_api')
        
        if provider == "web_speech_api":
            return WebSpeechAPIProcessor()
        elif provider == "huggingface_api":
            return HuggingFaceAPISpeechProcessor()
        elif provider == "whisper_web":
            return WhisperWebProcessor()
        elif provider == "local_whisper":
            return LocalWhisperProcessor()
        else:
            # Default fallback
            return WebSpeechAPIProcessor()

class SpeechProcessorAlternative:
    """Alternative speech processor that combines multiple providers"""
    
    def __init__(self):
        self.processor = SpeechProcessorFactory.create_processor()
        self.analyzer = SpeechAnalyzer()
    
    async def process_speech_to_text(self, audio_file_path: str, language: str = "en") -> Dict[str, Any]:
        """Process speech to text with fallback options"""
        return await self.processor.speech_to_text(audio_file_path, language)
    
    async def process_text_to_speech(self, text: str, voice: str = "alloy", language: str = "en") -> Dict[str, Any]:
        """Process text to speech with fallback options"""
        return await self.processor.text_to_speech(text, voice, language)
    
    async def analyze_speech(self, transcribed_text: str, expected_text: str = None) -> Dict[str, Any]:
        """Analyze speech for errors and patterns"""
        return await self.analyzer.analyze_speech_errors(transcribed_text, expected_text)

# Initialize the speech processor and analyzer
speech_processor = SpeechProcessorFactory.create_processor()
speech_analyzer = SpeechAnalyzer()
