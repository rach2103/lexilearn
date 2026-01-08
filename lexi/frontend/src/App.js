import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { AccessibilityProvider } from './contexts/AccessibilityContext';
import { PrivacyProvider } from './contexts/PrivacyContext';
import useTimeTracking from './useTimeTracking';

// Components
import Navbar from './components/layout/Navbar';
import Footer from './components/layout/Footer';
import LoadingSpinner from './components/common/LoadingSpinner';

// Pages
import Login from './pages/auth/Login';
import Register from './pages/auth/Register';
import ForgotPassword from './pages/auth/ForgotPassword';
import OAuthCallback from './pages/auth/OAuthCallback';
import Dashboard from './pages/Dashboard';
import ChatBot from './pages/ChatBot';
import DyslexiaTest from './pages/DyslexiaTest';
import Lessons from './pages/Lessons';
import Progress from './pages/Progress';
import Settings from './pages/Settings';
import NotFound from './pages/NotFound';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const { user, loading } = useAuth();
  
  if (loading) {
    return <LoadingSpinner />;
  }
  
  return user ? children : <Navigate to="/login" replace />;
};

// Main App Component
const AppContent = () => {
  const { user } = useAuth();
  useTimeTracking(); // Global time tracking
  const [isLoading, setIsLoading] = useState(true);
  const [sessionStartTime] = useState(Date.now());
  const [alertShown, setAlertShown] = useState(false);

  useEffect(() => {
    // Simulate initial loading
    const timer = setTimeout(() => {
      setIsLoading(false);
    }, 1000);

    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!user) return;

    const checkUsageTime = () => {
      const currentTime = Date.now();
      const usageTime = (currentTime - sessionStartTime) / 1000 / 60;

      if (usageTime >= 30 && !alertShown) {
        alert('⏰ You\'ve been using the app for 30 minutes!\n\nTake a break to rest your eyes and mind. Regular breaks help with learning and prevent fatigue.\n\n💡 Tip: Try the 20-20-20 rule - every 20 minutes, look at something 20 feet away for 20 seconds.');
        setAlertShown(true);
      }
    };

    const interval = setInterval(checkUsageTime, 60000);
    return () => clearInterval(interval);
  }, [user, sessionStartTime, alertShown]);

  if (isLoading) {
    return <LoadingSpinner />;
  }

  return (
    <Router>
      <div className="min-h-screen bg-gray-50 flex flex-col">
        {user && <Navbar />}
        
        <main className="flex-1">
          <Routes>
            {/* Public Routes */}
            <Route path="/login" element={!user ? <Login /> : <Navigate to="/dashboard" replace />} />
            <Route path="/register" element={!user ? <Register /> : <Navigate to="/dashboard" replace />} />
            <Route path="/forgot-password" element={!user ? <ForgotPassword /> : <Navigate to="/dashboard" replace />} />
            <Route path="/auth/callback" element={<OAuthCallback />} />
            
            {/* Protected Routes */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            
            <Route path="/chat" element={
              <ProtectedRoute>
                <ChatBot />
              </ProtectedRoute>
            } />
            
            <Route path="/test" element={
              <ProtectedRoute>
                <DyslexiaTest />
              </ProtectedRoute>
            } />
            
            <Route path="/lessons" element={
              <ProtectedRoute>
                <Lessons />
              </ProtectedRoute>
            } />
            
            <Route path="/progress" element={
              <ProtectedRoute>
                <Progress />
              </ProtectedRoute>
            } />
            
            <Route path="/settings" element={
              <ProtectedRoute>
                <Settings />
              </ProtectedRoute>
            } />
            
            {/* Default Routes */}
            <Route path="/" element={<Navigate to={user ? "/dashboard" : "/login"} replace />} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </main>
        
        {user && <Footer />}
        
        {/* Toast Notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              fontFamily: 'OpenDyslexic, Arial, sans-serif',
              fontSize: '1rem',
              lineHeight: '1.6',
              letterSpacing: '0.05em',
              borderRadius: '8px',
              padding: '16px',
            },
            success: {
              style: {
                background: '#d4edda',
                color: '#155724',
                border: '2px solid #c3e6cb',
              },
            },
            error: {
              style: {
                background: '#f8d7da',
                color: '#721c24',
                border: '2px solid #f5c6cb',
              },
            },
          }}
        />
      </div>
    </Router>
  );
};

// Root App Component with Providers
const App = () => {
  return (
    <AuthProvider>
      <AccessibilityProvider>
        <AppContent />
      </AccessibilityProvider>
    </AuthProvider>
  );
};

export default App;
