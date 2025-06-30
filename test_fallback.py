import sys
import os

# Temporarily hide textstat to test fallback
import builtins
real_import = builtins.__import__

def mock_import(name, *args, **kwargs):
    if name == 'textstat':
        raise ImportError("Simulating textstat not available")
    return real_import(name, *args, **kwargs)

builtins.__import__ = mock_import

# Now import and test
from content_analyzer import ContentAnalyzer
from bs4 import BeautifulSoup

# Test content
test_html = """
<html>
<body>
<h1>Test Article</h1>
<p>This is a test article to check readability analysis. The content should be clear and easy to understand. We want to make sure that our fallback readability calculation works properly when textstat is not available.</p>
<p>AI systems prefer content that is written at an appropriate reading level. Content that is too complex may be difficult for AI to process and understand. On the other hand, content that is too simple may not provide enough value.</p>
<p>By implementing a fallback readability calculation, we ensure that the analysis can still provide useful metrics even when the textstat library is not available. This makes our tool more robust and reliable.</p>
</body>
</html>
"""

# Restore normal import
builtins.__import__ = real_import

# Analyze
analyzer = ContentAnalyzer()
soup = BeautifulSoup(test_html, 'html.parser')
content_analysis = analyzer.analyze_content(test_html, soup)

# Check readability results
readability = content_analysis['readability']
print("Fallback Readability Analysis Test")
print("=" * 50)
print(f"Flesch Reading Ease: {readability.get('flesch_reading_ease', 'N/A')}")
print(f"Flesch-Kincaid Grade: {readability.get('flesch_kincaid_grade', 'N/A')}")
print(f"Interpretation: {readability.get('interpretation', 'N/A')}")
print(f"AI Friendly: {readability.get('ai_friendly', 'N/A')}")
print(f"Calculation Method: {readability.get('calculation_method', 'textstat')}")

# Also check word count
print(f"\nWord Count: {content_analysis['content_quality']['word_count']}")
print(f"Sentence Count: {content_analysis['content_quality']['sentence_count']}")
