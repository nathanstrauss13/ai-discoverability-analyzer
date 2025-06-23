"""
AI Discoverability Analyzer - Freemium SaaS Version
Main application file with authentication, subscription management, and tier-based features
"""
import os
import re
import requests
import json
import secrets
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_login import LoginManager, login_required, current_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin
from datetime import datetime
from anthropic import Anthropic
from dotenv import load_dotenv
import stripe

# Import our modules
from models import db, User, Analysis, Subscription, Usage, ApiKey
from config import Config, TIER_LIMITS, PRICING
from auth import auth_bp, init_session
from email_utils import mail, send_usage_limit_warning_email

# Load .env file if it exists (for local development)
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
mail.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Initialize Stripe
stripe.api_key = app.config['STRIPE_SECRET_KEY']

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

# Register blueprints
app.register_blueprint(auth_bp)

@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login"""
    return User.query.get(int(user_id))

@app.before_request
def before_request():
    """Initialize session for anonymous users"""
    init_session()

@app.route('/')
def index():
    """Landing page with analysis tool"""
    return render_template('index.html', 
                         user=current_user,
                         stripe_key=app.config['STRIPE_PUBLISHABLE_KEY'])

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    # Get user's recent analyses
    recent_analyses = Analysis.query.filter_by(user_id=current_user.id)\
                                   .order_by(Analysis.created_at.desc())\
                                   .limit(10).all()
    
    # Get current usage
    usage = current_user.get_current_usage()
    
    # Calculate usage percentage for free tier
    usage_percent = 0
    if current_user.tier == 'free':
        limit = TIER_LIMITS['free']['analyses_per_month']
        usage_percent = (usage.analyses_count / limit) * 100 if limit > 0 else 0
    
    return render_template('dashboard.html',
                         user=current_user,
                         recent_analyses=recent_analyses,
                         usage=usage,
                         usage_percent=usage_percent,
                         tier_limits=TIER_LIMITS[current_user.tier])

@app.route('/pricing')
def pricing():
    """Pricing page"""
    return render_template('pricing.html',
                         pricing=PRICING,
                         tier_limits=TIER_LIMITS,
                         user=current_user)

@app.route('/analyze', methods=['POST'])
@limiter.limit("30 per hour")
def analyze():
    """Analyze a URL - with tier-based restrictions"""
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'Please provide a URL'}), 400
    
    # Check if user can perform analysis
    if current_user.is_authenticated:
        if not current_user.can_analyze():
            return jsonify({
                'error': 'You have reached your monthly analysis limit. Please upgrade your plan.',
                'upgrade_url': url_for('pricing')
            }), 403
    else:
        # Anonymous user - check session-based limits
        session_id = session.get('session_id')
        if session_id:
            # Count analyses in current month
            current_month = datetime.utcnow().strftime('%Y-%m')
            month_start = datetime.strptime(current_month, '%Y-%m')
            
            anonymous_count = Analysis.query.filter_by(session_id=session_id)\
                                          .filter(Analysis.created_at >= month_start)\
                                          .count()
            
            if anonymous_count >= 3:  # Anonymous users get 3 free analyses
                return jsonify({
                    'error': 'You have reached the free analysis limit. Please sign up for more analyses.',
                    'signup_url': url_for('auth.register')
                }), 403
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://', 'file://')):
        url = 'https://' + url
    
    # Check if URL points to a PDF
    if url.lower().endswith('.pdf') or 'application/pdf' in url.lower():
        error_msg = (
            '**PDF files cannot be analyzed directly.**\n\n'
            'This tool is designed to analyze HTML web pages, not PDF documents.'
        )
        return jsonify({'error': error_msg}), 400
    
    # Fetch webpage content
    html_content = fetch_webpage_content(url)
    if not html_content:
        error_msg = 'Unable to fetch the webpage. The site may be blocking automated requests.'
        return jsonify({'error': error_msg}), 400
    
    # Analyze webpage structure
    analysis_data = analyze_webpage_structure(html_content, url)
    
    # Generate AI recommendations based on tier
    if current_user.is_authenticated and current_user.tier != 'free':
        ai_recommendations = generate_ai_recommendations(analysis_data)
    else:
        ai_recommendations = generate_basic_recommendations(analysis_data)
    
    # Calculate score
    score, score_breakdown = calculate_ai_readiness_score(analysis_data)
    
    # Save analysis to database
    analysis = Analysis(
        user_id=current_user.id if current_user.is_authenticated else None,
        session_id=session.get('session_id') if not current_user.is_authenticated else None,
        url_analyzed=url,
        score=score,
        recommendations=ai_recommendations
    )
    analysis.set_analysis_data(analysis_data)
    db.session.add(analysis)
    
    # Increment usage count for authenticated users
    if current_user.is_authenticated:
        current_user.increment_analysis_count()
        
        # Send warning email if approaching limit (free tier only)
        if current_user.tier == 'free':
            usage = current_user.get_current_usage()
            limit = TIER_LIMITS['free']['analyses_per_month']
            usage_percent = (usage.analyses_count / limit) * 100
            
            if usage_percent >= 80 and usage.analyses_count == 4:  # First time hitting 80%
                send_usage_limit_warning_email(current_user, int(usage_percent))
    
    db.session.commit()
    
    # Prepare response based on tier
    response_data = {
        'success': True,
        'analysis': analysis_data,
        'recommendations': ai_recommendations,
        'score': score,
        'timestamp': datetime.now().isoformat()
    }
    
    # Include detailed breakdown for paid tiers
    if current_user.is_authenticated and current_user.tier != 'free':
        response_data['score_breakdown'] = score_breakdown
    
    return jsonify(response_data)

@app.route('/api/analyze', methods=['POST'])
@limiter.limit("10 per minute")
def api_analyze():
    """API endpoint for analysis - requires API key"""
    api_key = request.headers.get('X-API-Key')
    
    if not api_key:
        return jsonify({'error': 'API key required'}), 401
    
    # Validate API key
    key_record = ApiKey.query.filter_by(key=api_key, is_active=True).first()
    if not key_record:
        return jsonify({'error': 'Invalid API key'}), 401
    
    # Update last used
    key_record.last_used_at = datetime.utcnow()
    
    # Check API usage limits
    user = key_record.user
    usage = user.get_current_usage()
    tier_limit = TIER_LIMITS[user.tier]['api_calls']
    
    if tier_limit != -1 and usage.api_calls_count >= tier_limit:
        return jsonify({'error': 'API call limit exceeded for this month'}), 429
    
    # Process the analysis request
    data = request.get_json()
    url = data.get('url', '').strip()
    
    if not url:
        return jsonify({'error': 'URL parameter required'}), 400
    
    # Perform analysis (similar to main analyze endpoint)
    # ... (analysis code here) ...
    
    # Increment API usage
    usage.api_calls_count += 1
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': 'API endpoint coming soon'
    })

@app.route('/export/<int:analysis_id>/<format>')
@login_required
def export_analysis(analysis_id, format):
    """Export analysis in various formats (paid feature)"""
    # Check if user's tier allows exports
    if current_user.tier == 'free':
        flash('Export feature is only available for paid plans.', 'warning')
        return redirect(url_for('pricing'))
    
    # Get the analysis
    analysis = Analysis.query.get_or_404(analysis_id)
    
    # Verify ownership
    if analysis.user_id != current_user.id:
        flash('You do not have permission to export this analysis.', 'error')
        return redirect(url_for('dashboard'))
    
    # Generate export based on format
    if format == 'pdf':
        # TODO: Implement PDF generation
        flash('PDF export coming soon!', 'info')
    elif format == 'csv':
        # TODO: Implement CSV generation
        flash('CSV export coming soon!', 'info')
    else:
        flash('Invalid export format.', 'error')
    
    return redirect(url_for('dashboard'))

# Stripe webhook endpoint
@app.route('/stripe/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhook events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, app.config['STRIPE_WEBHOOK_SECRET']
        )
    except ValueError:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        # Payment successful, provision subscription
        session = event['data']['object']
        
        # TODO: Update user subscription in database
        
    elif event['type'] == 'customer.subscription.deleted':
        # Subscription cancelled
        subscription = event['data']['object']
        
        # TODO: Downgrade user to free tier
    
    return jsonify({'received': True}), 200

# Keep existing helper functions from original app.py
def fetch_webpage_content(url):
    """Fetch and parse webpage content from HTTP(S) or local file:// URLs."""
    # (Keep the existing implementation)
    pass

def analyze_webpage_structure(html_content, url):
    """Analyze the structure and content of a webpage."""
    # (Keep the existing implementation)
    pass

def generate_ai_recommendations(analysis):
    """Generate AI recommendations for paid tiers."""
    # (Keep the existing implementation)
    pass

def generate_basic_recommendations(analysis):
    """Generate basic recommendations for free tier."""
    return """Based on your analysis, here are some general recommendations:

1. **Improve Your Score**: Your site needs optimization for AI discoverability.
2. **Add Missing Elements**: Ensure you have proper meta tags and structured data.
3. **Enhance Content Structure**: Use semantic HTML and clear heading hierarchy.

For detailed AI-powered recommendations and advanced features, upgrade to a paid plan."""

def calculate_ai_readiness_score(analysis):
    """Calculate an AI readiness score."""
    # (Keep the existing implementation)
    pass

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    debug_mode = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    print(f"Starting Flask app on port {port}")
    print(f"Debug mode: {debug_mode}")
    print(f"Stripe configured: {'Yes' if app.config['STRIPE_SECRET_KEY'] else 'No'}")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=port)
