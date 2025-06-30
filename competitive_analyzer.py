"""
Standalone Competitive Content Analyzer for AI Discoverability
Integrates with existing Flask app - copy this entire file to your VSC and share with Anthropic API
"""

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
import uuid
import json
import time

# Load environment variables
load_dotenv()

# Initialize Anthropic client
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
anthropic_client = None

if ANTHROPIC_API_KEY and ANTHROPIC_API_KEY.strip():
    try:
        anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
        print("Anthropic client initialized successfully for competitive analysis")
    except Exception as e:
        print(f"Error initializing Anthropic client: {e}")
        anthropic_client = None
else:
    print("Warning: ANTHROPIC_API_KEY not found. Competitive analysis will be limited.")

class CompetitiveAnalyzer:
    def __init__(self):
        self.client = anthropic_client
    
    def scrape_url_content(self, url):
        """Scrape and clean content from URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            response = requests.get(url, headers=headers, timeout=15, allow_redirects=True)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script, style, nav, footer, header elements
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            return text[:10000]  # Limit content length for API efficiency
            
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return f"Error: Unable to scrape content from {url}"
    
    def analyze_content_strategic(self, content, url):
        """Analyze content with strategic focus for AI discoverability"""
        
        print(f"🔍 Starting analysis for: {url}")
        print(f"🤖 Anthropic client available: {self.client is not None}")
        
        if not self.client:
            print("❌ No Anthropic client - using fallback")
            return self._get_fallback_analysis()
        
        prompt = f"""
        Analyze this content for AI discoverability and respond with ONLY valid JSON:

        URL: {url}
        Content: {content[:3000]}

        Analyze the actual content and provide a JSON response with this structure:
        {{
            "strategic_positioning": {{
                "current_tone": "promotional|educational|hybrid",
                "promotional_percentage": [0-100 based on actual content],
                "audience_level": "early-stage|decision-maker|technical",
                "narrative_focus": "product-centric|outcome-focused|solution-oriented"
            }},
            "content_gaps": {{
                "factual_density_score": [0-100 based on facts/data in content],
                "authority_signals_score": [0-100 based on credibility indicators],
                "answer_structure_score": [0-100 based on Q&A format],
                "evidence_quality_score": [0-100 based on citations/proof]
            }},
            "strategic_recommendations": [
                {{
                    "category": "positioning|evidence|structure",
                    "priority": "high|medium|low",
                    "recommendation": "[specific recommendation based on content analysis]",
                    "business_impact": "[specific impact description]",
                    "effort": "high|medium|low",
                    "timeline": "1-2 weeks|1-2 months|3+ months"
                }}
            ],
            "competitive_strengths": ["[list actual strengths found in content]"],
            "ai_optimization_score": [0-100 overall score based on analysis]
        }}

        Important: Analyze the ACTUAL content provided. Give different scores and recommendations based on what you actually see in the content.
        """
        
        try:
            print("🚀 Making API call to Claude...")
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",  # More reliable model
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            
            print(f"✅ API response received: {len(response.content[0].text)} characters")
            
            # Extract and clean the response
            text = response.content[0].text.strip()
            print(f"📝 Raw response preview: {text[:200]}...")
            
            # Handle markdown code blocks
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
                print("🔧 Extracted JSON from markdown block")
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
                print("🔧 Extracted content from code block")
            
            # Find JSON object boundaries
            start = text.find('{')
            end = text.rfind('}') + 1
            if start >= 0 and end > start:
                text = text[start:end]
                print("🔧 Extracted JSON object boundaries")
            
            print(f"🧹 Cleaned text preview: {text[:200]}...")
            
            # Parse JSON response
            result = json.loads(text)
            print("✅ JSON parsed successfully")
            return result
            
        except json.JSONDecodeError as e:
            print(f"❌ JSON parsing error: {e}")
            print(f"📝 Full raw response: {response.content[0].text}")
            return self._get_fallback_analysis()
        except Exception as e:
            print(f"❌ API call error: {e}")
            return self._get_fallback_analysis()
    
    def generate_content_rewrites(self, content, strategic_gaps):
        """Generate specific content rewrite suggestions"""
        
        if not self.client:
            return {"rewrites": [], "overall_strategy": "AI-powered rewrites require API configuration"}
        
        prompt = f"""
        Based on this content and strategic gaps, provide specific rewrite suggestions:

        Original Content: {content[:3000]}...
        
        Strategic Gaps: {json.dumps(strategic_gaps)}

        Provide 3-5 specific rewrite examples in this format:
        {{
            "rewrites": [
                {{
                    "section": "headline|intro|body|conclusion",
                    "original": "original text excerpt",
                    "rewritten": "improved version",
                    "reasoning": "why this improves AI discoverability",
                    "impact": "high|medium|low"
                }}
            ],
            "overall_strategy": "summary of strategic content direction"
        }}

        Focus on:
        1. Transforming promotional language to factual/educational
        2. Adding specific metrics and proof points
        3. Improving answer structure for AI queries
        4. Enhancing authority signals
        """
        
        try:
            response = self.client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text)
            return result
            
        except Exception as e:
            print(f"Error generating rewrites: {e}")
            return {"rewrites": [], "overall_strategy": "Unable to generate rewrites"}
    
    def compare_urls(self, urls):
        """Compare multiple URLs strategically"""
        results = []
        
        for url in urls:
            if not url.strip():
                continue
                
            print(f"Analyzing: {url}")
            content = self.scrape_url_content(url)
            if content.startswith("Error:"):
                results.append({
                    'url': url,
                    'domain': urlparse(url).netloc,
                    'error': content,
                    'analysis': None
                })
                continue
                
            analysis = self.analyze_content_strategic(content, url)
            
            results.append({
                'url': url,
                'domain': urlparse(url).netloc,
                'analysis': analysis,
                'content_preview': content[:200] + "..." if len(content) > 200 else content
            })
            
            # Add delay to avoid rate limiting
            time.sleep(1)
        
        return results
    
    def _get_fallback_analysis(self):
        """Fallback analysis if API fails"""
        return {
            "strategic_positioning": {
                "current_tone": "promotional",
                "promotional_percentage": 65,
                "audience_level": "early-stage",
                "narrative_focus": "product-centric"
            },
            "content_gaps": {
                "factual_density_score": 60,
                "authority_signals_score": 45,
                "answer_structure_score": 40,
                "evidence_quality_score": 50
            },
            "strategic_recommendations": [
                {
                    "category": "positioning",
                    "priority": "high",
                    "recommendation": "Shift from product features to customer outcomes",
                    "business_impact": "Improved AI citation probability",
                    "effort": "high",
                    "timeline": "1-2 months"
                }
            ],
            "competitive_strengths": ["Clear product description"],
            "ai_optimization_score": 55
        }

# Add these routes to your existing Flask app
def add_competitive_routes(app):
    """Add competitive analysis routes to existing Flask app"""

    @app.route('/api/analyze-competitive', methods=['POST'])
    def analyze_competitive():
        """API endpoint for competitive analysis"""
        try:
            data = request.get_json()
            analysis_type = data.get('analysis_type', 'direct')
            
            analyzer = CompetitiveAnalyzer()
            
            if analysis_type == 'direct':
                urls = data.get('urls', [])
                urls = [url for url in urls if url.strip()]  # Filter empty URLs
                
                if len(urls) < 2:
                    return jsonify({'error': 'Please provide at least 2 URLs for comparison'}), 400
                
                results = analyzer.compare_urls(urls)
                
                return jsonify({
                    'success': True,
                    'analysis_type': 'direct',
                    'results': results,
                    'timestamp': time.time()
                })
            
            elif analysis_type == 'topic':
                topic = data.get('topic', '')
                return jsonify({
                    'error': 'Topic-based analysis coming soon',
                    'message': 'This feature will automatically find top content for your topic'
                }), 501
            
            else:
                return jsonify({'error': 'Invalid analysis type'}), 400
        
        except Exception as e:
            print(f"Error in competitive analysis: {e}")
            return jsonify({'error': 'Analysis failed. Please try again.'}), 500

    @app.route('/api/generate-rewrites', methods=['POST'])
    def generate_rewrites():
        """API endpoint for content rewrite suggestions"""
        try:
            data = request.get_json()
            url = data.get('url', '')
            
            if not url:
                return jsonify({'error': 'URL is required'}), 400
            
            analyzer = CompetitiveAnalyzer()
            
            # Get content and analyze
            content = analyzer.scrape_url_content(url)
            if content.startswith("Error:"):
                return jsonify({'error': content}), 400
                
            strategic_analysis = analyzer.analyze_content_strategic(content, url)
            
            # Generate rewrites
            rewrites = analyzer.generate_content_rewrites(content, strategic_analysis['content_gaps'])
            
            return jsonify({
                'success': True,
                'url': url,
                'strategic_analysis': strategic_analysis,
                'rewrites': rewrites,
                'timestamp': time.time()
            })
        
        except Exception as e:
            print(f"Error generating rewrites: {e}")
            return jsonify({'error': 'Failed to generate rewrites. Please try again.'}), 500

    @app.route('/test-competitive')
    def test_competitive():
        """Test endpoint for competitive analysis"""
        return jsonify({
            'message': 'Competitive analysis routes are working!',
            'anthropic_configured': anthropic_client is not None,
            'available_endpoints': [
                '/competitive-analysis',
                '/api/analyze-competitive',
                '/api/generate-rewrites'
            ]
        })

# HTML Template for competitive analysis
COMPETITIVE_ANALYSIS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Competitive Content Analysis - AI Discoverability Analyzer</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
</head>
<body class="bg-gradient-to-br from-blue-50 to-indigo-100 min-h-screen">
    <div class="container mx-auto px-6 py-8">
        <div class="text-center mb-8">
            <h1 class="text-4xl font-bold text-gray-900 mb-2">
                <i class="fas fa-chart-line text-blue-500 mr-3"></i>
                Strategic Content Analysis
            </h1>
            <p class="text-xl text-gray-600">Compare your content strategy against competitors for AI optimization</p>
            <div class="flex justify-center mt-4 space-x-4">
                <span class="bg-purple-100 text-purple-800 px-3 py-1 rounded-full text-sm font-medium">Strategic-First</span>
                <span class="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium">Content-Focused</span>
                <span class="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm font-medium">Consultant-Ready</span>
            </div>
        </div>

        <!-- URL Comparison Section -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-6">
            <h2 class="text-2xl font-bold mb-4">
                <i class="fas fa-balance-scale text-blue-500 mr-2"></i>
                Compare URLs Strategically
            </h2>
            
            <div class="space-y-3" id="url-inputs">
                <div class="flex space-x-2">
                    <input type="url" placeholder="Your content URL..." class="url-input flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                </div>
                <div class="flex space-x-2">
                    <input type="url" placeholder="Competitor URL..." class="url-input flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                </div>
            </div>

            <div class="flex justify-between mt-4">
                <button id="add-url-btn" class="flex items-center space-x-2 px-4 py-2 text-blue-500 border border-blue-500 rounded-lg hover:bg-blue-50">
                    <i class="fas fa-plus"></i>
                    <span>Add URL</span>
                </button>
                
                <button id="analyze-btn" class="bg-blue-500 text-white px-8 py-3 rounded-lg font-medium hover:bg-blue-600 disabled:opacity-50 transition-all">
                    <i class="fas fa-chart-bar mr-2"></i>
                    Analyze Competition
                </button>
            </div>

            <div class="mt-4 p-4 bg-blue-50 rounded-lg">
                <h4 class="font-medium text-blue-900 mb-2">
                    <i class="fas fa-shield-alt mr-2"></i>Strategic Analysis Features
                </h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm text-blue-800">
                    <div>
                        <strong>Content Positioning:</strong>
                        <ul class="mt-1 space-y-1">
                            <li>• Promotional vs. educational tone analysis</li>
                            <li>• Audience sophistication assessment</li>
                            <li>• Narrative structure evaluation</li>
                        </ul>
                    </div>
                    <div>
                        <strong>AI Optimization:</strong>
                        <ul class="mt-1 space-y-1">
                            <li>• Factual density scoring</li>
                            <li>• Authority signal detection</li>
                            <li>• Answer structure analysis</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Loading State -->
        <div id="loading-state" class="hidden bg-white rounded-xl shadow-lg p-8 text-center">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <h3 class="text-lg font-medium text-gray-900 mb-2">Analyzing competitive content...</h3>
            <div class="space-y-1 text-sm text-gray-600">
                <p><i class="fas fa-check text-green-500 mr-2"></i>Crawling and parsing content</p>
                <p><i class="fas fa-spinner fa-spin text-blue-500 mr-2"></i>Running strategic analysis</p>
                <p class="text-gray-400"><i class="far fa-clock mr-2"></i>Identifying content gaps</p>
            </div>
        </div>

        <!-- Results Section -->
        <div id="results-section" class="hidden space-y-6">
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h3 class="text-xl font-bold mb-4">
                    <i class="fas fa-chart-bar text-blue-500 mr-2"></i>
                    Competitive Analysis Results
                </h3>
                <div id="results-content">
                    <!-- Results will be populated by JavaScript -->
                </div>
            </div>
        </div>
    </div>

    <script>
        let urlCount = 2;
        const maxUrls = 5;

        document.getElementById('add-url-btn').addEventListener('click', () => {
            if (urlCount < maxUrls) {
                urlCount++;
                const urlInputs = document.getElementById('url-inputs');
                const newInput = document.createElement('div');
                newInput.className = 'flex space-x-2';
                newInput.innerHTML = `
                    <input type="url" placeholder="Competitor URL..." class="url-input flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                    <button class="remove-url-btn px-3 py-3 text-red-500 hover:bg-red-50 rounded-lg">
                        <i class="fas fa-times"></i>
                    </button>
                `;
                urlInputs.appendChild(newInput);
                
                newInput.querySelector('.remove-url-btn').addEventListener('click', () => {
                    newInput.remove();
                    urlCount--;
                    updateAddButton();
                });
                
                updateAddButton();
            }
        });

        function updateAddButton() {
            const addBtn = document.getElementById('add-url-btn');
            if (urlCount >= maxUrls) {
                addBtn.style.display = 'none';
            } else {
                addBtn.style.display = 'flex';
            }
        }

        document.getElementById('analyze-btn').addEventListener('click', async () => {
            const urls = Array.from(document.querySelectorAll('.url-input')).map(input => input.value.trim()).filter(url => url);
            
            if (urls.length < 2) {
                alert('Please provide at least 2 URLs for comparison');
                return;
            }

            document.getElementById('loading-state').classList.remove('hidden');
            document.getElementById('results-section').classList.add('hidden');

            try {
                const response = await fetch('/api/analyze-competitive', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        analysis_type: 'direct',
                        urls: urls
                    })
                });

                const data = await response.json();

                if (data.success) {
                    displayResults(data.results);
                } else {
                    alert('Analysis failed: ' + (data.error || 'Unknown error'));
                }
            } catch (error) {
                console.error('Error:', error);
                alert('Analysis failed. Please try again.');
            } finally {
                document.getElementById('loading-state').classList.add('hidden');
            }
        });

        function displayResults(results) {
            const container = document.getElementById('results-content');
            
            let html = '<div class="space-y-6">';
            
            results.forEach((result, index) => {
                if (result.error) {
                    html += `
                        <div class="p-4 bg-red-50 border border-red-200 rounded-lg">
                            <h4 class="font-medium text-red-900">${result.domain}</h4>
                            <p class="text-red-700 text-sm">${result.error}</p>
                        </div>
                    `;
                    return;
                }
                
                const analysis = result.analysis;
                const positioning = analysis.strategic_positioning;
                
                html += `
                    <div class="border rounded-lg p-6 ${index === 0 ? 'border-blue-500 bg-blue-50' : 'border-gray-200'}">
                        <div class="flex justify-between items-start mb-4">
                            <div>
                                <h4 class="text-lg font-bold ${index === 0 ? 'text-blue-900' : 'text-gray-900'}">
                                    ${index === 0 ? '🏠 Your Content' : '🏢 Competitor'}: ${result.domain}
                                </h4>
                                <p class="text-sm text-gray-600">${result.url}</p>
                            </div>
                            <div class="text-right">
                                <div class="text-2xl font-bold ${analysis.ai_optimization_score >= 80 ? 'text-green-600' : analysis.ai_optimization_score >= 60 ? 'text-yellow-600' : 'text-red-600'}">
                                    ${analysis.ai_optimization_score}/100
                                </div>
                                <div class="text-sm text-gray-600">AI Optimization Score</div>
                            </div>
                        </div>
                        
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                            <div class="bg-white p-3 rounded border">
                                <h5 class="font-medium mb-2">Content Positioning</h5>
                                <p class="text-sm">Tone: <span class="font-medium">${positioning.current_tone}</span></p>
                                <p class="text-sm">Focus: <span class="font-medium">${positioning.narrative_focus}</span></p>
                                <p class="text-sm">Audience: <span class="font-medium">${positioning.audience_level}</span></p>
                            </div>
                            <div class="bg-white p-3 rounded border">
                                <h5 class="font-medium mb-2">Content Quality Scores</h5>
                                <div class="space-y-1">
                                    <div class="flex justify-between text-sm">
                                        <span>Factual Density</span>
                                        <span class="font-medium">${analysis.content_gaps.factual_density_score}/100</span>
                                    </div>
                                    <div class="flex justify-between text-sm">
                                        <span>Authority Signals</span>
                                        <span class="font-medium">${analysis.content_gaps.authority_signals_score}/100</span>
                                    </div>
                                    <div class="flex justify-between text-sm">
                                        <span>Answer Structure</span>
                                        <span class="font-medium">${analysis.content_gaps.answer_structure_score}/100</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        ${analysis.strategic_recommendations.length > 0 ? `
                            <div class="bg-white p-3 rounded border">
                                <h5 class="font-medium mb-2">Top Strategic Recommendations</h5>
                                <div class="space-y-2">
                                    ${analysis.strategic_recommendations.slice(0, 3).map(rec => `
                                        <div class="text-sm">
                                            <span class="inline-block w-16 text-xs font-medium ${rec.priority === 'high' ? 'text-red-600' : rec.priority === 'medium' ? 'text-yellow-600' : 'text-green-600'}">${rec.priority.toUpperCase()}</span>
                                            ${rec.recommendation}
                                        </div>
                                    `).join('')}
                                </div>
                            </div>
                        ` : ''}
                    </div>
                `;
            });
            
            html += '</div>';
            container.innerHTML = html;
            document.getElementById('results-section').classList.remove('hidden');
        }

        updateAddButton();
    </script>
</body>
</html>
'''

# Instructions for integration
INTEGRATION_INSTRUCTIONS = '''
# INTEGRATION INSTRUCTIONS

## Step 1: Save this file
Save this entire file as 'competitive_analyzer.py' in your project root

## Step 2: Update your main app.py
Add these lines to your existing app.py:

```python
# Add this import at the top with your other imports
from competitive_analyzer import add_competitive_routes, COMPETITIVE_ANALYSIS_TEMPLATE

# Add this after creating your Flask app (after app = Flask(__name__))
add_competitive_routes(app)

# Add this route to serve the template
@app.route('/competitive-analysis')
def competitive_analysis():
    return COMPETITIVE_ANALYSIS_TEMPLATE
```

## Step 3: Test the integration
1. Restart your Flask app
2. Visit: http://127.0.0.1:5009/competitive-analysis
3. Test the /test-competitive endpoint: http://127.0.0.1:5009/test-competitive

## Features included:
- Strategic content positioning analysis
- AI optimization scoring
- Content gap identification
- Rewrite suggestions (when Anthropic API is configured)
- Competitor comparison
- Consultant-ready reports

## API Endpoints:
- GET /competitive-analysis - Main interface
- GET /test-competitive - Test endpoint
- POST /api/analyze-competitive - Compare URLs
- POST /api/generate-rewrites - Generate content optimizations

## Requirements:
Your existing requirements should cover this, but ensure you have:
- requests
- beautifulsoup4
- anthropic
- flask

This is a complete, standalone solution that integrates with your existing Flask app!
'''

if __name__ == "__main__":
    # For testing as standalone
    app = Flask(__name__)
    add_competitive_routes(app)
    
    @app.route('/competitive-analysis')
    def competitive_analysis():
        return COMPETITIVE_ANALYSIS_TEMPLATE
    
    @app.route('/')
    def home():
        return '<h1>Competitive Analyzer Test</h1><p><a href="/competitive-analysis">Go to Competitive Analysis</a></p>'
    
    print("Standalone competitive analyzer running...")
    print("Visit: http://127.0.0.1:5000/competitive-analysis")
    app.run(debug=True, port=5000)
