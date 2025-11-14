import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Dog Walking Client Dashboard", layout="wide")

st.title("🐶 Client Dashboard – Dog Walking Company")

# --- INITIAL DATA STORE ---
if "clients" not in st.session_state:
    st.session_state.clients = pd.DataFrame(columns=["Client ID", "Name", "Phone", "Email", "Address"])
if "dogs" not in st.session_state:
    st.session_state.dogs = pd.DataFrame(columns=["Dog ID", "Name", "Breed", "Age", "Owner"])
if "walks" not in st.session_state:
    st.session_state.walks = pd.DataFrame(columns=["Walk ID", "Dog", "Walker", "Client", "Date", "Time", "Status", "Notes"])

# --- SIDEBAR NAVIGATION ---
st.sidebar.header("🔍 Navigation")
page = st.sidebar.radio("Go to", [
    "Overview",
    "My Dogs",
    "Walk Schedule",
    "Progress & History",
    "Feedback"
])

# --- CLIENT SELECTION ---
if len(st.session_state.clients) == 0:
    st.warning("No clients found. Please have the admin add clients first.")
else:
    client_name = st.sidebar.selectbox("Select Your Profile", st.session_state.clients["Name"])
    client_dogs = st.session_state.dogs[st.session_state.dogs["Owner"] == client_name]
    client_walks = st.session_state.walks[st.session_state.walks["Client"] == client_name]

# --- OVERVIEW PAGE ---
if page == "Overview":
    st.header(f"👋 Welcome back, {client_name}!")

    num_dogs = len(client_dogs)
    num_walks = len(client_walks)
    completed = len(client_walks[client_walks["Status"] == "Completed"])
    cancelled = len(client_walks[client_walks["Status"] == "Cancelled"])

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🐕 Your Dogs", num_dogs)
    col2.metric("📅 Total Walks", num_walks)
    col3.metric("✅ Completed Walks", completed)
    col4.metric("❌ Cancelled Walks", cancelled)

    st.markdown("---")

    st.subheader("Recent Scheduled Walks")
    if len(client_walks) == 0:
        st.info("No walks scheduled yet.")
    else:
        st.dataframe(client_walks.sort_values("Date", ascending=False).head(10))

# --- MY DOGS PAGE ---
elif page == "My Dogs":
    st.header("🐾 My Dogs")

    if len(client_dogs) == 0:
        st.info("You don’t have any dogs registered yet. Contact support to add your dog.")
    else:
        st.dataframe(client_dogs)

    st.markdown("---")
    st.subheader("Request to Add a New Dog")
    with st.form("add_dog_request"):
        name = st.text_input("Dog Name")
        breed = st.text_input("Breed")
        age = st.number_input("Age", 0, 30, 1)
        notes = st.text_area("Special Notes (optional)")
        submitted = st.form_submit_button("Send Request")

        if submitted and name:
            st.success(f"Request to add {name} ({breed}, {age} years) sent for review!")

# --- WALK SCHEDULE PAGE ---
elif page == "Walk Schedule":
    st.header("📅 My Walk Schedule")

    upcoming = client_walks[client_walks["Date"] >= datetime.now().date()]
    past = client_walks[client_walks["Date"] < datetime.now().date()]

    st.subheader("Upcoming Walks")
    if len(upcoming) == 0:
        st.info("No upcoming walks scheduled.")
    else:
        st.dataframe(upcoming.sort_values("Date"))

    st.subheader("Past Walks")
    if len(past) == 0:
        st.info("No past walks yet.")
    else:
        st.dataframe(past.sort_values("Date", ascending=False))

    st.markdown("---")
    st.subheader("📝 Request a New Walk")
    if len(client_dogs) == 0:
        st.warning("Add a dog first before scheduling a walk.")
    else:
        with st.form("request_walk_form"):
            dog = st.selectbox("Select Dog", client_dogs["Name"])
            date = st.date_input("Preferred Date", datetime.now().date())
            time = st.time_input("Preferred Time", datetime.now().time())
            notes = st.text_area("Notes (optional, e.g., feeding, route, behavior)")
            submitted = st.form_submit_button("Request Walk")

            if submitted:
                walk_request = pd.DataFrame([{
                    "Walk ID": len(st.session_state.walks) + 1,
                    "Dog": dog,
                    "Walker": "Pending",
                    "Client": client_name,
                    "Date": date,
                    "Time": time,
                    "Status": "Requested",
                    "Notes": notes
                }])
                st.session_state.walks = pd.concat([st.session_state.walks, walk_request], ignore_index=True)
                st.success(f"Walk request submitted for {dog} on {date} at {time}.")

# --- PROGRESS PAGE ---
elif page == "Progress & History":
    st.header("📈 Walk Progress & History")

    completed_walks = client_walks[client_walks["Status"] == "Completed"]

    if len(completed_walks) == 0:
        st.info("No completed walks yet.")
    else:
        st.dataframe(completed_walks.sort_values("Date", ascending=False))

        st.markdown("---")
        st.subheader("Summary Insights")
        total_walks = len(client_walks)
        completion_rate = (len(completed_walks) / total_walks * 100) if total_walks > 0 else 0
        st.metric("✅ Completion Rate", f"{completion_rate:.1f}%")

# --- FEEDBACK PAGE ---
elif page == "Feedback":
    st.header("💬 Give Feedback")

    if len(client_walks) == 0:
        st.info("You can leave feedback after a walk is completed.")
    else:
        past_walks = client_walks[client_walks["Status"] == "Completed"]
        if len(past_walks) == 0:
            st.info("No completed walks to review yet.")
        else:
            with st.form("feedback_form"):
                walk = st.selectbox("Select Walk to Review", past_walks["Walk ID"])
                rating = st.slider("Rating (1 = poor, 5 = excellent)", 1, 5, 5)
                comments = st.text_area("Comments")
                submitted = st.form_submit_button("Submit Feedback")

                if submitted:
                    st.success(f"Feedback submitted for walk #{walk}. Thank you!")
