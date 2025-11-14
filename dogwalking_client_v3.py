import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

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

# --- CLIENT PAGE ---
st.title("🐾 Client Dashboard")

# Select Client
clients = get_table("clients")
if clients.empty:
    st.warning("No clients found. Please contact admin.")
else:
    client_name = st.selectbox("Select Your Profile", clients["name"])
    client_id = clients.loc[clients["name"]==client_name, "client_id"].values[0]

    # --- CLIENT DOGS ---
    dogs = get_table("dogs")
    client_dogs = dogs[dogs["owner_id"] == client_id]
    st.subheader("🐕 My Dogs")
    st.dataframe(client_dogs)

    # Add new dog request
    st.subheader("Request to Add a New Dog")
    with st.form("add_dog_request"):
        name = st.text_input("Dog Name")
        breed = st.text_input("Breed")
        age = st.number_input("Age", 0, 30)
        notes = st.text_area("Special Notes (optional)")
        submitted = st.form_submit_button("Send Request")
        if submitted and name:
            st.success(f"Request to add {name} sent for review.")

    # --- WALK SCHEDULE ---
    walks = get_table("walks")
    client_walks = walks[walks["client_id"] == client_id]

    st.subheader("📅 My Walk Schedule")
    upcoming = client_walks[client_walks["date"] >= datetime.now().date()]
    past = client_walks[client_walks["date"] < datetime.now().date()]

    st.markdown("**Upcoming Walks**")
    if upcoming.empty:
        st.info("No upcoming walks scheduled.")
    else:
        st.dataframe(upcoming.sort_values("date"))

    st.markdown("**Past Walks**")
    if past.empty:
        st.info("No past walks yet.")
    else:
        st.dataframe(past.sort_values("date", ascending=False))

    # Request a new walk
    st.subheader("Request a New Walk")
    if client_dogs.empty:
        st.warning("Add a dog first before requesting a walk.")
    else:
        with st.form("request_walk_form"):
            dog = st.selectbox("Select Dog", client_dogs["name"])
            date = st.date_input("Preferred Date", datetime.now())
            time = st.time_input("Preferred Time", datetime.now().time())
            notes = st.text_area("Notes (optional)")
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
                st.success(f"Walk request submitted for {dog} on {date} at {time}.")
