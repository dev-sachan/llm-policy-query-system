import parse as pr

def test_query_parser():
    """Test the query parsing functionality"""
    
    test_cases = [
        # Test Case 1: Complete query
        {
            "query": "46M knee surgery 6-month policy Pune",
            "expected": {
                "age": 46,
                "gender": "Male",
                "procedure": "Knee Surgery",
                "location": "Pune",
                "policy_duration_months": 6
            }
        },
        # Test Case 2: Different format
        {
            "query": "25 female heart surgery 2 year policy Mumbai",
            "expected": {
                "age": 25,
                "gender": "Female", 
                "procedure": "Heart Surgery",
                "location": "Mumbai",
                "policy_duration_months": 24
            }
        },
        # Test Case 3: Missing information
        {
            "query": "dental treatment Delhi",
            "expected": {
                "procedure": "Dental Treatment",
                "location": "Delhi",
                "age": None,
                "gender": None,
                "policy_duration_months": None
            }
        }
    ]
    
    print("🧪 Testing Query Parser...")
    for i, test in enumerate(test_cases):
        result = pr.parse_query(test["query"])
        print(f"\nTest {i+1}: {test['query']}")
        print(f"Result: {result}")
        
        # Check each expected field
        for key, expected_value in test["expected"].items():
            if result.get(key) == expected_value:
                print(f"✅ {key}: PASS")
            else:
                print(f"❌ {key}: FAIL (expected {expected_value}, got {result.get(key)})")

if __name__ == "__main__":
    test_query_parser()