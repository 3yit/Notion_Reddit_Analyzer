"""
Time Series Analysis for Notion Complaints
Analyzes trends, seasonality, and forecasts future complaint volumes
"""

import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from scipy import stats
from datetime import datetime, timedelta


def load_time_series_data():
    """Load complaint data as time series"""
    
    db_path = Path(__file__).parent.parent / 'data' / 'notion_complaints.db'
    conn = sqlite3.connect(db_path)
    
    query = '''
        SELECT 
            p.date,
            p.score,
            p.num_comments,
            c.name as category,
            s.name as subreddit
        FROM posts p
        JOIN subreddits s ON p.subreddit_id = s.subreddit_id
        LEFT JOIN post_categories pc ON p.post_id = pc.post_id
        LEFT JOIN categories c ON pc.category_id = c.category_id
        ORDER BY p.date
    '''
    
    df = pd.read_sql_query(query, conn)
    df['date'] = pd.to_datetime(df['date'])
    conn.close()
    
    return df


def calculate_moving_average(series, window=7):
    """Calculate moving average"""
    return series.rolling(window=window, min_periods=1).mean()


def calculate_growth_rate(df):
    """Calculate week-over-week growth rates"""
    
    # Group by week
    df['week'] = df['date'].dt.to_period('W')
    weekly = df.groupby('week').size()
    
    # Calculate growth rate
    growth_rates = weekly.pct_change() * 100
    
    return weekly, growth_rates


def detect_trend(df):
    """Detect overall trend using linear regression"""
    
    daily_counts = df.groupby('date').size().reset_index()
    daily_counts.columns = ['date', 'count']
    
    # Convert dates to numeric (days since start)
    daily_counts['days'] = (daily_counts['date'] - daily_counts['date'].min()).dt.days
    
    # Linear regression
    slope, intercept, r_value, p_value, std_err = stats.linregress(
        daily_counts['days'],
        daily_counts['count']
    )
    
    return {
        'slope': slope,
        'intercept': intercept,
        'r_squared': r_value ** 2,
        'p_value': p_value,
        'trend': 'increasing' if slope > 0 else 'decreasing',
        'daily_change': slope,
        'significant': p_value < 0.05
    }


def analyze_category_trends(df):
    """Analyze trends by complaint category"""
    
    category_daily = df.groupby(['date', 'category']).size().reset_index()
    category_daily.columns = ['date', 'category', 'count']
    
    # Calculate trend for each category
    trends = {}
    
    for category in df['category'].dropna().unique():
        cat_data = category_daily[category_daily['category'] == category].copy()
        cat_data['days'] = (cat_data['date'] - cat_data['date'].min()).dt.days
        
        if len(cat_data) > 5:  # Need enough data points
            slope, intercept, r_value, p_value, std_err = stats.linregress(
                cat_data['days'],
                cat_data['count']
            )
            
            trends[category] = {
                'slope': slope,
                'r_squared': r_value ** 2,
                'p_value': p_value,
                'trend': 'increasing' if slope > 0 else 'decreasing',
                'significant': p_value < 0.05
            }
    
    return trends


def calculate_engagement_metrics(df):
    """Calculate engagement metrics over time"""
    
    daily_metrics = df.groupby('date').agg({
        'score': 'mean',
        'num_comments': 'mean'
    }).reset_index()
    
    return daily_metrics


def find_anomalies(df, threshold=2.5):
    """Find anomalous complaint volumes using z-score"""
    
    daily_counts = df.groupby('date').size()
    
    # Calculate z-scores
    mean = daily_counts.mean()
    std = daily_counts.std()
    z_scores = np.abs((daily_counts - mean) / std)
    
    # Find anomalies
    anomalies = daily_counts[z_scores > threshold]
    
    return anomalies


