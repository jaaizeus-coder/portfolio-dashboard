#!/bin/bash
# Deploy to GitHub Pages

echo "🚀 Deploying to GitHub Pages..."

# Commit changes
git add index.html
git commit -m "Update dashboard - $(date '+%Y-%m-%d %H:%M')"

# Push to main branch (GitHub Pages source)
git push origin main

echo "✅ Deployed to: https://jaaizeus-coder.github.io/portfolio-dashboard/"
