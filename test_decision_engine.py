from everything import InsuranceClaimsProcessor
import json

def test_decision_engine():
    """Test the decision making functionality"""
    
    # Initialize processor
    try:
        processor = InsuranceClaimsProcessor()
        print("✅ Processor initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize processor: {e}")
        return
    
    # Test cases for decision making
    test_cases = [
        # Test Case 1: Should be rejected (waiting period not met)
        {
            "name": "Knee Surgery - Waiting period not met",
            "parsed": {
                "age": 46,
                "gender": "Male",
                "procedure": "knee surgery",
                "location": "Pune",
                "policy_duration_months": 12
            },
            "expected_decision": "rejected"
        },
        # Test Case 2: Should be approved (waiting period met)
        {
            "name": "Knee Surgery - Waiting period met",
            "parsed": {
                "age": 46,
                "gender": "Male", 
                "procedure": "knee surgery",
                "location": "Pune",
                "policy_duration_months": 30
            },
            "expected_decision": "approved"
        },
        # Test Case 3: Should be rejected (excluded procedure)
        {
            "name": "Dental Treatment - Excluded",
            "parsed": {
                "age": 30,
                "gender": "Female",
                "procedure": "dental treatment",
                "location": "Mumbai",
                "policy_duration_months": 12
            },
            "expected_decision": "rejected"
        }
    ]
    
    print("\n🧪 Testing Decision Engine...")
    for i, test in enumerate(test_cases):
        print(f"\nTest {i+1}: {test['name']}")
        print(f"Input: {test['parsed']}")
        
        try:
            decision = processor.make_decision(test["parsed"])
            print(f"Decision: {decision['decision']}")
            print(f"Justification: {decision['justification']}")
            print(f"Confidence: {decision['confidence']}")
            
            if decision["decision"] == test["expected_decision"]:
                print("✅ PASS")
            else:
                print(f"❌ FAIL (expected {test['expected_decision']})")
                
        except Exception as e:
            print(f"❌ ERROR: {e}")

if __name__ == "__main__":
    test_decision_engine()