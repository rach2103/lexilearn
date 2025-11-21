"""
Tests for Exercise Generator functionality
"""
import pytest
from ml_models.exercise_generator import exercise_generator

class TestExerciseGenerator:
    """Exercise Generator tests"""
    
    def test_generate_phonics_exercise(self):
        """Test generating phonics exercise"""
        exercise = exercise_generator.generate_exercise(
            skill_area="phonics",
            exercise_type="word_building",
            difficulty="beginner"
        )
        assert "skill_area" in exercise
        assert exercise["skill_area"] == "phonics"
        assert "instructions" in exercise
    
    def test_generate_sight_words_exercise(self):
        """Test generating sight words exercise"""
        exercise = exercise_generator.generate_exercise(
            skill_area="sight_words",
            exercise_type="flash_cards",
            difficulty="beginner"
        )
        assert exercise["skill_area"] == "sight_words"
        assert "words" in exercise or "exercises" in exercise
    
    def test_generate_adaptive_exercises(self):
        """Test generating adaptive exercise set"""
        user_progress = {
            "average_accuracy": 75,
            "areas_for_improvement": ["phonics", "spelling"],
            "strengths": ["sight_words"]
        }
        
        exercises = exercise_generator.generate_adaptive_exercise_set(user_progress)
        assert isinstance(exercises, list)
        assert len(exercises) > 0
    
    def test_exercise_evaluation(self):
        """Test exercise evaluation"""
        exercise = {
            "skill_area": "spelling",
            "exercise_type": "pattern_practice",
            "correct_word": "cat"
        }
        
        evaluation = exercise_generator.evaluate_exercise_response(
            exercise, 
            "cat"
        )
        assert "correct" in evaluation
        assert "score" in evaluation
    
    def test_difficulty_levels(self):
        """Test different difficulty levels"""
        for difficulty in ["beginner", "intermediate", "advanced"]:
            exercise = exercise_generator.generate_exercise(
                skill_area="phonics",
                exercise_type="word_building",
                difficulty=difficulty
            )
            assert "skill_area" in exercise
    
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        with pytest.raises(Exception) or exercise_generator.generate_exercise(
            skill_area="invalid",
            exercise_type="invalid",
            difficulty="invalid"
        ):
            # Should handle gracefully or raise informative error
            pass

class TestExerciseTypes:
    """Test different exercise types"""
    
    def test_word_building(self):
        """Test word building exercise"""
        exercise = exercise_generator.generate_exercise(
            "phonics", "word_building", "beginner"
        )
        assert exercise["exercise_type"] == "word_building"
    
    def test_sentence_completion(self):
        """Test sentence completion exercise"""
        exercise = exercise_generator.generate_exercise(
            "sight_words", "sentence_completion", "beginner"
        )
        assert "exercises" in exercise or "words" in exercise
    
    def test_flash_cards(self):
        """Test flash cards exercise"""
        exercise = exercise_generator.generate_exercise(
            "sight_words", "flash_cards", "beginner"
        )
        assert "words" in exercise or "exercises" in exercise

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

