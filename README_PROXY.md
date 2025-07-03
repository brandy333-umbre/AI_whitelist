# 🤖 AI-Driven Proxy Filter

An intelligent web filtering system that uses AI embeddings and mission-driven filtering to block distracting websites while allowing productive content. Unlike traditional domain-based blockers, this system understands the *semantic meaning* of websites and makes intelligent decisions based on your stated mission.

## 🎯 How It Works

1. **Proxy Interception**: All HTTP(S) requests flow through `mitmdump -s proxy_filter.py`
2. **Mission Context**: Your mission text is embedded using sentence transformers
3. **AI Decision**: Each URL is embedded and compared to your mission using cosine similarity
4. **Smart Caching**: Decisions are cached in SQLite for instant repeat lookups
5. **Fast Response**: Target ≤50ms decision time per URL with ≤20ms embeddings

## 🚀 Quick Start

### 1. Setup
```bash
# Install dependencies and configure
python setup_proxy.py

# Test the system
python test_filter.py
```

### 2. Configure Your Mission
Edit `mission.json` or let the setup script guide you:
```json
{
  "mission": "Focus on software development, programming tutorials, and technical documentation",
  "settings": {
    "similarity_threshold": 0.4
  }
}
```

### 3. Start the Proxy
```bash
# Linux/Mac
./run_proxy.sh

# Windows
run_proxy.bat

# Manual
mitmdump -s proxy_filter.py --listen-port 8080
```

### 4. Configure Your Browser
Set your browser's proxy to:
- **HTTP Proxy**: `127.0.0.1:8080`  
- **HTTPS Proxy**: `127.0.0.1:8080`

## 📊 Performance Features

### Lightning Fast Decisions
- **<20ms** embeddings using MiniLM model
- **<50ms** total decision time (including similarity computation)
- **<10ms** cached decisions from SQLite

### Smart Caching
- SQLite database stores URL decisions
- Instant repeat lookups
- Automatic cache invalidation when mission changes
- Performance metrics tracking

### Concurrent Processing
- `@concurrent` decorator for parallel request handling
- Thread-safe AI filter with locking
- No blocking of legitimate traffic

## 🧠 AI Intelligence

### Semantic Understanding
Instead of blocking `facebook.com`, the system understands:
- `facebook.com/business/tools` (might allow for work)
- `facebook.com/gaming` (likely block for focus)

### Mission Alignment
The system compares each URL against your mission:
```python
similarity = cosine_similarity(url_embedding, mission_embedding)
decision = similarity >= threshold  # Default: 0.4
```

### Contextual URL Processing
URLs are enhanced with context for better embedding:
```python
# "github.com/python/cpython" becomes:
# "website content about github com python cpython web page information"
```

## 🔧 Configuration

### Mission Settings
```json
{
  "mission": "Your focus objective",
  "settings": {
    "similarity_threshold": 0.4,    // Higher = more restrictive
    "cache_enabled": true,
    "log_level": "INFO"
  }
}
```

### Threshold Tuning
- **0.2-0.3**: Very permissive (allows most sites)
- **0.4**: Balanced (default)
- **0.5-0.6**: Restrictive (blocks more aggressively)
- **0.7+**: Very restrictive (only highly relevant sites)

## 📝 Logging & Monitoring

### Activity Logs
All decisions logged to `activity.log`:
```
2024-01-01 10:00:00 - INFO - ALLOW: https://github.com/python (similarity: 0.756, time: 15.2ms)
2024-01-01 10:00:01 - INFO - BLOCK: https://facebook.com (similarity: 0.123, time: 18.7ms)
2024-01-01 10:00:02 - INFO - CACHED - ALLOW: https://github.com/python (time: 2.1ms)
```

### Performance Monitoring
- Decision times tracked per URL
- Slow decisions (>50ms) flagged
- Cache hit rates monitored
- Session statistics

### Real-time Stats
Get filtering statistics:
```python
import ai_filter
stats = ai_filter.get_ai_filter().get_stats()
print(f"Blocked: {stats['blocked']}, Allowed: {stats['allowed']}")
```

## 🛡️ Blocking Behavior

