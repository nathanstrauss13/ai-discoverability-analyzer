import os
import re
import requests
from flask import Flask, render_template, request, jsonify, redirect, url_for
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import sys
from content_analyzer import ContentAnalyzer
import uuid
import json
from datetime import timedelta

# Load .env file if it exists (for local development)
load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "your_secret_key_here")

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
anthropic = None

# In-memory storage for results (in production, use a database)
stored_results = {}

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
        
        # Check if the response is a PDF
        content_type = response.headers.get('Content-Type', '').lower()
        if 'application/pdf' in content_type:
            print(f"PDF detected via Content-Type header: {content_type}")
            return None
        
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

def generate_optimization_workflow(analysis, score):
    """Generate a step-by-step optimization workflow based on analysis results."""
    workflow = {
        'quick_wins': [],
        'deep_optimizations': [],
        'strategic_initiatives': []
    }
    
    # Quick Wins (1-2 hours)
    if not analysis.get('meta_description'):
        workflow['quick_wins'].append({
            'task': 'Add meta descriptions to all pages',
            'impact': 'Helps AI understand page context quickly'
        })
    
    if analysis.get('images', {}).get('without_alt', 0) > 0:
        workflow['quick_wins'].append({
            'task': f"Add alt text to {analysis['images']['without_alt']} images",
            'impact': 'Makes visual content accessible to AI systems'
        })
    
    if not analysis.get('robots_txt'):
        workflow['quick_wins'].append({
            'task': 'Create robots.txt file',
            'impact': 'Ensures AI crawlers can access your content'
        })
    
    if not analysis.get('sitemap_xml'):
        workflow['quick_wins'].append({
            'task': 'Generate and submit sitemap.xml',
            'impact': 'Helps AI discover all your content'
        })
    
    # Content-specific quick wins
    if 'content_analysis' in analysis:
        ca = analysis['content_analysis']
        if ca.get('credibility_signals', {}).get('has_author_info') == False:
            workflow['quick_wins'].append({
                'task': 'Add author bylines and credentials',
                'impact': 'Increases content credibility for AI evaluation'
            })
    
    # Deep Optimizations (2-3 days)
    if not analysis.get('structured_data'):
        workflow['deep_optimizations'].append({
            'task': 'Implement structured data markup (Schema.org)',
            'impact': 'Critical for AI understanding - enables rich results'
        })
    
    if not analysis.get('faq_detected'):
        workflow['deep_optimizations'].append({
            'task': 'Create comprehensive FAQ sections',
            'impact': 'AI systems prioritize Q&A format for direct answers'
        })
    
    if 'content_analysis' in analysis:
        ca = analysis['content_analysis']
        if ca.get('promotional_language', {}).get('is_promotional'):
            workflow['deep_optimizations'].append({
                'task': 'Rewrite promotional content with factual focus',
                'impact': 'AI prefers objective, fact-based content'
            })
        
        if not ca.get('factual_content', {}).get('is_fact_based'):
            workflow['deep_optimizations'].append({
                'task': 'Add statistics, research citations, and data',
                'impact': 'Factual content is more likely to be cited by AI'
            })
    
    # Strategic Initiatives
    workflow['strategic_initiatives'].append({
        'task': 'Develop topical authority content strategy',
        'impact': 'Establishes your brand as the go-to source for AI'
    })
    
    workflow['strategic_initiatives'].append({
        'task': 'Build knowledge graph-aligned content',
        'impact': 'Helps AI understand entity relationships'
    })
    
    if 'content_analysis' in analysis:
        ca = analysis['content_analysis']
        if ca.get('wikipedia_presence', {}).get('wikipedia_ready') == False:
            workflow['strategic_initiatives'].append({
                'task': 'Create Wikipedia-style neutral content',
                'impact': 'AI models are heavily trained on Wikipedia format'
            })
    
    workflow['strategic_initiatives'].append({
        'task': 'Implement advanced schema strategies',
        'impact': 'Enables AI to extract specific data points'
    })
    
    return workflow


