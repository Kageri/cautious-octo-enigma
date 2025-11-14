import streamlit as st
import pandas as pd
import mysql.connector
from werkzeug.security import check_password_hash
from datetime import datetime
import plotly.express as px

# --- Database Connection ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Tsu9tail$13",
    database="dog_walking_company"
)
cursor = conn.cursor(dictionary=True)

# --- Session State for Login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "walker_id" not in st.session_state:
    st.session_state.walker_id = None
if "walker_name" not in st.session_state:
    st.session_state.walker_name = ""

# --- Login Form ---
if not st.session_state.logged_in:
    st.sidebar.title("Walker Login")
    username = st.sidebar.text_input("Name")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        cursor.execute("SELECT * FROM walkers WHERE name=%s", (username,))
        walker = cursor.fetchone()
        if walker and check_password_hash(walker["password_hash"], password):
            st.session_state.logged_in = True
            st.session_state.walker_id = walker["walker_id"]
            st.session_state.walker_name = walker["name"]
            st.success(f"Logged in as {walker['name']}")
        else:
            st.error("Invalid credentials")
    st.stop()

# --- Fetch Walks for This Walker ---
cursor.execute("""
    SELECT w.walk_id, w.date, w.time, w.status, w.notes, d.name as dog_name, c.name as client_name
    FROM walks w
    JOIN dogs d ON w.dog_id = d.dog_id
    JOIN clients c ON w.client_id = c.client_id
    WHERE w.walker_id = %s
    ORDER BY w.date, w.time
""", (st.session_state.walker_id,))
walks = cursor.fetchall()
df = pd.DataFrame(walks)
if df.empty:
    st.info("No scheduled walks for you yet.")
else:
    df["datetime"] = pd.to_datetime(df["date"].astype(str) + " " + df["time"].astype(str))
    df["day"] = df["datetime"].dt.date

    # --- Calendar Heatmap ---
    st.subheader("Monthly Calendar View")
    calendar_data = df.groupby(["day"]).size().reset_index(name="walk_count")

    # Fill missing days for current month
    month_start = datetime.today().replace(day=1).date()
    month_end = (month_start + pd.DateOffset(months=1) - pd.DateOffset(days=1)).date()
    all_days = pd.date_range(month_start, month_end, freq="D").date
    full_index = pd.MultiIndex.from_product([all_days], names=["day"])
    calendar_full = calendar_data.set_index(["day"]).reindex(full_index, fill_value=0).reset_index()

    fig = px.imshow(
        calendar_full.pivot(index=None, columns="day", values="walk_count"),
        text_auto=True,
        aspect="auto",
        labels=dict(x="Date", y="", color="Number of Walks"),
        color_continuous_scale="Blues"
    )
    st.plotly_chart(fig, use_container_width=True)

    # --- Upcoming Walks with Expanders ---
    st.subheader("Upcoming Walks")
    today = datetime.today().date()
    upcoming = df[df["datetime"].dt.date >= today].sort_values("datetime")
    for _, row in upcoming.iterrows():
        with st.expander(f"🐾 {row['dog_name']} with {row['client_name']} on {row['date']} at {row['time']}"):
            st.markdown(f"**Status:** {row['status']}")
            st.markdown(f"**Notes:** {row['notes']}")
