# 🤖 LLM Data Generation Prompt for Anchorite Training

## Your Task
Generate 10,000 training examples in the enhanced metadata format for a productivity filtering AI. The AI needs to distinguish between educational/productive content and distracting/entertainment content.

## JSON Format Required
Follow the exact schema in `enhanced_training_data_schema.json`. Each example needs:

### Required Fields
```json
{
  "url": "realistic URL",
  "mission": "user's learning goal", 
  "label": 1 or 0,
  "category": "type of content",
  "enhanced_metadata": { /* ALL metadata fields */ }
}
```

## Distribution Requirements
- **5,000 productive examples (label: 1)**
- **5,000 distracting examples (label: 0)**

## Mission Templates (Use these)
1. "I want to learn logistic regression and machine learning techniques in Python for my data science career"
2. "I need to master web development with React and JavaScript to build modern applications"
3. "I'm studying computer science fundamentals including algorithms and data structures for my degree"
4. "I want to learn digital marketing and SEO strategies to grow my online business"
5. "I need to understand financial literacy and investment strategies for personal wealth building"

## URL Categories

### PRODUCTIVE (label: 1) - 5,000 examples
**YouTube Educational:**
- Channels: 3Blue1Brown, StatQuest, freeCodeCamp, Khan Academy, MIT OpenCourseWare, Crash Course
- Titles: "Logistic Regression Explained", "React Tutorial", "Data Structures in Python"
- high educational_indicators (10-20), low entertainment_indicators (0-2)

**Documentation Sites:**
- docs.python.org, pytorch.org, react.dev, developer.mozilla.org
- Long content_length (5000-20000), has_code: true, has_structured_content: true

**Educational Platforms:**
- coursera.org, edx.org, udacity.com, kaggle.com/learn
- High content_quality_score (0.8-0.95)

### DISTRACTING (label: 0) - 5,000 examples  
**Entertainment YouTube:**
- Music videos, comedy, gaming, vlogs, memes, reaction videos
- Titles: "Funny Cat Compilation", "Epic Fails 2024", "Celebrity Drama"
- High entertainment_indicators (8-15), low educational_indicators (0-2)

**Social Media:**
- reddit.com/r/funny, reddit.com/r/aww, twitter.com, instagram.com, tiktok.com
- Short content_length (500-2000), low content_quality_score (0.1-0.3)

**Entertainment Sites:**
- tmz.com, buzzfeed.com, netflix.com, twitch.tv
- entertainment_indicators > educational_indicators

## Critical Metadata Rules

### Educational Content (label: 1)
```json
"educational_indicators": 10-25,  // Keywords: tutorial, learn, course, algorithm, programming
"entertainment_indicators": 0-3,  // Minimal fun/funny keywords
"content_quality_score": 0.75-0.95,
"youtube_description": "Learn X with step-by-step examples...", // 200-500 chars
"has_code": true,  // For programming content
"has_structured_content": true,
"content_length": 5000-20000
```

### Entertainment Content (label: 0)
```json
"educational_indicators": 0-3,    // Minimal learning keywords  
"entertainment_indicators": 8-20, // Keywords: funny, viral, epic, meme, cute
"content_quality_score": 0.1-0.4,
"youtube_description": "Hilarious compilation of...", // 100-200 chars
"has_code": false,
"has_structured_content": false, 
"content_length": 500-3000
```

## Example Output Structure
```json
{
  "description": "Enhanced training data with 10,000 examples for Anchorite productivity AI",
  "total_examples": 10000,
  "examples": [
    {
      "url": "https://www.youtube.com/watch?v=example1",
      "mission": "I want to learn logistic regression...",
      "label": 1,
      "category": "educational_video",
      "enhanced_metadata": {
        "title": "Complete title",
        "meta_description": "Description", 
        "content_keywords": ["keyword1", "keyword2"],
        "extracted_text": "Sample content text...",
        "domain": "youtube.com",
        "path": "/watch",
        "query_params": {"v": "example1"},
        "has_video": true,
        "has_forms": false,
        "content_length": 8500,
        "images_count": 15,
        "links_count": 30,
        "external_links_count": 5,
        "response_time_ms": 250,
        "youtube_title": "Same as title for YouTube URLs",
        "youtube_description": "Detailed description 200-500 chars",
        "youtube_channel": "Channel Name",
        "youtube_category": "Education",
        "content_quality_score": 0.89,
        "educational_indicators": 15,
        "entertainment_indicators": 1,
        "og_title": "Same as title",
        "og_description": "Brief description",
        "og_type": "video",
        "paragraph_count": 12,
        "heading_count": 8,
        "list_count": 4,
        "avg_paragraph_length": 150,
        "has_structured_content": true,
        "has_code": true,
        "code_block_count": 6
      }
    }
    // ... 9,999 more examples
  ]
}
```

## Quality Checks
- Each URL should be realistic and match the domain
- Educational content should have mission alignment
- Entertainment content should clearly not match missions
- Metadata should be internally consistent
- Educational vs entertainment indicators should be opposite
- Content quality scores should match the content type

Generate realistic, varied examples that will train an AI to distinguish productive from distracting content with 90%+ accuracy.
