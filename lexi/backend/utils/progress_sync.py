"""
Centralized progress synchronization service
Ensures all pages (Dashboard, Progress, Lessons) stay in sync
"""
from typing import Dict, Any, List
from datetime import datetime
import json
from utils.logger import main_logger

class ProgressSyncService:
    """Service to synchronize progress across all pages"""
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 60  # Cache for 60 seconds
        self.last_updated = {}
    
    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Get synchronized user stats"""
        import time
        from database.database import db_manager
        
        # Check cache
        cache_key = f"stats_{user_id}"
        if cache_key in self.cache:
            last_update = self.last_updated.get(cache_key, 0)
            if time.time() - last_update < self.cache_ttl:
                main_logger.debug(f"Returning cached stats for user {user_id}")
                return self.cache[cache_key]
        
        # Fetch from database
        try:
            stats = self._calculate_user_stats(user_id, db_manager)
            
            # Cache the result
            self.cache[cache_key] = stats
            self.last_updated[cache_key] = time.time()
            
            return stats
        except Exception as e:
            main_logger.error(f"Error fetching stats for user {user_id}: {e}")
            return self._get_default_stats()
    
    def _calculate_user_stats(self, user_id: str, db_manager) -> Dict[str, Any]:
        """Calculate comprehensive user statistics"""
        from ml_models.ai_tutor import ai_tutor
        
        # Get AI tutor progress
        ai_progress = ai_tutor.user_progress.get(user_id, {})
        sessions = ai_progress.get("sessions", [])
        
        # Calculate statistics
        total_exercises = len(sessions)
        correct_count = sum(1 for s in sessions if s.get("data", {}).get("correct", False))
        accuracy = (correct_count / total_exercises * 100) if total_exercises > 0 else 0
        
        # Get chat history count
        chat_history = ai_tutor.get_history(user_id, 1000)
        total_messages = len(chat_history)
        
        # Calculate study time
        total_study_time = sum(s.get("data", {}).get("session_duration", 0) for s in sessions) // 60
        
        # Get database progress if available
        try:
            if hasattr(db_manager, 'get_user_progress'):
                db_progress = db_manager.get_user_progress(int(user_id)) if user_id.isdigit() else {}
            else:
                db_progress = {}
        except:
            db_progress = {}
        
        # Calculate skill-specific progress
        skill_progress = self._calculate_skill_progress(sessions, ai_progress)
        
        # Combine all statistics
        stats = {
            "exercises_completed": total_exercises,
            "accuracy": round(accuracy, 1),
            "total_messages": total_messages,
            "study_time_minutes": total_study_time,
            "skill_progress": skill_progress,
            "recent_activity": sessions[-5:] if sessions else [],
            "last_updated": datetime.utcnow().isoformat()
        }
        
        return stats
    
    def _calculate_skill_progress(self, sessions: List[Dict], ai_progress: Dict) -> Dict[str, float]:
        """Calculate skill-specific progress"""
        skill_progress = {
            "reading": 0,
            "writing": 0,
            "spelling": 0,
            "comprehension": 0
        }
        
        skill_counts = {
            "reading": {"correct": 0, "total": 0},
            "writing": {"correct": 0, "total": 0},
            "spelling": {"correct": 0, "total": 0},
            "comprehension": {"correct": 0, "total": 0}
        }
        
        # Map skill areas to categories
        skill_mapping = {
            "phonics": "reading",
            "sight_words": "reading",
            "phonemic_awareness": "reading",
            "writing": "writing",
            "spelling": "spelling",
            "reading_comprehension": "comprehension"
        }
        
        for session in sessions:
            data = session.get("data", {})
            skill_area = data.get("skill_area", "")
            is_correct = data.get("correct", False)
            
            # Map to category
            category = skill_mapping.get(skill_area)
            if category:
                skill_counts[category]["total"] += 1
                if is_correct:
                    skill_counts[category]["correct"] += 1
        
        # Calculate percentages
        for skill, counts in skill_counts.items():
            if counts["total"] > 0:
                skill_progress[skill] = round((counts["correct"] / counts["total"]) * 100, 1)
        
        return skill_progress
    
    def _get_default_stats(self) -> Dict[str, Any]:
        """Return default stats"""
        return {
            "exercises_completed": 0,
            "accuracy": 0,
            "total_messages": 0,
            "study_time_minutes": 0,
            "skill_progress": {
                "reading": 0,
                "writing": 0,
                "spelling": 0,
                "comprehension": 0
            },
            "recent_activity": [],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def invalidate_cache(self, user_id: str = None):
        """Invalidate cache for user or all users"""
        if user_id:
            cache_key = f"stats_{user_id}"
            if cache_key in self.cache:
                del self.cache[cache_key]
            if cache_key in self.last_updated:
                del self.last_updated[cache_key]
            main_logger.info(f"Cache invalidated for user {user_id}")
        else:
            self.cache.clear()
            self.last_updated.clear()
            main_logger.info("All cache invalidated")
    
    def update_progress(self, user_id: str, progress_data: Dict[str, Any]):
        """Update progress and invalidate cache"""
        from ml_models.ai_tutor import ai_tutor
        
        # Update AI tutor context
        ai_tutor.update_user_context(user_id, progress_data)
        
        # Invalidate cache
        self.invalidate_cache(user_id)
        
        main_logger.info(f"Progress updated for user {user_id}")


# Create singleton instance
progress_sync_service = ProgressSyncService()

