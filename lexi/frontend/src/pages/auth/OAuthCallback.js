import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const OAuthCallback = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const { setToken } = useAuth();

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (token) {
      localStorage.setItem('token', token);
      if (setToken) {
        setToken(token);
      }
      navigate('/dashboard');
    } else {
      navigate('/login');
    }
  }, [searchParams, navigate, setToken]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-primary-50 to-secondary-50">
      <div className="text-center">
        <div className="spinner mx-auto mb-4"></div>
        <p className="text-dyslexic-lg text-gray-700">Completing sign in...</p>
      </div>
    </div>
  );
};

export default OAuthCallback;
