import requests
import json
import time

print("Waiting 30 seconds for Render to start redeploying...")
time.sleep(30)

# Test the deployed app with the fallback readability
url = "https://ai-discoverability-analyzer.innatec3.com/analyze"
test_urls = [
    "https://en.wikipedia.org/wiki/Python_(programming_language)",
    "https://docs.python.org/3/tutorial/introduction.html"
]

for test_url in test_urls:
    print(f"\nTesting: {test_url}")
    print("-" * 50)
    
    response = requests.post(url, json={"url": test_url})
    
    if response.status_code == 200:
        result = response.json()
        
        if 'analysis' in result and 'content_analysis' in result['analysis']:
            readability = result['analysis']['content_analysis']['readability']
            
            print("Readability Analysis:")
            print(f"  - Flesch Reading Ease: {readability.get('flesch_reading_ease', 'N/A')}")
            print(f"  - Flesch-Kincaid Grade: {readability.get('flesch_kincaid_grade', 'N/A')}")
            print(f"  - Interpretation: {readability.get('interpretation', 'N/A')}")
            print(f"  - AI Friendly: {readability.get('ai_friendly', 'N/A')}")
            print(f"  - Calculation Method: {readability.get('calculation_method', 'Not specified')}")
            
            # Check if it's using fallback
            if readability.get('calculation_method') == 'fallback':
                print("  ✓ Using fallback calculation successfully!")
            elif readability.get('flesch_reading_ease') is not None:
                print("  ✓ Readability scores calculated successfully!")
            else:
                print("  ✗ Readability calculation failed")
    else:
        print(f"Error: {response.status_code}")
