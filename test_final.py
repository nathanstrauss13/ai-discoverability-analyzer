import requests
import json

# Test with a content-rich website
urls_to_test = [
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://docs.python.org/3/tutorial/index.html"
]

for test_url in urls_to_test:
    print(f"\nTesting: {test_url}")
    print("-" * 50)
    
    # Test deployed version
    response = requests.post(
        "https://ai-discoverability-analyzer.innatec3.com/analyze",
        json={"url": test_url}
    )
    
    if response.status_code == 200:
        result = response.json()
        
        # Check readability in the correct location
        if 'analysis' in result and 'content_analysis' in result['analysis']:
            readability = result['analysis']['content_analysis']['readability']
            
            print(f"Readability Analysis:")
            print(f"  - Flesch Reading Ease: {readability.get('flesch_reading_ease', 'N/A')}")
            print(f"  - Flesch-Kincaid Grade: {readability.get('flesch_kincaid_grade', 'N/A')}")
            print(f"  - Interpretation: {readability.get('interpretation', 'N/A')}")
            print(f"  - AI Friendly: {readability.get('ai_friendly', 'N/A')}")
            
            # Also check word count to see if content was analyzed
            content_quality = result['analysis']['content_analysis']['content_quality']
            print(f"\nContent Stats:")
            print(f"  - Word Count: {content_quality.get('word_count', 0)}")
            print(f"  - Sentence Count: {content_quality.get('sentence_count', 0)}")
    else:
        print(f"Error: {response.status_code}")
