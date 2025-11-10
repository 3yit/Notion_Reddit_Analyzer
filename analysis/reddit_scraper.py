"""
Real Reddit Scraper for Notion Complaint Analyzer
Pulls actual Reddit posts about Notion from the last month
"""

import praw
import json
from datetime import datetime, timedelta
from typing import List, Dict
import os
from dotenv import load_dotenv

load_dotenv()


class RedditScraper:
    """Scrape Reddit posts about Notion"""
    
    def __init__(self):
        """Initialize Reddit API connection"""
        # Reddit API credentials (get from https://www.reddit.com/prefs/apps)
        self.reddit = praw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'notion-complaint-analyzer/1.0')
        )
    
    def scrape_notion_posts(self, 
                           search_query: str = "notion",
                           subreddits: List[str] = None,
                           time_filter: str = "month",
                           limit: int = 1000) -> List[Dict]:
        """
        Scrape Reddit posts about Notion
        
        Parameters:
        -----------
        search_query : str
            Search term (default: "notion")
        subreddits : List[str]
            List of subreddits to search (None = all)
        time_filter : str
            Time period: "hour", "day", "week", "month", "year", "all"
        limit : int
            Maximum number of posts to retrieve
        
        Returns:
        --------
        List[Dict] : List of post data with full content and metadata
        """
        
        if subreddits is None:
            # Expanded subreddit list for larger dataset
            subreddits = ['Notion', 'productivity', 'NotionSo', 'digitalplanner', 
                         'studytips', 'PKM', 'Zettelkasten', 'getdisciplined',
                         'SelfImprovement', 'organization', 'PKMS']
        
        all_posts = []
        
        for subreddit_name in subreddits:
            try:
                print(f"🔍 Searching r/{subreddit_name}...")
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search for posts
                search_results = subreddit.search(
                    query=search_query,
                    time_filter=time_filter,
                    limit=limit,
                    sort='relevance'
                )
                
                for post in search_results:
                    # Calculate post age
                    post_date = datetime.fromtimestamp(post.created_utc)
                    
                    # Skip if older than specified time filter
                    if time_filter == "month":
                        cutoff = datetime.now() - timedelta(days=30)
                        if post_date < cutoff:
                            continue
                    elif time_filter == "year":
                        cutoff = datetime.now() - timedelta(days=365)
                        if post_date < cutoff:
                            continue
                    
                    post_data = {
                        'id': post.id,
                        'title': post.title,
                        'author': str(post.author) if post.author else '[deleted]',
                        'subreddit': subreddit_name,
                        'url': f"https://www.reddit.com{post.permalink}",
                        'score': post.score,
                        'upvote_ratio': post.upvote_ratio,
                        'num_comments': post.num_comments,
                        'created_utc': post.created_utc,
                        'date': post_date.strftime('%Y-%m-%d'),
                        'selftext': post.selftext,  # Full post content (word-by-word)
                        'is_self': post.is_self,
                        'link_flair_text': post.link_flair_text,
                    }
                    
                    # Get top comments for additional context
                    post.comments.replace_more(limit=0)  # Remove "MoreComments" objects
                    top_comments = []
                    
                    for comment in post.comments[:5]:  # Get top 5 comments
                        if hasattr(comment, 'body'):
                            top_comments.append({
                                'author': str(comment.author) if comment.author else '[deleted]',
                                'body': comment.body,
                                'score': comment.score
                            })
                    
                    post_data['top_comments'] = top_comments
                    all_posts.append(post_data)
                
                print(f"   ✅ Found {len([p for p in all_posts if p['subreddit'] == subreddit_name])} posts")
                
            except Exception as e:
                print(f"   ⚠️  Error searching r/{subreddit_name}: {str(e)}")
                continue
        
        # Sort by score (most upvoted first)
        all_posts.sort(key=lambda x: x['score'], reverse=True)
        
        print(f"\n📊 Total posts collected: {len(all_posts)}")
        return all_posts
    
    def categorize_complaints(self, posts: List[Dict]) -> Dict:
        """
        Categorize posts into complaint types
        
        Parameters:
        -----------
        posts : List[Dict]
            List of Reddit posts
        
        Returns:
        --------
        Dict : Structured complaint data
        """
        
        # Keywords for each category
        categories = {
            'performance': ['slow', 'lag', 'crash', 'freeze', 'loading', 'speed', 'performance', 'bug'],
            'onboarding': ['confusing', 'complicated', 'learn', 'tutorial', 'beginner', 'new user', 'getting started'],
            'mobile': ['mobile', 'app', 'iphone', 'android', 'ios', 'tablet', 'phone'],
            'collaboration': ['share', 'collaborate', 'team', 'permission', 'comment', 'notification', 'workspace'],
            'pricing': ['price', 'expensive', 'cost', 'plan', 'subscription', 'free', 'paid', 'tier'],
            'features': ['feature request', 'missing', 'need', 'wish', 'should have', 'add', 'implement'],
            'sync': ['sync', 'syncing', 'synchronize', 'conflict', 'version'],
            'offline': ['offline', 'internet', 'connection', 'network']
        }
        
        categorized_posts = {category: [] for category in categories.keys()}
        categorized_posts['other'] = []
        
        for post in posts:
            # Combine title and body for keyword matching
            text = f"{post['title']} {post['selftext']}".lower()
            
            # Find matching categories
            matched = False
            for category, keywords in categories.items():
                if any(keyword in text for keyword in keywords):
                    categorized_posts[category].append(post)
                    matched = True
                    break  # Assign to first matching category
            
            if not matched:
                categorized_posts['other'].append(post)
        
        # Create summary
        summary = {
            'total_posts': len(posts),
            'by_category': {cat: len(posts_list) for cat, posts_list in categorized_posts.items() if len(posts_list) > 0},
            'date_range': f"{min(post['date'] for post in posts)} to {max(post['date'] for post in posts)}" if posts else "No posts"
        }
        
        return {
            'categorized_posts': categorized_posts,
            'summary': summary
        }
    
    def save_to_json(self, posts: List[Dict], filename: str = 'reddit_posts.json'):
        """Save posts to JSON file"""
        
        output_path = f"../data/{filename}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Saved {len(posts)} posts to {output_path}")
    
    def generate_markdown_report(self, posts: List[Dict], filename: str = 'reddit_analysis.md'):
        """Generate a markdown report with clickable links and full quotes"""
        
        output_path = f"../data/{filename}"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Reddit Notion Complaint Analysis\n\n")
            f.write(f"**Total Posts Analyzed:** {len(posts)}\n\n")
            f.write(f"**Date Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
            
            for i, post in enumerate(posts[:50], 1):  # Top 50 posts
                f.write(f"## {i}. {post['title']}\n\n")
                f.write(f"**🔗 Link:** [{post['url']}]({post['url']})\n\n")
                f.write(f"**👤 Author:** u/{post['author']} | ")
                f.write(f"**📅 Date:** {post['date']} | ")
                f.write(f"**⬆️ Score:** {post['score']} | ")
                f.write(f"**💬 Comments:** {post['num_comments']}\n\n")
                f.write(f"**📍 Subreddit:** r/{post['subreddit']}\n\n")
                
                if post['selftext']:
                    f.write("**📝 Full Post Content:**\n\n")
                    f.write(f"> {post['selftext']}\n\n")
                else:
                    f.write("*[Link post - no text content]*\n\n")
                
                if post['top_comments']:
                    f.write("**💭 Top Comments:**\n\n")
                    for j, comment in enumerate(post['top_comments'][:3], 1):
                        f.write(f"{j}. **u/{comment['author']}** (↑{comment['score']}): {comment['body'][:200]}{'...' if len(comment['body']) > 200 else ''}\n\n")
                
                f.write("---\n\n")
        
        print(f"📄 Generated markdown report: {output_path}")


def main():
    """Main execution"""
    
    print("🚀 Starting Reddit scraper for Notion complaints...\n")
    
    # Initialize scraper
    scraper = RedditScraper()
    
    # Scrape posts - increased limit and expanded time range for larger dataset
    posts = scraper.scrape_notion_posts(
        search_query="notion",
        time_filter="year",  # Changed from "month" to "year" for more posts
        limit=2000  # Increased limit
    )
    
    if not posts:
        print("❌ No posts found. Check your Reddit API credentials.")
        return
    
    # Categorize complaints
    print("\n📊 Categorizing complaints...")
    categorized = scraper.categorize_complaints(posts)
    
    print("\n📈 Category breakdown:")
    for category, count in categorized['summary']['by_category'].items():
        print(f"   • {category}: {count} posts")
    
    # Save raw data
    scraper.save_to_json(posts, 'reddit_posts_raw.json')
    
    # Save categorized data
    scraper.save_to_json(categorized, 'reddit_posts_categorized.json')
    
    # Generate markdown report with full quotes and clickable links
    scraper.generate_markdown_report(posts, 'reddit_analysis_report.md')
    
    print("\n✅ Done! Check the data/ folder for results.")


if __name__ == "__main__":
    main()
