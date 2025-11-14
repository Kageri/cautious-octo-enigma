import streamlit as st
import pandas as pd
from datetime import datetime
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
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
if "must_change_password" not in st.session_state:
    st.session_state.must_change_password = False

# --- Login Form ---
if not st.session_state.logged_in:
    st.title("Dog Walker Login")
    walker_name = st.text_input("Name")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        cursor.execute("SELECT * FROM walkers WHERE name=%s", (walker_name,))
        walker = cursor.fetchone()
        if walker and check_password_hash(walker["password_hash"], password):
            st.session_state.logged_in = True
            st.session_state.walker_id = walker["walker_id"]
            st.session_state.walker_name = walker["name"]
            st.session_state.must_change_password = walker["must_change_password"]
            st.success(f"Logged in as {walker['name']}")
        else:
            st.error("Invalid credentials")
    st.stop()

# --- Force Password Change if First Login ---
if st.session_state.must_change_password:
    st.warning("Please set a new password")
    new_password = st.text_input("New Password", type="password")
    if st.button("Update Password"):
        new_hash = generate_password_hash(new_password)
        cursor.execute("""
            UPDATE walkers 
            SET password_hash=%s, must_change_password=FALSE
            WHERE walker_id=%s
        """, (new_hash, st.session_state.walker_id))
        conn.commit()
        st.session_state.must_change_password = False
        st.success("Password updated! Reload the page to access your dashboard.")
    st.stop()

# --- Dashboard ---
st.title(f"Welcome, {st.session_state.walker_name}")

# --- Fetch Walks for This Walker ---
cursor.execute("""
    SELECT w.walk_id, w.date, w.time, w.status, w.notes, d.name AS dog_name, c.name AS client_name
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

    # Fill missing days for the current month
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

    # --- Upcoming Walks ---
    st.subheader("Upcoming Walks")
    today = datetime.today().date()
    upcoming = df[df["datetime"].dt.date >= today].sort_values("datetime")
    for _, row in upcoming.iterrows():
        with st.expander(f"🐾 {row['dog_name']} with {row['client_name']} on {row['date']} at {row['time']}"):
            st.markdown(f"**Status:** {row['status']}")
            st.markdown(f"**Notes:** {row['notes']}")
            st.markdown(f"**Dog:** {row['dog_name']}")
            st.markdown(f"**Client:** {row['client_name']}")
            st.markdown(f"**Date:** {row['date']}")
            st.markdown(f"**Time:** {row['time']}")

cursor.close()
conn.close()
