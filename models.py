"""Database models for AI Discoverability Analyzer"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication and subscription management"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255))
    name = db.Column(db.String(100))
    company = db.Column(db.String(100))
    tier = db.Column(db.String(20), default='free', nullable=False)  # free, professional, agency, enterprise
    stripe_customer_id = db.Column(db.String(100), unique=True)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic')
    subscription = db.relationship('Subscription', backref='user', uselist=False)
    usage_records = db.relationship('Usage', backref='user', lazy='dynamic')
    
    def set_password(self, password):
        """Hash and set the user's password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if the provided password matches the hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_current_usage(self):
        """Get current month's usage statistics"""
        current_month = datetime.utcnow().strftime('%Y-%m')
        usage = Usage.query.filter_by(
            user_id=self.id,
            month_year=current_month
        ).first()
        
        if not usage:
            usage = Usage(user_id=self.id, month_year=current_month)
            db.session.add(usage)
            db.session.commit()
        
        return usage
    
    def can_analyze(self):
        """Check if user can perform another analysis based on tier limits"""
        from config import TIER_LIMITS
        
        if self.tier == 'free':
            usage = self.get_current_usage()
            return usage.analyses_count < TIER_LIMITS['free']['analyses_per_month']
        
        # Professional and above have unlimited analyses
        return True
    
    def increment_analysis_count(self):
        """Increment the analysis count for the current month"""
        usage = self.get_current_usage()
        usage.analyses_count += 1
        db.session.commit()
    
    def to_dict(self):
        """Convert user object to dictionary"""
        return {
            'id': self.id,
            'email': self.email,
            'name': self.name,
            'company': self.company,
            'tier': self.tier,
            'email_verified': self.email_verified,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Analysis(db.Model):
    """Analysis history and results"""
    __tablename__ = 'analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    session_id = db.Column(db.String(100), nullable=True)  # For anonymous users
    url_analyzed = db.Column(db.String(500), nullable=False)
    score = db.Column(db.Integer)
    analysis_data = db.Column(db.Text)  # JSON string of full analysis
    recommendations = db.Column(db.Text)  # AI recommendations
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_analysis_data(self, data):
        """Store analysis data as JSON"""
        self.analysis_data = json.dumps(data)
    
    def get_analysis_data(self):
        """Retrieve analysis data from JSON"""
        return json.loads(self.analysis_data) if self.analysis_data else {}
    
    def to_dict(self):
        """Convert analysis to dictionary"""
        return {
            'id': self.id,
            'url_analyzed': self.url_analyzed,
            'score': self.score,
            'analysis_data': self.get_analysis_data(),
            'recommendations': self.recommendations,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Subscription(db.Model):
    """Subscription management"""
    __tablename__ = 'subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    stripe_subscription_id = db.Column(db.String(100), unique=True)
    stripe_price_id = db.Column(db.String(100))
    tier = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), nullable=False)  # active, cancelled, past_due, etc.
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    cancel_at_period_end = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def is_active(self):
        """Check if subscription is currently active"""
        return self.status == 'active' or self.status == 'trialing'
    
    def to_dict(self):
        """Convert subscription to dictionary"""
        return {
            'id': self.id,
            'tier': self.tier,
            'status': self.status,
            'current_period_start': self.current_period_start.isoformat() if self.current_period_start else None,
            'current_period_end': self.current_period_end.isoformat() if self.current_period_end else None,
            'cancel_at_period_end': self.cancel_at_period_end
        }


class Usage(db.Model):
    """Monthly usage tracking"""
    __tablename__ = 'usage'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month_year = db.Column(db.String(7), nullable=False)  # Format: YYYY-MM
    analyses_count = db.Column(db.Integer, default=0)
    api_calls_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Unique constraint on user_id and month_year
    __table_args__ = (db.UniqueConstraint('user_id', 'month_year'),)
    
    def to_dict(self):
        """Convert usage to dictionary"""
        return {
            'month_year': self.month_year,
            'analyses_count': self.analyses_count,
            'api_calls_count': self.api_calls_count
        }


class ApiKey(db.Model):
    """API keys for programmatic access"""
    __tablename__ = 'api_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    key = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    last_used_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='api_keys')
    
    def to_dict(self):
        """Convert API key to dictionary (without exposing the actual key)"""
        return {
            'id': self.id,
            'name': self.name,
            'is_active': self.is_active,
            'last_used_at': self.last_used_at.isoformat() if self.last_used_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
