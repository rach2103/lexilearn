import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useAccessibility } from '../../contexts/AccessibilityContext';
import { 
  FiMenu, 
  FiX, 
  FiHome, 
  FiMessageCircle, 
  FiAward, 
  FiTrendingUp, 
  FiSettings, 
  FiLogOut,
  FiUser,
  FiEye,
  FiType,
  FiVolume2
} from 'react-icons/fi';
import toast from 'react-hot-toast';

const Navbar = () => {
  const { user, logout } = useAuth();
  const { 
    settings, 
    toggleHighContrast, 
    toggleTextToSpeech, 
    increaseFontSize, 
    decreaseFontSize,
    increaseLineSpacing,
    decreaseLineSpacing
  } = useAccessibility();
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isAccessibilityOpen, setIsAccessibilityOpen] = useState(false);
  const location = useLocation();

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: FiHome },
    { name: 'AI Chat', href: '/chat', icon: FiMessageCircle },
    { name: 'Dyslexia Test', href: '/test', icon: FiAward },
    { name: 'Progress', href: '/progress', icon: FiTrendingUp },
    { name: 'Settings', href: '/settings', icon: FiSettings },
  ];

  const handleLogout = () => {
    logout();
    toast.success('Logged out successfully');
  };

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          {/* Logo and main navigation */}
          <div className="flex items-center">
            <Link to="/dashboard" className="flex items-center">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center mr-3">
                <span className="text-white font-bold text-lg">L</span>
              </div>
              <span className="text-dyslexic-xl font-bold text-gray-900">
                LexiLearn
              </span>
            </Link>
          </div>

          {/* Desktop navigation */}
          <div className="hidden md:flex items-center space-x-8">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-3 py-2 rounded-lg text-dyslexic-base font-medium transition-colors ${
                    isActive(item.href)
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="mr-2" size={18} />
                  {item.name}
                </Link>
              );
            })}
          </div>

          {/* Right side - User menu and accessibility */}
          <div className="flex items-center space-x-4">
            {/* Accessibility menu */}
            <div className="relative">
              <button
                onClick={() => setIsAccessibilityOpen(!isAccessibilityOpen)}
                className="p-2 text-gray-500 hover:text-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
                aria-label="Accessibility settings"
              >
                <FiEye size={20} />
              </button>

              {isAccessibilityOpen && (
                <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="p-4">
                    <h3 className="text-dyslexic-lg font-semibold text-gray-900 mb-4">
                      Accessibility Settings
                    </h3>
                    
                    <div className="space-y-4">
                      {/* Font size controls */}
                      <div>
                        <label className="text-dyslexic-sm font-medium text-gray-700 mb-2 block">
                          Font Size
                        </label>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={decreaseFontSize}
                            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                            aria-label="Decrease font size"
                          >
                            <FiType size={16} />
                          </button>
                          <span className="text-dyslexic-base font-mono min-w-[3rem] text-center">
                            {settings.fontSize}px
                          </span>
                          <button
                            onClick={increaseFontSize}
                            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                            aria-label="Increase font size"
                          >
                            <FiType size={20} />
                          </button>
                        </div>
                      </div>

                      {/* Line spacing controls */}
                      <div>
                        <label className="text-dyslexic-sm font-medium text-gray-700 mb-2 block">
                          Line Spacing
                        </label>
                        <div className="flex items-center space-x-2">
                          <button
                            onClick={decreaseLineSpacing}
                            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                            aria-label="Decrease line spacing"
                          >
                            <FiType size={16} />
                          </button>
                          <span className="text-dyslexic-base font-mono min-w-[3rem] text-center">
                            {settings.lineSpacing.toFixed(1)}
                          </span>
                          <button
                            onClick={increaseLineSpacing}
                            className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                            aria-label="Increase line spacing"
                          >
                            <FiType size={20} />
                          </button>
                        </div>
                      </div>

                      {/* Toggle switches */}
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-dyslexic-sm text-gray-700">High Contrast</span>
                          <button
                            onClick={toggleHighContrast}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                              settings.highContrast ? 'bg-primary-600' : 'bg-gray-200'
                            }`}
                            aria-label="Toggle high contrast"
                          >
                            <span
                              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                settings.highContrast ? 'translate-x-6' : 'translate-x-1'
                              }`}
                            />
                          </button>
                        </div>

                        <div className="flex items-center justify-between">
                          <span className="text-dyslexic-sm text-gray-700">Text to Speech</span>
                          <button
                            onClick={toggleTextToSpeech}
                            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                              settings.textToSpeech ? 'bg-primary-600' : 'bg-gray-200'
                            }`}
                            aria-label="Toggle text to speech"
                          >
                            <span
                              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                                settings.textToSpeech ? 'translate-x-6' : 'translate-x-1'
                              }`}
                            />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            {/* User menu */}
            <div className="relative">
              <button
                onClick={() => setIsMenuOpen(!isMenuOpen)}
                className="flex items-center space-x-2 p-2 text-gray-500 hover:text-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
                aria-label="User menu"
              >
                <FiUser size={20} />
                <span className="text-dyslexic-base font-medium">
                  {user?.full_name || user?.username || 'User'}
                </span>
              </button>

              {isMenuOpen && (
                <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 z-50">
                  <div className="py-1">
                    <div className="px-4 py-2 border-b border-gray-100">
                      <p className="text-dyslexic-sm font-medium text-gray-900">
                        {user?.full_name || user?.username}
                      </p>
                      <p className="text-dyslexic-sm text-gray-500">
                        {user?.email}
                      </p>
                    </div>
                    <button
                      onClick={handleLogout}
                      className="w-full text-left px-4 py-2 text-dyslexic-sm text-gray-700 hover:bg-gray-50 flex items-center"
                    >
                      <FiLogOut className="mr-2" size={16} />
                      Sign out
                    </button>
                  </div>
                </div>
              )}
            </div>

            {/* Mobile menu button */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 text-gray-500 hover:text-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
              aria-label="Toggle mobile menu"
            >
              {isMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 bg-white border-t border-gray-200">
            {navigation.map((item) => {
              const Icon = item.icon;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  onClick={() => setIsMenuOpen(false)}
                  className={`flex items-center px-3 py-2 rounded-lg text-dyslexic-base font-medium transition-colors ${
                    isActive(item.href)
                      ? 'bg-primary-100 text-primary-700'
                      : 'text-gray-600 hover:text-primary-600 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="mr-3" size={20} />
                  {item.name}
                </Link>
              );
            })}
            <button
              onClick={() => {
                handleLogout();
                setIsMenuOpen(false);
              }}
              className="w-full text-left flex items-center px-3 py-2 rounded-lg text-dyslexic-base font-medium text-gray-600 hover:text-red-600 hover:bg-red-50"
            >
              <FiLogOut className="mr-3" size={20} />
              Sign out
            </button>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
