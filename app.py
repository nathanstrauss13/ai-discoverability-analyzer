import os
import re
import requests
from flask import Flask, render_template, request, jsonify
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import sys

# Load .env file if it exists (for local development)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_secret_key_here")

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
anthropic = None

if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY.strip():
    try:
        anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)
        print("Anthropic client initialized successfully")
    except Exception as e:
        print(f"Error initializing Anthropic client: {e}")
        anthropic = None
else:
    print("Warning: ANTHROPIC_API_KEY not found or empty. AI recommendations will be disabled.")

def fetch_webpage_content(url):
    """Fetch and parse webpage content."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
        response.raise_for_status()
        return response.text
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 403:
            print(f"Access forbidden (403) for URL: {url}")
            return None
        else:
            print(f"HTTP Error fetching URL: {e}")
            return None
    except Exception as e:
        print(f"Error fetching URL: {e}")
        return None

def analyze_webpage_structure(html_content, url):
    """Analyze the structure and content of a webpage."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    analysis = {
        'url': url,
        'title': soup.title.string if soup.title else 'No title found',
        'meta_description': '',
        'headings': {
            'h1': [],
            'h2': [],
            'h3': [],
            'h4': [],
            'h5': [],
            'h6': []
        },
        'images': {
            'total': 0,
            'with_alt': 0,
            'without_alt': 0
        },
        'links': {
            'internal': 0,
            'external': 0,
            'total': 0
        },
        'structured_data': False,
        'tables': 0,
        'forms': 0,
        'semantic_elements': {
            'article': 0,
            'section': 0,
            'nav': 0,
            'aside': 0,
            'header': 0,
            'footer': 0,
            'main': 0
        }
    }
    
    # Get meta description
    meta_desc = soup.find('meta', attrs={'name': 'description'})
    if meta_desc:
        analysis['meta_description'] = meta_desc.get('content', '')
    
    # Analyze headings
    for i in range(1, 7):
        headings = soup.find_all(f'h{i}')
        analysis['headings'][f'h{i}'] = [h.get_text(strip=True) for h in headings]
    
    # Analyze images
    images = soup.find_all('img')
    analysis['images']['total'] = len(images)
    for img in images:
        if img.get('alt'):
            analysis['images']['with_alt'] += 1
        else:
            analysis['images']['without_alt'] += 1
    
    # Analyze links
    parsed_url = urlparse(url)
    base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
    
    links = soup.find_all('a', href=True)
    analysis['links']['total'] = len(links)
    for link in links:
        href = link['href']
        if href.startswith('http'):
            if base_domain in href:
                analysis['links']['internal'] += 1
            else:
                analysis['links']['external'] += 1
        elif href.startswith('/') or href.startswith('#'):
            analysis['links']['internal'] += 1
    
    # Check for structured data
    json_ld = soup.find_all('script', type='application/ld+json')
    analysis['structured_data'] = len(json_ld) > 0
    
    # Count tables and forms
    analysis['tables'] = len(soup.find_all('table'))
    analysis['forms'] = len(soup.find_all('form'))
    
    # Count semantic HTML5 elements
    for element in analysis['semantic_elements']:
        analysis['semantic_elements'][element] = len(soup.find_all(element))
    
    return analysis

