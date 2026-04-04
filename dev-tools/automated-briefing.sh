#!/bin/bash
# Enhanced Automated Briefing with News + Trending Analysis
# This script replaces the old briefing.py with enhanced integration

cd /Users/jaai/.openclaw/workspace/poseidon-dashboard

echo "🔱 Enhanced Poseidon Daily Briefing System"
echo "=========================================="
echo "$(date): Starting enhanced briefing with news + trending..."

# Run enhanced integration and send email
python3 briefing-integration-enhanced.py --email 2>&1

# Check if briefing data was generated
if [ -f "briefing-data.json" ]; then
    echo "✅ Enhanced dashboard data updated: briefing-data.json"
    
    # Get summary from JSON
    TOTAL=$(grep -o '"total_positions": *[0-9]*' briefing-data.json | grep -o '[0-9]*')
    UP=$(grep -o '"positions_up": *[0-9]*' briefing-data.json | grep -o '[0-9]*')
    DOWN=$(grep -o '"positions_down": *[0-9]*' briefing-data.json | grep -o '[0-9]*')
    
    echo "📊 Portfolio: $TOTAL positions, $UP up, $DOWN down"
    echo "🚀 Trending analysis included"
    echo "📰 News links integrated"
else
    echo "❌ Enhanced data generation failed"
fi

echo "$(date): Enhanced briefing automation complete"
echo
