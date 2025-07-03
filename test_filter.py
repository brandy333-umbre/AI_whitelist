#!/usr/bin/env python3
"""
Test script for AI-driven URL filtering
"""

import time
import json
import sys
import ai_filter

def test_performance():
    """Test filtering performance and latency"""
    print("🔧 Performance Testing")
    print("=" * 30)
    
    # Test URLs with various categories
    test_urls = [
        # Productive/work related
        "https://github.com/microsoft/vscode",
        "https://stackoverflow.com/questions/python-programming",
        "https://docs.python.org/3/tutorial/",
        "https://developer.mozilla.org/en-US/docs/Web/JavaScript",
        "https://code.visualstudio.com/docs",
        
        # Distracting/entertainment
        "https://facebook.com/entertainment",
        "https://twitter.com/celebrities",
        "https://youtube.com/watch?v=funny_cat_video",
        "https://instagram.com/fashion",
        "https://reddit.com/r/funny",
        
        # Ambiguous/edge cases
        "https://medium.com/programming-tips",
        "https://linkedin.com/jobs/software-engineer",
        "https://amazon.com/programming-books",
        "https://news.ycombinator.com/programming",
        "https://wikipedia.org/wiki/Computer_science"
    ]
    
    print(f"Testing {len(test_urls)} URLs...")
    
    times = []
    decisions = {"allowed": 0, "blocked": 0}
    
    for i, url in enumerate(test_urls, 1):
        start_time = time.time()
        is_allowed = ai_filter.is_url_allowed(url)
        decision_time = (time.time() - start_time) * 1000
        
        times.append(decision_time)
        decisions["allowed" if is_allowed else "blocked"] += 1
        
        status = "ALLOW" if is_allowed else "BLOCK"
        print(f"  {i:2d}. {status} ({decision_time:5.1f}ms): {url}")
    
    # Performance statistics
    avg_time = sum(times) / len(times)
    max_time = max(times)
    min_time = min(times)
    slow_decisions = sum(1 for t in times if t > 50)
    
    print(f"\n📊 Performance Results:")
    print(f"  Average decision time: {avg_time:.1f}ms")
    print(f"  Fastest decision: {min_time:.1f}ms")
    print(f"  Slowest decision: {max_time:.1f}ms")
    print(f"  Decisions > 50ms: {slow_decisions}/{len(times)} ({slow_decisions/len(times)*100:.1f}%)")
    print(f"  Allowed: {decisions['allowed']}, Blocked: {decisions['blocked']}")
    
    # Test cache performance
    print(f"\n🚀 Cache Performance Test")
    cache_times = []
    for url in test_urls[:5]:  # Test first 5 URLs again
        start_time = time.time()
        ai_filter.is_url_allowed(url)
        cache_time = (time.time() - start_time) * 1000
        cache_times.append(cache_time)
    
    avg_cache_time = sum(cache_times) / len(cache_times)
    print(f"  Average cached decision time: {avg_cache_time:.1f}ms")
    
    return avg_time < 50 and avg_cache_time < 10  # Performance targets

def test_mission_accuracy():
    """Test filtering accuracy with different missions"""
    print("\n🎯 Mission Accuracy Testing")
    print("=" * 30)
    
    missions = [
        {
            "mission": "Focus on Python programming and software development",
            "should_allow": [
                "https://python.org/documentation",
                "https://github.com/python/cpython",
                "https://stackoverflow.com/questions/tagged/python"
            ],
            "should_block": [
                "https://facebook.com",
                "https://youtube.com/watch?v=funny_video",
                "https://instagram.com"
            ]
        },
        {
            "mission": "Research machine learning and artificial intelligence",
            "should_allow": [
                "https://arxiv.org/list/cs.AI/recent",
                "https://pytorch.org/tutorials",
                "https://scikit-learn.org/stable/documentation.html"
            ],
            "should_block": [
                "https://twitter.com/celebrity_gossip",
                "https://reddit.com/r/funny",
                "https://tiktok.com"
            ]
        }
    ]
    
    total_correct = 0
    total_tests = 0
    
    for mission_data in missions:
        print(f"\n📝 Mission: {mission_data['mission']}")
        ai_filter.set_mission(mission_data['mission'])
        
        mission_correct = 0
        mission_total = 0
        
        # Test URLs that should be allowed
        for url in mission_data['should_allow']:
            is_allowed = ai_filter.is_url_allowed(url)
            correct = is_allowed
            mission_correct += correct
            mission_total += 1
            total_correct += correct
            total_tests += 1
            
            status = "✅" if correct else "❌"
            print(f"  {status} ALLOW: {url} -> {'ALLOWED' if is_allowed else 'BLOCKED'}")
        
        # Test URLs that should be blocked
        for url in mission_data['should_block']:
            is_allowed = ai_filter.is_url_allowed(url)
            correct = not is_allowed
            mission_correct += correct
            mission_total += 1
            total_correct += correct
            total_tests += 1
            
            status = "✅" if correct else "❌"
            print(f"  {status} BLOCK: {url} -> {'ALLOWED' if is_allowed else 'BLOCKED'}")
        
        accuracy = (mission_correct / mission_total) * 100
        print(f"  Mission accuracy: {mission_correct}/{mission_total} ({accuracy:.1f}%)")
    
    overall_accuracy = (total_correct / total_tests) * 100
    print(f"\n📈 Overall accuracy: {total_correct}/{total_tests} ({overall_accuracy:.1f}%)")
    
    return overall_accuracy >= 80  # Accuracy target

def test_edge_cases():
    """Test edge cases and error handling"""
    print("\n🔍 Edge Case Testing")
    print("=" * 30)
    
    edge_cases = [
        "",  # Empty URL
        "not-a-url",  # Invalid URL
        "http://",  # Incomplete URL
        "https://very-long-domain-name-that-might-cause-issues.com/with/very/long/path/segments/that/could/potentially/cause/problems",
        "https://127.0.0.1:8080",  # Localhost
        "https://кириллица.рф",  # Non-ASCII domain
    ]
    
    passed = 0
    total = len(edge_cases)
    
    for url in edge_cases:
        try:
            start_time = time.time()
            result = ai_filter.is_url_allowed(url)
            decision_time = (time.time() - start_time) * 1000
            
            print(f"  ✅ '{url}' -> {'ALLOW' if result else 'BLOCK'} ({decision_time:.1f}ms)")
            passed += 1
        except Exception as e:
            print(f"  ❌ '{url}' -> ERROR: {e}")
    
    print(f"\nEdge case handling: {passed}/{total} passed")
    return passed == total

def main():
    """Run all tests"""
    print("🧪 AI Filter Testing Suite")
    print("=" * 40)
    
    # Check if AI filter is available
    try:
        ai_filter.set_mission("Focus on productive work and learning")
        print("✅ AI filter module loaded successfully")
    except Exception as e:
        print(f"❌ Error loading AI filter: {e}")
        print("Make sure dependencies are installed: python setup_proxy.py")
        sys.exit(1)
    
    # Run tests
    tests = [
        ("Performance", test_performance),
        ("Mission Accuracy", test_mission_accuracy),
        ("Edge Cases", test_edge_cases)
    ]
    
    passed_tests = 0
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            if result:
                print(f"\n✅ {test_name}: PASSED")
                passed_tests += 1
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n💥 {test_name}: ERROR - {e}")
    
    print(f"\n🏆 Test Results: {passed_tests}/{len(tests)} tests passed")
    
    if passed_tests == len(tests):
        print("🎉 All tests passed! The AI filter is ready for use.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()