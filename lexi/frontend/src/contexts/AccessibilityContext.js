import React, { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext';

const AccessibilityContext = createContext();

export const useAccessibility = () => {
  const context = useContext(AccessibilityContext);
  if (!context) {
    throw new Error('useAccessibility must be used within an AccessibilityProvider');
  }
  return context;
};

export const AccessibilityProvider = ({ children }) => {
  const { user } = useAuth();
  const [settings, setSettings] = useState({
    // Font settings
    preferredFont: 'OpenDyslexic',
    fontSize: 16,
    lineSpacing: 1.5,
    letterSpacing: 0.1,
    
    // Color settings
    colorScheme: 'high_contrast',
    highContrast: false,
    
    // Reading settings
    readingGuide: false,
    textToSpeech: false,
    speechRate: 1.0,
    
    // Visual settings
    reduceMotion: false,
    focusIndicator: true,
    largeCursor: false,
    
    // Language settings
    language: 'en',
    
    // Dyslexia-specific settings
    wordSpacing: 0.1,
    paragraphSpacing: 1.5,
    textAlignment: 'left',
    lineLength: 'medium', // short, medium, long
  });

  // Load settings from localStorage on mount or when user changes
  useEffect(() => {
    if (user?.email) {
      const storageKey = `accessibilitySettings_${user.email}`;
      const savedSettings = localStorage.getItem(storageKey);
      if (savedSettings) {
        try {
          const parsedSettings = JSON.parse(savedSettings);
          setSettings(prev => ({ ...prev, ...parsedSettings }));
        } catch (error) {
          console.error('Error loading accessibility settings:', error);
        }
      }
    }
  }, [user?.email]);

  // Save settings to localStorage whenever they change
  useEffect(() => {
    if (user?.email) {
      const storageKey = `accessibilitySettings_${user.email}`;
      localStorage.setItem(storageKey, JSON.stringify(settings));
    }
    
    // Apply settings to document
    applySettingsToDocument(settings);
  }, [settings, user?.email]);

  const applySettingsToDocument = (newSettings) => {
    const root = document.documentElement;
    
    // Apply font settings
    root.style.setProperty('--font-family', getFontFamily(newSettings.preferredFont));
    root.style.setProperty('--font-size', `${newSettings.fontSize}px`);
    root.style.setProperty('--line-height', newSettings.lineSpacing.toString());
    root.style.setProperty('--letter-spacing', `${newSettings.letterSpacing}em`);
    root.style.setProperty('--word-spacing', `${newSettings.wordSpacing}em`);
    
    // Apply color scheme
    document.body.classList.remove('high-contrast', 'standard', 'dark', 'sepia');
    if (newSettings.colorScheme) {
      const className = newSettings.colorScheme.replace('_', '-');
      document.body.classList.add(className);
    }
    
    // Apply motion settings
    if (newSettings.reduceMotion) {
      document.body.classList.add('reduce-motion');
    } else {
      document.body.classList.remove('reduce-motion');
    }
    
    // Apply focus indicator
    if (newSettings.focusIndicator) {
      document.body.classList.add('focus-indicator');
    } else {
      document.body.classList.remove('focus-indicator');
    }
    
    // Apply large cursor
    if (newSettings.largeCursor) {
      document.body.classList.add('large-cursor');
    } else {
      document.body.classList.remove('large-cursor');
    }
    
    // Apply language
    if (newSettings.language) {
      document.documentElement.lang = newSettings.language;
    }
  };

  const getFontFamily = (fontName) => {
    const fontMap = {
      'OpenDyslexic': 'OpenDyslexic, Arial, sans-serif',
      'OpenSans': 'Open Sans, Arial, sans-serif',
      'Amiri': 'Amiri, serif',
      'NotoSansDevanagari': 'Noto Sans Devanagari, sans-serif',
      'PTSans': 'PT Sans, sans-serif',
      'Arial': 'Arial, sans-serif',
      'Verdana': 'Verdana, sans-serif',
      'ComicSans': 'Comic Sans MS, cursive, sans-serif'
    };
    
    return fontMap[fontName] || fontMap['OpenDyslexic'];
  };

  const updateSettings = (newSettings) => {
    setSettings(prev => ({ ...prev, ...newSettings }));
  };

  const resetSettings = () => {
    const defaultSettings = {
      preferredFont: 'OpenDyslexic',
      fontSize: 16,
      lineSpacing: 1.5,
      letterSpacing: 0.1,
      colorScheme: 'high_contrast',
      highContrast: false,
      readingGuide: false,
      textToSpeech: false,
      speechRate: 1.0,
      reduceMotion: false,
      focusIndicator: true,
      largeCursor: false,
      language: 'en',
      wordSpacing: 0.1,
      paragraphSpacing: 1.5,
      textAlignment: 'left',
      lineLength: 'medium',
    };
    
    setSettings(defaultSettings);
  };

  const toggleHighContrast = () => {
    setSettings(prev => ({ ...prev, highContrast: !prev.highContrast }));
  };

  const toggleTextToSpeech = () => {
    setSettings(prev => ({ ...prev, textToSpeech: !prev.textToSpeech }));
  };

  const toggleReadingGuide = () => {
    setSettings(prev => ({ ...prev, readingGuide: !prev.readingGuide }));
  };

  const increaseFontSize = () => {
    setSettings(prev => ({ 
      ...prev, 
      fontSize: Math.min(prev.fontSize + 2, 32) 
    }));
  };

  const decreaseFontSize = () => {
    setSettings(prev => ({ 
      ...prev, 
      fontSize: Math.max(prev.fontSize - 2, 12) 
    }));
  };

  const increaseLineSpacing = () => {
    setSettings(prev => ({ 
      ...prev, 
      lineSpacing: Math.min(prev.lineSpacing + 0.1, 3.0) 
    }));
  };

  const decreaseLineSpacing = () => {
    setSettings(prev => ({ 
      ...prev, 
      lineSpacing: Math.max(prev.lineSpacing - 0.1, 1.0) 
    }));
  };

  const value = {
    settings,
    updateSettings,
    resetSettings,
    toggleHighContrast,
    toggleTextToSpeech,
    toggleReadingGuide,
    increaseFontSize,
    decreaseFontSize,
    increaseLineSpacing,
    decreaseLineSpacing,
    getFontFamily,
  };

  return (
    <AccessibilityContext.Provider value={value}>
      {children}
    </AccessibilityContext.Provider>
  );
};
