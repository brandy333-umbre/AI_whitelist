#!/usr/bin/env python3
"""
Proxy Filter Script for mitmdump
Filters web traffic based on user's mission and productivity goals
"""

import json
import logging
import re
from pathlib import Path
from datetime import datetime
from urllib.parse import urlparse
import appdirs

from mitmproxy import http
from mitmproxy.script import concurrent


class FocusProxyFilter:
    def __init__(self):
        self.app_name = "ProxyFocusAgent"
        self.app_dir = Path(appdirs.user_data_dir(self.app_name))
        
        # Configuration files
        self.mission_file = self.app_dir / "mission.json"
        self.config_file = self.app_dir / "config.json"
        self.blocked_log_file = self.app_dir / "blocked_requests.log"
        self.allowed_log_file = self.app_dir / "allowed_requests.log"
        
        # Load configuration
        self.load_mission()
        self.load_config()
        
        # Setup logging
        self.setup_logging()
        
        # Compile regex patterns for efficiency
        self.compile_patterns()
        
    def setup_logging(self):
        """Setup logging for proxy filtering"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger("ProxyFilter")
        
    def load_mission(self):
        """Load the user's current mission configuration"""
        default_mission = {
            "title": "Focus Session",
            "description": "Stay productive and avoid distractions",
            "allowed_domains": [
                "github.com", "stackoverflow.com", "python.org",
                "docs.python.org", "pypi.org", "readthedocs.io",
                "localhost", "127.0.0.1"
            ],
            "allowed_keywords": [
                "python", "programming", "coding", "development",
                "tutorial", "documentation", "api", "framework",
                "learn", "study", "education"
            ],
            "blocked_domains": [
                "facebook.com", "twitter.com", "x.com", "instagram.com",
                "youtube.com", "tiktok.com", "reddit.com", "netflix.com",
                "amazon.com", "ebay.com", "linkedin.com", "pinterest.com"
            ]
        }
        
        if self.mission_file.exists():
            try:
                with open(self.mission_file, 'r') as f:
                    self.mission = json.load(f)
                    # Merge with defaults for missing keys
                    for key, value in default_mission.items():
                        if key not in self.mission:
                            self.mission[key] = value
            except Exception as e:
                self.logger.error(f"Failed to load mission: {e}")
                self.mission = default_mission
        else:
            self.mission = default_mission
            
    def load_config(self):
        """Load proxy configuration"""
        default_config = {
            "log_all_requests": True,
            "strict_mode": True,
            "allow_https": True,
            "block_social_media": True,
            "block_shopping": True,
            "block_entertainment": True
        }
        
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in self.config:
                            self.config[key] = value
            except Exception as e:
                self.logger.error(f"Failed to load config: {e}")
                self.config = default_config
        else:
            self.config = default_config
            
    def compile_patterns(self):
        """Compile regex patterns for efficient matching"""
        # Compile allowed domain patterns
        self.allowed_domain_patterns = []
        for domain in self.mission.get("allowed_domains", []):
            # Escape special regex characters and create pattern
            escaped_domain = re.escape(domain)
            # Allow subdomains
            pattern = rf"(^|\.)({escaped_domain})$"
            self.allowed_domain_patterns.append(re.compile(pattern, re.IGNORECASE))
            
        # Compile blocked domain patterns
        self.blocked_domain_patterns = []
        for domain in self.mission.get("blocked_domains", []):
            escaped_domain = re.escape(domain)
            pattern = rf"(^|\.)({escaped_domain})$"
            self.blocked_domain_patterns.append(re.compile(pattern, re.IGNORECASE))
            
        # Compile keyword patterns
        self.keyword_patterns = []
        for keyword in self.mission.get("allowed_keywords", []):
            pattern = re.compile(rf"\b{re.escape(keyword)}\b", re.IGNORECASE)
            self.keyword_patterns.append(pattern)
            
    def is_domain_allowed(self, domain):
        """Check if a domain is explicitly allowed"""
        if not domain:
            return False
            
        # Check if domain matches any allowed patterns
        for pattern in self.allowed_domain_patterns:
            if pattern.search(domain):
                return True
                
        return False
        
    def is_domain_blocked(self, domain):
        """Check if a domain is explicitly blocked"""
        if not domain:
            return False
            
        # Check if domain matches any blocked patterns
        for pattern in self.blocked_domain_patterns:
            if pattern.search(domain):
                return True
                
        return False
        
    def contains_allowed_keywords(self, url, title=""):
        """Check if URL or title contains mission-relevant keywords"""
        text_to_check = f"{url} {title}".lower()
        
        for pattern in self.keyword_patterns:
            if pattern.search(text_to_check):
                return True
                
        return False
        
    def get_block_reason(self, url, domain):
        """Get specific reason for blocking a request"""
        if self.is_domain_blocked(domain):
            return f"Blocked domain: {domain}"
            
        if not self.is_domain_allowed(domain) and not self.contains_allowed_keywords(url):
            return f"Not in allowed domains and no relevant keywords: {domain}"
            
        return "Unknown block reason"
        
    def should_allow_request(self, flow: http.HTTPFlow):
        """Main decision logic for allowing/blocking requests"""
        url = flow.request.pretty_url
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        # Always allow localhost and local network requests
        if domain in ['localhost', '127.0.0.1'] or domain.startswith('192.168.') or domain.startswith('10.'):
            return True, "Local network request"
            
        # Check if domain is explicitly blocked
        if self.is_domain_blocked(domain):
            return False, f"Domain {domain} is explicitly blocked"
            
        # Check if domain is explicitly allowed
        if self.is_domain_allowed(domain):
            return True, f"Domain {domain} is explicitly allowed"
            
        # If not explicitly allowed or blocked, check for keywords in strict mode
        if self.config.get("strict_mode", True):
            if self.contains_allowed_keywords(url):
                return True, f"URL contains allowed keywords: {url}"
            else:
                return False, f"Strict mode: URL not explicitly allowed and no keywords: {url}"
        else:
            # In non-strict mode, allow by default unless explicitly blocked
            return True, f"Non-strict mode: allowing {url}"
            
    def log_request(self, flow: http.HTTPFlow, allowed: bool, reason: str):
        """Log the request decision"""
        timestamp = datetime.now().isoformat()
        url = flow.request.pretty_url
        method = flow.request.method
        
        log_entry = f"{timestamp} | {method} | {url} | {reason}\n"
        
        try:
            if allowed:
                with open(self.allowed_log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
            else:
                with open(self.blocked_log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry)
        except Exception as e:
            self.logger.error(f"Failed to log request: {e}")
            
        if self.config.get("log_all_requests", True):
            status = "ALLOWED" if allowed else "BLOCKED"
            self.logger.info(f"{status}: {method} {url} - {reason}")
            
    def create_block_response(self, flow: http.HTTPFlow, reason: str):
        """Create a blocked response page"""
        block_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Focus Session - Site Blocked</title>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    max-width: 600px;
                    margin: 100px auto;
                    padding: 20px;
                    text-align: center;
                    background-color: #f5f5f5;
                }}
                .block-container {{
                    background-color: white;
                    padding: 40px;
                    border-radius: 10px;
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #e74c3c;
                    margin-bottom: 20px;
                }}
                .mission {{
                    background-color: #3498db;
                    color: white;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                }}
                .url {{
                    background-color: #ecf0f1;
                    padding: 10px;
                    border-radius: 5px;
                    font-family: monospace;
                    word-break: break-all;
                }}
            </style>
        </head>
        <body>
            <div class="block-container">
                <h1>🔒 Site Blocked - Focus Session Active</h1>
                <p><strong>This site has been blocked to help you stay focused on your mission.</strong></p>
                
                <div class="mission">
                    <h3>Current Mission: {self.mission.get('title', 'Focus Session')}</h3>
                    <p>{self.mission.get('description', 'Stay productive and avoid distractions')}</p>
                </div>
                
                <p><strong>Blocked URL:</strong></p>
                <div class="url">{flow.request.pretty_url}</div>
                
                <p><strong>Reason:</strong> {reason}</p>
                
                <p>To access this site, you'll need to end your focus session first.</p>
                <p><em>Stay strong and keep working toward your goals! 💪</em></p>
            </div>
        </body>
        </html>
        """
        
        flow.response = http.Response.make(
            200,  # Return 200 instead of error to avoid browser retry loops
            block_html,
            {"Content-Type": "text/html; charset=utf-8"}
        )


# Global filter instance
filter_instance = FocusProxyFilter()


@concurrent
def request(flow: http.HTTPFlow) -> None:
    """Handle incoming HTTP requests"""
    try:
        allowed, reason = filter_instance.should_allow_request(flow)
        
        if not allowed:
            filter_instance.log_request(flow, False, reason)
            filter_instance.create_block_response(flow, reason)
        else:
            filter_instance.log_request(flow, True, reason)
            
    except Exception as e:
        # In case of error, log and allow the request to avoid breaking browsing
        filter_instance.logger.error(f"Error processing request: {e}")
        filter_instance.log_request(flow, True, f"Error occurred, allowing by default: {e}")


def response(flow: http.HTTPFlow) -> None:
    """Handle HTTP responses (optional processing)"""
    try:
        # Could add response modification here if needed
        # For now, just pass through
        pass
    except Exception as e:
        filter_instance.logger.error(f"Error processing response: {e}")


# Entry point for mitmdump
def start():
    """Called when the script starts"""
    filter_instance.logger.info("Focus Proxy Filter started")
    filter_instance.logger.info(f"Mission: {filter_instance.mission.get('title', 'Unknown')}")
    filter_instance.logger.info(f"Allowed domains: {len(filter_instance.mission.get('allowed_domains', []))}")
    filter_instance.logger.info(f"Blocked domains: {len(filter_instance.mission.get('blocked_domains', []))}")


def done():
    """Called when the script shuts down"""
    filter_instance.logger.info("Focus Proxy Filter stopped")