#!/bin/bash

echo "=========================================="
echo "AI Discoverability Analyzer - Test Setup"
echo "=========================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"
echo ""

# Install minimal dependencies for testing
echo "Installing minimal dependencies for testing..."
echo ""

# Try pip3 first, then python3 -m pip
if command -v pip3 &> /dev/null; then
    pip3 install Flask Flask-Login
elif python3 -m pip --version &> /dev/null; then
    python3 -m pip install Flask Flask-Login
else
    echo "❌ pip is not installed. Installing pip..."
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    python3 get-pip.py
    rm get-pip.py
    python3 -m pip install Flask Flask-Login
fi

echo ""
echo "✓ Setup complete!"
echo ""
echo "To test the freemium UX locally, run:"
echo "  python3 test_local.py"
echo ""
echo "Then open http://localhost:5001 in your browser"
echo ""
echo "=========================================="