def analyze_webpage_structure(html_content, url):
    """Analyze the structure and content of a webpage, including advanced discoverability checks."""
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Initialize content analyzer
    content_analyzer = ContentAnalyzer()

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
        'meta_charset': '',
        # AI Agent optimization fields
        'faq_detected': False,
        'qa_schema': False,
        'llms_txt': False,
        'definition_lists': 0,
        'ordered_lists': 0,
        'unordered_lists': 0,
        'review_schema': False,
        'organization_schema': False
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
    
    # AI Agent optimization checks
    # Check for FAQ patterns
    faq_indicators = ['faq', 'frequently asked', 'questions', 'q&a', 'q & a']
    page_text = soup.get_text().lower()
    for indicator in faq_indicators:
        if indicator in page_text:
            analysis['faq_detected'] = True
            break
    
    # Check for Q&A schema
    for script in json_ld:
        try:
            import json
            data = json.loads(script.string)
            if isinstance(data, dict) and data.get('@type') in ['FAQPage', 'QAPage', 'Question']:
                analysis['qa_schema'] = True
            elif isinstance(data, dict) and data.get('@type') == 'Review':
                analysis['review_schema'] = True
            elif isinstance(data, dict) and data.get('@type') in ['Organization', 'Corporation', 'LocalBusiness']:
                analysis['organization_schema'] = True
        except:
            pass
    
    # Check for llms.txt file (only for HTTP(S) URLs)
    if url.startswith(('http://', 'https://')):
        try:
            llms_resp = requests.get(urljoin(base_url, '/llms.txt'), timeout=5)
            if llms_resp.status_code == 200:
                analysis['llms_txt'] = True
        except:
            pass
    
    # Count list elements for content structure
    analysis['definition_lists'] = len(soup.find_all('dl'))
    analysis['ordered_lists'] = len(soup.find_all('ol'))
    analysis['unordered_lists'] = len(soup.find_all('ul'))
    
    # Add comprehensive content analysis
    analysis['content_analysis'] = content_analyzer.analyze_content(html_content, soup)
    
    return analysis

def generate_ai_recommendations(analysis):
    """Use Claude to generate specific recommendations based on the analysis."""
    
    if not anthropic:
        # Generate content recommendations without AI
        content_analyzer = ContentAnalyzer()
        content_recs = []
        
        if 'content_analysis' in analysis:
            content_recs = content_analyzer.generate_content_recommendations(
                analysis['content_analysis'], 
                analysis
            )
        
        # Format recommendations
        rec_text = "AI-powered recommendations are not available (API key not configured).\n\n"
        rec_text += "## Content Optimization Recommendations\n\n"
        
        for rec in content_recs:
            rec_text += f"### {rec['category']} ({rec['priority']} Priority)\n"
            rec_text += f"**Issue:** {rec['issue']}\n"
            rec_text += f"**Action:** {rec['action']}\n"
            rec_text += f"**Impact:** {rec['impact']}\n\n"
        
        rec_text += """## Technical Recommendations

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
   - Specify language with html lang attribute"""
        
        return rec_text
    
    # Create a comprehensive summary of the analysis for Claude
    content_summary = ""
    if 'content_analysis' in analysis:
        ca = analysis['content_analysis']
        content_summary = f"""
    
    Content Quality Analysis:
    - Readability: {ca['readability'].get('interpretation', 'N/A')} (Score: {ca['readability'].get('flesch_reading_ease', 'N/A')})
    - Word Count: {ca['content_quality'].get('word_count', 0)}
    - Average Sentence Length: {ca['content_quality'].get('avg_sentence_length', 0)}
    - Promotional Language: {ca['promotional_language'].get('recommendation', 'N/A')}
    - Factual Content Score: {ca['factual_content'].get('factual_score', 0)}/100
    - Statistics/Numbers: {ca['factual_content'].get('statistics_count', 0)}
    - Citations: {ca['factual_content'].get('citation_count', 0)}
    - FAQ Section: {'Yes' if ca['answer_optimization'].get('has_faq_section') else 'No'}
    - Q&A Pairs: {ca['answer_optimization'].get('qa_pairs_count', 0)}
    - Credibility Score: {ca['credibility_signals'].get('credibility_score', 0)}/100
    - Author Info: {'Yes' if ca['credibility_signals'].get('has_author_info') else 'No'}
    - Quality External Links: {ca['credibility_signals'].get('quality_links', 0)}
    - Brevity Score: {ca['brevity_score'].get('brevity_score', 0)}/100
    - Content Structure: {'Has summary' if ca['content_structure'].get('has_summary') else 'No summary'}
    """
    
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
    
    AI Agent Optimization:
    - FAQ content detected: {'Yes' if analysis.get('faq_detected') else 'No'}
    - Q&A schema markup: {'Yes' if analysis.get('qa_schema') else 'No'}
    - llms.txt file: {'Present' if analysis.get('llms_txt') else 'Missing'}
    - Organization schema: {'Yes' if analysis.get('organization_schema') else 'No'}
    - List elements: {analysis.get('ordered_lists', 0) + analysis.get('unordered_lists', 0) + analysis.get('definition_lists', 0)} total
      (OL: {analysis.get('ordered_lists', 0)}, UL: {analysis.get('unordered_lists', 0)}, DL: {analysis.get('definition_lists', 0)})
    
    Data Organization:
    - Tables: {analysis['tables']}
    - Forms: {analysis['forms']}
    {content_summary}
    """
    
    try:
        response = anthropic.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=1500,
            messages=[{
                "role": "user",
                "content": f"""Based on this comprehensive website and content analysis, provide specific recommendations to improve the page's discoverability and crawlability for AI/LLM systems. 

