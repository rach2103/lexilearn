import React from 'react';
import { FiCheck, FiX, FiAlertCircle } from 'react-icons/fi';

/**
 * ExerciseFeedback Component
 * Displays exercise evaluation results with visual indicators
 */
const ExerciseFeedback = ({ data, isCorrect }) => {
  if (!data || isCorrect === undefined) {
    return null;
  }

  // Attempt to resolve a 'correct word' from common field names or nested item data
  const resolvedCorrect = (() => {
    if (!data) return '';
    const candidates = [
      'correct_word',
      'correctWord',
      'correct',
      'correct_answer',
      'correctAnswer',
      'answer',
      'expected_word',
      'expectedWord',
      'expected'
    ];

    for (const key of candidates) {
      if (data[key]) return data[key];
    }

    // Check common nested shapes (exercise item payloads)
    if (data.item) {
      if (data.item.answer) return data.item.answer;
      if (data.item.correct) return data.item.correct;
      if (data.item.expectedWord) return data.item.expectedWord;
      if (data.item.expected_word) return data.item.expected_word;
      if (data.item.word) return data.item.word;
      if (data.item.target_word) return data.item.target_word;
    }

    // Sometimes the exercise object itself contains an exercises array with answers
    if (Array.isArray(data.exercises) && data.exercises.length > 0) {
      const first = data.exercises[0];
      if (first.answer) return first.answer;
      if (first.correct) return first.correct;
      if (first.word) return first.word;
      if (first.target_word) return first.target_word;
    }

    return '';
  })();

  const isPartialCredit = false; // No longer using scores

  return (
    <div className={`mt-4 p-4 rounded-lg border-2 ${
      isCorrect 
        ? 'bg-green-50 border-green-300' 
        : isPartialCredit
        ? 'bg-yellow-50 border-yellow-300'
        : 'bg-red-50 border-red-300'
    }`}>
      {/* Result Header */}
      <div className="flex items-center space-x-3 mb-3">
        <div className={`flex-shrink-0 ${
          isCorrect 
            ? 'text-green-600' 
            : isPartialCredit
            ? 'text-yellow-600'
            : 'text-red-600'
        }`}>
          {isCorrect ? (
            <FiCheck size={24} className="font-bold" />
          ) : isPartialCredit ? (
            <FiAlertCircle size={24} />
          ) : (
            <FiX size={24} className="font-bold" />
          )}
        </div>
        <div>
          <h3 className={`text-dyslexic-lg font-bold ${
            isCorrect 
              ? 'text-green-800' 
              : isPartialCredit
              ? 'text-yellow-800'
              : 'text-red-800'
          }`}>
            {isCorrect ? '🌟 Excellent!' : isPartialCredit ? '⚠️ Good Effort!' : '❌ Not Quite Right'}
          </h3>
          <p className={`text-dyslexic-sm ${
            isCorrect 
              ? 'text-green-700' 
              : 'text-red-700'
          }`}>
            {isCorrect 
              ? 'You got it right!' 
              : 'Let\'s try again'}
          </p>
        </div>
      </div>



      {/* Feedback Message */}
      {data.message && (
        <div className={`text-dyslexic-base mb-3 p-3 rounded bg-white bg-opacity-50 ${
          isCorrect 
            ? 'text-green-800' 
            : isPartialCredit
            ? 'text-yellow-800'
            : 'text-red-800'
        }`}>
          {data.message}
        </div>
      )}

      {/* Show the resolved correct word when available and the user was incorrect */}
      {resolvedCorrect && !isCorrect && (
        <div className={`text-dyslexic-base mb-3 p-3 rounded bg-white bg-opacity-50 ${
          'text-red-800'
        }`}>
          <strong>📚 The correct word is:</strong> {resolvedCorrect}
        </div>
      )}

      {/* Suggestions */}
      {data.suggestions && data.suggestions.length > 0 && (
        <div className="mb-3">
          <h4 className={`text-dyslexic-sm font-semibold mb-2 ${
            isCorrect 
              ? 'text-green-800' 
              : isPartialCredit
              ? 'text-yellow-800'
              : 'text-red-800'
          }`}>
            💡 Next Steps:
          </h4>
          <ul className={`text-dyslexic-sm space-y-1 ${
            isCorrect 
              ? 'text-green-700' 
              : isPartialCredit
              ? 'text-yellow-700'
              : 'text-red-700'
          }`}>
            {data.suggestions.slice(0, 3).map((suggestion, idx) => (
              <li key={idx} className="flex items-start">
                <span className="mr-2">→</span>
                <span>{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tips */}
      {data.tips && data.tips.length > 0 && (
        <div>
          <h4 className={`text-dyslexic-sm font-semibold mb-2 ${
            isCorrect 
              ? 'text-green-800' 
              : isPartialCredit
              ? 'text-yellow-800'
              : 'text-red-800'
          }`}>
            📚 Learning Tips:
          </h4>
          <ul className={`text-dyslexic-sm space-y-1 ${
            isCorrect 
              ? 'text-green-700' 
              : isPartialCredit
              ? 'text-yellow-700'
              : 'text-red-700'
          }`}>
            {data.tips.slice(0, 2).map((tip, idx) => (
              <li key={idx} className="flex items-start">
                <span className="mr-2">•</span>
                <span>{tip}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ExerciseFeedback;
