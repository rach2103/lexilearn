import React from 'react';
import { Link } from 'react-router-dom';
import { FiHeart } from 'react-icons/fi';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* Brand */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-lg">L</span>
              </div>
              <span className="text-dyslexic-xl font-bold text-gray-900">
                LexiLearn
              </span>
            </div>
            <p className="text-dyslexic-base text-gray-600 mb-4 max-w-md">
              Empowering dyslexic students with AI-powered learning tools designed for accessibility and success.
            </p>
            <div className="flex items-center text-dyslexic-sm text-gray-500">
              <span>Made with</span>
              <FiHeart className="mx-2 text-red-500" size={16} />
              <span>for inclusive education</span>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-dyslexic-lg font-semibold text-gray-900 mb-4">
              Quick Links
            </h3>
            <ul className="space-y-2">
              <li>
                <Link to="/dashboard" className="text-dyslexic-base text-gray-600 hover:text-primary-600">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link to="/chat" className="text-dyslexic-base text-gray-600 hover:text-primary-600">
                  AI Chat
                </Link>
              </li>
              <li>
                <Link to="/test" className="text-dyslexic-base text-gray-600 hover:text-primary-600">
                  Dyslexia Test
                </Link>
              </li>
              <li>
                <Link to="/progress" className="text-dyslexic-base text-gray-600 hover:text-primary-600">
                  Progress
                </Link>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