IMPORTANT CONTEXT: 
- 80% of consumers now rely on AI-generated summaries (zero-click searches)
- 58% have replaced search engines with AI for recommendations
- 90%+ of AI responses come from third-party sources, not brand sites
- AI agents evaluate based on facts, not emotions
- Brands are invisible in AI responses unless optimized for machine comprehension

{summary}

Please structure your response with these sections:

## 1. CONTENT QUALITY IMPROVEMENTS
Based on the content analysis, provide specific recommendations for:
- Reducing promotional language and increasing factual content
- Improving readability and brevity
- Adding credibility signals and citations
- Structuring content for direct answer extraction

## 2. ZERO-CLICK OPTIMIZATION
How to ensure content appears in AI-generated summaries:
- FAQ/Q&A content structure
- Definition and glossary sections
- Key facts and statistics placement
- Summary boxes and key takeaways

## 3. THIRD-PARTY AUTHORITY BUILDING
Strategies for external validation:
- PR and media mention strategies
- Expert contribution opportunities
- Wikipedia and directory presence
- Review and testimonial optimization

## 4. TECHNICAL QUICK WINS
Immediate technical improvements:
- Schema markup implementation
- llms.txt file creation
- Meta data optimization
- Content structure improvements

## 5. CONSULTING OPPORTUNITIES
Identify specific areas where professional content creation and optimization services would have the highest impact, focusing on:
- Content rewrites for AI optimization
- Authority-building content campaigns
- Ongoing content strategy development

For each recommendation, include:
- The specific issue identified
- The recommended action
- The expected impact on AI visibility
- Implementation priority (Immediate/Short-term/Long-term)

