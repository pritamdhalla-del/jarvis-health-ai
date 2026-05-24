
import sys
import os
from web_tools import WebTools
from usage_tracker import UsageTracker

def test_web_tools():
    print("\n=== Testing WebTools ===")
    wt = WebTools()
    
    # Test Search
    print("1. Testing internet search...")
    try:
        results = wt.search_internet("latest python version", num_results=3)
        if results.get("success"):
            print("✅ Search successful")
            print(f"   Found {results.get('count')} results")
            print(f"   First result: {results['results'][0]['title']}")
        else:
            print(f"❌ Search failed: {results.get('error')}")
    except Exception as e:
        print(f"❌ Search exception: {e}")

    # Test Read URL
    print("\n2. Testing URL reading...")
    try:
        # Use a reliable stable URL
        res = wt.read_url("https://www.python.org/")
        if res.get("success"):
            print("✅ Read URL successful")
            print(f"   Title: {res.get('title')}")
            print(f"   Content length: {res.get('length')}")
            print(f"   Snippet: {res.get('content')[:100]}...")
        else:
            print(f"❌ Read URL failed: {res.get('error')}")
    except Exception as e:
        print(f"❌ Read URL exception: {e}")

def test_usage_tracker():
    print("\n=== Testing UsageTracker ===")
    ut = UsageTracker("test_usage.json") # Use test file
    
    # Test initial state
    print("1. Testing initial state...")
    initial = ut.get_usage_summary()
    print(f"   Initial calls: {initial['total_calls']}")
    
    # Test increment
    print("\n2. Testing increment...")
    ut.increment_usage("test-model", 100)
    ut.increment_usage("test-model", 50)
    
    summary = ut.get_usage_summary()
    if summary["total_calls"] == initial["total_calls"] + 2:
        print("✅ Call count correct")
    else:
        print(f"❌ Call count incorrect: {summary['total_calls']}")
        
    if summary["models"]["test-model"]["tokens"] == 150:
        print("✅ Token count correct")
    else:
        print(f"❌ Token count incorrect: {summary['models']['test-model']['tokens']}")
        
    # Clean up
    if os.path.exists("test_usage.json"):
        os.remove("test_usage.json")
        print("   Cleaned up test file")

if __name__ == "__main__":
    test_web_tools()
    test_usage_tracker()
