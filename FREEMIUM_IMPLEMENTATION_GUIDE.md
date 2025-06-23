# AI Discoverability Analyzer - Freemium SaaS Implementation Guide

## Overview
This guide walks you through implementing the freemium SaaS model for your AI Discoverability Analyzer. The implementation includes user authentication, subscription management, tier-based features, and Stripe integration.

## Architecture Summary

### New Components Added:
1. **User Authentication System** - Registration, login, email verification
2. **Database Models** - Users, subscriptions, usage tracking, API keys
3. **Tier Management** - Free, Professional, Agency, Enterprise
4. **Payment Integration** - Stripe for subscription billing
5. **Usage Tracking** - Monthly limits and API call tracking
6. **Email System** - Verification, notifications, receipts

## Setup Instructions

### 1. Environment Variables
Add these to your `.env` file:

```bash
# Database (for production, use PostgreSQL)
DATABASE_URL=postgresql://username:password@localhost/ai_analyzer_db

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=noreply@ai-analyzer.com

# Stripe Keys (get from https://dashboard.stripe.com)
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Stripe Price IDs (create in Stripe Dashboard)
STRIPE_PROFESSIONAL_MONTHLY_PRICE_ID=price_...
STRIPE_PROFESSIONAL_YEARLY_PRICE_ID=price_...
STRIPE_AGENCY_MONTHLY_PRICE_ID=price_...
STRIPE_AGENCY_YEARLY_PRICE_ID=price_...
```

### 2. Database Setup

#### Local Development (SQLite):
```bash
# The database will be created automatically when you run the app
python app_freemium.py
```

#### Production (PostgreSQL):
```bash
# Install PostgreSQL
brew install postgresql  # macOS
sudo apt-get install postgresql  # Ubuntu

# Create database
createdb ai_analyzer_db

# Run migrations (after setting DATABASE_URL)
python
>>> from app_freemium import app, db
>>> with app.app_context():
...     db.create_all()
```

### 3. Stripe Setup

#### Create Products and Prices in Stripe Dashboard:

1. Go to https://dashboard.stripe.com/products
2. Create products:
   - **Professional Plan**
     - Monthly: $49.00
     - Yearly: $490.00 (save $98)
   - **Agency Plan**
     - Monthly: $199.00
     - Yearly: $1990.00 (save $398)

3. Copy the Price IDs to your `.env` file

#### Set up Webhook:
1. Go to https://dashboard.stripe.com/webhooks
2. Add endpoint: `https://your-domain.com/stripe/webhook`
3. Select events:
   - `checkout.session.completed`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
4. Copy the webhook secret to your `.env` file

### 4. Email Setup

#### Gmail App Password:
1. Enable 2-factor authentication on your Gmail account
2. Go to https://myaccount.google.com/apppasswords
3. Generate an app password
4. Use this password in `MAIL_PASSWORD`

#### Production Email Service:
Consider using SendGrid, Mailgun, or AWS SES for production

### 5. Install Dependencies

```bash
cd "innate apps/ai-discoverability-analyzer"
pip install -r requirements.txt
```

### 6. Run the Application

```bash
# Development
python app_freemium.py

# Production (with Gunicorn)
gunicorn app_freemium:app -w 4 -b 0.0.0.0:5000
```

## Feature Implementation Details

### User Registration Flow:
1. User fills out registration form
2. Account created with `tier='free'`
3. Verification email sent
4. User clicks verification link
5. Account activated, can log in

### Analysis Limits:
- **Anonymous users**: 3 analyses per month (tracked by session)
- **Free tier**: 5 analyses per month
- **Paid tiers**: Unlimited analyses

### Tier-Based Features:

#### Free Tier Restrictions:
- Basic AI recommendations only
- No score breakdown details
- No export functionality
- No API access

#### Professional Features:
- Full AI recommendations
- Detailed score breakdown
- PDF/CSV export
- API access (100 calls/month)
- White-label reports

