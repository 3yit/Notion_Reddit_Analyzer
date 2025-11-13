"""
Test the relevance filter on existing data to see how many posts get filtered out
"""

import json
import sys

def is_notion_relevant(post):
    """
    Check if a post is actually about Notion (not just mentioning it in passing)
    """
    title_lower = post['title'].lower()
    body_lower = post.get('selftext', '').lower()
    combined_text = f"{title_lower} {body_lower}"
    
    # Always include posts from Notion-specific subreddits
    if post['subreddit'] in ['Notion', 'NotionSo']:
        return True
    
    # Include if "notion" is in the title
    if 'notion' in title_lower:
        return True
    
    # Include if "notion" appears 3+ times (means it's a major topic)
    notion_mentions = combined_text.count('notion')
    if notion_mentions >= 3:
        return True
    
    # Exclude posts where Notion is just mentioned in a list
    if notion_mentions <= 2:
        # Check if it's just in a list with other tools
        tool_list_patterns = [
            'notion,', ', notion', 'notion and', 'todoist', 'obsidian',
            'trello', 'evernote', 'onenote', 'clickup', 'asana'
        ]
        if any(pattern in combined_text for pattern in tool_list_patterns):
            # Only include if Notion gets substantial discussion
            if notion_mentions == 1 and len(combined_text) < 500:
                return False
    
    return notion_mentions > 0


def main():
    # Load existing data
    with open('../data/reddit_posts_raw.json', 'r') as f:
        posts = json.load(f)
    
    print(f"📊 Total posts in dataset: {len(posts)}")
    print("\n" + "="*80)
    print("FILTERING ANALYSIS")
    print("="*80 + "\n")
    
    # Test filter
    relevant = []
    filtered_out = []
    
    for post in posts:
        if is_notion_relevant(post):
            relevant.append(post)
        else:
            filtered_out.append(post)
    
    print(f"✅ Posts that ARE about Notion: {len(relevant)} ({len(relevant)/len(posts)*100:.1f}%)")
    print(f"❌ Posts filtered out: {len(filtered_out)} ({len(filtered_out)/len(posts)*100:.1f}%)")
    
    if filtered_out:
        print("\n" + "="*80)
        print("EXAMPLES OF FILTERED OUT POSTS (not actually about Notion)")
        print("="*80 + "\n")
        
        for i, post in enumerate(filtered_out[:10], 1):
            title = post['title']
            subreddit = post['subreddit']
            text_preview = post.get('selftext', '')[:200]
            notion_count = (post['title'] + post.get('selftext', '')).lower().count('notion')
            
            print(f"{i}. 📝 {title}")
            print(f"   📍 r/{subreddit}")
            print(f"   🔢 Mentions 'Notion' {notion_count} time(s)")
            print(f"   📄 Preview: {text_preview[:150]}...")
            print()
    
    print("\n" + "="*80)
    print("BREAKDOWN BY SUBREDDIT")
    print("="*80 + "\n")
    
    from collections import Counter
    
    # Count by subreddit for all posts
    all_subreddits = Counter(p['subreddit'] for p in posts)
    relevant_subreddits = Counter(p['subreddit'] for p in relevant)
    filtered_subreddits = Counter(p['subreddit'] for p in filtered_out)
    
    for subreddit in sorted(all_subreddits.keys()):
        total = all_subreddits[subreddit]
        kept = relevant_subreddits.get(subreddit, 0)
        removed = filtered_subreddits.get(subreddit, 0)
        keep_pct = (kept/total*100) if total > 0 else 0
        
        print(f"r/{subreddit:20} Total: {total:3} | Kept: {kept:3} ({keep_pct:5.1f}%) | Filtered: {removed:3}")


if __name__ == "__main__":
    main()
