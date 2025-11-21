"""
Enhanced AI Tutor for Dyslexic Students
Provides intelligent, adaptive responses based on user needs and learning context
Integrates with text_analysis, handwriting_recognition, and speech_processing models
"""

import re
import json
import asyncio
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import random
from .lesson_content import lesson_manager

class AITutor:
    """Intelligent AI tutor that provides personalized learning support"""
    
    def __init__(self):
        self.conversation_history = {}  # Store per user session: {user_id: {session_id: [messages]}}
        self.current_sessions = {}  # Track current session per user: {user_id: session_id}
        self.user_progress = {}
        self.learning_preferences = {}
        self.active_exercises = {}  # Track active exercises per user
        self.last_practice_words = {}  # Track last given practice words per user
        
        # Enhanced conversation tracking
        self.conversation_context = {}  # Track conversation context per user
        self.conversation_turns = {}  # Track conversation turns for natural flow
        self.user_names = {}  # Store user names for personalization
        self.last_topics = {}  # Track what was discussed last
        
        self.response_templates = self._initialize_response_templates()
        self.encouragement_phrases = self._initialize_encouragement()
        self.error_explanations = self._initialize_error_explanations()
        
        # Initialize integrated models
        self.text_analyzer = None
        self.handwriting_recognizer = None
        self.speech_processor = None
        self._initialize_models()
        
        # API configuration
        self.api_enabled = False
        self.api_url = ""
        self.api_key = ""
        self._initialize_api_config()
    
    def _initialize_models(self):
        """Initialize integrated ML models"""
        try:
            from .text_analysis import text_analyzer
            self.text_analyzer = text_analyzer
            analyzer_type = getattr(text_analyzer, '__class__', type(text_analyzer)).__name__
            print(f"[AI_TUTOR] Text analyzer loaded successfully: {analyzer_type}")
        except Exception as e:
            print(f"[AI_TUTOR] Text analyzer initialization failed: {e}")
        
        try:
            from .handwriting_recognition import handwriting_recognizer
            self.handwriting_recognizer = handwriting_recognizer
            print("[AI_TUTOR] Handwriting recognizer loaded successfully")
        except Exception as e:
            print(f"[AI_TUTOR] Handwriting recognizer initialization failed: {e}")
        
        try:
            from .speech_processing_alternative import SpeechProcessorAlternative
            self.speech_processor = SpeechProcessorAlternative()
            print("[AI_TUTOR] Speech processor loaded successfully")
        except Exception as e:
            print(f"[AI_TUTOR] Speech processor initialization failed: {e}")
    
    def _initialize_api_config(self):
        """Initialize API configuration for chat responses"""
        import os
        from dotenv import load_dotenv
        load_dotenv()
        
        self.api_enabled = os.getenv('AI_API_ENABLED', 'false').lower() == 'true'
        self.api_url = os.getenv('AI_API_URL', 'https://api.openai.com/v1/chat/completions')
        self.api_key = os.getenv('AI_API_KEY', '')
        
        # Validate API key if enabled
        if self.api_enabled and not self.api_key:
            print("[AI_TUTOR] Warning: AI_API_ENABLED=true but no API key found")
            self.api_enabled = False
        
        print(f"[AI_TUTOR] API configuration initialized (enabled: {self.api_enabled})")
    
    def _initialize_response_templates(self) -> Dict[str, List[str]]:
        """Initialize response templates for different scenarios"""
        return {
            "greeting": [
                "Hello! I'm here to help you with your learning journey. What would you like to work on today?",
                "Hi there! Ready to learn something new? I'm excited to help you!",
                "Welcome back! Let's continue building your reading and writing skills together."
            ],
            "encouragement": [
                "You're doing great! Keep up the excellent work!",
                "I can see you're really trying hard. That's what matters most!",
                "Every mistake is a learning opportunity. You're getting better!",
                "Your progress is amazing! I'm proud of how hard you're working."
            ],
            "error_support": [
                "That's a common mistake! Let me help you understand why.",
                "No worries! Everyone makes mistakes while learning. Let's work through this together.",
                "I notice you're having trouble with this. Let me break it down for you.",
                "That's actually a really good attempt! Here's how we can make it even better."
            ],
            "spelling_error": [
                "I see a spelling opportunity here! Let's work on this word together.",
                "Great attempt! The word is spelled slightly differently. Let me show you.",
                "You're close! Let's practice the correct spelling together."
            ],
            "lesson_suggestion": [
                "Based on what we've been working on, I think you'd benefit from practicing {}.",
                "You're ready for the next challenge! How about we try {}?",
                "I have a great lesson that will help with this: {}. Would you like to try it?"
            ],
            "comprehension_check": [
                "Can you tell me what you understood from that?",
                "What do you think is the main idea here?",
                "How would you explain this to a friend?",
                "What questions do you have about what we just learned?"
            ]
        }
    
    def _initialize_encouragement(self) -> Dict[str, List[str]]:
        """Initialize encouragement phrases based on achievement level"""
        return {
            "high_achievement": [
                "Wow! You're really mastering this skill!",
                "Excellent work! You're becoming a reading superstar!",
                "Outstanding! Your hard work is really paying off!",
                "Incredible progress! You should be very proud of yourself!"
            ],
            "good_progress": [
                "Great job! You're making steady progress!",
                "Nice work! I can see you're getting better at this!",
                "Good effort! You're on the right track!",
                "Well done! Keep practicing and you'll master this!"
            ],
            "needs_support": [
                "You're working hard, and that's what counts!",
                "Don't give up! Learning takes time and practice!",
                "I believe in you! Let's try a different approach!",
                "Every expert was once a beginner. You're doing fine!"
            ],
            "breakthrough_moment": [
                "Yes! You got it! That 'aha' moment is so exciting!",
                "Perfect! You just had a breakthrough!",
                "Fantastic! Something just clicked for you, didn't it?",
                "Amazing! You figured it out all by yourself!"
            ]
        }
    
    def _initialize_error_explanations(self) -> Dict[str, Dict[str, str]]:
        """Initialize explanations for common dyslexic errors"""
        return {
            "letter_reversal": {
                "explanation": "Letter reversals like 'b' and 'd' are very common. Your brain is still learning the difference!",
                "strategy": "Try using your hands: make a 'b' with your left hand (thumb up) and 'd' with your right hand.",
                "practice": "Let's practice with some fun activities to help your brain remember the difference."
            },
            "phonetic_spelling": {
                "explanation": "You're spelling the word exactly how it sounds! That shows good phonetic awareness.",
                "strategy": "Some words don't follow the rules. These are called 'sight words' and we need to memorize them.",
                "practice": "Let's practice this word using the look-say-cover-write-check method."
            },
            "word_omission": {
                "explanation": "Sometimes when we read fast, we skip words. This is normal!",
                "strategy": "Try using your finger or a bookmark to track each word as you read.",
                "practice": "Let's practice reading more slowly and checking that we read every word."
            },
            "sequence_confusion": {
                "explanation": "Getting letters or sounds mixed up in order is common with dyslexia.",
                "strategy": "Let's break the word into smaller parts and practice each part separately.",
                "practice": "We can use clapping or tapping to help remember the correct sequence."
            },
            "spelling_error": {
                "explanation": "Spelling can be tricky! Let's work on this word together.",
                "strategy": "Break the word into syllables and practice each part.",
                "practice": "Let's use the look-say-cover-write-check method to master this word."
            }
        }
    
    def analyze_user_input(self, message: str, user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Analyze user input to determine intent and appropriate response"""
        message_lower = message.lower().strip()
        
        analysis = {
            "intent": self._determine_intent(message_lower, message),
            "emotion": self._detect_emotion(message_lower),
            "learning_need": self._identify_learning_need(message_lower),
            "difficulty_level": self._assess_difficulty_level(message, user_context),
            "errors": self._identify_errors_with_text_analyzer(message),
            "strengths": self._identify_strengths(message),
            "is_short_input": len(message.split()) <= 3,
            "word_count": len(message.split())
        }
        
        return analysis
    
    def _determine_intent(self, message_lower: str, original_message: str) -> str:
        """Determine user's intent from their message"""
        # Priority order matters - check specific intents first
        
        # Greeting (exact match)
        if re.match(r"^(hello|hi|hey|good morning|good afternoon|good evening)[\s!,.]*$", message_lower):
            return "greeting"
        
        # Word request (HIGHEST PRIORITY - check before anything else)
        word_request_patterns = [
            r"different\s+words",
            r"other\s+words",
            r"more\s+words",
            r"new\s+words",
            r"another\s+word",
            r"give.*words",
            r"\d+\s+words",
            r"words\s+to\s+practice",
            r"practice\s+words"
        ]
        if any(re.search(pattern, message_lower) for pattern in word_request_patterns):
            return "word_request"
        
        # Help request (only if explicitly asking for help)
        if re.search(r"\bhelp me\b|\bneed help\b|\bcan you help\b|\bdon't understand\b|\bconfused\b|\bhow do i\b", message_lower):
            return "help_request"
        
        # Practice request (including "practice more words")
        if re.search(r"\bpractice\b.*\bwords\b|\bmore\b.*\bwords\b|\bexercise\b|\bwork on\b|\blearn\b|\bstudy\b|\btrain\b", message_lower):
            # Check if it's specifically asking for words
            if re.search(r"\bpractice\b.*\bwords\b|\bmore\b.*\bwords\b|\bdifferent\b.*\bwords\b|\bother\b.*\bwords\b|\bnew\b.*\bwords\b", message_lower):
                return "word_request"
            return "practice_request"
        
        # Question (has question words and question mark or starts with question word)
        if re.search(r"\?", message_lower) or re.match(r"^(what|how|why|when|where|can you|could you|will you|should i|do i)\b", message_lower):
            return "question"
        
        # Sharing work or progress update
        if re.search(r"\bwrote\b|\bread\b|\bfinished\b|\bcompleted\b|\bcheck this\b|\bi (read|wrote|made|did|finished|completed)", message_lower):
            return "sharing_work"
        
        # Frustration
        if re.search(r"\bfrustrated\b|\bangry\b|\bcan't do\b|\bgive up\b|\btoo hard\b|\btoo difficult\b", message_lower):
            return "frustration"
        
        # Celebration
        if re.search(r"\bdid it\b|\bgot it\b|\byay\b|\bawesome\b|\bamazing\b", message_lower):
            return "celebration"
        
        # Spelling check
        if re.search(r"\bspell\b|\bspelling\b|\bis this right\b|\bhow do you spell\b|\bcorrect\b", message_lower) and len(original_message.split()) > 2:
            return "spelling_check"
        
        # Short text submission (1-3 words, no special keywords)
        if len(original_message.split()) <= 3 and len(original_message) > 0:
            # Exclude if it's just "help" or other command words
            if message_lower not in ["help", "hi", "hello", "hey", "practice", "exercise"]:
                return "short_text_submission"
        
        return "general"
    
    def _detect_emotion(self, message: str) -> str:
        """Detect emotional state from user message"""
        emotion_indicators = {
            "frustrated": [r"frustrated", r"angry", r"mad", r"hate", r"stupid", r"dumb", r"ugh", r"argh"],
            "confused": [r"confused", r"don't understand", r"lost", r"unclear", r"what", r"huh"],
            "excited": [r"excited", r"love", r"awesome", r"great", r"amazing", r"cool", r"yay"],
            "confident": [r"easy", r"got it", r"understand", r"know", r"sure", r"definitely"],
            "worried": [r"worried", r"scared", r"nervous", r"anxious", r"afraid"],
            "proud": [r"proud", r"happy", r"accomplished", r"did it", r"yes"]
        }
        
        for emotion, indicators in emotion_indicators.items():
            if any(re.search(indicator, message) for indicator in indicators):
                return emotion
        
        return "neutral"
    
    def _identify_learning_need(self, message: str) -> str:
        """Identify specific learning needs from user message"""
        learning_needs = {
            "phonics": [r"sound", r"letter", r"phonics", r"blend", r"decode", r"pronounce"],
            "spelling": [r"spell", r"spelling", r"write", r"letters", r"correct"],
            "reading": [r"read", r"reading", r"book", r"story", r"text", r"passage"],
            "comprehension": [r"understand", r"meaning", r"comprehension", r"what does", r"main idea"],
            "writing": [r"write", r"writing", r"sentence", r"paragraph", r"essay", r"compose"],
            "vocabulary": [r"word", r"vocabulary", r"definition", r"meaning", r"synonym"],
            "fluency": [r"fluency", r"speed", r"smooth", r"expression", r"fast"]
        }
        
        for need, patterns in learning_needs.items():
            if any(re.search(pattern, message) for pattern in patterns):
                return need
        
        return "general"
    
    def _assess_difficulty_level(self, message: str, user_context: Dict[str, Any] = None) -> str:
        """Assess appropriate difficulty level for user"""
        if not user_context:
            return "beginner"
        
        accuracy = user_context.get("average_accuracy", 0)
        grade_level = user_context.get("grade_level", 1)
        
        if accuracy >= 85 and grade_level >= 3:
            return "advanced"
        elif accuracy >= 75 or grade_level >= 2:
            return "intermediate"
        else:
            return "beginner"
    
    def _identify_errors_with_text_analyzer(self, message: str) -> List[Dict[str, Any]]:
        """Identify errors using integrated text analyzer"""
        errors = []
        
        # Use text analyzer if available
        if self.text_analyzer:
            try:
                # Run text analyzer synchronously
                import asyncio
                try:
                    loop = asyncio.get_event_loop()
                except RuntimeError:
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                
                analysis = loop.run_until_complete(self.text_analyzer.analyze_text(message))
                
                if analysis and analysis.get("errors"):
                    for error in analysis["errors"]:
                        errors.append({
                            "type": error.get("type", "spelling"),
                            "word": error.get("word", ""),
                            "suggestion": error.get("suggestion", ""),
                            "explanation": self.error_explanations.get(error.get("type", "spelling_error"), {})
                        })
                
                print(f"[AI_TUTOR] Text analyzer found {len(errors)} errors")
            except Exception as e:
                print(f"[AI_TUTOR] Text analyzer error: {e}")
        
        # Fallback to pattern-based error detection
        if not errors:
            errors = self._identify_errors_pattern_based(message)
        
        return errors
    
    def _identify_errors_pattern_based(self, message: str) -> List[Dict[str, Any]]:
        """Fallback pattern-based error identification"""
        errors = []
        
        error_patterns = {
            "letter_reversal": [r"\b(abd|doy|bid|dack|qut|puite)\b"],
            "phonetic_spelling": [r"\b(sed|wuz|cuz|becuz|lite|nite)\b"],
            "word_confusion": [r"there.*their", r"were.*where", r"then.*than"]
        }
        
        for error_type, patterns in error_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, message.lower())
                for match in matches:
                    errors.append({
                        "type": error_type,
                        "word": match.group(),
                        "suggestion": "",
                        "explanation": self.error_explanations.get(error_type, {})
                    })
        
        return errors
    
    def _identify_strengths(self, message: str) -> List[str]:
        """Identify strengths demonstrated in user's message"""
        strengths = []
        
        if len(message.split()) > 10:
            strengths.append("good_expression")
        
        if any(word in message.lower() for word in ["because", "however", "therefore", "although"]):
            strengths.append("complex_vocabulary")
        
        if message.count(".") > 1 or message.count("!") > 0 or message.count("?") > 0:
            strengths.append("punctuation_awareness")
        
        if len(message) > 0 and message[0].isupper():
            strengths.append("capitalization_awareness")
        
        return strengths
    
    async def generate_response(self, user_message: str, analysis: Dict[str, Any], user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate appropriate AI tutor response"""
        
        response_data = {
            "message": "",
            "suggestions": [],
            "encouragement": "",
            "lesson_recommendations": [],
            "exercises": [],
            "tips": [],
            "emotional_support": "",
            "analysis": analysis
        }
        
        # Check if user is asking for help/instructions (HIGHEST PRIORITY)
        message_lower = user_message.lower().strip()
        
        # Detect help/instruction questions or answer requests
        if re.search(r"\bhow (do i|to|should i|to answer|can i)\b|\bwhat (do i|should i|can i)\b|\bshould i\b|\bhow to answer\b|\bhow.*answer", message_lower):
            # Check if asking for the answer to an active exercise
            if re.search(r"\bwhat.*(is|are|'s).*answer|\bwhat.*(is|are|'s).*correct|\bshow.*answer|\btell.*answer|\bgive.*answer", message_lower):
                return self._handle_answer_request(user_message, analysis, user_context)
            # Otherwise it's a help request
            return self._handle_help_request(user_message, analysis, user_context)
        
        # Check intent first to determine if this is a new request
        intent = analysis["intent"]
        user_id = user_context.get("user_id") if user_context else None
        
        print(f"[AI_TUTOR] Intent detected: {intent} for message: '{user_message[:50]}'")
        print(f"[AI_TUTOR] Active exercise exists: {user_id in self.active_exercises if user_id else False}")
        
        # PRIORITY: Clear active exercise if user is making a new request
        if intent in ["word_request", "practice_request", "greeting", "question"] and user_id and user_id in self.active_exercises:
            print(f"[AI_TUTOR] Clearing active exercise for new {intent}")
            del self.active_exercises[user_id]
            # Also clear practice words to avoid confusion
            if user_id in self.last_practice_words:
                del self.last_practice_words[user_id]
        
        # Only check for active exercise response if NOT making a new request
        if intent not in ["word_request", "practice_request", "greeting", "question"] and user_id is not None and user_id in self.active_exercises:
            print(f"[AI_TUTOR] User {user_id} has active exercise")
            exercise_response = self._handle_exercise_response(user_message, user_id, analysis)
            if exercise_response:
                return exercise_response
        
        # Handle structured intents with rule-based handlers (these need specific formats)
        if intent == "greeting":
            response_data.update(self._handle_greeting(analysis, user_context))
        elif intent == "word_request":
            response_data.update(self._handle_word_request(user_message, analysis, user_context))
        elif intent == "practice_request":
            response_data.update(self._handle_practice_request(analysis, user_context))
        elif intent == "help_request":
            response_data.update(self._handle_help_request(user_message, analysis, user_context))
        elif intent == "spelling_check":
            response_data.update(self._handle_spelling_check(user_message, analysis, user_context))
        elif intent == "sharing_work":
            response_data.update(self._handle_work_sharing(user_message, analysis, user_context))
        elif intent == "frustration":
            response_data.update(self._handle_frustration(analysis, user_context))
        elif intent == "celebration":
            response_data.update(self._handle_celebration(analysis, user_context))
        elif intent == "short_text_submission":
            response_data.update(self._handle_short_text_submission(user_message, analysis, user_context))
        else:
            # For general conversation, try OpenAI API first
            if self.api_enabled:
                api_response = await self._generate_api_response(user_message, analysis, user_context)
                if api_response:
                    response_data["message"] = api_response
                    response_data["emotional_support"] = self._provide_emotional_support(analysis["emotion"])
                    if analysis["strengths"]:
                        response_data["encouragement"] = self._generate_strength_based_encouragement(analysis["strengths"])
                    return response_data
            # Fallback to rule-based general response
            response_data.update(self._handle_general_response(user_message, analysis, user_context))
        
        # Add emotional support
        response_data["emotional_support"] = self._provide_emotional_support(analysis["emotion"])
        
        # Add encouragement based on strengths
        if analysis["strengths"]:
            response_data["encouragement"] = self._generate_strength_based_encouragement(analysis["strengths"])
        
        # Fallback if no message generated
        if not response_data["message"]:
            response_data["message"] = self._get_fallback_response(analysis)
        
        return response_data
    
    def _handle_greeting(self, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle greeting intent"""
        return {
            "message": random.choice(self.response_templates["greeting"]),
            "suggestions": self._get_daily_suggestions(user_context),
            "lesson_recommendations": lesson_manager.get_all_lessons_summary()[:3] if lesson_manager else []
        }
    
    def _handle_answer_request(self, message: str, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle request for exercise answer"""
        user_id = user_context.get("user_id") if user_context else None
        
        if not user_id or user_id not in self.active_exercises:
            return {
                "message": "There's no active exercise right now. Would you like me to generate one for you?",
                "suggestions": ["Ask for practice words", "Request an exercise", "Start practicing"]
            }
        
        exercise = self.active_exercises[user_id]
        skill_area = exercise.get("skill_area", "")
        exercise_type = exercise.get("exercise_type", "")
        
        # Provide answers based on exercise type
        if skill_area == "phonemic_awareness":
            exercises_list = exercise.get("exercises", [])
            if exercises_list:
                answers = []
                for idx, ex in enumerate(exercises_list, 1):
                    word = ex.get("word", "")
                    answer = ex.get("answer", "")
                    answers.append(f"{idx}. {word} → {answer}")
                
                return {
                    "message": f"📚 Here are the answers for the phonemic awareness exercise:\n\n" + "\n".join(answers),
                    "suggestions": ["Try another exercise", "Practice more sounds", "Ready for the next challenge?"],
                    "tips": ["Listen carefully to each sound", "Practice makes perfect", "You're learning!"]
                }
        
        elif skill_area == "spelling":
            exercises_list = exercise.get("exercises", [])
            if exercises_list:
                first_ex = exercises_list[0]
                correct_word = first_ex.get("correct_word", "")
                return {
                    "message": f"📝 The correct spelling is: {correct_word}",
                    "suggestions": ["Try spelling it yourself", "Practice writing it", "Sound it out"],
                    "tips": [f"Break it down: {' - '.join(list(correct_word))}", "Practice makes perfect", "You can do this!"]
                }
        
        elif skill_area == "sight_words":
            if exercise_type == "sentence_completion":
                exercises_list = exercise.get("exercises", [])
                if exercises_list:
                    answers = []
                    for idx, ex in enumerate(exercises_list, 1):
                        sentence = ex.get("sentence", "")
                        correct_answer = ex.get("correct_answer", "")
                        answers.append(f"{idx}. {sentence.replace('___', correct_answer)}")
                    
                    return {
                        "message": f"📖 Here are the completed sentences:\n\n" + "\n".join(answers),
                        "suggestions": ["Try completing them yourself", "Practice these sight words", "Ready for more?"],
                        "tips": ["Sight words need to be memorized", "Read them multiple times", "Practice daily"]
                    }
            else:
                words = exercise.get("words", [])
                return {
                    "message": f"👀 The sight words to practice are: {', '.join(words)}",
                    "suggestions": ["Try reading each word", "Practice writing them", "Use them in sentences"],
                    "tips": ["Sight words don't follow phonetic rules", "Memorize them through repetition", "You're doing great!"]
                }
        
        elif skill_area == "phonics" and exercise_type == "word_building":
            exercises_list = exercise.get("exercises", [])
            if exercises_list and len(exercises_list) > 1:
                target_words = [ex.get("target_word", "") for ex in exercises_list if ex.get("target_word")]
                return {
                    "message": f"🔤 The words to build are: {', '.join(target_words)}",
                    "suggestions": ["Try building them yourself", "Sound out each letter", "Take your time"],
                    "tips": ["Use the letters provided", "Say each sound", "Put them together"]
                }
            else:
                target_word = exercise.get("target_word", "")
                if not target_word and exercises_list:
                    target_word = exercises_list[0].get("target_word", "")
                return {
                    "message": f"🔤 The word to build is: {target_word}",
                    "suggestions": ["Try building it yourself", "Sound out each letter", "You can do this!"],
                    "tips": [f"Letters: {' - '.join(list(target_word))}", "Say each sound", "Put them together"]
                }
        
        elif skill_area == "writing":
            word_bank = exercise.get("word_bank", [])
            return {
                "message": f"✍️ Create a sentence using these words: {', '.join(word_bank)}\n\nThere's no single correct answer - be creative!",
                "suggestions": ["Use all the words", "Make it interesting", "Check your spelling"],
                "tips": ["Start with a capital letter", "End with punctuation", "Make sure it makes sense"]
            }
        
        elif skill_area == "reading_comprehension":
            questions = exercise.get("questions", [])
            if questions:
                answers = []
                for idx, q in enumerate(questions, 1):
                    question_text = q.get("question", "")
                    answer = q.get("answer", "")
                    answers.append(f"{idx}. Q: {question_text}\n   A: {answer}")
                
                return {
                    "message": f"📚 Here are the answers:\n\n" + "\n\n".join(answers),
                    "suggestions": ["Try answering yourself first", "Read the passage again", "Look for details"],
                    "tips": ["Read carefully", "Find evidence in the text", "Take your time"]
                }
        
        # Generic response
        return {
            "message": f"📚 For this {skill_area} exercise, try your best! There's no single right way to learn.",
            "suggestions": ["Give it a try", "Do your best", "I'm here to help"],
            "tips": ["Learning is a process", "Mistakes help you grow", "You're doing great!"]
        }
    
    def _handle_help_request(self, message: str, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle help request"""
        message_lower = message.lower().strip()
        user_id = user_context.get("user_id") if user_context else None
        
        # Check if asking about how to answer an active exercise
        if user_id and user_id in self.active_exercises:
            exercise = self.active_exercises[user_id]
            skill_area = exercise.get("skill_area", "")
            exercise_type = exercise.get("exercise_type", "")
            instructions = exercise.get("instructions", "")
            
            if skill_area == "spelling":
                exercises_list = exercise.get("exercises", [])
                if exercises_list:
                    first_ex = exercises_list[0]
                    incomplete = first_ex.get("incomplete_word", "")
                    correct_word = first_ex.get("correct_word", "")
                    
                    # Check if multiple words
                    if len(exercises_list) > 1:
                        examples = [ex.get("incomplete_word", "") for ex in exercises_list[:3]]
                        return {
                            "message": f"📝 **How to answer this spelling exercise:**\n\n1. Look at each incomplete word: {', '.join(examples)}...\n2. Fill in the missing letter for EACH word\n3. Type ALL complete words separated by commas\n\n**Example:** If you see 'd_g, c_t, r_n', type: dog, cat, run\n\n✍️ Now type your answers!",
                            "suggestions": ["Complete all words", "Separate with commas", "Sound out each word"],
                            "tips": [f"There are {len(exercises_list)} words to complete", "Use the pattern hints", "Take your time with each one"]
                        }
                    else:
                        return {
                            "message": f"📝 **How to answer this spelling exercise:**\n\n1. Look at the incomplete word: '{incomplete}'\n2. Figure out the missing letter\n3. Type the complete word\n\n**Example:** If you see 'c_t', type: cat\n\n✍️ Now type your answer!",
                            "suggestions": ["Type the complete word", "Sound it out slowly", "Look for the pattern"],
                            "tips": ["Take your time", "Use the pattern hint", "You can do this!"]
                        }
            
            elif skill_area == "sight_words":
                if exercise_type == "flash_cards":
                    words = exercise.get("words", [])
                    return {
                        "message": f"👀 **How to answer this sight words exercise:**\n\n1. Read each word carefully\n2. Type ONE word at a time\n3. I'll tell you if it's correct\n\n**Words to practice:** {', '.join(words[:5])}\n\n**Example:** Just type: {words[0] if words else 'cat'}\n\n✍️ Type your first word!",
                        "suggestions": ["Type one word", "Read it carefully", "Take your time"],
                        "tips": ["Sight words need to be memorized", "Practice makes perfect", "You're doing great!"]
                    }
                elif exercise_type == "sentence_completion":
                    exercises_list = exercise.get("exercises", [])
                    if exercises_list:
                        first_sentence = exercises_list[0].get("sentence", "")
                        options = exercises_list[0].get("options", [])
                        return {
                            "message": f"📖 **How to answer this sentence completion exercise:**\n\n1. Read each sentence with the blank (___)\n2. Choose the correct sight word to fill the blank\n3. Type the complete sentence with your word\n\n**Example sentence:** {first_sentence}\n**Word choices:** {', '.join(options) if options else 'Choose from the word bank'}\n\n✍️ Type the complete sentence!",
                            "suggestions": ["Read the sentence carefully", "Think about which word makes sense", "Type the complete sentence"],
                            "tips": ["Read the whole sentence", "Try each option in your head", "Trust your instinct"]
                        }
                    return {
                        "message": "📖 **How to answer this sentence completion exercise:**\n\n1. Read each sentence with the blank (___)\n2. Choose the correct sight word\n3. Type the complete sentence\n\n✍️ Type your answer!",
                        "suggestions": ["Read carefully", "Think about what makes sense", "Type the complete sentence"],
                        "tips": ["Read the whole sentence", "Try each option", "Trust your instinct"]
                    }
            
            elif skill_area == "writing":
                word_bank = exercise.get("word_bank", [])
                return {
                    "message": f"✍️ **How to answer this writing exercise:**\n\n1. Use ALL these words: {', '.join(word_bank)}\n2. Create ONE complete sentence\n3. Make sure it makes sense\n\n**Example:** If words are 'cat, sat, mat', you could write: \"The cat sat on the mat.\"\n\n✍️ Now type your sentence!",
                    "suggestions": ["Use all the words", "Make it creative", "Check your spelling"],
                    "tips": ["Start with a capital letter", "End with a period", "Make sure it makes sense"]
                }
            
            elif skill_area == "phonics":
                exercise_type = exercise.get("exercise_type", "")
                if exercise_type == "sound_out":
                    practice_items = exercise.get("practice_items", [])
                    if practice_items:
                        return {
                            "message": f"🔤 **How to answer this phonics exercise:**\n\n1. Look at each word: {', '.join(practice_items[:3])}...\n2. Sound out each letter (c-a-t = cat)\n3. Type the word you hear\n\n**Example:** If you see 'cat', sound it out: c-a-t, then type: cat\n\n✍️ Type one word at a time!",
                            "suggestions": ["Sound out each letter", "Say the sounds together", "Type what you hear"],
                            "tips": ["Break it into sounds", "Say each sound slowly", "Blend them together"]
                        }
                elif exercise_type == "word_building":
                    exercises_list = exercise.get("exercises", [])
                    if exercises_list and len(exercises_list) > 1:
                        letters_list = [ex.get("letters", []) for ex in exercises_list[:2]]
                        return {
                            "message": f"🔤 **How to answer this word building exercise:**\n\n1. Look at the letters provided for each word\n2. Build a word using those letters\n3. Type ALL the words you build\n\n**Example:** If given letters 'c, a, t' and 'd, o, g', type: cat dog\n\n✍️ Type all the words separated by spaces!",
                            "suggestions": ["Use the letters shown", "Build one word at a time", "Separate words with spaces"],
                            "tips": [f"Build {len(exercises_list)} words", "Sound out each letter", "Put the sounds together"]
                        }
                    else:
                        target_word = exercise.get("target_word", "")
                        letters = exercise.get("letters", [])
                        return {
                            "message": f"🔤 **How to answer this word building exercise:**\n\n1. Look at the letters: {', '.join(letters) if letters else 'provided'}\n2. Build a word using these letters\n3. Type the word\n\n**Example:** If letters are 'c, a, t', type: cat\n\n✍️ Type your word!",
                            "suggestions": ["Use all the letters", "Sound out each letter", "Build the word"],
                            "tips": ["Say each sound", "Put them together", "You can do this!"]
                        }
                return {
                    "message": f"🔤 **How to answer this phonics exercise:**\n\n{instructions}\n\n✍️ Type your answer and I'll check it!",
                    "suggestions": ["Sound out each letter", "Build the word", "Take your time"],
                    "tips": ["Break it into sounds", "Say each sound", "Put them together"]
                }
            
            elif skill_area == "reading_comprehension":
                passage = exercise.get("passage", "")
                questions = exercise.get("questions", [])
                if passage and questions:
                    first_question = questions[0].get("question", "") if questions else ""
                    return {
                        "message": f"📚 **How to answer this reading comprehension exercise:**\n\n1. Read the passage carefully\n2. Answer the question in your own words\n3. Type your answer\n\n**Passage:** {passage[:100]}...\n**Question:** {first_question}\n\n**Example:** If asked 'What is the main idea?', type: The story is about...\n\n✍️ Type your answer!",
                        "suggestions": ["Read the passage first", "Think about the question", "Answer in your own words"],
                        "tips": ["Look for details in the text", "Take your time", "There's no single right way to answer"]
                    }
            
            # Generic exercise help
            return {
                "message": f"📚 **How to answer this exercise:**\n\n{instructions}\n\n✍️ Just type your answer and I'll check it for you!",
                "suggestions": ["Read the instructions", "Take your time", "Do your best"],
                "tips": ["There's no rush", "Try your best", "I'm here to help"]
            }
        
        # No active exercise - provide general help
        learning_need = analysis["learning_need"]
        
        # Provide contextual help based on what they're asking
        if learning_need != "general":
            response = {
                "message": f"I'd love to help you with {learning_need}! Let me break this down for you.",
                "suggestions": [],
                "lesson_recommendations": [],
                "exercises": [],
                "tips": []
            }
        else:
            response = {
                "message": "I'm here to help! I can assist you with:\n• Reading practice\n• Spelling and writing\n• Phonics exercises\n• Comprehension questions\n\nWhat would you like to work on?",
                "suggestions": [
                    "Try asking: 'give me 5 words to practice'",
                    "Say 'practice reading' for reading exercises",
                    "Type any sentence for spelling feedback"
                ],
                "tips": [
                    "I'm patient and here to support you",
                    "There's no wrong question",
                    "We'll work at your pace"
                ]
            }
            return response
        
        # Get relevant lessons
        if lesson_manager:
            try:
                relevant_lessons = lesson_manager.get_lessons_by_category(learning_need)
                if relevant_lessons:
                    response["lesson_recommendations"] = relevant_lessons[:2]
            except:
                pass
        
        # Provide tips
        tips_map = {
            "phonics": [
                "Break words into smaller sounds",
                "Use your finger to track each sound",
                "Practice with rhyming words"
            ],
            "spelling": [
                "Sound out the word slowly",
                "Look for patterns you recognize",
                "Use memory tricks for tricky words"
            ],
            "reading": [
                "Read slowly and carefully",
                "Use your finger to track words",
                "Ask yourself what's happening in the story"
            ],
            "writing": [
                "Start with simple sentences",
                "Use words you know how to spell",
                "Read your work out loud"
            ]
        }
        
        response["tips"] = tips_map.get(learning_need, ["Take your time", "Practice regularly", "Ask questions when confused"])
        response["suggestions"] = [
            f"Let's start with a simple {learning_need} exercise",
            "I can generate practice activities for you",
            "Ask me specific questions anytime"
        ]
        
        return response
    
    def _handle_practice_request(self, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle practice request"""
        learning_need = analysis["learning_need"]
        difficulty = analysis["difficulty_level"]
        
        return {
            "message": f"Great! Let's practice {learning_need}. I have some perfect activities for you!",
            "suggestions": [
                f"Start with {difficulty} level exercises",
                "Take breaks when you need them",
                "Celebrate small victories!"
            ]
        }
    
    def _handle_word_request(self, message: str, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle word request"""
        number_match = re.search(r'(\d+)\s+words?', message.lower())
        num_words = int(number_match.group(1)) if number_match else 5
        num_words = min(num_words, 10)
        
        difficulty = analysis["difficulty_level"]
        
        word_lists = {
            "beginner": ["cat", "dog", "sun", "big", "red", "hop", "sit", "run", "pen", "cup", "hat", "map", "top", "bag", "leg"],
            "intermediate": ["cake", "bike", "rope", "cute", "make", "like", "hope", "tube", "game", "time", "snake", "plane", "smile", "stone", "grape"],
            "advanced": ["happy", "garden", "window", "pencil", "rabbit", "basket", "button", "kitten", "yellow", "purple", "elephant", "butterfly", "computer", "telephone", "adventure"]
        }
        
        selected_words = random.sample(word_lists[difficulty], min(num_words, len(word_lists[difficulty])))
        
        # Store practice words for context
        user_id = user_context.get("user_id") if user_context else 0
        self.last_practice_words[user_id] = selected_words
        
        # Set up an active writing exercise with these words
        writing_exercise = {
            "skill_area": "writing",
            "exercise_type": "sentence_construction",
            "word_bank": selected_words,
            "instructions": f"Create a sentence using all these words: {', '.join(selected_words)}",
            "target_words": selected_words
        }
        self.set_active_exercise(user_id, writing_exercise)
        
        # Build message with words listed
        words_list = "\n".join([f"{i+1}. {word}" for i, word in enumerate(selected_words)])
        message_text = f"Here are {len(selected_words)} {difficulty} level words for you to practice:\n\n{words_list}\n\n📝 **Challenge:** Try using ALL {len(selected_words)} words in a sentence! Just type your sentence below and I'll check it."
        
        return {
            "message": message_text,
            "practice_words": selected_words,
            "instructions": [
                "Use ALL the words in ONE sentence",
                "Create a complete sentence that makes sense",
                "Check your spelling as you go"
            ],
            "encouragement": "Take your time and be creative!",
            "tips": [
                "Start with a capital letter",
                "End with punctuation",
                "Make sure your sentence tells a complete thought"
            ]
        }
    
    def _handle_spelling_check(self, message: str, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle spelling check request"""
        errors = analysis.get("errors", [])
        
        if errors:
            error_list = ", ".join([f"'{e['word']}' → '{e['suggestion']}'" for e in errors if e.get('suggestion')])
            return {
                "message": f"I found some spelling opportunities: {error_list}. Let's practice these words together!",
                "suggestions": [e.get("explanation", {}).get("strategy", "") for e in errors if e.get("explanation")],
                "tips": ["Sound out each word", "Break it into syllables", "Practice writing it multiple times"]
            }
        else:
            return {
                "message": "Great job! Your spelling looks correct!",
                "encouragement": "You're doing excellent work!"
            }
    
    def _handle_short_text_submission(self, message: str, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle short text submission (1-3 words) - with exercise validation"""
        errors = analysis.get("errors", [])
        strengths = analysis.get("strengths", [])
        
        # Check if this is a response to an active exercise
        user_id = user_context.get("user_id") if user_context else None
        if user_id is not None and user_id in self.active_exercises:
            exercise = self.active_exercises[user_id]
            skill_area = exercise.get("skill_area", "")
            
            # Handle phonics word building exercise
            if skill_area == "phonics" and exercise.get("exercise_type") == "word_building":
                return self._evaluate_word_building_response(message, exercise, analysis)
            
            # Handle sight words exercise
            elif skill_area == "sight_words":
                return self._evaluate_sight_words_response(message, exercise, analysis)
            
            # Handle spelling exercise
            elif skill_area == "spelling":
                return self._evaluate_spelling_response(message, exercise, analysis)
            
            # Handle writing exercise
            elif skill_area == "writing":
                return self._evaluate_writing_response(message, exercise, analysis)
            
            # Handle reading comprehension exercise
            elif skill_area == "reading_comprehension":
                return self._evaluate_comprehension_response(message, exercise, analysis)
        
        # Generic short text submission feedback (no active exercise)
        # Provide helpful conversational feedback without scoring
        if len(message.split()) <= 2 and not errors:
            # Very short input - guide user to more interaction
            response = {
                "message": f"I see you wrote '{message}'. Would you like to:\n• Practice more words?\n• Write a full sentence?\n• Try an exercise?",
                "suggestions": [
                    "Say 'give me 5 words' for practice words",
                    "Try writing a full sentence",
                    "Ask for a specific exercise"
                ],
                "encouragement": "I'm here to help you learn!"
            }
        elif errors:
            # Has errors - provide constructive feedback
            response = {
                "message": f"I see you wrote: '{message}'. I noticed '{errors[0]['word']}' could be spelled '{errors[0]['suggestion']}'. Great practice!",
                "suggestions": [
                    "Would you like to practice spelling?",
                    "Try writing a full sentence",
                    "Ask me for practice words"
                ],
                "tips": [
                    "Sound out each word slowly",
                    "Break words into syllables",
                    "Practice makes perfect!"
                ]
            }
        else:
            # Good text - encourage more
            response = {
                "message": f"Nice! You wrote: '{message}'. That's good writing! Would you like to:\n• Practice more words?\n• Write a longer sentence?\n• Try an exercise?",
                "suggestions": [
                    "Say 'give me 5 words' for practice words",
                    "Try writing a longer sentence",
                    "Ask for a specific exercise"
                ],
                "encouragement": "Keep up the great work!"
            }

        return response
    
    def _evaluate_word_building_response(self, user_response: str, exercise: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate word building exercise response"""
        # Check if exercise has multiple words
        exercises_list = exercise.get("exercises", [])
        
        if exercises_list and len(exercises_list) > 1:
            # Multiple word building exercise
            user_answer = user_response.strip().lower()
            cleaned = re.sub(r"[^a-z0-9\s]", "", user_answer)
            user_words = [w for w in cleaned.split() if w]
            
            # Get all target words
            target_words = [ex.get("target_word", "").lower() for ex in exercises_list if ex.get("target_word")]
            
            if not target_words:
                return {"message": "No target words found in exercise.", "is_correct": False}
            
            # Check which words user got correct
            correct_words = [word for word in target_words if word in user_words]
            correct_count = len(correct_words)
            total_count = len(target_words)
            
            is_correct = correct_count == total_count
            score = int((correct_count / total_count) * 100) if total_count > 0 else 0
            
            response = {
                "message": "",
                "encouragement": "",
                "suggestions": [],
                "tips": [],
                "is_correct": is_correct
            }
            
            if is_correct:
                response["message"] = f"🌟 Fantastic! You built all {total_count} words correctly: {', '.join(target_words)}!"
                response["encouragement"] = random.choice(self.encouragement_phrases["breakthrough_moment"])
                response["suggestions"] = [
                    "Ready for another challenge?",
                    "Try more challenging words!",
                    "You're a word-building expert!"
                ]
            elif correct_count > 0:
                missing_words = [w for w in target_words if w not in correct_words]
                response["message"] = f"Good work! You got {correct_count} out of {total_count} correct: {', '.join(correct_words)}. Missing: {', '.join(missing_words)}"
                response["encouragement"] = random.choice(self.encouragement_phrases["good_progress"])
                response["suggestions"] = [
                    f"Try building: {', '.join(missing_words)}",
                    "Sound out each word",
                    "You're almost there!"
                ]
                response["tips"] = [
                    f"Expected words: {', '.join(target_words)}",
                    "Use the letters provided for each word",
                    "Take your time with each word"
                ]
            else:
                response["message"] = f"For this exercise, build these words: {', '.join(target_words)}. You wrote: '{user_response.strip()}'"
                response["encouragement"] = random.choice(self.encouragement_phrases["needs_support"])
                response["suggestions"] = [
                    "Try building one word at a time",
                    "Sound out each letter",
                    "Use the letters provided"
                ]
                response["tips"] = [
                    f"Target words: {', '.join(target_words)}",
                    "Build each word using the letters shown",
                    "Practice makes perfect!"
                ]
            
            return response
        
        # Single word building exercise
        target_word = exercise.get("target_word", "").lower()
        if not target_word and exercises_list:
            target_word = exercises_list[0].get("target_word", "").lower()
        
        user_answer = user_response.strip().lower()
        cleaned = re.sub(r"[^a-z0-9\s]", "", user_answer)
        user_words = [w for w in cleaned.split() if w]

        contains_target = target_word and any(w == target_word for w in user_words)
        exact_match = user_answer == target_word

        if exact_match:
            score = 100
        elif contains_target:
            score = 90
        else:
            score = 0

        is_correct = score >= 90

        response = {
            "message": "",
            "encouragement": "",
            "suggestions": [],
            "tips": [],
            "is_correct": is_correct,
            "correct_word": target_word
        }

        if is_correct:
            response["message"] = f"🌟 Fantastic! You built the word '{target_word}' correctly!"
            response["encouragement"] = random.choice(self.encouragement_phrases["breakthrough_moment"])
            response["suggestions"] = [
                "Ready for another word?",
                "Try a more challenging word!",
                "You're a word-building expert!"
            ]
        else:
            if user_words:
                response["message"] = f"Good try! The correct word is '{target_word}'. I see you wrote: '{user_response.strip()}'."
            else:
                response["message"] = f"Good try! The correct spelling is '{target_word}'. You wrote '{user_answer}'."

            response["encouragement"] = random.choice(self.encouragement_phrases["good_progress"])
            response["suggestions"] = [
                "Let's try again - sound out each letter",
                "Remember the letters: " + ", ".join(list(target_word)),
                "Try writing it one more time"
            ]
            response["tips"] = [
                "Sound out each letter slowly: " + " - ".join(list(target_word)),
                "Check each letter carefully",
                "Practice makes perfect!"
            ]

        return response
    
    def _evaluate_sight_words_response(self, user_response: str, exercise: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate sight words exercise response"""
        # Get the expected word from exercise
        expected_word = exercise.get("current_word", "")
        
        # Try to get from exercises list if not set
        if not expected_word:
            exercises_list = exercise.get("exercises", [])
            if exercises_list and len(exercises_list) > 0:
                expected_word = exercises_list[0].get("correct_answer", "")
        
        # Fallback to words list
        if not expected_word and exercise.get("words"):
            expected_word = exercise.get("words", [])[0] if exercise.get("words") else ""
        
        user_answer = user_response.strip().lower()
        
        is_correct = user_answer.lower() == expected_word.lower()
        
        response = {
            "message": "",
            "encouragement": "",
            "suggestions": [],
            "tips": [],
            "is_correct": is_correct
        }
        
        if is_correct:
            response["message"] = f"✅ Perfect! You recognized the sight word '{expected_word}' instantly!"
            response["encouragement"] = random.choice(self.encouragement_phrases["high_achievement"])
            response["suggestions"] = [
                "Excellent sight word recognition!",
                "You're building fluency!",
                "Ready for the next word?"
            ]
        else:
            response["message"] = f"Good effort! This sight word is '{expected_word}'. You wrote '{user_answer}'."
            response["encouragement"] = random.choice(self.encouragement_phrases["good_progress"])
            response["suggestions"] = [
                "Let's practice this word again",
                "Sight words need to be memorized",
                "Try writing it a few more times"
            ]
            response["tips"] = [
                f"The correct word is: {expected_word}",
                "Sight words don't follow phonetic rules",
                "Repetition helps memorize sight words"
            ]
        
        return response
    
    def _evaluate_spelling_response(self, user_response: str, exercise: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate spelling exercise response"""
        exercises_list = exercise.get("exercises", [])
        user_answer = user_response.strip().lower()
        
        # Parse user answer - handle comma-separated or space-separated words
        user_words = [w.strip() for w in re.split(r'[,\s]+', user_answer) if w.strip()]
        
        # Get all correct words from exercises list
        correct_words = [ex.get("correct_word", "").lower() for ex in exercises_list if ex.get("correct_word")]
        
        if not correct_words:
            # Fallback to single word
            correct_word = exercise.get("correct_word", "").lower()
            if correct_word:
                correct_words = [correct_word]
        
        response = {
            "message": "",
            "encouragement": "",
            "suggestions": [],
            "tips": [],
            "is_correct": False
        }
        
        if not correct_words:
            response["message"] = "No correct words found in exercise."
            return response
        
        # Check if user provided all correct words
        if len(user_words) == len(correct_words):
            # Check each word
            correct_count = sum(1 for i, word in enumerate(user_words) if i < len(correct_words) and word == correct_words[i])
            total_count = len(correct_words)
            score = int((correct_count / total_count) * 100) if total_count > 0 else 0
            is_correct = correct_count == total_count
            
            response["is_correct"] = is_correct
            
            if is_correct:
                response["message"] = f"📝 Excellent! You spelled all {total_count} words correctly: {', '.join(correct_words)}!"
                response["encouragement"] = random.choice(self.encouragement_phrases["high_achievement"])
                response["suggestions"] = [
                    "Perfect spelling!",
                    "You're mastering this pattern!",
                    "Ready for more challenging words?"
                ]
            elif correct_count > 0:
                wrong_words = [f"{user_words[i]} → {correct_words[i]}" for i in range(len(user_words)) if user_words[i] != correct_words[i]]
                response["message"] = f"Good work! You got {correct_count} out of {total_count} correct. Check: {', '.join(wrong_words)}"
                response["encouragement"] = random.choice(self.encouragement_phrases["good_progress"])
                response["suggestions"] = [
                    "Review the incorrect words",
                    "Try breaking them into syllables",
                    "Sound out each word slowly"
                ]
                response["tips"] = [
                    f"Correct spellings: {', '.join(correct_words)}",
                    "Look for spelling patterns",
                    "Practice writing each word"
                ]
            else:
                response["message"] = f"Let's practice! The correct spellings are: {', '.join(correct_words)}. You wrote: {', '.join(user_words)}"
                response["encouragement"] = random.choice(self.encouragement_phrases["needs_support"])
                response["suggestions"] = [
                    "Try each word one at a time",
                    "Sound out each letter",
                    "Look at the pattern hints"
                ]
                response["tips"] = [
                    f"Correct spellings: {', '.join(correct_words)}",
                    "Use the consonant-vowel-consonant pattern",
                    "Practice makes perfect!"
                ]
        elif len(user_words) == 1 and len(correct_words) > 1:
            # User only provided one word when multiple expected
            response["message"] = f"You need to complete all {len(correct_words)} words! You only provided: {user_words[0]}"
            response["encouragement"] = "Keep going!"
            response["suggestions"] = [
                f"Complete all {len(correct_words)} words",
                "Separate your answers with commas",
                "Example: dog, pen, sit, run, cup"
            ]
            response["tips"] = [
                f"There are {len(correct_words)} words to complete",
                "Fill in the missing letter for each word",
                "Use commas to separate your answers"
            ]
        else:
            # Wrong number of words
            response["message"] = f"You provided {len(user_words)} words but need {len(correct_words)}. Correct answers: {', '.join(correct_words)}"
            response["encouragement"] = random.choice(self.encouragement_phrases["needs_support"])
            response["suggestions"] = [
                f"Provide exactly {len(correct_words)} words",
                "Check each incomplete word",
                "Separate answers with commas"
            ]
            response["tips"] = [
                f"Correct spellings: {', '.join(correct_words)}",
                "Count the number of words to complete",
                "Fill in each missing letter"
            ]
        
        return response
    
    def _evaluate_writing_response(self, user_response: str, exercise: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate writing exercise response"""
        word_bank = exercise.get("word_bank", [])
        user_answer = user_response.strip()
        
        # Check if all required words are present (case-insensitive)
        user_answer_lower = user_answer.lower()
        words_found = [word for word in word_bank if word.lower() in user_answer_lower]
        missing_words = [word for word in word_bank if word.lower() not in user_answer_lower]
        all_words_present = len(words_found) == len(word_bank) and len(word_bank) > 0
        
        score = 100 if all_words_present else int((len(words_found) / len(word_bank)) * 100) if word_bank else 0
        
        response = {
            "message": "",
            "encouragement": "",
            "suggestions": [],
            "tips": [],
            "is_correct": all_words_present
        }
        
        if all_words_present:
            response["message"] = f"🌟 Fantastic sentence! You used all {len(word_bank)} words!\n\nYour sentence: \"{user_answer}\"\n\nGreat job! Would you like more words to practice?"
            response["encouragement"] = random.choice(self.encouragement_phrases["breakthrough_moment"])
            response["suggestions"] = [
                "Say 'give me 5 words' for new words",
                "Try 'different words' for a new challenge",
                "Ask for 'more words' anytime!"
            ]
            response["tips"] = [
                "You completed the exercise!",
                "Ready for more practice?",
                "Just ask for new words!"
            ]
        elif len(words_found) > 0:
            response["message"] = f"👍 Good work! You used {len(words_found)} out of {len(word_bank)} words.\n\nYour sentence: \"{user_answer}\"\n\nYou're missing: {', '.join(missing_words)}.\n\nWant to try adding them?"
            response["encouragement"] = random.choice(self.encouragement_phrases["good_progress"])
            response["suggestions"] = [
                f"Try adding: {', '.join(missing_words)}",
                "You're on the right track!",
                "Include ALL the words"
            ]
            response["tips"] = [
                f"Required words: {', '.join(word_bank)}",
                "Make sure your sentence makes sense",
                "Check that you used every word"
            ]
        else:
            response["message"] = f"Good try! Your sentence: \"{user_answer}\"\n\nRemember to use these words in your sentence: {', '.join(word_bank)}"
            response["encouragement"] = random.choice(self.encouragement_phrases["needs_support"])
            response["suggestions"] = [
                "Try using all the words together",
                "Look at the word list again",
                "Create a story with them"
            ]
            response["tips"] = [
                f"Required words: {', '.join(word_bank)}",
                "Create a sentence that makes sense",
                "Use all the words provided"
            ]
        
        return response
    
    def _evaluate_comprehension_response(self, user_response: str, exercise: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Evaluate reading comprehension exercise response"""
        passage = exercise.get("passage", "")
        correct_main_idea = exercise.get("correct_main_idea", "").lower()
        user_answer = user_response.strip().lower()
        
        response = {
            "message": "",
            "encouragement": "",
            "suggestions": [],
            "tips": [],
            "is_correct": False
        }
        
        # Check for non-answer responses
        if user_answer in ["done", "ok", "next", "continue", "finished"]:
            response["message"] = "Please tell me what the main idea of the passage is. What is the story mainly about?"
            response["suggestions"] = ["Read the passage again", "Think about what happens in the story", "Answer in your own words"]
            response["tips"] = ["The passage is about a cat", "What is the cat doing?", "Where is the cat?"]
            return response
        
        if not correct_main_idea:
            response["message"] = "Let me help you with this comprehension question!"
            response["suggestions"] = ["Read the passage carefully", "Look for key details", "Answer in your own words"]
            return response
        
        # Extract key concepts from the main idea
        main_idea_keywords = set(correct_main_idea.split())
        user_words = set(user_answer.split())
        
        # Also check if user mentioned key details from passage
        passage_keywords = {"cat", "mat", "sitting", "sat", "on"}
        
        # Calculate match
        main_idea_matches = main_idea_keywords.intersection(user_words)
        passage_matches = passage_keywords.intersection(user_words)
        
        # Score based on keyword matches
        if len(main_idea_matches) >= 2 or len(passage_matches) >= 2:
            match_percentage = 80
        elif len(main_idea_matches) >= 1 or len(passage_matches) >= 1:
            match_percentage = 50
        else:
            match_percentage = 0
        
        is_correct = match_percentage >= 60
        
        response["is_correct"] = is_correct
        
        if is_correct:
            response["message"] = f"✅ Excellent! Your answer '{user_answer}' shows great comprehension!"
            response["encouragement"] = random.choice(self.encouragement_phrases["high_achievement"])
            response["suggestions"] = [
                "You understood the passage well!",
                "Ready for the next question?",
                "You're a great reader!"
            ]
            response["tips"] = [
                "Keep reading carefully like this",
                "You're building strong comprehension skills",
                "Great job finding the details!"
            ]
        elif match_percentage >= 30:
            response["message"] = f"Good effort! Your answer '{user_answer}' is partially correct. The passage says: '{expected_answer}'"
            response["encouragement"] = random.choice(self.encouragement_phrases["good_progress"])
            response["suggestions"] = [
                "You're on the right track!",
                "Look for more details in the passage",
                "Try again with more information"
            ]
            response["tips"] = [
                f"The answer should include: {expected_answer}",
                "Read the passage again carefully",
                "Look for key words and details"
            ]
        else:
            response["message"] = f"Let's look at this more carefully. The passage says: '{expected_answer}'"
            response["encouragement"] = random.choice(self.encouragement_phrases["needs_support"])
            response["suggestions"] = [
                "Read the passage again",
                "Look for the answer in the text",
                "Try to find the key details"
            ]
            response["tips"] = [
                f"The correct answer is: {expected_answer}",
                "Use your finger to track the text",
                "Read slowly and carefully"
            ]
        
        return response
    
    def _handle_work_sharing(self, message: str, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle work sharing"""
        errors = analysis.get("errors", [])
        strengths = analysis.get("strengths", [])
        message_lower = message.lower()
        user_id = user_context.get("user_id") if user_context else None
        
        # Check if sharing time/progress info
        if re.search(r"\b(\d+)\s*(min|minute|second|hour)", message_lower):
            time_match = re.search(r"(\d+)\s*(min|minute|second|hour)", message_lower)
            time_value = int(time_match.group(1))
            time_unit = time_match.group(2)
            
            # Check recent performance to determine response
            recent_sessions = self.user_progress.get(user_id, {}).get("sessions", [])[-3:] if user_id else []
            
            if recent_sessions:
                correct_count = sum(1 for s in recent_sessions if s.get("data", {}).get("correct", False))
                total = len(recent_sessions)
                accuracy = (correct_count / total * 100) if total > 0 else 0
                
                if accuracy >= 70 or time_value <= 5:
                    # Good performance or quick completion - praise
                    return {
                        "message": f"🎉 Fantastic! You completed it in {time_value} {time_unit}s! That's excellent progress!\n\nYou're getting faster and more confident. Great job!",
                        "encouragement": "You're mastering these skills!",
                        "suggestions": ["Ready for more challenging words?", "Try another exercise", "Keep up the momentum!"]
                    }
                else:
                    # Needs more practice
                    return {
                        "message": f"Good effort spending {time_value} {time_unit}s practicing! 💪\n\nLet's practice some more words to build your confidence and speed.",
                        "encouragement": "Practice makes progress!",
                        "suggestions": ["Try practicing the same words again", "Ask for more words to practice", "Take your time with each word"],
                        "practice_words": self._get_practice_words_for_review(user_id) if user_id else []
                    }
            else:
                # No recent performance data - encourage more practice
                return {
                    "message": f"Great dedication spending {time_value} {time_unit}s! 🌟\n\nLet's keep practicing to build your skills even more!",
                    "encouragement": "Your effort is paying off!",
                    "suggestions": ["Ask for more practice words", "Try making sentences", "Keep practicing regularly"]
                }
        
        response = {
            "message": "Thank you for sharing your work! Let me take a look...",
            "encouragement": "",
            "suggestions": [],
            "tips": []
        }
        
        # Acknowledge strengths first
        if strengths:
            strength_feedback = {
                "good_expression": "I love how you expressed your ideas clearly!",
                "complex_vocabulary": "You used some really sophisticated words!",
                "punctuation_awareness": "Great job with your punctuation!",
                "capitalization_awareness": "Perfect capitalization!"
            }
            response["encouragement"] = " ".join([strength_feedback.get(s, "") for s in strengths])
        
        # Address errors constructively
        if errors:
            response["message"] += " I noticed a few areas where we can make improvements together."
            for error in errors[:2]:  # Limit to 2 errors
                if error.get("explanation"):
                    response["suggestions"].append(error["explanation"].get("strategy", ""))
        else:
            response["message"] += " This looks really good!"
        
        return response
    
    def _get_practice_words_for_review(self, user_id: int) -> List[str]:
        """Get words that need more practice based on user history"""
        # Return some basic words for review
        return ["cat", "dog", "run", "sit", "big"]
    
    def _handle_frustration(self, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle frustration"""
        return {
            "message": "I understand that this feels frustrating right now. That's completely normal when learning something new!",
            "emotional_support": "Remember, everyone learns at their own pace. You're doing better than you think!",
            "suggestions": [
                "Let's take a short break",
                "Try a different approach",
                "Focus on one small step at a time",
                "Remember how much you've already learned"
            ],
            "encouragement": random.choice(self.encouragement_phrases["needs_support"])
        }
    
    def _handle_celebration(self, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle celebration"""
        return {
            "message": random.choice(self.encouragement_phrases["breakthrough_moment"]),
            "encouragement": "Your hard work is paying off! This is exactly what progress looks like!",
            "suggestions": [
                "Keep up the great work!",
                "You're ready for the next challenge!",
                "Share your success with someone you care about!"
            ]
        }
    
    def _handle_general_response(self, message: str, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general conversation"""
        message_lower = message.lower()
        user_id = user_context.get("user_id") if user_context else 0
        
        # Check if user is using practice words in a sentence
        if user_id in self.last_practice_words:
            practice_words = self.last_practice_words[user_id]
            words_used = [word for word in practice_words if word.lower() in message_lower]
            
            if len(words_used) >= 2:  # Used at least 2 practice words
                all_used = len(words_used) == len(practice_words)
                
                if all_used:
                    return {
                        "message": f"🌟 Excellent sentence! You used all {len(practice_words)} practice words: {', '.join(practice_words)}!\n\nYour sentence: \"{message}\"\n\nGreat job putting them together!",
                        "encouragement": "You're really mastering these words!",
                        "suggestions": ["Ready for more words?", "Try another sentence", "You're doing amazing!"]
                    }
                else:
                    missing = [w for w in practice_words if w not in words_used]
                    return {
                        "message": f"👍 Good work! You used {len(words_used)} words: {', '.join(words_used)}.\n\nYour sentence: \"{message}\"\n\nYou're missing: {', '.join(missing)}. Want to try adding them?",
                        "encouragement": "You're on the right track!",
                        "suggestions": ["Try including all the words", "Make another sentence", "You're doing well!"]
                    }
            elif len(words_used) == 1:
                return {
                    "message": f"Nice! I see you used '{words_used[0]}' from the practice words.\n\nYour sentence: \"{message}\"\n\nTry using more of the practice words: {', '.join(practice_words)}",
                    "suggestions": ["Use all the practice words", "Try again with more words", "You can do it!"]
                }
        
        # Handle feedback requests - analyze recent performance
        if re.search(r"\bfeedback\b|\bhow did i do\b|\bhow was that\b", message_lower):
            recent_sessions = self.user_progress.get(user_id, {}).get("sessions", [])[-5:] if user_id else []
            
            if recent_sessions:
                # Calculate recent performance
                correct_count = sum(1 for s in recent_sessions if s.get("data", {}).get("correct", False))
                total = len(recent_sessions)
                accuracy = (correct_count / total * 100) if total > 0 else 0
                
                if accuracy >= 80:
                    return {
                        "message": f"🎉 High five! You're doing amazing! You got {correct_count} out of {total} exercises correct ({accuracy:.0f}%)!\n\nYou're really mastering these skills. Keep up the excellent work!",
                        "encouragement": "You're a star learner!",
                        "suggestions": ["Ready for more challenging words?", "Try a different skill area", "Keep practicing to maintain your streak!"]
                    }
                elif accuracy >= 50:
                    return {
                        "message": f"👍 Good progress! You got {correct_count} out of {total} exercises correct ({accuracy:.0f}%).\n\nYou're learning and improving. Let's practice a bit more to strengthen these skills!",
                        "encouragement": "You're on the right track!",
                        "suggestions": ["Practice the same words again", "Try similar exercises", "Take your time with each word"]
                    }
                else:
                    return {
                        "message": f"💪 Keep going! You got {correct_count} out of {total} exercises correct.\n\nLearning takes practice, and you're putting in the effort. Let's work on building your confidence with more practice!",
                        "encouragement": "Every practice session makes you stronger!",
                        "suggestions": ["Let's practice more words", "Try easier exercises first", "Take breaks when needed"]
                    }
            else:
                return {
                    "message": "I haven't seen you complete any exercises yet. Let's start practicing!\n\nTry asking for practice words or generating an exercise to get started.",
                    "suggestions": ["Say 'give me 5 words to practice'", "Click the exercise button", "Ask me any questions"]
                }
        
        # Handle instruction questions - check if there's an active exercise
        if re.search(r"\bshould i (make|write|create).*sentence\b", message_lower):
            if user_id and user_id in self.active_exercises:
                exercise = self.active_exercises[user_id]
                skill_area = exercise.get("skill_area", "")
                
                if skill_area == "writing" or "sentence" in exercise.get("instructions", "").lower():
                    return {
                        "message": "Yes! The exercise asks you to write a sentence. Go ahead and create one using the words provided!",
                        "suggestions": ["Use all the practice words", "Make it creative", "Check your spelling"]
                    }
                else:
                    return {
                        "message": "For this exercise, you can practice the words individually. But making sentences is always great practice too if you'd like!",
                        "suggestions": ["Practice each word first", "Then try making sentences", "Both approaches work well"]
                    }
            else:
                return {
                    "message": "Yes! Making sentences with practice words is an excellent way to learn. Go ahead and try it!",
                    "suggestions": ["Use the practice words I gave you", "Be creative", "Don't worry about perfection"]
                }
        
        # Default general response
        return {
            "message": "I'm here to help you learn and grow! What would you like to work on today?",
            "suggestions": self._get_daily_suggestions(user_context) + ["Ask me for practice words by saying 'give me 5 words to practice'"],
            "lesson_recommendations": lesson_manager.get_all_lessons_summary()[:3] if lesson_manager else []
        }
    
    def _provide_emotional_support(self, emotion: str) -> str:
        """Provide emotional support"""
        support_messages = {
            "frustrated": "It's okay to feel frustrated. Learning can be challenging, but you're stronger than you know!",
            "confused": "Confusion is just your brain making room for new understanding. Let's work through this together!",
            "excited": "I love your enthusiasm! That positive energy will help you learn even faster!",
            "worried": "It's natural to feel worried about new things. Remember, I'm here to support you every step of the way!",
            "proud": "You should be proud! Recognizing your own progress is a sign of wisdom!"
        }
        
        return support_messages.get(emotion, "You're doing great! Keep up the good work!")
    
    def _generate_strength_based_encouragement(self, strengths: List[str]) -> str:
        """Generate encouragement based on strengths"""
        strength_messages = {
            "good_expression": "You have a wonderful way of expressing your thoughts!",
            "complex_vocabulary": "Your vocabulary is really impressive!",
            "punctuation_awareness": "You have a great sense of how punctuation works!",
            "capitalization_awareness": "Great attention to capitalization!"
        }
        
        messages = [strength_messages.get(strength, "") for strength in strengths if strength in strength_messages]
        return " ".join(messages) if messages else "You're showing real progress!"
    
    def _get_daily_suggestions(self, user_context: Dict[str, Any]) -> List[str]:
        """Get daily suggestions"""
        if not user_context:
            return [
                "Start with a phonics warm-up",
                "Practice sight words for 5 minutes",
                "Read a short story together"
            ]
        
        suggestions = []
        
        recent_accuracy = user_context.get("recent_accuracy", 0)
        if recent_accuracy < 70:
            suggestions.append("Let's review some fundamentals to build confidence")
        elif recent_accuracy > 85:
            suggestions.append("You're ready for a new challenge!")
        
        last_lesson = user_context.get("last_lesson_category", "")
        if last_lesson:
            suggestions.append(f"Continue building on your {last_lesson} skills")
        
        return suggestions or ["Let's start with something fun and engaging!", "Try asking: 'give me 5 words to practice'"]
    
    def _get_fallback_response(self, analysis: Dict[str, Any]) -> str:
        """Get fallback response"""
        intent = analysis.get("intent", "general")
        
        fallback_responses = {
            "word_request": "I'd be happy to give you some practice words!",
            "help_request": "I'm here to help you! Let's work through this together.",
            "celebration": "That's wonderful! You're doing such great work!",
            "practice_request": "Let's practice together! I have some perfect activities for you.",
            "spelling_check": "Let me help you with spelling!",
            "short_text_submission": "Great effort! Keep practicing!",
            "general": "I'm here to help you learn! What would you like to work on?"
        }
        
        return fallback_responses.get(intent, "I'm here to help you learn and grow!")
    
    async def _generate_api_response(self, user_message: str, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Generate response using OpenAI API"""
        try:
            import aiohttp
            
            # Build conversation history for context
            user_id = user_context.get("user_id") if user_context else None
            conversation_history = []
            
            if user_id:
                recent_messages = self.get_current_session_history(user_id)[-5:]  # Last 5 exchanges
                for msg in recent_messages:
                    conversation_history.append({"role": "user", "content": msg.get("user", "")})
                    conversation_history.append({"role": "assistant", "content": msg.get("bot", "")})
            
            # Build system prompt with context
            system_prompt = self._build_system_prompt(analysis, user_context)
            
            # Build messages array
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend(conversation_history)
            messages.append({"role": "user", "content": user_message})
            
            payload = {
                "model": "gpt-3.5-turbo",
                "messages": messages,
                "max_tokens": 200,
                "temperature": 0.8
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.api_url, json=payload, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as response:
                    if response.status == 200:
                        data = await response.json()
                        api_message = data["choices"][0]["message"]["content"].strip()
                        print(f"[AI_TUTOR] OpenAI API response generated successfully")
                        return api_message
                    else:
                        error_text = await response.text()
                        print(f"[AI_TUTOR] API error {response.status}: {error_text}")
        except Exception as e:
            print(f"[AI_TUTOR] API response generation failed: {e}")
        
        return ""
    
    def _build_system_prompt(self, analysis: Dict[str, Any], user_context: Dict[str, Any]) -> str:
        """Build system prompt for OpenAI API"""
        prompt_parts = [
            "You are Lexi, a warm, supportive AI tutor specializing in helping students with dyslexia.",
            "Your role is to provide personalized learning support with patience, encouragement, and understanding.",
            "\nKey guidelines:",
            "- Be conversational and friendly, like a supportive teacher",
            "- Celebrate small victories and progress",
            "- Provide constructive feedback on errors without discouragement",
            "- Use emojis occasionally to make responses engaging (🌟, 📚, ✨, 💪, 🎉)",
            "- Keep responses concise (2-4 sentences) unless explaining concepts",
            "- Adapt to the student's emotional state and learning needs",
            "- Offer specific, actionable suggestions",
            "- Remember context from the conversation"
        ]
        
        # Add emotional context
        emotion = analysis.get("emotion", "neutral")
        if emotion == "frustrated":
            prompt_parts.append("\nThe student seems frustrated - be extra encouraging and patient.")
        elif emotion == "excited":
            prompt_parts.append("\nThe student is excited - match their enthusiasm!")
        elif emotion == "confused":
            prompt_parts.append("\nThe student is confused - provide clear, simple explanations.")
        elif emotion == "worried":
            prompt_parts.append("\nThe student seems worried - be reassuring and supportive.")
        
        # Add learning focus
        learning_need = analysis.get("learning_need", "general")
        if learning_need != "general":
            prompt_parts.append(f"\nFocus area: {learning_need} skills")
        
        # Add error context
        errors = analysis.get("errors", [])
        if errors:
            error_words = [e.get("word", "") for e in errors[:2]]
            prompt_parts.append(f"\nNote: Student has spelling opportunities with: {', '.join(error_words)}")
        
        # Add user context
        if user_context:
            grade_level = user_context.get("grade_level")
            if grade_level:
                prompt_parts.append(f"\nStudent grade level: {grade_level}")
        
        return "\n".join(prompt_parts)
    
    def _handle_exercise_response(self, user_message: str, user_id: int, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Handle exercise response"""
        exercise = self.active_exercises.get(user_id)
        if not exercise:
            return None
        
        user_answer = user_message.strip().lower()
        skill_area = exercise.get("skill_area", "")
        
        is_correct = False
        feedback = ""
        
        if skill_area == "writing":
            required_words = exercise.get("word_bank", [])
            words_found = [word for word in required_words if word.lower() in user_answer]
            
            if len(words_found) == len(required_words):
                is_correct = True
                feedback = f"🌟 Excellent sentence! You used all the words: {', '.join(required_words)}."
            elif len(words_found) > 0:
                missing = [w for w in required_words if w not in words_found]
                feedback = f"Good start! You used {', '.join(words_found)}, but you're missing: {', '.join(missing)}."
            else:
                feedback = f"Remember to use these words in your sentence: {', '.join(required_words)}"
        
        elif skill_area == "sight_words":
            exercise_type = exercise.get("exercise_type", "")
            
            if exercise_type == "sentence_completion":
                # For sentence completion, parse user's complete sentences
                exercises_list = exercise.get("exercises", [])
                
                if exercises_list:
                    # Split user answer into sentences (by period or newline)
                    user_sentences = [s.strip() for s in re.split(r'[.\n]+', user_answer) if s.strip()]
                    
                    correct_count = 0
                    total_count = len(exercises_list)
                    feedback_parts = []
                    
                    for idx, ex in enumerate(exercises_list):
                        expected_word = ex.get("correct_answer", "").lower()
                        sentence_template = ex.get("sentence", "")
                        
                        # Get the sentence pattern without the blank
                        pattern_parts = sentence_template.replace("___", "").strip().lower().split()
                        
                        # Check if user provided a sentence matching this pattern with the correct word
                        found_correct = False
                        for user_sent in user_sentences:
                            user_sent_lower = user_sent.lower()
                            # Check if sentence contains the expected word and pattern words
                            if expected_word in user_sent_lower:
                                # Check if it matches the sentence pattern
                                if all(part in user_sent_lower for part in pattern_parts if part):
                                    found_correct = True
                                    break
                        
                        if found_correct:
                            correct_count += 1
                        else:
                            feedback_parts.append(f"Sentence {idx+1}: needs '{expected_word}'")
                    
                    if correct_count == total_count:
                        is_correct = True
                        feedback = f"🌟 Excellent! You completed all {total_count} sentences correctly!"
                    elif correct_count > 0:
                        is_correct = False
                        feedback = f"Good work! You got {correct_count} out of {total_count} correct. {', '.join(feedback_parts)}"
                    else:
                        is_correct = False
                        expected_words = [ex.get("correct_answer", "") for ex in exercises_list]
                        feedback = f"Please complete the sentences with these words: {', '.join(expected_words)}"
                else:
                    feedback = "No sentences found in exercise."
            else:
                # Flash cards - single word recognition
                exercises_list = exercise.get("exercises", [])
                correct_answer = None
                
                if exercises_list:
                    for ex in exercises_list:
                        if ex.get("correct_answer"):
                            correct_answer = ex.get("correct_answer")
                            break
                
                if not correct_answer:
                    words = exercise.get("words", [])
                    if words and user_answer in [w.lower() for w in words]:
                        correct_answer = user_answer
                        is_correct = True
                        feedback = f"✅ Perfect! You recognized '{user_answer}'!"
                    elif words:
                        correct_answer = words[0]
                        feedback = f"Good try! For this exercise, practice these sight words: {', '.join(words[:5])}. Try typing one of them!"
                
                if correct_answer and not is_correct:
                    if user_answer == correct_answer.lower():
                        is_correct = True
                        feedback = f"✅ Perfect! '{correct_answer}' is the correct sight word!"
                    else:
                        feedback = f"Good effort! This sight word is '{correct_answer}'. You wrote '{user_answer}'."

        elif skill_area == "phonics" and exercise.get("exercise_type") == "word_building":
            # Delegate to the word building evaluator which handles sentences and single words
            resp = self._evaluate_word_building_response(user_answer, exercise, analysis)
            if user_id in self.active_exercises:
                del self.active_exercises[user_id]
            return resp
        
        elif skill_area == "spelling":
            # Get correct word from exercise
            exercises_list = exercise.get("exercises", [])
            correct_word = None
            
            if exercises_list:
                first_ex = exercises_list[0]
                correct_word = first_ex.get("correct_word", "")
            
            if correct_word:
                if user_answer == correct_word.lower():
                    is_correct = True
                    feedback = f"📝 Excellent! You spelled '{correct_word}' correctly!"
                else:
                    feedback = f"Good try! The correct spelling is '{correct_word}'. You wrote '{user_answer}'."
            else:
                # No correct word specified
                if len(user_answer) > 0 and any(c.isalpha() for c in user_answer):
                    is_correct = True
                    feedback = f"📝 Nice work spelling '{user_answer}'! Keep practicing!"
                else:
                    feedback = "Remember to use letters when spelling words."
        
        else:
            if len(user_answer) > 0:
                is_correct = True
                feedback = f"✨ Good answer: '{user_answer}'!"
        
        if user_id in self.active_exercises:
            del self.active_exercises[user_id]
        
        encouragement_level = "high_achievement" if is_correct else "good_progress"
        
        response = {
            "message": feedback,
            "encouragement": random.choice(self.encouragement_phrases[encouragement_level]),
            "suggestions": [
                "Ready for another challenge?",
                "Want to practice something specific?",
                "You're making great progress!"
            ] if is_correct else [
                "Let's practice this word again",
                "Sight words need to be memorized",
                "Try writing it a few more times"
            ],
            "tips": [
                "Every practice session makes you stronger",
                "Mistakes are just learning opportunities",
                "You're doing better than you think!"
            ],
            "emotional_support": "You're doing amazing! 🌟" if is_correct else "Keep trying! 💪",
            "is_correct": is_correct
        }
        
        # Add correct answer to tips if wrong
        if not is_correct and correct_answer:
            response["tips"].insert(0, f"The correct word is: {correct_answer}")
            response["tips"].insert(1, "Sight words don't follow phonetic rules")
        
        return response
    
    def set_active_exercise(self, user_id: int, exercise: Dict[str, Any]):
        """Set active exercise"""
        self.active_exercises[user_id] = exercise
        print(f"[AI_TUTOR] Set active exercise for user {user_id}")
    
    def update_user_context(self, user_id: int, session_data: Dict[str, Any]):
        """Update user context"""
        if user_id not in self.user_progress:
            self.user_progress[user_id] = {
                "sessions": [],
                "strengths": [],
                "areas_for_improvement": [],
                "preferred_learning_style": "visual"
            }
        
        self.user_progress[user_id]["sessions"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "data": session_data
        })
        
        self.user_progress[user_id]["sessions"] = self.user_progress[user_id]["sessions"][-10:]
    
    def start_new_session(self, user_id: int) -> str:
        """Start a new session for user (called on login)"""
        now = datetime.utcnow()
        session_id = f"session_{now.strftime('%Y%m%d')}_{now.timestamp()}"
        self.current_sessions[user_id] = session_id
        
        # Always load history from database to ensure we have latest data
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = {}
        
        # Load history from database every time to get all sessions
        try:
            from database.database import db_manager
            if isinstance(user_id, str) and "@" in user_id:
                user = db_manager.get_user_by_email(user_id)
                if user:
                    loaded_history = db_manager.load_chat_history(user["id"])
                    # Merge loaded history with existing (preserve any unsaved messages)
                    for sess_id, messages in loaded_history.items():
                        if sess_id not in self.conversation_history[user_id]:
                            self.conversation_history[user_id][sess_id] = messages
            else:
                loaded_history = db_manager.load_chat_history(user_id)
                # Merge loaded history with existing
                for sess_id, messages in loaded_history.items():
                    if sess_id not in self.conversation_history[user_id]:
                        self.conversation_history[user_id][sess_id] = messages
            print(f"[AI_TUTOR] Loaded {len(self.conversation_history[user_id])} total sessions from database")
        except Exception as e:
            print(f"[AI_TUTOR] Failed to load history from database: {e}")
        
        # Create new session
        self.conversation_history[user_id][session_id] = []
        print(f"[AI_TUTOR] Started new session {session_id} for user {user_id}")
        return session_id
    
    def get_current_session_id(self, user_id: int) -> str:
        """Get current session ID for user"""
        if user_id not in self.current_sessions:
            return self.start_new_session(user_id)
        return self.current_sessions[user_id]
    
    def get_current_session_history(self, user_id: int) -> List[Dict[str, Any]]:
        """Get conversation history for current session"""
        session_id = self.get_current_session_id(user_id)
        
        if user_id not in self.conversation_history:
            return []
        
        return self.conversation_history[user_id].get(session_id, [])
    
    def get_history(self, user_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Get conversation history for current session (backward compatibility)"""
        return self.get_current_session_history(user_id)[-limit:]

    def get_conversation_context(self, user_id: int) -> Dict[str, Any]:
        """Get conversation context for more natural dialogue"""
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = {
                "turns": 0,
                "last_topic": "",
                "conversation_style": "formal",
                "user_preferences": {}
            }
        return self.conversation_context[user_id]
    
    def update_conversation_context(self, user_id: int, topic: str, user_message: str):
        """Update conversation context for continuity"""
        if user_id not in self.conversation_context:
            self.conversation_context[user_id] = {
                "turns": 0,
                "last_topic": "",
                "conversation_style": "formal",
                "user_preferences": {}
            }
        
        context = self.conversation_context[user_id]
        context["turns"] = context.get("turns", 0) + 1
        context["last_topic"] = topic
        
        # Detect conversation style based on user messages
        if any(word in user_message.lower() for word in ["hi", "hey", "thanks", "thanks!", "thank you"]):
            context["conversation_style"] = "casual"
        elif any(word in user_message.lower() for word in ["please", "could you", "would you"]):
            context["conversation_style"] = "polite"
    
    def get_conversation_continuity(self, user_id: int) -> str:
        """Get conversation continuity based on context"""
        context = self.get_conversation_context(user_id)
        turns = context.get("turns", 0)
        
        if turns == 0:
            return "First interaction - warm welcome"
        elif turns < 3:
            return "Early conversation - establishing rapport"
        elif turns < 10:
            return "Developing conversation - building trust"
        else:
            return "Established conversation - comfortable rapport"
    
    def add_conversation_memory(self, user_id: int, message: str, response: str):
        """Add to conversation memory for context retention"""
        session_id = self.get_current_session_id(user_id)
        
        if user_id not in self.conversation_history:
            self.conversation_history[user_id] = {}
        
        if session_id not in self.conversation_history[user_id]:
            self.conversation_history[user_id][session_id] = []
        
        # Add to history with full message content
        self.conversation_history[user_id][session_id].append({
            "user": message,
            "bot": response,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Save to database
        try:
            from database.database import db_manager
            # Get user ID from email if it's an email string
            if isinstance(user_id, str) and "@" in user_id:
                user = db_manager.get_user_by_email(user_id)
                if user:
                    db_manager.save_chat_message(user["id"], session_id, message, response)
            else:
                db_manager.save_chat_message(user_id, session_id, message, response)
        except Exception as e:
            print(f"[AI_TUTOR] Failed to save to database: {e}")
        
        print(f"[AI_TUTOR] Added conversation: user={user_id}, session={session_id}, total_messages={len(self.conversation_history[user_id][session_id])}")
    
    def get_recent_conversation(self, user_id: int, limit: int = 3) -> List[str]:
        """Get recent conversation for context"""
        session_id = self.get_current_session_id(user_id)
        
        if user_id not in self.conversation_history:
            return []
        
        session_history = self.conversation_history[user_id].get(session_id, [])
        recent = session_history[-limit:] if len(session_history) > limit else session_history
        
        return [entry["user"] + " -> " + entry["bot"] for entry in recent]
    
    def generate_natural_followup(self, user_context: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """Generate natural followup questions based on context"""
        user_id = user_context.get("user_id") if user_context else None
        context = self.get_conversation_context(user_id) if user_id else {}
        
        turns = context.get("turns", 0)
        last_topic = context.get("last_topic", "")
        
        followups = []
        
        # First few turns - establish rapport
        if turns < 3:
            followups.append("What would you like to work on today?")
            followups.append("How can I help you learn today?")
        # Building conversation
        elif last_topic:
            followups.append(f"How did you feel about practicing {last_topic}?")
            followups.append(f"Would you like to continue with {last_topic} or try something new?")
        # Established conversation
        else:
            followups.append("What else would you like to practice?")
            followups.append("You're doing great! What's next?")
        
        return random.choice(followups)

    def clear_history(self, user_id: int):
        """Clear conversation history for current session"""
        session_id = self.get_current_session_id(user_id)
        
        if user_id in self.conversation_history and session_id in self.conversation_history[user_id]:
            self.conversation_history[user_id][session_id] = []
        
        # Also clear active exercises and practice words
        if user_id in self.active_exercises:
            del self.active_exercises[user_id]
        if user_id in self.last_practice_words:
            del self.last_practice_words[user_id]
        
# Initialize the AI tutor
ai_tutor = AITutor()