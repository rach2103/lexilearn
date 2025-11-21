import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { FiBookOpen, FiPlay, FiClock, FiStar, FiVideo } from 'react-icons/fi';
import LearningVideos from '../components/LearningVideos';

const Lessons = () => {
  const [activeTab, setActiveTab] = useState('lessons');
  
  const lessons = [
    {
      id: 1,
      title: 'Phonics Practice',
      description: 'Master letter sounds and combinations with interactive exercises',
      duration: '20 min',
      difficulty: 'Beginner',
      completed: true,
      externalUrl: 'https://www.dyslexiclogic.com/fabulous-phonics-resources'
    },
    {
      id: 2,
      title: 'Reading Comprehension',
      description: 'Improve understanding of written text with dyslexia-friendly materials',
      duration: '25 min',
      difficulty: 'Intermediate',
      completed: false,
      externalUrl: 'https://elt.oup.com/student/englishfile/dyslexicfriendly?srsltid=AfmBOoq7m0HWapHLCU3yF6tLUmCQciQ5QUuYxv70QHvfBPbFqImcIDnh&cc=global&selLanguage=en'
    },
    {
      id: 3,
      title: 'Sight Words',
      description: 'Practice common sight words recognition with proven techniques',
      duration: '15 min',
      difficulty: 'Beginner',
      completed: false,
      externalUrl: 'https://www.understood.org/en/articles/12-tips-to-help-kids-with-dyslexia-learn-sight-words'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-6 sm:px-8 lg:px-12">
        <div className="mb-8">
          <h1 className="text-dyslexic-3xl font-bold text-gray-900 mb-2">
            Start Learning
          </h1>
          <p className="text-dyslexic-lg text-gray-600">
            Choose lessons or watch educational videos to continue your learning journey
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="mb-8">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('lessons')}
                className={`py-2 px-1 border-b-2 font-medium text-dyslexic-base ${
                  activeTab === 'lessons'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <FiBookOpen className="inline mr-2" size={16} />
                Learning Sources
              </button>
              <button
                onClick={() => setActiveTab('videos')}
                className={`py-2 px-1 border-b-2 font-medium text-dyslexic-base ${
                  activeTab === 'videos'
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <FiVideo className="inline mr-2" size={16} />
                Learning Videos
              </button>
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === 'lessons' && (
          <div className="grid gap-6">
            {lessons.map((lesson) => (
              <div
                key={lesson.id}
                className="bg-white rounded-xl shadow-sm p-6 border border-gray-200 hover:shadow-md transition-shadow"
              >
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center mb-2">
                      <FiBookOpen className="text-primary-600 mr-2" size={20} />
                      <h3 className="text-dyslexic-xl font-semibold text-gray-900">
                        {lesson.title}
                      </h3>
                      {lesson.completed && (
                        <FiStar className="text-yellow-500 ml-2" size={16} />
                      )}
                    </div>
                    
                    <p className="text-dyslexic-base text-gray-600 mb-4">
                      {lesson.description}
                    </p>
                    
                    <div className="flex items-center space-x-4 text-dyslexic-sm text-gray-500">
                      <div className="flex items-center">
                        <FiClock className="mr-1" size={14} />
                        {lesson.duration}
                      </div>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        lesson.difficulty === 'Beginner' 
                          ? 'bg-success-100 text-success-800'
                          : 'bg-warning-100 text-warning-800'
                      }`}>
                        {lesson.difficulty}
                      </span>
                    </div>
                  </div>
                  
                  <div className="ml-6">
                    <a
                      href={lesson.externalUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="btn-primary flex items-center"
                    >
                      <FiPlay className="mr-2" size={16} />
                      View Source
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'videos' && (
          <div className="bg-white rounded-xl shadow-sm p-6">
            <div className="mb-6">
              <h2 className="text-dyslexic-2xl font-bold text-gray-900 mb-2">
                Educational Videos
              </h2>
              <p className="text-dyslexic-base text-gray-600">
                Watch curated YouTube videos about dyslexia and learning strategies
              </p>
            </div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              {[
                { id: 'BRfHEdM2cWw', title: 'Understanding Dyslexia', duration: '15 min' },
                { id: 'JzO-DoJNZCE', title: 'Reading Strategies for Dyslexia', duration: '12 min' },
                { id: 'AfgXYhB_Bw0', title: 'Phonics Fundamentals', duration: '18 min' },
                { id: 'M1S668Aemiw', title: 'Spelling Techniques', duration: '10 min' },
                { id: 'ZgFZO9nLnYk', title: 'Writing Skills Development', duration: '14 min' },
                { id: '8SJtv2s1XL8', title: 'Memory and Learning Tips', duration: '16 min' },
                { id: 'dRuuvC-vmU4', title: 'Comprehension Strategies', duration: '13 min' },
                { id: '3_cHBybqMpk', title: 'Sight Words Mastery', duration: '11 min' },
                { id: 'etPZXHIfp50', title: 'Overcoming Reading Challenges', duration: '17 min' },
                { id: 'ftrXVxbkjUs', title: 'Building Confidence in Learning', duration: '12 min' },
                { id: 'zafiGBrFkRM', title: 'Study Skills for Success', duration: '15 min' }
              ].map((video) => (
                <div
                  key={video.id}
                  className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow"
                >
                  <div className="relative bg-gray-900 aspect-video">
                    <img
                      src={`https://img.youtube.com/vi/${video.id}/hqdefault.jpg`}
                      alt={video.title}
                      className="w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                      <button
                        onClick={() => window.open(`https://www.youtube.com/watch?v=${video.id}`, '_blank')}
                        className="bg-red-600 hover:bg-red-700 text-white rounded-full p-4 transition-colors"
                      >
                        <FiPlay size={24} />
                      </button>
                    </div>
                    <div className="absolute bottom-2 right-2 bg-black bg-opacity-75 text-white px-2 py-1 rounded text-sm flex items-center">
                      <FiClock size={12} className="mr-1" />
                      {video.duration}
                    </div>
                  </div>
                  <div className="p-4">
                    <h3 className="text-dyslexic-lg font-semibold text-gray-900 mb-4">
                      {video.title}
                    </h3>
                    <button
                      onClick={() => window.open(`https://www.youtube.com/watch?v=${video.id}`, '_blank')}
                      className="w-full btn-primary flex items-center justify-center"
                    >
                      <FiPlay className="mr-2" size={16} />
                      Watch on YouTube
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Lessons;