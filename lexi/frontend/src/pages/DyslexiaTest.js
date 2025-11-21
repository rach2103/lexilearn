import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { 
  FiCheck, 
  FiX, 
  FiArrowRight, 
  FiArrowLeft, 
  FiClock, 
  FiAward,
  FiAlertTriangle,
  FiInfo,
  FiPlay,
  FiPause
} from 'react-icons/fi';
import toast from 'react-hot-toast';
import axios from 'axios';

const DyslexiaTest = () => {
  const { user } = useAuth();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [testStarted, setTestStarted] = useState(false);
  const [testCompleted, setTestCompleted] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [isTimerRunning, setIsTimerRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Enhanced 15-question dyslexia screening test
  const testQuestions = [
    {
      id: 1,
      question: 'Did you have difficulty learning to read as a child?',
      options: [
        { id: 'a', text: 'No, I learned easily' },
        { id: 'b', text: 'Some difficulty, but manageable' },
        { id: 'c', text: 'Yes, significant difficulty' },
        { id: 'd', text: 'Yes, extreme difficulty' }
      ],
      category: 'early_reading'
    },
    {
      id: 2,
      question: 'How do you find spelling words correctly?',
      options: [
        { id: 'a', text: 'Very easy for me' },
        { id: 'b', text: 'Manageable with effort' },
        { id: 'c', text: 'Quite challenging' },
        { id: 'd', text: 'Extremely difficult' }
      ],
      category: 'spelling'
    },
    {
      id: 3,
      question: 'Do you sometimes reverse letters or numbers when writing?',
      options: [
        { id: 'a', text: 'Never' },
        { id: 'b', text: 'Rarely' },
        { id: 'c', text: 'Sometimes' },
        { id: 'd', text: 'Frequently' }
      ],
      category: 'reversals'
    },
    {
      id: 4,
      question: 'How well can you sound out unfamiliar words?',
      options: [
        { id: 'a', text: 'Very well' },
        { id: 'b', text: 'With some difficulty' },
        { id: 'c', text: 'With great difficulty' },
        { id: 'd', text: 'Cannot do it' }
      ],
      category: 'phonics'
    },
    {
      id: 5,
      question: 'Do you have trouble remembering sequences (like phone numbers)?',
      options: [
        { id: 'a', text: 'No trouble at all' },
        { id: 'b', text: 'Some trouble' },
        { id: 'c', text: 'Significant trouble' },
        { id: 'd', text: 'Major difficulty' }
      ],
      category: 'memory'
    },
    {
      id: 6,
      question: 'How is your reading speed compared to others?',
      options: [
        { id: 'a', text: 'Faster than average' },
        { id: 'b', text: 'About average' },
        { id: 'c', text: 'Slower than average' },
        { id: 'd', text: 'Much slower' }
      ],
      category: 'reading_speed'
    },
    {
      id: 7,
      question: 'Do you have difficulty understanding what you read?',
      options: [
        { id: 'a', text: 'No difficulty' },
        { id: 'b', text: 'Sometimes struggle' },
        { id: 'c', text: 'Often struggle' },
        { id: 'd', text: 'Always struggle' }
      ],
      category: 'comprehension'
    },
    {
      id: 8,
      question: 'How do you feel about writing tasks?',
      options: [
        { id: 'a', text: 'Enjoy and find easy' },
        { id: 'b', text: 'Manageable' },
        { id: 'c', text: 'Find challenging' },
        { id: 'd', text: 'Avoid when possible' }
      ],
      category: 'writing'
    },
    {
      id: 9,
      question: 'Do you have trouble finding the right word when speaking?',
      options: [
        { id: 'a', text: 'Never' },
        { id: 'b', text: 'Sometimes' },
        { id: 'c', text: 'Often' },
        { id: 'd', text: 'Very often' }
      ],
      category: 'word_finding'
    },
    {
      id: 10,
      question: 'How well do you follow multi-step instructions?',
      options: [
        { id: 'a', text: 'Very well' },
        { id: 'b', text: 'Usually well' },
        { id: 'c', text: 'With difficulty' },
        { id: 'd', text: 'Very poorly' }
      ],
      category: 'instructions'
    },
    {
      id: 11,
      question: 'How organized are you with tasks and materials?',
      options: [
        { id: 'a', text: 'Very organized' },
        { id: 'b', text: 'Somewhat organized' },
        { id: 'c', text: 'Often disorganized' },
        { id: 'd', text: 'Very disorganized' }
      ],
      category: 'organization'
    },
    {
      id: 12,
      question: 'Is there a family history of reading or learning difficulties?',
      options: [
        { id: 'a', text: 'No family history' },
        { id: 'b', text: 'Possibly, not sure' },
        { id: 'c', text: 'Yes, some family members' },
        { id: 'd', text: 'Yes, multiple family members' }
      ],
      category: 'family_history'
    },
    {
      id: 13,
      question: 'How do you find math word problems?',
      options: [
        { id: 'a', text: 'Easy to understand' },
        { id: 'b', text: 'Sometimes confusing' },
        { id: 'c', text: 'Often confusing' },
        { id: 'd', text: 'Very difficult' }
      ],
      category: 'math'
    },
    {
      id: 14,
      question: 'Do you have trouble managing time and being punctual?',
      options: [
        { id: 'a', text: 'No trouble' },
        { id: 'b', text: 'Occasional trouble' },
        { id: 'c', text: 'Frequent trouble' },
        { id: 'd', text: 'Constant trouble' }
      ],
      category: 'time_management'
    },
    {
      id: 15,
      question: 'How has your reading/writing difficulty affected your confidence?',
      options: [
        { id: 'a', text: 'No impact on confidence' },
        { id: 'b', text: 'Minor impact' },
        { id: 'c', text: 'Significant impact' },
        { id: 'd', text: 'Major impact on self-esteem' }
      ],
      category: 'self_esteem'
    }
  ];

  // Timer effect
  useEffect(() => {
    let interval = null;
    if (isTimerRunning) {
      interval = setInterval(() => {
        setTimeElapsed(prev => prev + 1);
      }, 1000);
    }
    return () => clearInterval(interval);
  }, [isTimerRunning]);

  // Start test
  const startTest = () => {
    setTestStarted(true);
    setIsTimerRunning(true);
    toast.success('Test started! Take your time with each question.');
  };

  // Handle answer selection
  const handleAnswerSelect = (questionId, answerId) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: {
        selected: answerId,
        timestamp: Date.now(),
        timeSpent: timeElapsed
      }
    }));
  };

  // Navigate to next question
  const nextQuestion = () => {
    if (currentQuestion < testQuestions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    }
  };

  // Navigate to previous question
  const prevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(prev => prev - 1);
    }
  };

  // Submit test
  const submitTest = async () => {
    if (Object.keys(answers).length < testQuestions.length) {
      toast.error('Please answer all questions before submitting.');
      return;
    }

    setIsSubmitting(true);
    try {
      const testData = {
        test_type: 'screening',
        answers: answers,
        time_elapsed: timeElapsed,
        questions_answered: Object.keys(answers).length
      };

      const response = await axios.post('/api/dyslexia-test', testData);
      setResults(response.data);
      setTestCompleted(true);
      setIsTimerRunning(false);
      toast.success('Test completed! View your results below.');
    } catch (error) {
      console.error('Test submission error:', error);
      toast.error('Failed to submit test. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  // Calculate progress
  const progress = (Object.keys(answers).length / testQuestions.length) * 100;

  // Get current question
  const question = testQuestions[currentQuestion];
  const currentAnswer = answers[question?.id];

  // Format time
  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  if (!testStarted) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-8">
              <div className="mx-auto w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mb-4">
                <FiAward className="text-primary-600" size={32} />
              </div>
              <h1 className="text-dyslexic-2xl font-bold text-gray-900 mb-4">
                Dyslexia Screening Test
              </h1>
              <p className="text-dyslexic-base text-gray-600 max-w-2xl mx-auto">
                This screening test helps identify potential signs of dyslexia. 
                It's designed to be dyslexia-friendly and takes about 10-15 minutes to complete.
              </p>
            </div>

            <div className="bg-blue-50 rounded-lg p-6 mb-8">
              <h3 className="text-dyslexic-lg font-semibold text-blue-900 mb-4 flex items-center">
                <FiInfo className="mr-2" />
                What to Expect
              </h3>
              <ul className="text-dyslexic-sm text-blue-800 space-y-2">
                <li>• 15 questions covering different aspects of reading and writing</li>
                <li>• No time pressure - take as long as you need</li>
                <li>• Your answers are confidential and secure</li>
                <li>• Results provide personalized recommendations</li>
                <li>• This is a screening tool, not a diagnosis</li>
              </ul>
            </div>

            <div className="bg-yellow-50 rounded-lg p-6 mb-8">
              <h3 className="text-dyslexic-lg font-semibold text-yellow-900 mb-4 flex items-center">
                <FiAlertTriangle className="mr-2" />
                Important Note
              </h3>
              <p className="text-dyslexic-sm text-yellow-800">
                This test is for educational purposes only and should not replace professional assessment. 
                If you have concerns about dyslexia, please consult with a qualified professional.
              </p>
            </div>

            <div className="text-center">
              <button
                onClick={startTest}
                className="btn-primary text-dyslexic-lg px-8 py-4"
              >
                <FiPlay className="mr-2" />
                Start Test
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (testCompleted && results) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-3xl mx-auto">
          <div className="bg-white rounded-xl shadow-lg p-8">
            <div className="text-center mb-8">
              <div className={`mx-auto w-16 h-16 rounded-full flex items-center justify-center mb-4 ${
                results.risk_level === 'low' ? 'bg-success-100' :
                results.risk_level === 'mild' ? 'bg-blue-100' :
                results.risk_level === 'moderate' ? 'bg-warning-100' : 'bg-error-100'
              }`}>
                <FiAward className={
                  results.risk_level === 'low' ? 'text-success-600' :
                  results.risk_level === 'mild' ? 'text-blue-600' :
                  results.risk_level === 'moderate' ? 'text-warning-600' : 'text-error-600'
                } size={32} />
              </div>
              <h1 className="text-dyslexic-2xl font-bold text-gray-900 mb-4">
                Test Results
              </h1>
              <div className="text-dyslexic-lg text-gray-600 mb-6">
                Score: {results.score.toFixed(1)}%
              </div>
              <div className={`inline-block px-4 py-2 rounded-full text-white font-semibold ${
                results.risk_level === 'low' ? 'bg-success-600' :
                results.risk_level === 'mild' ? 'bg-blue-600' :
                results.risk_level === 'moderate' ? 'bg-warning-600' : 'bg-error-600'
              }`}>
                Risk Level: {results.risk_level.charAt(0).toUpperCase() + results.risk_level.slice(1)}
              </div>
            </div>

            {results.summary && (
              <div className="bg-blue-50 rounded-lg p-6 mb-6">
                <h3 className="text-dyslexic-lg font-semibold text-blue-900 mb-4">
                  Assessment Summary
                </h3>
                <p className="text-dyslexic-base text-blue-800">
                  {results.summary}
                </p>
              </div>
            )}

            <div className="bg-gray-50 rounded-lg p-6 mb-8">
              <h3 className="text-dyslexic-lg font-semibold text-gray-900 mb-4">
                Recommendations
              </h3>
              <ul className="text-dyslexic-base text-gray-700 space-y-3">
                {results.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start">
                    <span className="mr-3 text-primary-600">•</span>
                    <span>{rec}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="text-center space-y-4">
              <button
                onClick={() => window.location.reload()}
                className="btn-primary text-dyslexic-lg px-8 py-4"
              >
                Take Test Again
              </button>
              <div>
                <button
                  onClick={() => window.history.back()}
                  className="text-primary-600 hover:text-primary-500 text-dyslexic-base"
                >
                  Back to Dashboard
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-dyslexic-xl font-bold text-gray-900">
              Dyslexia Screening Test
            </h1>
            <p className="text-dyslexic-sm text-gray-600">
              Question {currentQuestion + 1} of {testQuestions.length}
            </p>
          </div>
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2 text-gray-600">
              <FiClock size={20} />
              <span className="text-dyslexic-base font-mono">{formatTime(timeElapsed)}</span>
            </div>
            <div className="w-32 bg-gray-200 rounded-full h-2">
              <div 
                className="bg-primary-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${progress}%` }}
              ></div>
            </div>
          </div>
        </div>
      </div>

      {/* Test Content */}
      <div className="flex-1 max-w-4xl mx-auto w-full p-6">
        <div className="bg-white rounded-xl shadow-lg p-8">
          {/* Question */}
          <div className="mb-8">
            <div className="flex items-center justify-between mb-4">
              <span className="text-dyslexic-sm text-gray-500">
                Question {question.id}
              </span>
              <span className="text-dyslexic-sm text-gray-500">
                {question.category.replace('_', ' ').toUpperCase()}
              </span>
            </div>
            
            <h2 className="text-dyslexic-xl font-semibold text-gray-900 mb-6">
              {question.question}
            </h2>

            {question.passage && (
              <div className="bg-gray-50 rounded-lg p-6 mb-6">
                <p className="text-dyslexic-base text-gray-700 leading-relaxed">
                  {question.passage}
                </p>
              </div>
            )}
          </div>

          {/* Options */}
          <div className="space-y-4 mb-8">
            {question.options.map((option) => (
              <button
                key={option.id}
                onClick={() => handleAnswerSelect(question.id, option.id)}
                className={`w-full text-left p-4 rounded-lg border-2 transition-all duration-200 ${
                  currentAnswer?.selected === option.id
                    ? 'border-primary-500 bg-primary-50 text-primary-900'
                    : 'border-gray-200 hover:border-gray-300 bg-white'
                }`}
              >
                <div className="flex items-center">
                  <div className={`w-6 h-6 rounded-full border-2 flex items-center justify-center mr-4 ${
                    currentAnswer?.selected === option.id
                      ? 'border-primary-500 bg-primary-500'
                      : 'border-gray-300'
                  }`}>
                    {currentAnswer?.selected === option.id && (
                      <FiCheck className="text-white" size={16} />
                    )}
                  </div>
                  <span className="text-dyslexic-base">{option.text}</span>
                </div>
              </button>
            ))}
          </div>

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <button
              onClick={prevQuestion}
              disabled={currentQuestion === 0}
              className="btn-secondary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <FiArrowLeft className="mr-2" />
              Previous
            </button>

            <div className="flex items-center space-x-4">
              {currentQuestion === testQuestions.length - 1 ? (
                <button
                  onClick={submitTest}
                  disabled={isSubmitting || Object.keys(answers).length < testQuestions.length}
                  className="btn-success flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {isSubmitting ? (
                    <>
                      <div className="spinner mr-2"></div>
                      Submitting...
                    </>
                  ) : (
                    <>
                      <FiCheck className="mr-2" />
                      Submit Test
                    </>
                  )}
                </button>
              ) : (
                <button
                  onClick={nextQuestion}
                  disabled={!currentAnswer}
                  className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Next
                  <FiArrowRight className="ml-2" />
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DyslexiaTest;
