import requests
import json

# Test the deployed app
url = "https://ai-discoverability-analyzer.innatec3.com/analyze"
data = {
    "url": "https://press.tiffany.com"
}

print("Testing deployed app at:", url)
print("Analyzing URL:", data["url"])
print("-" * 50)

try:
    response = requests.post(url, json=data)
    
    if response.status_code == 200:
        result = response.json()
        print("Success! Response received:")
        print(json.dumps(result, indent=2))
        
        # Check if readability analysis is present in content_analysis
        if 'analysis' in result and 'content_analysis' in result['analysis']:
            content_analysis = result['analysis']['content_analysis']
            if 'readability' in content_analysis:
                print("\n✓ Readability analysis is available!")
                readability = content_analysis['readability']
                print(f"  - AI Friendly: {readability.get('ai_friendly', 'N/A')}")
                print(f"  - Flesch Reading Ease: {readability.get('flesch_reading_ease', 'N/A')}")
                print(f"  - Flesch-Kincaid Grade: {readability.get('flesch_kincaid_grade', 'N/A')}")
                print(f"  - Interpretation: {readability.get('interpretation', 'N/A')}")
                
                # Check if textstat is available
                if readability.get('interpretation') == 'Textstat library not available for readability analysis':
                    print("\n  ⚠️  Note: Textstat library is not available on the deployed server")
                    print("     Readability scores cannot be calculated without the library")
            else:
                print("\n✗ Readability analysis is missing from content_analysis!")
        else:
            print("\n✗ Content analysis is missing from the response!")
    else:
        print(f"Error: HTTP {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"Error: {e}")
