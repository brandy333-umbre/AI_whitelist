#!/usr/bin/env python3
"""
RL Filter - Reinforcement Learning-based URL filtering
Replaces threshold-based filtering with adaptive learning
"""

import numpy as np
import sqlite3
import json
import time
import logging
import torch
import torch.nn as nn
import torch.optim as optim
import random
from collections import deque
from datetime import datetime
from typing import Tuple, List, Optional, Dict
import threading
import os
import re
import hashlib
try:
    from .enhanced_metadata_extractor import get_enhanced_metadata_extractor
except ImportError:
    # Fallback for when running as script (not as package)
    from enhanced_metadata_extractor import get_enhanced_metadata_extractor

class URLFeatureExtractor:
    """Extract features from URLs for RL agent"""
    
    def __init__(self):
        # Pure numerical feature extraction - no hardcoded rules
        # Let the pretrained model learn what's productive vs distracting
        pass
        
    def extract_features(self, url: str, mission: str) -> np.ndarray:
        """Extract feature vector from URL and mission (basic version)"""
        # Create minimal metadata for compatibility
        metadata = {
            "url": url,
            "title": "",
            "meta_description": "",
            "content_keywords": [],
            "extracted_text": "",
            "domain": self._extract_domain(url),
            "has_video": False,
            "has_forms": False,
            "content_length": 0
        }
        return self.extract_features_from_metadata(metadata, mission)
    
    def extract_features_from_metadata(self, metadata: dict, mission: str) -> np.ndarray:
        """Extract feature vector from universal metadata and mission"""
        url = metadata.get("url", "")
        
        # Create content text from metadata
        content_text = self._create_content_text_from_metadata(metadata, mission)
        
        # Generate simple text-based features (NO EXTERNAL MODELS)
        url_features_simple = self._extract_url_text_features(url)        # 384 dims
        mission_features_simple = self._extract_mission_text_features(mission)  # 384 dims  
        content_features_simple = self._extract_content_text_features(content_text)  # 384 dims
        
        # Dynamic URL characteristics (no hardcoded platforms)
        url_features = self._extract_dynamic_url_features(metadata)
        
        # Content features from metadata
        content_features = self._extract_content_features(metadata, mission)
        
        # Time features
        time_features = self._extract_time_features()
        
        # Combine all features (maintain 1181 dimensions for pretrained model)
        features = np.concatenate([
            url_features_simple,       # URL text features (384 dims)
            mission_features_simple,   # Mission text features (384 dims)  
            content_features_simple,   # Content text features (384 dims)
            url_features,              # Dynamic URL features (15 dims)
            content_features,          # Content-based features (10 dims)
            time_features              # Time features (4 dims)
        ])
        
        return features
    
    def _extract_url_text_features(self, url: str) -> np.ndarray:
        """Extract 384-dimensional text features from URL without external models"""
        features = []
        url_lower = url.lower()
        
        # Basic URL characteristics (50 features)
        features.extend([
            len(url), len(url_lower.split('/')), len(url_lower.split('.')),
            url_lower.count('/'), url_lower.count('?'), url_lower.count('&'),
            url_lower.count('='), url_lower.count('-'), url_lower.count('_'),
            url_lower.count('%'), len(url_lower.split('?')[0]), 
            1.0 if 'https' in url_lower else 0.0, 1.0 if 'www' in url_lower else 0.0,
            1.0 if '.com' in url_lower else 0.0, 1.0 if '.org' in url_lower else 0.0,
            1.0 if '.edu' in url_lower else 0.0, 1.0 if '.gov' in url_lower else 0.0,
            len([c for c in url_lower if c.isalpha()]), 
            len([c for c in url_lower if c.isdigit()]),
            len([c for c in url_lower if not c.isalnum()])
        ] + [0.0] * 30)  # Pad to 50
        
        # URL pattern features (100 features) - no hardcoded keywords
        # Simple URL complexity metrics instead
        features.extend([
            url_lower.count('youtube'), url_lower.count('reddit'), url_lower.count('github'),
            url_lower.count('stackoverflow'), url_lower.count('wikipedia'), url_lower.count('docs'),
            url_lower.count('learn'), url_lower.count('tutorial'), url_lower.count('course'),
            url_lower.count('video'), url_lower.count('watch'), url_lower.count('search'),
            1.0 if any(term in url_lower for term in ['api', 'doc', 'guide']) else 0.0,
            1.0 if any(term in url_lower for term in ['game', 'play', 'fun']) else 0.0,
            url_lower.count('/')  # Path depth indicator
        ] + [0.0] * 85)  # Pad to 100
        
        # Character n-grams as hash features (234 features)
        url_clean = re.sub(r'[^a-zA-Z0-9]', ' ', url_lower)
        words = url_clean.split()
        for i in range(234):
            hash_val = hash(f"url_{i}_{' '.join(words[:5])}")  # Use first 5 words
            features.append(float((hash_val % 1000) / 1000.0))  # Normalize to 0-1
            
        return np.array(features[:384], dtype=np.float32)
    
    def _extract_mission_text_features(self, mission: str) -> np.ndarray:
        """Extract 384-dimensional text features from mission without external models"""
        features = []
        mission_lower = mission.lower()
        
        # Basic text characteristics (50 features)
        words = mission_lower.split()
        features.extend([
            len(mission), len(words), len(set(words)),
            mission_lower.count(' '), mission_lower.count('.'), mission_lower.count(','),
            mission_lower.count('!'), mission_lower.count('?'), mission_lower.count(';'),
            mission_lower.count(':'), len([c for c in mission_lower if c.isalpha()]),
            len([c for c in mission_lower if c.isdigit()]),
            len([c for c in mission_lower if not c.isalnum()]),
            sum(len(word) for word in words) / max(len(words), 1),  # Avg word length
            max(len(word) for word in words) if words else 0,  # Max word length
        ] + [0.0] * 35)  # Pad to 50
        
        # Mission type indicators (100 features) - no hardcoded categorization
        # Simple mission pattern detection
        learning_indicators = sum(1 for term in ['learn', 'study', 'understand', 'master', 'tutorial'] if term in mission_lower)
        work_indicators = sum(1 for term in ['work', 'job', 'project', 'task', 'complete'] if term in mission_lower)
        creative_indicators = sum(1 for term in ['create', 'build', 'develop', 'design', 'make'] if term in mission_lower)
        research_indicators = sum(1 for term in ['research', 'find', 'information', 'data', 'explore'] if term in mission_lower)
        skill_indicators = sum(1 for term in ['skill', 'practice', 'improve', 'training', 'course'] if term in mission_lower)
        
        features.extend([
            learning_indicators, work_indicators, creative_indicators,
            research_indicators, skill_indicators,
            len(mission_lower.split()),  # Mission complexity
            mission_lower.count('?'),  # Questions in mission
            mission_lower.count('.'),  # Sentences in mission
        ] + [0.0] * 92)  # Pad to 100
        
        # Word-based hash features (234 features)
        for i in range(234):
            if i < len(words):
                hash_val = hash(f"mission_{i}_{words[i]}")
            else:
                hash_val = hash(f"mission_{i}_empty")
            features.append(float((hash_val % 1000) / 1000.0))  # Normalize to 0-1
            
        return np.array(features[:384], dtype=np.float32)
    
    def _extract_content_text_features(self, content_text: str) -> np.ndarray:
        """Extract 384-dimensional text features from content without external models"""
        features = []
        content_lower = content_text.lower()
        
        # Basic content characteristics (50 features)
        sentences = content_lower.split('.')
        words = content_lower.split()
        features.extend([
            len(content_text), len(words), len(set(words)), len(sentences),
            content_lower.count(' '), content_lower.count('.'), content_lower.count(','),
            content_lower.count('!'), content_lower.count('?'), content_lower.count(':'),
            content_lower.count(';'), content_lower.count('"'), content_lower.count("'"),
            len([c for c in content_lower if c.isalpha()]),
            len([c for c in content_lower if c.isdigit()]),
            sum(len(word) for word in words) / max(len(words), 1),  # Avg word length
            max(len(word) for word in words) if words else 0,  # Max word length
            len([word for word in words if len(word) > 10]),  # Long words
            content_lower.count('http'), content_lower.count('www'),
        ] + [0.0] * 31)  # Pad to 50
        
        # Content quality and type indicators (100 features)
        title_indicators = sum(1 for term in ['title', 'heading', 'header'] if term in content_lower)
        description_indicators = sum(1 for term in ['description', 'summary', 'about'] if term in content_lower)
        tutorial_indicators = sum(1 for term in ['tutorial', 'guide', 'how to', 'step'] if term in content_lower)
        documentation_indicators = sum(1 for term in ['documentation', 'docs', 'api', 'reference'] if term in content_lower)
        learning_indicators = sum(1 for term in ['learn', 'course', 'lesson', 'education'] if term in content_lower)
        
        # Content structure indicators
        has_lists = 1.0 if content_lower.count('•') > 0 or content_lower.count('-') > 3 else 0.0
        has_code = 1.0 if content_lower.count('code') > 0 or content_lower.count('function') > 0 else 0.0
        question_density = content_lower.count('?') / max(len(words), 1)
        
        features.extend([
            title_indicators, description_indicators, tutorial_indicators,
            documentation_indicators, learning_indicators,
            has_lists, has_code, question_density,
            len(sentences),  # Content structure complexity
            max(len(word) for word in words) if words else 0  # Longest word (technical terms)
        ] + [0.0] * 90)  # Pad to 100
        
        # Content-based hash features (234 features)
        content_words = words[:20]  # Use first 20 words for consistency
        for i in range(234):
            if i < len(content_words):
                hash_val = hash(f"content_{i}_{content_words[i]}")
            else:
                hash_val = hash(f"content_{i}_empty")
            features.append(float((hash_val % 1000) / 1000.0))  # Normalize to 0-1
            
        return np.array(features[:384], dtype=np.float32)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if "://" in url:
            url = url.split("://", 1)[1]
        domain = url.split("/")[0]
        if domain.startswith("www."):
            domain = domain[4:]
        return domain
    
    def _create_content_text_from_metadata(self, metadata: dict, mission: str = "") -> str:
        """Create enriched content text from enhanced metadata"""
        content_parts = []
        
        # YouTube-specific content (highest priority)
        youtube_title = metadata.get("youtube_title", "")
        youtube_description = metadata.get("youtube_description", "")
        youtube_channel = metadata.get("youtube_channel", "")
        
        if youtube_title:
            content_parts.append(f"Video Title: {youtube_title}")
        if youtube_description:
            content_parts.append(f"Video Description: {youtube_description[:300]}")
        if youtube_channel:
            content_parts.append(f"Channel: {youtube_channel}")
        
        # Educational/Entertainment indicators
        educational_score = metadata.get("educational_indicators", 0)
        entertainment_score = metadata.get("entertainment_indicators", 0)
        if educational_score > 0:
            content_parts.append(f"Educational Content Score: {educational_score}")
        if entertainment_score > 0:
            content_parts.append(f"Entertainment Content Score: {entertainment_score}")
        
        # Standard HTML metadata (fallback)
        if not youtube_title:  # Only use if no YouTube-specific data
            title = metadata.get("title", "")
            if title:
                content_parts.append(f"Page Title: {title}")
        
        if not youtube_description:  # Only use if no YouTube-specific data
            description = metadata.get("meta_description", "") or metadata.get("og_description", "")
            if description:
                content_parts.append(f"Description: {description[:200]}")
        
        # Content keywords
        keywords = metadata.get("content_keywords", [])
        if keywords:
            content_parts.append(f"Keywords: {' '.join(keywords[:10])}")
        
        # Extracted text (reduced priority for YouTube videos)
        extracted_text = metadata.get("extracted_text", "")
        if extracted_text and not youtube_title:  # Only use if no YouTube-specific data
            content_parts.append(f"Content: {extracted_text[:200]}")
        
        # Content quality indicators
        quality_score = metadata.get("content_quality_score", 0.0)
        if quality_score > 0:
            content_parts.append(f"Quality Score: {quality_score:.2f}")
        
        # Combine or fallback to URL
        if content_parts:
            combined_text = " | ".join(content_parts)
            # Enhance with mission-specific context
            if mission and "logistic regression" in mission.lower():
                combined_text += " | Mission Context: Machine Learning Education Focus"
            return combined_text
        else:
            # Simple URL text without external model processing
            url = metadata.get('url', '')
            if "://" in url:
                url = url.split("://", 1)[1]
            return f"Website: {url.replace('/', ' ').replace('-', ' ').replace('_', ' ')}"
    
    def _extract_dynamic_url_features(self, metadata: dict) -> np.ndarray:
        """Extract URL-based features without hardcoded platforms"""
        features = []
        
        url = metadata.get("url", "").lower()
        domain = metadata.get("domain", "").lower()
        path = metadata.get("path", "").lower()
        
        # Domain characteristics (dynamic)
        features.append(len(domain.split(".")))  # Domain complexity
        features.append(1.0 if domain.endswith(".edu") else 0.0)  # Educational domain
        features.append(1.0 if domain.endswith(".org") else 0.0)  # Organization domain
        features.append(1.0 if domain.endswith(".gov") else 0.0)  # Government domain
        features.append(1.0 if "docs" in domain or "documentation" in domain else 0.0)  # Documentation site
        
        # Path characteristics
        features.append(len(path.split("/")))  # Path depth
        features.append(1.0 if "/watch" in path or "/video" in path else 0.0)  # Video content
        features.append(1.0 if "/article" in path or "/post" in path or "/blog" in path else 0.0)  # Article content
        features.append(1.0 if "/search" in path or "/results" in path else 0.0)  # Search results
        features.append(1.0 if "/user" in path or "/profile" in path else 0.0)  # User profiles
        
        # Query parameters
        query_params = metadata.get("query_params", {})
        features.append(len(query_params))  # Number of query parameters
        features.append(1.0 if "q" in query_params or "search" in query_params else 0.0)  # Search query
        
        # URL length and complexity
        features.append(len(url))  # Total URL length
        features.append(url.count("&"))  # Number of parameters
        features.append(1.0 if "https" in url else 0.0)  # HTTPS indicator
        
        return np.array(features, dtype=np.float32)
    
    def _extract_content_features(self, metadata: dict, mission: str = "") -> np.ndarray:
        """Extract enhanced content-based features from metadata"""
        features = []
        
        # Enhanced content quality indicators
        features.append(1.0 if metadata.get("title", "") else 0.0)  # Has title
        features.append(1.0 if metadata.get("meta_description", "") else 0.0)  # Has description
        features.append(len(metadata.get("content_keywords", [])))  # Number of keywords
        features.append(metadata.get("content_length", 0) / 10000.0)  # Content length (normalized)
        
        # YouTube-specific features
        features.append(1.0 if metadata.get("youtube_title", "") else 0.0)  # Has YouTube title
        features.append(1.0 if metadata.get("youtube_description", "") else 0.0)  # Has YouTube description
        features.append(1.0 if metadata.get("youtube_channel", "") else 0.0)  # Has channel info
        
        # Educational vs Entertainment indicators (key for filtering!)
        educational_score = metadata.get("educational_indicators", 0)
        entertainment_score = metadata.get("entertainment_indicators", 0)
        features.append(min(educational_score / 10.0, 1.0))  # Educational indicators (normalized)
        features.append(min(entertainment_score / 10.0, 1.0))  # Entertainment indicators (normalized)
        
        # Content quality and educational bias
        quality_score = metadata.get("content_quality_score", 0.0)
        features.append(quality_score)  # Content quality score
        
        # Educational vs entertainment ratio (critical feature)
        if entertainment_score > 0:
            edu_ent_ratio = educational_score / entertainment_score
            features.append(min(edu_ent_ratio, 5.0) / 5.0)  # Normalize to 0-1, cap at 5:1 ratio
        else:
            features.append(1.0 if educational_score > 0 else 0.0)  # Pure educational or unknown
        
        # Mission alignment indicators
        mission_lower = mission.lower() if mission else ""
        youtube_title_lower = metadata.get("youtube_title", "").lower()
        youtube_desc_lower = metadata.get("youtube_description", "").lower()
        
        # Mission keyword matching
        mission_keywords = ['logistic regression', 'machine learning', 'python', 'tutorial', 'algorithm']
        title_mission_match = sum(1 for keyword in mission_keywords if keyword in youtube_title_lower)
        desc_mission_match = sum(1 for keyword in mission_keywords if keyword in youtube_desc_lower)
        
        features.append(min(title_mission_match / 3.0, 1.0))  # Title mission alignment
        features.append(min(desc_mission_match / 5.0, 1.0))   # Description mission alignment
        
        # Media and interactive elements (reduced from original 10 to fit new features)
        features.append(1.0 if metadata.get("has_video", False) else 0.0)  # Has video
        features.append(1.0 if metadata.get("has_forms", False) else 0.0)  # Has forms
        
        return np.array(features, dtype=np.float32)
    
    def _extract_time_features(self) -> np.ndarray:
        """Extract time-based features"""
        now = datetime.now()
        
        # Hour of day (0-23) normalized
        hour_norm = now.hour / 23.0
        
        # Day of week (0-6) as one-hot-like encoding
        day_of_week = now.weekday() / 6.0
        
        # Working hours indicator
        is_work_hours = 1.0 if 9 <= now.hour <= 17 else 0.0
        
        # Weekend indicator  
        is_weekend = 1.0 if now.weekday() >= 5 else 0.0
        
        return np.array([hour_norm, day_of_week, is_work_hours, is_weekend], dtype=np.float32)


