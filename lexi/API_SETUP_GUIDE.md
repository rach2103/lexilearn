# LexiLearn API Setup Guide

This guide helps you configure speech processing APIs for LexiLearn. You can choose from several options based on your needs and budget.

## 🆓 Free Options (Recommended)

### 1. Hugging Face (Recommended)
**Best for**: Most users, good quality, generous free tier
**Cost**: Free with generous limits

#### Setup Steps:
1. Visit [Hugging Face Settings](https://huggingface.co/settings/tokens)
2. Create a new token
3. Add to `backend/.env`:
   ```env
   SPEECH_API_TYPE=huggingface
   HUGGINGFACE_TOKEN=your-token-here
   ```

#### Pros:
- ✅ Completely free
- ✅ High-quality models
- ✅ Good multilingual support
- ✅ Easy setup

#### Cons:
- ⚠️ Rate limits on free tier
- ⚠️ Requires internet connection

### 2. Local Whisper (Completely Free)
**Best for**: Privacy-conscious users, offline use
**Cost**: Free (runs on your computer)

#### Setup Steps:
1. Install dependencies: `pip install whisper TTS`
2. Add to `backend/.env`:
   ```env
   SPEECH_API_TYPE=local_whisper
   ```

#### Pros:
- ✅ Completely free
- ✅ Works offline
- ✅ No API limits
- ✅ Privacy (data stays on your machine)

#### Cons:
- ⚠️ Requires more computing power
- ⚠️ Slower processing
- ⚠️ Larger disk space needed

## 💰 Affordable Options

### 3. Google Cloud Speech API
**Best for**: Production use, high accuracy
**Cost**: Free tier + pay-as-you-go

#### Setup Steps:
1. Visit [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project
3. Enable Speech-to-Text and Text-to-Speech APIs
4. Create a service account and download credentials
5. Add to `backend/.env`:
   ```env
   SPEECH_API_TYPE=google
   GOOGLE_CLOUD_CREDENTIALS=path/to/your/credentials.json
   ```

#### Pros:
- ✅ Excellent quality
- ✅ Generous free tier (60 min STT, 4M chars TTS/month)
- ✅ Production-ready

#### Cons:
- ⚠️ Requires Google Cloud account
- ⚠️ Pay-as-you-go after free tier

### 4. Azure Cognitive Services
**Best for**: Enterprise users, Microsoft ecosystem
**Cost**: Free tier + pay-as-you-go

#### Setup Steps:
1. Visit [Azure Portal](https://portal.azure.com/)
2. Create a Speech resource
3. Get the key and region
4. Add to `backend/.env`:
   ```env
   SPEECH_API_TYPE=azure
   AZURE_SPEECH_KEY=your-key-here
   AZURE_SPEECH_REGION=your-region-here
   ```

#### Pros:
- ✅ High quality
- ✅ Good free tier (5 hours/month)
- ✅ Enterprise features

#### Cons:
- ⚠️ Requires Azure account
- ⚠️ Pay-as-you-go after free tier

## 💳 Paid Option

### 5. OpenAI (Original)
**Best for**: Users who already have OpenAI credits
**Cost**: Pay-per-use

#### Setup Steps:
1. Visit [OpenAI API Keys](https://platform.openai.com/api-keys)
2. Create an API key
3. Add to `backend/.env`:
   ```env
   SPEECH_API_TYPE=openai
   OPENAI_API_KEY=your-api-key-here
   ```

## 🔧 Quick Setup Commands

### For Hugging Face (Recommended):
```bash
# 1. Run setup script
python setup.py

# 2. Edit backend/.env
SPEECH_API_TYPE=huggingface
HUGGINGFACE_TOKEN=your-token-here

# 3. Start the application
cd backend && python -m uvicorn main:app --reload
cd frontend && npm start
```

### For Local Whisper:
```bash
# 1. Run setup script
python setup.py

# 2. Edit backend/.env
SPEECH_API_TYPE=local_whisper

# 3. Start the application
cd backend && python -m uvicorn main:app --reload
cd frontend && npm start
```

## 📊 Comparison Table

| API | Cost | Quality | Speed | Setup | Offline |
|-----|------|---------|-------|-------|---------|
| Hugging Face | Free | High | Fast | Easy | ❌ |
| Local Whisper | Free | High | Slow | Easy | ✅ |
| Google Cloud | Free tier | Very High | Fast | Medium | ❌ |
| Azure | Free tier | Very High | Fast | Medium | ❌ |
| OpenAI | Paid | Very High | Fast | Easy | ❌ |

## 🚀 Recommendation

**For most users**: Start with **Hugging Face** - it's free, high-quality, and easy to set up.

**For privacy/offline use**: Use **Local Whisper** - completely free and private.

**For production**: Consider **Google Cloud** or **Azure** for their reliability and generous free tiers.

## 🔄 Switching APIs

You can easily switch between APIs by changing the `SPEECH_API_TYPE` in your `backend/.env` file. The application will automatically use the appropriate implementation without any code changes.

## 🆘 Troubleshooting

### Common Issues:

1. **"No module named 'whisper'"**
   ```bash
   pip install openai-whisper
   ```

2. **"No module named 'TTS'"**
   ```bash
   pip install TTS
   ```

3. **Hugging Face token issues**
   - Make sure your token is valid
   - Check if you have the necessary permissions

4. **Local Whisper slow performance**
   - Consider using a smaller model: `whisper.load_model("tiny")`
   - Ensure you have enough RAM (4GB+ recommended)

### Getting Help:
- Check the [README.md](README.md) for general setup
- Review the [backend/requirements.txt](backend/requirements.txt) for dependencies
- Ensure all environment variables are set correctly in `backend/.env`
