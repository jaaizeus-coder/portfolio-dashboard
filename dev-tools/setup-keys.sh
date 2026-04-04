#!/bin/bash
# Development API key setup

echo "🔧 Poseidon Development Setup"
echo "=============================="
echo

echo "1. Finnhub API Key (for stock data)"
echo "   Visit: https://finnhub.io/register"
echo "   Free tier: 60 calls/min"
echo "   Current: sandbox (limited data)"
echo

echo "2. Anthropic API Key (for AI briefs)"
echo "   Visit: https://console.anthropic.com/"
echo "   $5/month for Haiku model"
echo "   Current: disabled"
echo

echo "3. Update keys in index.html:"
echo "   const FINNHUB_KEY = 'your_key_here';"
echo "   const ANTHROPIC_KEY = 'your_key_here';"
echo

echo "4. Local server running at: http://localhost:8080"
echo
