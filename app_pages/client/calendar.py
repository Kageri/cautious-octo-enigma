import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

def app():
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
    if "schedule" not in st.session_state:
        st.session_state.schedule = [
            {"dog": "Buddy", "datetime": "2025-11-16 10:00"},
            {"dog": "Luna", "datetime": "2025-11-16 12:00"},
            {"dog": "Buddy", "datetime": "2025-11-18 09:30"},
        ]

    # Convert schedule to DataFrame
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
    # CALENDAR VIEW (streamlit-calendar)
    # -------------------------
    st.subheader("Calendar View")

    # Convert schedule into FullCalendar event objects
    events = []
    for _, row in schedule_df.iterrows():
        events.append({
            "title": f"{row['dog']} @ {row['Time']}",
            "start": row["datetime"].strftime("%Y-%m-%dT%H:%M"),
        })

    calendar_options = {
        "initialView": "dayGridMonth",
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        },
        "events": events,
        "height": 650,
    }

    calendar(calendar_options)


