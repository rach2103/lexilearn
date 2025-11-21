import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useAccessibility } from '../contexts/AccessibilityContext';
import { 
  FiUser, 
  FiEye, 
  FiType, 
  FiVolume2, 
  FiSave,
  FiRotateCcw,
  FiBell,
  FiShield
} from 'react-icons/fi';
import toast from 'react-hot-toast';

const Settings = () => {
  const { user, updateUser } = useAuth();
  const { 
    settings, 
    updateSettings, 
    resetSettings,
    toggleHighContrast,
    toggleTextToSpeech,
    increaseFontSize,
    decreaseFontSize,
    increaseLineSpacing,
    decreaseLineSpacing
  } = useAccessibility();

  const [isSaving, setIsSaving] = useState(false);
  const [userSettings, setUserSettings] = useState({
    fullName: user?.full_name || '',
    email: user?.email || '',
    preferredFont: settings.preferredFont,
    fontSize: settings.fontSize,
    lineSpacing: settings.lineSpacing,
    colorScheme: settings.colorScheme,
    language: settings.language,
    notifications: true,
    privacyMode: false
  });

  // Keep local form state in sync with context settings when they load or change.
  // This prevents the page from showing defaults while the context hydrates from localStorage
  useEffect(() => {
    setUserSettings(prev => ({
      fullName: user?.full_name || prev.fullName || '',
      email: user?.email || prev.email || '',
      preferredFont: settings.preferredFont,
      fontSize: settings.fontSize,
      lineSpacing: settings.lineSpacing,
      colorScheme: settings.colorScheme,
      language: settings.language,
      notifications: prev.notifications ?? true,
      privacyMode: prev.privacyMode ?? false
    }));
  }, [settings, user]);

  const fontOptions = [
    { value: 'OpenDyslexic', label: 'OpenDyslexic (Recommended)' },
    { value: 'OpenSans', label: 'Open Sans' },
    { value: 'Arial', label: 'Arial' },
    { value: 'Verdana', label: 'Verdana' },
    { value: 'ComicSans', label: 'Comic Sans MS' }
  ];



  const colorSchemeOptions = [
    { value: 'high_contrast', label: 'High Contrast' },
    { value: 'standard', label: 'Standard' },
    { value: 'dark', label: 'Dark Mode' },
    { value: 'sepia', label: 'Sepia' }
  ];

  const handleSave = async () => {
    setIsSaving(true);
    try {
      // Update user settings
      await updateUser({
        full_name: userSettings.fullName,
        preferred_font: userSettings.preferredFont,
        font_size: userSettings.fontSize,
        line_spacing: userSettings.lineSpacing,
        color_scheme: userSettings.colorScheme,
        language_preference: userSettings.language
      });

      // Update accessibility settings
      updateSettings({
        preferredFont: userSettings.preferredFont,
        fontSize: userSettings.fontSize,
        lineSpacing: userSettings.lineSpacing,
        colorScheme: userSettings.colorScheme,
        language: userSettings.language
      });

      toast.success('Settings saved successfully!');
    } catch (error) {
      console.error('Save settings error:', error);
      toast.error('Failed to save settings');
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    resetSettings();
    setUserSettings({
      fullName: user?.full_name || '',
      email: user?.email || '',
      preferredFont: 'OpenDyslexic',
      fontSize: 16,
      lineSpacing: 1.5,
      colorScheme: 'high_contrast',
      language: 'en',
      notifications: true,
      privacyMode: false
    });
    toast.success('Settings reset to defaults');
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-dyslexic-2xl font-bold text-gray-900 mb-2">
            Settings
          </h1>
          <p className="text-dyslexic-base text-gray-600">
            Customize your learning experience
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Settings */}
          <div className="lg:col-span-2 space-y-6">
            {/* Profile Settings */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h2 className="text-dyslexic-xl font-bold text-gray-900 mb-6 flex items-center">
                <FiUser className="mr-2" />
                Profile Settings
              </h2>
              <div className="space-y-4">
                <div>
                  <label className="form-label">Full Name</label>
                  <input
                    type="text"
                    value={userSettings.fullName}
                    onChange={(e) => setUserSettings(prev => ({ ...prev, fullName: e.target.value }))}
                    className="input-field"
                    placeholder="Enter your full name"
                  />
                </div>
                <div>
                  <label className="form-label">Email Address</label>
                  <input
                    type="email"
                    value={userSettings.email}
                    disabled
                    className="input-field bg-gray-50"
                    placeholder="Your email"
                  />
                  <p className="text-dyslexic-sm text-gray-500 mt-1">
                    Email cannot be changed
                  </p>
                </div>
              </div>
            </div>

            {/* Accessibility Settings */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h2 className="text-dyslexic-xl font-bold text-gray-900 mb-6 flex items-center">
                <FiEye className="mr-2" />
                Accessibility Settings
              </h2>
              <div className="space-y-6">
                {/* Font Settings */}
                <div>
                  <label className="form-label">Preferred Font</label>
                  <select
                    value={userSettings.preferredFont}
                    onChange={(e) => {
                      setUserSettings(prev => ({ ...prev, preferredFont: e.target.value }));
                      updateSettings({ preferredFont: e.target.value });
                    }}
                    className="input-field"
                  >
                    {fontOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Font Size */}
                <div>
                  <label className="form-label">Font Size</label>
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => {
                        const newSize = Math.max(userSettings.fontSize - 2, 12);
                        setUserSettings(prev => ({ ...prev, fontSize: newSize }));
                        updateSettings({ fontSize: newSize });
                      }}
                      className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                    >
                      <FiType size={16} />
                    </button>
                    <span className="text-dyslexic-base font-mono min-w-[3rem] text-center">
                      {userSettings.fontSize}px
                    </span>
                    <button
                      onClick={() => {
                        const newSize = Math.min(userSettings.fontSize + 2, 32);
                        setUserSettings(prev => ({ ...prev, fontSize: newSize }));
                        updateSettings({ fontSize: newSize });
                      }}
                      className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                    >
                      <FiType size={20} />
                    </button>
                  </div>
                </div>

                {/* Line Spacing */}
                <div>
                  <label className="form-label">Line Spacing</label>
                  <div className="flex items-center space-x-4">
                    <button
                      onClick={() => {
                        const newSpacing = Math.max(userSettings.lineSpacing - 0.1, 1.0);
                        setUserSettings(prev => ({ ...prev, lineSpacing: newSpacing }));
                        updateSettings({ lineSpacing: newSpacing });
                      }}
                      className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                    >
                      <FiType size={16} />
                    </button>
                    <span className="text-dyslexic-base font-mono min-w-[3rem] text-center">
                      {userSettings.lineSpacing.toFixed(1)}
                    </span>
                    <button
                      onClick={() => {
                        const newSpacing = Math.min(userSettings.lineSpacing + 0.1, 3.0);
                        setUserSettings(prev => ({ ...prev, lineSpacing: newSpacing }));
                        updateSettings({ lineSpacing: newSpacing });
                      }}
                      className="p-2 bg-gray-100 hover:bg-gray-200 rounded-lg"
                    >
                      <FiType size={20} />
                    </button>
                  </div>
                </div>

                {/* Color Scheme */}
                <div>
                  <label className="form-label">Color Scheme</label>
                  <select
                    value={userSettings.colorScheme}
                    onChange={(e) => {
                      setUserSettings(prev => ({ ...prev, colorScheme: e.target.value }));
                      updateSettings({ colorScheme: e.target.value });
                    }}
                    className="input-field"
                  >
                    {colorSchemeOptions.map(option => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>


              </div>
            </div>

            {/* Notification Settings */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h2 className="text-dyslexic-xl font-bold text-gray-900 mb-6 flex items-center">
                <FiBell className="mr-2" />
                Notification Settings
              </h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-dyslexic-base font-medium text-gray-900">Email Notifications</p>
                    <p className="text-dyslexic-sm text-gray-600">Receive updates and reminders</p>
                  </div>
                  <button
                    onClick={() => setUserSettings(prev => ({ ...prev, notifications: !prev.notifications }))}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      userSettings.notifications ? 'bg-primary-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        userSettings.notifications ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Quick Actions Sidebar */}
          <div className="space-y-6">
            {/* Quick Actions */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-dyslexic-lg font-semibold text-gray-900 mb-4">
                Quick Actions
              </h3>
              <div className="space-y-3">
                <button
                  onClick={toggleHighContrast}
                  className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center">
                    <FiEye className="mr-3 text-primary-600" size={18} />
                    <span className="text-dyslexic-base">Toggle High Contrast</span>
                  </div>
                </button>

                <button
                  onClick={toggleTextToSpeech}
                  className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center">
                    <FiVolume2 className="mr-3 text-primary-600" size={18} />
                    <span className="text-dyslexic-base">Toggle Text-to-Speech</span>
                  </div>
                </button>

                <button
                  onClick={handleReset}
                  className="w-full text-left p-3 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
                >
                  <div className="flex items-center">
                    <FiRotateCcw className="mr-3 text-warning-600" size={18} />
                    <span className="text-dyslexic-base">Reset to Defaults</span>
                  </div>
                </button>
              </div>
            </div>

            {/* Privacy Settings */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <h3 className="text-dyslexic-lg font-semibold text-gray-900 mb-4 flex items-center">
                <FiShield className="mr-2" />
                Privacy
              </h3>
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-dyslexic-base font-medium text-gray-900">Privacy Mode</p>
                    <p className="text-dyslexic-sm text-gray-600">Hide sensitive information</p>
                  </div>
                  <button
                    onClick={() => setUserSettings(prev => ({ ...prev, privacyMode: !prev.privacyMode }))}
                    className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                      userSettings.privacyMode ? 'bg-primary-600' : 'bg-gray-200'
                    }`}
                  >
                    <span
                      className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                        userSettings.privacyMode ? 'translate-x-6' : 'translate-x-1'
                      }`}
                    />
                  </button>
                </div>
              </div>
            </div>

            {/* Save Button */}
            <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
              <button
                onClick={handleSave}
                disabled={isSaving}
                className="btn-primary w-full flex justify-center items-center py-3 text-dyslexic-base font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isSaving ? (
                  <div className="flex items-center">
                    <div className="spinner mr-3"></div>
                    Saving...
                  </div>
                ) : (
                  <>
                    <FiSave className="mr-2" />
                    Save Settings
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
