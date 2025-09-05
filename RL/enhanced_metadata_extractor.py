#!/usr/bin/env python3
"""
Enhanced Metadata Extractor for Anchorite RL System
Fetches real webpage content to enable content-aware filtering
"""

import requests
import re
import json
import time
import logging
try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Warning: BeautifulSoup not found. Install with: pip install beautifulsoup4")
    BeautifulSoup = None
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional, Any
import threading
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError


class EnhancedMetadataExtractor:
    """Enhanced metadata extractor that fetches actual webpage content"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        
        # Configure session with realistic headers
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        
        # Timeouts and limits
        self.request_timeout = 8  # seconds
        self.max_content_length = 500000  # 500KB max
        self.max_workers = 3
        
        # Cache for performance
        self.metadata_cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Threading for non-blocking operation
        self.executor = ThreadPoolExecutor(max_workers=self.max_workers)
        
    def extract_metadata_async(self, url: str) -> Dict[str, Any]:
        """Extract metadata asynchronously (non-blocking for proxy)"""
        try:
            # Check cache first
            cache_key = self._get_cache_key(url)
            if cache_key in self.metadata_cache:
                cached_data, timestamp = self.metadata_cache[cache_key]
                if time.time() - timestamp < self.cache_ttl:
                    return cached_data
            
            # Submit async task
            future = self.executor.submit(self._extract_metadata_sync, url)
            
            # Try to get result quickly, fallback to basic metadata if slow
            try:
                metadata = future.result(timeout=2.0)  # 2 second timeout for real-time filtering
                
                # Cache the result
                self.metadata_cache[cache_key] = (metadata, time.time())
                return metadata
                
            except FutureTimeoutError:
                self.logger.warning(f"Metadata extraction timeout for {url}, using basic metadata")
                return self._create_basic_metadata(url)
                
        except Exception as e:
            self.logger.error(f"Error in async metadata extraction for {url}: {e}")
            return self._create_basic_metadata(url)
    
    def _extract_metadata_sync(self, url: str) -> Dict[str, Any]:
        """Synchronously extract detailed metadata from URL"""
        try:
            # Basic metadata structure
            metadata = self._create_basic_metadata(url)
            
            # Fetch webpage content
            response = self.session.get(url, timeout=self.request_timeout, stream=True)
            
            # Check content length
            content_length = response.headers.get('content-length')
            if content_length and int(content_length) > self.max_content_length:
                self.logger.warning(f"Content too large for {url}, using basic metadata")
                return metadata
            
            # Read content with size limit
            content = b''
            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                if len(content) > self.max_content_length:
                    break
            
            # Parse HTML
            if BeautifulSoup is None:
                self.logger.warning("BeautifulSoup not available, using basic metadata")
                return metadata
            soup = BeautifulSoup(content, 'html.parser')
            
            # Enhanced metadata extraction
            metadata.update(self._extract_html_metadata(soup, url))
            metadata.update(self._extract_youtube_metadata(soup, url))
            metadata.update(self._extract_open_graph_metadata(soup))
            metadata.update(self._extract_content_analysis(soup))
            
            return metadata
            
        except requests.RequestException as e:
            self.logger.warning(f"Network error fetching {url}: {e}")
            return self._create_basic_metadata(url)
        except Exception as e:
            self.logger.error(f"Error extracting metadata from {url}: {e}")
            return self._create_basic_metadata(url)
    
    def _create_basic_metadata(self, url: str) -> Dict[str, Any]:
        """Create basic metadata when full extraction fails"""
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        if domain.startswith('www.'):
            domain = domain[4:]
            
        return {
            "url": url,
            "domain": domain,
            "path": parsed.path,
            "query_params": parse_qs(parsed.query),
            "title": "",
            "meta_description": "",
            "content_keywords": [],
            "extracted_text": "",
            "has_video": False,
            "has_forms": False,
            "content_length": 0,
            "images_count": 0,
            "links_count": 0,
            "external_links_count": 0,
            "response_time_ms": 0,
            "youtube_title": "",
            "youtube_description": "",
            "youtube_channel": "",
            "youtube_category": "",
            "content_quality_score": 0.0,
            "educational_indicators": 0,
            "entertainment_indicators": 0
        }
    
    def _extract_html_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract standard HTML metadata"""
        metadata = {}
        
        # Title
        title_tag = soup.find('title')
        metadata['title'] = title_tag.get_text().strip() if title_tag else ""
        
        # Meta description
        desc_tag = soup.find('meta', attrs={'name': 'description'})
        metadata['meta_description'] = desc_tag.get('content', "").strip() if desc_tag else ""
        
        # Keywords
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag:
            keywords = keywords_tag.get('content', "").split(',')
            metadata['content_keywords'] = [k.strip() for k in keywords if k.strip()]
        else:
            metadata['content_keywords'] = []
        
        # Content analysis
        text_content = soup.get_text()
        metadata['extracted_text'] = self._clean_text(text_content)[:1000]  # First 1000 chars
        metadata['content_length'] = len(text_content)
        
        # Media analysis
        metadata['has_video'] = bool(soup.find(['video', 'iframe']) or 'youtube.com' in url or 'vimeo.com' in url)
        metadata['has_forms'] = bool(soup.find('form'))
        metadata['images_count'] = len(soup.find_all('img'))
        
        # Link analysis
        links = soup.find_all('a', href=True)
        metadata['links_count'] = len(links)
        
        external_links = [link for link in links if self._is_external_link(link.get('href'), url)]
        metadata['external_links_count'] = len(external_links)
        
        return metadata
    
    def _extract_youtube_metadata(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract YouTube-specific metadata"""
        metadata = {
            "youtube_title": "",
            "youtube_description": "",
            "youtube_channel": "",
            "youtube_category": "",
            "youtube_keywords": []
        }
        
        if 'youtube.com' not in url and 'youtu.be' not in url:
            return metadata
        
        try:
            # YouTube title (multiple selectors for robustness)
            title_selectors = [
                'h1[class*="title"]',
                'h1.ytd-video-primary-info-renderer',
                'h1.ytd-watch-metadata',
                'meta[property="og:title"]',
                'title'
            ]
            
            for selector in title_selectors:
                title_elem = soup.select_one(selector)
                if title_elem:
                    if title_elem.name == 'meta':
                        metadata['youtube_title'] = title_elem.get('content', '').strip()
                    else:
                        metadata['youtube_title'] = title_elem.get_text().strip()
                    if metadata['youtube_title']:
                        break
            
            # YouTube description
            desc_selectors = [
                'meta[name="description"]',
                'meta[property="og:description"]',
                '[class*="description"]',
                '#description'
            ]
            
            for selector in desc_selectors:
                desc_elem = soup.select_one(selector)
                if desc_elem:
                    if desc_elem.name == 'meta':
                        metadata['youtube_description'] = desc_elem.get('content', '').strip()
                    else:
                        metadata['youtube_description'] = desc_elem.get_text().strip()
                    if metadata['youtube_description']:
                        break
            
            # Channel information
            channel_selectors = [
                'link[itemprop="name"]',
                '[class*="channel"]',
                'meta[property="og:site_name"]'
            ]
            
            for selector in channel_selectors:
                channel_elem = soup.select_one(selector)
                if channel_elem:
                    if channel_elem.name == 'meta':
                        metadata['youtube_channel'] = channel_elem.get('content', '').strip()
                    elif channel_elem.name == 'link':
                        metadata['youtube_channel'] = channel_elem.get('href', '').strip()
                    else:
                        metadata['youtube_channel'] = channel_elem.get_text().strip()
                    if metadata['youtube_channel']:
                        break
            
            # Extract keywords from content
            content_text = (metadata['youtube_title'] + " " + metadata['youtube_description']).lower()
            
            # Educational keywords
            educational_keywords = [
                'tutorial', 'learn', 'course', 'education', 'explain', 'guide', 'how to',
                'lesson', 'teaching', 'instruction', 'training', 'study', 'academic',
                'university', 'college', 'research', 'analysis', 'theory', 'concept',
                'algorithm', 'programming', 'coding', 'development', 'science',
                'mathematics', 'physics', 'chemistry', 'biology', 'history',
                'machine learning', 'data science', 'artificial intelligence',
                'logistic regression', 'neural network', 'deep learning'
            ]
            
            # Entertainment keywords  
            entertainment_keywords = [
                'funny', 'comedy', 'meme', 'cute', 'adorable', 'hilarious', 'lol',
                'entertainment', 'fun', 'game', 'play', 'music video', 'vlog',
                'reaction', 'prank', 'challenge', 'trend', 'viral', 'cat', 'dog',
                'pet', 'animal compilation', 'fail', 'epic', 'awesome', 'cool',
                'amazing', 'incredible', 'unbelievable', 'shocking'
            ]
            
            # Count indicators
            educational_count = sum(1 for keyword in educational_keywords if keyword in content_text)
            entertainment_count = sum(1 for keyword in entertainment_keywords if keyword in content_text)
            
            metadata['educational_indicators'] = educational_count
            metadata['entertainment_indicators'] = entertainment_count
            
            # Content quality scoring
            quality_score = 0.0
            
            # Length indicators (longer descriptions often mean more educational content)
            if len(metadata['youtube_description']) > 200:
                quality_score += 0.3
            if len(metadata['youtube_title']) > 30:
                quality_score += 0.2
                
            # Educational vs entertainment ratio
            if educational_count > entertainment_count:
                quality_score += 0.5
            elif entertainment_count > educational_count * 2:
                quality_score -= 0.4
                
            metadata['content_quality_score'] = max(0.0, min(1.0, quality_score))
            
        except Exception as e:
            self.logger.error(f"Error extracting YouTube metadata: {e}")
        
        return metadata
    
    def _extract_open_graph_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract Open Graph metadata"""
        og_data = {}
        
        og_tags = soup.find_all('meta', property=lambda x: x and x.startswith('og:'))
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if prop and content:
                og_data[f'og_{prop}'] = content
        
        return og_data
    
    def _extract_content_analysis(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Analyze content structure and quality"""
        analysis = {}
        
        # Text structure analysis
        paragraphs = soup.find_all('p')
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        lists = soup.find_all(['ul', 'ol'])
        
        analysis['paragraph_count'] = len(paragraphs)
        analysis['heading_count'] = len(headings)  
        analysis['list_count'] = len(lists)
        
        # Content depth indicators
        avg_paragraph_length = 0
        if paragraphs:
            total_length = sum(len(p.get_text()) for p in paragraphs)
            avg_paragraph_length = total_length / len(paragraphs)
        
        analysis['avg_paragraph_length'] = avg_paragraph_length
        analysis['has_structured_content'] = bool(headings and lists)
        
        # Technical content indicators
        code_blocks = soup.find_all(['code', 'pre'])
        analysis['has_code'] = bool(code_blocks)
        analysis['code_block_count'] = len(code_blocks)
        
        return analysis
    
    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove non-printable characters
        text = re.sub(r'[^\x20-\x7E]', '', text)
        return text.strip()
    
    def _is_external_link(self, href: str, base_url: str) -> bool:
        """Check if link is external"""
        try:
            base_domain = urlparse(base_url).netloc
            link_domain = urlparse(href).netloc
            return link_domain and link_domain != base_domain
        except:
            return False
    
    def _get_cache_key(self, url: str) -> str:
        """Generate cache key for URL"""
        return f"metadata_{hash(url)}"
    
    def shutdown(self):
        """Shutdown the executor"""
        self.executor.shutdown(wait=True)


# Global instance
_enhanced_metadata_extractor = None

def get_enhanced_metadata_extractor() -> EnhancedMetadataExtractor:
    """Get or create global enhanced metadata extractor instance"""
    global _enhanced_metadata_extractor
    if _enhanced_metadata_extractor is None:
        _enhanced_metadata_extractor = EnhancedMetadataExtractor()
    return _enhanced_metadata_extractor
