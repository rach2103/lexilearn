import React from 'react';
import { Link } from 'react-router-dom';
import { FiHeart, FiGithub, FiMail, FiInfo } from 'react-icons/fi';

const Footer = () => {
  return (
    <footer className="bg-white border-t border-gray-200 mt-auto">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
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

          {/* Support */}
          <div>
            <h3 className="text-dyslexic-lg font-semibold text-gray-900 mb-4">
              Support
            </h3>
            <ul className="space-y-2">
              <li>
                <Link to="/help" className="text-dyslexic-base text-gray-600 hover:text-primary-600 flex items-center">
                  <FiInfo className="mr-2" size={16} />
                  Help Center
                </Link>
              </li>
              <li>
                <a href="mailto:support@lexilearn.com" className="text-dyslexic-base text-gray-600 hover:text-primary-600 flex items-center">
                  <FiMail className="mr-2" size={16} />
                  Contact Us
                </a>
              </li>
              <li>
                <a href="https://github.com/lexilearn" target="_blank" rel="noopener noreferrer" className="text-dyslexic-base text-gray-600 hover:text-primary-600 flex items-center">
                  <FiGithub className="mr-2" size={16} />
                  GitHub
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-200 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center">
            <div className="text-dyslexic-sm text-gray-500 mb-4 md:mb-0">
              © 2024 LexiLearn. All rights reserved.
            </div>
            <div className="flex space-x-6">
              <Link to="/privacy" className="text-dyslexic-sm text-gray-500 hover:text-primary-600">
                Privacy Policy
              </Link>
              <Link to="/terms" className="text-dyslexic-sm text-gray-500 hover:text-primary-600">
                Terms of Service
              </Link>
              <Link to="/accessibility" className="text-dyslexic-sm text-gray-500 hover:text-primary-600">
                Accessibility
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
