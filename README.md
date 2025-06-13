# AI Discoverability Analyzer

[![Python](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3.2-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A web application that analyzes websites to determine how well they are optimized for AI and Large Language Model (LLM) crawling and processing. Built with Flask and powered by Claude AI for intelligent recommendations.

![AI Discoverability Analyzer](https://img.shields.io/badge/innate%20c3-AI%20Analyzer-005e30)

## Features

- **URL Analysis**: Enter any website URL to analyze its AI readiness
- **AI Readiness Score**: Get a comprehensive score (0-100) based on multiple factors
- **Technical Analysis**: Detailed breakdown of:
  - Page title and meta descriptions
  - Heading structure (H1-H6)
  - Image alt text coverage
  - Structured data presence
  - Semantic HTML usage
  - Table and form elements
- **AI-Powered Recommendations**: Receive specific, actionable recommendations powered by Claude AI
- **Clean, Modern UI**: Responsive design that works on all devices

## Installation

1. Clone or download this directory
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Set up environment variables:
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

The analyzer evaluates websites based on several key factors that affect AI/LLM processing:

- **Content Structure**: Proper use of headings, semantic HTML elements
- **Metadata**: Title tags, meta descriptions for context
- **Accessibility**: Alt text for images, proper markup
- **Machine Readability**: Structured data, clean HTML
- **Data Organization**: Tables for tabular data, clear content hierarchy

## Scoring System

- **80-100**: Excellent - Well-optimized for AI systems
- **60-79**: Good - Has room for improvement
- **0-59**: Needs Work - Significant improvements recommended

## Technologies Used

- Flask (Python web framework)
- Beautiful Soup (HTML parsing)
- Anthropic Claude API (AI recommendations)
- Modern CSS with responsive design
