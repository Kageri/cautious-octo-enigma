import streamlit as st
import pandas as pd
import numpy as np
import datetime as dt

# -------------------------------
# Page setup
# -------------------------------
st.set_page_config(page_title="Dog Walking Analytics", page_icon="🐾", layout="wide")

st.title("🐾 Dog Walking App Analytics Dashboard")
st.markdown("Monitor performance, client activity, and walker stats in real time.")

# -------------------------------
# Mock data generation
# -------------------------------
np.random.seed(42)
dates = pd.date_range(dt.date.today() - dt.timedelta(days=30), periods=30)
walkers = ["Alice", "Ben", "Clara", "Diego", "Ella"]
clients = ["John", "Sophie", "Mike", "Laura", "Nina", "Oscar"]

data = []
for date in dates:
    for walker in walkers:
        walks_today = np.random.randint(0, 5)
        for _ in range(walks_today):
            client = np.random.choice(clients)
            duration = np.random.choice([15, 30, 45, 60])
            data.append({
                "date": date,
                "walker": walker,
                "client": client,
                "duration_mins": duration
            })

df = pd.DataFrame(data)

# -------------------------------
# KPIs
# -------------------------------
total_dogs_walked = len(df)
unique_clients = df["client"].nunique()
total_walkers = df["walker"].nunique()
avg_duration = df["duration_mins"].mean()

col1, col2, col3, col4 = st.columns(4)
col1.metric("🐕 Total Walks", f"{total_dogs_walked}")
col2.metric("👥 Active Clients", f"{unique_clients}")
col3.metric("🚶‍♀️ Walkers", f"{total_walkers}")
col4.metric("⏱️ Avg. Duration", f"{avg_duration:.1f} mins")

# -------------------------------
# Charts
# -------------------------------
st.markdown("### 📊 Walk Trends Over Time")

walks_per_day = df.groupby("date").size().reset_index(name="walk_count")
st.line_chart(walks_per_day, x="date", y="walk_count")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🦮 Walks per Walker")
    walks_per_walker = df["walker"].value_counts()
    st.bar_chart(walks_per_walker)

with col2:
    st.markdown("### 🐾 Top Clients by Walks")
    top_clients = df["client"].value_counts()
    st.bar_chart(top_clients)

# -------------------------------
# Detailed Table
# -------------------------------
st.markdown("### 📋 Recent Walks")
st.dataframe(df.tail(20))

# -------------------------------
# Filters
# -------------------------------
st.sidebar.header("Filters")
selected_walker = st.sidebar.selectbox("Select Walker", ["All"] + walkers)
selected_client = st.sidebar.selectbox("Select Client", ["All"] + clients)

filtered_df = df.copy()
if selected_walker != "All":
    filtered_df = filtered_df[filtered_df["walker"] == selected_walker]
if selected_client != "All":
    filtered_df = filtered_df[filtered_df["client"] == selected_client]

st.sidebar.write(f"Total Walks: {len(filtered_df)}")
st.sidebar.write(f"Average Duration: {filtered_df['duration_mins'].mean():.1f} mins")

