# LexiLearn - AI Tutor for Dyslexic Students

A comprehensive web application designed to help dyslexic students learn and improve their reading, writing, and speaking skills through AI-powered assistance.

## Features

### 🎯 Core Features
- **AI Chat Bot**: Interactive chat with text, image, and voice input support
- **Dyslexia Detection Test**: Simple assessment to predict dyslexia likelihood
- **Real-time Error Detection**: ML-powered spelling, grammar, and phonetic error detection
- **Text-to-Speech**: Read aloud functionality for auditory support
- **Speech-to-Text**: Practice speaking exercises with real-time feedback
- **Handwriting Recognition**: Analyze handwritten text for corrections
- **Progress Tracking**: Interactive dashboard to monitor learning progress

### 🎨 Dyslexic-Friendly Design
- High contrast color schemes
- Dyslexia-friendly fonts (OpenDyslexic, Amiri Dyslexic, etc.)
- Increased line spacing and letter spacing
- Color-coded error highlighting
- Multi-language support

## Tech Stack

### Frontend
- **React** - Interactive, accessible UI
- **Tailwind CSS** - Responsive, accessible styling
- **Dynamic Font Loading** - Dyslexia-friendly fonts

### Backend
- **Python FastAPI** - RESTful API and WebSocket support
- **PostgreSQL** - User data and multilingual text storage
- **Redis** - ML model caching and session management

### AI/ML Models
- **Whisper** - Speech-to-text and text-to-speech
- **DistilBERT** - Text analysis and correction
- **TrOCR** - Handwriting recognition

## Project Structure

```
lexilearn/
├── frontend/          # React application
├── backend/           # FastAPI server
├── ml_models/         # AI/ML model implementations
├── database/          # Database schemas and migrations
└── docs/             # Documentation
```

## Quick Start

### Prerequisites
- Node.js 18+
- Python 3.9+
- PostgreSQL
- Redis

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd lexilearn
```

2. **Backend Setup**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3. **Frontend Setup**
```bash
cd frontend
npm install
```

4. **Database Setup**
```bash
# Install PostgreSQL and Redis (see DATABASE_SETUP.md for detailed instructions)
# PostgreSQL: https://www.postgresql.org/download/
# Redis: https://redis.io/download
```

5. **Run the Application**
```bash
# Backend (from backend directory)
uvicorn main:app --reload

# Frontend (from frontend directory)
npm start
```

## Environment Variables

Create `.env` files in both frontend and backend directories:

### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost/lexilearn
REDIS_URL=redis://localhost:6379
SECRET_KEY=your-secret-key
OPENAI_API_KEY=your-openai-api-key
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details
