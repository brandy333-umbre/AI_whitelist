#!/bin/bash
# Run the RL-driven proxy filter (Linux/Mac version)
echo "Starting RL-driven proxy filter..."
echo "Configure your browser to use proxy: 127.0.0.1:8080"
echo "Press Ctrl+C to stop"
echo ""

# Use the correct RL proxy filter
python -m mitmproxy.tools.dump -s RL/rl_proxy_filter.py --listen-port 8080
