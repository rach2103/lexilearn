import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { FiLock, FiEye, FiEyeOff, FiCheck } from 'react-icons/fi';
import toast from 'react-hot-toast';
import axios from 'axios';

const ResetPassword = () => {
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [isValidToken, setIsValidToken] = useState(null);
  const [resetSuccess, setResetSuccess] = useState(false);
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const token = searchParams.get('token');

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setError
  } = useForm();

  const password = watch('password');

  useEffect(() => {
    if (!token) {
      setIsValidToken(false);
      return;
    }
    setIsValidToken(true);
  }, [token]);

  const onSubmit = async (data) => {
    setIsLoading(true);
    
    try {
      await axios.post('http://localhost:8000/auth/reset-password', {
        token,
        new_password: data.password
      });
      
      setResetSuccess(true);
      toast.success('Password reset successful!');
    } catch (error) {
      console.error('Reset password error:', error);
      const message = error.response?.data?.detail || 'Failed to reset password';
      toast.error(message);
      setError('root', { type: 'manual', message });
    } finally {
      setIsLoading(false);
    }
  };

  if (isValidToken === null) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50">
        <div className="spinner-large"></div>
      </div>
    );
  }

  if (isValidToken === false) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <h1 className="text-dyslexic-2xl font-bold text-gray-900 mb-2">
              Invalid Reset Link
            </h1>
            <p className="text-dyslexic-base text-gray-600 mb-6">
              This password reset link is invalid or has expired.
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-gray-200 text-center">
            <p className="text-dyslexic-base text-gray-700 mb-6">
              Please request a new password reset link.
            </p>
            
            <div className="space-y-4">
              <Link
                to="/forgot-password"
                className="btn-primary w-full py-3 text-dyslexic-base font-semibold inline-block"
              >
                Request New Reset Link
              </Link>
              
              <Link
                to="/login"
                className="btn-secondary w-full py-3 text-dyslexic-base font-semibold inline-block"
              >
                Back to Login
              </Link>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (resetSuccess) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
              <FiCheck className="h-8 w-8 text-green-600" />
            </div>
            <h1 className="text-dyslexic-2xl font-bold text-gray-900 mb-2">
              Password Reset Complete
            </h1>
            <p className="text-dyslexic-base text-gray-600 mb-6">
              Your password has been successfully reset.
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-gray-200 text-center">
            <p className="text-dyslexic-base text-gray-700 mb-6">
              You can now log in with your new password.
            </p>
            
            <button
              onClick={() => navigate('/login')}
              className="btn-primary w-full py-3 text-dyslexic-base font-semibold"
            >
              Go to Login
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          <h1 className="text-dyslexic-2xl font-bold text-gray-900 mb-2">
            Reset Your Password
          </h1>
          <p className="text-dyslexic-base text-gray-600">
            Enter your new password below.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-gray-200">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
            {/* New Password Field */}
            <div className="form-group">
              <label htmlFor="password" className="form-label flex items-center">
                <FiLock className="mr-2 text-primary-600" />
                New Password
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
                  placeholder="Enter new password"
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
                Confirm New Password
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
                  placeholder="Confirm new password"
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
                  Resetting Password...
                </div>
              ) : (
                'Reset Password'
              )}
            </button>
          </form>
        </div>

        <div className="text-center">
          <Link
            to="/login"
            className="text-primary-600 hover:text-primary-500 font-medium text-dyslexic-base"
          >
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ResetPassword;