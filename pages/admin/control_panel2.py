import streamlit as st
import calendar
import pandas as pd
from datetime import datetime

def app():
    st.title("Analytics")
    st.write("Admin analytics page content here.")


st.set_page_config(page_title="Admin Control Panel", layout="wide")

# ---------------------------------------------------------
# ADMIN-ONLY CONTROL PANEL (NO LOGIN)
# ---------------------------------------------------------

st.title("Admin Control Panel")

tabs = st.tabs([
    "Create Admin",
    "Create Client",
    "Create Walker",
    "View All Users",
    "View Dogs",
    "View Schedules"
])

# ------------------------- CREATE ADMIN -------------------------
with tabs[0]:
    st.header("Create Admin")
    admin_email = st.text_input("Admin Email", key="a_email")
    admin_pw = st.text_input("Admin Password", key="a_pw", type="password")
    if st.button("Add Admin", key="add_admin"):
        st.success(f"Created admin: {admin_email}")

# ------------------------- CREATE CLIENT -------------------------
with tabs[1]:
    st.header("Create Client")
    client_name = st.text_input("Client Name", key="c_name")
    client_email = st.text_input("Client Email", key="c_email")
    client_phone = st.text_input("Client Phone", key="c_phone")
    if st.button("Add Client", key="add_client"):
        st.success(f"Created client: {client_name}")

# ------------------------- CREATE WALKER -------------------------
with tabs[2]:
    st.header("Create Walker")
    walker_name = st.text_input("Walker Name", key="w_name")
    walker_email = st.text_input("Walker Email", key="w_email")
    walker_phone = st.text_input("Walker Phone", key="w_phone")
    if st.button("Add Walker", key="add_walker"):
        st.success(f"Created walker: {walker_name}")

# ------------------------- VIEW ALL USERS ------------------------
with tabs[3]:
    st.header("All Users")
    st.table([
        {"name": "Admin One", "email": "admin@example.com", "role": "admin"},
        {"name": "Client One", "email": "client@example.com", "role": "client"},
        {"name": "Walker One", "email": "walker@example.com", "role": "walker"},
    ])

# ------------------------- VIEW DOGS -----------------------------
with tabs[4]:
    st.header("Dogs")
    st.table([
        {"dog": "Buddy", "owner": "Client One", "breed": "Labrador"},
        {"dog": "Luna", "owner": "Client Two", "breed": "Husky"},
    ])

# ------------------------- VIEW SCHEDULES + CALENDAR -------------
with tabs[5]:
    st.header("Walking Schedule")

    st.subheader("Upcoming Walks")
    schedule_data = [
        {"walker": "Walker One", "dog": "Buddy", "datetime": "2025-11-16 10:00"},
        {"walker": "Walker One", "dog": "Luna", "datetime": "2025-11-16 12:00"},
        {"walker": "Walker Two", "dog": "Charlie", "datetime": "2025-11-17 09:30"},
    ]
    schedule_df = pd.DataFrame(schedule_data)
    schedule_df["datetime"] = pd.to_datetime(schedule_df["datetime"])
    schedule_df["Month/Day"] = schedule_df["datetime"].dt.strftime("%m/%d")
    schedule_df["Time"] = schedule_df["datetime"].dt.strftime("%I:%M %p")
    st.table(schedule_df[["walker", "dog", "Month/Day", "Time"]])

    st.subheader("Calendar View")

    # Build calendar table with scheduled walks highlighted
    year = st.number_input("Year", value=datetime.now().year, step=1)
    month = st.number_input("Month", value=datetime.now().month, min_value=1, max_value=12, step=1)

    import calendar
    cal = calendar.monthcalendar(int(year), int(month))
    cal_table = []
    for week in cal:
        week_row = []
        for day in week:
            if day == 0:
                week_row.append("")
            else:
                # Check if any walk exists on this date
                walks = schedule_df[
                    (schedule_df["datetime"].dt.year == year) &
                    (schedule_df["datetime"].dt.month == month) &
                    (schedule_df["datetime"].dt.day == day)
                ]
                if not walks.empty:
                    week_row.append(f"{day} ✅")
                else:
                    week_row.append(str(day))
        cal_table.append(week_row)

    st.table(pd.DataFrame(cal_table, columns=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]))
