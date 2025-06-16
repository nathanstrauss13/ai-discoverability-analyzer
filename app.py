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
    """Fetch and parse webpage content from HTTP(S) or local file:// URLs."""
    
    # Handle local file URLs
    if url.startswith('file://'):
        try:
            # Convert file:// URL to local path
            from urllib.parse import unquote
            file_path = url.replace('file://', '')
            # Handle URL encoding (like %20 for spaces)
            file_path = unquote(file_path)
            
            # Read the local file
            with open(file_path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            return None
        except Exception as e:
            print(f"Error reading local file: {e}")
            return None
    
    # Handle HTTP(S) URLs
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
    """Analyze the structure and content of a webpage, including advanced discoverability checks."""
    soup = BeautifulSoup(html_content, 'html.parser')

    # Initialize analysis dictionary with new fields
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
        },
        # New fields for advanced analysis
        'robots_txt': False,
        'sitemap_xml': False,
        'open_graph_tags': [],
        'twitter_card_tags': [],
        'canonical_tag': '',
        'html_lang': '',
        'meta_charset': ''
    }

    # Check robots.txt and sitemap.xml presence (only for HTTP(S) URLs)
    if url.startswith(('http://', 'https://')):
        try:
            parsed_url = urlparse(url)
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
            robots_resp = requests.get(urljoin(base_url, '/robots.txt'), timeout=5)
            if robots_resp.status_code == 200 and 'User-agent' in robots_resp.text:
                analysis['robots_txt'] = True
            sitemap_resp = requests.get(urljoin(base_url, '/sitemap.xml'), timeout=5)
            if sitemap_resp.status_code == 200 and ('<urlset' in sitemap_resp.text or '<sitemapindex' in sitemap_resp.text):
                analysis['sitemap_xml'] = True
        except Exception as e:
            pass  # Don't fail analysis if these checks error

    # Open Graph and Twitter Card tags
    og_tags = soup.find_all('meta', attrs={'property': re.compile(r'^og:', re.I)})
    analysis['open_graph_tags'] = [tag.get('property') for tag in og_tags if tag.get('property')]
    twitter_tags = soup.find_all('meta', attrs={'name': re.compile(r'^twitter:', re.I)})
    analysis['twitter_card_tags'] = [tag.get('name') for tag in twitter_tags if tag.get('name')]

    # Canonical tag
    canonical = soup.find('link', rel='canonical')
    if canonical and canonical.get('href'):
        analysis['canonical_tag'] = canonical['href']

    # HTML lang attribute
    html_tag = soup.find('html')
    if html_tag and html_tag.get('lang'):
        analysis['html_lang'] = html_tag['lang']

    # Meta charset
    meta_charset = soup.find('meta', attrs={'charset': True})
    if meta_charset and meta_charset.get('charset'):
        analysis['meta_charset'] = meta_charset['charset']

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
   - Add robots.txt and sitemap.xml files

2. **Content Structure:**
   - Use semantic HTML5 elements (article, section, nav, etc.)
   - Create a clear heading hierarchy (H1 → H2 → H3)
   - Break content into logical sections

3. **Technical SEO:**
   - Add alt text to all images
   - Implement Open Graph and Twitter Card tags
   - Add canonical tags to prevent duplicate content issues
   - Specify language with html lang attribute

4. **Accessibility:**
   - Ensure all interactive elements are keyboard accessible
   - Use ARIA labels where appropriate
   - Maintain good color contrast

