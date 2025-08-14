import streamlit as st
import requests
from bs4 import BeautifulSoup
import validators
from urllib.parse import urljoin, urlparse
import json
from seo_analyzer import SEOAnalyzer
from utils import format_preview_text, get_domain_from_url, export_to_json

# Page configuration
st.set_page_config(
    page_title="SEO Meta Tags Analyzer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better mobile responsiveness and visual appeal
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .seo-tip {
        background: #f8f9ff;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #e1e5fe;
        margin: 1rem 0;
    }
    .preview-container {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    @media (max-width: 768px) {
        .main-header {
            padding: 1rem;
        }
        .metric-card {
            margin: 0.5rem 0;
            padding: 1rem;
        }
    }
    .status-good { color: #28a745; font-weight: bold; }
    .status-warning { color: #ffc107; font-weight: bold; }
    .status-error { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Main header with gradient background
st.markdown("""
<div class="main-header">
    <h1>🔍 SEO Meta Tags Analyzer</h1>
    <p>Analyze any website's SEO performance with visual previews and expert recommendations</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state
if 'analysis_results' not in st.session_state:
    st.session_state.analysis_results = None
if 'url' not in st.session_state:
    st.session_state.url = ""

# URL input section with better styling
with st.container():
    st.markdown("### 🌐 Enter Website URL")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        url_input = st.text_input(
            "Website URL", 
            value=st.session_state.url,
            placeholder="https://example.com",
            help="Enter the full URL including http:// or https://",
            label_visibility="collapsed"
        )
    with col2:
        analyze_button = st.button("🚀 Analyze", type="primary", use_container_width=True)
    
    # Quick examples for beginners
    st.markdown("**Try these examples:** ")
    example_urls = ["https://example.com", "https://github.com", "https://stackoverflow.com"]
    cols = st.columns(len(example_urls))
    for i, url in enumerate(example_urls):
        with cols[i]:
            if st.button(f"Test {url.split('//')[1].split('.')[0].title()}", key=f"example_{i}"):
                st.session_state.url = url
                st.rerun()

if analyze_button and url_input:
    # Validate URL
    if not validators.url(url_input):
        st.error("❌ Please enter a valid URL (including http:// or https://)")
    else:
        st.session_state.url = url_input
        
        with st.spinner("Fetching and analyzing website..."):
            try:
                # Create analyzer instance
                analyzer = SEOAnalyzer()
                
                # Fetch and analyze
                results = analyzer.analyze_url(url_input)
                st.session_state.analysis_results = results
                
                if results['success']:
                    st.success("✅ Analysis completed successfully!")
                else:
                    st.error(f"❌ Error: {results['error']}")
                    
            except Exception as e:
                st.error(f"❌ Unexpected error: {str(e)}")

# Display results if available
if st.session_state.analysis_results and st.session_state.analysis_results['success']:
    results = st.session_state.analysis_results
    
    # Overview section with enhanced visual design
    st.markdown("### 📊 SEO Analysis Dashboard")
    
    # Score calculation
    total_checks = len(results['seo_analysis'])
    passed_checks = sum(1 for check in results['seo_analysis'].values() if check['status'] == 'good')
    warning_checks = sum(1 for check in results['seo_analysis'].values() if check['status'] == 'warning')
    error_checks = sum(1 for check in results['seo_analysis'].values() if check['status'] == 'error')
    score = int((passed_checks / total_checks) * 100) if total_checks > 0 else 0
    
    # Color-coded score display
    score_color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: {score_color}; margin: 0;">{score}%</h3>
            <p style="margin: 0; color: #666;">SEO Score</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #28a745; margin: 0;">{passed_checks}</h3>
            <p style="margin: 0; color: #666;">Passed Checks</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #ffc107; margin: 0;">{warning_checks}</h3>
            <p style="margin: 0; color: #666;">Warnings</p>
        </div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3 style="color: #dc3545; margin: 0;">{error_checks}</h3>
            <p style="margin: 0; color: #666;">Errors</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Progress bar for visual score representation
    progress_color = "#28a745" if score >= 80 else "#ffc107" if score >= 60 else "#dc3545"
    st.markdown(f"""
    <div style="background: #e9ecef; border-radius: 10px; height: 20px; margin: 1rem 0;">
        <div style="background: {progress_color}; width: {score}%; height: 100%; border-radius: 10px; transition: width 0.3s ease;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # SEO Analysis Details with categorization
    st.markdown("### 🔍 Detailed SEO Analysis")
    
    # Categorize checks for better organization
    basic_seo = {}
    social_media = {}
    technical = {}
    
    for tag_name, analysis in results['seo_analysis'].items():
        if any(keyword in tag_name.lower() for keyword in ['title', 'description', 'keywords']):
            basic_seo[tag_name] = analysis
        elif any(keyword in tag_name.lower() for keyword in ['open graph', 'twitter', 'og:', 'twitter:']):
            social_media[tag_name] = analysis
        else:
            technical[tag_name] = analysis
    
    # Display categorized results in tabs
    tab1, tab2, tab3 = st.tabs(["📝 Basic SEO", "📱 Social Media", "⚙️ Technical"])
    
    def display_analysis_section(analysis_dict):
        for tag_name, analysis in analysis_dict.items():
            status = analysis['status']
            icon = "✅" if status == 'good' else "⚠️" if status == 'warning' else "❌"
            status_class = f"status-{status}"
            
            with st.expander(f"{icon} {tag_name}", expanded=(status != 'good')):
                st.markdown(f'<p class="{status_class}">{analysis["message"]}</p>', unsafe_allow_html=True)
                
                if analysis.get('recommendation'):
                    st.markdown(f"""
                    <div class="seo-tip">
                        <strong>💡 Recommendation:</strong> {analysis['recommendation']}
                    </div>
                    """, unsafe_allow_html=True)
    
    with tab1:
        if basic_seo:
            display_analysis_section(basic_seo)
            st.markdown("""
            <div class="seo-tip">
                <h4>📚 Basic SEO Tips for Beginners:</h4>
                <ul>
                    <li><strong>Title Tags:</strong> Should be 50-60 characters and include your main keyword</li>
                    <li><strong>Meta Descriptions:</strong> Write compelling 150-160 character summaries</li>
                    <li><strong>Keywords:</strong> Focus on natural language, avoid keyword stuffing</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No basic SEO elements found in analysis.")
    
    with tab2:
        if social_media:
            display_analysis_section(social_media)
            st.markdown("""
            <div class="seo-tip">
                <h4>📱 Social Media Optimization Tips:</h4>
                <ul>
                    <li><strong>Open Graph:</strong> Controls how your page looks when shared on Facebook</li>
                    <li><strong>Twitter Cards:</strong> Enhances your tweets with rich media previews</li>
                    <li><strong>Images:</strong> Use 1200x630px images for best results</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No social media tags found in analysis.")
    
    with tab3:
        if technical:
            display_analysis_section(technical)
            st.markdown("""
            <div class="seo-tip">
                <h4>⚙️ Technical SEO Essentials:</h4>
                <ul>
                    <li><strong>Canonical URLs:</strong> Prevent duplicate content issues</li>
                    <li><strong>Language Tags:</strong> Help search engines understand your content</li>
                    <li><strong>Viewport:</strong> Essential for mobile-friendly websites</li>
                    <li><strong>Robots:</strong> Control how search engines crawl your site</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No technical SEO elements found in analysis.")
    
    # SEO Insights Dashboard for beginners
    st.markdown("### 📈 SEO Insights & Recommendations")
    
    # Priority recommendations
    recommendations = []
    critical_issues = []
    improvements = []
    
    for tag_name, analysis in results['seo_analysis'].items():
        if analysis['status'] == 'error':
            critical_issues.append({
                'tag': tag_name,
                'message': analysis['message'],
                'recommendation': analysis.get('recommendation', 'No specific recommendation available')
            })
        elif analysis['status'] == 'warning':
            improvements.append({
                'tag': tag_name,
                'message': analysis['message'],
                'recommendation': analysis.get('recommendation', 'No specific recommendation available')
            })
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚨 Critical Issues to Fix First")
        if critical_issues:
            for issue in critical_issues[:3]:  # Show top 3 critical issues
                st.markdown(f"""
                <div style="background: #fff2f2; border: 1px solid #fecaca; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                    <strong style="color: #dc2626;">{issue['tag']}</strong><br>
                    <small style="color: #666;">{issue['message']}</small><br>
                    <span style="color: #059669;">💡 {issue['recommendation']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("🎉 No critical issues found! Your basic SEO setup looks good.")
    
    with col2:
        st.markdown("#### ⚡ Quick Improvements")
        if improvements:
            for improvement in improvements[:3]:  # Show top 3 improvements
                st.markdown(f"""
                <div style="background: #fffbeb; border: 1px solid #fed7aa; border-radius: 8px; padding: 1rem; margin: 0.5rem 0;">
                    <strong style="color: #d97706;">{improvement['tag']}</strong><br>
                    <small style="color: #666;">{improvement['message']}</small><br>
                    <span style="color: #059669;">💡 {improvement['recommendation']}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("Great job! No immediate improvements needed.")
    
    # SEO Score Breakdown with explanations
    st.markdown("#### 📊 Score Breakdown & Next Steps")
    
    if score >= 80:
        st.success(f"""
        **Excellent SEO Score: {score}%** 🎉
        
        Your website has strong SEO fundamentals! Focus on:
        - Creating high-quality content regularly
        - Building quality backlinks
        - Monitoring performance with Google Search Console
        """)
    elif score >= 60:
        st.warning(f"""
        **Good SEO Score: {score}%** 👍
        
        You're on the right track! To improve further:
        - Fix the warning issues above
        - Add missing social media tags
        - Optimize your content for target keywords
        """)
    else:
        st.error(f"""
        **SEO Score Needs Work: {score}%** 🔧
        
        Don't worry - every website starts somewhere! Priority actions:
        - Fix all critical issues first
        - Add basic meta tags (title, description)
        - Set up social media sharing tags
        """)
    
    # Enhanced Previews section
    st.markdown("### 👀 Visual Previews")
    st.markdown("See how your website appears across different platforms:")
    
    # Responsive preview tabs
    preview_tab1, preview_tab2, preview_tab3 = st.tabs(["🔍 Google Search", "📘 Facebook", "🐦 Twitter/X"])
    
    with preview_tab1:
        st.markdown("#### How your site appears in Google search results")
        with st.container():
            st.markdown(f"""
            <div class="preview-container">
                <div style="border: 1px solid #dadce0; border-radius: 8px; padding: 20px; background-color: white; max-width: 600px; margin: 0 auto;">
                    <div style="color: #1a0dab; font-size: 20px; font-family: arial,sans-serif; margin-bottom: 4px; cursor: pointer;">
                        {format_preview_text(results['meta_tags'].get('title', 'No title found'), 60)}
                    </div>
                    <div style="color: #006621; font-size: 14px; margin-bottom: 4px;">
                        {get_domain_from_url(st.session_state.url)} ›
                    </div>
                    <div style="color: #4d5156; font-size: 14px; line-height: 1.5;">
                        {format_preview_text(results['meta_tags'].get('description', 'No description available - this will hurt your click-through rate'), 160)}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Google-specific tips
        st.markdown("""
        <div class="seo-tip">
            <strong>🎯 Google Search Tips:</strong>
            <ul>
                <li>Title should be compelling and include your main keyword</li>
                <li>Description acts as your "ad copy" - make it clickable!</li>
                <li>Length matters: Google may truncate long titles and descriptions</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with preview_tab2:
        st.markdown("#### How your content appears when shared on Facebook")
        
        og_title = results['meta_tags'].get('og:title', results['meta_tags'].get('title', 'No title'))
        og_description = results['meta_tags'].get('og:description', results['meta_tags'].get('description', 'No description'))
        og_image = results['meta_tags'].get('og:image', '')
        
        with st.container():
            st.markdown(f"""
            <div class="preview-container">
                <div style="border: 1px solid #dddfe2; border-radius: 8px; overflow: hidden; max-width: 500px; background-color: white; margin: 0 auto;">
                    {f'<div style="height: 260px; background: linear-gradient(45deg, #f0f2f5, #e4e6ea); display: flex; align-items: center; justify-content: center; color: #65676b; font-size: 14px;">🖼️ Featured Image<br><small style="font-size: 12px;">{og_image[:50] + "..." if og_image and len(og_image) > 50 else og_image or "No image specified"}</small></div>' if og_image else '<div style="height: 120px; background: #f0f2f5; display: flex; align-items: center; justify-content: center; color: #65676b; font-size: 14px;">📷 No image specified</div>'}
                    <div style="padding: 16px;">
                        <div style="font-size: 12px; color: #606770; text-transform: uppercase; margin-bottom: 6px; font-weight: 600;">
                            {get_domain_from_url(st.session_state.url).upper()}
                        </div>
                        <div style="font-size: 16px; font-weight: 600; color: #1d2129; margin-bottom: 6px; line-height: 1.3;">
                            {format_preview_text(og_title, 95)}
                        </div>
                        <div style="font-size: 14px; color: #606770; line-height: 1.4;">
                            {format_preview_text(og_description, 160)}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="seo-tip">
            <strong>📘 Facebook Sharing Tips:</strong>
            <ul>
                <li>Use high-quality images (1200x630px recommended)</li>
                <li>Keep titles under 95 characters</li>
                <li>Write engaging descriptions that encourage clicks</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with preview_tab3:
        st.markdown("#### How your content appears in Twitter/X cards")
        
        twitter_title = results['meta_tags'].get('twitter:title', results['meta_tags'].get('title', 'No title'))
        twitter_description = results['meta_tags'].get('twitter:description', results['meta_tags'].get('description', 'No description'))
        twitter_image = results['meta_tags'].get('twitter:image', '')
        
        with st.container():
            st.markdown(f"""
            <div class="preview-container">
                <div style="border: 1px solid #cfd9de; border-radius: 16px; overflow: hidden; max-width: 500px; background-color: white; margin: 0 auto;">
                    {f'<div style="height: 250px; background: linear-gradient(45deg, #f7f9fa, #e1e8ed); display: flex; align-items: center; justify-content: center; color: #536471; font-size: 14px;">🖼️ Twitter Image<br><small style="font-size: 12px;">{twitter_image[:50] + "..." if twitter_image and len(twitter_image) > 50 else twitter_image or "No image specified"}</small></div>' if twitter_image else '<div style="height: 100px; background: #f7f9fa; display: flex; align-items: center; justify-content: center; color: #536471; font-size: 14px;">📷 No image specified</div>'}
                    <div style="padding: 16px;">
                        <div style="font-size: 15px; font-weight: 700; color: #0f1419; margin-bottom: 6px; line-height: 1.3;">
                            {format_preview_text(twitter_title, 70)}
                        </div>
                        <div style="font-size: 15px; color: #536471; margin-bottom: 6px; line-height: 1.4;">
                            {format_preview_text(twitter_description, 125)}
                        </div>
                        <div style="font-size: 15px; color: #536471;">
                            🔗 {get_domain_from_url(st.session_state.url)}
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="seo-tip">
            <strong>🐦 Twitter/X Card Tips:</strong>
            <ul>
                <li>Summary cards work great for most content</li>
                <li>Large image cards get more engagement</li>
                <li>Keep titles concise and impactful</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Beginner-friendly comparison section
    st.markdown("### 📋 SEO Checklist for Beginners")
    
    # Create a visual checklist
    checklist_items = [
        ("Page Title", results['meta_tags'].get('title'), "Should be 50-60 characters and include main keywords"),
        ("Meta Description", results['meta_tags'].get('description'), "Should be 150-160 characters and compelling"),
        ("Facebook Title", results['meta_tags'].get('og:title'), "Optimizes how your page looks when shared on Facebook"),
        ("Facebook Description", results['meta_tags'].get('og:description'), "Description for Facebook shares"),
        ("Facebook Image", results['meta_tags'].get('og:image'), "Image shown when shared on Facebook (1200x630px)"),
        ("Twitter Card", results['meta_tags'].get('twitter:card'), "Enables rich previews on Twitter/X"),
        ("Viewport Tag", results['meta_tags'].get('viewport'), "Essential for mobile-friendly display"),
        ("Language Tag", results['meta_tags'].get('lang'), "Helps search engines understand your content language"),
    ]
    
    for item_name, item_value, item_description in checklist_items:
        if item_value:
            st.success(f"✅ **{item_name}**: Present")
            with st.expander(f"View {item_name} details"):
                st.code(f"{item_value[:100]}{'...' if len(item_value) > 100 else ''}")
                st.info(f"💡 {item_description}")
        else:
            st.error(f"❌ **{item_name}**: Missing")
            with st.expander(f"Why {item_name} is important"):
                st.info(f"💡 {item_description}")
    
    # Meta Tags Details
    st.markdown("### 🏷️ All Meta Tags Found")
    
    if results['meta_tags']:
        # Create expandable sections for different tag types
        basic_tags = {}
        og_tags = {}
        twitter_tags = {}
        other_tags = {}
        
        for key, value in results['meta_tags'].items():
            if key.startswith('og:'):
                og_tags[key] = value
            elif key.startswith('twitter:'):
                twitter_tags[key] = value
            elif key in ['title', 'description', 'keywords']:
                basic_tags[key] = value
            else:
                other_tags[key] = value
        
        col1, col2 = st.columns(2)
        
        with col1:
            if basic_tags:
                with st.expander("📝 Basic SEO Tags", expanded=True):
                    for key, value in basic_tags.items():
                        st.text(f"{key}: {value}")
            
            if og_tags:
                with st.expander("📘 Open Graph Tags"):
                    for key, value in og_tags.items():
                        st.text(f"{key}: {value}")
        
        with col2:
            if twitter_tags:
                with st.expander("🐦 Twitter Card Tags"):
                    for key, value in twitter_tags.items():
                        st.text(f"{key}: {value}")
            
            if other_tags:
                with st.expander("🔧 Other Meta Tags"):
                    for key, value in other_tags.items():
                        st.text(f"{key}: {value[:100]}{'...' if len(value) > 100 else ''}")
    else:
        st.warning("No meta tags found on this page.")
    
    # Export functionality
    st.subheader("📁 Export Analysis")
    
    if st.button("📄 Export Analysis Report (JSON)"):
        report_data = {
            'url': st.session_state.url,
            'analysis_date': results.get('timestamp'),
            'seo_score': score,
            'seo_analysis': results['seo_analysis'],
            'meta_tags': results['meta_tags']
        }
        
        json_str = export_to_json(report_data)
        st.download_button(
            label="Download JSON Report",
            data=json_str,
            file_name=f"seo_analysis_{get_domain_from_url(st.session_state.url)}.json",
            mime="application/json"
        )

# Enhanced Sidebar with beginner-friendly information
with st.sidebar:
    st.markdown("## 📚 SEO Learning Center")
    
    # Beginner's guide section
    with st.expander("🎯 What is SEO?", expanded=False):
        st.markdown("""
        **SEO (Search Engine Optimization)** helps your website appear higher in search results like Google.
        
        **Why it matters:**
        - More people find your website
        - Increased traffic and visitors
        - Better user experience
        - Higher credibility and trust
        """)
    
    with st.expander("📊 Understanding Your Score", expanded=False):
        st.markdown("""
        **Score Ranges:**
        - 🟢 **80-100%**: Excellent SEO setup
        - 🟡 **60-79%**: Good, with room for improvement
        - 🔴 **Below 60%**: Needs significant work
        
        **Focus on fixing errors first, then warnings.**
        """)
    
    with st.expander("🔍 Meta Tags Explained", expanded=False):
        st.markdown("""
        **Title Tag**: The clickable headline in search results
        
        **Meta Description**: The snippet text under your title
        
        **Open Graph**: Controls how your page looks on Facebook
        
        **Twitter Cards**: Controls how your page looks on Twitter/X
        """)
    
    with st.expander("🚀 Quick Wins", expanded=False):
        st.markdown("""
        **Easy improvements:**
        1. Write compelling page titles (50-60 chars)
        2. Create engaging descriptions (150-160 chars)
        3. Add social media tags
        4. Use relevant keywords naturally
        5. Ensure mobile-friendly design
        """)
    
    with st.expander("📱 Social Media Setup", expanded=False):
        st.markdown("""
        **Required tags for sharing:**
        - `og:title` - Facebook title
        - `og:description` - Facebook description
        - `og:image` - Facebook image (1200x630px)
        - `twitter:card` - Twitter card type
        - `twitter:title` - Twitter title
        - `twitter:description` - Twitter description
        """)
    
    with st.expander("⚡ Advanced Tips", expanded=False):
        st.markdown("""
        **Pro techniques:**
        - Use schema markup for rich snippets
        - Optimize for featured snippets
        - Add canonical URLs
        - Set up proper redirects
        - Monitor Core Web Vitals
        """)
    
    st.markdown("---")
    st.markdown("### 🔗 Helpful Resources")
    st.markdown("""
    - [Google Search Console](https://search.google.com/search-console)
    - [Facebook Sharing Debugger](https://developers.facebook.com/tools/debug/)
    - [Twitter Card Validator](https://cards-dev.twitter.com/validator)
    """)
    
    st.markdown("---")
    st.info("💡 **Tip**: Start with fixing errors, then warnings. Focus on one improvement at a time!")

# Footer
st.markdown("---")
st.markdown("Built with ❤️ using Streamlit | Check your website's SEO performance")
