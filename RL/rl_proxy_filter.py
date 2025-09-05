#!/usr/bin/env python3
"""
RL Proxy Filter - mitmproxy script using reinforcement learning
Replaces the threshold-based AI filter with adaptive RL
"""

import json
import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path
from mitmproxy import http, ctx
import rl_filter
import sqlite3

class RLProxyFilter:
    """Proxy filter using reinforcement learning"""
    
    def __init__(self):
        self.rl_filter = rl_filter.get_rl_filter()
        # Load mission from root directory, not RL subdirectory
        self.mission_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "mission.json")
        self.logger = logging.getLogger(__name__)
        self.stats = {
            "requests_processed": 0,
            "requests_allowed": 0,
            "requests_blocked": 0,
            "session_start": datetime.now().isoformat(),
            "feedback_provided": 0
        }
        
        # Load mission
        self.load_mission()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # Initialize feedback collection
        self._setup_feedback_system()
    
    def _setup_feedback_system(self):
        """Setup feedback collection system"""
        self.pending_feedback = {}  # Store recent decisions for feedback
        self.feedback_timeout = 300  # 5 minutes to provide feedback
    
    def load_mission(self):
        """Load mission from mission.json file"""
        try:
            if os.path.exists(self.mission_file):
                with open(self.mission_file, 'r') as f:
                    mission_data = json.load(f)
                    mission_text = mission_data.get('mission', '')
                    if mission_text:
                        self.rl_filter.set_mission(mission_text)
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
            self.rl_filter.set_mission(default_mission["mission"])
            self.logger.info("Created default mission file")
        except Exception as e:
            self.logger.error(f"Error creating default mission: {e}")
    
    def request(self, flow: http.HTTPFlow) -> None:
        """Handle incoming HTTP requests"""
        start_time = time.time()
        
        try:
            url = flow.request.pretty_url
            self.stats["requests_processed"] += 1
            
            # Get RL decision
            is_allowed = self.rl_filter.is_url_allowed(url)
            decision_time = (time.time() - start_time) * 1000
            
            if is_allowed:
                self.stats["requests_allowed"] += 1
                self.logger.info(f"ALLOW: {url} ({decision_time:.2f}ms)")
                
                # Store for potential feedback
                self._store_pending_feedback(url, True, decision_time)
                
            else:
                self.stats["requests_blocked"] += 1
                self.logger.info(f"BLOCK: {url} ({decision_time:.2f}ms)")
                
                # Store for potential feedback
                self._store_pending_feedback(url, False, decision_time)
                
                # Create enhanced blocked response with feedback option
                blocked_html = self._create_blocked_response_with_feedback(url)
                flow.response = http.Response.make(
                    403,
                    blocked_html,
                    {"Content-Type": "text/html; charset=utf-8"}
                )
            
            # Clean up old pending feedback
            self._cleanup_pending_feedback()
            
        except Exception as e:
            self.logger.error(f"Error processing request for {flow.request.pretty_url}: {e}")
            self.stats["requests_allowed"] += 1  # Allow on error for safety
    
    def _store_pending_feedback(self, url: str, was_allowed: bool, decision_time: float):
        """Store decision for potential user feedback"""
        current_time = time.time()
        
        # Clean URL for storage key
        url_key = url.split('?')[0]  # Remove query parameters for grouping
        
        self.pending_feedback[url_key] = {
            "url": url,
            "was_allowed": was_allowed,
            "timestamp": current_time,
            "decision_time": decision_time
        }
    
    def _cleanup_pending_feedback(self):
        """Remove old pending feedback entries"""
        current_time = time.time()
        expired_keys = [
            key for key, data in self.pending_feedback.items()
            if current_time - data["timestamp"] > self.feedback_timeout
        ]
        
        for key in expired_keys:
            del self.pending_feedback[key]
    
    def _create_blocked_response_with_feedback(self, url: str) -> str:
        """Create HTML response for blocked requests with feedback option"""
        
        # Get RL stats
        rl_stats = self.rl_filter.get_stats()
        mission_text = rl_stats.get('mission', 'your current mission')
        accuracy = rl_stats.get('accuracy', 0) * 100
        
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
                    max-width: 600px;
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
                .feedback {{
                    background: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 5px;
                    padding: 20px;
                    margin: 20px 0;
                }}
                .feedback-buttons {{
                    margin-top: 15px;
                }}
                .btn {{
                    padding: 10px 20px;
                    margin: 0 10px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    font-size: 14px;
                    text-decoration: none;
                    display: inline-block;
                }}
                .btn-correct {{
                    background-color: #28a745;
                    color: white;
                }}
                .btn-incorrect {{
                    background-color: #dc3545;
                    color: white;
                }}
                .stats {{
                    margin-top: 30px;
                    padding: 15px;
                    background: #f9f9f9;
                    border-radius: 5px;
                    font-size: 14px;
                }}
                .rl-stats {{
                    background: #e1f5fe;
                    border-left: 4px solid #0288d1;
                    padding: 10px;
                    margin: 10px 0;
                    font-size: 12px;
                }}
                .time {{
                    color: #666;
                    font-size: 12px;
                }}
            </style>
            <script>
                function provideFeedback(url, isCorrect) {{
                    // TODO: Implement actual feedback submission to backend
                    // Currently only shows confirmation - feedback doesn't reach the AI system
                    // Would need HTTP endpoint or WebSocket to send to handle_feedback_request()
                    var message = isCorrect ? 
                        "Thank you! This helps improve the AI's accuracy." : 
                        "Thank you! The AI will learn from this mistake.";
                    
                    document.getElementById('feedback-section').innerHTML = 
                        '<div style="background: #d4edda; color: #155724; padding: 10px; border-radius: 5px;">' + 
                        message + '<br><small>(Note: Feedback display only - backend integration pending)</small></div>';
                }}
            </script>
        </head>
        <body>
            <div class="container">
                <div class="icon">🤖</div>
                <h1>AI-Filtered Block</h1>
                <p>This website has been blocked by the AI filter to help you stay focused on your mission.</p>
                
                <div class="url">{url}</div>
                
                <div class="mission">
                    <strong>Your Current Mission:</strong><br>
                    {mission_text}
                </div>
                
                <div id="feedback-section" class="feedback">
                    <strong>Help Improve the AI:</strong><br>
                    Was this decision correct?
                    <div class="feedback-buttons">
                        <button class="btn btn-correct" onclick="provideFeedback('{url}', true)">
                            ✓ Correct (should block)
                        </button>
                        <button class="btn btn-incorrect" onclick="provideFeedback('{url}', false)">
                            ✗ Wrong (should allow)
                        </button>
                    </div>
                </div>
                
                <div class="stats">
                    <strong>Session Stats:</strong><br>
                    Requests Processed: {self.stats["requests_processed"]}<br>
                    Allowed: {self.stats["requests_allowed"]} | Blocked: {self.stats["requests_blocked"]}<br>
                    Block Rate: {(self.stats["requests_blocked"]/max(1,self.stats["requests_processed"])*100):.1f}%<br>
                    Feedback Provided: {self.stats["feedback_provided"]}
                </div>
                
                <div class="rl-stats">
                    <strong>AI Performance:</strong><br>
                    Total Decisions: {rl_stats.get('total_decisions', 0)}<br>
                    Learning Accuracy: {accuracy:.1f}%<br>
                    User Feedback Count: {rl_stats.get('user_feedback_count', 0)}<br>
                    Cache Hit Rate: {rl_stats.get('cache_hit_rate', 0)*100:.1f}%<br>
                    Fast Path Rate: {rl_stats.get('fast_path_rate', 0)*100:.1f}%<br>
                    Model Type: {rl_stats.get('model_type', 'unknown')}
                </div>
                
                <div class="time">
                    Blocked at {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
                </div>
            </div>
        </body>
        </html>
        """
        return html.strip()
    
    def provide_feedback_for_url(self, url: str, is_correct: bool):
        """Provide feedback for a specific URL decision"""
        try:
            # Provide feedback to RL system
            self.rl_filter.provide_feedback(url, is_correct)
            self.stats["feedback_provided"] += 1
            
            self.logger.info(f"Feedback provided for {url}: {'correct' if is_correct else 'incorrect'}")
            
            # Remove from pending feedback
            url_key = url.split('?')[0]
            if url_key in self.pending_feedback:
                del self.pending_feedback[url_key]
                
        except Exception as e:
            self.logger.error(f"Error providing feedback for {url}: {e}")
    
    def response(self, flow: http.HTTPFlow) -> None:
        """Handle HTTP responses"""
        pass
    
    def log_stats(self):
        """Log current session statistics"""
        total = self.stats["requests_processed"]
        rl_stats = self.rl_filter.get_stats()
        
        if total > 0:
            allowed_pct = (self.stats["requests_allowed"] / total) * 100
            blocked_pct = (self.stats["requests_blocked"] / total) * 100
            
            self.logger.info(f"SESSION STATS - Total: {total}, Allowed: {self.stats['requests_allowed']} ({allowed_pct:.1f}%), Blocked: {self.stats['requests_blocked']} ({blocked_pct:.1f}%)")
            self.logger.info(f"RL STATS - Feedback: {self.stats['feedback_provided']}, Accuracy: {rl_stats.get('accuracy', 0)*100:.1f}%, Cache Hit Rate: {rl_stats.get('cache_hit_rate', 0)*100:.1f}%, Fast Path Rate: {rl_stats.get('fast_path_rate', 0)*100:.1f}%")


# Create global instance for mitmproxy
rl_proxy_filter = RLProxyFilter()

# mitmproxy entry points
def request(flow: http.HTTPFlow) -> None:
    """mitmproxy entry point for requests"""
    rl_proxy_filter.request(flow)

def response(flow: http.HTTPFlow) -> None:
    """mitmproxy entry point for responses"""
    rl_proxy_filter.response(flow)

def configure(updated):
    """mitmproxy configuration handler"""
    if updated:
        ctx.log.info("RL Proxy filter configured")

def done():
    """mitmproxy shutdown handler"""
    rl_proxy_filter.log_stats()
    ctx.log.info("RL Proxy filter shutting down")


# Feedback API endpoint (simplified - in production would use proper web framework)
def handle_feedback_request(url: str, is_correct: bool):
    """Handle feedback from user interface"""
    rl_proxy_filter.provide_feedback_for_url(url, is_correct) 