#!/bin/bash

# Quick Start Script for Reddit Scraping

echo "🚀 Notion Complaint Analyzer - Reddit Scraper"
echo "=============================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found!"
    echo ""
    echo "📝 Setting up .env file..."
    cp .env.example .env
    echo "✅ Created .env file from template"
    echo ""
    echo "🔑 Please edit .env and add your Reddit API credentials:"
    echo "   1. Go to https://www.reddit.com/prefs/apps"
    echo "   2. Create a 'script' app"
    echo "   3. Copy CLIENT_ID and CLIENT_SECRET to .env"
    echo ""
    echo "Then run this script again!"
    exit 1
fi

# Check if venv exists
if [ ! -d "venv" ] && [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    source venv/bin/activate
fi

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Run the scraper
echo ""
echo "🔍 Starting Reddit scraper..."
echo "   • Searching for 'notion' posts from the last month"
echo "   • Pulling full content and comments"
echo "   • Generating reports with clickable links"
echo ""

cd analysis
python reddit_scraper.py

echo ""
echo "✅ Done! Check the data/ folder for results:"
echo "   • reddit_posts_raw.json - All scraped posts"
echo "   • reddit_posts_categorized.json - Posts by category"
echo "   • reddit_analysis_report.md - Formatted report"
