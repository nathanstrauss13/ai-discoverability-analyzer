# Testing the Freemium UX Locally

## Quick Start

1. **Stop any running server** (press Ctrl+C in the terminal)

2. **Run the test server**:
   ```bash
   cd "innate apps/ai-discoverability-analyzer"
   python3 test_local.py
   ```

3. **Open your browser** and visit: http://localhost:5001

## Test Scenarios

### 1. Anonymous User Experience
- Go to http://localhost:5001
- Try analyzing a URL without logging in
- Notice the "Consulting Services" button (from original template)

### 2. Free User Experience
- Go to http://localhost:5001/login
- Click "Login as Free User"
- You'll be redirected to the dashboard showing:
  - 3/5 analyses used (60% usage bar)
  - No recent analyses
  - Upgrade prompt

### 3. Professional User Experience
- Go to http://localhost:5001/login
- Click "Login as Professional User"
- Dashboard shows:
  - Unlimited analyses
  - API usage (45/100 calls)
  - Recent analyses with export options
  - API statistics section

### 4. Agency User Experience
- Go to http://localhost:5001/login
- Click "Login as Agency User"
- Similar to Professional but with:
  - Higher API limits (45/1000 calls)
  - Agency tier badge

### 5. Pricing Page
- Visit http://localhost:5001/pricing
- Test the monthly/yearly toggle
- See the three-tier pricing structure
- FAQ section at the bottom

## Key Features to Test

1. **Usage Limits**:
   - Free users see usage bar (3/5 analyses)
   - Paid users see "Unlimited" badge

2. **Tier-Based Features**:
   - Free users: No export buttons, no API stats
   - Paid users: Export PDF/CSV buttons, API usage stats

3. **Navigation**:
   - Logo returns to analyzer
   - Pricing link in navigation
   - Logout functionality

4. **Responsive Design**:
   - Test on different screen sizes
   - Mobile-friendly layout

## Known Limitations in Test Mode

- Email verification is bypassed
- Stripe payments show alerts instead of real checkout
- API keys management shows "coming soon"
- Export functions show alerts
- Analysis results are mocked

## Troubleshooting

If the server won't start:
1. Make sure no other process is using port 5001
2. Check that Flask and Flask-Login are installed:
   ```bash
   pip3 install Flask Flask-Login
   ```

If you see import errors:
1. Make sure you're in the correct directory
2. The test script imports from the original app.py

## Full Production Implementation

For the complete freemium implementation with real features:
- See `app_freemium.py` for the full application
- See `FREEMIUM_IMPLEMENTATION_GUIDE.md` for setup instructions
- Configure Stripe, email, and database as described in the guide
