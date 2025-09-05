# Universal Metadata Schema for Anchorite RL Training

## Overview

This document describes the universal metadata schema designed for Anchorite's reinforcement learning system. Unlike the previous hardcoded approach that only worked with specific platforms, this schema can extract useful data from **any website** to help the RL algorithm make intelligent filtering decisions.

## Key Improvements

### ❌ Old Approach (Hardcoded)
- Limited to specific platforms (YouTube, Twitter, etc.)
- Static platform detection
- Poor generalization to new websites
- Only ~800-1000 training examples

### ✅ New Approach (Universal)
- Works with **any website**
- Dynamic content analysis
- Extracts meaningful metadata from any HTTP response
- Supports 5000+ training examples

## Universal Metadata Schema

The JSON schema captures the most useful decision-making data that can be extracted from any website:

```json
{
  "url": "https://example.com/path/to/content?param=value",
  "method": "GET",
  "domain": "example.com",
  "path": "/path/to/content",
  "query_params": {
    "param": "value",
    "search": "machine learning"
  },
  "title": "Complete Guide to Machine Learning - Example Site",
  "meta_description": "Learn machine learning from basics to advanced concepts...",
  "og_title": "Machine Learning Guide",
  "og_description": "Comprehensive guide covering ML fundamentals",
  "og_type": "article",
  "content_keywords": ["machine", "learning", "tutorial", "guide", "programming"],
  "extracted_text": "Machine learning is a method of data analysis...",
  "content_length": 15420,
  "images_count": 8,
  "links_count": 23,
  "external_links_count": 5,
  "has_video": false,
  "has_forms": true,
  "language": "en",
  "content_type": "text/html",
  "status_code": 200,
  "response_time_ms": 245,
  "mission": "Learn machine learning and improve programming skills",
  "label": 1,
  "timestamp": 1703123456.789
}
```

## Field Descriptions

### Core Request Data
- **url**: Full URL of the request
- **method**: HTTP method (GET, POST, etc.)
- **domain**: Clean domain name (without www/protocols)
- **path**: URL path after domain
- **query_params**: Object containing URL parameters

### Content Metadata
- **title**: Page title from `<title>` tag
- **meta_description**: Content from meta description tag
- **og_title**: Open Graph title (social media preview)
- **og_description**: Open Graph description
- **og_type**: Content type (article, video, website, etc.)

### Content Analysis
- **content_keywords**: Array of significant words from content
- **extracted_text**: First 200-500 chars of visible text
- **content_length**: Total character count
- **images_count**: Number of images on page
- **links_count**: Total number of links
- **external_links_count**: Links to external domains

### Technical Indicators
- **has_video**: Boolean for video content presence
- **has_forms**: Boolean for form elements
- **language**: Page language (en, es, fr, etc.)
- **content_type**: HTTP response content type
- **status_code**: HTTP response status
- **response_time_ms**: Page load time

### Training Data
- **mission**: User's specific mission statement
- **label**: 1 = allow, 0 = block
- **timestamp**: Unix timestamp

## How the RL Algorithm Uses This Data

The system now extracts **1181-dimensional feature vectors** from this metadata:

1. **URL Embedding (384 dims)**: Semantic understanding of the URL structure
2. **Mission Embedding (384 dims)**: User's goal/intention
3. **Content Embedding (384 dims)**: Page content and meaning
4. **Dynamic URL Features (15 dims)**: Domain type, path analysis, parameters
5. **Content Features (10 dims)**: Media elements, interactivity, quality indicators
6. **Time Features (4 dims)**: When the request occurred

### Dynamic Features (No Hardcoding!)

Instead of checking `if 'youtube.com' in url`, the system now analyzes:

- **Domain patterns**: `.edu`, `.org`, `.gov`, documentation sites
- **Path patterns**: `/video/`, `/article/`, `/search/`, `/user/`
- **Content quality**: Has title, description, keywords, etc.
- **Media presence**: Videos, forms, images, external links
- **Semantic content**: What the page is actually about

## Generating Training Data

To create 5000 training examples, generate JSON objects following this schema:

### Educational Content (Label = 1)
```json
{
  "url": "https://docs.python.org/3/tutorial/",
  "title": "The Python Tutorial — Python 3.12.1 documentation",
  "meta_description": "Python programming tutorial with examples",
  "content_keywords": ["python", "tutorial", "programming", "documentation"],
  "has_video": false,
  "has_forms": false,
  "mission": "Learn Python programming for web development",
  "label": 1
}
```

### Distraction Content (Label = 0)
```json
{
  "url": "https://entertainment.com/funny-videos/compilation",
  "title": "Hilarious Fail Videos 2024 - Will Make You Laugh!",
  "meta_description": "Watch funny fail videos and comedy compilations",
  "content_keywords": ["funny", "videos", "comedy", "entertainment", "laugh"],
  "has_video": true,
  "mission": "Focus on learning data science and statistics",
  "label": 0
}
```

## Benefits of Universal Approach

1. **Works on any website**: Not limited to specific platforms
2. **Better decision context**: Rich content analysis vs just URL patterns
3. **Scalable training**: Can generate thousands of diverse examples
4. **Future-proof**: Adapts to new websites automatically
5. **Mission-aware**: Considers user's specific goals

## Implementation Notes

- The RL proxy can extract this metadata from any HTTP request/response
- The feature extractor dynamically analyzes content without hardcoded rules
- The neural network processes 1181-dimensional feature vectors
- Training can use 5000+ examples for better generalization

## Next Steps

1. Generate 5000 training examples using this schema
2. Pre-train the RL model with diverse, realistic data
3. Deploy the universal system that works on any website
4. Collect real user feedback to continuously improve

This universal approach makes Anchorite truly platform-agnostic while providing the RL algorithm with rich, meaningful data for intelligent filtering decisions.