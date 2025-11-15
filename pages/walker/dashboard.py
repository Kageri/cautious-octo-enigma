import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

st.set_page_config(page_title="Walker Dashboard", layout="wide")

st.title("Walker Dashboard — Schedule & Availability")

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
# WALK SCHEDULE
# -------------------------
if "walk_schedule" not in st.session_state:
    st.session_state.walk_schedule = [
        {"walker": "Alice Walker", "dog": "Buddy", "owner": "John Doe", "datetime": "2025-11-16 10:00", "notes": "Bring leash"},
        {"walker": "Alice Walker", "dog": "Luna", "owner": "Jane Smith", "datetime": "2025-11-16 12:00", "notes": "Needs water bowl"},
        {"walker": "Alice Walker", "dog": "Charlie", "owner": "Mark Lee", "datetime": "2025-11-17 09:30", "notes": ""},
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
# CLICKED DAY STATE
# -------------------------
if "clicked_day" not in st.session_state:
    st.session_state.clicked_day = None

def set_day(day):
    st.session_state.clicked_day = day

# -------------------------
# CALENDAR VIEW
# -------------------------
st.subheader("Calendar View")
now = datetime.now()
year = st.number_input("Year", value=now.year, step=1)
month = st.number_input("Month", value=now.month, min_value=1, max_value=12, step=1)

cal_matrix = calendar.monthcalendar(year, month)
st.write("Click on a day to see scheduled walks:")

for week in cal_matrix:
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].write("")  # empty
        else:
            walks = schedule_df[
                (schedule_df["datetime"].dt.year == year) &
                (schedule_df["datetime"].dt.month == month) &
                (schedule_df["datetime"].dt.day == day)
            ]
            label = f"{day} ({len(walks)})" if not walks.empty else str(day)
            cols[i].button(label, key=f"day_{day}", on_click=set_day, args=(day,))

# -------------------------
# SHOW WALKS FOR CLICKED DAY
# -------------------------
if st.session_state.clicked_day:
    day = st.session_state.clicked_day
    st.subheader(f"Walks on {month}/{day}/{year}")
    walks = schedule_df[
        (schedule_df["datetime"].dt.year == year) &
        (schedule_df["datetime"].dt.month == month) &
        (schedule_df["datetime"].dt.day == day)
    ]
    if walks.empty:
        st.info("No walks scheduled.")
    else:
        for _, walk in walks.iterrows():
            with st.expander(f"{walk['dog']} @ {walk['Time']}"):
                st.write(f"Owner: {walk['owner']}")
                st.write(f"Dog: {walk['dog']}")
                st.write(f"Notes: {walk['notes'] if walk['notes'] else 'None'}")
