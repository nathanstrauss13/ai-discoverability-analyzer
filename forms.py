"""Forms for AI Discoverability Analyzer"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
import re

class LoginForm(FlaskForm):
    """User login form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class RegistrationForm(FlaskForm):
    """User registration form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    company = StringField('Company', validators=[Optional(), Length(max=100)])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')
    
    def validate_password(self, password):
        """Ensure password meets security requirements"""
        if not re.search(r'[A-Z]', password.data):
            raise ValidationError('Password must contain at least one uppercase letter.')
        if not re.search(r'[a-z]', password.data):
            raise ValidationError('Password must contain at least one lowercase letter.')
        if not re.search(r'[0-9]', password.data):
            raise ValidationError('Password must contain at least one number.')


class ResetPasswordRequestForm(FlaskForm):
    """Request password reset form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
    """Reset password form"""
    password = PasswordField('New Password', validators=[
        DataRequired(),
        Length(min=8, message='Password must be at least 8 characters long')
    ])
    password2 = PasswordField('Confirm New Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Reset Password')


class UpdateProfileForm(FlaskForm):
    """Update user profile form"""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    company = StringField('Company', validators=[Optional(), Length(max=100)])
    submit = SubmitField('Update Profile')


class ApiKeyForm(FlaskForm):
    """Create API key form"""
    name = StringField('API Key Name', validators=[
        DataRequired(),
        Length(min=3, max=100, message='Name must be between 3 and 100 characters')
    ])
    submit = SubmitField('Generate API Key')


class BulkAnalysisForm(FlaskForm):
    """Bulk URL analysis form (Agency tier)"""
    urls = TextAreaField('URLs (one per line)', validators=[
        DataRequired(),
        Length(min=1, message='Please enter at least one URL')
    ])
    submit = SubmitField('Analyze All URLs')
    
    def validate_urls(self, urls):
        """Validate URL list"""
        url_list = [url.strip() for url in urls.data.split('\n') if url.strip()]
        if len(url_list) > 100:
            raise ValidationError('Maximum 100 URLs allowed per bulk analysis.')
        
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        for url in url_list:
            if not url_pattern.match(url):
                raise ValidationError(f'Invalid URL format: {url}')


class ContactForm(FlaskForm):
    """Contact form for enterprise inquiries"""
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    company = StringField('Company', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    message = TextAreaField('Message', validators=[
        DataRequired(),
        Length(min=10, max=1000, message='Message must be between 10 and 1000 characters')
    ])
    submit = SubmitField('Send Message')
