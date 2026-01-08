import React, { createContext, useContext, useState, useEffect } from 'react';

const PrivacyContext = createContext();

export const usePrivacy = () => {
  const context = useContext(PrivacyContext);
  if (!context) {
    throw new Error('usePrivacy must be used within a PrivacyProvider');
  }
  return context;
};

export const PrivacyProvider = ({ children }) => {
  const [privacyMode, setPrivacyMode] = useState(false);

  // Load privacy mode from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem('privacyMode');
    if (saved) {
      setPrivacyMode(JSON.parse(saved));
    }
  }, []);

  // Save privacy mode to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('privacyMode', JSON.stringify(privacyMode));
  }, [privacyMode]);

  const togglePrivacyMode = () => {
    setPrivacyMode(prev => !prev);
  };

  const maskText = (text, showLength = 3) => {
    if (!privacyMode || !text) return text;
    if (text.length <= showLength) return '*'.repeat(text.length);
    return text.substring(0, showLength) + '*'.repeat(text.length - showLength);
  };

  const maskEmail = (email) => {
    if (!privacyMode || !email) return email;
    const [username, domain] = email.split('@');
    if (!domain) return maskText(email);
    return maskText(username, 2) + '@' + maskText(domain, 2);
  };

  return (
    <PrivacyContext.Provider value={{
      privacyMode,
      setPrivacyMode,
      togglePrivacyMode,
      maskText,
      maskEmail
    }}>
      {children}
    </PrivacyContext.Provider>
  );
};