5. **Quick Wins:**
   - Add charset meta tag
   - Compress images
   - Minify CSS and JavaScript"""
    
    # Create a comprehensive summary of the analysis for Claude
    summary = f"""
    Website Analysis Summary:
    - URL: {analysis['url']}
    - Title: {analysis['title']}
    - Meta Description: {'Present' if analysis['meta_description'] else 'Missing'}
    - HTML Language: {analysis.get('html_lang', 'Not specified')}
    - Charset: {analysis.get('meta_charset', 'Not specified')}
    
    Content Structure:
    - H1 tags: {len(analysis['headings']['h1'])}
    - H2 tags: {len(analysis['headings']['h2'])}
    - H3-H6 tags: {sum(len(analysis['headings'][f'h{i}']) for i in range(3, 7))}
    - Semantic HTML5 elements: {sum(analysis['semantic_elements'].values())} total
      ({', '.join(f"{k}: {v}" for k, v in analysis['semantic_elements'].items() if v > 0)})
    
    Media & Links:
    - Total images: {analysis['images']['total']} ({analysis['images']['without_alt']} missing alt text)
    - Internal links: {analysis['links']['internal']}
    - External links: {analysis['links']['external']}
    
    Technical SEO:
    - Robots.txt: {'Present' if analysis.get('robots_txt') else 'Missing'}
    - Sitemap.xml: {'Present' if analysis.get('sitemap_xml') else 'Missing'}
    - Canonical tag: {'Present' if analysis.get('canonical_tag') else 'Missing'}
    - Structured data (JSON-LD): {'Yes' if analysis['structured_data'] else 'No'}
    - Open Graph tags: {len(analysis.get('open_graph_tags', []))} found
    - Twitter Card tags: {len(analysis.get('twitter_card_tags', []))} found
    
    Data Organization:
    - Tables: {analysis['tables']}
    - Forms: {analysis['forms']}
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

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'anthropic_configured': anthropic is not None}), 200

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Please provide a URL'}), 400
    
    # Add protocol if missing (but not for file:// URLs)
    if not url.startswith(('http://', 'https://', 'file://')):
        url = 'https://' + url
    
    # Fetch webpage content
    html_content = fetch_webpage_content(url)
    if not html_content:
        error_msg = (
            'Unable to fetch the webpage. This could be because:\n'
            '• The website blocks automated requests (common with corporate sites)\n'
            '• The URL is incorrect or inaccessible\n'
            '• The website requires authentication\n\n'
            '**For sites that block automated access (like signetjewelers.com):**\n'
            '1. Save the webpage locally (Ctrl+S / Cmd+S in your browser)\n'
            '2. Open the saved HTML file in a browser\n'
            '3. Use the file:// URL in this analyzer\n\n'
            'Alternatively, try analyzing sites without aggressive bot protection:\n'
            '• Personal blogs and portfolios\n'
            '• Documentation sites\n'
            '• Open source project pages\n'
            '• Educational websites'
        )
        return jsonify({'error': error_msg}), 400
    
    # Analyze webpage structure
    analysis = analyze_webpage_structure(html_content, url)
    
    # Generate AI recommendations
    ai_recommendations = generate_ai_recommendations(analysis)
    
    # Calculate overall score and get breakdown
    score, score_breakdown = calculate_ai_readiness_score(analysis)
    
    return jsonify({
        'success': True,
        'analysis': analysis,
        'recommendations': ai_recommendations,
        'score': score,
        'score_breakdown': score_breakdown,
        'timestamp': datetime.now().isoformat()
    })

