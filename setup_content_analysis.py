#!/usr/bin/env python3
"""
Setup script for content analysis dependencies
Downloads required NLTK data and spaCy models
"""

import subprocess
import sys

def setup_nltk():
    """Download required NLTK data"""
    print("Setting up NLTK data...")
    try:
        import nltk
        nltk.download('punkt')
        nltk.download('stopwords')
        nltk.download('averaged_perceptron_tagger')
        print("✓ NLTK data downloaded successfully")
    except Exception as e:
        print(f"✗ Error setting up NLTK: {e}")
        return False
    return True

def setup_spacy():
    """Download spaCy English model"""
    print("\nSetting up spaCy model...")
    try:
        # Try to download the model
        subprocess.run([sys.executable, "-m", "spacy", "download", "en_core_web_sm"], check=True)
        print("✓ spaCy model downloaded successfully")
        return True
    except subprocess.CalledProcessError:
        print("✗ Failed to download spaCy model")
        print("  You can manually install it with: python -m spacy download en_core_web_sm")
        return False
    except Exception as e:
        print(f"✗ Error setting up spaCy: {e}")
        print("  Note: spaCy is optional. The analyzer will work without it.")
        return False

def test_imports():
    """Test that all required imports work"""
    print("\nTesting imports...")
    
    required_modules = [
        ('nltk', 'NLTK'),
        ('textstat', 'Textstat'),
        ('spacy', 'spaCy (optional)'),
        ('bs4', 'BeautifulSoup'),
        ('anthropic', 'Anthropic'),
    ]
    
    all_good = True
    for module, name in required_modules:
        try:
            __import__(module)
            print(f"✓ {name} imported successfully")
        except ImportError:
            if 'optional' in name:
                print(f"⚠ {name} not installed (this is optional)")
            else:
                print(f"✗ {name} import failed - please install with: pip install {module}")
                all_good = False
    
    return all_good

def main():
    print("AI Discoverability Analyzer - Content Analysis Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("✗ Python 3.7+ is required")
        sys.exit(1)
    
    print(f"✓ Python {sys.version.split()[0]} detected")
    
    # Install dependencies
    print("\nInstalling dependencies...")
    print("Please ensure you've run: pip install -r requirements.txt")
    
    # Setup NLTK
    nltk_ok = setup_nltk()
    
    # Setup spaCy (optional)
    spacy_ok = setup_spacy()
    
    # Test imports
    imports_ok = test_imports()
    
    print("\n" + "=" * 50)
    if nltk_ok and imports_ok:
        print("✓ Setup completed successfully!")
        print("\nThe content analysis features are ready to use.")
        if not spacy_ok:
            print("\nNote: spaCy is not installed, but the analyzer will work without it.")
    else:
        print("✗ Setup completed with errors")
        print("\nPlease fix the errors above before using content analysis features.")
        sys.exit(1)

if __name__ == "__main__":
    main()
