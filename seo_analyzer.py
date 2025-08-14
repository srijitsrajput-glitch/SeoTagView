import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import validators
from datetime import datetime
import re

class SEOAnalyzer:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10
    
    def analyze_url(self, url):
        """Main method to analyze a URL and return comprehensive SEO data"""
        try:
            # Fetch HTML content
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract meta tags
            meta_tags = self._extract_meta_tags(soup)
            
            # Perform SEO analysis
            seo_analysis = self._analyze_seo_tags(meta_tags, soup)
            
            return {
                'success': True,
                'url': url,
                'timestamp': datetime.now().isoformat(),
                'meta_tags': meta_tags,
                'seo_analysis': seo_analysis,
                'status_code': response.status_code
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Failed to fetch URL: {str(e)}",
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f"Analysis error: {str(e)}",
                'url': url,
                'timestamp': datetime.now().isoformat()
            }
    
    def _extract_meta_tags(self, soup):
        """Extract all relevant meta tags from the HTML"""
        meta_tags = {}
        
        # Title tag
        title_tag = soup.find('title')
        if title_tag:
            meta_tags['title'] = title_tag.get_text().strip()
        
        # Meta tags
        meta_elements = soup.find_all('meta')
        
        for meta in meta_elements:
            # Standard meta tags
            if meta.get('name'):
                name = meta.get('name').lower()
                content = meta.get('content', '').strip()
                if content:
                    meta_tags[name] = content
            
            # Open Graph tags
            elif meta.get('property'):
                property_name = meta.get('property').lower()
                content = meta.get('content', '').strip()
                if content:
                    meta_tags[property_name] = content
            
            # Twitter tags
            elif meta.get('name') and meta.get('name').startswith('twitter:'):
                name = meta.get('name').lower()
                content = meta.get('content', '').strip()
                if content:
                    meta_tags[name] = content
        
        # Canonical URL
        canonical = soup.find('link', {'rel': 'canonical'})
        if canonical and canonical.get('href'):
            meta_tags['canonical'] = canonical.get('href')
        
        # Language
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            meta_tags['lang'] = html_tag.get('lang')
        
        return meta_tags
    
    def _analyze_seo_tags(self, meta_tags, soup):
        """Analyze the extracted meta tags against SEO best practices"""
        analysis = {}
        
        # Title tag analysis
        analysis['Title Tag'] = self._analyze_title(meta_tags.get('title'))
        
        # Meta description analysis
        analysis['Meta Description'] = self._analyze_description(meta_tags.get('description'))
        
        # Keywords analysis
        analysis['Meta Keywords'] = self._analyze_keywords(meta_tags.get('keywords'))
        
        # Open Graph analysis
        analysis['Open Graph Title'] = self._analyze_og_title(meta_tags)
        analysis['Open Graph Description'] = self._analyze_og_description(meta_tags)
        analysis['Open Graph Image'] = self._analyze_og_image(meta_tags)
        
        # Twitter Cards analysis
        analysis['Twitter Card'] = self._analyze_twitter_card(meta_tags)
        
        # Canonical URL analysis
        analysis['Canonical URL'] = self._analyze_canonical(meta_tags)
        
        # Language analysis
        analysis['Language Declaration'] = self._analyze_language(meta_tags)
        
        # Viewport analysis
        analysis['Viewport Meta Tag'] = self._analyze_viewport(meta_tags)
        
        # Robots meta tag analysis
        analysis['Robots Meta Tag'] = self._analyze_robots(meta_tags)
        
        return analysis
    
    def _analyze_title(self, title):
        """Analyze title tag"""
        if not title:
            return {
                'status': 'error',
                'message': 'Title tag is missing',
                'recommendation': 'Add a title tag with 50-60 characters including your target keywords'
            }
        
        length = len(title)
        
        if length < 30:
            return {
                'status': 'warning',
                'message': f'Title is too short ({length} characters)',
                'recommendation': 'Expand your title to 50-60 characters for better SEO'
            }
        elif length > 60:
            return {
                'status': 'warning',
                'message': f'Title is too long ({length} characters) - may be truncated in search results',
                'recommendation': 'Reduce title length to 50-60 characters'
            }
        else:
            return {
                'status': 'good',
                'message': f'Title length is optimal ({length} characters)',
                'recommendation': None
            }
    
    def _analyze_description(self, description):
        """Analyze meta description"""
        if not description:
            return {
                'status': 'error',
                'message': 'Meta description is missing',
                'recommendation': 'Add a meta description with 150-160 characters describing your page content'
            }
        
        length = len(description)
        
        if length < 120:
            return {
                'status': 'warning',
                'message': f'Meta description is too short ({length} characters)',
                'recommendation': 'Expand your description to 150-160 characters for better visibility'
            }
        elif length > 160:
            return {
                'status': 'warning',
                'message': f'Meta description is too long ({length} characters) - may be truncated',
                'recommendation': 'Reduce description length to 150-160 characters'
            }
        else:
            return {
                'status': 'good',
                'message': f'Meta description length is optimal ({length} characters)',
                'recommendation': None
            }
    
    def _analyze_keywords(self, keywords):
        """Analyze meta keywords"""
        if not keywords:
            return {
                'status': 'good',
                'message': 'Meta keywords tag not found (recommended - not used by search engines)',
                'recommendation': None
            }
        else:
            return {
                'status': 'warning',
                'message': 'Meta keywords tag found (not recommended)',
                'recommendation': 'Remove meta keywords tag as it\'s not used by modern search engines and may be ignored'
            }
    
    def _analyze_og_title(self, meta_tags):
        """Analyze Open Graph title"""
        og_title = meta_tags.get('og:title')
        
        if not og_title:
            return {
                'status': 'warning',
                'message': 'Open Graph title is missing',
                'recommendation': 'Add og:title for better social media sharing'
            }
        
        length = len(og_title)
        if length > 95:
            return {
                'status': 'warning',
                'message': f'Open Graph title is too long ({length} characters)',
                'recommendation': 'Keep Open Graph title under 95 characters'
            }
        else:
            return {
                'status': 'good',
                'message': f'Open Graph title is present and well-sized ({length} characters)',
                'recommendation': None
            }
    
    def _analyze_og_description(self, meta_tags):
        """Analyze Open Graph description"""
        og_description = meta_tags.get('og:description')
        
        if not og_description:
            return {
                'status': 'warning',
                'message': 'Open Graph description is missing',
                'recommendation': 'Add og:description for better social media sharing'
            }
        
        length = len(og_description)
        if length > 300:
            return {
                'status': 'warning',
                'message': f'Open Graph description is too long ({length} characters)',
                'recommendation': 'Keep Open Graph description under 300 characters'
            }
        else:
            return {
                'status': 'good',
                'message': f'Open Graph description is present and well-sized ({length} characters)',
                'recommendation': None
            }
    
    def _analyze_og_image(self, meta_tags):
        """Analyze Open Graph image"""
        og_image = meta_tags.get('og:image')
        
        if not og_image:
            return {
                'status': 'warning',
                'message': 'Open Graph image is missing',
                'recommendation': 'Add og:image for better social media sharing (recommended size: 1200x630px)'
            }
        else:
            return {
                'status': 'good',
                'message': 'Open Graph image is present',
                'recommendation': 'Ensure image is 1200x630px for optimal display'
            }
    
    def _analyze_twitter_card(self, meta_tags):
        """Analyze Twitter Card tags"""
        twitter_card = meta_tags.get('twitter:card')
        
        if not twitter_card:
            return {
                'status': 'warning',
                'message': 'Twitter Card type is missing',
                'recommendation': 'Add twitter:card meta tag (summary, summary_large_image, etc.)'
            }
        else:
            return {
                'status': 'good',
                'message': f'Twitter Card type is set to "{twitter_card}"',
                'recommendation': None
            }
    
    def _analyze_canonical(self, meta_tags):
        """Analyze canonical URL"""
        canonical = meta_tags.get('canonical')
        
        if not canonical:
            return {
                'status': 'warning',
                'message': 'Canonical URL is missing',
                'recommendation': 'Add canonical URL to prevent duplicate content issues'
            }
        else:
            return {
                'status': 'good',
                'message': 'Canonical URL is present',
                'recommendation': None
            }
    
    def _analyze_language(self, meta_tags):
        """Analyze language declaration"""
        lang = meta_tags.get('lang')
        
        if not lang:
            return {
                'status': 'warning',
                'message': 'Language declaration is missing',
                'recommendation': 'Add lang attribute to <html> tag for accessibility and SEO'
            }
        else:
            return {
                'status': 'good',
                'message': f'Language is declared as "{lang}"',
                'recommendation': None
            }
    
    def _analyze_viewport(self, meta_tags):
        """Analyze viewport meta tag"""
        viewport = meta_tags.get('viewport')
        
        if not viewport:
            return {
                'status': 'warning',
                'message': 'Viewport meta tag is missing',
                'recommendation': 'Add viewport meta tag for mobile responsiveness'
            }
        else:
            return {
                'status': 'good',
                'message': 'Viewport meta tag is present',
                'recommendation': None
            }
    
    def _analyze_robots(self, meta_tags):
        """Analyze robots meta tag"""
        robots = meta_tags.get('robots')
        
        if not robots:
            return {
                'status': 'good',
                'message': 'No robots meta tag (default behavior)',
                'recommendation': None
            }
        else:
            if 'noindex' in robots.lower():
                return {
                    'status': 'warning',
                    'message': f'Page is set to noindex: "{robots}"',
                    'recommendation': 'Review robots directive if page should be indexed'
                }
            else:
                return {
                    'status': 'good',
                    'message': f'Robots directive: "{robots}"',
                    'recommendation': None
                }
