# Reddit API Setup Guide

## 🎯 Getting Your Reddit API Credentials

To scrape real Reddit posts, you need to register your application with Reddit. It's free and takes ~5 minutes.

### Step 1: Create a Reddit App

1. **Go to Reddit Apps page:** https://www.reddit.com/prefs/apps
2. **Scroll to the bottom** and click **"create another app..."**
3. **Fill in the form:**
   - **name:** `notion-complaint-analyzer` (or any name you like)
   - **App type:** Select **"script"**
   - **description:** `Personal data analysis tool` (optional)
   - **about url:** Leave blank
   - **redirect uri:** `http://localhost:8080` (required but not used for scripts)
4. **Click "create app"**

### Step 2: Get Your Credentials

After creating the app, you'll see:

```
notion-complaint-analyzer          personal use script
[Random string of characters]  <-- This is your CLIENT_ID
...
secret: [Another random string]  <-- This is your CLIENT_SECRET
```

### Step 3: Set Up Environment Variables

1. **Copy the example environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` and add your credentials:**
   ```bash
   REDDIT_CLIENT_ID=your_client_id_from_step_2
   REDDIT_CLIENT_SECRET=your_secret_from_step_2
   REDDIT_USER_AGENT=notion-complaint-analyzer/1.0
   ```

   Example:
   ```bash
   REDDIT_CLIENT_ID=AbCd123EfGh456
   REDDIT_CLIENT_SECRET=XyZ789qWeRtY012uIoP345
   REDDIT_USER_AGENT=notion-complaint-analyzer/1.0
   ```

### Step 4: Install Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate     # On Windows

# Install the Reddit API library
pip install praw
```

### Step 5: Run the Scraper

```bash
cd analysis
python reddit_scraper.py
```

This will:
- ✅ Search Reddit for "notion" posts from the last month
- ✅ Pull full post content (word-by-word)
- ✅ Extract top comments
- ✅ Categorize complaints automatically
- ✅ Generate a markdown report with clickable links
- ✅ Save everything to JSON for further analysis

### Output Files

After running, check the `data/` folder:

- **`reddit_posts_raw.json`** - All posts with full content
- **`reddit_posts_categorized.json`** - Posts organized by complaint type
- **`reddit_analysis_report.md`** - Human-readable report with quotes and links

---

## 🔧 Customization

You can modify the scraper behavior in `reddit_scraper.py`:

```python
# Change search parameters
posts = scraper.scrape_notion_posts(
    search_query="notion",           # Search term
    time_filter="month",             # "hour", "day", "week", "month", "year", "all"
    limit=1000,                      # Max posts to retrieve
    subreddits=['Notion', 'productivity']  # Specific subreddits
)
```

---

## 🚨 Troubleshooting

### Error: "Invalid credentials"
- Double-check your CLIENT_ID and CLIENT_SECRET
- Make sure there are no extra spaces in your `.env` file

### Error: "Received 403 HTTP response"
- Check your USER_AGENT is set correctly
- Make sure you selected "script" app type, not "web app"

### No posts found
- Try a broader search term
- Increase the `limit` parameter
- Check if the subreddits exist and have recent posts

---

## 📊 Reddit API Rate Limits

Reddit allows:
- **60 requests per minute** for script apps
- The scraper automatically respects rate limits
- For large datasets, the script may take several minutes

---

## ✅ Next Steps

Once you have real Reddit data:

1. **Run analysis in Jupyter:**
   ```bash
   jupyter notebook analysis/complaint_analysis.ipynb
   ```

2. **Update the React app** to display real data instead of mock data

3. **Run sentiment analysis** on the actual complaints

4. **Design A/B tests** based on real user feedback

