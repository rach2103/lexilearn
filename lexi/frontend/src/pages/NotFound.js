import React from 'react';
import { Link } from 'react-router-dom';
import { FiHome, FiArrowLeft, FiSearch } from 'react-icons/fi';

const NotFound = () => {
  return (
    <div className="min-h-screen bg-gray-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full text-center">
        {/* 404 Icon */}
        <div className="mb-8">
          <div className="mx-auto w-24 h-24 bg-primary-100 rounded-full flex items-center justify-center mb-4">
            <FiSearch className="text-primary-600" size={48} />
          </div>
        </div>

        {/* Error Message */}
        <div className="mb-8">
          <h1 className="text-dyslexic-2xl font-bold text-gray-900 mb-4">
            Page Not Found
          </h1>
          <p className="text-dyslexic-base text-gray-600 mb-6">
            Sorry, we couldn't find the page you're looking for. 
            It might have been moved, deleted, or you entered the wrong URL.
          </p>
          <div className="text-dyslexic-lg text-gray-500 font-mono">
            404
          </div>
        </div>

        {/* Action Buttons */}
        <div className="space-y-4">
          <Link
            to="/dashboard"
            className="btn-primary w-full flex justify-center items-center py-4 text-dyslexic-lg font-semibold"
          >
            <FiHome className="mr-2" />
            Go to Dashboard
          </Link>
          
          <button
            onClick={() => window.history.back()}
            className="btn-secondary w-full flex justify-center items-center py-4 text-dyslexic-lg font-semibold"
          >
            <FiArrowLeft className="mr-2" />
            Go Back
          </button>
        </div>

        {/* Helpful Links */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <h3 className="text-dyslexic-lg font-semibold text-gray-900 mb-4">
            Popular Pages
          </h3>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <Link
              to="/chat"
              className="p-4 bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all"
            >
              <div className="text-dyslexic-base font-medium text-gray-900">
                AI Chat
              </div>
              <div className="text-dyslexic-sm text-gray-600">
                Practice with AI tutor
              </div>
            </Link>
            
            <Link
              to="/test"
              className="p-4 bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all"
            >
              <div className="text-dyslexic-base font-medium text-gray-900">
                Dyslexia Test
              </div>
              <div className="text-dyslexic-sm text-gray-600">
                Take screening test
              </div>
            </Link>
            
            <Link
              to="/progress"
              className="p-4 bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all"
            >
              <div className="text-dyslexic-base font-medium text-gray-900">
                Progress
              </div>
              <div className="text-dyslexic-sm text-gray-600">
                View your progress
              </div>
            </Link>
            
            <Link
              to="/settings"
              className="p-4 bg-white rounded-lg border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all"
            >
              <div className="text-dyslexic-base font-medium text-gray-900">
                Settings
              </div>
              <div className="text-dyslexic-sm text-gray-600">
                Customize preferences
              </div>
            </Link>
          </div>
        </div>

        {/* Contact Support */}
        <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h3 className="text-dyslexic-lg font-semibold text-blue-900 mb-2">
            Need Help?
          </h3>
          <p className="text-dyslexic-sm text-blue-800 mb-3">
            If you believe this is an error, please contact our support team.
          </p>
          <a
            href="mailto:support@lexilearn.com"
            className="text-blue-600 hover:text-blue-500 text-dyslexic-sm font-medium"
          >
            Contact Support
          </a>
        </div>
      </div>
    </div>
  );
};

export default NotFound;
