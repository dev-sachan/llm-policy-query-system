import time
import statistics
import parse as pr
from everything import InsuranceClaimsProcessor

def test_performance():
    """Test system performance with multiple queries"""
    
    # Generate test queries
    test_queries = [
        f"{age}{gender} {procedure} {duration} {location}"
        for age in [25, 35, 45, 55]
        for gender in ["M", "F"] 
        for procedure in ["knee surgery", "heart surgery", "eye surgery"]
        for duration in ["6 months", "1 year", "2 years"]
        for location in ["Mumbai", "Delhi", "Pune"]
    ]
    
    print(f"🚀 Performance Testing with {len(test_queries)} queries...")
    
    try:
        processor = InsuranceClaimsProcessor()
        print("✅ Processor initialized")
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return
    
    # Warm up (first query is usually slower)
    pr.parse_query(test_queries[0])
    processor.make_decision(pr.parse_query(test_queries[0]))
    print("🔥 System warmed up")
    
    # Performance testing
    processing_times = []
    parsing_times = []
    decision_times = []
    
    successful_queries = 0
    
    for i, query in enumerate(test_queries[:50]):  # Test first 50 queries
        try:
            # Measure parsing time
            start_parse = time.time()
            parsed = pr.parse_query(query)
            end_parse = time.time()
            parse_time = (end_parse - start_parse) * 1000
            
            # Measure decision time
            start_decision = time.time()
            decision = processor.make_decision(parsed)
            end_decision = time.time()
            decision_time = (end_decision - start_decision) * 1000
            
            total_time = parse_time + decision_time
            
            parsing_times.append(parse_time)
            decision_times.append(decision_time)
            processing_times.append(total_time)
            successful_queries += 1
            
            if (i + 1) % 10 == 0:
                print(f"Processed {i + 1} queries...")
                
        except Exception as e:
            print(f"❌ Error with query {i+1}: {e}")
    
    # Calculate statistics
    if processing_times:
        print("\n" + "="*50)
        print("PERFORMANCE TEST RESULTS")
        print("="*50)
        
        print(f"Successful Queries: {successful_queries}/{len(test_queries[:50])}")
        print(f"Success Rate: {successful_queries/50*100:.1f}%")
        
        print(f"\nParsing Performance:")
        print(f"  Average: {statistics.mean(parsing_times):.1f}ms")
        print(f"  Median: {statistics.median(parsing_times):.1f}ms")
        print(f"  Min: {min(parsing_times):.1f}ms")
        print(f"  Max: {max(parsing_times):.1f}ms")
        
        print(f"\nDecision Performance:")
        print(f"  Average: {statistics.mean(decision_times):.1f}ms")
        print(f"  Median: {statistics.median(decision_times):.1f}ms")
        print(f"  Min: {min(decision_times):.1f}ms")
        print(f"  Max: {max(decision_times):.1f}ms")
        
        print(f"\nTotal Processing Performance:")
        print(f"  Average: {statistics.mean(processing_times):.1f}ms")
        print(f"  Median: {statistics.median(processing_times):.1f}ms")
        print(f"  Min: {min(processing_times):.1f}ms")
        print(f"  Max: {max(processing_times):.1f}ms")
        
        # Performance benchmarks
        avg_total = statistics.mean(processing_times)
        if avg_total < 300:
            print("✅ Performance: EXCELLENT (<300ms)")
        elif avg_total < 500:
            print("✅ Performance: GOOD (<500ms)")
        else:
            print("⚠️  Performance: NEEDS IMPROVEMENT (>500ms)")

if __name__ == "__main__":
    test_performance()