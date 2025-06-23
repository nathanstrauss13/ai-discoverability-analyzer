# AI Discoverability Analyzer

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.2-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive web application that analyzes websites for AI and LLM optimization, evaluating both technical SEO factors and content quality. Built with Flask, powered by Claude AI, and enhanced with advanced NLP capabilities.

![AI Discoverability Analyzer](https://img.shields.io/badge/innate%20c3-AI%20Analyzer-005e30)

## 🚀 New: Content Quality Analysis

The analyzer now includes advanced content analysis features to help optimize brand content for AI discoverability:

- **Readability Scoring**: Flesch Reading Ease and grade level analysis
- **Promotional Language Detection**: Identifies marketing buzzwords and suggests factual alternatives
- **Factual Content Analysis**: Measures statistics, citations, and credibility signals
- **Answer Optimization**: Detects FAQ structures and direct answer patterns
- **Authority Signals**: Evaluates author attribution and external validation
- **Content Brevity**: Analyzes conciseness and removes filler content

## Features

### Technical Analysis
- **URL Analysis**: Enter any website URL to analyze its AI readiness
- **AI Readiness Score**: Comprehensive scoring (0-100) with separate technical and content scores
- **Technical SEO Evaluation**:
  - Page title and meta descriptions
  - Heading structure (H1-H6)
  - Image alt text coverage
  - Structured data presence
  - Semantic HTML usage
  - robots.txt and sitemap.xml
  - Open Graph and Twitter Card tags

### Content Quality Analysis
- **Readability Metrics**: AI-friendly content assessment
- **Promotional vs Factual**: Balance between marketing and informational content
- **Answer Structure**: FAQ detection and Q&A optimization
- **Credibility Scoring**: Authority and trust signals
- **Brevity Analysis**: Conciseness and clarity metrics

### AI-Powered Recommendations
- **Structured Recommendations**: Organized by priority and impact
- **Consulting Opportunities**: Identifies areas for professional services
- **Implementation Roadmap**: Clear action items with expected outcomes

## Installation

1. Clone or download this directory
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up content analysis dependencies:
   ```bash
   python setup_content_analysis.py
   ```
4. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your Anthropic API key:
     ```
     ANTHROPIC_API_KEY=your_api_key_here
     FLASK_SECRET_KEY=your_secret_key_here
     ```

## Usage

1. Run the application:
   ```bash
   python app.py
   ```
2. Open your browser to `http://localhost:5001`
3. Enter a URL to analyze
4. Review the AI readiness score and recommendations

### Example URLs to Try

Some websites block automated requests. Here are examples that typically work:
- `https://example.com` - Simple test site
- `https://wikipedia.org` - Well-structured content
- `https://github.com` - Good semantic HTML
- Most personal blogs and smaller websites

Note: Large corporate sites often have anti-bot protection that may block analysis.

## How It Works

The analyzer evaluates websites across two main dimensions:

### Technical Factors
- **Content Structure**: Proper use of headings, semantic HTML elements
- **Metadata**: Title tags, meta descriptions for context
- **Accessibility**: Alt text for images, proper markup
- **Machine Readability**: Structured data, clean HTML
- **Crawlability**: robots.txt, sitemap.xml, canonical tags

### Content Quality Factors
- **Readability**: Text complexity and clarity for AI comprehension
- **Factual Density**: Statistics, citations, and verifiable information
- **Answer Structure**: FAQ patterns and direct answer formats
- **Authority Signals**: Author attribution and credibility markers
- **Content Tone**: Balance between promotional and informational

## Scoring System

### Overall Score (0-100)
- **80-100**: Excellent - Well-optimized for AI systems
- **60-79**: Good - Has room for improvement
- **0-59**: Needs Work - Significant improvements recommended

### Sub-Scores
- **Technical Score**: Traditional SEO and technical factors
- **Content Score**: Content quality and AI optimization metrics

## Use Cases

### For Consultants
- **Sales Tool**: Demonstrate AI optimization gaps to prospects
- **Service Packages**: Offer technical fixes, content rewrites, and authority building
- **Progress Tracking**: Show improvements over time

### For Brands
- **Self-Assessment**: Understand current AI visibility
- **Competitive Analysis**: Compare against industry standards
- **Implementation Guide**: Follow specific recommendations

## Technologies Used

- **Flask**: Python web framework
- **Beautiful Soup**: HTML parsing and analysis
- **NLTK**: Natural language processing
- **Textstat**: Readability calculations
- **spaCy**: Advanced NLP (optional)
- **Anthropic Claude API**: AI-powered recommendations
- **Tailwind CSS**: Modern, responsive design

## Documentation

- [AI Content Optimization Guide](AI_CONTENT_OPTIMIZATION_GUIDE.md) - Comprehensive guide for using the tool as a consulting sales enabler
- [AI Agent Brand Insights](AI_AGENT_BRAND_INSIGHTS.md) - Industry research and optimization strategies

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
