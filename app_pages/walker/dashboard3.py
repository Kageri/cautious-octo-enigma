import streamlit as st
import pandas as pd
from datetime import datetime
from streamlit_calendar import calendar

import sys, os

BASE = os.path.dirname(os.path.abspath(__file__))
if BASE not in sys.path:
    sys.path.insert(0, BASE)


# ---------------------------------------------------
# MAIN WALKER APP
# ---------------------------------------------------
def app():
    st.set_page_config(page_title="Walker Dashboard", layout="wide")
    st.title("Walker Dashboard — Schedule & Walk Actions")

    # -------------------------
    # DEMO WALKER DATA
    # -------------------------
    if "walker" not in st.session_state:
        st.session_state.walker = {
            "name": "Alice Walker",
            "email": "alice@example.com",
            "phone": "555-9876",
        }

    walker_name = st.session_state.walker["name"]

    # -------------------------
    # DEMO WALK SCHEDULE
    # -------------------------
    if "walk_schedule" not in st.session_state:
        st.session_state.walk_schedule = [
            {"walker": "Alice Walker", "dog": "Buddy", "owner": "John Doe", "owner_phone": "555-1111", "datetime": "2025-11-16 10:00", "notes": "Bring leash"},
            {"walker": "Alice Walker", "dog": "Luna", "owner": "Jane Smith", "owner_phone": "555-2222", "datetime": "2025-11-16 12:00", "notes": "Needs water bowl"},
            {"walker": "Alice Walker", "dog": "Charlie", "owner": "Mark Lee", "owner_phone": "555-3333", "datetime": "2025-11-17 09:30", "notes": "Friendly dog"},
            {"walker": "Alice Walker", "dog": "Max", "owner": "Anna Brown", "owner_phone": "555-4444", "datetime": "2025-11-17 11:00", "notes": ""},
        ]

    # Filter schedule
    walker_events = [
        event for event in st.session_state.walk_schedule
        if event["walker"] == walker_name
    ]

    schedule_df = pd.DataFrame(walker_events)
    schedule_df["datetime"] = pd.to_datetime(schedule_df["datetime"])
    schedule_df["Time"] = schedule_df["datetime"].dt.strftime("%I:%M %p")

    # ---------------------------------------------------
    # BUILD FULLCALENDAR EVENTS (Correct format)
    # ---------------------------------------------------
    fc_events = []
    for _, row in schedule_df.iterrows():
        fc_events.append({
            "id": f"{row['dog']}_{row['datetime']}",
            "title": f"{row['dog']} @ {row['Time']}",
            "start": row["datetime"].strftime("%Y-%m-%dT%H:%M"),
            "extendedProps": {
                "dog": row["dog"],
                "owner": row["owner"],
                "owner_phone": row["owner_phone"],
                "notes": row["notes"],
                "time": row["Time"],
            }
        })

    # ---------------------------------------------------
    # CALENDAR VIEW
    # ---------------------------------------------------
    st.subheader("Your Walking Schedule")

    calendar_options = {
        "initialView": "dayGridMonth",
        "height": 700,
        "events": fc_events,
        "eventClick": {
            "callback": "function(info) { return info.event.toPlainObject(); }",
            "name": "selected_event",
        },
        "headerToolbar": {
            "left": "prev,next today",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay"
        }
    }

    event_result = calendar(calendar_options)

    # ---------------------------------------------------
    # WHEN USER CLICKS AN EVENT (Consistent and safe)
    # ---------------------------------------------------
    ev = None

    if event_result and "selected_event" in event_result:
        ev = event_result["selected_event"]
        st.session_state.selected_walk = ev  # persistent selection

    elif "selected_walk" in st.session_state:
        ev = st.session_state.selected_walk

    # Render only if an event is selected
    if ev:
        dog = ev["extendedProps"]["dog"]
        owner = ev["extendedProps"]["owner"]
        owner_phone = ev["extendedProps"]["owner_phone"]
        notes = ev["extendedProps"]["notes"]
        start = ev["start"]

        st.markdown("---")
        st.subheader(f"Walk Details — {dog}")

        # -------------------------
        # CARD UI (guaranteed to show)
        # -------------------------
        st.markdown(
            f"""
            <div style="
                border: 1px solid #ddd;
                border-radius: 10px;
                padding: 15px;
                margin: 10px 0;
                background-color: #ffffff;
                box-shadow: 0 4px 12px rgba(0,0,0,0.08);
                width: 380px;
            ">
                <h4 style='margin-bottom:10px;'>Walk Details</h4>
                <p><b>Dog:</b> {dog}</p>
                <p><b>Owner:</b> {owner}</p>
                <p><b>Date/Time:</b> {datetime.fromisoformat(start).strftime('%Y-%m-%d %I:%M %p')}</p>
                <p><b>Notes:</b> {notes if notes else 'None'}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # ---------------------------------------------------
        # ACTION BUTTONS
        # ---------------------------------------------------
        st.subheader("Actions")

        uploaded_video = st.file_uploader(
            f"Upload walk video for {dog}", 
            type=["mp4", "mov", "avi"]
        )

        if uploaded_video:
            st.success(f"Uploaded: {uploaded_video.name}")

        col1, col2 = st.columns(2)

        with col1:
            if st.button(f"Call {owner}"):
                st.info(f"Calling {owner} at {owner_phone}...")

        with col2:
            if st.button(f"Text {owner}"):
                st.info(f"Texting {owner} at {owner_phone}...")