def calculate_ai_readiness_score(analysis):
    """Calculate an AI readiness score based on expanded, weighted factors with detailed breakdown."""
    score = 0
    max_score = 100
    breakdown = {
        'categories': [],
        'penalties': [],
        'total_earned': 0,
        'total_possible': 100,
        'final_score': 0
    }

    # Title and meta description (12 points)
    title_score = 0
    if analysis['title'] and analysis['title'] != 'No title found':
        title_score += 5
    if analysis['meta_description']:
        title_score += 7
    score += title_score
    breakdown['categories'].append({
        'name': 'Title & Meta Description',
        'earned': title_score,
        'possible': 12,
        'details': f"Title: {'✓' if title_score >= 5 else '✗'}, Meta Description: {'✓' if analysis['meta_description'] else '✗'}"
    })

    # Heading structure (12 points)
    heading_score = 0
    if len(analysis['headings']['h1']) == 1:
        heading_score += 6
    elif len(analysis['headings']['h1']) > 0:
        heading_score += 3
    if len(analysis['headings']['h2']) > 0:
        heading_score += 6
    score += heading_score
    breakdown['categories'].append({
        'name': 'Heading Structure',
        'earned': heading_score,
        'possible': 12,
        'details': f"H1: {len(analysis['headings']['h1'])}, H2: {len(analysis['headings']['h2'])}"
    })

    # Images with alt text (10 points)
    image_score = 0
    if analysis['images']['total'] > 0:
        alt_ratio = analysis['images']['with_alt'] / analysis['images']['total']
        image_score = int(10 * alt_ratio)
    else:
        image_score = 10
    score += image_score
    breakdown['categories'].append({
        'name': 'Image Alt Text',
        'earned': image_score,
        'possible': 10,
        'details': f"{analysis['images']['with_alt']}/{analysis['images']['total']} images have alt text" if analysis['images']['total'] > 0 else "No images found"
    })

    # Structured data (15 points)
    structured_score = 15 if analysis['structured_data'] else 0
    score += structured_score
    breakdown['categories'].append({
        'name': 'Structured Data',
        'earned': structured_score,
        'possible': 15,
        'details': 'JSON-LD present' if analysis['structured_data'] else 'No structured data found'
    })

    # Semantic HTML (10 points)
    semantic_count = sum(analysis['semantic_elements'].values())
    semantic_score = 0
    if semantic_count >= 5:
        semantic_score = 10
    elif semantic_count >= 3:
        semantic_score = 7
    elif semantic_count >= 1:
        semantic_score = 4
    score += semantic_score
    breakdown['categories'].append({
        'name': 'Semantic HTML',
        'earned': semantic_score,
        'possible': 10,
        'details': f"{semantic_count} semantic elements found"
    })

    # Tables/forms (5 points)
    data_score = 5 if (analysis['tables'] > 0 or analysis['forms'] > 0) else 0
    score += data_score
    breakdown['categories'].append({
        'name': 'Data Organization',
        'earned': data_score,
        'possible': 5,
        'details': f"Tables: {analysis['tables']}, Forms: {analysis['forms']}"
    })

    # robots.txt and sitemap.xml (12 points)
    crawl_score = 0
    if analysis.get('robots_txt'):
        crawl_score += 6
    if analysis.get('sitemap_xml'):
        crawl_score += 6
    score += crawl_score
    breakdown['categories'].append({
        'name': 'Crawlability Files',
        'earned': crawl_score,
        'possible': 12,
        'details': f"robots.txt: {'✓' if analysis.get('robots_txt') else '✗'}, sitemap.xml: {'✓' if analysis.get('sitemap_xml') else '✗'}"
    })

    # Open Graph/Twitter tags (10 points)
    social_score = 0
    if analysis.get('open_graph_tags'):
        social_score += 5
    if analysis.get('twitter_card_tags'):
        social_score += 5
    score += social_score
    breakdown['categories'].append({
        'name': 'Social Media Tags',
        'earned': social_score,
        'possible': 10,
        'details': f"OG: {len(analysis.get('open_graph_tags', []))}, Twitter: {len(analysis.get('twitter_card_tags', []))}"
    })

    # Canonical tag (6 points)
    canonical_score = 6 if analysis.get('canonical_tag') else 0
    score += canonical_score
    breakdown['categories'].append({
        'name': 'Canonical Tag',
        'earned': canonical_score,
        'possible': 6,
        'details': 'Present' if analysis.get('canonical_tag') else 'Missing'
    })

    # HTML lang and charset (8 points)
    lang_score = 0
    if analysis.get('html_lang'):
        lang_score += 5
    if analysis.get('meta_charset'):
        lang_score += 3
    score += lang_score
    breakdown['categories'].append({
        'name': 'Language & Charset',
        'earned': lang_score,
        'possible': 8,
        'details': f"Lang: {analysis.get('html_lang', 'Missing')}, Charset: {analysis.get('meta_charset', 'Missing')}"
    })

    # Apply penalties for missing critical elements
    penalties = 0
    if not analysis.get('robots_txt'):
        penalties += 3
        breakdown['penalties'].append({'name': 'Missing robots.txt', 'points': -3})
    if not analysis.get('sitemap_xml'):
        penalties += 3
        breakdown['penalties'].append({'name': 'Missing sitemap.xml', 'points': -3})
    if not analysis.get('canonical_tag'):
        penalties += 2
        breakdown['penalties'].append({'name': 'Missing canonical tag', 'points': -2})
    if not analysis.get('html_lang'):
        penalties += 2
        breakdown['penalties'].append({'name': 'Missing HTML lang attribute', 'points': -2})

    score -= penalties

    # Calculate totals
    breakdown['total_earned'] = sum(cat['earned'] for cat in breakdown['categories'])
    breakdown['total_penalties'] = -penalties
    breakdown['final_score'] = max(0, min(score, max_score))

    return breakdown['final_score'], breakdown

if __name__ == '__main__':
    # Get port from environment variable for Render deployment
    port = int(os.environ.get('PORT', 5001))
    # Disable debug mode in production
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"Starting Flask app on port {port}")
    print(f"Debug mode: {debug_mode}")
    print(f"ANTHROPIC_API_KEY present: {'Yes' if ANTHROPIC_API_KEY else 'No'}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