### Allowed Requests
- Request forwarded unmodified to destination
- Normal browsing experience
- Full HTTPS support

### Blocked Requests
- Immediate 403 Forbidden response
- Beautiful blocking page with:
  - Current mission reminder
  - Session statistics
  - Blocked URL display
  - Timestamp

## 🔬 Testing & Validation

### Performance Testing
```bash
python test_filter.py
```

Tests include:
- **Latency**: All decisions <50ms
- **Accuracy**: Mission alignment validation
- **Edge Cases**: Invalid URLs, errors
- **Cache Performance**: <10ms cached lookups

### Manual Testing
```python
import ai_filter

# Set mission
ai_filter.set_mission("Focus on Python programming")

# Test URLs
test_urls = [
    "https://python.org/docs",      # Should allow
    "https://facebook.com",         # Should block  
    "https://stackoverflow.com/python"  # Should allow
]

for url in test_urls:
    allowed = ai_filter.is_url_allowed(url)
    print(f"{'ALLOW' if allowed else 'BLOCK'}: {url}")
```

## 📁 File Structure

```
├── proxy_filter.py      # Main mitmproxy script
├── ai_filter.py         # AI filtering logic
├── mission.json         # Mission configuration
├── setup_proxy.py       # Setup & installation
├── test_filter.py       # Testing suite
├── run_proxy.sh/.bat    # Run scripts
├── filter_cache.db      # SQLite cache (auto-created)
├── activity.log         # Decision logs (auto-created)
└── requirements.txt     # Python dependencies
```

## 🔧 Dependencies

### Core AI Stack
- **sentence-transformers**: Fast embedding model
- **torch**: PyTorch backend
- **scikit-learn**: Cosine similarity
- **numpy**: Numerical operations

### Proxy Stack  
- **mitmproxy**: HTTPS proxy and interception
- **sqlite3**: Built-in caching database

### Installation
```bash
pip install mitmproxy sentence-transformers torch numpy scikit-learn transformers
```

## 🚨 Troubleshooting

### "Model loading failed"
```bash
# Clear transformer cache
rm -rf ~/.cache/huggingface/
python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"
```

### "Proxy connection refused"
- Check mitmproxy is running: `mitmdump -s proxy_filter.py --listen-port 8080`
- Verify browser proxy settings: `127.0.0.1:8080`
- Check firewall/antivirus blocking port 8080

### "Slow decision times"
- Monitor logs for >50ms decisions
- Check CPU usage during embeddings
- Consider reducing batch size or switching to CPU-optimized model

### "Wrong filtering decisions"
- Adjust `similarity_threshold` in `mission.json`
- Refine mission text to be more specific
- Check logs for similarity scores

## 🎛️ Advanced Usage

### Custom Embedding Models
```python
# In ai_filter.py, replace model initialization:
self.model = SentenceTransformer('all-MiniLM-L6-v2')  # Fast
# self.model = SentenceTransformer('all-mpnet-base-v2')  # Accurate
# self.model = SentenceTransformer('all-distilroberta-v1')  # Balanced
```

### Multiple Missions
```python
# Switch missions dynamically
ai_filter.set_mission("Focus on data science and machine learning")
ai_filter.clear_cache()  # Clear old decisions
```

### Custom Thresholds
```python
# Per-session threshold adjustment
filter_instance = ai_filter.get_ai_filter()
filter_instance.threshold = 0.5  # More restrictive
```

## 📈 Performance Benchmarks

Tested on Intel i7-8565U CPU:

| Operation | Time | Target |
|-----------|------|--------|
| Model Loading | ~2s | Once per session |
| URL Embedding | ~15ms | <20ms |
| Similarity Computation | ~2ms | <5ms |
| Cache Lookup | ~1ms | <5ms |
| **Total Decision** | **~18ms** | **<50ms** |

## 🤝 Contributing

1. **Performance**: Focus on <50ms decision times
2. **Accuracy**: Improve semantic understanding
3. **Features**: Add mission templates, better caching
4. **Testing**: Expand test coverage

## 📄 License

Open source - modify and distribute freely.

---

**Smart Focus, AI-Powered** 🧠✨