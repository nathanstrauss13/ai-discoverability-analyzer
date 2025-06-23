"""
Local testing script for AI Discoverability Analyzer Freemium
This script sets up a minimal environment for testing the UX locally
"""
import os
import sys
from datetime import datetime

# Set minimal environment variables for local testing
os.environ['FLASK_SECRET_KEY'] = 'dev-secret-key-for-testing'
os.environ['ANTHROPIC_API_KEY'] = os.environ.get('ANTHROPIC_API_KEY', '')

# Import the necessary functions from the original app
from app import fetch_webpage_content, analyze_webpage_structure, generate_ai_recommendations, calculate_ai_readiness_score

# Import Flask and required extensions
try:
    from flask import Flask, render_template, request, jsonify, redirect, url_for, session
    from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
    print("✓ Flask and Flask-Login imported successfully")
except ImportError as e:
    print(f"❌ Missing dependency: {e}")
    print("\nPlease install required packages:")
    print("pip3 install Flask Flask-Login Flask-SQLAlchemy Flask-WTF")
    sys.exit(1)

# Create a minimal Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-for-testing'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_ai_analyzer.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Mock user class for testing
class MockUser(UserMixin):
    def __init__(self, id, email, name, tier):
        self.id = id
        self.email = email
        self.name = name
        self.tier = tier
        self.company = "Test Company"
        self.created_at = datetime.now()
        
    def get_id(self):
        return str(self.id)

# Create test users
test_users = {
    'free@test.com': MockUser(1, 'free@test.com', 'Free User', 'free'),
    'pro@test.com': MockUser(2, 'pro@test.com', 'Pro User', 'professional'),
    'agency@test.com': MockUser(3, 'agency@test.com', 'Agency User', 'agency')
}

@login_manager.user_loader
def load_user(user_id):
    for user in test_users.values():
        if user.get_id() == user_id:
            return user
    return None

# Mock data for testing
mock_usage = {
    'analyses_count': 3,
    'api_calls_count': 45,
    'month_year': '2025-06'
}

mock_analyses = [
    {
        'id': 1,
        'url_analyzed': 'https://example.com',
        'score': 85,
        'created_at': type('obj', (object,), {'strftime': lambda self, fmt: 'June 15, 2025 at 02:30 PM'})()
    },
    {
        'id': 2,
        'url_analyzed': 'https://test-site.com',
        'score': 62,
        'created_at': type('obj', (object,), {'strftime': lambda self, fmt: 'June 14, 2025 at 10:15 AM'})()
    }
]

tier_limits = {
    'free': {
        'analyses_per_month': 5,
        'api_calls': 0
    },
    'professional': {
        'analyses_per_month': -1,
        'api_calls': 100
    },
    'agency': {
        'analyses_per_month': -1,
        'api_calls': 1000
    }
}

# Routes
@app.route('/')
def index():
    """Main analysis page"""
    return render_template('index.html', user=current_user, stripe_key='pk_test_dummy')

@app.route('/login')
def login():
    """Show login options"""
    return '''
    <html>
    <head>
        <title>Test Login - AI Discoverability Analyzer</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-100 p-8">
        <div class="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
            <h1 class="text-2xl font-bold mb-4">Test Login</h1>
            <p class="mb-4">Choose a test account to explore the UI:</p>
            <div class="space-y-2">
                <a href="/test-login/free@test.com" class="block w-full bg-gray-500 text-white py-2 px-4 rounded hover:bg-gray-600 text-center">
                    Login as Free User
                </a>
                <a href="/test-login/pro@test.com" class="block w-full bg-green-500 text-white py-2 px-4 rounded hover:bg-green-600 text-center">
                    Login as Professional User
                </a>
                <a href="/test-login/agency@test.com" class="block w-full bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600 text-center">
                    Login as Agency User
                </a>
            </div>
            <hr class="my-4">
            <a href="/" class="text-blue-500 hover:underline">← Back to analyzer</a>
        </div>
    </body>
    </html>
    '''

