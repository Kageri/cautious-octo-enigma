# ===============================================
# Streamlit + SQL Live Dashboards for Dog Walking
# Admin, Client, and Walker Interfaces
# ===============================================

# 1. Install dependencies
# pip install streamlit sqlalchemy pymysql pandas werkzeug

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

# --- DATABASE CONNECTION ---
DB_USER = "root"
DB_PASSWORD = "Tsu9tail$13"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "dog_walking_company"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# --- UTILITY FUNCTIONS ---
@st.cache_data(ttl=300)
def get_table(table_name: str) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql_table(table_name, conn)

def insert_data(table_name: str, data: dict):
    with engine.connect() as conn:
        pd.DataFrame([data]).to_sql(table_name, conn, if_exists='append', index=False)

def update_data(table_name: str, key_col: str, key_val, updates: dict):
    with engine.connect() as conn:
        set_clause = ", ".join([f"{col}='{val}'" for col, val in updates.items()])
        conn.execute(f"UPDATE {table_name} SET {set_clause} WHERE {key_col}={key_val}")

# --- SIDEBAR: USER TYPE ---
user_type = st.sidebar.radio("I am a:", ["Admin", "Client", "Walker"])

# =========================================
# ADMIN DASHBOARD
# =========================================
if user_type == "Admin":
    st.title("🛠 Admin Dashboard")

    # --- CLIENTS ---
    st.subheader("Clients")
    clients = get_table("clients")
    st.dataframe(clients)

    with st.form("add_client"):
        name = st.text_input("Name")
        phone = st.text_input("Phone")
        email = st.text_input("Email")
        address = st.text_input("Address")
        submitted = st.form_submit_button("Add Client")
        if submitted and name:
            insert_data("clients", {"name": name, "phone": phone, "email": email, "address": address})
            st.success(f"Client '{name}' added.")

    # --- DOGS ---
    st.subheader("Dogs")
    dogs = get_table("dogs")
    st.dataframe(dogs)

    with st.form("add_dog"):
        dog_name = st.text_input("Dog Name")
        breed = st.text_input("Breed")
        age = st.number_input("Age", 0, 30)
        owner = st.selectbox("Owner", clients["name"].tolist() if not clients.empty else [])
        submitted = st.form_submit_button("Add Dog")
        if submitted and dog_name and owner:
            owner_id = clients.loc[clients['name']==owner, 'client_id'].values[0]
            insert_data("dogs", {"name": dog_name, "breed": breed, "age": age, "owner_id": owner_id})
            st.success(f"Dog '{dog_name}' added for {owner}.")

    # --- WALKERS ---
    st.subheader("Walkers")
    walkers = get_table("walkers")
    st.dataframe(walkers)

    with st.form("add_walker"):
        walker_name = st.text_input("Walker Name")
        walker_phone = st.text_input("Phone")
        availability = st.multiselect("Availability", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
        temp_password = st.text_input("Temporary Password")
        submitted = st.form_submit_button("Add Walker")
        if submitted and walker_name and temp_password:
            password_hash = generate_password_hash(temp_password)
            insert_data("walkers", {
                "name": walker_name,
                "phone": walker_phone,
                "availability": ",".join(availability),
                "password_hash": password_hash,
                "must_change_password": True
            })
            st.success(f"Walker '{walker_name}' added with temporary password.")

    # --- WALKS ---
    st.subheader("Scheduled Walks")
    walks = get_table("walks")
    st.dataframe(walks)

# =========================================
# CLIENT DASHBOARD
# =========================================
elif user_type == "Client":
    st.title("🐶 Client Dashboard")

    clients = get_table("clients")
    if clients.empty:
        st.warning("No clients available. Ask admin to add your profile.")
    else:
        client_name = st.selectbox("Select Your Name", clients["name"])
        client_id = clients.loc[clients["name"]==client_name, "client_id"].values[0]

        dogs = get_table("dogs")
        client_dogs = dogs[dogs["owner_id"] == client_id]
        st.subheader("My Dogs")
        st.dataframe(client_dogs)

        walks = get_table("walks")
        my_walks = walks[walks["client_id"] == client_id]
        st.subheader("My Walk Schedule")
        st.dataframe(my_walks)

        st.subheader("Request a Walk")
        with st.form("request_walk"):
            if not client_dogs.empty:
                dog = st.selectbox("Select Dog", client_dogs["name"])
                date = st.date_input("Date", datetime.now())
                time = st.time_input("Time")
                notes = st.text_area("Notes")
                submitted = st.form_submit_button("Request Walk")
                if submitted:
                    dog_id = client_dogs.loc[client_dogs["name"]==dog, "dog_id"].values[0]
                    insert_data("walks", {
                        "dog_id": dog_id,
                        "walker_id": None,
                        "client_id": client_id,
                        "date": date,
                        "time": time,
                        "status": "Requested",
                        "notes": notes
                    })
                    st.success(f"Walk requested for {dog} on {date} at {time}.")

# =========================================
# WALKER DASHBOARD
# =========================================
elif user_type == "Walker":
    st.title("🚶 Walker Login")
    walkers = get_table("walkers")
    walker_name_input = st.text_input("Name")
    password_input = st.text_input("Password", type="password")

    if st.button("Login"):
        walker_row = walkers[walkers["name"] == walker_name_input]
        if not walker_row.empty:
            pw_hash = walker_row.iloc[0]["password_hash"]
            if check_password_hash(pw_hash, password_input):
                walker_id = walker_row.iloc[0]["walker_id"]
                must_change = walker_row.iloc[0].get("must_change_password", False)
                
                # --- Force password reset ---
                if must_change:
                    st.warning("Please set a new password")
                    new_password = st.text_input("New Password", type="password")
                    if st.button("Update Password"):
                        new_hash = generate_password_hash(new_password)
                        update_data("walkers", "walker_id", walker_id, {
                            "password_hash": new_hash,
                            "must_change_password": False
                        })
                        st.success("Password updated! Reload page to access dashboard.")
                    st.stop()

                # --- Dashboard after login ---
                st.success(f"Welcome, {walker_name_input}!")
                walks = get_table("walks")
                my_walks = walks[walks["walker_id"] == walker_id]
                st.subheader("My Walks")
                st.dataframe(my_walks)

                st.subheader("Update Walk Status")
                sched_walks = my_walks[my_walks["status"].isin(["Scheduled","Requested"])]
                if not sched_walks.empty:
                    walk_id = st.selectbox("Select Walk", sched_walks["walk_id"])
                    new_status = st.selectbox("New Status", ["Completed","Cancelled"])
                    notes = st.text_area("Notes")
                    if st.button("Update Status"):
                        update_data("walks", "walk_id", walk_id, {"status": new_status, "notes": notes})
                        st.success(f"Walk #{walk_id} updated to {new_status}.")
            else:
                st.error("Invalid password")
        else:
            st.error("Walker not found")
