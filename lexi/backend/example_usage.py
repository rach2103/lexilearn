#!/usr/bin/env python3
"""
Example usage of different speech processing APIs in LexiLearn
This script demonstrates how to use the alternative speech processors.
"""

import asyncio
import tempfile
import os
from ml_models.speech_processing_alternative import SpeechProcessorAlternative

async def test_speech_apis():
    """Test different speech processing APIs"""
    
    # Test text for TTS
    test_text = "Hello! This is a test of the speech processing system."
    
    # Test audio file (you would need to provide an actual audio file)
    test_audio_path = "test_audio.wav"  # Replace with actual audio file
    
    print("🎤 Testing Speech Processing APIs")
    print("=" * 50)
    
    # Test different API types
    api_types = ["huggingface", "local_whisper", "google", "azure"]
    
    for api_type in api_types:
        print(f"\n🔧 Testing {api_type.upper()} API:")
        print("-" * 30)
        
        try:
            # Initialize processor
            processor = SpeechProcessorAlternative(api_type=api_type)
            
            # Test Text-to-Speech
            print("📢 Testing Text-to-Speech...")
            tts_result = await processor.text_to_speech(test_text)
            
            if tts_result["success"]:
                print(f"✅ TTS Success: Audio saved to {tts_result['audio_file_path']}")
                # Clean up temporary file
                if os.path.exists(tts_result['audio_file_path']):
                    os.unlink(tts_result['audio_file_path'])
            else:
                print(f"❌ TTS Failed: {tts_result['error']}")
            
            # Test Speech-to-Text (if audio file exists)
            if os.path.exists(test_audio_path):
                print("🎧 Testing Speech-to-Text...")
                stt_result = await processor.speech_to_text(test_audio_path)
                
                if stt_result["success"]:
                    print(f"✅ STT Success: '{stt_result['text']}'")
                else:
                    print(f"❌ STT Failed: {stt_result['error']}")
            else:
                print("⚠️  Skipping STT test (no audio file provided)")
            
            # Test Speech Analysis
            if os.path.exists(test_audio_path):
                print("🔍 Testing Speech Analysis...")
                analysis_result = await processor.analyze_speech_errors(
                    test_audio_path, 
                    expected_text="Hello this is a test"
                )
                
                if analysis_result["success"]:
                    print(f"✅ Analysis Success: {analysis_result['accuracy']}% accuracy")
                    print(f"   Fluency Score: {analysis_result['fluency_score']}%")
                    if analysis_result['errors']:
                        print(f"   Errors found: {len(analysis_result['errors'])}")
                else:
                    print(f"❌ Analysis Failed: {analysis_result['error']}")
            
        except Exception as e:
            print(f"❌ {api_type.upper()} API Error: {str(e)}")
        
        print()

async def test_specific_api(api_type="huggingface"):
    """Test a specific API type"""
    print(f"🎯 Testing {api_type.upper()} API specifically")
    print("=" * 40)
    
    try:
        processor = SpeechProcessorAlternative(api_type=api_type)
        
        # Test TTS
        test_text = "Welcome to LexiLearn! This is an AI tutor for dyslexic students."
        print(f"📢 Converting text to speech: '{test_text}'")
        
        tts_result = await processor.text_to_speech(test_text)
        
        if tts_result["success"]:
            print(f"✅ Success! Audio file: {tts_result['audio_file_path']}")
            
            # Play the audio (if possible)
            try:
                import pygame
                pygame.mixer.init()
                pygame.mixer.music.load(tts_result['audio_file_path'])
                pygame.mixer.music.play()
                
                # Wait for audio to finish
                while pygame.mixer.music.get_busy():
                    await asyncio.sleep(0.1)
                
                pygame.mixer.quit()
            except ImportError:
                print("💡 Install pygame to play audio: pip install pygame")
            
            # Clean up
            if os.path.exists(tts_result['audio_file_path']):
                os.unlink(tts_result['audio_file_path'])
        else:
            print(f"❌ Failed: {tts_result['error']}")
    
    except Exception as e:
        print(f"❌ Error: {str(e)}")

def create_test_audio():
    """Create a simple test audio file for testing"""
    try:
        import numpy as np
        import wave
        
        # Create a simple sine wave
        sample_rate = 16000
        duration = 3  # seconds
        frequency = 440  # Hz (A note)
        
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        audio_data = np.sin(2 * np.pi * frequency * t) * 0.3
        
        # Convert to 16-bit integers
        audio_data = (audio_data * 32767).astype(np.int16)
        
        # Save as WAV file
        with wave.open("test_audio.wav", "w") as wav_file:
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        print("✅ Created test_audio.wav for testing")
        return True
    
    except ImportError:
        print("⚠️  numpy not available, skipping test audio creation")
        return False
    except Exception as e:
        print(f"❌ Failed to create test audio: {e}")
        return False

if __name__ == "__main__":
    print("🚀 LexiLearn Speech API Testing")
    print("=" * 50)
    
    # Create test audio if possible
    create_test_audio()
    
    # Test specific API (change this to test different APIs)
    api_to_test = "huggingface"  # Options: "huggingface", "local_whisper", "google", "azure"
    
    print(f"\n🎯 Testing {api_to_test.upper()} API...")
    asyncio.run(test_specific_api(api_to_test))
    
    print("\n📋 To test all APIs, uncomment the following line:")
    print("# asyncio.run(test_speech_apis())")
    
    print("\n🔧 Configuration:")
    print("- Edit backend/.env to set SPEECH_API_TYPE")
    print("- Add appropriate API keys/tokens")
    print("- See API_SETUP_GUIDE.md for detailed instructions")
