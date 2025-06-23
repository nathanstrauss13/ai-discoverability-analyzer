"""Email utilities for AI Discoverability Analyzer"""
from flask import render_template, url_for, current_app
from flask_mail import Mail, Message
from threading import Thread
import secrets
from datetime import datetime, timedelta
from itsdangerous import URLSafeTimedSerializer

mail = Mail()

def send_async_email(app, msg):
    """Send email asynchronously"""
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    """Send an email"""
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    
    # Send asynchronously to avoid blocking
    Thread(target=send_async_email, 
           args=(current_app._get_current_object(), msg)).start()

def generate_token(data, salt, expiration=3600):
    """Generate a secure token"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    return serializer.dumps(data, salt=salt)

def verify_token(token, salt, expiration=3600):
    """Verify a token and return the data"""
    serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    try:
        data = serializer.loads(token, salt=salt, max_age=expiration)
        return data
    except:
        return None

def send_verification_email(user):
    """Send email verification link"""
    token = generate_token({'user_id': user.id}, salt='email-verification')
    
    verify_url = url_for('auth.verify_email', token=token, _external=True)
    
    subject = 'Verify Your Email - AI Discoverability Analyzer'
    
    text_body = f"""
Hello {user.name or 'there'},

Welcome to AI Discoverability Analyzer! Please verify your email address by clicking the link below:

{verify_url}

This link will expire in 24 hours.

If you didn't create an account, please ignore this email.

Best regards,
The AI Discoverability Analyzer Team
"""
    
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #005e30;">Welcome to AI Discoverability Analyzer!</h2>
        
        <p>Hello {user.name or 'there'},</p>
        
        <p>Thank you for signing up! Please verify your email address to activate your account.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{verify_url}" 
               style="background-color: #005e30; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Verify Email Address
            </a>
        </div>
        
        <p style="color: #666; font-size: 14px;">
            This link will expire in 24 hours. If you didn't create an account, 
            please ignore this email.
        </p>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <p style="color: #666; font-size: 12px;">
            Best regards,<br>
            The AI Discoverability Analyzer Team
        </p>
    </div>
</body>
</html>
"""
    
    send_email(subject, 
               current_app.config['MAIL_DEFAULT_SENDER'],
               [user.email],
               text_body,
               html_body)

def send_password_reset_email(user):
    """Send password reset email"""
    token = generate_token({'user_id': user.id}, salt='password-reset')
    
    reset_url = url_for('auth.reset_password', token=token, _external=True)
    
    subject = 'Reset Your Password - AI Discoverability Analyzer'
    
    text_body = f"""
Hello {user.name or 'there'},

You requested a password reset for your AI Discoverability Analyzer account.

Click the link below to reset your password:

{reset_url}

This link will expire in 1 hour.

If you didn't request a password reset, please ignore this email and your password will remain unchanged.

Best regards,
The AI Discoverability Analyzer Team
"""
    
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #005e30;">Password Reset Request</h2>
        
        <p>Hello {user.name or 'there'},</p>
        
        <p>You requested a password reset for your AI Discoverability Analyzer account.</p>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{reset_url}" 
               style="background-color: #005e30; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Reset Password
            </a>
        </div>
        
        <p style="color: #666; font-size: 14px;">
            This link will expire in 1 hour. If you didn't request a password reset, 
            please ignore this email and your password will remain unchanged.
        </p>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <p style="color: #666; font-size: 12px;">
            Best regards,<br>
            The AI Discoverability Analyzer Team
        </p>
    </div>
</body>
</html>
"""
    
    send_email(subject,
               current_app.config['MAIL_DEFAULT_SENDER'],
               [user.email],
               text_body,
               html_body)

def send_subscription_confirmation_email(user, tier):
    """Send subscription confirmation email"""
    subject = f'Subscription Confirmed - {tier.title()} Plan'
    
    text_body = f"""
Hello {user.name or 'there'},

Your subscription to the {tier.title()} plan has been confirmed!

You now have access to:
- Unlimited analyses
- Advanced AI recommendations
- API access
- Export functionality
- And much more!

Log in to your dashboard to start using your new features:
{url_for('dashboard', _external=True)}

If you have any questions, please don't hesitate to contact us.

Best regards,
The AI Discoverability Analyzer Team
"""
    
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #005e30;">Welcome to {tier.title()} Plan!</h2>
        
        <p>Hello {user.name or 'there'},</p>
        
        <p>Your subscription has been confirmed. You now have access to all the premium features!</p>
        
        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin: 20px 0;">
            <h3 style="margin-top: 0;">Your {tier.title()} Plan includes:</h3>
            <ul style="list-style-type: none; padding-left: 0;">
                <li>✓ Unlimited analyses</li>
                <li>✓ Advanced AI recommendations</li>
                <li>✓ API access</li>
                <li>✓ PDF & CSV exports</li>
                <li>✓ White-label reports</li>
                <li>✓ Priority support</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{url_for('dashboard', _external=True)}" 
               style="background-color: #005e30; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Go to Dashboard
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <p style="color: #666; font-size: 12px;">
            Best regards,<br>
            The AI Discoverability Analyzer Team
        </p>
    </div>
</body>
</html>
"""
    
    send_email(subject,
               current_app.config['MAIL_DEFAULT_SENDER'],
               [user.email],
               text_body,
               html_body)

def send_usage_limit_warning_email(user, usage_percent):
    """Send warning when approaching usage limits"""
    subject = 'Usage Limit Warning - AI Discoverability Analyzer'
    
    text_body = f"""
Hello {user.name or 'there'},

You've used {usage_percent}% of your monthly analysis limit.

Your current plan allows 5 analyses per month. Consider upgrading to Professional 
for unlimited analyses and advanced features.

Upgrade now: {url_for('pricing', _external=True)}

Best regards,
The AI Discoverability Analyzer Team
"""
    
    html_body = f"""
<html>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #ff9500;">Usage Limit Warning</h2>
        
        <p>Hello {user.name or 'there'},</p>
        
        <p>You've used <strong>{usage_percent}%</strong> of your monthly analysis limit.</p>
        
        <div style="background-color: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0;">
            <p style="margin: 0;">Your Free plan includes 5 analyses per month. 
            Upgrade to Professional for unlimited analyses!</p>
        </div>
        
        <div style="text-align: center; margin: 30px 0;">
            <a href="{url_for('pricing', _external=True)}" 
               style="background-color: #005e30; color: white; padding: 12px 30px; 
                      text-decoration: none; border-radius: 5px; display: inline-block;">
                Upgrade to Professional
            </a>
        </div>
        
        <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
        
        <p style="color: #666; font-size: 12px;">
            Best regards,<br>
            The AI Discoverability Analyzer Team
        </p>
    </div>
</body>
</html>
"""
    
    send_email(subject,
               current_app.config['MAIL_DEFAULT_SENDER'],
               [user.email],
               text_body,
               html_body)
