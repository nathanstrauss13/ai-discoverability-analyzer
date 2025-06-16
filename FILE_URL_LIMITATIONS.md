# File URL Limitations - Important Information

## The Issue
File URLs (`file:///path/to/file.html`) **only work when running the analyzer locally on your computer**. They do NOT work on the deployed web version.

## Why This Happens
This is a fundamental web security restriction:
- Web servers cannot access files on your local computer
- Browsers block this for security reasons (prevents malicious websites from reading your files)
- This is not a bug - it's an important security feature

## Solutions for Analyzing Blocked Sites

### Option 1: Run Locally (Works with file:// URLs)
```bash
# Clone the repository
git clone https://github.com/nathanstrauss13/ai-discoverability-analyzer.git
cd ai-discoverability-analyzer

# Install dependencies
pip install -r requirements.txt

# Run locally
python app.py

# Open http://localhost:5001
# Now file:// URLs will work!
```

### Option 2: Use the Deployed Version (No file:// URLs)
The deployed version at your Render URL can only analyze publicly accessible websites that don't block automated requests.

### Option 3: Future Features (Coming Soon)
1. **HTML Upload** - Upload saved HTML files directly
2. **Copy/Paste HTML** - Paste HTML content into a text field
3. **Browser Extension** - Analyze any page you're viewing

## Current Workarounds

### For Sites That Block Access:
1. **Locally**: Save HTML → Run analyzer locally → Use file:// URL
2. **Deployed**: Wait for HTML upload feature or use sites without bot protection

### Sites That Work Well:
- Personal blogs
- Documentation sites
- Open source projects
- Educational websites
- Most sites without Cloudflare/aggressive bot protection

## Technical Details
When you try to use a file:// URL on the deployed version:
1. Your browser sends the URL to the server
2. The server tries to read `/Users/yourname/file.html`
3. This file doesn't exist on the server (it's on YOUR computer)
4. The request fails

This is why file:// URLs only work when the analyzer runs on the same computer where the files are stored.
