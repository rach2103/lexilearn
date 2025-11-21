import React, { useState, useEffect } from 'react';
import { FiPlay, FiClock, FiExternalLink, FiVideo } from 'react-icons/fi';
import axios from 'axios';
import toast from 'react-hot-toast';

const LearningVideos = ({ selectedLevel = 'beginner' }) => {
  const [videos, setVideos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentLevel, setCurrentLevel] = useState(selectedLevel);

  useEffect(() => {
    fetchVideos(currentLevel);
  }, [currentLevel]);

  const fetchVideos = async (level) => {
    try {
      setLoading(true);
      const response = await axios.get(`/api/learning-videos?level=${level}`);
      setVideos(response.data.videos);
    } catch (error) {
      console.error('Error fetching videos:', error);
      toast.error('Failed to load learning videos');
    } finally {
      setLoading(false);
    }
  };

  const openVideo = (videoUrl) => {
    window.open(videoUrl, '_blank');
  };

  const levels = [
    { id: 'beginner', name: 'Beginner', color: 'bg-green-100 text-green-800' },
    { id: 'intermediate', name: 'Intermediate', color: 'bg-blue-100 text-blue-800' },
    { id: 'advanced', name: 'Advanced', color: 'bg-purple-100 text-purple-800' }
  ];

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="spinner"></div>
        <span className="ml-3 text-gray-600">Loading videos...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Level Selector */}
      <div className="flex flex-wrap gap-3">
        {levels.map((level) => (
          <button
            key={level.id}
            onClick={() => setCurrentLevel(level.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition-all ${
              currentLevel === level.id
                ? level.color
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {level.name}
          </button>
        ))}
      </div>

      {/* Videos Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {videos.map((video) => (
          <div
            key={video.id}
            className="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-lg transition-shadow"
          >
            {/* Video Thumbnail */}
            <div className="relative bg-gray-900 aspect-video">
              <img
                src={`https://img.youtube.com/vi/${video.id}/maxresdefault.jpg`}
                alt={video.title}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = `https://img.youtube.com/vi/${video.id}/hqdefault.jpg`;
                }}
              />
              <div className="absolute inset-0 bg-black bg-opacity-40 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                <button
                  onClick={() => openVideo(video.url)}
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

            {/* Video Info */}
            <div className="p-4">
              <h3 className="text-dyslexic-lg font-semibold text-gray-900 mb-2 line-clamp-2">
                {video.title}
              </h3>
              <p className="text-dyslexic-sm text-gray-600 mb-4 line-clamp-3">
                {video.description}
              </p>
              <button
                onClick={() => openVideo(video.url)}
                className="w-full btn-primary flex items-center justify-center"
              >
                <FiExternalLink className="mr-2" size={16} />
                Watch on YouTube
              </button>
            </div>
          </div>
        ))}
      </div>

      {videos.length === 0 && (
        <div className="text-center py-12">
          <FiVideo className="mx-auto text-gray-400 mb-4" size={48} />
          <p className="text-gray-600">No videos available for this level.</p>
        </div>
      )}
    </div>
  );
};

export default LearningVideos;