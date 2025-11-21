import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
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

      setProgressData({
        weeklyProgress: weekly.length ? weekly : progressData.weeklyProgress,
        skillProgress: skills.length ? skills : progressData.skillProgress,
        achievements: achievements.length ? achievements : progressData.achievements,
        summary: {
          totalLessons: statsData.exercises_completed || (data.lessons_completed || []).length || 0,
          averageAccuracy: Math.round(statsData.accuracy || data.overall_accuracy || 0),
          studyTimeMins: Math.round(statsData.study_time_minutes || data.total_study_time || 0),
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
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Skill Progress */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h2 className="text-dyslexic-xl font-bold text-gray-900 mb-6">
              Skill Progress
            </h2>
            <div className="space-y-6">
              {progressData.skillProgress.map((skill, index) => (
                <div key={index}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-dyslexic-base font-medium text-gray-700">
                      {skill.skill}
                    </span>
                    <span className="text-dyslexic-sm text-gray-500">
                      {skill.current}% / {skill.target}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full ${getColorClasses(skill.color)}`}
                      style={{ width: `${(skill.current / skill.target) * 100}%` }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Achievements */}
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <h2 className="text-dyslexic-xl font-bold text-gray-900 mb-6">
              Recent Achievements
            </h2>
            <div className="space-y-4">
              {progressData.achievements.map((achievement) => {
                const Icon = achievement.icon;
                return (
                  <div key={achievement.id} className="flex items-start space-x-4 p-4 bg-gray-50 rounded-lg">
                    <div className="flex-shrink-0">
                      <div className="p-2 bg-yellow-100 rounded-lg">
                        <Icon className="text-yellow-600" size={20} />
                      </div>
                    </div>
                    <div className="flex-1">
                      <h3 className="text-dyslexic-base font-semibold text-gray-900">
                        {achievement.title}
                      </h3>
                      <p className="text-dyslexic-sm text-gray-600">
                        {achievement.description}
                      </p>
                      <p className="text-dyslexic-sm text-gray-500 mt-1">
                        {new Date(achievement.date).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

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
