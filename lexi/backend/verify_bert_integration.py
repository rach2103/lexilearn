"""
Verification script to confirm BERT integration with AI Tutor
"""

import asyncio
from ml_models.text_analysis import text_analyzer
from ml_models.ai_tutor import ai_tutor

async def verify_bert_integration():
    print("=" * 60)
    print("BERT Integration Verification")
    print("=" * 60)
    
    # Check text analyzer type
    analyzer_type = type(text_analyzer).__name__
    print(f"\n1. Text Analyzer Type: {analyzer_type}")
    
    if analyzer_type == "BERTTextAnalyzer":
        print("   ✓ BERT analyzer is active")
    else:
        print(f"   ⚠ Using {analyzer_type} instead of BERT")
    
    # Test text analysis
    print("\n2. Testing Text Analysis...")
    test_text = "I recieve the book yesterday"
    result = await text_analyzer.analyze_text(test_text)
    
    print(f"   Original: {result.get('original_text')}")
    print(f"   Corrected: {result.get('corrected_text')}")
    print(f"   Errors found: {result.get('error_count')}")
    print(f"   Analysis type: {result.get('analysis_type')}")
    print(f"   Confidence: {result.get('confidence_score')}")
    
    # Test AI tutor integration
    print("\n3. Testing AI Tutor Integration...")
    analysis = ai_tutor.analyze_user_input(test_text)
    print(f"   Intent: {analysis.get('intent')}")
    print(f"   Errors detected: {len(analysis.get('errors', []))}")
    
    if analysis.get('errors'):
        print("   Error details:")
        for error in analysis['errors'][:3]:
            print(f"     - {error.get('word')} → {error.get('suggestion')}")
    
    # Test AI tutor response generation
    print("\n4. Testing AI Tutor Response...")
    response = await ai_tutor.generate_response(test_text, analysis, {"user_id": 1})
    print(f"   Message: {response.get('message')[:100]}...")
    print(f"   Suggestions: {len(response.get('suggestions', []))}")
    print(f"   Tips: {len(response.get('tips', []))}")
    
    print("\n" + "=" * 60)
    print("Verification Complete!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(verify_bert_integration())
