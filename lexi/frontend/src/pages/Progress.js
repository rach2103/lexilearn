import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import useTimeTracking from '../useTimeTracking';
import { 
  FiTrendingUp, 
  FiCalendar, 
  FiClock, 
  FiTarget,
  FiBarChart2,
  FiAward,
  FiBookOpen
  ,FiRefreshCw
} from 'react-icons/fi';

const Progress = () => {
  const { user } = useAuth();
  const { getTotalTime } = useTimeTracking();
  const [showImprovementModal, setShowImprovementModal] = useState(false);
  const [newImprovementText, setNewImprovementText] = useState('');
  const [improvementItems, setImprovementItems] = useState([]);
  const [progressData, setProgressData] = useState({
    weeklyProgress: [],
    skillProgress: [],
    achievements: [],
    summary: {
      totalLessons: 0,
      averageAccuracy: 0,
      studyTimeMins: 0,
      currentStreak: 0
    }
  });

  const pollingRef = useRef(null);

  // Load improvement items from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('improvementItems');
    if (saved) {
      setImprovementItems(JSON.parse(saved));
    }
  }, []);

  // Save improvement items to localStorage
  const saveImprovementItems = (items) => {
    localStorage.setItem('improvementItems', JSON.stringify(items));
    setImprovementItems(items);
  };

  const addImprovementItem = () => {
    if (!newImprovementText.trim()) return;
    
    const newItem = {
      id: Date.now(),
      text: newImprovementText.trim(),
      completed: false,
      createdAt: new Date().toISOString()
    };
    
    const updatedItems = [...improvementItems, newItem];
    saveImprovementItems(updatedItems);
    setNewImprovementText('');
    setShowImprovementModal(false);
  };

  const toggleImprovementItem = (id) => {
    const updatedItems = improvementItems.map(item =>
      item.id === id ? { ...item, completed: !item.completed } : item
    );
    saveImprovementItems(updatedItems);
  };

  const removeImprovementItem = (id) => {
    const updatedItems = improvementItems.filter(item => item.id !== id);
    saveImprovementItems(updatedItems);
  };

  const getColorClasses = (color) => {
    const colors = {
      primary: 'bg-primary-600',
      success: 'bg-success-600',
      warning: 'bg-warning-600',
      secondary: 'bg-secondary-600'
    };
    return colors[color] || colors.primary;
  };

  const formatTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const fetchProgress = async () => {
    try {
      // Fetch user stats (works for anonymous users too)
      const statsResp = await axios.get('/api/user/stats');
      const statsData = statsResp.data || {};
      
      // Try to fetch detailed progress if user is logged in
      let data = {};
      if (user && user.id) {
        try {
          const resp = await axios.get(`/api/progress/${user.id}`);
          data = resp.data || {};
        } catch (err) {
          console.log('Detailed progress not available, using stats only');
        }
      }

      // Map backend response to UI model (with safe fallbacks)
      const weekly = (data.recent_sessions || []).slice().reverse().map((s, idx) => ({
        day: s.date ? new Date(s.date).toLocaleDateString(undefined, { weekday: 'short' }) : `Day ${idx+1}`,
        lessons: s.lessons_completed || 1,
        accuracy: Math.round((s.accuracy || 0)),
        time: Math.round((s.session_duration || 0) / 60)
      }));

      const skills = (data.strengths || []).map((skill) => ({ skill, current: 50, target: 100, color: 'primary' }));

      const achievements = (data.achievements || []).map((a, idx) => ({
        id: a.id || idx,
        title: a.title || a.name || 'Achievement',
        description: a.description || '',
        date: a.date || new Date().toISOString(),
        icon: FiAward
      }));

      // Get lesson clicks from localStorage
      const lessonClicks = parseInt(localStorage.getItem('lessonClicks') || '0', 10);
      
      // Get time from time tracking hook (in seconds, convert to minutes)
      const totalTimeSeconds = getTotalTime();
      const totalTimeMinutes = Math.floor(totalTimeSeconds / 60);

      setProgressData({
        weeklyProgress: weekly.length ? weekly : progressData.weeklyProgress,
        skillProgress: skills.length ? skills : progressData.skillProgress,
        achievements: achievements.length ? achievements : progressData.achievements,
        summary: {
          totalLessons: lessonClicks,
          averageAccuracy: Math.round(statsData.accuracy || data.overall_accuracy || 0),
          studyTimeMins: totalTimeMinutes,
          currentStreak: data.current_streak || 0
        }
      });
    } catch (error) {
      console.error('Failed to load progress:', error);
    }
  };

  // Fetch on mount and set up polling so progress updates while user uses app
  useEffect(() => {
    fetchProgress();
    // poll every 10 seconds
    pollingRef.current = setInterval(fetchProgress, 10000);
    return () => clearInterval(pollingRef.current);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user && user.id]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8 flex items-start justify-between">
          <div>
            <h1 className="text-dyslexic-2xl font-bold text-gray-900 mb-2">
              Your Learning Progress
            </h1>
            <p className="text-dyslexic-base text-gray-600">
              Track your improvement and celebrate your achievements
            </p>
          </div>
          <div className="flex items-center space-x-2">
            <button
              onClick={fetchProgress}
              className="p-2 bg-white border rounded shadow-sm hover:bg-gray-50"
              aria-label="Refresh progress"
            >
              <FiRefreshCw />
            </button>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-primary-100 rounded-lg">
                <FiBookOpen className="text-primary-600" size={24} />
              </div>
              <div className="ml-4">
                <p className="text-dyslexic-sm text-gray-600">Total Lessons</p>
                <p className="text-dyslexic-xl font-bold text-gray-900">{progressData.summary.totalLessons}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-success-100 rounded-lg">
                <FiTarget className="text-success-600" size={24} />
              </div>
              <div className="ml-4">
                <p className="text-dyslexic-sm text-gray-600">Average Accuracy</p>
                <p className="text-dyslexic-xl font-bold text-gray-900">{Math.round(progressData.summary.averageAccuracy)}%</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-warning-100 rounded-lg">
                <FiClock className="text-warning-600" size={24} />
              </div>
              <div className="ml-4">
                <p className="text-dyslexic-sm text-gray-600">Study Time</p>
                <p className="text-dyslexic-xl font-bold text-gray-900">{formatTime(progressData.summary.studyTimeMins)}</p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-secondary-100 rounded-lg">
                <FiTrendingUp className="text-secondary-600" size={24} />
              </div>
              <div className="ml-4">
                <p className="text-dyslexic-sm text-gray-600">Current Streak</p>
                <p className="text-dyslexic-xl font-bold text-gray-900">{progressData.summary.currentStreak} days</p>
              </div>
            </div>
          </div>
        </div>

        {/* Weekly Progress Chart */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 mb-8">
          <h2 className="text-dyslexic-xl font-bold text-gray-900 mb-6">
            Weekly Progress
          </h2>
          <div className="grid grid-cols-7 gap-4">
            {progressData.weeklyProgress.map((day, index) => (
              <div key={index} className="text-center">
                <div className="text-dyslexic-sm text-gray-600 mb-2">{day.day}</div>
                <div className="space-y-2">
                  <div className="bg-gray-200 rounded-lg p-2">
                    <div className="text-dyslexic-sm font-semibold text-gray-900">
                      {day.lessons}
                    </div>
                    <div className="text-xs text-gray-500">Lessons</div>
                  </div>
                  <div className="bg-gray-200 rounded-lg p-2">
                    <div className="text-dyslexic-sm font-semibold text-gray-900">
                      {day.accuracy}%
                    </div>
                    <div className="text-xs text-gray-500">Accuracy</div>
                  </div>
                  <div className="bg-gray-200 rounded-lg p-2">
                    <div className="text-dyslexic-sm font-semibold text-gray-900">
                      {formatTime(day.time)}
                    </div>
                    <div className="text-xs text-gray-500">Time</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Skill Progress and Achievements */}
        <div className="grid grid-cols-1 lg:grid-cols-1 gap-8">
          {/* Things to Improve */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-dyslexic-xl font-bold text-gray-900">
                Things to Improve
              </h2>
              <button
                onClick={() => setShowImprovementModal(true)}
                className="bg-primary-600 text-white px-4 py-2 rounded-lg hover:bg-primary-700 transition-colors"
              >
                Add Item
              </button>
            </div>
            <div className="space-y-3">
              {improvementItems.map((item) => (
                <div key={item.id} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <input
                    type="checkbox"
                    checked={item.completed}
                    onChange={() => toggleImprovementItem(item.id)}
                    className="h-5 w-5 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className={`flex-1 text-dyslexic-base ${
                    item.completed ? 'line-through text-gray-500' : 'text-gray-900'
                  }`}>
                    {item.text}
                  </span>
                  <button
                    onClick={() => removeImprovementItem(item.id)}
                    className="text-red-500 hover:text-red-700"
                  >
                    ×
                  </button>
                </div>
              ))}
              {improvementItems.length === 0 && (
                <p className="text-gray-500 text-center py-8">
                  No improvement items yet. Click "Add Item" to get started!
                </p>
              )}
            </div>
          </div>
        </div>

        {/* Improvement Modal */}
        {showImprovementModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center" onClick={() => setShowImprovementModal(false)}>
            <div className="bg-white rounded-lg shadow-xl max-w-md w-full mx-4" onClick={(e) => e.stopPropagation()}>
              <div className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Add Something to Improve
                </h3>
                <textarea
                  value={newImprovementText}
                  onChange={(e) => setNewImprovementText(e.target.value)}
                  placeholder="What would you like to work on?"
                  className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                  rows={3}
                />
                <div className="flex justify-end space-x-3 mt-4">
                  <button
                    onClick={() => setShowImprovementModal(false)}
                    className="px-4 py-2 text-gray-600 hover:text-gray-800"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={addImprovementItem}
                    disabled={!newImprovementText.trim()}
                    className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Detailed Analytics */}
        <div className="mt-8 bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <h2 className="text-dyslexic-xl font-bold text-gray-900 mb-6">
            Detailed Analytics
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
                              <FiBarChart2 className="mx-auto text-blue-600 mb-2" size={24} />
              <h3 className="text-dyslexic-lg font-semibold text-blue-900 mb-2">
                Reading Speed
              </h3>
              <p className="text-dyslexic-base text-blue-700">
                120 WPM
              </p>
              <p className="text-dyslexic-sm text-blue-600">
                +15% improvement
              </p>
            </div>

            <div className="text-center p-4 bg-green-50 rounded-lg">
              <FiTarget className="mx-auto text-green-600 mb-2" size={24} />
              <h3 className="text-dyslexic-lg font-semibold text-green-900 mb-2">
                Error Reduction
              </h3>
              <p className="text-dyslexic-base text-green-700">
                40% decrease
              </p>
              <p className="text-dyslexic-sm text-green-600">
                Last 30 days
              </p>
            </div>

            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <FiCalendar className="mx-auto text-purple-600 mb-2" size={24} />
              <h3 className="text-dyslexic-lg font-semibold text-purple-900 mb-2">
                Consistency
              </h3>
              <p className="text-dyslexic-base text-purple-700">
                85% attendance
              </p>
              <p className="text-dyslexic-sm text-purple-600">
                Weekly average
              </p>
            </div>
          </div>
        </div>

        {/* Recommendations */}
        <div className="mt-8 bg-gradient-to-r from-primary-500 to-secondary-500 rounded-xl p-8 text-center">
          <h2 className="text-dyslexic-xl font-bold text-white mb-4">
            Keep Up the Great Work!
          </h2>
          <p className="text-dyslexic-base text-primary-100 mb-6">
            You're making excellent progress. Consider focusing on spelling exercises 
            to reach your target of 80% accuracy.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button className="bg-white text-primary-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-50 transition-colors">
              Start New Lesson
            </button>
            <button className="bg-transparent border-2 border-white text-white px-6 py-3 rounded-lg font-semibold hover:bg-white hover:text-primary-600 transition-colors">
              View Recommendations
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Progress;
