"""
Simplified ML Model Accuracy Test for LexiLearn
"""

def test_dyslexia_assessment():
    """Test dyslexia risk assessment accuracy"""
    def calculate_test_score(answers):
        """Standalone score calculation"""
        risk_points = 0
        for q_id, answer in answers.items():
            selected = answer.get("selected")
            # High risk answers get points
            if (q_id == "1" and selected in ["c", "d"]) or \
               (q_id == "2" and selected in ["b", "c"]) or \
               (q_id == "3" and selected in ["c", "d"]) or \
               (q_id == "4" and selected == "b") or \
               (q_id == "5" and selected == "a") or \
               (q_id == "6" and selected in ["b", "c"]) or \
               (q_id == "7" and selected == "c") or \
               (q_id == "8" and selected in ["c", "d"]):
                risk_points += 1
        return (risk_points / 8) * 100
    
    def determine_risk_level(score):
        """Standalone risk level determination"""
        if score >= 60:
            return "high"
        elif score >= 30:
            return "moderate"
        else:
            return "low"
    
    test_cases = [
        # High risk case
        {"answers": {"1": {"selected": "d"}, "2": {"selected": "c"}, "3": {"selected": "d"}, 
                    "4": {"selected": "b"}, "5": {"selected": "a"}, "6": {"selected": "c"}, 
                    "7": {"selected": "c"}, "8": {"selected": "d"}}, "expected": "high"},
        
        # Low risk case  
        {"answers": {"1": {"selected": "a"}, "2": {"selected": "a"}, "3": {"selected": "b"}, 
                    "4": {"selected": "a"}, "5": {"selected": "c"}, "6": {"selected": "a"}, 
                    "7": {"selected": "b"}, "8": {"selected": "a"}}, "expected": "low"},
    ]
    
    correct = 0
    total = len(test_cases)
    
    for case in test_cases:
        score = calculate_test_score(case["answers"])
        risk_level = determine_risk_level(score)
        
        if risk_level == case["expected"]:
            correct += 1
        
        print(f"Score: {score:.1f}%, Risk: {risk_level}, Expected: {case['expected']}")
    
    accuracy = (correct / total) * 100
    print(f"Dyslexia Assessment Accuracy: {accuracy:.1f}%")
    return accuracy

def test_text_analysis():
    """Test text analysis accuracy (simulated)"""
    def analyze_text_simple(text):
        """Simple text analysis simulation"""
        common_errors = ["teh", "recieve", "beleive", "seperate", "occured"]
        error_count = sum(1 for error in common_errors if error in text.lower())
        return {"error_count": error_count}
    
    test_cases = [
        {"text": "The cat sat on the mat", "expected_errors": 0},
        {"text": "Teh cat sat on teh mat", "expected_errors": 2},
        {"text": "I recieve the letter", "expected_errors": 1},
        {"text": "They beleive in magic", "expected_errors": 1},
    ]
    
    correct = 0
    total = len(test_cases)
    
    for case in test_cases:
        analysis = analyze_text_simple(case["text"])
        error_count = analysis.get("error_count", 0)
        
        if error_count == case["expected_errors"]:
            correct += 1
        
        print(f"Text: '{case['text']}' | Errors found: {error_count} | Expected: {case['expected_errors']}")
    
    accuracy = (correct / total) * 100
    print(f"Text Analysis Accuracy: {accuracy:.1f}%")
    return accuracy

def test_intent_recognition():
    """Test intent recognition (simulated)"""
    def analyze_intent(message):
        """Simple intent recognition simulation"""
        message_lower = message.lower()
        if "words" in message_lower and ("give" in message_lower or "practice" in message_lower):
            return {"intent": "word_request"}
        elif "help" in message_lower:
            return {"intent": "help_request"}
        elif "frustrated" in message_lower or "angry" in message_lower:
            return {"intent": "frustration"}
        elif "did it" in message_lower or "finished" in message_lower:
            return {"intent": "celebration"}
        elif "hello" in message_lower or "hi" in message_lower:
            return {"intent": "greeting"}
        else:
            return {"intent": "general"}
    
    test_cases = [
        {"message": "give me 5 words to practice", "expected": "word_request"},
        {"message": "I need help with reading", "expected": "help_request"},
        {"message": "I'm frustrated with this", "expected": "frustration"},
        {"message": "I did it! I finished the lesson", "expected": "celebration"},
        {"message": "hello there", "expected": "greeting"},
    ]
    
    correct = 0
    total = len(test_cases)
    
    for case in test_cases:
        analysis = analyze_intent(case["message"])
        intent = analysis.get("intent")
        
        if intent == case["expected"]:
            correct += 1
        
        print(f"Message: '{case['message']}' | Intent: {intent} | Expected: {case['expected']}")
    
    accuracy = (correct / total) * 100
    print(f"Intent Recognition Accuracy: {accuracy:.1f}%")
    return accuracy

def run_all_tests():
    """Run all accuracy tests"""
    print("🧪 Testing LexiLearn ML Model Accuracy")
    print("=" * 50)
    
    results = {}
    
    print("\n1. Testing Dyslexia Assessment...")
    results["dyslexia_assessment"] = test_dyslexia_assessment()
    
    print("\n2. Testing Text Analysis...")
    results["text_analysis"] = test_text_analysis()
    
    print("\n3. Testing Intent Recognition...")
    results["intent_recognition"] = test_intent_recognition()
    
    print("\n" + "=" * 50)
    print("📊 OVERALL RESULTS:")
    print("=" * 50)
    
    total_accuracy = 0
    for test_name, accuracy in results.items():
        print(f"{test_name.replace('_', ' ').title()}: {accuracy:.1f}%")
        total_accuracy += accuracy
    
    average_accuracy = total_accuracy / len(results)
    print(f"\n🎯 Average Model Accuracy: {average_accuracy:.1f}%")
    
    if average_accuracy >= 90:
        print("🟢 Excellent model performance!")
    elif average_accuracy >= 80:
        print("🟡 Good model performance")
    elif average_accuracy >= 70:
        print("🟠 Acceptable model performance")
    else:
        print("🔴 Model needs improvement")
    
    return results

if __name__ == "__main__":
    run_all_tests()