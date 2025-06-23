"""
Content Analysis Module for AI Discoverability
Analyzes content quality, readability, and AI-optimization factors
"""

import re
from collections import Counter
from bs4 import BeautifulSoup

# Try to import optional NLP libraries
try:
    import nltk
    # Download required NLTK data
    try:
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('averaged_perceptron_tagger', quiet=True)
    except:
        pass
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    nltk = None

try:
    from textstat import flesch_reading_ease, flesch_kincaid_grade
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
    flesch_reading_ease = None
    flesch_kincaid_grade = None

try:
    import spacy
    # Load spaCy model for NLP analysis
    try:
        nlp = spacy.load("en_core_web_sm")
    except:
        nlp = None
except ImportError:
    spacy = None
    nlp = None

class ContentAnalyzer:
    """Analyzes content for AI discoverability and quality metrics"""
    
    def __init__(self):
        self.promotional_keywords = [
            'best', 'leading', 'premier', 'top', 'revolutionary', 'innovative',
            'cutting-edge', 'state-of-the-art', 'world-class', 'industry-leading',
            'unparalleled', 'exceptional', 'outstanding', 'superior', 'premium',
            'exclusive', 'unique', 'breakthrough', 'game-changing', 'transformative'
        ]
        
        self.factual_indicators = [
            'according to', 'research shows', 'studies indicate', 'data reveals',
            'statistics show', 'survey found', 'report states', 'analysis shows',
            'evidence suggests', 'findings indicate', 'results demonstrate'
        ]
        
        self.credibility_markers = [
            'phd', 'professor', 'researcher', 'scientist', 'expert', 'specialist',
            'university', 'institute', 'journal', 'publication', 'peer-reviewed',
            'citation', 'reference', 'source', 'bibliography'
        ]

    def analyze_content(self, html_content, soup=None):
        """Comprehensive content analysis for AI optimization"""
        if not soup:
            soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract text content
        text = self._extract_text(soup)
        
        analysis = {
            'readability': self._analyze_readability(text),
            'content_quality': self._analyze_content_quality(text, soup),
            'promotional_language': self._detect_promotional_language(text),
            'factual_content': self._analyze_factual_content(text),
            'answer_optimization': self._analyze_answer_optimization(soup),
            'credibility_signals': self._analyze_credibility(text, soup),
            'content_structure': self._analyze_content_structure(soup),
            'brevity_score': self._calculate_brevity_score(text, soup)
        }
        
        return analysis

    def _extract_text(self, soup):
        """Extract clean text from HTML"""
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text

    def _analyze_readability(self, text):
        """Analyze text readability metrics"""
        if not TEXTSTAT_AVAILABLE:
            return {
                'flesch_reading_ease': None,
                'flesch_kincaid_grade': None,
                'interpretation': 'Textstat library not available for readability analysis',
                'ai_friendly': None
            }
            
        if len(text.split()) < 100:
            return {
                'flesch_reading_ease': None,
                'flesch_kincaid_grade': None,
                'interpretation': 'Text too short for accurate readability analysis'
            }
        
        try:
            fre_score = flesch_reading_ease(text)
            fkg_score = flesch_kincaid_grade(text)
            
            # Interpret Flesch Reading Ease
            if fre_score >= 90:
                interpretation = "Very Easy (5th grade)"
            elif fre_score >= 80:
                interpretation = "Easy (6th grade)"
            elif fre_score >= 70:
                interpretation = "Fairly Easy (7th grade)"
            elif fre_score >= 60:
                interpretation = "Standard (8-9th grade)"
            elif fre_score >= 50:
                interpretation = "Fairly Difficult (10-12th grade)"
            elif fre_score >= 30:
                interpretation = "Difficult (College)"
            else:
                interpretation = "Very Difficult (College graduate)"
            
            return {
                'flesch_reading_ease': round(fre_score, 1),
                'flesch_kincaid_grade': round(fkg_score, 1),
                'interpretation': interpretation,
                'ai_friendly': fre_score >= 60  # AI prefers clear, accessible content
            }
        except:
            return {
                'flesch_reading_ease': None,
                'flesch_kincaid_grade': None,
                'interpretation': 'Unable to calculate readability scores'
            }

    def _analyze_content_quality(self, text, soup):
        """Analyze overall content quality metrics"""
        words = text.split()
        
        # Sentence tokenization
        if NLTK_AVAILABLE and nltk:
            sentences = nltk.sent_tokenize(text)
        else:
            # Simple fallback sentence splitting
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Calculate average sentence length
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        
        # Check for diverse vocabulary
        unique_words = set(word.lower() for word in words)
        vocabulary_diversity = len(unique_words) / len(words) if words else 0
        
        # Check for paragraph structure
        paragraphs = soup.find_all('p')
        avg_paragraph_length = sum(len(p.get_text().split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        return {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'vocabulary_diversity': round(vocabulary_diversity, 2),
            'paragraph_count': len(paragraphs),
            'avg_paragraph_length': round(avg_paragraph_length, 1),
            'quality_score': self._calculate_quality_score(avg_sentence_length, vocabulary_diversity, len(paragraphs))
        }

    def _detect_promotional_language(self, text):
        """Detect promotional and marketing language"""
        text_lower = text.lower()
        words = text_lower.split()
        
        # Count promotional keywords
        promotional_count = sum(1 for word in self.promotional_keywords if word in text_lower)
        
        # Calculate promotional density
        promotional_density = promotional_count / len(words) * 100 if words else 0
        
        # Find specific promotional phrases
        found_promotional = [word for word in self.promotional_keywords if word in text_lower]
        
        # Detect superlatives
        superlative_pattern = r'\b(most|best|greatest|finest|top|leading|premier)\b'
        superlatives = len(re.findall(superlative_pattern, text_lower))
        
        return {
            'promotional_keyword_count': promotional_count,
            'promotional_density': round(promotional_density, 2),
            'found_keywords': found_promotional[:10],  # Top 10
            'superlative_count': superlatives,
            'is_promotional': promotional_density > 2 or superlatives > 5,
            'recommendation': self._get_promotional_recommendation(promotional_density)
        }

    def _analyze_factual_content(self, text):
        """Analyze factual vs emotional content"""
        text_lower = text.lower()
        
        # Count factual indicators
        factual_count = sum(1 for indicator in self.factual_indicators if indicator in text_lower)
        
        # Look for statistics and numbers
        numbers = re.findall(r'\b\d+(?:\.\d+)?%?\b', text)
        statistics_count = len(numbers)
        
        # Look for citations or references
        citation_patterns = [
            r'\[\d+\]',  # [1] style citations
            r'\(\d{4}\)',  # (2024) year citations
            r'et al\.',  # Academic citations
            r'according to',
            r'source:',
            r'reference:'
        ]
        citation_count = sum(len(re.findall(pattern, text_lower)) for pattern in citation_patterns)
        
        return {
            'factual_indicators': factual_count,
            'statistics_count': statistics_count,
            'citation_count': citation_count,
            'numbers_found': numbers[:10],  # First 10 numbers
            'factual_score': self._calculate_factual_score(factual_count, statistics_count, citation_count),
            'is_fact_based': factual_count > 3 or statistics_count > 5
        }

    def _analyze_answer_optimization(self, soup):
        """Analyze content structure for answer optimization"""
        analysis = {
            'has_faq_section': False,
            'qa_pairs_count': 0,
            'definition_count': 0,
            'how_to_sections': 0,
            'list_usage': {
                'ordered': 0,
                'unordered': 0,
                'definition': 0
            },
            'direct_answers': []
        }
        
        # Check for FAQ patterns
        faq_indicators = ['faq', 'frequently asked', 'common questions', 'q&a', 'questions and answers']
        page_text = soup.get_text().lower()
        for indicator in faq_indicators:
            if indicator in page_text:
                analysis['has_faq_section'] = True
                break
        
        # Count Q&A pairs (questions followed by answers)
        questions = soup.find_all(text=re.compile(r'.*\?$'))
        analysis['qa_pairs_count'] = len(questions)
        
        # Count definition patterns
        definition_patterns = [
            r'what is',
            r'definition of',
            r'means that',
            r'refers to',
            r'is defined as'
        ]
        for pattern in definition_patterns:
            analysis['definition_count'] += len(re.findall(pattern, page_text, re.IGNORECASE))
        
        # Count how-to sections
        how_to_pattern = r'how to|how do|step-by-step|tutorial|guide'
        analysis['how_to_sections'] = len(re.findall(how_to_pattern, page_text, re.IGNORECASE))
        
        # Count list usage
        analysis['list_usage']['ordered'] = len(soup.find_all('ol'))
        analysis['list_usage']['unordered'] = len(soup.find_all('ul'))
        analysis['list_usage']['definition'] = len(soup.find_all('dl'))
        
        # Extract potential direct answers (first sentences after questions)
        for i, question in enumerate(questions[:5]):  # Limit to first 5
            # Try to find the next paragraph or text block
            next_element = question.find_next(['p', 'div', 'li'])
            if next_element:
                answer_preview = next_element.get_text()[:100] + '...' if len(next_element.get_text()) > 100 else next_element.get_text()
                analysis['direct_answers'].append({
                    'question': str(question)[:100],
                    'answer_preview': answer_preview
                })
        
        return analysis

    def _analyze_credibility(self, text, soup):
        """Analyze credibility and authority signals"""
        text_lower = text.lower()
        
        # Count credibility markers
        credibility_count = sum(1 for marker in self.credibility_markers if marker in text_lower)
        
        # Look for author information
        author_patterns = [
            r'by\s+[A-Z][a-z]+\s+[A-Z][a-z]+',  # "by First Last"
            r'author:\s*[A-Z][a-z]+',  # "Author: Name"
            r'written by',
            r'contributed by'
        ]
        author_mentions = sum(len(re.findall(pattern, text)) for pattern in author_patterns)
        
        # Check for external links (potential citations)
        external_links = soup.find_all('a', href=re.compile(r'^https?://'))
        quality_domains = ['edu', 'gov', 'org', 'wikipedia', 'pubmed', 'nature', 'science']
        quality_links = sum(1 for link in external_links if any(domain in link.get('href', '') for domain in quality_domains))
        
        # Look for testimonials or reviews
        testimonial_patterns = ['testimonial', 'review', 'feedback', 'said', 'according to']
        testimonial_count = sum(1 for pattern in testimonial_patterns if pattern in text_lower)
        
        return {
            'credibility_markers': credibility_count,
            'author_mentions': author_mentions,
            'external_links': len(external_links),
            'quality_links': quality_links,
            'testimonial_indicators': testimonial_count,
            'credibility_score': self._calculate_credibility_score(
                credibility_count, author_mentions, quality_links, testimonial_count
            ),
            'has_author_info': author_mentions > 0,
            'has_quality_citations': quality_links > 0
        }

    def _analyze_content_structure(self, soup):
        """Analyze content structure for AI parsing"""
        structure = {
            'has_summary': False,
            'has_conclusion': False,
            'has_key_takeaways': False,
            'section_count': 0,
            'avg_section_length': 0,
            'uses_schema_markup': False
        }
        
        # Check for summary/abstract
        summary_indicators = ['summary', 'abstract', 'overview', 'tldr', 'key points']
        page_text = soup.get_text().lower()
        for indicator in summary_indicators:
            if indicator in page_text:
                structure['has_summary'] = True
                break
        
        # Check for conclusion
        conclusion_indicators = ['conclusion', 'summary', 'final thoughts', 'wrap up', 'in closing']
        for indicator in conclusion_indicators:
            if indicator in page_text[-1000:]:  # Check last 1000 chars
                structure['has_conclusion'] = True
                break
        
        # Check for key takeaways
        takeaway_indicators = ['key takeaways', 'main points', 'highlights', 'key findings', 'important points']
        for indicator in takeaway_indicators:
            if indicator in page_text:
                structure['has_key_takeaways'] = True
                break
        
        # Count sections (h2 and h3 tags typically denote sections)
        sections = soup.find_all(['h2', 'h3'])
        structure['section_count'] = len(sections)
        
        # Calculate average section length
        if sections:
            section_lengths = []
            for i, section in enumerate(sections):
                # Find content between this section and the next
                next_section = sections[i + 1] if i + 1 < len(sections) else None
                content = []
                for sibling in section.find_next_siblings():
                    if sibling == next_section:
                        break
                    content.append(sibling.get_text())
                section_lengths.append(len(' '.join(content).split()))
            structure['avg_section_length'] = round(sum(section_lengths) / len(section_lengths)) if section_lengths else 0
        
        return structure

    def _calculate_brevity_score(self, text, soup):
        """Calculate brevity and conciseness score"""
        words = text.split()
        
        # Sentence tokenization
        if NLTK_AVAILABLE and nltk:
            sentences = nltk.sent_tokenize(text)
        else:
            # Simple fallback sentence splitting
            sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        
        # Ideal sentence length for AI is 15-20 words
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        sentence_brevity = 100 - abs(avg_sentence_length - 17.5) * 2  # Penalty for deviation from ideal
        
        # Check for filler words
        filler_words = [
            'very', 'really', 'actually', 'basically', 'literally', 'seriously',
            'obviously', 'clearly', 'simply', 'just', 'quite', 'rather',
            'somewhat', 'somehow', 'anyway', 'perhaps', 'maybe', 'probably'
        ]
        filler_count = sum(1 for word in words if word.lower() in filler_words)
        filler_density = (filler_count / len(words) * 100) if words else 0
        
        # Check for redundant phrases
        redundant_phrases = [
            'in order to', 'at this point in time', 'due to the fact that',
            'in the event that', 'for the purpose of', 'with regard to',
            'in terms of', 'as a matter of fact', 'at the end of the day'
        ]
        redundancy_count = sum(text.lower().count(phrase) for phrase in redundant_phrases)
        
        brevity_score = max(0, min(100, sentence_brevity - filler_density * 5 - redundancy_count * 3))
        
        return {
            'brevity_score': round(brevity_score),
            'avg_sentence_length': round(avg_sentence_length, 1),
            'filler_word_density': round(filler_density, 2),
            'redundant_phrases': redundancy_count,
            'is_concise': brevity_score > 70,
            'recommendation': self._get_brevity_recommendation(brevity_score, avg_sentence_length)
        }

    def _calculate_quality_score(self, avg_sentence_length, vocabulary_diversity, paragraph_count):
        """Calculate overall content quality score"""
        score = 50  # Base score
        
        # Sentence length (ideal: 15-20 words)
        if 15 <= avg_sentence_length <= 20:
            score += 20
        elif 10 <= avg_sentence_length <= 25:
            score += 10
        
        # Vocabulary diversity (ideal: 0.5-0.7)
        if 0.5 <= vocabulary_diversity <= 0.7:
            score += 20
        elif 0.4 <= vocabulary_diversity <= 0.8:
            score += 10
        
        # Paragraph usage
        if paragraph_count > 3:
            score += 10
        
        return min(100, score)

    def _calculate_factual_score(self, factual_indicators, statistics, citations):
        """Calculate factual content score"""
        score = 0
        
        # Weight different factors
        score += min(30, factual_indicators * 10)
        score += min(40, statistics * 8)
        score += min(30, citations * 15)
        
        return min(100, score)

    def _calculate_credibility_score(self, markers, authors, quality_links, testimonials):
        """Calculate credibility score"""
        score = 0
        
        score += min(25, markers * 5)
        score += min(25, authors * 12)
        score += min(30, quality_links * 10)
        score += min(20, testimonials * 4)
        
        return min(100, score)

    def _get_promotional_recommendation(self, density):
        """Get recommendation for promotional language"""
        if density < 1:
            return "Good - Minimal promotional language detected"
        elif density < 2:
            return "Moderate - Consider reducing marketing terms"
        elif density < 3:
            return "High - Replace promotional language with factual descriptions"
        else:
            return "Excessive - Major rewrite needed for AI optimization"

    def _get_brevity_recommendation(self, score, avg_length):
        """Get recommendation for brevity"""
        if score > 80:
            return "Excellent - Content is concise and clear"
        elif score > 60:
            return "Good - Minor improvements possible"
        elif score > 40:
            return "Fair - Reduce filler words and simplify sentences"
        else:
            return "Poor - Significant editing needed for clarity"

    def generate_content_recommendations(self, content_analysis, technical_analysis):
        """Generate specific content recommendations based on analysis"""
        recommendations = []
        
        # Readability recommendations
        if content_analysis['readability']['flesch_reading_ease']:
            if content_analysis['readability']['flesch_reading_ease'] < 60:
                recommendations.append({
                    'category': 'Readability',
                    'priority': 'High',
                    'issue': 'Content is too complex for optimal AI processing',
                    'action': 'Simplify sentences and use more common words. Aim for 8th-9th grade reading level.',
                    'impact': 'Improves AI comprehension and increases likelihood of content being used in responses'
                })
        
        # Promotional language recommendations
        if content_analysis['promotional_language']['is_promotional']:
            recommendations.append({
                'category': 'Content Tone',
                'priority': 'High',
                'issue': f"High promotional language density ({content_analysis['promotional_language']['promotional_density']}%)",
                'action': 'Replace marketing terms with factual descriptions. Focus on features and benefits rather than superlatives.',
                'impact': 'AI agents prefer factual content and may skip overly promotional material'
            })
        
        # Factual content recommendations
        if not content_analysis['factual_content']['is_fact_based']:
            recommendations.append({
                'category': 'Factual Content',
                'priority': 'High',
                'issue': 'Low factual content density',
                'action': 'Add statistics, research citations, and concrete examples. Include data points and measurable outcomes.',
                'impact': 'Factual content is more likely to be cited by AI agents as authoritative'
            })
        
        # Answer optimization recommendations
        if not content_analysis['answer_optimization']['has_faq_section']:
            recommendations.append({
                'category': 'Answer Structure',
                'priority': 'High',
                'issue': 'No FAQ or Q&A section detected',
                'action': 'Create a comprehensive FAQ section with direct answers to common questions about your product/service.',
                'impact': 'FAQ content is highly favored by AI for direct answer extraction'
            })
        
        # Credibility recommendations
        if content_analysis['credibility_signals']['credibility_score'] < 50:
            recommendations.append({
                'category': 'Authority Building',
                'priority': 'Medium',
                'issue': 'Low credibility signals',
                'action': 'Add author bylines, expert quotes, and citations to authoritative sources. Link to credible external resources.',
                'impact': 'Increases trust signals for AI evaluation'
            })
        
        # Structure recommendations
        if not content_analysis['content_structure']['has_summary']:
            recommendations.append({
                'category': 'Content Structure',
                'priority': 'Medium',
                'issue': 'No summary or overview section',
                'action': 'Add a brief summary or key points section at the beginning of your content.',
                'impact': 'Helps AI quickly understand and extract main points'
            })
        
        # Brevity recommendations
        if content_analysis['brevity_score']['brevity_score'] < 70:
            recommendations.append({
                'category': 'Content Brevity',
                'priority': 'Medium',
                'issue': f"Content lacks conciseness (score: {content_analysis['brevity_score']['brevity_score']})",
                'action': 'Remove filler words, redundant phrases, and unnecessarily complex sentences.',
                'impact': 'Concise content is easier for AI to process and extract'
            })
        
        # List usage recommendations
        total_lists = sum(content_analysis['answer_optimization']['list_usage'].values())
        if total_lists < 3:
            recommendations.append({
                'category': 'Content Formatting',
                'priority': 'Low',
                'issue': 'Limited use of lists and structured content',
                'action': 'Use bullet points, numbered lists, and definition lists to organize information clearly.',
                'impact': 'Lists are easily parsed by AI and improve content extraction'
            })
        
        return recommendations
