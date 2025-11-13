"""
Notion Complaint Dashboard
Interactive Streamlit dashboard for monitoring Reddit complaints
"""

import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="Notion Complaint Monitor",
    page_icon="📊",
    layout="wide"
)

@st.cache_resource
def get_db_connection():
    """Get database connection"""
    db_path = Path(__file__).parent.parent / 'data' / 'notion_complaints.db'
    return sqlite3.connect(db_path, check_same_thread=False)

@st.cache_data
def load_data():
    """Load data from database"""
    conn = get_db_connection()
    
    # Load posts with category and subreddit info
    query = '''
        SELECT 
            p.post_id,
            p.title,
            p.author,
            p.score,
            p.num_comments,
            p.date,
            p.selftext,
            p.url,
            s.name as subreddit,
            c.name as category
        FROM posts p
        JOIN subreddits s ON p.subreddit_id = s.subreddit_id
        LEFT JOIN post_categories pc ON p.post_id = pc.post_id
        LEFT JOIN categories c ON pc.category_id = c.category_id
    '''
    
    df = pd.read_sql_query(query, conn)
    df['date'] = pd.to_datetime(df['date'])
    
    return df

def main():
    st.title("📊 Notion Reddit Complaint Monitor")
    st.markdown("Real-time analysis of user feedback from Reddit")
    
    # Load data
    df = load_data()
    
    # Sidebar filters
    st.sidebar.header("Filters")
    
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    # Subreddit filter
    subreddits = ['All'] + sorted(df['subreddit'].unique().tolist())
    selected_subreddit = st.sidebar.selectbox("Subreddit", subreddits)
    
    # Category filter
    categories = ['All'] + sorted(df['category'].dropna().unique().tolist())
    selected_category = st.sidebar.selectbox("Category", categories)
    
    # Apply filters
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= date_range[0]) &
            (filtered_df['date'].dt.date <= date_range[1])
        ]
    
    if selected_subreddit != 'All':
        filtered_df = filtered_df[filtered_df['subreddit'] == selected_subreddit]
    
    if selected_category != 'All':
        filtered_df = filtered_df[filtered_df['category'] == selected_category]
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Posts",
            f"{len(filtered_df):,}",
            delta=f"{len(filtered_df) - len(df)}" if selected_subreddit != 'All' or selected_category != 'All' else None
        )
    
    with col2:
        avg_score = filtered_df['score'].mean()
        st.metric(
            "Avg Upvotes",
            f"{avg_score:.0f}",
        )
    
    with col3:
        total_engagement = filtered_df['num_comments'].sum()
        st.metric(
            "Total Comments",
            f"{total_engagement:,}"
        )
    
    with col4:
        top_post_score = filtered_df['score'].max()
        st.metric(
            "Top Post Score",
            f"{top_post_score:,}"
        )
    
    # Row 1: Category breakdown and trend over time
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Complaints by Category")
        
        category_counts = filtered_df['category'].value_counts().reset_index()
        category_counts.columns = ['Category', 'Count']
        
        fig = px.pie(
            category_counts,
            values='Count',
            names='Category',
            title='Distribution of Complaint Types',
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Complaints Over Time")
        
        # Group by date
        daily_counts = filtered_df.groupby(filtered_df['date'].dt.date).size().reset_index()
        daily_counts.columns = ['Date', 'Posts']
        
        fig = px.line(
            daily_counts,
            x='Date',
            y='Posts',
            title='Daily Complaint Volume',
            markers=True
        )
        fig.update_layout(xaxis_title="Date", yaxis_title="Number of Posts")
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 2: Top posts and subreddit breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Top Posts by Engagement")
        
        top_posts = filtered_df.nlargest(10, 'score')[['title', 'score', 'num_comments', 'subreddit']]
        
        for idx, row in top_posts.iterrows():
            with st.expander(f"⬆️ {row['score']:,} | {row['title'][:60]}..."):
                st.markdown(f"**Subreddit:** r/{row['subreddit']}")
                st.markdown(f"**Comments:** {row['num_comments']}")
                st.markdown(f"**Link:** {filtered_df[filtered_df['title'] == row['title']]['url'].iloc[0]}")
    
    with col2:
        st.subheader("Posts by Subreddit")
        
        subreddit_counts = filtered_df.groupby('subreddit').agg({
            'post_id': 'count',
            'score': 'mean',
            'num_comments': 'sum'
        }).reset_index()
        subreddit_counts.columns = ['Subreddit', 'Posts', 'Avg Score', 'Total Comments']
        
        fig = px.bar(
            subreddit_counts,
            x='Subreddit',
            y='Posts',
            title='Post Volume by Subreddit',
            text='Posts'
        )
        fig.update_traces(texttemplate='%{text}', textposition='outside')
        st.plotly_chart(fig, use_container_width=True)
    
    # Row 3: Category trends and engagement heatmap
    st.subheader("Category Trends Over Time")
    
    # Pivot data for stacked area chart
    category_daily = filtered_df.groupby([filtered_df['date'].dt.date, 'category']).size().reset_index()
    category_daily.columns = ['Date', 'Category', 'Count']
    
    fig = px.area(
        category_daily,
        x='Date',
        y='Count',
        color='Category',
        title='Complaint Categories Over Time (Stacked)'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Most recent high-impact posts
    st.subheader("Recent High-Impact Posts (Score > 100)")
    
    recent_high_impact = filtered_df[filtered_df['score'] > 100].nlargest(5, 'date')
    
    if len(recent_high_impact) > 0:
        for idx, row in recent_high_impact.iterrows():
            st.markdown(f"""
            **[{row['score']:,} ↑] {row['title']}**  
            *r/{row['subreddit']} • {row['date'].strftime('%Y-%m-%d')} • {row['num_comments']} comments*  
            Category: `{row['category']}`  
            [View on Reddit]({row['url']})
            """)
            st.markdown("---")
    else:
        st.info("No high-impact posts in selected filters")
    
    # Data table
    with st.expander("📋 View All Posts (Table)"):
        display_df = filtered_df[['date', 'title', 'subreddit', 'category', 'score', 'num_comments']].copy()
        display_df['date'] = display_df['date'].dt.strftime('%Y-%m-%d')
        display_df = display_df.sort_values('score', ascending=False)
        
        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **Data Source:** Reddit API via PRAW  
    **Last Updated:** November 10, 2025  
    **Total Dataset:** 323 Notion-relevant posts (93.1% of 347 scraped)  
    **Note:** Generic productivity posts filtered out using relevance criteria  
    """)


if __name__ == "__main__":
    main()