class ProductivityClassifier(nn.Module):
    """Pretrained productivity classifier from pretraining"""
    def __init__(self, input_size):
        super().__init__()
        self.fc1 = nn.Linear(input_size, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 1)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(0.2)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = self.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.relu(self.fc2(x))
        x = self.dropout(x)
        x = self.relu(self.fc3(x))
        x = self.sigmoid(self.fc4(x))
        return x


class DQNNetwork(nn.Module):
    """Deep Q-Network for URL filtering decisions"""
    
    def __init__(self, input_size: int = 1187, hidden_size: int = 512):  # 384+384+384+15+16+4 = 1187
        super(DQNNetwork, self).__init__()
        
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(hidden_size, 256),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 2)  # 2 actions: 0=block, 1=allow
        )
    
    def forward(self, x):
        return self.network(x)


class RLFilter:
    """Reinforcement Learning URL Filter"""
    
    def __init__(self, cache_db_path: str = "rl_filter_cache.db", pretrained_model_path: str = "best_pretrained_model.pth"):
        self.cache_db_path = cache_db_path
        self.pretrained_model_path = pretrained_model_path
        self.mission_text = None
        self.feature_extractor = URLFeatureExtractor()
        self.enhanced_metadata_extractor = get_enhanced_metadata_extractor()
        self._lock = threading.Lock()
        
        # Initialize device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize pretrained productivity classifier
        # Feature size: 384 (URL) + 384 (mission) + 384 (content) + 15 (URL features) + 16 (enhanced content features) + 4 (time) = 1187
        self.input_size = 1186
        self.productivity_model = ProductivityClassifier(self.input_size).to(self.device)
        
        # Decision threshold for allow/block (probability > threshold = allow)
        self.decision_threshold = 0.5
        
        # Decision caching for performance
        self.decision_cache = {}  # URL -> (decision, timestamp)
        self.cache_ttl = 300  # 5 minutes cache TTL
        

        
        # Statistics
        self.stats = {
            "total_decisions": 0,
            "correct_decisions": 0,
            "user_feedback_count": 0,
            "average_reward": 0.0,
            "cache_hits": 0,
            "fast_path_decisions": 0
        }
        
        # Setup database and logging
        self._setup_database()
        self._setup_logging()
        self._load_model()

    def _build_mission_keywords(self) -> List[str]:
        """Extract simple mission keywords (no external NLP)."""
        if not self.mission_text:
            return []
        mission = self.mission_text.lower()
        raw_tokens = [
            token.strip(".,:;!?'\"()[]{}")
            for token in mission.split()
        ]
        stop = {
            'the','and','for','with','about','that','this','from','into','your','their','there','then',
            'have','will','should','would','could','what','when','where','why','how','make','create',
            'work','task','focus','session','goal','doing','doing,','do','on','to','of','in','at','a','an'
        }
        base = [t for t in raw_tokens if len(t) >= 3 and t not in stop]
        # Add bigrams (two-word phrases)
        bigrams: List[str] = []
        for i in range(len(base) - 1):
            w1, w2 = base[i], base[i+1]
            if len(w1) >= 3 and len(w2) >= 3:
                bigrams.append(f"{w1} {w2}")
        keywords = base + bigrams
        # Deduplicate and cap length
        dedup: List[str] = []
        for w in keywords:
            if w not in dedup:
                dedup.append(w)
        return dedup[:20]

    def _text_matches_mission(self, text: str) -> bool:
        """Check if any mission keyword appears in provided text."""
        if not text:
            return False
        text_l = text.lower()
        for kw in self._build_mission_keywords():
            if kw in text_l:
                return True
        return False

    def _is_youtube_video_mission_aligned(self, url: str) -> bool:
        """Fetch basic metadata for a YouTube video and check mission alignment.
        We only call this for watch/player endpoints to avoid performance hits elsewhere.
        """
        try:
            metadata = self.enhanced_metadata_extractor.extract_metadata_async(url)
            title = metadata.get('youtube_title') or metadata.get('title') or ''
            desc = metadata.get('youtube_description') or metadata.get('meta_description') or ''
            combined = f"{title} \n {desc}"
            # If no metadata available, allow (avoid over-blocking)
            if not combined.strip():
                return True
            return self._text_matches_mission(combined)
        except Exception as e:
            # Fall back to conservative block if we cannot determine alignment
            self.logger.info(f"Metadata check failed for {url}: {e}")
            return True
    
    def _setup_database(self):
        """Initialize database for caching and feedback"""
        with sqlite3.connect(self.cache_db_path) as conn:
            # Decision cache
            conn.execute("""
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    mission TEXT,
                    features BLOB,
                    action INTEGER,
                    confidence REAL,
                    timestamp REAL,
                    user_feedback INTEGER DEFAULT NULL,
                    reward REAL DEFAULT 0.0
                )
            """)
            
            # Training data
            conn.execute("""
                CREATE TABLE IF NOT EXISTS training_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    mission TEXT,
                    features BLOB,
                    label INTEGER,
                    source TEXT,
                    timestamp REAL
                )
            """)
            conn.commit()
    
    def _setup_logging(self):
        """Setup logging"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    

    
    def _get_cached_decision(self, url: str) -> Optional[bool]:
        """Get cached decision if available and not expired"""
        if url in self.decision_cache:
            decision, timestamp = self.decision_cache[url]
            if time.time() - timestamp < self.cache_ttl:
                self.stats["cache_hits"] += 1
                return decision
            else:
                del self.decision_cache[url]
        return None
    
    def _cache_decision(self, url: str, decision: bool):
        """Cache decision with timestamp"""
        self.decision_cache[url] = (decision, time.time())
    
    def clear_cache(self):
        """Clear decision cache"""
        with self._lock:
            self.decision_cache.clear()
            self.logger.info("Decision cache cleared")
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "cache_size": len(self.decision_cache),
            "cache_hits": self.stats["cache_hits"],
            "fast_path_decisions": self.stats["fast_path_decisions"]
        }
    
    def add_educational_domain(self, domain: str):
        """Add domain to educational whitelist"""
        # This would be used to dynamically update the fast decision system
        self.logger.info(f"Added educational domain: {domain}")
    
    def add_blocked_domain(self, domain: str):
        """Add domain to blocked list"""
        # This would be used to dynamically update the fast decision system
        self.logger.info(f"Added blocked domain: {domain}")
    
    def _load_model(self):
        """Load pretrained productivity classifier"""
        try:
            pretrained_path = os.path.join(os.path.dirname(__file__), self.pretrained_model_path)
            if os.path.exists(pretrained_path):
                # Load the pretrained model state dict
                pretrained_state_dict = torch.load(pretrained_path, map_location=self.device)
                self.productivity_model.load_state_dict(pretrained_state_dict)
                self.productivity_model.eval()  # Set to evaluation mode
                self.logger.info(f"Pretrained model loaded from {pretrained_path}")
            else:
                self.logger.warning(f"Pretrained model not found at {pretrained_path}, using randomly initialized model")
        except Exception as e:
            self.logger.error(f"Error loading pretrained model: {e}")
            self.logger.warning("Using randomly initialized model")
    
    def _save_stats(self):
        """Save current statistics"""
        try:
            stats_path = os.path.join(os.path.dirname(__file__), "rl_filter_stats.json")
            with open(stats_path, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving stats: {e}")
    
    def set_mission(self, mission_text: str):
        """Set mission text"""
        with self._lock:
            self.mission_text = mission_text
            self.logger.info(f"Mission set: {mission_text}")
    
    def is_url_allowed(self, url: str) -> bool:
        """Ultra-fast URL decision using dictionary lookups"""
        self.logger.info(f"FAST METHOD CALLED: {url}")
        url_lower = url.lower()
        
        # Check cache first (fastest path)
        cached_decision = self._get_cached_decision(url)
        if cached_decision is not None:
            return cached_decision
        
        # Extract domain for fast lookups
        domain = self._extract_domain_fast(url)
        
        # Dictionary-based fast decisions
        decision = self._fast_url_decision(url_lower, domain)
        
        # Cache the decision
        self._cache_decision(url, decision)
        return decision
    
    def _extract_domain_fast(self, url: str) -> str:
        """Fast domain extraction without regex"""
        if "://" in url:
            url = url.split("://", 1)[1]
        domain = url.split("/")[0]
        if domain.startswith("www."):
            domain = domain[4:]
        return domain.lower()
    
    def _fast_url_decision(self, url_lower: str, domain: str) -> bool:
        """Ultra-fast decision using dictionary lookups"""
        # Count decision for RL stats
        self.stats["total_decisions"] += 1

        # PRIORITY BLOCK: YouTube Shorts and Reel APIs (block BEFORE any allow rules)
        if 'youtube.com' in domain:
            youtube_shorts_markers = [
                '/shorts',               # Page path
                'el=shortspage',         # Shorts context param in stats calls
                'reel_watch_sequence',   # Shorts API
                'reel_item_watch',       # Shorts API
                'youtubei/v1/reel'       # Shorts API base
            ]
            if any(marker in url_lower for marker in youtube_shorts_markers):
                self.logger.info(f"BLOCK: {url_lower} (YouTube shorts/reel)")
                self.stats["fast_path_decisions"] += 1
                return False

        # 1. ALWAYS ALLOW - Infrastructure/Streaming
        always_allow = {
            'googlevideo.com', 'ggpht.com', 'ytimg.com', 'gstatic.com',
            'googleusercontent.com', 'googleapis.com', 'google.com',
            'youtube.com/api/stats', 'youtube.com/videoplayback',
            'youtube.com/get_video_info', 'youtube.com/iframe_api',
            'youtube.com/embed', 'youtube.com/player', 'youtube.com/s/player',
            'youtube.com/feather', 'youtube.com/iframe', 'youtube.com/static',
            'youtube.com/yt', 'youtube.com/accounts', 'youtube.com/channel',
            'youtube.com/user', 'youtube.com/c', 'youtube.com/playlist',
            'youtube.com/results', 'youtube.com/search'
        }
        
        if domain in always_allow or any(allow_domain in url_lower for allow_domain in always_allow):
            self.logger.info(f"ALLOW: {url_lower} (infrastructure)")
            self.stats["fast_path_decisions"] += 1
            return True
        
        # 2. ALWAYS ALLOW - Educational/Productive
        educational_domains = {
            'github.com', 'stackoverflow.com', 'wikipedia.org', 'docs.python.org',
            'python.org', 'realpython.com', 'geeksforgeeks.org', 'tutorialspoint.com',
            'w3schools.com', 'mdn.io', 'developer.mozilla.org', 'kaggle.com',
            'coursera.org', 'edx.org', 'udemy.com', 'freecodecamp.org',
            'leetcode.com', 'hackerrank.com', 'codewars.com', 'exercism.io',
            'rust-lang.org', 'golang.org', 'nodejs.org', 'reactjs.org',
            'vuejs.org', 'angular.io', 'djangoproject.com', 'flask.palletsprojects.com',
            'fastapi.tiangolo.com', 'pytorch.org', 'tensorflow.org', 'scikit-learn.org',
            'pandas.pydata.org', 'numpy.org', 'matplotlib.org', 'seaborn.pydata.org',
            'plotly.com', 'jupyter.org', 'anaconda.com', 'conda.io'
        }
        
        if domain in educational_domains:
            self.logger.info(f"ALLOW: {url_lower} (educational)")
            self.stats["fast_path_decisions"] += 1
            return True
        
        # 3. ALWAYS BLOCK - Known Distractions (Domain-based)
        always_block_domains = {
            'facebook.com', 'snapchat.com', 'reddit.com', '9gag.com', 'imgur.com',
            'buzzfeed.com', 'vice.com', 'vox.com', 'huffpost.com',
            'dailymail.co.uk', 'thesun.co.uk', 'tmz.com', 'eonline.com',
            'people.com', 'usmagazine.com', 'justjared.com', 'popsugar.com',
            'refinery29.com', 'bustle.com', 'cosmopolitan.com', 'elle.com',
            'vogue.com', 'glamour.com', 'seventeen.com', 'teenvogue.com',
            'tumblr.com', 'deviantart.com', 'flickr.com',
            '500px.com', 'behance.net', 'dribbble.com', 'artstation.com'
        }
        
        if domain in always_block_domains:
            self.logger.info(f"BLOCK: {url_lower} (distraction domain)")
            self.stats["fast_path_decisions"] += 1
            return False
        
        # 4. BLOCK - Specific URL Patterns (Path-based)
        always_block_patterns = [
            'instagram.com/reels/', 'instagram.com/explore/', 
            'x.com/home', 'x.com/explore', 'youtube.com/shorts/',
            'youtube.com/shorts', 'youtube.com/feed', 'youtube.com/trending',
            'instagram.com/reels', 'instagram.com/explore',
            'x.com/home', 'x.com/explore'
        ]
        
        # Debug: Log the URL being checked
        if 'youtube.com' in url_lower and ('shorts' in url_lower or 'short' in url_lower):
            self.logger.info(f"DEBUG: Checking YouTube URL: {url_lower}")
            self.logger.info(f"DEBUG: Domain: {domain}")
            self.logger.info(f"DEBUG: Contains 'shorts': {'shorts' in url_lower}")
            self.logger.info(f"DEBUG: Contains 'short': {'short' in url_lower}")
        
        if any(pattern in url_lower for pattern in always_block_patterns):
            self.logger.info(f"BLOCK: {url_lower} (distraction pattern)")
            self.stats["fast_path_decisions"] += 1
            return False
        
        # 5. BLOCK - YouTube Shorts (comprehensive) - MUST BE BEFORE YOUTUBE ALLOWANCE
        if 'youtube.com' in domain and ('shorts' in url_lower or '/shorts' in url_lower):
            self.logger.info(f"BLOCK: {url_lower} (YouTube shorts)")
            self.stats["fast_path_decisions"] += 1
            return False
        
        # 6. BLOCK - Social Media Patterns
        social_patterns = ['/feed', '/home', '/timeline', '/stories', '/reels', '/shorts']
        if any(pattern in url_lower for pattern in social_patterns):
            self.logger.info(f"BLOCK: {url_lower} (social pattern)")
            self.stats["fast_path_decisions"] += 1
            return False
        
        # 7. ALLOW - YouTube Educational Content (based on URL patterns)
        if 'youtube.com' in domain:
            educational_keywords = ['tutorial', 'course', 'learn', 'education', 'how to', 'guide', 'lesson']
            if any(keyword in url_lower for keyword in educational_keywords):
                self.logger.info(f"ALLOW: {url_lower} (educational YouTube)")
                self.stats["fast_path_decisions"] += 1
                return True
            
            # For standard watch/player endpoints, require mission alignment
            if ('/watch' in url_lower) or ('youtubei/v1/player' in url_lower):
                is_aligned = self._is_youtube_video_mission_aligned(url_lower)
                if not is_aligned:
                    self.logger.info(f"BLOCK: {url_lower} (YouTube not mission-aligned)")
                    self.stats["fast_path_decisions"] += 1
                    return False
                self.logger.info(f"ALLOW: {url_lower} (YouTube mission-aligned)")
                self.stats["fast_path_decisions"] += 1
                return True
            
            # Other YouTube pages (non-shorts): allow infra; policy fallback
            self.logger.info(f"ALLOW: {url_lower} (YouTube other)")
            self.stats["fast_path_decisions"] += 1
            return True
        
        # 8. ALLOW - Search Engines
        search_engines = {'google.com', 'bing.com', 'duckduckgo.com', 'yahoo.com'}
        if domain in search_engines:
            self.logger.info(f"ALLOW: {url_lower} (search engine)")
            self.stats["fast_path_decisions"] += 1
            return True
        
        # 9. DEFAULT - Allow unknown domains (conservative approach)
        self.logger.info(f"ALLOW: {url_lower} (default)")
        self.stats["fast_path_decisions"] += 1
        return True
    
    def is_url_allowed_with_metadata(self, metadata: dict) -> bool:
        """Make allow/block decision using universal metadata"""
        self.logger.info(f"SLOW METHOD CALLED: {metadata.get('url', 'unknown')}")
        if not self.mission_text:
            return False
        
        url = metadata.get("url", "").lower()
        domain = metadata.get("domain", "").lower()
        
        with self._lock:
            try:
                # Extract features from universal metadata
                features = self.feature_extractor.extract_features_from_metadata(metadata, self.mission_text)
                
                # Convert to tensor
                features_tensor = torch.FloatTensor(features).unsqueeze(0).to(self.device)
                
                # Get productivity probability from pretrained model
                with torch.no_grad():
                    productivity_probability = self.productivity_model(features_tensor)
                    confidence = productivity_probability.item()
                
                # Make decision based on threshold
                decision = confidence > self.decision_threshold  # True=allow, False=block
                action = int(decision)  # Convert to int for storage compatibility
                
                # Store decision for potential feedback
                url = metadata.get("url", "unknown")
                self._store_decision(url, features, action, confidence)
                
                self.stats["total_decisions"] += 1
                
                # Enhanced logging with key metadata
                title = metadata.get("title", "")
                domain = metadata.get("domain", "")
                log_info = f"{url}"
                if domain:
                    log_info += f" [{domain}]"
                if title:
                    log_info += f" - {title[:50]}..."
                    
                self.logger.info(f"{'ALLOW' if decision else 'BLOCK'}: {log_info} (productivity: {confidence:.3f})")
                
                return decision
                
            except Exception as e:
                self.logger.error(f"Error processing metadata for {metadata.get('url', 'unknown')}: {e}")
                return False
    
    def _store_decision(self, url: str, features: np.ndarray, action: int, confidence: float):
        """Store decision for potential user feedback"""
        with sqlite3.connect(self.cache_db_path) as conn:
            conn.execute("""
                INSERT INTO decisions (url, mission, features, action, confidence, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (url, self.mission_text, features.tobytes(), action, confidence, time.time()))
            conn.commit()
    
    def provide_feedback(self, url: str, is_correct: bool):
        """Provide feedback on a decision"""
        reward = 1.0 if is_correct else -1.0
        
        with sqlite3.connect(self.cache_db_path) as conn:
            # Update most recent decision for this URL
            conn.execute("""
                UPDATE decisions 
                SET user_feedback = ?, reward = ?
                WHERE url = ? AND mission = ?
                ORDER BY timestamp DESC
                LIMIT 1
            """, (int(is_correct), reward, url, self.mission_text))
            
            # Get the decision data for training
            result = conn.execute("""
                SELECT features, action, reward
                FROM decisions 
                WHERE url = ? AND mission = ? AND user_feedback IS NOT NULL
                ORDER BY timestamp DESC
                LIMIT 1
            """, (url, self.mission_text)).fetchone()
            
            if result:
                features = np.frombuffer(result[0], dtype=np.float32)
                action = result[1]
                reward = result[2]
                
                # Update statistics
                self.stats["user_feedback_count"] += 1
                if is_correct:
                    self.stats["correct_decisions"] += 1
                
                # Collect feedback stats periodically
                self._collect_feedback_stats()
                
                conn.commit()
    
    def _collect_feedback_stats(self):
        """Collect feedback statistics for model evaluation"""
        # Since we're using a pretrained model, we just collect stats
        # Future versions could use feedback to fine-tune the model
        if self.stats["user_feedback_count"] % 100 == 0:
            self._save_stats()
    
    def get_stats(self) -> dict:
        """Get current statistics"""
        accuracy = 0.0
        if self.stats["user_feedback_count"] > 0:
            accuracy = self.stats["correct_decisions"] / self.stats["user_feedback_count"]
        
        cache_hit_rate = 0.0
        if self.stats["total_decisions"] > 0:
            cache_hit_rate = self.stats["cache_hits"] / self.stats["total_decisions"]
        
        fast_path_rate = 0.0
        if self.stats["total_decisions"] > 0:
            fast_path_rate = self.stats["fast_path_decisions"] / self.stats["total_decisions"]
        
        return {
            "mission": self.mission_text,
            "total_decisions": self.stats["total_decisions"],
            "user_feedback_count": self.stats["user_feedback_count"],
            "accuracy": accuracy,
            "decision_threshold": self.decision_threshold,
            "model_type": "pretrained_classifier",
            "cache_hits": self.stats["cache_hits"],
            "cache_hit_rate": cache_hit_rate,
            "fast_path_decisions": self.stats["fast_path_decisions"],
            "fast_path_rate": fast_path_rate
        }


# Global instance
_rl_filter_instance = None

def get_rl_filter() -> RLFilter:
    """Get or create global RL filter instance"""
    global _rl_filter_instance
    if _rl_filter_instance is None:
        _rl_filter_instance = RLFilter()
    return _rl_filter_instance

def set_mission(mission_text: str):
    """Set mission for RL filter"""
    rl_filter = get_rl_filter()
    rl_filter.set_mission(mission_text)

def is_url_allowed(url: str) -> bool:
    """Check if URL is allowed using RL filter"""
    rl_filter = get_rl_filter()
    return rl_filter.is_url_allowed(url)

def provide_feedback(url: str, is_correct: bool):
    """Provide feedback on decision"""
    rl_filter = get_rl_filter()
    rl_filter.provide_feedback(url, is_correct)