Keep recommendations specific, actionable, and focused on improving AI agent comprehension and zero-click visibility."""
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
    
    # Check if URL points to a PDF
    if url.lower().endswith('.pdf') or 'application/pdf' in url.lower():
        error_msg = (
            '**PDF files cannot be analyzed directly.**\n\n'
            'This tool is designed to analyze HTML web pages, not PDF documents.\n\n'
            '**Options for PDF content:**\n'
            '1. If the PDF is a report/document on a website, analyze the webpage that hosts it instead\n'
            '2. Convert the PDF to HTML using online tools, then analyze the HTML\n'
            '3. Look for an HTML version of the same content\n\n'
            '**Why PDFs are challenging for AI discoverability:**\n'
            '• PDFs are primarily designed for printing, not web crawling\n'
            '• They lack semantic HTML structure\n'
            '• No meta tags, headings hierarchy, or structured data\n'
            '• Limited accessibility for screen readers and crawlers\n\n'
            'For better AI discoverability, content should be published as HTML web pages.'
        )
        return jsonify({'error': error_msg}), 400
    
    # Fetch webpage content
    html_content = fetch_webpage_content(url)
    if not html_content:
        # Check if it's a file:// URL on the deployed version
        if url.startswith('file://') and not os.environ.get('FLASK_ENV', 'development') == 'development':
            error_msg = (
                '**File URLs only work when running the analyzer locally.**\n\n'
                'The deployed web version cannot access files on your computer for security reasons.\n\n'
                '**Options for analyzing blocked sites:**\n'
                '1. **Run the analyzer locally** on your computer\n'
                '2. **Copy and paste the HTML** (coming soon)\n'
                '3. **Use the browser extension** (coming soon)\n\n'
                'For now, try analyzing sites without aggressive bot protection:\n'
                '• Personal blogs and portfolios\n'
                '• Documentation sites\n'
                '• Open source project pages\n'
                '• Educational websites'
            )
        else:
            error_msg = (
                'Unable to fetch the webpage. This could be because:\n'
                '• The website blocks automated requests (common with corporate sites)\n'
                '• The URL is incorrect or inaccessible\n'
                '• The website requires authentication\n\n'
                '**For sites that block automated access (like signetjewelers.com):**\n'
                '1. Save the webpage locally (Ctrl+S / Cmd+S in your browser)\n'
                '2. Run this analyzer locally on your computer\n'
                '3. Use the file:// URL in the local analyzer\n\n'
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
    
    # Generate optimization workflow
    workflow = generate_optimization_workflow(analysis, score)
    
    # Generate unique ID for this result
    result_id = str(uuid.uuid4())
    
    # Store the result
    result_data = {
        'id': result_id,
        'analysis': analysis,
        'recommendations': ai_recommendations,
        'score': score,
        'score_breakdown': score_breakdown,
        'workflow': workflow,
        'timestamp': datetime.now().isoformat(),
        'created_at': datetime.now()
    }
    
    stored_results[result_id] = result_data
    
    # Clean up old results (keep only last 1000 or from last 24 hours)
    cleanup_old_results()
    
    return jsonify({
        'success': True,
        'id': result_id,
        'analysis': analysis,
        'recommendations': ai_recommendations,
        'score': score,
        'score_breakdown': score_breakdown,
        'workflow': workflow,
        'timestamp': result_data['timestamp']
    })

def cleanup_old_results():
    """Remove results older than 24 hours or keep only the most recent 1000"""
    if len(stored_results) > 1000:
        # Sort by creation time and keep only the most recent 1000
        sorted_results = sorted(stored_results.items(), key=lambda x: x[1]['created_at'], reverse=True)
        stored_results.clear()
        for result_id, data in sorted_results[:1000]:
            stored_results[result_id] = data
    
    # Also remove results older than 24 hours
    cutoff_time = datetime.now() - timedelta(hours=24)
    to_remove = [rid for rid, data in stored_results.items() if data['created_at'] < cutoff_time]
    for rid in to_remove:
        del stored_results[rid]

@app.route('/results/<result_id>')
def view_result(result_id):
    """View a shared result"""
    result = stored_results.get(result_id)
    if not result:
        return render_template('index.html', error="Result not found or has expired")
    
    # Pass the result data to the template
    return render_template('index.html', shared_result=result)

def calculate_ai_readiness_score(analysis):
    """Calculate an AI readiness score based on expanded, weighted factors with detailed breakdown."""
    score = 0
    max_score = 100  # Total possible score (50 technical + 50 content)
    breakdown = {
        'categories': [],
        'penalties': [],
        'total_earned': 0,
        'total_possible': 100,
        'final_score': 0,
        'content_score': 0,
        'technical_score': 0
    }

    # TECHNICAL SEO SCORING (50 points total)
    
    # Title and meta description (6 points)
    title_score = 0
    if analysis['title'] and analysis['title'] != 'No title found':
        title_score += 2
    if analysis['meta_description']:
        title_score += 4
    score += title_score
    breakdown['categories'].append({
        'name': 'Title & Meta Description',
        'earned': title_score,
        'possible': 6,
        'details': f"Title: {'✓' if title_score >= 2 else '✗'}, Meta Description: {'✓' if analysis['meta_description'] else '✗'}"
    })

    # Heading structure (6 points)
    heading_score = 0
    if len(analysis['headings']['h1']) == 1:
        heading_score += 3
    elif len(analysis['headings']['h1']) > 0:
        heading_score += 1
    if len(analysis['headings']['h2']) > 0:
        heading_score += 3
    score += heading_score
    # Count all heading levels
    all_headings = sum(len(analysis['headings'][f'h{i}']) for i in range(1, 7))
    breakdown['categories'].append({
        'name': 'Heading Structure',
        'earned': heading_score,
        'possible': 6,
        'details': f"H1: {len(analysis['headings']['h1'])}, H2: {len(analysis['headings']['h2'])}, H3-H6: {sum(len(analysis['headings'][f'h{i}']) for i in range(3, 7))} (Total: {all_headings})"
    })

    # Images with alt text (5 points)
    image_score = 0
    if analysis['images']['total'] > 0:
        alt_ratio = analysis['images']['with_alt'] / analysis['images']['total']
        image_score = int(5 * alt_ratio)
        details = f"{analysis['images']['with_alt']}/{analysis['images']['total']} images have alt text"
    else:
        image_score = 5  # Full points if no images (not a penalty)
        details = "No images to optimize (not applicable)"
    score += image_score
    breakdown['categories'].append({
        'name': 'Image Alt Text',
        'earned': image_score,
        'possible': 5,
        'details': details
    })

    # Structured data (7 points)
    structured_score = 7 if analysis['structured_data'] else 0
    score += structured_score
    breakdown['categories'].append({
        'name': 'Structured Data',
        'earned': structured_score,
        'possible': 7,
        'details': 'JSON-LD present' if analysis['structured_data'] else 'No structured data found'
    })

    # Semantic HTML (5 points)
    semantic_count = sum(analysis['semantic_elements'].values())
    semantic_score = 0
    if semantic_count >= 5:
        semantic_score = 5
    elif semantic_count >= 3:
        semantic_score = 3
    elif semantic_count >= 1:
        semantic_score = 2
    score += semantic_score
    breakdown['categories'].append({
        'name': 'Semantic HTML',
        'earned': semantic_score,
        'possible': 5,
        'details': f"{semantic_count} semantic elements found"
    })

    # Tables/forms (2 points)
    data_score = 2 if (analysis['tables'] > 0 or analysis['forms'] > 0) else 0
    score += data_score
    breakdown['categories'].append({
        'name': 'Data Organization',
        'earned': data_score,
        'possible': 2,
        'details': f"Tables: {analysis['tables']}, Forms: {analysis['forms']}"
    })

    # robots.txt and sitemap.xml (6 points)
    crawl_score = 0
    if analysis.get('robots_txt'):
        crawl_score += 3
    if analysis.get('sitemap_xml'):
        crawl_score += 3
    score += crawl_score
    breakdown['categories'].append({
        'name': 'Crawlability Files',
        'earned': crawl_score,
        'possible': 6,
        'details': f"robots.txt: {'✓' if analysis.get('robots_txt') else '✗'}, sitemap.xml: {'✓' if analysis.get('sitemap_xml') else '✗'}"
    })

    # Open Graph/Twitter tags (5 points)
    social_score = 0
    if analysis.get('open_graph_tags'):
        social_score += 3
    if analysis.get('twitter_card_tags'):
        social_score += 2
    score += social_score
    breakdown['categories'].append({
        'name': 'Social Media Tags',
        'earned': social_score,
        'possible': 5,
        'details': f"Open Graph: {len(analysis.get('open_graph_tags', []))} tags, Twitter/X Cards: {len(analysis.get('twitter_card_tags', []))} tags"
    })

    # Canonical tag (3 points)
    canonical_score = 3 if analysis.get('canonical_tag') else 0
    score += canonical_score
    breakdown['categories'].append({
        'name': 'Canonical Tag',
        'earned': canonical_score,
        'possible': 3,
        'details': 'Present' if analysis.get('canonical_tag') else 'Missing'
    })

    # HTML lang and charset (4 points)
    lang_score = 0
    if analysis.get('html_lang'):
        lang_score += 3
    if analysis.get('meta_charset'):
        lang_score += 1
    score += lang_score
    breakdown['categories'].append({
        'name': 'Language & Charset',
        'earned': lang_score,
        'possible': 4,
        'details': f"Lang: {analysis.get('html_lang') if analysis.get('html_lang') else '✗'}, Charset: {analysis.get('meta_charset') if analysis.get('meta_charset') else '✗'}"
    })

    # Content Quality Scoring (50 additional points)
    if 'content_analysis' in analysis:
        ca = analysis['content_analysis']
        
        # Readability (10 points)
        readability_score = 0
        if ca['readability'].get('ai_friendly'):
            readability_score = 10
        elif ca['readability'].get('flesch_reading_ease'):
            if ca['readability']['flesch_reading_ease'] >= 50:
                readability_score = 7
            elif ca['readability']['flesch_reading_ease'] >= 30:
                readability_score = 4
        score += readability_score
        # Handle missing textstat library gracefully
        if ca['readability'].get('interpretation') == 'Textstat library not available for readability analysis':
            readability_details = 'Readability analysis unavailable (library not installed)'
        else:
            readability_details = ca['readability'].get('interpretation', 'Not analyzed')
        
        breakdown['categories'].append({
            'name': 'Content Readability',
            'earned': readability_score,
            'possible': 10,
            'details': readability_details
        })
        
        # Promotional vs Factual Content (15 points)
        content_tone_score = 0
        if not ca['promotional_language'].get('is_promotional', True):
            content_tone_score += 8
        elif ca['promotional_language'].get('promotional_density', 100) < 2:
            content_tone_score += 4
        
        if ca['factual_content'].get('is_fact_based', False):
            content_tone_score += 7
        elif ca['factual_content'].get('factual_score', 0) > 50:
            content_tone_score += 4
        
        score += content_tone_score
        # Create clearer details for tone and factuality
        promo_status = "Good" if not ca['promotional_language'].get('is_promotional', True) else "Too promotional"
        factual_status = f"Factual content: {ca['factual_content'].get('statistics_count', 0)} statistics, {ca['factual_content'].get('citation_count', 0)} citations"
        
        breakdown['categories'].append({
            'name': 'Content Tone & Factuality',
            'earned': content_tone_score,
            'possible': 15,
            'details': f"{promo_status} - {factual_status}"
        })
        
        # Answer Optimization (10 points)
        answer_score = 0
        if ca['answer_optimization'].get('has_faq_section'):
            answer_score += 5
        if ca['answer_optimization'].get('qa_pairs_count', 0) > 3:
            answer_score += 3
        if sum(ca['answer_optimization']['list_usage'].values()) > 5:
            answer_score += 2
        score += answer_score
        breakdown['categories'].append({
            'name': 'Answer Optimization',
            'earned': answer_score,
            'possible': 10,
            'details': f"FAQ: {'✓' if ca['answer_optimization'].get('has_faq_section') else '✗'}, Q&A Pairs: {ca['answer_optimization'].get('qa_pairs_count', 0)}"
        })
        
        # Credibility & Authority (10 points)
        cred_score = 0
        if ca['credibility_signals'].get('credibility_score', 0) >= 70:
            cred_score = 10
        elif ca['credibility_signals'].get('credibility_score', 0) >= 50:
            cred_score = 7
        elif ca['credibility_signals'].get('credibility_score', 0) >= 30:
            cred_score = 4
        score += cred_score
        # Build comprehensive credibility details
        author_status = "✓" if ca['credibility_signals'].get('has_author_info') else "✗"
        citations = ca['factual_content'].get('citation_count', 0)
        quality_links = ca['credibility_signals'].get('quality_links', 0)
        
        breakdown['categories'].append({
            'name': 'Credibility & Authority',
            'earned': cred_score,
            'possible': 10,
            'details': f"Author info: {author_status}, Citations: {citations}, Quality links: {quality_links}"
        })
        
        # Content Brevity (5 points)
        brevity_score = 0
        if ca['brevity_score'].get('is_concise', False):
            brevity_score = 5
        elif ca['brevity_score'].get('brevity_score', 0) > 50:
            brevity_score = 3
        score += brevity_score
        breakdown['categories'].append({
            'name': 'Content Brevity',
            'earned': brevity_score,
            'possible': 5,
            'details': ca['brevity_score'].get('recommendation', 'Not analyzed')
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
    
    # Content-specific penalties
    if 'content_analysis' in analysis:
        ca = analysis['content_analysis']
        if ca['promotional_language'].get('is_promotional', False):
            penalties += 5
            breakdown['penalties'].append({'name': 'Excessive promotional language', 'points': -5})
        if not ca['answer_optimization'].get('has_faq_section', False):
            penalties += 3
            breakdown['penalties'].append({'name': 'No FAQ/Q&A section', 'points': -3})

    score -= penalties

    # Calculate totals
    breakdown['total_earned'] = sum(cat['earned'] for cat in breakdown['categories'])
    breakdown['total_penalties'] = -penalties
    
    # Normalize to 100-point scale
    normalized_score = int((score / max_score) * 100)
    breakdown['final_score'] = max(0, min(normalized_score, 100))
    
    # Calculate sub-scores
    technical_categories = ['Title & Meta Description', 'Heading Structure', 'Image Alt Text', 
                          'Structured Data', 'Semantic HTML', 'Data Organization', 
                          'Crawlability Files', 'Social Media Tags', 'Canonical Tag', 
                          'Language & Charset']
    content_categories = ['Content Readability', 'Content Tone & Factuality', 
                         'Answer Optimization', 'Credibility & Authority', 'Content Brevity']
    
    breakdown['technical_score'] = sum(cat['earned'] for cat in breakdown['categories'] 
                                     if cat['name'] in technical_categories)
    breakdown['content_score'] = sum(cat['earned'] for cat in breakdown['categories'] 
                                   if cat['name'] in content_categories)

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
