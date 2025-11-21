import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { FiMail, FiArrowLeft, FiCheck } from 'react-icons/fi';
import toast from 'react-hot-toast';
import axios from 'axios';

const ForgotPassword = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [emailSent, setEmailSent] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    getValues
  } = useForm();

  const onSubmit = async (data) => {
    setIsLoading(true);
    
    try {
      await axios.post('http://localhost:8000/auth/forgot-password', {
        email: data.email
      });
      
      setEmailSent(true);
      toast.success('Password reset email sent!');
    } catch (error) {
      console.error('Forgot password error:', error);
      toast.error(error.response?.data?.detail || 'Failed to send reset email');
    } finally {
      setIsLoading(false);
    }
  };

  if (emailSent) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8">
          <div className="text-center">
            <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100 mb-4">
              <FiCheck className="h-8 w-8 text-green-600" />
            </div>
            <h1 className="text-dyslexic-2xl font-bold text-gray-900 mb-2">
              Check Your Email
            </h1>
            <p className="text-dyslexic-base text-gray-600 mb-6">
              We've sent a password reset link to <strong>{getValues('email')}</strong>
            </p>
          </div>

          <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-gray-200">
            <div className="text-center space-y-4">
              <p className="text-dyslexic-base text-gray-700">
                Please check your email and click the reset link to create a new password.
              </p>
              <p className="text-dyslexic-sm text-gray-500">
                Didn't receive the email? Check your spam folder or try again.
              </p>
              
              <div className="pt-4">
                <button
                  onClick={() => setEmailSent(false)}
                  className="btn-secondary w-full py-3 text-dyslexic-base font-semibold"
                >
                  Try Different Email
                </button>
              </div>
            </div>
          </div>

          <div className="text-center">
            <Link
              to="/login"
              className="inline-flex items-center text-primary-600 hover:text-primary-500 font-medium text-dyslexic-base"
            >
              <FiArrowLeft className="mr-2" />
              Back to Login
            </Link>
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
            Forgot Password?
          </h1>
          <p className="text-dyslexic-base text-gray-600">
            No worries! Enter your email and we'll send you a reset link.
          </p>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-8 border-2 border-gray-200">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
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
                <p className="form-error">
                  {errors.email.message}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isLoading}
              className="btn-primary w-full flex justify-center items-center py-4 text-dyslexic-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isLoading ? (
                <div className="flex items-center">
                  <div className="spinner mr-3"></div>
                  Sending Reset Link...
                </div>
              ) : (
                'Send Reset Link'
              )}
            </button>
          </form>
        </div>

        <div className="text-center">
          <Link
            to="/login"
            className="inline-flex items-center text-primary-600 hover:text-primary-500 font-medium text-dyslexic-base"
          >
            <FiArrowLeft className="mr-2" />
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
};

export default ForgotPassword;