#### Agency Features:
- Everything in Professional
- Multi-user support (up to 5)
- Bulk URL analysis
- Custom branding
- API access (1000 calls/month)

### API Implementation:
```python
# Example API usage
import requests

headers = {
    'X-API-Key': 'your-api-key-here',
    'Content-Type': 'application/json'
}

data = {
    'url': 'https://example.com'
}

response = requests.post(
    'https://ai-analyzer.com/api/analyze',
    headers=headers,
    json=data
)
```

## Deployment Considerations

### 1. Security:
- Use HTTPS in production
- Set strong SECRET_KEY
- Enable CSRF protection
- Implement rate limiting
- Validate all user inputs

### 2. Performance:
- Use PostgreSQL for production
- Implement caching (Redis)
- Use CDN for static assets
- Optimize database queries
- Consider background tasks for heavy operations

### 3. Monitoring:
- Set up error tracking (Sentry)
- Monitor API usage
- Track subscription metrics
- Set up alerts for failures

### 4. Backup:
- Daily database backups
- Store backups offsite
- Test restore procedures
- Document recovery process

## Testing the Implementation

### 1. Test User Registration:
```bash
# Register a new user
# Verify email functionality
# Check database for user record
```

### 2. Test Analysis Limits:
```bash
# Create free account
# Perform 5 analyses
# Verify 6th analysis is blocked
# Check usage tracking in database
```

### 3. Test Stripe Integration:
```bash
# Use Stripe test cards
# 4242 4242 4242 4242 (Success)
# 4000 0000 0000 0002 (Decline)
```

### 4. Test API Access:
```bash
# Generate API key for user
# Make API requests
# Verify rate limiting works
```

## Migration from Current Version

### 1. Notify Current Users:
- Send email about new features
- Offer 30-day Professional trial
- Provide migration guide

### 2. Database Migration:
```python
# Script to migrate existing analyses
from app_freemium import app, db
from models import Analysis

with app.app_context():
    # Migrate anonymous analyses to new schema
    # Add session_id field to existing records
    pass
```

### 3. Gradual Rollout:
1. Deploy new version to staging
2. Test with small user group
3. Monitor for issues
4. Full production deployment

## Revenue Optimization Tips

### 1. Conversion Optimization:
- A/B test pricing page
- Optimize upgrade prompts
- Track conversion funnel
- Implement exit-intent popups

### 2. Retention Strategies:
- Send usage reports
- Highlight feature usage
- Offer annual discounts
- Implement win-back campaigns

### 3. Upsell Opportunities:
- Show API usage approaching limit
- Highlight features they're missing
- Offer time-limited upgrades
- Bundle with training/consulting

## Support Documentation

### User FAQ:
- How to upgrade/downgrade
- Billing questions
- Feature explanations
- API documentation

### Internal Documentation:
- Database schema
- API endpoints
- Webhook handling
- Error codes

## Next Steps

1. **Phase 1** (Week 1-2): Set up infrastructure
2. **Phase 2** (Week 3-4): Implement core features
3. **Phase 3** (Week 5-6): Testing and refinement
4. **Phase 4** (Week 7-8): Marketing launch

## Additional Features to Consider

1. **Analytics Dashboard**: Show users their AI visibility trends
2. **Competitor Tracking**: Compare scores with competitors
3. **Scheduled Scans**: Weekly/monthly automatic analyses
4. **Team Collaboration**: Comments and sharing within teams
5. **White Label API**: Let agencies rebrand completely
6. **Certification Program**: AI Optimization Specialist cert
7. **Affiliate Program**: Revenue sharing for referrals
8. **Chrome Extension**: Quick analysis while browsing

## Contact for Help

If you need assistance with implementation:
- Technical issues: Review Flask/Stripe documentation
- Business questions: Consider your target market needs
- Scaling concerns: Plan for growth from day one

Remember: Start simple, iterate based on user feedback, and focus on providing value that justifies the pricing.
