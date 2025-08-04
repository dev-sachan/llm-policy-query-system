import parse as pr
from everything import InsuranceClaimsProcessor
import time

def test_end_to_end():
    """Test complete end-to-end workflow"""
    
    # Sample queries to test
    queries = [
        "46M knee replacement surgery 30-month policy Pune",
        "25F heart surgery 1 year policy Mumbai", 
        "35M dental treatment 6 months Delhi",
        "40F eye surgery 8-month policy Bangalore",
        "55M cancer treatment 2 months Chennai"
    ]
    
    print("🧪 End-to-End Integration Testing...")
    
    # Initialize processor
    try:
        processor = InsuranceClaimsProcessor()
        print("✅ System initialized successfully")
    except Exception as e:
        print(f"❌ System initialization failed: {e}")
        return
    
    results = []
    
    for i, query in enumerate(queries):
        print(f"\n--- Test {i+1} ---")
        print(f"Query: {query}")
        
        start_time = time.time()
        
        try:
            # Step 1: Parse query
            parsed = pr.parse_query(query)
            print(f"Parsed: {parsed}")
            
            # Step 2: Make decision
            decision = processor.make_decision(parsed)
            
            end_time = time.time()
            processing_time = (end_time - start_time) * 1000  # Convert to ms
            
            print(f"Decision: {decision['decision']}")
            print(f"Confidence: {decision['confidence']:.2f}")
            print(f"Processing Time: {processing_time:.1f}ms")
            
            if decision['justification']:
                print(f"Reason: {decision['justification'][0]}")
            
            results.append({
                "query": query,
                "decision": decision['decision'],
                "confidence": decision['confidence'],
                "processing_time_ms": processing_time,
                "success": True
            })
            
            print("✅ SUCCESS")
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append({
                "query": query,
                "success": False,
                "error": str(e)
            })
    
    # Summary
    print("\n" + "="*50)
    print("INTEGRATION TEST SUMMARY")
    print("="*50)
    
    successful = sum(1 for r in results if r.get('success', False))
    total = len(results)
    
    print(f"Success Rate: {successful}/{total} ({successful/total*100:.1f}%)")
    
    if successful > 0:
        avg_time = sum(r.get('processing_time_ms', 0) for r in results if r.get('success')) / successful
        print(f"Average Processing Time: {avg_time:.1f}ms")
        
    print("\nDetailed Results:")
    for i, result in enumerate(results):
        status = "✅" if result.get('success') else "❌"
        print(f"{status} Test {i+1}: {result.get('decision', 'ERROR')} "
              f"({result.get('processing_time_ms', 0):.1f}ms)")

if __name__ == "__main__":
    test_end_to_end()