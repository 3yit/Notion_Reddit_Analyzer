# Reddit API Setup Guide

## Getting Your Reddit API Credentials

To scrape Reddit posts, register your application with Reddit. Free, takes ~5 minutes.

### Step 1: Create a Reddit App

1. Go to https://www.reddit.com/prefs/apps
2. Scroll down and click "create another app..."
3. Fill in the form:
   - **name:** `notion-complaint-analyzer`
   - **App type:** Select "script"
   - **redirect uri:** `http://localhost:8080`
4. Click "create app"

### Step 2: Get Your Credentials

After creating the app:

```
notion-complaint-analyzer          personal use script
[Random string]  <-- This is your CLIENT_ID
...
secret: [Random string]  <-- This is your CLIENT_SECRET
```

### Step 3: Set Up Environment Variables

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your credentials:
   ```bash
   REDDIT_CLIENT_ID=your_client_id_from_step_2
   REDDIT_CLIENT_SECRET=your_secret_from_step_2
   REDDIT_USER_AGENT=notion-complaint-analyzer/1.0
   ```

### Step 4: Run the Scraper

```bash
./run_scraper.sh
```

Or manually:

```bash
cd analysis
python reddit_scraper.py
```

## Output Files

Check the `data/` folder:

- **reddit_posts_raw.json** - All posts with full content
- **reddit_posts_categorized.json** - Posts organized by category
- **reddit_analysis_report.md** - Report with quotes and links

## Customization

Modify search parameters in `reddit_scraper.py`:

```python
posts = scraper.scrape_notion_posts(
    search_query="notion",
    time_filter="month",  # "hour", "day", "week", "month", "year"
    limit=1000,
    subreddits=['Notion', 'productivity']
)
```

## Troubleshooting

**"Invalid credentials"**
- Double-check your CLIENT_ID and CLIENT_SECRET in `.env`
- Remove any extra spaces

**"Received 403 HTTP response"**
- Verify USER_AGENT is set correctly
- Confirm you selected "script" app type

**No posts found**
- Try a broader search term
- Increase the `limit` parameter

## Rate Limits

Reddit allows 60 requests per minute for script apps. The scraper automatically respects this.

