import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px

st.set_page_config(page_title="Dogwalker Dashboard", layout="wide")
st.title("Dogwalker Dashboard - Calendar & Schedule")

# --- Example Data ---
data = [
    {"dog_name": "Rex", "walker_name": "Alice", "client_name": "John", "date": "2025-11-12", "time": "09:00", "notes": "Bring water bowl"},
    {"dog_name": "Buddy", "walker_name": "Bob", "client_name": "Sarah", "date": "2025-11-12", "time": "11:00", "notes": "Pick up from front door"},
    {"dog_name": "Luna", "walker_name": "Alice", "client_name": "Mike", "date": "2025-11-13", "time": "14:00", "notes": "Avoid park due to construction"},
    {"dog_name": "Max", "walker_name": "Charlie", "client_name": "Anna", "date": "2025-11-14", "time": "16:00", "notes": "Bring leash and snacks"},
    {"dog_name": "Bella", "walker_name": "Alice", "client_name": "Tom", "date": "2025-11-15", "time": "10:00", "notes": "Check for allergies"},
]

df = pd.DataFrame(data)
df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
df["day"] = df["datetime"].dt.date

# --- Sidebar Filter ---
walker_filter = st.sidebar.selectbox("Select Walker", ["All"] + df["walker_name"].unique().tolist())
if walker_filter != "All":
    df = df[df["walker_name"] == walker_filter]

# --- Calendar Heatmap ---
st.subheader("Monthly Calendar View")
calendar_data = df.groupby(["day", "walker_name"]).size().reset_index(name="walk_count")

month_start = datetime.today().replace(day=1).date()
month_end = (month_start + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()
all_days = pd.date_range(month_start, month_end, freq="D").date
walkers = df["walker_name"].unique()
full_index = pd.MultiIndex.from_product([all_days, walkers], names=["day", "walker_name"])
calendar_full = calendar_data.set_index(["day","walker_name"]).reindex(full_index, fill_value=0).reset_index()

fig = px.imshow(
    calendar_full.pivot(index="walker_name", columns="day", values="walk_count"),
    text_auto=True,
    aspect="auto",
    labels=dict(x="Date", y="Walker", color="Number of Walks"),
    color_continuous_scale="Blues"
)
st.plotly_chart(fig, use_container_width=True)

# --- Table View ---
st.subheader("Scheduled Walks")
st.dataframe(df[["date","time","dog_name","client_name","walker_name","notes"]])

# --- Upcoming Walks with Clickable Popups ---
today = datetime.today().date()
upcoming = df[df["datetime"].dt.date >= today].sort_values("datetime")
st.subheader("Upcoming Walks")

for i, row in upcoming.iterrows():
    with st.expander(f"🐾 {row['dog_name']} with {row['walker_name']} on {row['date']} at {row['time']}"):
        st.markdown(f"**Client:** {row['client_name']}")
        st.markdown(f"**Date:** {row['date']}")
        st.markdown(f"**Time:** {row['time']}")
        st.markdown(f"**Walker:** {row['walker_name']}")
        st.markdown(f"**Notes:** {row['notes']}")
