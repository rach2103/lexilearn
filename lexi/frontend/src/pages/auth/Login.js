import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { useAuth } from '../../contexts/AuthContext';
import { useAccessibility } from '../../contexts/AccessibilityContext';
import { FiEye, FiEyeOff, FiMail, FiLock } from 'react-icons/fi';
import toast from 'react-hot-toast';

const Login = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const { settings } = useAccessibility();
  const navigate = useNavigate();

  const {
    register,
    handleSubmit,
    formState: { errors },
    setError,
  } = useForm();

  const onSubmit = async (data) => {
    setIsLoading(true);
    console.log('Login form submitted:', data.email);
    
    try {
      const result = await login(data.email, data.password);
      console.log('Login result:', result);
      
      if (result.success) {
        console.log('Login successful, navigating to dashboard');
        setTimeout(() => {
          navigate('/dashboard', { replace: true });
        }, 100);
      } else {
        console.error('Login failed:', result.error);
        setError('root', {
          type: 'manual',
          message: result.error || 'Login failed. Please try again.'
        });
      }
    } catch (error) {
      console.error('Login error:', error);
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
            Welcome to LexiLearn
          </h1>
          <p className="text-dyslexic-base text-gray-600">
            Your AI-powered learning companion for dyslexic students
          </p>
        </div>

        {/* Login Form */}
        <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-gray-200">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
                placeholder="Enter your email"
                autoComplete="email"
                aria-describedby={errors.email ? 'email-error' : undefined}
              />
              {errors.email && (
                <p id="email-error" className="form-error">
                  {String(errors.email.message || 'Invalid email')}
                </p>
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
                      value: 6,
                      message: 'Password must be at least 6 characters'
                    }
                  })}
                  className={`input-field pr-12 ${errors.password ? 'border-error-500' : ''}`}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  aria-describedby={errors.password ? 'password-error' : undefined}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 hover:text-gray-700 focus:outline-none focus:text-gray-700"
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                >
                  {showPassword ? <FiEyeOff size={20} /> : <FiEye size={20} />}
                </button>
              </div>
              {errors.password && (
                <p id="password-error" className="form-error">
                  {String(errors.password.message || 'Invalid password')}
                </p>
              )}
            </div>

            {/* Remember Me */}
            <div className="flex items-center">
              <input
                id="remember-me"
                name="remember-me"
                type="checkbox"
                className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              />
              <label htmlFor="remember-me" className="ml-2 text-dyslexic-sm text-gray-700">
                Remember me
              </label>
            </div>

            {/* Root Error */}
            {errors.root && (
              <div className="bg-error-50 border border-error-200 rounded-lg p-4">
                <p className="text-error-700 text-dyslexic-sm">
                  {String(errors.root.message || 'An error occurred')}
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
                  Signing in...
                </div>
              ) : (
                'Sign In'
              )}
            </button>
          </form>


        </div>

        {/* Sign Up Link */}
        <div className="text-center">
          <p className="text-dyslexic-base text-gray-600">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="text-primary-600 hover:text-primary-500 font-semibold"
            >
              Sign up here
            </Link>
          </p>
        </div>

        {/* Accessibility Features */}
        <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
          <h3 className="text-dyslexic-lg font-semibold text-blue-900 mb-2">
            Accessibility Features
          </h3>
          <ul className="text-dyslexic-sm text-blue-800 space-y-1">
            <li>• High contrast mode available</li>
            <li>• Dyslexia-friendly fonts</li>
            <li>• Adjustable text size and spacing</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default Login;
