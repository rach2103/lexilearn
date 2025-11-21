import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../contexts/AuthContext';
import { useAccessibility } from '../../contexts/AccessibilityContext';
import { FiMail, FiLock, FiUser, FiEye, FiEyeOff } from 'react-icons/fi';
import toast from 'react-hot-toast';

const Register = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { register: registerUser } = useAuth();
  const { settings } = useAccessibility();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setError,
  } = useForm();

  const password = watch('password');

  const onSubmit = async (data) => {
    setIsLoading(true);
    
    try {
      const userData = {
        username: data.username,
        email: data.email,
        password: data.password,
        full_name: data.fullName || data.username,
        preferred_font: 'OpenDyslexic',
        font_size: 16,
        line_spacing: 1.5,
        color_scheme: 'high_contrast',
        language_preference: 'en'
      };
      
      const result = await registerUser(userData);
      if (result.success) {
        navigate('/dashboard');
      } else {
        setError('root', {
          type: 'manual',
          message: result.error || 'Registration failed. Please try again.'
        });
      }
    } catch (error) {
      console.error('Registration error:', error);
      setError('root', {
        type: 'manual',
        message: 'An unexpected error occurred. Please try again.'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <h1 className="text-dyslexic-2xl font-bold text-gray-900 mb-2">
            Join LexiLearn
          </h1>
          <p className="text-dyslexic-base text-gray-600">
            Create your account and start your learning journey
          </p>
        </div>

        {/* Registration Form */}
        <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-gray-200">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* Full Name Field */}
            <div className="form-group">
              <label htmlFor="fullName" className="form-label flex items-center">
                <FiUser className="mr-2 text-primary-600" />
                Full Name
              </label>
              <input
                id="fullName"
                type="text"
                {...register('fullName', {
                  required: 'Full name is required',
                  minLength: {
                    value: 2,
                    message: 'Full name must be at least 2 characters'
                  }
                })}
                className={`input-field ${errors.fullName ? 'border-error-500' : ''}`}
                placeholder="Enter your full name"
                autoComplete="name"
              />
              {errors.fullName && (
                <p className="form-error">{errors.fullName.message}</p>
              )}
            </div>

            {/* Username Field */}
            <div className="form-group">
              <label htmlFor="username" className="form-label flex items-center">
                <FiUser className="mr-2 text-primary-600" />
                Username
              </label>
              <input
                id="username"
                type="text"
                {...register('username', {
                  required: 'Username is required',
                  minLength: {
                    value: 3,
                    message: 'Username must be at least 3 characters'
                  },
                  pattern: {
                    value: /^[a-zA-Z0-9_]+$/,
                    message: 'Username can only contain letters, numbers, and underscores'
                  }
                })}
                className={`input-field ${errors.username ? 'border-error-500' : ''}`}
                placeholder="Choose a username"
                autoComplete="username"
              />
              {errors.username && (
                <p className="form-error">{errors.username.message}</p>
              )}
            </div>

            {/* Email Field */}
            <div className="form-group">
              <label htmlFor="email" className="form-label flex items-center">
                <FiMail className="mr-2 text-primary-600" />
                Email Address
              </label>
              <input
                id="email"
                type="email"
                {...register('email', {
                  required: 'Email is required',
                  pattern: {
                    value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
                    message: 'Please enter a valid email address'
                  }
                })}
                className={`input-field ${errors.email ? 'border-error-500' : ''}`}
                placeholder="Enter your email address"
                autoComplete="email"
              />
              {errors.email && (
                <p className="form-error">{errors.email.message}</p>
              )}
            </div>

            {/* Password Field */}
            <div className="form-group">
              <label htmlFor="password" className="form-label flex items-center">
                <FiLock className="mr-2 text-primary-600" />
                Password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  {...register('password', {
                    required: 'Password is required',
                    minLength: {
                      value: 8,
                      message: 'Password must be at least 8 characters'
                    },
                    pattern: {
                      value: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/,
                      message: 'Password must contain uppercase, lowercase, and number'
                    }
                  })}
                  className={`input-field pr-12 ${errors.password ? 'border-error-500' : ''}`}
                  placeholder="Create a strong password"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
                >
                  {showPassword ? <FiEyeOff size={20} /> : <FiEye size={20} />}
                </button>
              </div>
              {errors.password && (
                <p className="form-error">{errors.password.message}</p>
              )}
            </div>

            {/* Confirm Password Field */}
            <div className="form-group">
              <label htmlFor="confirmPassword" className="form-label flex items-center">
                <FiLock className="mr-2 text-primary-600" />
                Confirm Password
              </label>
              <div className="relative">
                <input
                  id="confirmPassword"
                  type={showConfirmPassword ? 'text' : 'password'}
                  {...register('confirmPassword', {
                    required: 'Please confirm your password',
                    validate: value => value === password || 'Passwords do not match'
                  })}
                  className={`input-field pr-12 ${errors.confirmPassword ? 'border-error-500' : ''}`}
                  placeholder="Confirm your password"
                  autoComplete="new-password"
                />
                <button
                  type="button"
                  onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none"
                >
                  {showConfirmPassword ? <FiEyeOff size={20} /> : <FiEye size={20} />}
                </button>
              </div>
              {errors.confirmPassword && (
                <p className="form-error">{errors.confirmPassword.message}</p>
              )}
            </div>

            {/* Password Requirements */}
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <h4 className="text-dyslexic-sm font-semibold text-blue-900 mb-2">
                Password Requirements:
              </h4>
              <ul className="text-dyslexic-xs text-blue-800 space-y-1">
                <li>• At least 8 characters long</li>
                <li>• Contains uppercase letter</li>
                <li>• Contains lowercase letter</li>
                <li>• Contains at least one number</li>
              </ul>
            </div>

            {/* Root Error */}
            {errors.root && (
              <div className="bg-error-50 border border-error-200 rounded-lg p-4">
                <p className="text-error-700 text-dyslexic-sm">
                  {errors.root.message}
                </p>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full flex justify-center items-center py-4 text-dyslexic-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="spinner mr-3"></div>
                  Creating Account...
                </div>
              ) : (
                'Create Account'
              )}
            </button>
          </form>
        </div>

        {/* Sign In Link */}
        <div className="text-center">
          <p className="text-dyslexic-base text-gray-600">
            Already have an account?{' '}
            <Link
              to="/login"
              className="text-primary-600 hover:text-primary-500 font-semibold"
            >
              Sign in here
            </Link>
          </p>
        </div>

        {/* Accessibility Features */}
        <div className="bg-green-50 rounded-lg p-4 border border-green-200">
          <h3 className="text-dyslexic-lg font-semibold text-green-900 mb-2">
            What You'll Get
          </h3>
          <ul className="text-dyslexic-sm text-green-800 space-y-1">
            <li>• Personalized AI tutoring</li>
            <li>• Dyslexia-friendly interface</li>
            <li>• Speech-to-text capabilities</li>
            <li>• Progress tracking</li>
            <li>• Interactive lessons</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Register;