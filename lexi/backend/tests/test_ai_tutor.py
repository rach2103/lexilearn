"""
Tests for AI Tutor functionality
"""
import pytest
from ml_models.ai_tutor import ai_tutor

class TestAITutor:
    """AI Tutor tests"""
    
    def test_analyze_user_input(self):
        """Test analyzing user input"""
        analysis = ai_tutor.analyze_user_input(
            "I need help with reading",
            {"user_id": "test_user"}
        )
        assert "intent" in analysis
        assert "emotion" in analysis
        assert "learning_need" in analysis
    
    def test_conversation_context(self):
        """Test conversation context tracking"""
        user_id = "test_user_2"
        
        # First message
        ai_tutor.update_conversation_context(user_id, "phonics", "I want to practice phonics")
        context = ai_tutor.get_conversation_context(user_id)
        assert context["turns"] == 1
        assert context["last_topic"] == "phonics"
        
        # Second message
        ai_tutor.update_conversation_context(user_id, "spelling", "Let's do spelling now")
        context = ai_tutor.get_conversation_context(user_id)
        assert context["turns"] == 2
        assert context["last_topic"] == "spelling"
    
    def test_conversation_memory(self):
        """Test conversation memory"""
        user_id = "test_user_3"
        
        ai_tutor.add_conversation_memory(user_id, "Hello", "Hi there!")
        recent = ai_tutor.get_recent_conversation(user_id)
        
        assert len(recent) > 0
        assert "Hello" in recent[0]
        assert "Hi there!" in recent[0]
    
    def test_natural_followup(self):
        """Test natural followup generation"""
        user_context = {"user_id": "test_user_4"}
        analysis = {"learning_need": "phonics"}
        
        followup = ai_tutor.generate_natural_followup(user_context, analysis)
        assert followup is not None
        assert len(followup) > 0

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

