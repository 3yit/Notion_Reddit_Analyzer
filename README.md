# Notion Reddit Analyzer

A data science tool that analyzes Reddit posts to identify product improvement opportunities for Notion. Scrapes real user feedback via Reddit API, categorizes complaints, and designs A/B tests with statistical rigor.

## Overview

**Current Dataset:**
- 347 complaint posts from the past 30 days
- Scraper can be configured for larger datasets (different time ranges, more subreddits)

**Key Findings:**
- Mobile issues: 32.6% of complaints
- Performance issues: 11.8% of complaints
- Designed A/B tests with power analysis and sample size calculations

## Project Structure

```
├── analysis/
│   ├── reddit_scraper.py          # PRAW API scraper
│   ├── complaint_analysis.ipynb   # Jupyter analysis notebook
│   └── statistical_analysis.py    # Statistical utilities
├── data/
│   ├── reddit_posts_raw.json          # 347 posts with full content
│   ├── reddit_posts_categorized.json  # Posts by category
│   └── reddit_analysis_report.md      # Formatted report
├── requirements.txt
├── run_scraper.sh
├── REDDIT_SETUP.md
└── DATA_SUMMARY.md
```

## Setup

### Prerequisites
- Python 3.9+
- Reddit API credentials (free - see REDDIT_SETUP.md)

### Quick Start

```bash
# Clone repository
git clone https://github.com/3yit/Notion_Reddit_Analyzer.git
cd Notion_Reddit_Analyzer

# Set up credentials
cp .env.example .env
# Edit .env with your Reddit API credentials

# Run scraper
./run_scraper.sh
```

### Manual Setup

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run scraper
cd analysis
python reddit_scraper.py
```

## Data Collection

Uses PRAW (Python Reddit API Wrapper) to collect and filter Reddit posts:

**Filtering Logic:**
- Only includes posts **actually about Notion** (not just mentioning it in a list)
- Posts from r/Notion and r/NotionSo are always included
- Posts from other subreddits must have "Notion" in the title OR mention it 3+ times
- Filters out generic productivity posts that briefly mention Notion alongside 10 other tools

**Data collected:**
- Full post content (word-for-word)
- Metadata (score, comments, date)
- Top 5 comments per post
- Clickable links to original posts

**Subreddits searched:**
r/Notion, r/productivity, r/studytips, r/digitalplanner, r/NotionSo, r/PKM

## Analysis Results

### Complaint Distribution

| Category | Count | Percentage |
|----------|-------|------------|
| Mobile | 113 | 32.6% |
| Onboarding | 46 | 13.3% |
| Performance | 41 | 11.8% |
| Pricing | 32 | 9.2% |
| Collaboration | 26 | 7.5% |
| Features | 23 | 6.6% |

### A/B Test Designs

For top complaints, designed experiments with:
- Hypothesis statements
- Sample size calculations (80% power, 5% significance)
- Success metrics
- Expected impact estimates

See `complaint_analysis.ipynb` for full analysis.

## Methodology

### Data Collection
- **Source**: Reddit API (PRAW)
- **Time Period**: Last 30 days
- **Sample Size**: 347 posts
- **Authentication**: Official Reddit API

### Categorization
- **Method**: Two-stage filtering process
  1. **Relevance Filter**: Removes posts that only mention Notion in passing (e.g., "I use Notion, Todoist, and 10 other apps")
  2. **Keyword Classification**: Categorizes relevant posts into complaint types
- **Categories**: Performance, mobile, onboarding, pricing, collaboration, features
- **Validation**: Manual review of sample posts

### Relevance Criteria
A post is considered "about Notion" if it meets any of:
- Posted in r/Notion or r/NotionSo
- Has "Notion" in the title
- Mentions "Notion" 3+ times (indicates substantial discussion)
- Posts mentioning Notion once in a list with other tools are excluded

### Statistical Analysis
- **Frequency Analysis**: Distribution across categories
- **Engagement Metrics**: Upvotes and comments as importance proxies
- **A/B Test Design**: Two-proportion z-test
  - Power: 0.80
  - Significance: α = 0.05
  - Effect sizes from industry benchmarks

### Limitations
- Keyword matching may miss nuanced complaints
- Reddit users may not represent all Notion users (skews toward power users)
- Self-selection bias (users with strong opinions more likely to post)
- Cannot establish causality without experimental data
- Relevance filtering may exclude some edge cases where Notion is discussed indirectly

## Output Files

After running the scraper:

1. **reddit_posts_raw.json** - All 347 posts with complete data
2. **reddit_posts_categorized.json** - Posts organized by type
3. **reddit_analysis_report.md** - Formatted report with top 50 posts

All posts include clickable links to original sources for verification.

## Technologies

- Python 3.9+
- PRAW (Reddit API)
- pandas, scipy
- Jupyter

## Future Enhancements

- Analyze positive feedback alongside complaints to determine if issues affect all users or specific segments
- Real-time complaint tracking dashboard
- Automated weekly reports
- Integration with actual product analytics
- Multi-platform analysis (Twitter, Discord, support tickets)
- Predictive modeling for churn risk
- Causal inference analysis

## Data Quality

- 100% real data from Reddit API
- Full source citations
- Reproducible analysis
- Official API with authentication

## License

MIT

---

**Note:** Research project using publicly available Reddit data. No proprietary Notion data included.
