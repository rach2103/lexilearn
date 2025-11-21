"""
Dynamic Exercise Generator for Dyslexic Students
Creates adaptive, personalized exercises based on learning needs and progress
"""

import random
# import json  # Not currently used
from typing import Dict, List, Any, Optional
from datetime import datetime

class ExerciseGenerator:
    """Generates adaptive exercises for different learning areas"""
    
    def __init__(self):
        self.exercise_templates = self._initialize_exercise_templates()
        self.word_lists = self._initialize_word_lists()
        self.difficulty_levels = self._initialize_difficulty_levels()
        
    def _initialize_exercise_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize exercise templates for different skills"""
        return {
            "phonemic_awareness": {
                "sound_identification": {
                    "instructions": "Listen to the word and identify the {position} sound",
                    "positions": ["first", "middle", "last"],
                    "feedback": {
                        "correct": "Great! You identified the sound correctly!",
                        "incorrect": "Not quite. Let's try again. The {position} sound in '{word}' is {correct_sound}."
                    }
                },
                "sound_blending": {
                    "instructions": "Blend these sounds together to make a word: {sounds}",
                    "feedback": {
                        "correct": "Perfect! You blended the sounds to make '{word}'!",
                        "incorrect": "Good try! When we blend {sounds} together, we get '{word}'."
                    }
                },
                "sound_segmentation": {
                    "instructions": "Break this word into individual sounds: {word}",
                    "feedback": {
                        "correct": "Excellent! You correctly broke '{word}' into {sounds}!",
                        "incorrect": "Let's practice. '{word}' breaks into these sounds: {sounds}."
                    }
                }
            },
            "phonics": {
                "letter_sound_matching": {
                    "instructions": "Match each letter with its sound",
                    "feedback": {
                        "correct": "Perfect match! {letter} makes the {sound} sound!",
                        "incorrect": "Remember, {letter} makes the {sound} sound."
                    }
                },
                "word_building": {
                    "instructions": "Use these letters to build the word: {target_word}",
                    "feedback": {
                        "correct": "Fantastic! You built the word '{word}' correctly!",
                        "incorrect": "Good effort! The correct spelling is '{word}'."
                    }
                },
                "decode_words": {
                    "instructions": "Sound out this word: {word}",
                    "feedback": {
                        "correct": "Excellent decoding! You read '{word}' perfectly!",
                        "incorrect": "Let's sound it out together: {phonetic_breakdown}"
                    }
                }
            },
            "sight_words": {
                "flash_cards": {
                    "instructions": "Read this word as quickly as you can",
                    "timing": True,
                    "feedback": {
                        "correct": "Great! You recognized '{word}' instantly!",
                        "incorrect": "This word is '{word}'. Let's practice it again."
                    }
                },
                "sentence_completion": {
                    "instructions": "Choose the correct sight word to complete the sentence",
                    "feedback": {
                        "correct": "Perfect! '{word}' completes the sentence correctly!",
                        "incorrect": "The correct word is '{word}'. Let's read the sentence together."
                    }
                },
                "word_hunt": {
                    "instructions": "Find all the sight words in this passage",
                    "feedback": {
                        "correct": "Excellent! You found {count} sight words!",
                        "partial": "Good job! You found {found} out of {total} sight words."
                    }
                }
            },
            "reading_comprehension": {
                "main_idea": {
                    "instructions": "Read the passage and identify the main idea",
                    "feedback": {
                        "correct": "Excellent! You identified the main idea correctly!",
                        "incorrect": "The main idea is about {main_idea}. Let's discuss why."
                    }
                },
                "detail_questions": {
                    "instructions": "Answer questions about specific details in the text",
                    "feedback": {
                        "correct": "Great attention to detail!",
                        "incorrect": "Let's look back at the text to find the answer."
                    }
                },
                "inference": {
                    "instructions": "What can you infer from this information?",
                    "feedback": {
                        "correct": "Excellent inference! You're thinking like a detective!",
                        "incorrect": "Good thinking! Here's another way to look at it..."
                    }
                }
            },
            "spelling": {
                "pattern_practice": {
                    "instructions": "Complete the word using the correct spelling pattern",
                    "feedback": {
                        "correct": "Perfect! You used the {pattern} pattern correctly!",
                        "incorrect": "Remember the {pattern} pattern. The correct spelling is '{word}'."
                    }
                },
                "rule_application": {
                    "instructions": "Apply the {rule} rule to spell this word",
                    "feedback": {
                        "correct": "Excellent! You applied the {rule} rule perfectly!",
                        "incorrect": "Let's review the {rule} rule and try again."
                    }
                }
            },
            "writing": {
                "sentence_construction": {
                    "instructions": "Write a complete sentence using these words: {words}",
                    "feedback": {
                        "correct": "Great sentence! You used all the words correctly!",
                        "needs_improvement": "Good start! Let's work on making it a complete sentence."
                    }
                },
                "story_sequencing": {
                    "instructions": "Put these story events in the correct order",
                    "feedback": {
                        "correct": "Perfect sequencing! Your story flows logically!",
                        "incorrect": "Good try! Let's think about what happens first, then next..."
                    }
                }
            }
        }
    
    def _initialize_word_lists(self) -> Dict[str, List[str]]:
        """Initialize word lists for different difficulty levels and categories"""
        return {
            "cvc_words": ["cat", "dog", "sun", "big", "red", "hop", "sit", "run", "pen", "cup"],
            "cvce_words": ["cake", "bike", "rope", "cute", "make", "like", "hope", "tube", "game", "time"],
            "sight_words_pre_k": ["I", "a", "the", "to", "and", "go", "you", "it", "in", "said"],
            "sight_words_k": ["he", "for", "are", "as", "with", "his", "they", "at", "be", "this"],
            "sight_words_1st": ["have", "from", "or", "one", "had", "by", "word", "but", "not", "what"],
            "consonant_blends": ["stop", "play", "tree", "frog", "clap", "swim", "drop", "flag", "spin", "glad"],
            "digraph_words": ["ship", "chat", "thin", "when", "fish", "much", "with", "that", "shop", "chip"],
            "long_vowel_words": ["rain", "play", "light", "boat", "blue", "tree", "pie", "coat", "day", "night"],
            "r_controlled": ["car", "bird", "turn", "park", "girl", "corn", "hurt", "star", "work", "farm"],
            "multisyllable": ["happy", "garden", "window", "pencil", "rabbit", "basket", "button", "kitten", "yellow", "purple"]
        }
    
    def _initialize_difficulty_levels(self) -> Dict[str, Dict[str, Any]]:
        """Initialize difficulty level parameters"""
        return {
            "beginner": {
                "word_length": (3, 4),
                "syllables": 1,
                "complexity": "simple",
                "time_limit": 30,
                "hints_available": 3
            },
            "intermediate": {
                "word_length": (4, 6),
                "syllables": (1, 2),
                "complexity": "moderate",
                "time_limit": 20,
                "hints_available": 2
            },
            "advanced": {
                "word_length": (5, 8),
                "syllables": (2, 3),
                "complexity": "complex",
                "time_limit": 15,
                "hints_available": 1
            }
        }
    
    def generate_exercise(self, skill_area: str, exercise_type: str, difficulty: str = "beginner", 
                         user_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Generate a specific exercise based on parameters"""
        try:
            # Input validation
            if not skill_area or not isinstance(skill_area, str):
                return {"error": "Invalid skill_area parameter"}
            
            if not exercise_type or not isinstance(exercise_type, str):
                return {"error": "Invalid exercise_type parameter"}
            
            if not difficulty or not isinstance(difficulty, str):
                difficulty = "beginner"
            
            if skill_area not in self.exercise_templates:
                return {
                    "error": f"Skill area '{skill_area}' not supported",
                    "available_skill_areas": list(self.exercise_templates.keys())
                }
            
            if exercise_type not in self.exercise_templates[skill_area]:
                return {
                    "error": f"Exercise type '{exercise_type}' not found in '{skill_area}'",
                    "available_exercise_types": list(self.exercise_templates[skill_area].keys())
                }
            
            template = self.exercise_templates[skill_area][exercise_type]
            difficulty_params = self.difficulty_levels.get(difficulty, self.difficulty_levels["beginner"])
            
            # Generate exercise based on type
            try:
                if skill_area == "phonemic_awareness":
                    return self._generate_phonemic_exercise(exercise_type, template, difficulty_params, user_context)
                elif skill_area == "phonics":
                    return self._generate_phonics_exercise(exercise_type, template, difficulty_params, user_context)
                elif skill_area == "sight_words":
                    return self._generate_sight_word_exercise(exercise_type, template, difficulty_params, user_context)
                elif skill_area == "reading_comprehension":
                    return self._generate_comprehension_exercise(exercise_type, template, difficulty_params, user_context)
                elif skill_area == "spelling":
                    return self._generate_spelling_exercise(exercise_type, template, difficulty_params, user_context)
                elif skill_area == "writing":
                    return self._generate_writing_exercise(exercise_type, template, difficulty_params, user_context)
                else:
                    return {"error": "Exercise generation failed - unknown skill area"}
            except Exception as e:
                print(f"Error generating {skill_area}/{exercise_type} exercise: {e}")
                return {"error": f"Exercise generation failed: {str(e)}"}
        
        except Exception as e:
            print(f"Error in generate_exercise: {e}")
            return {"error": f"Exercise generation failed: {str(e)}"}
    
    def _generate_phonemic_exercise(self, exercise_type: str, template: Dict[str, Any], 
                                  difficulty: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate phonemic awareness exercises"""
        try:
            if exercise_type == "sound_identification":
                words = random.sample(self.word_lists["cvc_words"], 5)
                position = random.choice(template["positions"])
                
                exercises = []
                for word in words:
                    if position == "first":
                        correct_sound = word[0]
                    elif position == "last":
                        correct_sound = word[-1]
                    else:  # middle
                        correct_sound = word[1] if len(word) > 2 else word[0]
                    
                    exercises.append({
                        "word": word,
                        "position": position,
                        "correct_sound": correct_sound,
                        "options": [correct_sound] + random.sample("bcdfghjklmnpqrstvwxyz", 3)
                    })
                
                return {
                    "exercise_id": f"phonemic_{exercise_type}_{datetime.utcnow().timestamp()}",
                    "skill_area": "phonemic_awareness",
                    "exercise_type": exercise_type,
                    "difficulty": difficulty,
                    "instructions": template["instructions"].format(position=position),
                    "exercises": exercises,
                    "feedback_templates": template["feedback"],
                    "time_limit": difficulty.get("time_limit", 30),
                    "hints_available": difficulty.get("hints_available", 3)
                }
            
            elif exercise_type == "sound_blending":
                words = random.sample(self.word_lists["cvc_words"], 3)
                exercises = []
                
                for word in words:
                    sounds = list(word)
                    exercises.append({
                        "sounds": sounds,
                        "correct_word": word,
                        "sound_display": " - ".join(sounds)
                    })
                
                return {
                    "exercise_id": f"phonemic_{exercise_type}_{datetime.utcnow().timestamp()}",
                    "skill_area": "phonemic_awareness",
                    "exercise_type": exercise_type,
                    "difficulty": difficulty,
                    "instructions": template["instructions"],
                    "exercises": exercises,
                    "feedback_templates": template["feedback"]
                }
            
            elif exercise_type == "sound_segmentation":
                words = random.sample(self.word_lists["cvc_words"], 3)
                exercises = []
                
                for word in words:
                    sounds = list(word)
                    exercises.append({
                        "word": word,
                        "correct_sounds": sounds,
                        "sound_count": len(sounds)
                    })
                
                return {
                    "exercise_id": f"phonemic_{exercise_type}_{datetime.utcnow().timestamp()}",
                    "skill_area": "phonemic_awareness",
                    "exercise_type": exercise_type,
                    "difficulty": difficulty,
                    "instructions": template["instructions"],
                    "exercises": exercises,
                    "feedback_templates": template["feedback"]
                }
            
            return {"error": f"Unknown exercise type: {exercise_type}"}
        except Exception as e:
            print(f"Error generating phonemic exercise: {e}")
            return {"error": f"Failed to generate phonemic exercise: {str(e)}"}
    
    def _generate_sight_word_exercise(self, exercise_type: str, template: Dict[str, Any], 
                                    difficulty: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate sight word exercises"""
        try:
            # Select appropriate word list based on difficulty
            if difficulty.get("complexity") == "simple":
                word_list = self.word_lists["sight_words_pre_k"]
            elif difficulty.get("complexity") == "moderate":
                word_list = self.word_lists["sight_words_k"]
            else:
                word_list = self.word_lists["sight_words_1st"]
            
            if exercise_type == "flash_cards":
                words = random.sample(word_list, min(10, len(word_list)))
                
                return {
                    "exercise_id": f"sight_words_{exercise_type}_{datetime.utcnow().timestamp()}",
                    "skill_area": "sight_words",
                    "exercise_type": exercise_type,
                    "difficulty": difficulty,
                    "instructions": template["instructions"],
                    "words": words,
                    "timing": template.get("timing", False),
                    "time_per_word": 3,
                    "feedback_templates": template["feedback"]
                }
            
            elif exercise_type == "sentence_completion":
                sentences = [
                    ("I ___ a red ball.", ["see", "saw", "say"], "see"),
                    ("The dog can ___.", ["run", "ran", "running"], "run"),
                    ("___ is my friend.", ["He", "His", "Him"], "He"),
                    ("We ___ to school.", ["go", "goes", "going"], "go"),
                    ("___ cat is black.", ["The", "A", "An"], "The")
                ]
                
                selected_sentences = random.sample(sentences, min(3, len(sentences)))
                exercises = []
                
                for sentence, options, correct in selected_sentences:
                    exercises.append({
                        "sentence": sentence,
                        "options": options,
                        "correct_answer": correct
                    })
                
                return {
                    "exercise_id": f"sight_words_{exercise_type}_{datetime.utcnow().timestamp()}",
                    "skill_area": "sight_words",
                    "exercise_type": exercise_type,
                    "difficulty": difficulty,
                    "instructions": template["instructions"],
                    "exercises": exercises,
                    "feedback_templates": template["feedback"]
                }
            
            return {"error": f"Unknown exercise type: {exercise_type}"}
        except Exception as e:
            print(f"Error generating sight word exercise: {e}")
            return {"error": f"Failed to generate sight word exercise: {str(e)}"}
    
    def _generate_comprehension_exercise(self, exercise_type: str, template: Dict[str, Any], 
                                       difficulty: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate reading comprehension exercises"""
        
        # Sample passages for different difficulty levels
        passages = {
            "simple": {
                "text": "The cat sat on the mat. The cat was big and black. The mat was red. The cat liked the mat.",
                "main_idea": "A cat sitting on a mat",
                "details": ["The cat was big and black", "The mat was red", "The cat liked the mat"],
                "questions": [
                    {"question": "What color was the cat?", "answer": "black", "type": "detail"},
                    {"question": "Where did the cat sit?", "answer": "on the mat", "type": "detail"},
                    {"question": "What is this story mainly about?", "answer": "a cat on a mat", "type": "main_idea"}
                ]
            },
            "moderate": {
                "text": "Sam went to the park with his dog, Max. They played fetch with a red ball. Max ran fast to catch the ball. Sam threw the ball high in the air. They had fun together at the park.",
                "main_idea": "Sam and his dog playing at the park",
                "details": ["Sam's dog is named Max", "They played with a red ball", "Max ran fast", "Sam threw the ball high"],
                "questions": [
                    {"question": "What is the dog's name?", "answer": "Max", "type": "detail"},
                    {"question": "What game did they play?", "answer": "fetch", "type": "detail"},
                    {"question": "How do you think Sam felt at the park?", "answer": "happy/fun", "type": "inference"}
                ]
            }
        }
        
        complexity = difficulty.get("complexity", "simple")
        passage_data = passages.get(complexity, passages["simple"])
        
        if exercise_type == "main_idea":
            return {
                "exercise_id": f"comprehension_{exercise_type}_{datetime.utcnow().timestamp()}",
                "skill_area": "reading_comprehension",
                "exercise_type": exercise_type,
                "difficulty": difficulty,
                "instructions": template["instructions"],
                "passage": passage_data["text"],
                "correct_main_idea": passage_data["main_idea"],
                "options": [passage_data["main_idea"]] + ["The weather was nice", "Animals are fun", "Playing games"],
                "feedback_templates": template["feedback"]
            }
        
        elif exercise_type == "detail_questions":
            detail_questions = [q for q in passage_data["questions"] if q["type"] == "detail"]
            
            return {
                "exercise_id": f"comprehension_{exercise_type}_{datetime.utcnow().timestamp()}",
                "skill_area": "reading_comprehension",
                "exercise_type": exercise_type,
                "difficulty": difficulty,
                "instructions": template["instructions"],
                "passage": passage_data["text"],
                "questions": detail_questions,
                "feedback_templates": template["feedback"]
            }
    
    def _generate_spelling_exercise(self, exercise_type: str, template: Dict[str, Any], 
                                  difficulty: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate spelling exercises"""
        
        if exercise_type == "pattern_practice":
            patterns = {
                "CVC": {"words": self.word_lists["cvc_words"], "pattern": "consonant-vowel-consonant"},
                "CVCe": {"words": self.word_lists["cvce_words"], "pattern": "consonant-vowel-consonant-e"}
            }
            
            pattern_name = random.choice(list(patterns.keys()))
            pattern_data = patterns[pattern_name]
            words = random.sample(pattern_data["words"], 5)
            
            exercises = []
            for word in words:
                # Create word with missing letters
                missing_pos = random.randint(1, len(word) - 2)
                incomplete_word = word[:missing_pos] + "_" + word[missing_pos + 1:]
                
                exercises.append({
                    "incomplete_word": incomplete_word,
                    "correct_word": word,
                    "missing_letter": word[missing_pos],
                    "pattern": pattern_data["pattern"]
                })
            
            return {
                "exercise_id": f"spelling_{exercise_type}_{datetime.utcnow().timestamp()}",
                "skill_area": "spelling",
                "exercise_type": exercise_type,
                "difficulty": difficulty,
                "instructions": template["instructions"],
                "pattern": pattern_data["pattern"],
                "exercises": exercises,
                "feedback_templates": template["feedback"]
            }
    
    def _generate_writing_exercise(self, exercise_type: str, template: Dict[str, Any], 
                                 difficulty: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate writing exercises"""
        
        if exercise_type == "sentence_construction":
            word_sets = [
                ["cat", "big", "the"],
                ["dog", "runs", "fast"],
                ["I", "like", "books"],
                ["sun", "is", "bright"],
                ["we", "play", "games"],
                ["bird", "can", "fly"],
                ["fish", "swim", "water"],
                ["tree", "is", "tall"],
                ["moon", "shines", "night"],
                ["flowers", "are", "pretty"],
                ["rain", "falls", "down"],
                ["wind", "blows", "hard"],
                ["snow", "is", "white"],
                ["stars", "twinkle", "sky"],
                ["car", "goes", "fast"]
            ]
            
            # Shuffle to ensure variety
            random.shuffle(word_sets)
            selected_words = word_sets[0]
            
            return {
                "exercise_id": f"writing_{exercise_type}_{datetime.utcnow().timestamp()}",
                "skill_area": "writing",
                "exercise_type": exercise_type,
                "difficulty": difficulty,
                "instructions": template["instructions"].format(words=", ".join(selected_words)),
                "word_bank": selected_words,
                "requirements": ["Use all words", "Make a complete sentence", "Start with capital letter", "End with period"],
                "feedback_templates": template["feedback"]
            }
    
    def generate_adaptive_exercise_set(self, user_progress: Dict[str, Any], 
                                     target_skills: List[str] = None) -> List[Dict[str, Any]]:
        """Generate a set of exercises adapted to user's progress and needs"""
        
        exercises = []
        
        # Determine user's current level
        accuracy = user_progress.get("average_accuracy", 0)
        if accuracy >= 85:
            difficulty = "advanced"
        elif accuracy >= 70:
            difficulty = "intermediate"
        else:
            difficulty = "beginner"
        
        # Identify areas needing work
        weak_areas = user_progress.get("areas_for_improvement", [])
        strong_areas = user_progress.get("strengths", [])
        
        # Generate exercises for weak areas (70% of exercises)
        if weak_areas:
            for area in weak_areas[:2]:  # Focus on top 2 weak areas
                if area in self.exercise_templates:
                    exercise_types = list(self.exercise_templates[area].keys())
                    for exercise_type in exercise_types[:2]:  # 2 exercises per area
                        exercise = self.generate_exercise(area, exercise_type, difficulty, user_progress)
                        if "error" not in exercise:
                            exercises.append(exercise)
        
        # Generate exercises for maintenance of strong areas (30% of exercises)
        if strong_areas and len(exercises) < 6:
            for area in strong_areas[:1]:  # 1 strong area
                if area in self.exercise_templates:
                    exercise_types = list(self.exercise_templates[area].keys())
                    exercise_type = random.choice(exercise_types)
                    exercise = self.generate_exercise(area, exercise_type, difficulty, user_progress)
                    if "error" not in exercise:
                        exercises.append(exercise)
        
        # Fill remaining slots with general exercises
        while len(exercises) < 5:
            skill_area = random.choice(list(self.exercise_templates.keys()))
            exercise_type = random.choice(list(self.exercise_templates[skill_area].keys()))
            exercise = self.generate_exercise(skill_area, exercise_type, difficulty, user_progress)
            if "error" not in exercise:
                exercises.append(exercise)
        
        return exercises[:5]  # Return maximum 5 exercises
    
    def _generate_phonics_exercise(self, exercise_type: str, template: Dict[str, Any], 
                                 difficulty: Dict[str, Any], user_context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate phonics exercises"""
        
        if exercise_type == "letter_sound_matching":
            letters = ['b', 'c', 'd', 'f', 'g', 'h', 'j', 'k', 'l', 'm']
            sounds = ['buh', 'kuh', 'duh', 'fuh', 'guh', 'huh', 'juh', 'kuh', 'luh', 'muh']
            
            exercises = []
            selected_letters = random.sample(letters, 5)
            
            for letter in selected_letters:
                correct_sound = sounds[letters.index(letter)]
                options = [correct_sound] + random.sample([s for s in sounds if s != correct_sound], 3)
                random.shuffle(options)
                
                exercises.append({
                    "letter": letter,
                    "correct_sound": correct_sound,
                    "options": options
                })
            
            return {
                "exercise_id": f"phonics_{exercise_type}_{datetime.utcnow().timestamp()}",
                "skill_area": "phonics",
                "exercise_type": exercise_type,
                "difficulty": difficulty,
                "instructions": template["instructions"],
                "exercises": exercises,
                "feedback_templates": template["feedback"]
            }
        
        elif exercise_type == "word_building":
            target_words = random.sample(self.word_lists["cvc_words"], 3)
            exercises = []
            
            for word in target_words:
                letters = list(word)
                scrambled = letters.copy()
                random.shuffle(scrambled)
                
                exercises.append({
                    "target_word": word,
                    "available_letters": scrambled,
                    "word_length": len(word)
                })
            
            return {
                "exercise_id": f"phonics_{exercise_type}_{datetime.utcnow().timestamp()}",
                "skill_area": "phonics",
                "exercise_type": exercise_type,
                "difficulty": difficulty,
                "instructions": template["instructions"],
                "exercises": exercises,
                "feedback_templates": template["feedback"]
            }
        
        elif exercise_type == "decode_words":
            words = random.sample(self.word_lists["cvc_words"], 5)
            exercises = []
            
            for word in words:
                phonetic_breakdown = "-".join(list(word))
                exercises.append({
                    "word": word,
                    "phonetic_breakdown": phonetic_breakdown,
                    "syllables": 1
                })
            
            return {
                "exercise_id": f"phonics_{exercise_type}_{datetime.utcnow().timestamp()}",
                "skill_area": "phonics",
                "exercise_type": exercise_type,
                "difficulty": difficulty,
                "instructions": template["instructions"],
                "exercises": exercises,
                "feedback_templates": template["feedback"]
            }
    
    def evaluate_exercise_response(self, exercise: Dict[str, Any], user_response: Any) -> Dict[str, Any]:
        """Evaluate user's response to an exercise"""
        try:
            # Input validation
            if not exercise or not isinstance(exercise, dict):
                return {
                    "correct": False,
                    "score": 0,
                    "feedback": "Invalid exercise data",
                    "hints": [],
                    "next_steps": ["Please try again with a valid exercise"]
                }
            
            if user_response is None:
                user_response = ""
            
            skill_area = exercise.get("skill_area")
            exercise_type = exercise.get("exercise_type")
            
            # Default evaluation
            evaluation = {
                "correct": False,
                "score": 0,
                "feedback": "",
                "hints": [],
                "next_steps": []
            }
            
            if not skill_area or not exercise_type:
                evaluation["feedback"] = "Missing exercise information"
                return evaluation
            
            # Evaluation logic based on exercise type
            try:
                if skill_area == "sight_words" and exercise_type == "flash_cards":
                    correct_word = exercise.get("current_word", "")
                    if correct_word and str(user_response).lower().strip() == correct_word.lower():
                        evaluation["correct"] = True
                        evaluation["score"] = 100
                        evaluation["feedback"] = f"Perfect! You recognized '{correct_word}' correctly!"
                    else:
                        evaluation["feedback"] = f"This word is '{correct_word}'. Let's practice it again."
                        if correct_word and len(correct_word) > 0:
                            evaluation["hints"] = [f"This word starts with '{correct_word[0]}'", f"This word has {len(correct_word)} letters"]
                
                elif skill_area == "phonemic_awareness" and exercise_type == "sound_identification":
                    correct_sound = exercise.get("correct_sound", "")
                    if correct_sound and str(user_response).lower() == correct_sound.lower():
                        evaluation["correct"] = True
                        evaluation["score"] = 100
                        evaluation["feedback"] = "Great! You identified the sound correctly!"
                    else:
                        evaluation["feedback"] = f"The correct sound is '{correct_sound}'. Let's try another one!"
                
                elif skill_area == "phonics" and exercise_type == "word_building":
                    # Handle phonics word building evaluation
                    target_word = exercise.get("target_word", "")
                    user_answer = str(user_response).lower().strip()
                    if target_word and user_answer == target_word.lower():
                        evaluation["correct"] = True
                        evaluation["score"] = 100
                        evaluation["feedback"] = f"Excellent! You built '{target_word}' correctly!"
                    elif target_word:
                        evaluation["feedback"] = f"Close! The correct word is '{target_word}'. You wrote '{user_answer}'."
                        evaluation["hints"] = [f"Try saying each letter sound", f"The word is '{target_word}'"]
                
                else:
                    # Generic evaluation for unhandled types
                    evaluation["feedback"] = "Exercise evaluated successfully"
                
            except Exception as e:
                print(f"Error in specific evaluation: {e}")
                evaluation["feedback"] = f"Error evaluating response: {str(e)}"
            
            # Add general encouragement
            if evaluation.get("correct"):
                evaluation["next_steps"] = ["Try a more challenging exercise", "Practice similar words", "Move to the next skill"]
            elif not evaluation.get("next_steps"):
                evaluation["next_steps"] = ["Review the concept", "Try with easier words", "Use multi-sensory techniques"]
            
            return evaluation
        
        except Exception as e:
            print(f"Error in evaluate_exercise_response: {e}")
            return {
                "correct": False,
                "score": 0,
                "feedback": f"Evaluation failed: {str(e)}",
                "hints": [],
                "next_steps": ["Please try again"]
            }

# Initialize the exercise generator
exercise_generator = ExerciseGenerator()