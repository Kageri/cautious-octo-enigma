import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

st.set_page_config(page_title="Walker Dashboard", layout="wide")
st.title("Walker Dashboard — Schedule & Walk Details")

# -------------------------
# DEMO WALKER DATA
# -------------------------
if "walker" not in st.session_state:
    st.session_state.walker = {
        "name": "Alice Walker",
        "email": "alice@example.com",
        "phone": "555-9876",
    }

# -------------------------
# DEMO WALK SCHEDULE
# -------------------------
if "walk_schedule" not in st.session_state:
    st.session_state.walk_schedule = [
        {"walker": "Alice Walker", "dog": "Buddy", "owner": "John Doe", "datetime": "2025-11-16 10:00", "notes": "Bring leash"},
        {"walker": "Alice Walker", "dog": "Luna", "owner": "Jane Smith", "datetime": "2025-11-16 12:00", "notes": "Needs water bowl"},
        {"walker": "Alice Walker", "dog": "Charlie", "owner": "Mark Lee", "datetime": "2025-11-17 09:30", "notes": "Friendly dog"},
        {"walker": "Alice Walker", "dog": "Max", "owner": "Anna Brown", "datetime": "2025-11-17 11:00", "notes": ""},
    ]

# -------------------------
# FILTER SCHEDULE FOR WALKER
# -------------------------
walker_schedule = [w for w in st.session_state.walk_schedule if w["walker"] == st.session_state.walker["name"]]
schedule_df = pd.DataFrame(walker_schedule)
schedule_df["datetime"] = pd.to_datetime(schedule_df["datetime"])
schedule_df["Month/Day"] = schedule_df["datetime"].dt.strftime("%m/%d")
schedule_df["Time"] = schedule_df["datetime"].dt.strftime("%I:%M %p")

# -------------------------
# SELECT DAY
# -------------------------
st.subheader("Select a day to view walks")
now = datetime.now()
year = st.number_input("Year", value=now.year, step=1)
month = st.number_input("Month", value=now.month, min_value=1, max_value=12, step=1)

# Get all days with walks for this walker in the selected month
days_with_walks = sorted(schedule_df[
    (schedule_df["datetime"].dt.year == year) &
    (schedule_df["datetime"].dt.month == month)
]["datetime"].dt.day.unique())

if not days_with_walks:
    st.info("No walks scheduled for this month.")
else:
    selected_day = st.selectbox("Choose a day", options=days_with_walks)

    # -------------------------
    # SHOW WALKS FOR THAT DAY
    # -------------------------
    day_walks = schedule_df[
        (schedule_df["datetime"].dt.year == year) &
        (schedule_df["datetime"].dt.month == month) &
        (schedule_df["datetime"].dt.day == selected_day)
    ]

    walk_options = [f"{row['dog']} @ {row['Time']}" for _, row in day_walks.iterrows()]
    selected_walk = st.selectbox("Select a walk to see details", options=walk_options)

    if selected_walk:
        walk_row = day_walks.iloc[walk_options.index(selected_walk)]
        # -------------------------
        # SHOW WALK INFO IN CARD
        # -------------------------
        st.markdown(
            f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background-color: #f9f9f9;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
                width: 300px;
            ">
                <h4 style='margin-bottom:10px;'>Walk Details</h4>
                <p><b>Dog:</b> {walk_row['dog']}</p>
                <p><b>Owner:</b> {walk_row['owner']}</p>
                <p><b>Date/Time:</b> {walk_row['datetime'].strftime('%Y-%m-%d %I:%M %p')}</p>
                <p><b>Notes:</b> {walk_row['notes'] if walk_row['notes'] else 'None'}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

# -------------------------
# BUILD CALENDAR
# -------------------------
st.subheader("Calendar")
cal = calendar.Calendar()
weeks = cal.monthdayscalendar(year, month)
weekdays = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

# Header
st.write(" | ".join(weekdays))

# Calendar buttons
for week in weeks:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")
        else:
            day_walks = schedule_df[
                (schedule_df["datetime"].dt.year == year) &
                (schedule_df["datetime"].dt.month == month) &
                (schedule_df["datetime"].dt.day == day)
            ]
            label = f"{day} ({len(day_walks)})" if not day_walks.empty else str(day)
            if cols[i].button(label, key=f"day_{day}"):
                st.session_state.selected_day = day
