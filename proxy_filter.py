#!/usr/bin/env python3
"""
Proxy Filter - mitmproxy script for AI-driven URL filtering
Usage: mitmdump -s proxy_filter.py
"""

import json
import os
import logging
from mitmproxy import http, ctx
from mitmproxy.script import concurrent
import ai_filter
import time
from datetime import datetime

class ProxyFilter:
    def __init__(self):
        self.ai_filter = ai_filter.get_ai_filter()
        self.mission_file = "mission.json"
        self.stats = {
            "requests_processed": 0,
            "requests_allowed": 0,
            "requests_blocked": 0,
            "session_start": datetime.now().isoformat()
        }
        self.load_mission()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_mission(self):
        """Load mission from mission.json file"""
        try:
            if os.path.exists(self.mission_file):
                with open(self.mission_file, 'r') as f:
                    mission_data = json.load(f)
                    mission_text = mission_data.get('mission', '')
                    if mission_text:
                        self.ai_filter.set_mission(mission_text)
                        self.logger.info(f"Mission loaded: {mission_text}")
                    else:
                        self.logger.warning("No mission text found in mission.json")
            else:
                self.logger.warning(f"Mission file {self.mission_file} not found")
                self.create_default_mission()
        except Exception as e:
            self.logger.error(f"Error loading mission: {e}")
            self.create_default_mission()
    
    def create_default_mission(self):
        """Create a default mission file"""
        default_mission = {
            "mission": "Focus on productive work and learning, avoiding social media and entertainment distractions",
            "created": datetime.now().isoformat(),
            "description": "Default mission for productivity-focused browsing"
        }
        
        try:
            with open(self.mission_file, 'w') as f:
                json.dump(default_mission, f, indent=2)
            self.ai_filter.set_mission(default_mission["mission"])
            self.logger.info("Created default mission file")
        except Exception as e:
            self.logger.error(f"Error creating default mission: {e}")
    
    @concurrent
    def request(self, flow: http.HTTPFlow) -> None:
        """Handle incoming HTTP requests"""
        start_time = time.time()
        
        try:
            # Extract full URL
            url = flow.request.pretty_url
            self.stats["requests_processed"] += 1
            
            # Check if URL should be allowed
            is_allowed = self.ai_filter.is_url_allowed(url)
            decision_time = (time.time() - start_time) * 1000
            
            if is_allowed:
                # Allow request to proceed
                self.stats["requests_allowed"] += 1
                self.logger.info(f"ALLOW: {url} ({decision_time:.2f}ms)")
            else:
                # Block request with 403 Forbidden response
                self.stats["requests_blocked"] += 1
                self.logger.info(f"BLOCK: {url} ({decision_time:.2f}ms)")
                
                # Create blocked response
                blocked_html = self._create_blocked_response(url)
                flow.response = http.Response.make(
                    403,  # Forbidden
                    blocked_html,
                    {"Content-Type": "text/html; charset=utf-8"}
                )
                
            # Log performance metrics
            if decision_time > 50:  # Log slow decisions
                self.logger.warning(f"SLOW DECISION: {url} took {decision_time:.2f}ms (target: <50ms)")
                
        except Exception as e:
            self.logger.error(f"Error processing request for {flow.request.pretty_url}: {e}")
            # On error, allow request to avoid breaking user's browsing
            self.stats["requests_allowed"] += 1
    
    def _create_blocked_response(self, url: str) -> str:
        """Create HTML response for blocked requests"""
        mission_text = getattr(self.ai_filter, 'mission_text', 'your current mission')
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Access Blocked - Focus Mode</title>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            margin: 0;
            padding: 0;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .container {{
            background: white;
            padding: 40px;
            border-radius: 10px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            text-align: center;
            max-width: 500px;
            margin: 20px;
        }}
        .icon {{
            font-size: 64px;
            margin-bottom: 20px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .url {{
            background: #f5f5f5;
            padding: 10px;
            border-radius: 5px;
            font-family: monospace;
            word-break: break-all;
            margin: 20px 0;
        }}
        .mission {{
            background: #e8f4fd;
            border-left: 4px solid #2196F3;
            padding: 15px;
            margin: 20px 0;
            text-align: left;
        }}
        .stats {{
            margin-top: 30px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 5px;
            font-size: 14px;
        }}
        .time {{
            color: #666;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="icon">🔒</div>
        <h1>Access Blocked</h1>
        <p>This website has been blocked to help you stay focused on your mission.</p>
        
        <div class="url">{url}</div>
        
        <div class="mission">
            <strong>Your Current Mission:</strong><br>
            {mission_text}
        </div>
        
        <div class="stats">
            <strong>Session Stats:</strong><br>
            Requests Processed: {self.stats["requests_processed"]}<br>
            Allowed: {self.stats["requests_allowed"]} | Blocked: {self.stats["requests_blocked"]}<br>
            Block Rate: {(self.stats["requests_blocked"]/max(1,self.stats["requests_processed"])*100):.1f}%
        </div>
        
        <div class="time">
            Blocked at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        </div>
    </div>
</body>
</html>
        """
        return html.strip()
    
    def response(self, flow: http.HTTPFlow) -> None:
        """Handle HTTP responses (currently unused)"""
        pass
    
    def log_stats(self):
        """Log current session statistics"""
        total = self.stats["requests_processed"]
        if total > 0:
            allowed_pct = (self.stats["requests_allowed"] / total) * 100
            blocked_pct = (self.stats["requests_blocked"] / total) * 100
            
            self.logger.info(f"SESSION STATS - Total: {total}, Allowed: {self.stats['requests_allowed']} ({allowed_pct:.1f}%), Blocked: {self.stats['requests_blocked']} ({blocked_pct:.1f}%)")

# Create global instance for mitmproxy
proxy_filter = ProxyFilter()

# mitmproxy entry points
def request(flow: http.HTTPFlow) -> None:
    """mitmproxy entry point for requests"""
    proxy_filter.request(flow)

def response(flow: http.HTTPFlow) -> None:
    """mitmproxy entry point for responses"""
    proxy_filter.response(flow)

def configure(updated):
    """mitmproxy configuration handler"""
    if updated:
        ctx.log.info("Proxy filter configured")

def done():
    """mitmproxy shutdown handler"""
    proxy_filter.log_stats()
    ctx.log.info("Proxy filter shutting down")