"""Configuration for AI Discoverability Analyzer"""
import os
from datetime import timedelta

class Config:
    """Base configuration"""
    SECRET_KEY = os.environ.get('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///ai_analyzer.db')
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        # Fix for SQLAlchemy compatibility
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Session
    SESSION_TYPE = 'filesystem'
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # Mail settings (for email verification and notifications)
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@ai-analyzer.com')
    
    # Stripe
    STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY')
    STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY')
    STRIPE_WEBHOOK_SECRET = os.environ.get('STRIPE_WEBHOOK_SECRET')
    
    # Stripe Price IDs (you'll need to create these in Stripe Dashboard)
    STRIPE_PRICE_IDS = {
        'professional_monthly': os.environ.get('STRIPE_PROFESSIONAL_MONTHLY_PRICE_ID'),
        'professional_yearly': os.environ.get('STRIPE_PROFESSIONAL_YEARLY_PRICE_ID'),
        'agency_monthly': os.environ.get('STRIPE_AGENCY_MONTHLY_PRICE_ID'),
        'agency_yearly': os.environ.get('STRIPE_AGENCY_YEARLY_PRICE_ID'),
    }
    
    # Application settings
    ANALYSES_PER_PAGE = 20
    MAX_URL_LENGTH = 500
    
    # Security
    WTF_CSRF_ENABLED = True
    WTF_CSRF_TIME_LIMIT = None


# Tier configuration
TIER_LIMITS = {
    'free': {
        'analyses_per_month': 5,
        'api_calls': 0,
        'features': [
            'basic_analysis',
            'basic_recommendations',
            'basic_score'
        ],
        'export_formats': [],
        'white_label': False,
        'api_access': False,
        'priority_support': False,
        'multi_user': False,
        'custom_branding': False
    },
    'professional': {
        'analyses_per_month': -1,  # unlimited
        'api_calls': 100,
        'features': [
            'full_analysis',
            'advanced_recommendations',
            'detailed_score_breakdown',
            'historical_tracking',
            'competitor_comparison'
        ],
        'export_formats': ['pdf', 'csv'],
        'white_label': True,
        'api_access': True,
        'priority_support': False,
        'multi_user': False,
        'custom_branding': False
    },
    'agency': {
        'analyses_per_month': -1,  # unlimited
        'api_calls': 1000,
        'features': [
            'full_analysis',
            'advanced_recommendations',
            'detailed_score_breakdown',
            'historical_tracking',
            'competitor_comparison',
            'bulk_analysis',
            'client_management'
        ],
        'export_formats': ['pdf', 'csv', 'json'],
        'white_label': True,
        'api_access': True,
        'priority_support': True,
        'multi_user': True,
        'max_users': 5,
        'custom_branding': True
    },
    'enterprise': {
        'analyses_per_month': -1,  # unlimited
        'api_calls': -1,  # unlimited
        'features': [
            'full_analysis',
            'advanced_recommendations',
            'detailed_score_breakdown',
            'historical_tracking',
            'competitor_comparison',
            'bulk_analysis',
            'client_management',
            'custom_features'
        ],
        'export_formats': ['pdf', 'csv', 'json', 'xml'],
        'white_label': True,
        'api_access': True,
        'priority_support': True,
        'multi_user': True,
        'max_users': -1,  # unlimited
        'custom_branding': True
    }
}

# Pricing configuration (in cents)
PRICING = {
    'professional': {
        'monthly': 4900,  # $49.00
        'yearly': 49000,  # $490.00 (2 months free)
        'display_monthly': '$49',
        'display_yearly': '$490',
        'savings_yearly': '$98'
    },
    'agency': {
        'monthly': 19900,  # $199.00
        'yearly': 199000,  # $1990.00 (2 months free)
        'display_monthly': '$199',
        'display_yearly': '$1990',
        'savings_yearly': '$398'
    },
    'enterprise': {
        'custom': True,
        'display': 'Contact us'
    }
}