@app.route('/test-login/<email>')
def test_login(email):
    """Quick login for testing"""
    if email in test_users:
        user = test_users[email]
        login_user(user)
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/logout')
@login_required
def logout():
    """Logout"""
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    """User dashboard"""
    usage_percent = 0
    if current_user.tier == 'free':
        usage_percent = (mock_usage['analyses_count'] / tier_limits['free']['analyses_per_month']) * 100
    
    return render_template('dashboard.html',
                         user=current_user,
                         recent_analyses=mock_analyses if current_user.id > 1 else [],
                         usage=type('obj', (object,), mock_usage)(),
                         usage_percent=usage_percent,
                         tier_limits=tier_limits[current_user.tier])

@app.route('/pricing')
def pricing():
    """Pricing page"""
    pricing_data = {
        'professional': {
            'monthly': 4900,
            'yearly': 49000,
            'display_monthly': '$49',
            'display_yearly': '$490',
            'savings_yearly': '$98'
        },
        'agency': {
            'monthly': 19900,
            'yearly': 199000,
            'display_monthly': '$199',
            'display_yearly': '$1990',
            'savings_yearly': '$398'
        }
    }
    return render_template('pricing.html',
                         pricing=pricing_data,
                         tier_limits=tier_limits,
                         user=current_user,
                         stripe_key='pk_test_dummy')

@app.route('/auth/login')
def auth_login():
    """Redirect to test login"""
    return redirect(url_for('login'))

@app.route('/auth/register')
def auth_register():
    """Mock registration page"""
    return '''
    <html>
    <head>
        <title>Register - AI Discoverability Analyzer</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
    </head>
    <body class="bg-gray-100 p-8">
        <div class="max-w-md mx-auto bg-white rounded-lg shadow-lg p-6">
            <h1 class="text-2xl font-bold mb-4">Registration (Test Mode)</h1>
            <p class="mb-4">In production, users would register here with email verification.</p>
            <p class="mb-4">For testing, use the test login instead.</p>
            <a href="/login" class="bg-blue-500 text-white py-2 px-4 rounded hover:bg-blue-600">
                Go to Test Login
            </a>
        </div>
    </body>
    </html>
    '''

@app.route('/auth/logout')
def auth_logout():
    """Logout route"""
    return logout()

# Mock analyze endpoint
@app.route('/analyze', methods=['POST'])
def analyze():
    """Mock analyze endpoint for testing"""
    data = request.get_json()
    url = data.get('url', '').strip()
    
    # Check if user is logged in and has reached limit
    if current_user.is_authenticated and current_user.tier == 'free':
        if mock_usage['analyses_count'] >= 5:
            return jsonify({
                'error': 'You have reached your monthly analysis limit. Please upgrade your plan.',
                'upgrade_url': url_for('pricing')
            }), 403
    
    # Return mock data for testing
    return jsonify({
        'success': True,
        'analysis': {
            'url': url,
            'title': 'Test Page',
            'meta_description': 'Test description',
            'headings': {'h1': ['Test Heading'], 'h2': [], 'h3': [], 'h4': [], 'h5': [], 'h6': []},
            'images': {'total': 5, 'with_alt': 3, 'without_alt': 2},
            'structured_data': True,
            'robots_txt': True,
            'sitemap_xml': False
        },
        'recommendations': 'This is a test recommendation. In production, AI-powered recommendations would appear here.',
        'score': 75,
        'score_breakdown': {
            'categories': [
                {'name': 'Title & Meta', 'earned': 10, 'possible': 12, 'details': 'Good'},
                {'name': 'Structure', 'earned': 8, 'possible': 12, 'details': 'Needs work'}
            ],
            'final_score': 75
        } if current_user.is_authenticated and current_user.tier != 'free' else None
    })

# Error handlers
@app.errorhandler(404)
def not_found(e):
    return "Page not found. <a href='/'>Go home</a>", 404

if __name__ == '__main__':
    print("\n" + "="*60)
    print("AI DISCOVERABILITY ANALYZER - FREEMIUM TEST MODE")
    print("="*60)
    print("\nStarting local test server...")
    print("\nAvailable test accounts:")
    print("  - Free User: free@test.com")
    print("  - Professional User: pro@test.com")
    print("  - Agency User: agency@test.com")
    print("\nTest URLs:")
    print(f"  - Home: http://localhost:5001/")
    print(f"  - Login: http://localhost:5001/login")
    print(f"  - Pricing: http://localhost:5001/pricing")
    print(f"  - Dashboard: http://localhost:5001/dashboard (requires login)")
    print("\n" + "="*60 + "\n")
    
    app.run(debug=True, port=5001)
