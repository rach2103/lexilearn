import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  FiSend, 
  FiMic, 
  FiMicOff, 
  FiCamera, 
  FiImage, 
  FiVolume2, 
  FiVolumeX,
  FiArrowUp,
  FiArrowDown,
  FiMessageCircle,
  FiEdit3,
  FiCheck,
  FiX
} from 'react-icons/fi';
import toast from 'react-hot-toast';
import axios from 'axios';
import ExerciseFeedback from '../components/ExerciseFeedback';

const ChatBot = () => {
  const { user } = useAuth();
  const settings = { language: 'en-US', textToSpeech: true }; // Mock settings
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [isReading, setIsReading] = useState(false);
  const [chatHistory, setChatHistory] = useState([]);
  const [showHistory, setShowHistory] = useState(false);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedDateMessages, setSelectedDateMessages] = useState([]);
  
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const fileInputRef = useRef(null);
  const audioRef = useRef(null);

  // Scroll functions
  const scrollToTop = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize with welcome message and load history
  useEffect(() => {
    const initializeChat = async () => {
      // Load chat history first
      await loadChatHistory();
      
      // Check if user cleared the screen
      const screenCleared = localStorage.getItem('chatScreenCleared') === 'true';
      
      if (screenCleared) {
        // Show only welcome message if screen was cleared
        setMessages([
          {
            id: 1,
            type: 'ai',
            content: `Hello ${user?.full_name || 'there'}! I'm your LexiLearn AI tutor. I can help you with reading, writing, and speaking exercises. You can type, speak, or upload images of your handwriting. Let's start learning!`,
            timestamp: new Date(),
            analysis: null
          }
        ]);
        return;
      }
      
      // Check if there's existing history
      const response = await axios.get('/api/chat/history');
      console.log('Initial history check:', response.data);
      
      const hasHistory = response.data && response.data.history_by_date && response.data.history_by_date.length > 0;
      
      if (!hasHistory) {
        // Only show welcome message if no history exists
        setMessages([
          {
            id: 1,
            type: 'ai',
            content: `Hello ${user?.full_name || 'there'}! I'm your LexiLearn AI tutor. I can help you with reading, writing, and speaking exercises. You can type, speak, or upload images of your handwriting. Let's start learning!`,
            timestamp: new Date(),
            analysis: null
          }
        ]);
      } else {
        // Restore messages from history
        const restoredMessages = [];
        let messageId = 1;
        
        response.data.history_by_date.forEach((dateGroup) => {
          dateGroup.messages.forEach((item) => {
            // Add user message
            restoredMessages.push({
              id: messageId++,
              type: 'user',
              content: item.user_message,
              timestamp: new Date(item.timestamp)
            });
            // Add AI response
            restoredMessages.push({
              id: messageId++,
              type: 'ai',
              content: item.bot_response,
              timestamp: new Date(item.timestamp)
            });
          });
        });
        
        console.log('Restored messages:', restoredMessages.length);
        setMessages(restoredMessages);
      }
    };
    
    initializeChat();
  }, [user]);

  // Load chat history for sidebar
  const loadChatHistory = async () => {
    try {
      const response = await axios.get('/api/chat/history');
      console.log('Chat history response:', response.data);
      
      if (response.data && response.data.history_by_date) {
        // Keep day-wise grouped format
        setChatHistory(response.data.history_by_date);
        console.log('Loaded chat history:', response.data.history_by_date.length, 'days');
      }
    } catch (error) {
      console.error('Failed to load chat history:', error);
    }
  };

  // Load specific date's messages
  const loadDateMessages = (dateGroup) => {
    const messages = [];
    let messageId = 1;
    
    dateGroup.messages.forEach((item) => {
      messages.push({
        id: messageId++,
        type: 'user',
        content: item.user_message,
        timestamp: new Date(item.timestamp)
      });
      messages.push({
        id: messageId++,
        type: 'ai',
        content: item.bot_response,
        timestamp: new Date(item.timestamp)
      });
    });
    
    setSelectedDate(dateGroup.date);
    setSelectedDateMessages(messages);
  };

  // Text analysis function
  const analyzeText = async (text) => {
    try {
      const response = await axios.post('/api/analyze-text', { text });
      return response.data;
    } catch (error) {
      console.error('Text analysis error:', error);
      // Return mock analysis for demo
      return {
        errors: [],
        corrected_text: text,
        confidence_score: 0.85,
        error_count: 0
      };
    }
  };

  // Text-to-speech function
  const speakText = async (text) => {
    try {
      setIsReading(true);
      const response = await axios.post('/api/text-to-speech', { text });
      
      if (response.data.success && response.data.audio_file_path) {
        const audio = new Audio(response.data.audio_file_path);
        audio.onended = () => setIsReading(false);
        audio.play();
      }
    } catch (error) {
      console.error('Text-to-speech error:', error);
      setIsReading(false);
      toast.error('Failed to read text aloud');
    }
  };

  // Speech-to-text function
  const startSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      
      recognition.continuous = false;
      recognition.interimResults = false;
      recognition.lang = settings.language || 'en-US';
      
      recognition.onstart = () => {
        setIsListening(true);
        toast.success('Listening... Speak now!');
      };
      
      recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInputText(transcript);
        setIsListening(false);
        toast.success('Speech captured!');
      };
      
      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
        toast.error('Speech recognition failed. Please try again.');
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognition.start();
    } else {
      toast.error('Speech recognition is not supported in your browser');
    }
  };

  // Handle file upload
  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      if (file.type.startsWith('image/')) {
        setSelectedFile(file);
        const url = URL.createObjectURL(file);
        setPreviewUrl(url);
      } else {
        toast.error('Please select an image file');
      }
    }
  };

  // Process handwriting recognition
  const processHandwriting = async () => {
    if (!selectedFile) return null;

    try {
      const formData = new FormData();
      formData.append('image_file', selectedFile);
      formData.append('language', settings.language || 'en');

      const response = await axios.post('/api/recognize-handwriting', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      if (response.data.success) {
        const recognizedText = response.data.recognized_text;
        setInputText(recognizedText);
        setCurrentAnalysis(response.data);
        toast.success('Handwriting recognized successfully!');
        return response.data;
      } else {
        toast.error('Failed to recognize handwriting');
        return null;
      }
    } catch (error) {
      console.error('Handwriting recognition error:', error);
      toast.error('Failed to process handwriting');
      return null;
    }
  };

  // Send message
  const sendMessage = async () => {
    if (!inputText.trim() && !selectedFile) return;

    // Clear the screen cleared flag when user sends a new message
    localStorage.removeItem('chatScreenCleared');

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputText,
      timestamp: new Date(),
      file: selectedFile,
      previewUrl: previewUrl
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    // If the user typed a simple greeting like "hi" or "hello", start a fresh conversation
    const greetingMatch = inputText && inputText.trim().toLowerCase().match(/^\s*(hi|hello)[\s!,.]*$/);
    const startNewConversation = () => {
      const separator = {
        id: Date.now(),
        type: 'system',
        content: '--- New Conversation ---',
        timestamp: new Date(),
        meta: { conversationStart: true }
      };

      const welcomeMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: `Hello ${user?.full_name || 'there'}! I'm your LexiLearn AI tutor. I can help you with reading, writing, and speaking exercises. You can type, speak, or upload images of your handwriting. Let's start learning!`,
        timestamp: new Date(),
        analysis: null
      };

      setMessages(prev => [...prev, separator, welcomeMessage]);
      setInputText('');
      setSelectedFile(null);
      setPreviewUrl(null);
      setCurrentAnalysis(null);
      setIsLoading(false);
    };

    if (greetingMatch && !selectedFile) {
      // Start a new conversation segment and do not send to backend
      startNewConversation();
      return;
    }

    try {
      let aiResponse = '';
      let analysis = null;
      let fullAIData = null;

      // Process handwriting if file is present
      let handwritingResult = null;
      if (selectedFile) {
        handwritingResult = await processHandwriting();
        aiResponse = generateAIResponse(inputText, null, selectedFile, handwritingResult);
      } else if (inputText.trim()) {
        // Send to backend AI tutor for intelligent response
        try {
          const response = await axios.post('/api/chat/message', {
            message: inputText
          });
          
          if (response.data) {
            const data = response.data;
            fullAIData = data;
            aiResponse = data.message || '';
            
            // Extract analysis if available
            if (data.analysis) {
              analysis = data.analysis;
            }
            
            // Add additional context from AI response
            if (data.encouragement) {
              aiResponse += `\n\n✨ ${data.encouragement}`;
            }
            
            // Add practice words if available
            if (data.practice_words && data.practice_words.length > 0) {
              aiResponse += `\n\n📝 **Practice Words:**\n`;
              data.practice_words.forEach((word, idx) => {
                aiResponse += `${idx + 1}. ${word}\n`;
              });
            }
            
            // Add instructions if available
            if (data.instructions && data.instructions.length > 0) {
              aiResponse += `\n\n📋 **Instructions:**\n${data.instructions.map(i => `• ${i}`).join('\n')}`;
            }
            
            // Add exercise evaluation feedback if available
            if (data.is_correct !== undefined) {
              const correctIcon = data.is_correct ? '✅' : '❌';
              aiResponse += `\n\n${correctIcon} **Result:** ${data.is_correct ? 'Correct!' : 'Let\'s try again'}`;
            }
            
            // Add error analysis if available
            if (data.analysis && data.analysis.errors && data.analysis.errors.length > 0) {
              aiResponse += `\n\n🔍 **Spelling/Grammar Opportunities:**\n`;
              data.analysis.errors.slice(0, 3).forEach((error, idx) => {
                aiResponse += `${idx + 1}. "${error.word}" → "${error.suggestion}"\n`;
              });
            }
            
            if (data.suggestions && data.suggestions.length > 0) {
              aiResponse += `\n\n💡 **Suggestions:**\n${data.suggestions.slice(0, 2).map(s => `• ${s}`).join('\n')}`;
            }
            
            if (data.tips && data.tips.length > 0) {
              aiResponse += `\n\n📚 **Tips:**\n${data.tips.slice(0, 2).map(t => `• ${t}`).join('\n')}`;
            }
            
            if (data.emotional_support) {
              aiResponse += `\n\n💪 ${data.emotional_support}`;
            }
          }
        } catch (error) {
          console.error('AI chat error:', error);
          // Fallback to local response generation
          analysis = await analyzeText(inputText);
          aiResponse = generateAIResponse(inputText, analysis, null, null);
        }
      }

      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: aiResponse,
        timestamp: new Date(),
        analysis: analysis,
        fullData: fullAIData
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Send message error:', error);
      toast.error('Failed to send message');
    } finally {
      setIsLoading(false);
      setInputText('');
      setSelectedFile(null);
      setPreviewUrl(null);
      setCurrentAnalysis(null);
    }
  };

  // Handle key press
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  // Generate exercise
  const generateExercise = async () => {
    try {
      setIsLoading(true);
      
      const response = await axios.get('/api/exercises/generate-random', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (response.data) {
        const exercise = response.data;
        
        // Create exercise message
        const exerciseMessage = {
          id: Date.now(),
          type: 'ai',
          content: formatExerciseMessage(exercise),
          timestamp: new Date(),
          exercise: exercise
        };
        
        setMessages(prev => [...prev, exerciseMessage]);
        toast.success('Exercise generated!');
      }
    } catch (error) {
      console.error('Exercise generation error:', error);
      toast.error('Failed to generate exercise');
    } finally {
      setIsLoading(false);
    }
  };
  
  // Format exercise for display
  const formatExerciseMessage = (exercise) => {
    let message = `🎯 **${exercise.skill_area.replace(/_/g, ' ').toUpperCase()} EXERCISE**\n\n`;
    message += `**Instructions:** ${exercise.instructions}\n\n`;
    
    // Handle different exercise structures
    if (exercise.exercises && exercise.exercises.length > 0) {
      message += `**Practice Items:**\n`;
      exercise.exercises.forEach((item, index) => {
        if (item.incomplete_word) {
          // Spelling pattern practice
          message += `${index + 1}. Complete: ${item.incomplete_word} (${item.pattern})\n`;
        } else if (item.sentence) {
          // Sentence completion
          message += `${index + 1}. ${item.sentence}\n`;
        } else if (item.word) {
          // General word exercise
          message += `${index + 1}. ${item.word}\n`;
        } else if (item.sounds) {
          // Sound blending
          message += `${index + 1}. Blend: ${item.sound_display || item.sounds.join('-')}\n`;
        } else if (item.letter) {
          // Letter-sound matching
          message += `${index + 1}. Letter: ${item.letter.toUpperCase()}\n`;
        } else if (item.target_word) {
          // Word building
          message += `${index + 1}. Build the word using: ${item.available_letters.join(', ')}\n`;
        }
      });
    } else if (exercise.words && exercise.words.length > 0) {
      message += `**Words to practice:**\n`;
      exercise.words.forEach((word, index) => {
        message += `${index + 1}. ${word}\n`;
      });
    } else if (exercise.word_bank) {
      message += `**Word Bank:** ${exercise.word_bank.join(', ')}\n\n`;
      if (exercise.requirements) {
        message += `**Requirements:**\n`;
        exercise.requirements.forEach(req => {
          message += `• ${req}\n`;
        });
      }
    } else if (exercise.passage) {
      message += `**Passage:**\n"${exercise.passage}"\n\n`;
      if (exercise.questions) {
        message += `**Questions:**\n`;
        exercise.questions.forEach((q, index) => {
          message += `${index + 1}. ${q.question}\n`;
        });
      }
    }
    
    message += `\n💡 **Difficulty:** ${exercise.difficulty?.complexity || 'simple'}`;
    if (exercise.time_limit) {
      message += `\n⏱️ **Time limit:** ${exercise.time_limit} seconds`;
    }
    
    return message;
  };

  // Clear current input
  const clearInput = () => {
    setInputText('');
    setSelectedFile(null);
    setPreviewUrl(null);
    setCurrentAnalysis(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Generate AI response based on input
  const generateAIResponse = (text, analysis, file, handwritingResult) => {
    if (!text && !file) {
      return "I'm ready to help you learn! You can type a message, speak to me, or upload an image of your handwriting.";
    }

    const textLower = text ? text.toLowerCase() : '';
    
    // Handle specific questions and topics
    if (textLower.includes('what') && (textLower.includes('dyslexia') || textLower.includes('dyslexic'))) {
      return "Dyslexia is a learning difference that affects reading, writing, and spelling. It's not related to intelligence - many successful people have dyslexia! I can help you practice reading, writing, and develop strategies that work best for your learning style.";
    }
    
    if (textLower.includes('how') && (textLower.includes('improve') || textLower.includes('better'))) {
      return "Great question! Here are some ways I can help you improve: 1) Practice reading with immediate feedback, 2) Work on spelling with visual and phonetic cues, 3) Break down complex words into smaller parts, 4) Use multi-sensory learning techniques. What specific area would you like to focus on?";
    }
    
    if (textLower.includes('read') && (textLower.includes('difficult') || textLower.includes('hard') || textLower.includes('struggle'))) {
      return "Reading challenges are common with dyslexia. Try these strategies: 1) Use your finger to track words, 2) Read aloud to engage multiple senses, 3) Take breaks when needed, 4) Use dyslexia-friendly fonts. Would you like to practice reading with me?";
    }
    
    if (textLower.includes('spell') && (textLower.includes('difficult') || textLower.includes('hard') || textLower.includes('wrong'))) {
      return "Spelling can be tricky! I can help by: 1) Breaking words into syllables, 2) Finding patterns and rules, 3) Using memory tricks, 4) Practicing frequently misspelled words. Try typing a word you find difficult and I'll help you with it!";
    }
    
    // Handle greetings with context
    const greetingWords = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening'];
    if (greetingWords.some(word => textLower.includes(word))) {
      return `Hello! I'm your AI learning assistant. I can see you wrote: "${text}". I'm here to help with reading, writing, spelling, and building confidence. What would you like to work on today?`;
    }
    
    // Handle questions about the AI
    if (textLower.includes('who are you') || textLower.includes('what are you') || textLower.includes('what can you do')) {
      return "I'm your AI tutor specialized in helping with dyslexia-friendly learning. I can analyze your writing, help with spelling and grammar, provide reading practice, recognize handwriting, and give personalized feedback. I'm designed to be patient, encouraging, and adaptive to your learning style!";
    }
    
    // Handle help requests with specific guidance
    const helpWords = ['help', 'assist', 'support', 'stuck', 'confused'];
    if (helpWords.some(word => textLower.includes(word))) {
      return `I can see you need help with: "${text}". Here's how I can assist: 1) Type any text for spelling/grammar check, 2) Ask me questions about reading or writing, 3) Upload handwriting images for recognition, 4) Practice with specific words or sentences. What specific challenge are you facing?`;
    }
    
    // Handle file uploads with educational feedback
    if (file && handwritingResult) {
      let response = `📝 **Handwriting Analysis Complete!**\n\n`;
      
      if (handwritingResult.recognized_text) {
        response += `**Recognized Text:** "${handwritingResult.recognized_text}"\n\n`;
        
        // Add educational feedback
        if (handwritingResult.educational_feedback) {
          const feedback = handwritingResult.educational_feedback;
          response += `**📊 Assessment:** ${feedback.overall_assessment}\n\n`;
          
          if (feedback.strengths && feedback.strengths.length > 0) {
            response += `**✅ Strengths:**\n`;
            feedback.strengths.forEach(strength => {
              response += `• ${strength}\n`;
            });
            response += `\n`;
          }
          
          if (feedback.areas_for_improvement && feedback.areas_for_improvement.length > 0) {
            response += `**🎯 Areas to Improve:**\n`;
            feedback.areas_for_improvement.forEach(area => {
              response += `• ${area}\n`;
            });
            response += `\n`;
          }
          
          if (feedback.specific_tips && feedback.specific_tips.length > 0) {
            response += `**💡 Helpful Tips:**\n`;
            feedback.specific_tips.slice(0, 3).forEach(tip => {
              response += `• ${tip}\n`;
            });
            response += `\n`;
          }
        }
        
        // Add character analysis feedback
        if (handwritingResult.educational_feedback && handwritingResult.educational_feedback.character_feedback) {
          const charFeedback = handwritingResult.educational_feedback.character_feedback;
          if (charFeedback.length > 0) {
            response += `**🔍 Character Analysis:**\n`;
            charFeedback.slice(0, 3).forEach((char) => {
              response += `**Character ${char.character_id}:**\n`;
              if (char.template_match) {
                response += `• Detected as '${char.template_match.letter}' (${Math.round(char.template_match.confidence * 100)}% confidence)\n`;
                response += `• ${char.template_match.reasoning}\n`;
              }
              if (char.issues.length > 0) {
                response += `• Issues: ${char.issues[0]}\n`;
              }
              if (char.suggestions.length > 0) {
                response += `• Tip: ${char.suggestions[0]}\n`;
              }
              response += `\n`;
            });
          }
        }
        
        // Add learning suggestions
        if (handwritingResult.learning_suggestions && handwritingResult.learning_suggestions.length > 0) {
          response += `**📚 Practice Suggestions:**\n`;
          handwritingResult.learning_suggestions.slice(0, 2).forEach(suggestion => {
            response += `• **${suggestion.title}**: ${suggestion.description}\n`;
          });
          response += `\n`;
        }
        
        // Add template matching summary
        if (handwritingResult.educational_feedback && handwritingResult.educational_feedback.template_matches) {
          const matches = handwritingResult.educational_feedback.template_matches;
          if (matches.length > 0) {
            response += `**🎯 Letter Recognition:**\n`;
            const uniqueLetters = [...new Set(matches.map(m => m.letter))];
            response += `Detected letters: ${uniqueLetters.join(', ')}\n\n`;
          }
        }
        
        response += `**Confidence Level:** ${Math.round((handwritingResult.confidence || 0) * 100)}%\n\n`;
        response += `Great job practicing your handwriting! Keep it up! 🌟`;
      } else {
        // Show specific image quality issues
        const charAnalysis = handwritingResult.character_analysis;
        if (charAnalysis && charAnalysis.characters && charAnalysis.characters.length > 0) {
          response += `I found ${charAnalysis.characters.length} character(s) but couldn't read them clearly.\n\n`;
          response += `**Character Detection Issues:**\n`;
          charAnalysis.characters.slice(0, 2).forEach((char, index) => {
            if (char.errors && char.errors.length > 0) {
              response += `• Character ${index + 1}: ${char.errors[0].description}\n`;
            }
          });
          response += `\n`;
        } else {
          response += `I had trouble detecting any characters in this image.\n\n`;
        }
        
        response += `**Try these improvements:**\n`;
        response += `• Ensure good lighting\n`;
        response += `• Write clearly with dark ink\n`;
        response += `• Avoid shadows or glare\n`;
        response += `• Take the photo straight on\n`;
        response += `• Make letters larger and more spaced out\n\n`;
        response += `Feel free to try again with another image!`;
      }
      
      return response;
    } else if (file) {
      return "I can see you've uploaded an image! I'll analyze any handwriting in it and provide educational feedback to help you improve.";
    }
    
    // Handle text analysis results with detailed feedback
    if (analysis && analysis.error_count > 0) {
      let response = `I analyzed your text: "${text}"\n\n`;
      response += `I found ${analysis.error_count} area${analysis.error_count > 1 ? 's' : ''} to improve:\n\n`;
      
      if (analysis.errors && analysis.errors.length > 0) {
        analysis.errors.forEach((error, index) => {
          const suggestion = error.suggestion || error.message || 'Consider reviewing this part';
          response += `${index + 1}. "${error.word || 'Word'}": ${suggestion}\n`;
        });
      }
      
      if (analysis.corrected_text && analysis.corrected_text !== text) {
        response += `\n✅ Corrected version: "${analysis.corrected_text}"\n`;
      }
      
      response += `\n💪 Keep practicing! Your confidence score is ${Math.round((analysis.confidence_score || 0.8) * 100)}%. Each practice session helps you improve!`;
      return response;
    }
    
    // Handle good text with contextual encouragement
    if (text && text.trim().length > 0) {
      const wordCount = text.split(' ').length;
      let response = `Great work on your text: "${text}"\n\n`;
      
      if (wordCount > 20) {
        response += `Impressive! You wrote ${wordCount} words. That shows excellent effort and focus. `;
      } else if (wordCount > 10) {
        response += `Nice job! ${wordCount} words is a solid piece of writing. `;
      } else {
        response += `Good start with ${wordCount} word${wordCount > 1 ? 's' : ''}! `;
      }
      
      response += "Your text looks clean with no major errors. Would you like to try writing something longer, or do you have any questions about reading or writing?";
      return response;
    }
    
    // Default contextual response
    return "I'm here to help with your learning journey! Try typing a sentence, asking a question about reading or writing, or uploading an image of your handwriting. What would you like to practice today?";
  };

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* Date Messages Modal */}
      {selectedDate && (
        <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center" onClick={() => setSelectedDate(null)}>
          <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full max-h-[80vh] overflow-hidden" onClick={(e) => e.stopPropagation()}>
            <div className="bg-primary-600 text-white px-6 py-4 flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold">Chat History</h3>
                <p className="text-sm text-primary-100">{selectedDate}</p>
              </div>
              <button onClick={() => setSelectedDate(null)} className="text-white hover:text-gray-200">
                <FiX size={24} />
              </button>
            </div>
            <div className="p-6 overflow-y-auto max-h-[calc(80vh-80px)] space-y-4">
              {selectedDateMessages.map((message) => (
                <div key={message.id} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-lg rounded-lg p-4 ${message.type === 'user' ? 'bg-primary-600 text-white' : 'bg-gray-100 text-gray-900'}`}>
                    <div className="text-sm whitespace-pre-wrap">{message.content}</div>
                    <div className={`text-xs mt-2 ${message.type === 'user' ? 'text-primary-100' : 'text-gray-500'}`}>
                      {message.timestamp.toLocaleTimeString()}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* History Sidebar */}
      <div className={`${showHistory ? 'w-64' : 'w-0'} transition-all duration-300 bg-white border-r border-gray-200 overflow-hidden`}>
        <div className="p-4">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-semibold text-gray-900">Chat History</h3>
            <button onClick={() => setShowHistory(false)} className="text-gray-500 hover:text-gray-700">
              <FiX size={20} />
            </button>
          </div>
          <div className="space-y-2 max-h-[calc(100vh-120px)] overflow-y-auto">
            {chatHistory.map((dateGroup) => (
              <div 
                key={dateGroup.date} 
                onClick={() => loadDateMessages(dateGroup)}
                className="p-3 bg-gray-50 rounded-lg hover:bg-primary-50 cursor-pointer border border-gray-200 hover:border-primary-300 transition-all"
              >
                <div className="flex items-center justify-between">
                  <p className="text-sm font-semibold text-gray-800">{dateGroup.date}</p>
                  <span className="text-xs bg-primary-100 text-primary-700 px-2 py-1 rounded-full">
                    {dateGroup.message_count}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {dateGroup.messages[0]?.user_message.substring(0, 40)}...
                </p>
              </div>
            ))}
            {chatHistory.length === 0 && (
              <p className="text-sm text-gray-500 text-center py-4">No history yet</p>
            )}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowHistory(!showHistory)}
                className="p-2 text-gray-500 hover:text-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
                aria-label="Toggle history"
              >
                <FiMessageCircle size={20} />
              </button>
              <div>
                <h1 className="text-dyslexic-xl font-bold text-gray-900">
                  AI Chat Tutor
                </h1>
                <p className="text-dyslexic-sm text-gray-600">
                  Practice reading, writing, and speaking with AI assistance
                </p>
                <div className="text-xs text-gray-500 mt-1">
                  {messages.length > 1 ? `${messages.length - 1} messages exchanged` : 'Start your conversation'}
                </div>
              </div>
            </div>
            <div className="flex items-center space-x-2">
            <button
              onClick={() => {
                setMessages([{
                  id: 1,
                  type: 'ai',
                  content: `Hello ${user?.full_name || 'there'}! I'm your LexiLearn AI tutor. I can help you with reading, writing, and speaking exercises. You can type, speak, or upload images of your handwriting. Let's start learning!`,
                  timestamp: new Date(),
                  analysis: null
                }]);
                localStorage.setItem('chatScreenCleared', 'true');
                toast.success('Screen cleared! Your history is still saved.');
              }}
              className="p-2 text-gray-500 hover:text-red-600 focus:outline-none focus:ring-2 focus:ring-red-500 rounded-lg"
              aria-label="Clear screen"
              title="Clear screen (history is saved)"
            >
              <FiX size={20} />
            </button>
            <button
              onClick={() => settings.textToSpeech && speakText("Welcome to LexiLearn AI Chat")}
              className="p-2 text-gray-500 hover:text-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg"
              aria-label="Read welcome message"
            >
              {isReading ? <FiVolumeX size={20} /> : <FiVolume2 size={20} />}
            </button>
            </div>
          </div>
        </div>

        {/* Chat Container */}
        <div className="flex-1 flex flex-col max-w-4xl mx-auto w-full">
        {/* Messages */}
        <div ref={messagesContainerRef} className="flex-1 overflow-y-auto p-6 space-y-4 relative">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-3xl rounded-lg p-4 ${
                  message.type === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-white border border-gray-200'
                }`}
              >
                {/* File preview */}
                {message.file && message.previewUrl && (
                  <div className="mb-3">
                    <img
                      src={message.previewUrl}
                      alt="Uploaded handwriting"
                      className="max-w-full h-auto rounded border"
                    />
                  </div>
                )}

                {/* Message content */}
                <div className="text-dyslexic-base whitespace-pre-wrap">
                  {message.content}
                </div>

                {/* Analysis results */}
                {message.analysis && message.analysis.errors && message.analysis.errors.length > 0 && (
                  <div className="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <h4 className="text-dyslexic-sm font-semibold text-yellow-800 mb-2">
                      Corrections Found:
                    </h4>
                    <ul className="text-dyslexic-sm text-yellow-700 space-y-1">
                      {message.analysis.errors.map((error, index) => (
                        <li key={index} className="flex items-start">
                          <span className="mr-2">•</span>
                          <span>
                            <strong>{error.word || 'Text'}</strong>: {error.suggestion}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Exercise feedback component when the backend provides structured feedback */}
                {message.fullData && message.fullData.is_correct !== undefined && (
                  <div className="mt-3">
                    <ExerciseFeedback
                      data={message.fullData}
                      isCorrect={message.fullData.is_correct}
                    />
                  </div>
                )}

                {/* Timestamp */}
                <div className={`text-xs mt-2 ${
                  message.type === 'user' ? 'text-primary-100' : 'text-gray-500'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </div>
              </div>
            </div>
          ))}

          {/* Loading indicator */}
          {isLoading && (
            <div className="flex justify-start">
              <div className="bg-white border border-gray-200 rounded-lg p-4">
                <div className="flex items-center space-x-2">
                  <div className="spinner"></div>
                  <span className="text-dyslexic-sm text-gray-600">AI is thinking...</span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />

          {/* Scroll buttons */}
          {messages.length > 3 && (
            <div className="fixed bottom-32 right-8 flex flex-col space-y-2 z-10">
              <button
                onClick={scrollToTop}
                className="p-3 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                aria-label="Scroll to top"
                title="Scroll to top"
              >
                <FiArrowUp size={20} />
              </button>
              <button
                onClick={scrollToBottom}
                className="p-3 bg-primary-600 text-white rounded-full shadow-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 transition-all"
                aria-label="Scroll to bottom"
                title="Scroll to bottom"
              >
                <FiArrowDown size={20} />
              </button>
            </div>
          )}
        </div>

        {/* Current Analysis */}
        {currentAnalysis && (
          <div className="bg-blue-50 border-t border-blue-200 p-4">
            <div className="flex items-center justify-between">
              <h3 className="text-dyslexic-lg font-semibold text-blue-900">
                Text Analysis
              </h3>
              <button
                onClick={() => setCurrentAnalysis(null)}
                className="text-blue-600 hover:text-blue-800"
              >
                <FiX size={20} />
              </button>
            </div>
            <div className="mt-2 text-dyslexic-sm text-blue-800">
              <p>Confidence: {Math.round(currentAnalysis.confidence_score * 100)}%</p>
              {currentAnalysis.error_count > 0 && (
                <p>Errors found: {currentAnalysis.error_count}</p>
              )}
            </div>
          </div>
        )}

        {/* Input Area */}
        <div className="bg-white border-t border-gray-200 p-6">
          <div className="space-y-4">
            {/* File upload preview */}
            {selectedFile && (
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <FiImage className="text-gray-500" size={20} />
                    <span className="text-dyslexic-sm text-gray-700">
                      {selectedFile.name}
                    </span>
                  </div>
                  <button
                    onClick={clearInput}
                    className="text-gray-500 hover:text-red-600"
                  >
                    <FiX size={20} />
                  </button>
                </div>
                {previewUrl && (
                  <img
                    src={previewUrl}
                    alt="Preview"
                    className="mt-2 max-w-xs h-auto rounded border"
                  />
                )}
              </div>
            )}

            {/* Text input */}
            <div className="flex items-end space-x-2">
              <div className="flex-1">
                <textarea
                  value={inputText}
                  onChange={(e) => setInputText(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message, or upload handwriting..."
                  className="input-field resize-none"
                  rows={3}
                  disabled={isLoading}
                />
              </div>

              {/* Action buttons */}
              <div className="flex flex-col space-y-2">
                {/* File upload */}
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-3 text-gray-500 hover:text-primary-600 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg border border-gray-300 hover:border-primary-300"
                  aria-label="Upload handwriting image"
                  disabled={isLoading}
                >
                  <FiCamera size={20} />
                </button>

                {/* Voice input */}
                <button
                  onClick={startSpeechRecognition}
                  className={`p-3 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg border ${
                    isListening
                      ? 'text-red-600 border-red-300 bg-red-50'
                      : 'text-gray-500 hover:text-primary-600 border-gray-300 hover:border-primary-300'
                  }`}
                  aria-label={isListening ? 'Stop listening' : 'Start voice input'}
                  disabled={isLoading}
                >
                  {isListening ? <FiMicOff size={20} /> : <FiMic size={20} />}
                </button>

                {/* Exercise Generator */}
                <button
                  onClick={generateExercise}
                  className="p-3 text-purple-600 hover:text-purple-700 focus:outline-none focus:ring-2 focus:ring-purple-500 rounded-lg border border-purple-300 hover:border-purple-400 bg-purple-50 hover:bg-purple-100"
                  aria-label="Generate practice exercise"
                  disabled={isLoading}
                >
                  <FiEdit3 size={20} />
                </button>

                {/* Send button */}
                <button
                  onClick={sendMessage}
                  disabled={isLoading || (!inputText.trim() && !selectedFile)}
                  className="p-3 bg-primary-600 text-white hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed"
                  aria-label="Send message"
                >
                  <FiSend size={20} />
                </button>
              </div>
            </div>

            {/* Hidden file input */}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              onChange={handleFileUpload}
              className="hidden"
            />
          </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;
