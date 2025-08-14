import json
from urllib.parse import urlparse
import re

def format_preview_text(text, max_length):
    """Format text for preview with proper truncation"""
    if not text:
        return "No text available"
    
    if len(text) <= max_length:
        return text
    
    # Find the last space before the max length to avoid cutting words
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.8:  # If space is reasonably close to the end
        return truncated[:last_space] + "..."
    else:
        return truncated + "..."

def get_domain_from_url(url):
    """Extract domain name from URL"""
    try:
        parsed_url = urlparse(url)
        return parsed_url.netloc
    except:
        return url

def clean_text(text):
    """Clean text by removing extra whitespace and line breaks"""
    if not text:
        return ""
    
    # Remove extra whitespace and normalize line breaks
    cleaned = re.sub(r'\s+', ' ', text).strip()
    return cleaned

def validate_image_url(url):
    """Check if URL appears to be a valid image URL"""
    if not url:
        return False
    
    # Basic validation - check if it looks like an image URL
    image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg']
    url_lower = url.lower()
    
    return any(ext in url_lower for ext in image_extensions) or 'image' in url_lower

def export_to_json(data):
    """Export analysis data to JSON format"""
    return json.dumps(data, indent=2, ensure_ascii=False)

def calculate_reading_time(text):
    """Calculate estimated reading time for text"""
    if not text:
        return 0
    
    words = len(text.split())
    # Average reading speed is about 200 words per minute
    minutes = words / 200
    return max(1, round(minutes))

def extract_social_media_data(meta_tags):
    """Extract and organize social media specific meta tags"""
    social_data = {
        'facebook': {},
        'twitter': {},
        'general': {}
    }
    
    for key, value in meta_tags.items():
        if key.startswith('og:'):
            social_data['facebook'][key] = value
        elif key.startswith('twitter:'):
            social_data['twitter'][key] = value
        elif key in ['title', 'description']:
            social_data['general'][key] = value
    
    return social_data

def get_seo_recommendations(analysis_results):
    """Generate prioritized SEO recommendations based on analysis"""
    recommendations = []
    
    # Critical issues first
    critical_issues = []
    warnings = []
    
    for tag_name, analysis in analysis_results.items():
        if analysis['status'] == 'error' and analysis.get('recommendation'):
            critical_issues.append({
                'priority': 'high',
                'tag': tag_name,
                'recommendation': analysis['recommendation']
            })
        elif analysis['status'] == 'warning' and analysis.get('recommendation'):
            warnings.append({
                'priority': 'medium',
                'tag': tag_name,
                'recommendation': analysis['recommendation']
            })
    
    recommendations.extend(critical_issues)
    recommendations.extend(warnings)
    
    return recommendations

def generate_seo_score(analysis_results):
    """Generate a numerical SEO score based on analysis results"""
    total_checks = len(analysis_results)
    if total_checks == 0:
        return 0
    
    scores = {
        'good': 100,
        'warning': 70,
        'error': 0
    }
    
    total_score = 0
    for analysis in analysis_results.values():
        total_score += scores.get(analysis['status'], 0)
    
    return round(total_score / total_checks)

def format_meta_tag_display(key, value, max_display_length=100):
    """Format meta tag for display in UI"""
    if not value:
        return f"{key}: (empty)"
    
    if len(value) > max_display_length:
        return f"{key}: {value[:max_display_length]}..."
    
    return f"{key}: {value}"

def detect_structured_data(soup):
    """Detect presence of structured data (JSON-LD, microdata, etc.)"""
    structured_data = {
        'json_ld': False,
        'microdata': False,
        'rdfa': False
    }
    
    # Check for JSON-LD
    json_ld_scripts = soup.find_all('script', {'type': 'application/ld+json'})
    if json_ld_scripts:
        structured_data['json_ld'] = True
    
    # Check for microdata
    microdata_elements = soup.find_all(attrs={'itemscope': True})
    if microdata_elements:
        structured_data['microdata'] = True
    
    # Check for RDFa
    rdfa_elements = soup.find_all(attrs={'typeof': True})
    if rdfa_elements:
        structured_data['rdfa'] = True
    
    return structured_data

def analyze_page_speed_indicators(soup):
    """Analyze basic page speed indicators from HTML"""
    indicators = {
        'external_scripts': 0,
        'external_stylesheets': 0,
        'inline_styles': 0,
        'images_without_alt': 0
    }
    
    # Count external scripts
    scripts = soup.find_all('script', src=True)
    indicators['external_scripts'] = len(scripts)
    
    # Count external stylesheets
    stylesheets = soup.find_all('link', {'rel': 'stylesheet'})
    indicators['external_stylesheets'] = len(stylesheets)
    
    # Count inline styles
    inline_styles = soup.find_all('style')
    indicators['inline_styles'] = len(inline_styles)
    
    # Count images without alt text
    images = soup.find_all('img')
    for img in images:
        if not img.get('alt'):
            indicators['images_without_alt'] += 1
    
    return indicators
