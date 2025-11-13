"""
Create SQLite database from Reddit posts data
Demonstrates SQL expertise and relational database design
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path


def create_database():
    """Create SQLite database with normalized schema"""
    
    # Connect to database (creates file if doesn't exist)
    db_path = Path(__file__).parent.parent / 'data' / 'notion_complaints.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("📊 Creating database schema...")
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS comments')
    cursor.execute('DROP TABLE IF EXISTS post_categories')
    cursor.execute('DROP TABLE IF EXISTS posts')
    cursor.execute('DROP TABLE IF EXISTS categories')
    cursor.execute('DROP TABLE IF EXISTS subreddits')
    
    # Create subreddits table
    cursor.execute('''
        CREATE TABLE subreddits (
            subreddit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create categories table
    cursor.execute('''
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT
        )
    ''')
    
    # Create posts table
    cursor.execute('''
        CREATE TABLE posts (
            post_id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT,
            subreddit_id INTEGER,
            url TEXT,
            score INTEGER,
            upvote_ratio REAL,
            num_comments INTEGER,
            created_utc INTEGER,
            date TEXT,
            selftext TEXT,
            is_self BOOLEAN,
            link_flair_text TEXT,
            FOREIGN KEY (subreddit_id) REFERENCES subreddits(subreddit_id)
        )
    ''')
    
    # Create post_categories junction table (many-to-many)
    cursor.execute('''
        CREATE TABLE post_categories (
            post_id TEXT,
            category_id INTEGER,
            PRIMARY KEY (post_id, category_id),
            FOREIGN KEY (post_id) REFERENCES posts(post_id),
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )
    ''')
    
    # Create comments table
    cursor.execute('''
        CREATE TABLE comments (
            comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id TEXT,
            author TEXT,
            body TEXT,
            score INTEGER,
            comment_rank INTEGER,
            FOREIGN KEY (post_id) REFERENCES posts(post_id)
        )
    ''')
    
    # Create indexes for common queries
    cursor.execute('CREATE INDEX idx_posts_date ON posts(date)')
    cursor.execute('CREATE INDEX idx_posts_score ON posts(score DESC)')
    cursor.execute('CREATE INDEX idx_posts_subreddit ON posts(subreddit_id)')
    cursor.execute('CREATE INDEX idx_comments_post ON comments(post_id)')
    
    conn.commit()
    print("✅ Database schema created")
    
    return conn, cursor


def populate_categories(cursor):
    """Populate categories table"""
    
    categories = [
        ('performance', 'Performance issues: slow, lag, crash, freeze'),
        ('onboarding', 'Onboarding and learning curve issues'),
        ('mobile', 'Mobile app issues (iOS/Android)'),
        ('collaboration', 'Team collaboration and sharing issues'),
        ('pricing', 'Pricing and subscription concerns'),
        ('features', 'Feature requests and missing functionality'),
        ('sync', 'Syncing and conflict issues'),
        ('offline', 'Offline mode and connectivity issues'),
        ('other', 'Other complaints and feedback')
    ]
    
    cursor.executemany(
        'INSERT INTO categories (name, description) VALUES (?, ?)',
        categories
    )
    
    print(f"✅ Inserted {len(categories)} categories")


def categorize_post(post_text):
    """Categorize a post based on keywords (same logic as scraper)"""
    
    categories_keywords = {
        'performance': ['slow', 'lag', 'crash', 'freeze', 'loading', 'speed', 'performance', 'bug'],
        'onboarding': ['confusing', 'complicated', 'learn', 'tutorial', 'beginner', 'new user', 'getting started'],
        'mobile': ['mobile', 'app', 'iphone', 'android', 'ios', 'tablet', 'phone'],
        'collaboration': ['share', 'collaborate', 'team', 'permission', 'comment', 'notification', 'workspace'],
        'pricing': ['price', 'expensive', 'cost', 'plan', 'subscription', 'free', 'paid', 'tier'],
        'features': ['feature request', 'missing', 'need', 'wish', 'should have', 'add', 'implement'],
        'sync': ['sync', 'syncing', 'synchronize', 'conflict', 'version'],
        'offline': ['offline', 'internet', 'connection', 'network']
    }
    
    text_lower = post_text.lower()
    matched_categories = []
    
    for category, keywords in categories_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            matched_categories.append(category)
    
    if not matched_categories:
        matched_categories.append('other')
    
    return matched_categories


def load_reddit_data(cursor):
    """Load Reddit posts data into database"""
    
    # Load raw posts
    data_path = Path(__file__).parent.parent / 'data' / 'reddit_posts_raw.json'
    
    with open(data_path, 'r', encoding='utf-8') as f:
        posts = json.load(f)
    
    print(f"📥 Loading {len(posts)} posts...")
    
    # Get subreddit IDs (insert if not exists)
    subreddit_map = {}
    unique_subreddits = set(post['subreddit'] for post in posts)
    
    for subreddit in unique_subreddits:
        cursor.execute(
            'INSERT OR IGNORE INTO subreddits (name) VALUES (?)',
            (subreddit,)
        )
        cursor.execute(
            'SELECT subreddit_id FROM subreddits WHERE name = ?',
            (subreddit,)
        )
        subreddit_map[subreddit] = cursor.fetchone()[0]
    
    print(f"✅ Inserted {len(unique_subreddits)} subreddits")
    
    # Get category IDs
    cursor.execute('SELECT category_id, name FROM categories')
    category_map = {name: cat_id for cat_id, name in cursor.fetchall()}
    
    # Insert posts
    posts_inserted = 0
    comments_inserted = 0
    
    for post in posts:
        # Insert post
        cursor.execute('''
            INSERT OR REPLACE INTO posts 
            (post_id, title, author, subreddit_id, url, score, upvote_ratio, 
             num_comments, created_utc, date, selftext, is_self, link_flair_text)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            post['id'],
            post['title'],
            post['author'],
            subreddit_map[post['subreddit']],
            post['url'],
            post['score'],
            post.get('upvote_ratio', 0),
            post['num_comments'],
            post['created_utc'],
            post['date'],
            post.get('selftext', ''),
            post.get('is_self', True),
            post.get('link_flair_text')
        ))
        posts_inserted += 1
        
        # Categorize and link to categories
        post_text = f"{post['title']} {post.get('selftext', '')}"
        matched_categories = categorize_post(post_text)
        
        for category_name in matched_categories:
            category_id = category_map.get(category_name)
            if category_id:
                cursor.execute(
                    'INSERT OR IGNORE INTO post_categories (post_id, category_id) VALUES (?, ?)',
                    (post['id'], category_id)
                )
        
        # Insert comments
        for rank, comment in enumerate(post.get('top_comments', []), start=1):
            cursor.execute('''
                INSERT INTO comments (post_id, author, body, score, comment_rank)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                post['id'],
                comment.get('author', '[deleted]'),
                comment.get('body', ''),
                comment.get('score', 0),
                rank
            ))
            comments_inserted += 1
    
    print(f"✅ Inserted {posts_inserted} posts")
    print(f"✅ Inserted {comments_inserted} comments")


def run_sample_queries(cursor):
    """Run sample SQL queries to demonstrate database capabilities"""
    
    print("\n" + "="*80)
    print("SAMPLE SQL QUERIES")
    print("="*80 + "\n")
    
    # Query 1: Top 10 posts by score
    print("1. Top 10 Posts by Score:")
    print("-" * 80)
    cursor.execute('''
        SELECT p.title, p.score, s.name as subreddit, p.num_comments
        FROM posts p
        JOIN subreddits s ON p.subreddit_id = s.subreddit_id
        ORDER BY p.score DESC
        LIMIT 10
    ''')
    
    for i, (title, score, subreddit, comments) in enumerate(cursor.fetchall(), 1):
        print(f"{i}. [{score:,} ↑] {title[:60]}... (r/{subreddit}, {comments} comments)")
    
    # Query 2: Complaints by category
    print("\n2. Complaints by Category:")
    print("-" * 80)
    cursor.execute('''
        SELECT c.name, COUNT(DISTINCT pc.post_id) as post_count
        FROM categories c
        LEFT JOIN post_categories pc ON c.category_id = pc.category_id
        GROUP BY c.category_id
        ORDER BY post_count DESC
    ''')
    
    for category, count in cursor.fetchall():
        print(f"{category:15} {count:4} posts")
    
    # Query 3: Most active subreddits
    print("\n3. Posts by Subreddit:")
    print("-" * 80)
    cursor.execute('''
        SELECT s.name, COUNT(*) as post_count, AVG(p.score) as avg_score
        FROM subreddits s
        JOIN posts p ON s.subreddit_id = p.subreddit_id
        GROUP BY s.subreddit_id
        ORDER BY post_count DESC
    ''')
    
    for subreddit, count, avg_score in cursor.fetchall():
        print(f"r/{subreddit:20} {count:3} posts (avg score: {avg_score:.1f})")
    
    # Query 4: Mobile complaints with high engagement
    print("\n4. High-Engagement Mobile Complaints (Score > 50):")
    print("-" * 80)
    cursor.execute('''
        SELECT p.title, p.score, p.num_comments
        FROM posts p
        JOIN post_categories pc ON p.post_id = pc.post_id
        JOIN categories c ON pc.category_id = c.category_id
        WHERE c.name = 'mobile' AND p.score > 50
        ORDER BY p.score DESC
        LIMIT 5
    ''')
    
    for title, score, comments in cursor.fetchall():
        print(f"[{score:,} ↑] {title[:70]}... ({comments} comments)")
    
    # Query 5: Posts with most comments
    print("\n5. Most Discussed Posts:")
    print("-" * 80)
    cursor.execute('''
        SELECT p.title, p.num_comments, p.score, s.name
        FROM posts p
        JOIN subreddits s ON p.subreddit_id = s.subreddit_id
        ORDER BY p.num_comments DESC
        LIMIT 5
    ''')
    
    for title, comments, score, subreddit in cursor.fetchall():
        print(f"[{comments} 💬] {title[:60]}... ({score:,} ↑, r/{subreddit})")


def main():
    """Main function to create and populate database"""
    
    print("🗄️  Creating Notion Complaints Database\n")
    
    # Create schema
    conn, cursor = create_database()
    
    # Populate reference tables
    populate_categories(cursor)
    
    # Load Reddit data
    load_reddit_data(cursor)
    
    # Commit all changes
    conn.commit()
    
    # Run sample queries
    run_sample_queries(cursor)
    
    # Database stats
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80 + "\n")
    
    cursor.execute('SELECT COUNT(*) FROM posts')
    print(f"Total posts: {cursor.fetchone()[0]:,}")
    
    cursor.execute('SELECT COUNT(*) FROM comments')
    print(f"Total comments: {cursor.fetchone()[0]:,}")
    
    cursor.execute('SELECT COUNT(*) FROM subreddits')
    print(f"Total subreddits: {cursor.fetchone()[0]}")
    
    cursor.execute('SELECT COUNT(*) FROM categories')
    print(f"Total categories: {cursor.fetchone()[0]}")
    
    # Close connection
    conn.close()
    
    db_path = Path(__file__).parent.parent / 'data' / 'notion_complaints.db'
    print(f"\n✅ Database created: {db_path}")
    print("💾 Size: {:.2f} MB".format(db_path.stat().st_size / 1024 / 1024))


if __name__ == "__main__":
    main()
