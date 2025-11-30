import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

def app():
    st.title("Analytics")
    st.write("Admin analytics page content here.")
# --- PAGE CONFIG ---
st.set_page_config(page_title="Dog Walking Logistics Manager", layout="wide")

st.title("🐾 Dog Walking Company Logistics Management System")

# --- SIDEBAR NAVIGATION ---
page = st.sidebar.radio("Navigation", [
    "Dashboard",
    "Clients",
    "Dogs",
    "Walkers",
    "Scheduling",
    "Reports"
])

# --- INITIAL DATA STORE ---
if "clients" not in st.session_state:
    st.session_state.clients = pd.DataFrame(columns=["Client ID", "Name", "Phone", "Email", "Address"])
if "dogs" not in st.session_state:
    st.session_state.dogs = pd.DataFrame(columns=["Dog ID", "Name", "Breed", "Age", "Owner"])
if "walkers" not in st.session_state:
    st.session_state.walkers = pd.DataFrame(columns=["Walker ID", "Name", "Phone", "Availability"])
if "walks" not in st.session_state:
    st.session_state.walks = pd.DataFrame(columns=["Walk ID", "Dog", "Walker", "Client", "Date", "Time", "Status"])

# --- DASHBOARD ---
if page == "Dashboard":
    st.header("📊 Operations Overview")
    total_clients = len(st.session_state.clients)
    total_dogs = len(st.session_state.dogs)
    total_walkers = len(st.session_state.walkers)
    total_walks = len(st.session_state.walks)

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("👥 Clients", total_clients)
    col2.metric("🐕 Dogs", total_dogs)
    col3.metric("🚶 Walkers", total_walkers)
    col4.metric("📅 Scheduled Walks", total_walks)

    st.markdown("---")

    st.subheader("Recent Scheduled Walks")
    if total_walks == 0:
        st.info("No walks scheduled yet.")
    else:
        st.dataframe(st.session_state.walks.tail(10).sort_values("Date", ascending=False))

# --- CLIENT MANAGEMENT ---
elif page == "Clients":
    st.header("👥 Client Management")
    with st.form("add_client_form"):
        st.subheader("Add New Client")
        client_name = st.text_input("Client Name")
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
        address = st.text_input("Address")
        submitted = st.form_submit_button("Add Client")

        if submitted and client_name:
            new_client = pd.DataFrame([{
                "Client ID": len(st.session_state.clients) + 1,
                "Name": client_name,
                "Phone": phone,
                "Email": email,
                "Address": address
            }])
            st.session_state.clients = pd.concat([st.session_state.clients, new_client], ignore_index=True)
            st.success(f"Client '{client_name}' added!")

    st.subheader("All Clients")
    st.dataframe(st.session_state.clients)

# --- DOG MANAGEMENT ---
elif page == "Dogs":
    st.header("🐕 Dog Management")

    if len(st.session_state.clients) == 0:
        st.warning("Add a client before adding a dog.")
    else:
        with st.form("add_dog_form"):
            st.subheader("Add New Dog")
            dog_name = st.text_input("Dog Name")
            breed = st.text_input("Breed")
            age = st.number_input("Age", min_value=0, max_value=30, step=1)
            owner = st.selectbox("Owner", st.session_state.clients["Name"])
            submitted = st.form_submit_button("Add Dog")

            if submitted and dog_name:
                new_dog = pd.DataFrame([{
                    "Dog ID": len(st.session_state.dogs) + 1,
                    "Name": dog_name,
                    "Breed": breed,
                    "Age": age,
                    "Owner": owner
                }])
                st.session_state.dogs = pd.concat([st.session_state.dogs, new_dog], ignore_index=True)
                st.success(f"Dog '{dog_name}' added for owner {owner}!")

    st.subheader("All Dogs")
    st.dataframe(st.session_state.dogs)

# --- WALKER MANAGEMENT ---
elif page == "Walkers":
    st.header("🚶 Walker Management")
    with st.form("add_walker_form"):
        st.subheader("Add New Walker")
        walker_name = st.text_input("Walker Name")
        walker_phone = st.text_input("Phone Number")
        availability = st.multiselect("Availability Days", 
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
        submitted = st.form_submit_button("Add Walker")

        if submitted and walker_name:
            new_walker = pd.DataFrame([{
                "Walker ID": len(st.session_state.walkers) + 1,
                "Name": walker_name,
                "Phone": walker_phone,
                "Availability": ", ".join(availability)
            }])
            st.session_state.walkers = pd.concat([st.session_state.walkers, new_walker], ignore_index=True)
            st.success(f"Walker '{walker_name}' added!")

    st.subheader("All Walkers")
    st.dataframe(st.session_state.walkers)

# --- SCHEDULING WALKS ---
elif page == "Scheduling":
    st.header("📅 Schedule Dog Walks")

    if len(st.session_state.dogs) == 0 or len(st.session_state.walkers) == 0:
        st.warning("Add dogs and walkers before scheduling walks.")
    else:
        with st.form("schedule_walk_form"):
            st.subheader("Create Walk Appointment")
            dog = st.selectbox("Select Dog", st.session_state.dogs["Name"])
            walker = st.selectbox("Assign Walker", st.session_state.walkers["Name"])
            client = st.session_state.dogs.loc[
                st.session_state.dogs["Name"] == dog, "Owner"
            ].values[0]
            date = st.date_input("Date", datetime.now().date())
            time = st.time_input("Time", datetime.now().time())
            status = st.selectbox("Status", ["Scheduled", "Completed", "Cancelled"])
            submitted = st.form_submit_button("Add Walk")

            if submitted:
                new_walk = pd.DataFrame([{
                    "Walk ID": len(st.session_state.walks) + 1,
                    "Dog": dog,
                    "Walker": walker,
                    "Client": client,
                    "Date": date,
                    "Time": time,
                    "Status": status
                }])
                st.session_state.walks = pd.concat([st.session_state.walks, new_walk], ignore_index=True)
                st.success(f"Walk scheduled for {dog} with {walker} on {date} at {time}.")

    st.subheader("Scheduled Walks")
    st.dataframe(st.session_state.walks.sort_values("Date", ascending=False))

# --- REPORTS ---
elif page == "Reports":
    st.header("📈 Reports & Insights")

    total_walks = len(st.session_state.walks)
    completed = len(st.session_state.walks[st.session_state.walks["Status"] == "Completed"])
    cancelled = len(st.session_state.walks[st.session_state.walks["Status"] == "Cancelled"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Walks", total_walks)
    col2.metric("Completed", completed)
    col3.metric("Cancelled", cancelled)

    if total_walks > 0:
        st.subheader("Recent Activity")
        st.dataframe(st.session_state.walks.tail(10))
    else:
        st.info("No walks recorded yet.")
