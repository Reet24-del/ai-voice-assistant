#!/usr/bin/env python3
"""
Test script for the new /llm/query endpoint
"""

import requests
import json
import time

def test_llm_endpoint():
    """Test the LLM query endpoint with various prompts"""
    
    base_url = "http://127.0.0.1:8000"
    endpoint = f"{base_url}/llm/query"
    
    # Test cases
    test_cases = [
        {
            "name": "Greeting",
            "text": "Hello! How are you today?"
        },
        {
            "name": "Explanation",
            "text": "Explain artificial intelligence in simple terms"
        },
        {
            "name": "Creative Writing",
            "text": "Write a haiku about coding"
        },
        {
            "name": "Problem Solving",
            "text": "What are the benefits of using APIs in software development?"
        }
    ]
    
    print("🤖 Testing LLM Query Endpoint")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Test: {test_case['name']}")
        print(f"   Query: {test_case['text']}")
        print("-" * 40)
        
        try:
            # Make the API request
            response = requests.post(
                endpoint,
                headers={"Content-Type": "application/json"},
                json={"text": test_case["text"]},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Status: {data['status']}")
                print(f"   ⏱️ Processing Time: {data['processing_time']}s")
                print(f"   💬 Response: {data['response']}")
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request failed: {str(e)}")
        
        if i < len(test_cases):
            print("\n" + "="*50)
            time.sleep(1)  # Brief pause between requests
    
    print("\n🎉 Testing completed!")

if __name__ == "__main__":
    test_llm_endpoint()