def generate_ai_recommendations(analysis):
    """Use Claude to generate specific recommendations based on the analysis."""
    
    if not anthropic:
        return """AI-powered recommendations are not available (API key not configured).

Based on the technical analysis, here are general recommendations:

1. **Top Priority Improvements:**
   - Ensure you have exactly one H1 tag per page
   - Add meta descriptions to all pages
   - Implement structured data (Schema.org)

2. **Content Structure:**
   - Use semantic HTML5 elements (article, section, nav, etc.)
   - Create a clear heading hierarchy (H1 → H2 → H3)
   - Break content into logical sections

3. **Technical SEO:**
   - Add alt text to all images
   - Create an XML sitemap
   - Implement Open Graph tags

4. **Accessibility:**
   - Ensure all interactive elements are keyboard accessible
   - Use ARIA labels where appropriate
   - Maintain good color contrast

5. **Quick Wins:**
   - Add a robots.txt file
   - Compress images
   - Minify CSS and JavaScript"""
    
    # Create a summary of the analysis for Claude
    summary = f"""
    Website Analysis Summary:
    - Title: {analysis['title']}
    - Meta Description: {'Present' if analysis['meta_description'] else 'Missing'}
    - H1 tags: {len(analysis['headings']['h1'])}
    - H2 tags: {len(analysis['headings']['h2'])}
    - Total images: {analysis['images']['total']} ({analysis['images']['without_alt']} missing alt text)
    - Structured data: {'Yes' if analysis['structured_data'] else 'No'}
    - Tables: {analysis['tables']}
    - Semantic HTML5 elements used: {sum(analysis['semantic_elements'].values())}
    """
    
    try:
        response = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": f"""Based on this website analysis, provide specific recommendations to improve the page's discoverability and crawlability for AI/LLM systems. Focus on practical, actionable improvements.

{summary}

Please structure your response with:
1. Top 3 Priority Improvements (most impactful changes)
2. Content Structure Recommendations
3. Technical SEO Improvements
4. Accessibility Enhancements
5. Quick Wins (easy changes with good impact)

Keep recommendations concise and actionable. Focus on changes that will help AI systems better understand and process the content."""
            }]
        )
        
        return response.content[0].text
    except Exception as e:
        print(f"Error generating AI recommendations: {e}")
        return "Unable to generate AI recommendations at this time. Please check your API configuration."

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Please provide a URL'}), 400
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    # Fetch webpage content
    html_content = fetch_webpage_content(url)
    if not html_content:
        error_msg = (
            'Unable to fetch the webpage. This could be because:\n'
            '• The website blocks automated requests\n'
            '• The URL is incorrect or inaccessible\n'
            '• The website requires authentication\n\n'
            'Try analyzing a different website, or use the standalone.html file '
            'to view general AI optimization recommendations.'
        )
        return jsonify({'error': error_msg}), 400
    
    # Analyze webpage structure
    analysis = analyze_webpage_structure(html_content, url)
    
    # Generate AI recommendations
    ai_recommendations = generate_ai_recommendations(analysis)
    
    # Calculate overall score
    score = calculate_ai_readiness_score(analysis)
    
    return jsonify({
        'success': True,
        'analysis': analysis,
        'recommendations': ai_recommendations,
        'score': score,
        'timestamp': datetime.now().isoformat()
    })

def calculate_ai_readiness_score(analysis):
    """Calculate an AI readiness score based on various factors."""
    score = 0
    max_score = 100
    
    # Title and meta description (15 points)
    if analysis['title'] and analysis['title'] != 'No title found':
        score += 5
    if analysis['meta_description']:
        score += 10
    
    # Heading structure (20 points)
    if len(analysis['headings']['h1']) == 1:
        score += 10
    elif len(analysis['headings']['h1']) > 0:
        score += 5
    
    if len(analysis['headings']['h2']) > 0:
        score += 10
    
    # Images with alt text (15 points)
    if analysis['images']['total'] > 0:
        alt_ratio = analysis['images']['with_alt'] / analysis['images']['total']
        score += int(15 * alt_ratio)
    else:
        score += 15  # No penalty if no images
    
    # Structured data (20 points)
    if analysis['structured_data']:
        score += 20
    
    # Semantic HTML (20 points)
    semantic_count = sum(analysis['semantic_elements'].values())
    if semantic_count >= 5:
        score += 20
    elif semantic_count >= 3:
        score += 15
    elif semantic_count >= 1:
        score += 10
    
    # Tables for data (10 points)
    if analysis['tables'] > 0:
        score += 10
    
    return min(score, max_score)

if __name__ == '__main__':
    # Get port from environment variable for Render deployment
    port = int(os.environ.get('PORT', 5001))
    # Disable debug mode in production
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