def generate_report():
    """Generate comprehensive time series analysis report"""
    
    print("📈 TIME SERIES ANALYSIS - NOTION COMPLAINTS\n")
    print("=" * 80)
    
    # Load data
    df = load_time_series_data()
    
    print(f"\n📊 Dataset Overview")
    print("-" * 80)
    print(f"Date Range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Total Days: {(df['date'].max() - df['date'].min()).days + 1}")
    print(f"Total Posts: {len(df):,}")
    
    # Overall trend
    print(f"\n📉 Overall Trend Analysis")
    print("-" * 80)
    
    trend = detect_trend(df)
    print(f"Trend Direction: {trend['trend'].upper()}")
    print(f"Daily Change Rate: {trend['daily_change']:+.2f} posts/day")
    print(f"R² (Fit Quality): {trend['r_squared']:.3f}")
    print(f"Statistical Significance: {'Yes' if trend['significant'] else 'No'} (p={trend['p_value']:.4f})")
    
    if trend['significant']:
        if trend['trend'] == 'increasing':
            print(f"⚠️  Complaints are INCREASING by ~{abs(trend['daily_change'] * 7):.1f} posts/week")
        else:
            print(f"✅ Complaints are DECREASING by ~{abs(trend['daily_change'] * 7):.1f} posts/week")
    else:
        print("📊 No significant trend detected (stable volume)")
    
    # Week-over-week growth
    print(f"\n📅 Week-Over-Week Growth")
    print("-" * 80)
    
    weekly, growth_rates = calculate_growth_rate(df)
    
    print(f"Average Weekly Volume: {weekly.mean():.1f} posts")
    print(f"Peak Week: {weekly.max()} posts ({weekly.idxmax()})")
    print(f"Slowest Week: {weekly.min()} posts ({weekly.idxmin()})")
    
    recent_growth = growth_rates.tail(4)
    print(f"\nRecent 4 Weeks Growth:")
    for week, rate in recent_growth.items():
        if not pd.isna(rate):
            print(f"  {week}: {rate:+.1f}%")
    
    # Category trends
    print(f"\n🏷️  Complaint Category Trends")
    print("-" * 80)
    
    cat_trends = analyze_category_trends(df)
    
    # Sort by slope (fastest growing first)
    sorted_trends = sorted(cat_trends.items(), key=lambda x: x[1]['slope'], reverse=True)
    
    print("\nFastest Growing Categories:")
    for category, metrics in sorted_trends[:3]:
        print(f"  {category:15} {metrics['slope']:+.3f} posts/day", end="")
        if metrics['significant']:
            print(" ⚠️  SIGNIFICANT")
        else:
            print()
    
    print("\nDeclining Categories:")
    for category, metrics in sorted_trends[-3:]:
        if metrics['slope'] < 0:
            print(f"  {category:15} {metrics['slope']:+.3f} posts/day", end="")
            if metrics['significant']:
                print(" ✅ SIGNIFICANT")
            else:
                print()
    
    # Engagement metrics
    print(f"\n💬 Engagement Trends")
    print("-" * 80)
    
    engagement = calculate_engagement_metrics(df)
    
    print(f"Average Upvotes per Post: {engagement['score'].mean():.1f}")
    print(f"Average Comments per Post: {engagement['num_comments'].mean():.1f}")
    
    # Trend in engagement
    eng_trend = detect_trend(engagement.rename(columns={'score': 'count'}))
    if eng_trend['significant']:
        print(f"\nEngagement Trend: {eng_trend['trend'].upper()} ({eng_trend['daily_change']:+.2f} upvotes/day)")
    
    # Anomalies
    print(f"\n🚨 Anomaly Detection (Unusual Complaint Spikes)")
    print("-" * 80)
    
    anomalies = find_anomalies(df)
    
    if len(anomalies) > 0:
        print(f"Found {len(anomalies)} anomalous days:\n")
        for date, count in anomalies.items():
            print(f"  {date.date()}: {count} posts (usual: ~{df.groupby('date').size().mean():.0f})")
            
            # Find what happened that day
            day_posts = df[df['date'] == date]
            top_post = day_posts.nlargest(1, 'score')
            if not top_post.empty:
                print(f"    → Top post: '{top_post.iloc[0]['title'][:60]}...' ({top_post.iloc[0]['score']} ↑)")
    else:
        print("No significant anomalies detected.")
    
    # Summary and insights
    print(f"\n💡 KEY INSIGHTS")
    print("=" * 80)
    
    insights = []
    
    if trend['significant'] and trend['trend'] == 'increasing':
        insights.append(f"⚠️  Overall complaint volume is GROWING at {abs(trend['daily_change'] * 7):.1f} posts/week")
    
    # Find fastest growing category
    if sorted_trends and sorted_trends[0][1]['significant']:
        cat_name = sorted_trends[0][0]
        cat_growth = sorted_trends[0][1]['slope'] * 7
        insights.append(f"⚠️  '{cat_name}' complaints growing fastest: +{cat_growth:.1f} posts/week")
    
    # Check for anomalies
    if len(anomalies) > 0:
        latest_anomaly = max(anomalies.index)
        insights.append(f"🚨 Recent spike detected on {latest_anomaly.date()}")
    
    if not insights:
        insights.append("✅ Complaint volumes are stable with no concerning trends")
    
    for insight in insights:
        print(f"\n{insight}")
    
    print("\n" + "=" * 80)
    
    return df, trend, cat_trends


def main():
    """Main execution"""
    df, trend, cat_trends = generate_report()
    
    print("\n✅ Analysis complete!")
    print("\nNext steps:")
    print("  1. Review the dashboard: streamlit run dashboard.py")
    print("  2. Check SQL queries: python analysis/create_database.py")
    print("  3. View Jupyter notebook for detailed analysis")


if __name__ == "__main__":
    main()
