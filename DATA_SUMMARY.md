# Data Summary

## Dataset Overview

**Date Scraped:** November 10, 2025  
**Time Period:** Last 30 days (October 11 - November 10, 2025)  
**Method:** Reddit API via PRAW

**Raw Data:** 347 posts scraped  
**After Filtering:** 266 Notion-relevant posts (76.7%)  
**Filtered Out:** 81 generic/off-topic posts (23.3%)

**Filtering Criteria:**
- Posts from r/Notion or r/NotionSo (always included)
- "Notion" appears in the title
- "Notion" mentioned 3+ times in post content
- Posts with 1-2 mentions excluded (likely just passing references)

## Dataset Statistics

### Posts Collected
- **Total Posts:** 347
- **Subreddits Searched:** 7
  - r/Notion: 241 posts
  - r/productivity: 66 posts
  - r/digitalplanner: 13 posts
  - r/studytips: 27 posts
  - r/NotionSo: 0 posts
  - r/PKM: 0 posts
  - r/Zettelkasten: 0 posts

### Data Included for Each Post
- Full post title
- Complete post content (word-by-word)
- Author username
- Post URL (clickable link)
- Upvote score
- Upvote ratio
- Number of comments
- Timestamp/date
- Top 5 comments with scores
- Subreddit source

---

## Complaint Categories

Automated categorization using keyword matching:

| Category | Count | Percentage |
|----------|-------|------------|
| **Mobile** | 113 | 32.6% |
| **Onboarding** | 46 | 13.3% |
| **Performance** | 41 | 11.8% |
| **Pricing** | 32 | 9.2% |
| **Collaboration** | 26 | 7.5% |
| **Features** | 23 | 6.6% |
| **Other** | 60 | 17.3% |
| **Sync** | 4 | 1.2% |
| **Offline** | 2 | 0.6% |

## Top Posts by Engagement

**Most Upvoted:**  
"NOTION WILL BAN YOUR ACCOUNT FOR NO REASON AND KEEP YOUR DATA"  
2,926 upvotes | 682 comments  
https://www.reddit.com/r/Notion/comments/1odxw00/

## Output Files

1. **reddit_posts_raw.json** - All 347 scraped posts (before filtering)
2. **reddit_posts_categorized.json** - 266 Notion-relevant posts organized by category
3. **reddit_analysis_report.md** - Formatted report with top 50 posts
4. **notion_complaints.db** - SQLite database (0.73 MB, 266 posts)

## Data Quality

- 100% real data from Reddit API
- Full source citations with clickable URLs
- Relevance filtering removes generic productivity posts
- Verifiable and reproducible
- No synthetic or mock data

## Updating the Dataset

```bash
./run_scraper.sh
```

Or manually:

```bash
cd analysis
python reddit_scraper.py
```
