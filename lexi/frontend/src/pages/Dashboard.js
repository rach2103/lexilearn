import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import useTimeTracking from '../useTimeTracking';
import axios from 'axios';
import { 
  FiMessageCircle, 
  FiAward, 
  FiTrendingUp, 
  FiBookOpen,
  FiClock,
  FiTarget,
  FiPlay,
  FiStar
} from 'react-icons/fi';

const Dashboard = () => {
  const { user } = useAuth();
  useTimeTracking(); // Start time tracking
  const [stats, setStats] = useState({
    exercises_completed: 0,
    accuracy: 0,
    total_messages: 0,
    daily_messages: 0,
    study_time_minutes: 0,
    skill_progress: {
      reading: 0,
      writing: 0,
      spelling: 0,
      comprehension: 0
    }
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUserStats();
  }, []);

  const fetchUserStats = async () => {
    try {
      const response = await axios.get('/api/user/stats');
      const exercisesFromStorage = parseInt(localStorage.getItem('exercisesCompleted') || '0', 10);
      setStats({
        ...response.data,
        exercises_completed: exercisesFromStorage
      });
    } catch (error) {
      console.error('Failed to fetch user stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLessonClick = () => {
    const currentClicks = parseInt(localStorage.getItem('lessonClicks') || '0', 10);
    localStorage.setItem('lessonClicks', (currentClicks + 1).toString());
  };

  const quickActions = [
    {
      title: 'Start AI Chat',
      description: 'Practice with your AI tutor',
      icon: FiMessageCircle,
      href: '/chat',
      color: 'bg-blue-100 text-blue-700'
    },
    {
      title: 'Take Test',
      description: 'Dyslexia screening assessment',
      icon: FiAward,
      href: '/test',
      color: 'bg-green-100 text-green-700'
    },
    {
      title: 'View Progress',
      description: 'Track your learning journey',
      icon: FiTrendingUp,
      href: '/progress',
      color: 'bg-purple-100 text-purple-700'
    },
    {
      title: 'Start Lesson',
      description: 'Begin a new learning session',
      icon: FiBookOpen,
      href: '/lessons',
      color: 'bg-orange-100 text-orange-700',
      onClick: handleLessonClick
    },
    {
      title: 'Reading Fundamentals',
      description: 'View comprehensive reading strategies',
      icon: FiStar,
      href: 'https://texasldcenter.org/wp-content/uploads/2023/12/ReadingStrategies_Dyslexia_Complete.pdf',
      color: 'bg-pink-100 text-pink-700',
      external: true
    }
  ];

  const formatTime = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Welcome Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Welcome back, {user?.full_name || user?.username || 'Student'}!
          </h1>
          <p className="text-lg text-gray-600">
            Ready to continue your learning journey? Here's your progress overview.
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-blue-100 rounded-lg">
                <FiBookOpen className="text-blue-600" size={24} />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Exercises Completed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {loading ? '...' : stats.exercises_completed}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-green-100 rounded-lg">
                <FiTarget className="text-green-600" size={24} />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Accuracy</p>
                <p className="text-2xl font-bold text-gray-900">
                  {loading ? '...' : `${stats.accuracy}%`}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-yellow-100 rounded-lg">
                <FiClock className="text-yellow-600" size={24} />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Study Time</p>
                <p className="text-2xl font-bold text-gray-900">
                  {loading ? '...' : formatTime(stats.study_time_minutes)}
                </p>
              </div>
            </div>
          </div>

          <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
            <div className="flex items-center">
              <div className="p-3 bg-purple-100 rounded-lg">
                <FiTrendingUp className="text-purple-600" size={24} />
              </div>
              <div className="ml-4">
                <p className="text-sm text-gray-600">Daily Messages</p>
                <p className="text-2xl font-bold text-gray-900">
                  {loading ? '...' : stats.daily_messages}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Quick Actions
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {quickActions.map((action, index) => {
              const Icon = action.icon;
              const Component = action.external ? 'a' : Link;
              const linkProps = action.external 
                ? { href: action.href, target: '_blank', rel: 'noopener noreferrer' }
                : { to: action.href };
              
              const handleClick = () => {
                if (action.onClick) action.onClick();
              };
              
              return (
                <Component
                  key={index}
                  {...linkProps}
                  onClick={handleClick}
                  className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow group"
                >
                  <div className="flex items-center mb-4">
                    <div className={`p-3 rounded-lg ${action.color}`}>
                      <Icon size={24} />
                    </div>
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                    {action.title}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {action.description}
                  </p>
                </Component>
              );
            })}
          </div>
        </div>

        {/* Learning Progress */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">
            Learning Progress
          </h2>
          
          {loading ? (
            <div className="text-center py-8 text-gray-500">Loading progress...</div>
          ) : stats.exercises_completed === 0 ? (
            <div className="text-center py-8 text-gray-500">
              Start practicing to see your progress!
            </div>
          ) : (
            <div className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-blue-700 mb-1">Daily Chat Messages</div>
                  <div className="text-2xl font-bold text-blue-900">{stats.daily_messages || 0}</div>
                  <div className="text-xs text-blue-600">Messages today</div>
                </div>
                <div className="bg-green-50 rounded-lg p-4">
                  <div className="text-sm font-medium text-green-700 mb-1">Learning Rate</div>
                  <div className="text-2xl font-bold text-green-900">{stats.accuracy}%</div>
                  <div className="text-xs text-green-600">Overall accuracy</div>
                </div>
              </div>
              
              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-base font-medium text-gray-700">
                    Reading Skills
                  </span>
                  <span className="text-sm text-gray-500">{stats.skill_progress.reading}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-blue-600 h-3 rounded-full" style={{ width: `${stats.skill_progress.reading}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-base font-medium text-gray-700">
                    Writing Skills
                  </span>
                  <span className="text-sm text-gray-500">{stats.skill_progress.writing}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-green-600 h-3 rounded-full" style={{ width: `${stats.skill_progress.writing}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-base font-medium text-gray-700">
                    Spelling
                  </span>
                  <span className="text-sm text-gray-500">{stats.skill_progress.spelling}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-yellow-600 h-3 rounded-full" style={{ width: `${stats.skill_progress.spelling}%` }}></div>
                </div>
              </div>

              <div>
                <div className="flex items-center justify-between mb-2">
                  <span className="text-base font-medium text-gray-700">
                    Comprehension
                  </span>
                  <span className="text-sm text-gray-500">{stats.skill_progress.comprehension}%</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-3">
                  <div className="bg-purple-600 h-3 rounded-full" style={{ width: `${stats.skill_progress.comprehension}%` }}></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Motivational Message */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl p-8 text-center">
          <h2 className="text-2xl font-bold text-white mb-4">
            Keep up the great work!
          </h2>
          <p className="text-lg text-blue-100 mb-6">
            You're making excellent progress in your learning journey. 
            Every step forward is a victory worth celebrating.
          </p>
          <Link
            to="/chat"
            className="inline-flex items-center px-6 py-3 bg-white text-blue-600 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
          >
            <FiPlay className="mr-2" />
            Continue Learning
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;