import streamlit as st
import pymongo
import pandas as pd
import time
import altair as alt

# Config
MONGO_URI = "mongodb://admin:password@localhost:27017/"
DB_NAME = "movie_db"
COLLECTION_NAME = "live_ratings"

@st.cache_resource
def init_connection():
    return pymongo.MongoClient(MONGO_URI)

client = init_connection()
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

st.set_page_config(page_title="Movie Data Real-Time Dashboard", layout="wide")

st.title("🎬 Movie Big Data System - Real-Time Dashboard")

# Layout
col1, col2 = st.columns(2)

with col1:
    st.header("Recent Ratings (Streaming)")
    placeholder = st.empty()

with col2:
    st.header("Top Rated Movies (Live Aggregation)")
    stats_placeholder = st.empty()

# Simulation Loop
# Layout - Top Metrics
st.markdown("### 📊 Real-Time Metrics")
m1, m2, m3, m4 = st.columns(4)

# Placeholders for metrics
metric_total_movies = m1.empty()
metric_avg_rating = m2.empty()
metric_top_genre = m3.empty()
metric_last_update = m4.empty()

# Layout - Main Charts
col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📈 Rating Trends & Distribution")
    chart_placeholder = st.empty()

with col2:
    st.markdown("### 📝 Live Feed")
    feed_placeholder = st.empty()

# Simulation Loop
while True:
    # Fetch all data for aggregation
    data = list(collection.find())
    
    if data:
        df = pd.DataFrame(data)
        if '_id' in df.columns:
            df = df.drop(columns=['_id'])
        
        # 1. Update Metrics
        total_movies = len(df)
        avg_rating = df['rating'].mean()
        top_genre = "N/A"
        # Handle genre list or string safely
        if 'genre' in df.columns:
            # Flatten list of genres if list, or just count if string
            all_genres = []
            for g in df['genre'].dropna():
                if isinstance(g, list): all_genres.extend(g)
                else: all_genres.append(g)
            if all_genres:
                top_genre = pd.Series(all_genres).mode()[0]

        metric_total_movies.metric("Total Events", total_movies)
        metric_avg_rating.metric("Avg Rating", f"{avg_rating:.2f} ⭐")
        metric_top_genre.metric("Top Genre", top_genre)
        metric_last_update.metric("Last Update", time.strftime('%H:%M:%S'))

        # 2. Update Charts (Altair)
        # Bar chart: Average Rating by Genre
        if 'genre' in df.columns:
            # Explode genre list to rows
            df_exploded = df.explode('genre')
            genre_ratings = df_exploded.groupby('genre')['rating'].mean().reset_index()
            
            chart = alt.Chart(genre_ratings).mark_bar().encode(
                x=alt.X('genre', sort='-y', title='Genre'),
                y=alt.Y('rating', title='Average Rating'),
                color=alt.Color('genre', legend=None),
                tooltip=['genre', 'rating']
            ).properties(
                title="Average Rating by Genre",
                height=300
            )
            chart_placeholder.altair_chart(chart, use_container_width=True)

        # 3. Update Live Feed (Table)
        # Show latest 10 items
        latest_df = df.tail(10)[['title', 'network', 'rating', 'timestamp']].sort_values(by='timestamp', ascending=False)
        feed_placeholder.table(latest_df)

    else:
        feed_placeholder.info("Waiting for data...")
    
    time.sleep(1)
