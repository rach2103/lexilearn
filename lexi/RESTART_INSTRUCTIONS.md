# Restart Instructions

## Backend Changes Made
Updated `backend/ml_models/ai_tutor.py` to fix word request detection:
- Enhanced intent detection for "give me different words", "more words", etc.
- Added logic to clear active exercises when new word requests are made
- Added debug logging to track intent detection

## How to Apply Changes

### Windows:
1. Stop the current backend server (Ctrl+C in the terminal running it)
2. Navigate to backend directory:
   ```
   cd c:\Users\rachana nanjundaiah\Downloads\lexi\lexi\lexi\backend
   ```
3. Restart the server:
   ```
   python main.py
   ```

### Or use the start-dev.bat:
1. Stop all running servers (Ctrl+C)
2. Navigate to project root:
   ```
   cd c:\Users\rachana nanjundaiah\Downloads\lexi\lexi\lexi
   ```
3. Run:
   ```
   start-dev.bat
   ```

## What to Test After Restart:
1. Say "give me 5 words to practice" → Should get 5 words
2. Say "give me different words" → Should get NEW 5 words (not treat it as exercise response)
3. Say "more words" → Should get NEW words
4. Say "other words" → Should get NEW words

## Expected Behavior:
- Any request for different/more/other/new words should clear the previous exercise
- System should generate fresh word list
- Should NOT treat word requests as exercise responses
