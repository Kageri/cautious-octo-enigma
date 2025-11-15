import streamlit as st
import pandas as pd
from datetime import datetime
import calendar

def app():
    st.title("Analytics")
    st.write("Admin analytics page content here.")
    
st.set_page_config(page_title="Client Dashboard", layout="wide")

st.title("Client Dashboard — Dog Walk Schedule")

# -------------------------
# DEMO CLIENT DATA
# -------------------------
if "client" not in st.session_state:
    st.session_state.client = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-1234",
        "address": "123 Main St",
        "notes": "Loves walks in the park",
    }

if "dogs" not in st.session_state:
    st.session_state.dogs = [
        {"name": "Buddy", "breed": "Labrador", "age": 4},
        {"name": "Luna", "breed": "Husky", "age": 2},
    ]

# -------------------------
# DEMO SCHEDULE DATA
# -------------------------
# Each entry: dog name, scheduled datetime
if "schedule" not in st.session_state:
    st.session_state.schedule = [
        {"dog": "Buddy", "datetime": "2025-11-16 10:00"},
        {"dog": "Luna", "datetime": "2025-11-16 12:00"},
        {"dog": "Buddy", "datetime": "2025-11-18 09:30"},
    ]

# Convert to DataFrame
schedule_df = pd.DataFrame(st.session_state.schedule)
schedule_df["datetime"] = pd.to_datetime(schedule_df["datetime"])
schedule_df["Month/Day"] = schedule_df["datetime"].dt.strftime("%m/%d")
schedule_df["Time"] = schedule_df["datetime"].dt.strftime("%I:%M %p")

# -------------------------
# UPCOMING WALKS TABLE
# -------------------------
st.subheader("Upcoming Walks")
st.table(schedule_df[["dog", "Month/Day", "Time"]])

# -------------------------
# CALENDAR VIEW
# -------------------------
st.subheader("Calendar View")
now = datetime.now()
year = st.number_input("Year", value=now.year, step=1)
month = st.number_input("Month", value=now.month, min_value=1, max_value=12, step=1)

cal_matrix = calendar.monthcalendar(year, month)
cal_table = []

for week in cal_matrix:
    week_row = []
    for day in week:
        if day == 0:
            week_row.append("")
        else:
            # Find all walks on this day
            walks = schedule_df[
                (schedule_df["datetime"].dt.year == year) &
                (schedule_df["datetime"].dt.month == month) &
                (schedule_df["datetime"].dt.day == day)
            ]
            if not walks.empty:
                # show day + all times
                times = "\n".join([f"{row['dog']} @ {row['Time']}" for _, row in walks.iterrows()])
                week_row.append(f"{day}\n{times}")
            else:
                week_row.append(str(day))
    cal_table.append(week_row)

st.table(pd.DataFrame(cal_table, columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]))
