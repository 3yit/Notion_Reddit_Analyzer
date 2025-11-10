# 📊 Actual Data Summary

## Real Reddit Data Collected

**Date Scraped:** November 10, 2025  
**Time Period:** Last 30 days (October 11 - November 10, 2025)  
**Method:** Reddit API via PRAW (official Python library)

---

## 📈 Dataset Statistics

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

## 🏷️ Complaint Categories

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

---

## 🔝 Top Posts by Engagement

### Most Upvoted Post
**Title:** "NOTION WILL BAN YOUR ACCOUNT FOR NO REASON AND KEEP YOUR DATA"  
**Score:** 2,926 upvotes  
**Comments:** 682  
**Link:** https://www.reddit.com/r/Notion/comments/1odxw00/

### Most Discussed Post
**Title:** Same as above (682 comments)

---

## 📁 Output Files

1. **`reddit_posts_raw.json`**
   - 10,780 lines
   - Full structured data for all 347 posts
   - Includes all metadata, content, and comments

2. **`reddit_posts_categorized.json`**
   - Posts organized by complaint category
   - Summary statistics included

3. **`reddit_analysis_report.md`**
   - 1,776 lines
   - Human-readable report
   - Top 50 posts with full content
   - Clickable links to original posts

---

## ✅ Data Quality

- **100% Real Data** - Scraped from actual Reddit posts
- **Full Citations** - Every post includes original URL
- **Verifiable** - Anyone can click links to verify content
- **Reproducible** - Run `./run_scraper.sh` to get fresh data
- **API-Based** - Uses official Reddit API, not web scraping

---

## 🔄 How to Update

Run the scraper again to get fresh data:

```bash
./run_scraper.sh
```

Or run it manually:

```bash
cd analysis
../.venv/bin/python reddit_scraper.py
```

**Pro Tip:** Run weekly and combine results to build a larger dataset!

---

## 📊 Use This Data For

1. **Resume bullets** - "Analyzed 347 Reddit posts..."
2. **Statistical analysis** - Real frequency distributions
3. **A/B test designs** - Based on actual complaint volumes
4. **Interview discussions** - Cite specific findings
5. **Further research** - Build on this foundation

---

**Last Updated:** November 10, 2025
