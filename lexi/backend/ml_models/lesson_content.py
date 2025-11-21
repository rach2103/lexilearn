"""
Comprehensive lesson content for dyslexic students
Structured learning materials with multi-sensory approaches
"""

from typing import Dict, List, Any
import json
from datetime import datetime

class LessonContentManager:
    """Manages structured lesson content for dyslexic learners"""
    
    def __init__(self):
        self.lessons = self._initialize_lessons()
        self.exercises = self._initialize_exercises()
        self.assessments = self._initialize_assessments()
    
    def _initialize_lessons(self) -> Dict[int, Dict[str, Any]]:
        """Initialize comprehensive lesson content"""
        return {
            1: {
                "id": 1,
                "title": "Phonemic Awareness Fundamentals",
                "category": "phonics",
                "difficulty": "beginner",
                "duration": 20,
                "description": "Master the foundation of reading by understanding individual sounds in words",
                "learning_objectives": [
                    "Identify individual phonemes in spoken words",
                    "Blend phonemes to form words",
                    "Segment words into individual sounds",
                    "Manipulate phonemes to create new words"
                ],
                "content": {
                    "introduction": "Phonemic awareness is the ability to hear, identify, and manipulate individual sounds in spoken words. This is crucial for reading success.",
                    "key_concepts": [
                        {
                            "concept": "Phoneme Identification",
                            "explanation": "A phoneme is the smallest unit of sound in language. For example, the word 'cat' has three phonemes: /k/, /æ/, /t/",
                            "examples": [
                                {"word": "cat", "phonemes": ["/k/", "/æ/", "/t/"], "audio_cue": "Listen: c-a-t"},
                                {"word": "dog", "phonemes": ["/d/", "/ɔ/", "/g/"], "audio_cue": "Listen: d-o-g"},
                                {"word": "fish", "phonemes": ["/f/", "/ɪ/", "/ʃ/"], "audio_cue": "Listen: f-i-sh"}
                            ]
                        },
                        {
                            "concept": "Phoneme Blending",
                            "explanation": "Combining individual sounds to form words",
                            "examples": [
                                {"sounds": ["/s/", "/u/", "/n/"], "word": "sun", "instruction": "Blend these sounds together"},
                                {"sounds": ["/b/", "/ɪ/", "/g/"], "word": "big", "instruction": "What word do these sounds make?"}
                            ]
                        }
                    ],
                    "activities": [
                        {
                            "name": "Sound Isolation",
                            "type": "interactive",
                            "instructions": "Listen to the word and identify the first sound you hear",
                            "examples": ["What's the first sound in 'apple'?", "What's the last sound in 'book'?"]
                        },
                        {
                            "name": "Sound Blending Game",
                            "type": "game",
                            "instructions": "Combine the sounds to make a word",
                            "difficulty_levels": ["2-3 phonemes", "4-5 phonemes", "complex blends"]
                        }
                    ]
                },
                "multisensory_elements": {
                    "visual": ["Color-coded phoneme charts", "Mouth position diagrams"],
                    "auditory": ["Clear pronunciation examples", "Rhythm and rhyme patterns"],
                    "kinesthetic": ["Hand gestures for each sound", "Physical movement activities"],
                    "tactile": ["Textured letter cards", "Sand tray writing"]
                },
                "assessment_criteria": {
                    "phoneme_identification": "Can identify 80% of phonemes correctly",
                    "blending_accuracy": "Successfully blends 3-4 phoneme words",
                    "segmentation_skills": "Can break words into individual sounds"
                }
            },
            
            2: {
                "id": 2,
                "title": "Letter-Sound Correspondence",
                "category": "phonics",
                "difficulty": "beginner",
                "duration": 25,
                "description": "Connect letters with their corresponding sounds using systematic phonics instruction",
                "learning_objectives": [
                    "Master single letter-sound relationships",
                    "Recognize common letter patterns",
                    "Apply phonics rules in reading",
                    "Decode simple words using phonics knowledge"
                ],
                "content": {
                    "introduction": "Understanding how letters represent sounds is essential for reading. We'll use systematic, explicit instruction to build this foundation.",
                    "key_concepts": [
                        {
                            "concept": "Single Letter Sounds",
                            "explanation": "Each letter has a primary sound. Learning these systematically builds reading foundation.",
                            "sequence": ["a", "m", "t", "s", "i", "f", "d", "r", "o", "g", "l", "h", "u", "c", "b", "n", "k", "v", "e", "w", "j", "p", "y", "x", "q", "z"],
                            "examples": [
                                {"letter": "m", "sound": "/m/", "keyword": "mouse", "gesture": "rub tummy"},
                                {"letter": "s", "sound": "/s/", "keyword": "snake", "gesture": "weave like snake"},
                                {"letter": "t", "sound": "/t/", "keyword": "tiger", "gesture": "turn head side to side"}
                            ]
                        },
                        {
                            "concept": "Consonant Digraphs",
                            "explanation": "Two letters that make one sound",
                            "examples": [
                                {"digraph": "sh", "sound": "/ʃ/", "words": ["ship", "fish", "wash"]},
                                {"digraph": "ch", "sound": "/tʃ/", "words": ["chair", "much", "lunch"]},
                                {"digraph": "th", "sound": "/θ/ or /ð/", "words": ["think", "that", "with"]}
                            ]
                        }
                    ],
                    "activities": [
                        {
                            "name": "Letter-Sound Matching",
                            "type": "matching",
                            "instructions": "Match each letter with its sound",
                            "adaptive_difficulty": True
                        },
                        {
                            "name": "Word Building",
                            "type": "construction",
                            "instructions": "Use letter tiles to build words",
                            "progression": ["CVC words", "CVCC words", "CCVC words"]
                        }
                    ]
                },
                "multisensory_elements": {
                    "visual": ["Large, clear letter cards", "Color coding for vowels/consonants"],
                    "auditory": ["Letter sound songs", "Alliterative phrases"],
                    "kinesthetic": ["Sky writing", "Letter formation in air"],
                    "tactile": ["Sandpaper letters", "Play dough letter formation"]
                }
            },
            
            3: {
                "id": 3,
                "title": "Sight Word Mastery",
                "category": "vocabulary",
                "difficulty": "beginner",
                "duration": 15,
                "description": "Learn high-frequency words that appear often in text but may not follow regular phonics patterns",
                "learning_objectives": [
                    "Recognize 100 most common sight words instantly",
                    "Read sight words in context",
                    "Spell common sight words accurately",
                    "Use sight words in writing"
                ],
                "content": {
                    "introduction": "Sight words are words that appear frequently in text. Learning to recognize them instantly improves reading fluency.",
                    "word_lists": {
                        "pre_primer": ["a", "and", "away", "big", "blue", "can", "come", "down", "find", "for", "funny", "go", "help", "here", "I", "in", "is", "it", "jump", "little", "look", "make", "me", "my", "not", "one", "play", "red", "run", "said", "see", "the", "three", "to", "two", "up", "we", "where", "yellow", "you"],
                        "primer": ["all", "am", "are", "at", "ate", "be", "black", "brown", "but", "came", "did", "do", "eat", "four", "get", "good", "have", "he", "into", "like", "must", "new", "no", "now", "on", "our", "out", "please", "pretty", "ran", "ride", "saw", "say", "she", "so", "soon", "that", "there", "they", "this", "too", "under", "want", "was", "well", "went", "what", "white", "who", "will", "with", "yes"],
                        "first_grade": ["after", "again", "an", "any", "as", "ask", "by", "could", "every", "fly", "from", "give", "giving", "had", "has", "her", "him", "his", "how", "just", "know", "let", "live", "may", "of", "old", "once", "open", "over", "put", "round", "some", "stop", "take", "thank", "them", "think", "walk", "were", "when"]
                    },
                    "teaching_strategies": [
                        {
                            "strategy": "Look-Say Method",
                            "description": "Show word, say word, student repeats",
                            "steps": ["Display word card", "Say word clearly", "Student repeats", "Use in sentence"]
                        },
                        {
                            "strategy": "Trace-Say Method",
                            "description": "Multi-sensory approach combining visual, auditory, and kinesthetic",
                            "steps": ["Trace word while saying it", "Write word from memory", "Check accuracy", "Use in context"]
                        }
                    ],
                    "activities": [
                        {
                            "name": "Sight Word Bingo",
                            "type": "game",
                            "instructions": "Mark sight words as they're called out",
                            "benefits": ["Recognition speed", "Visual memory", "Engagement"]
                        },
                        {
                            "name": "Rainbow Writing",
                            "type": "writing",
                            "instructions": "Write each sight word in different colors",
                            "benefits": ["Visual memory", "Spelling practice", "Fine motor skills"]
                        }
                    ]
                }
            },
            
            4: {
                "id": 4,
                "title": "Reading Fluency Development",
                "category": "fluency",
                "difficulty": "intermediate",
                "duration": 30,
                "description": "Build smooth, accurate, and expressive reading through systematic practice",
                "learning_objectives": [
                    "Read with appropriate speed and accuracy",
                    "Use proper expression and intonation",
                    "Recognize punctuation cues",
                    "Self-monitor reading for meaning"
                ],
                "content": {
                    "introduction": "Reading fluency is the bridge between word recognition and comprehension. Fluent readers can focus on meaning rather than decoding.",
                    "components": {
                        "accuracy": {
                            "description": "Reading words correctly",
                            "target": "95% accuracy for instructional level text",
                            "strategies": ["Slow down for difficult words", "Use context clues", "Apply phonics knowledge"]
                        },
                        "rate": {
                            "description": "Reading at appropriate speed",
                            "benchmarks": {
                                "grade_1": "60 words per minute",
                                "grade_2": "90 words per minute",
                                "grade_3": "110 words per minute"
                            }
                        },
                        "prosody": {
                            "description": "Reading with expression and proper phrasing",
                            "elements": ["Intonation", "Stress", "Phrasing", "Rhythm"]
                        }
                    },
                    "practice_methods": [
                        {
                            "method": "Repeated Reading",
                            "description": "Read the same passage multiple times",
                            "procedure": ["Choose appropriate text", "Read 3-4 times", "Track improvement", "Celebrate progress"]
                        },
                        {
                            "method": "Choral Reading",
                            "description": "Read together with model",
                            "benefits": ["Confidence building", "Prosody modeling", "Reduced anxiety"]
                        },
                        {
                            "method": "Echo Reading",
                            "description": "Teacher reads, student echoes",
                            "benefits": ["Pronunciation practice", "Phrasing awareness", "Expression modeling"]
                        }
                    ]
                }
            },
            
            5: {
                "id": 5,
                "title": "Reading Comprehension Strategies",
                "category": "comprehension",
                "difficulty": "intermediate",
                "duration": 35,
                "description": "Develop active reading strategies to understand and analyze text meaning",
                "learning_objectives": [
                    "Use before, during, and after reading strategies",
                    "Make connections between text and experience",
                    "Ask and answer questions about text",
                    "Summarize main ideas and details"
                ],
                "content": {
                    "introduction": "Comprehension is the ultimate goal of reading. Active readers use strategies to construct meaning from text.",
                    "strategy_categories": {
                        "before_reading": [
                            {
                                "strategy": "Preview",
                                "description": "Look at title, pictures, headings",
                                "purpose": "Activate prior knowledge and set purpose"
                            },
                            {
                                "strategy": "Predict",
                                "description": "Make educated guesses about content",
                                "purpose": "Engage with text and create expectations"
                            }
                        ],
                        "during_reading": [
                            {
                                "strategy": "Visualize",
                                "description": "Create mental images of text content",
                                "purpose": "Enhance understanding and memory"
                            },
                            {
                                "strategy": "Question",
                                "description": "Ask questions about text content",
                                "purpose": "Monitor understanding and deepen thinking"
                            },
                            {
                                "strategy": "Connect",
                                "description": "Link text to personal experience, other texts, or world knowledge",
                                "purpose": "Make text meaningful and memorable"
                            }
                        ],
                        "after_reading": [
                            {
                                "strategy": "Summarize",
                                "description": "Identify main ideas and key details",
                                "purpose": "Consolidate understanding"
                            },
                            {
                                "strategy": "Evaluate",
                                "description": "Judge text quality, accuracy, or relevance",
                                "purpose": "Develop critical thinking"
                            }
                        ]
                    }
                }
            },
            
            6: {
                "id": 6,
                "title": "Spelling Patterns and Rules",
                "category": "spelling",
                "difficulty": "intermediate",
                "duration": 25,
                "description": "Master common spelling patterns and rules to improve writing accuracy",
                "learning_objectives": [
                    "Apply common spelling rules",
                    "Recognize spelling patterns",
                    "Use spelling strategies for unknown words",
                    "Proofread and self-correct spelling errors"
                ],
                "content": {
                    "spelling_rules": [
                        {
                            "rule": "Silent E Rule",
                            "description": "When a word ends in silent e, the vowel before it says its name",
                            "examples": ["make", "bike", "hope", "cute"],
                            "exceptions": ["have", "give", "love"]
                        },
                        {
                            "rule": "Doubling Rule",
                            "description": "Double the final consonant when adding suffixes to short vowel words",
                            "examples": ["hop → hopping", "run → running", "big → bigger"]
                        },
                        {
                            "rule": "Drop E Rule",
                            "description": "Drop silent e when adding vowel suffixes",
                            "examples": ["make → making", "hope → hoping", "care → caring"]
                        }
                    ],
                    "spelling_patterns": [
                        {
                            "pattern": "CVC Pattern",
                            "description": "Consonant-Vowel-Consonant words usually have short vowel sounds",
                            "examples": ["cat", "dog", "pen", "big", "cup"]
                        },
                        {
                            "pattern": "CVCe Pattern",
                            "description": "Consonant-Vowel-Consonant-silent e words have long vowel sounds",
                            "examples": ["cake", "bike", "rope", "cube"]
                        }
                    ]
                }
            },
            
            7: {
                "id": 7,
                "title": "Writing Fundamentals",
                "category": "writing",
                "difficulty": "beginner",
                "duration": 30,
                "description": "Develop basic writing skills including letter formation, sentence structure, and organization",
                "learning_objectives": [
                    "Form letters correctly and legibly",
                    "Write complete sentences",
                    "Organize ideas in logical order",
                    "Use basic punctuation and capitalization"
                ],
                "content": {
                    "letter_formation": {
                        "lowercase": {
                            "starting_letters": ["c", "o", "a", "d", "g", "q"],
                            "description": "Start with circular motions",
                            "technique": "Start at 2 o'clock position"
                        },
                        "uppercase": {
                            "starting_letters": ["L", "F", "E", "H", "T", "I"],
                            "description": "Start with straight line letters",
                            "technique": "Top to bottom, left to right"
                        }
                    },
                    "sentence_structure": {
                        "components": ["Subject", "Predicate", "Complete thought"],
                        "examples": [
                            {"sentence": "The dog runs.", "subject": "The dog", "predicate": "runs"},
                            {"sentence": "My sister plays soccer.", "subject": "My sister", "predicate": "plays soccer"}
                        ]
                    }
                }
            },
            
            8: {
                "id": 8,
                "title": "Memory and Organization Strategies",
                "category": "study_skills",
                "difficulty": "intermediate",
                "duration": 20,
                "description": "Learn techniques to improve memory, organization, and study effectiveness",
                "learning_objectives": [
                    "Use memory strategies for learning",
                    "Organize materials and workspace",
                    "Manage time effectively",
                    "Apply study techniques for different subjects"
                ],
                "content": {
                    "memory_strategies": [
                        {
                            "strategy": "Mnemonics",
                            "description": "Memory aids using associations",
                            "examples": ["ROY G. BIV for rainbow colors", "My Very Educated Mother Just Served Us Nachos for planets"]
                        },
                        {
                            "strategy": "Chunking",
                            "description": "Break information into smaller, manageable pieces",
                            "examples": ["Phone numbers: 555-123-4567", "Social Security: 123-45-6789"]
                        },
                        {
                            "strategy": "Visualization",
                            "description": "Create mental images to remember information",
                            "techniques": ["Story method", "Method of loci", "Mind mapping"]
                        }
                    ],
                    "organization_tools": [
                        "Color-coded folders",
                        "Daily planners",
                        "Checklists",
                        "Digital calendars"
                    ]
                }
            }
        }
    
    def _initialize_exercises(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize practice exercises for each lesson"""
        return {
            "phonemic_awareness": [
                {
                    "type": "sound_identification",
                    "instruction": "What sound do you hear at the beginning of this word?",
                    "items": [
                        {"word": "apple", "answer": "/æ/", "audio": "apple.mp3"},
                        {"word": "ball", "answer": "/b/", "audio": "ball.mp3"},
                        {"word": "cat", "answer": "/k/", "audio": "cat.mp3"}
                    ]
                },
                {
                    "type": "sound_blending",
                    "instruction": "Blend these sounds to make a word",
                    "items": [
                        {"sounds": ["/s/", "/u/", "/n/"], "answer": "sun"},
                        {"sounds": ["/c/", "/a/", "/t/"], "answer": "cat"},
                        {"sounds": ["/d/", "/o/", "/g/"], "answer": "dog"}
                    ]
                }
            ],
            "sight_words": [
                {
                    "type": "flash_cards",
                    "instruction": "Read each word as quickly as you can",
                    "word_set": "pre_primer",
                    "timing": True
                },
                {
                    "type": "sentence_completion",
                    "instruction": "Choose the correct sight word to complete the sentence",
                    "items": [
                        {"sentence": "I ___ a red ball.", "options": ["see", "saw", "say"], "answer": "see"},
                        {"sentence": "The dog can ___.", "options": ["run", "ran", "running"], "answer": "run"}
                    ]
                }
            ]
        }
    
    def _initialize_assessments(self) -> Dict[str, Dict[str, Any]]:
        """Initialize assessment rubrics and criteria"""
        return {
            "phonemic_awareness": {
                "criteria": {
                    "sound_identification": {"excellent": 90, "good": 80, "needs_improvement": 70},
                    "sound_blending": {"excellent": 85, "good": 75, "needs_improvement": 65},
                    "sound_segmentation": {"excellent": 85, "good": 75, "needs_improvement": 65}
                },
                "feedback": {
                    "excellent": "Outstanding phonemic awareness skills!",
                    "good": "Good progress! Keep practicing.",
                    "needs_improvement": "Let's work on this skill together."
                }
            },
            "reading_fluency": {
                "criteria": {
                    "accuracy": {"excellent": 95, "good": 90, "needs_improvement": 85},
                    "rate": {"grade_appropriate": True, "above_grade": True, "below_grade": False},
                    "prosody": {"excellent": 4, "good": 3, "needs_improvement": 2}
                }
            }
        }
    
    def get_lesson(self, lesson_id: int) -> Dict[str, Any]:
        """Get complete lesson content by ID"""
        return self.lessons.get(lesson_id, {})
    
    def get_lessons_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all lessons in a specific category"""
        return [lesson for lesson in self.lessons.values() if lesson.get("category") == category]
    
    def get_exercises(self, lesson_category: str) -> List[Dict[str, Any]]:
        """Get exercises for a lesson category"""
        return self.exercises.get(lesson_category, [])
    
    def get_assessment_criteria(self, lesson_category: str) -> Dict[str, Any]:
        """Get assessment criteria for a lesson category"""
        return self.assessments.get(lesson_category, {})
    
    def get_all_lessons_summary(self) -> List[Dict[str, Any]]:
        """Get summary of all available lessons"""
        return [
            {
                "id": lesson["id"],
                "title": lesson["title"],
                "category": lesson["category"],
                "difficulty": lesson["difficulty"],
                "duration": lesson["duration"],
                "description": lesson["description"]
            }
            for lesson in self.lessons.values()
        ]

# Initialize the lesson content manager
lesson_manager = LessonContentManager()