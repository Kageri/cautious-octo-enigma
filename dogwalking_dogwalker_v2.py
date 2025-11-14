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

def update_data(table_name: str, key_col: str, key_val, updates: dict):
    with engine.connect() as conn:
        set_clause = ", ".join([f"{col}='{val}'" for col, val in updates.items()])
        conn.execute(f"UPDATE {table_name} SET {set_clause} WHERE {key_col}={key_val}")

# --- WALKER DASHBOARD ---
st.title("🚶 Dog Walker Dashboard")

walkers = get_table("walkers")
if walkers.empty:
    st.warning("No walkers found. Please contact admin.")
else:
    walker_name = st.selectbox("Select Your Profile", walkers["name"])
    walker_id = walkers.loc[walkers["name"]==walker_name, "walker_id"].values[0]

    # --- VIEW ASSIGNED WALKS ---
    walks = get_table("walks")
    my_walks = walks[walks["walker_id"] == walker_id]

    st.subheader("📅 My Walks")
    if my_walks.empty:
        st.info("No walks assigned yet.")
    else:
        st.dataframe(my_walks.sort_values("date"))

    # --- UPDATE WALK STATUS ---
    st.subheader("Update Walk Status")
    pending_walks = my_walks[my_walks["status"].isin(["Scheduled","Requested"])]
    if pending_walks.empty:
        st.info("No pending walks to update.")
    else:
        walk_id = st.selectbox("Select Walk", pending_walks["walk_id"])
        new_status = st.selectbox("New Status", ["Completed","Cancelled"])
        notes = st.text_area("Notes about this walk")
        if st.button("Update Status"):
            update_data("walks", "walk_id", walk_id, {"status": new_status, "notes": notes})
            st.success(f"Walk #{walk_id} updated to {new_status}.")

    # --- VIEW CLIENT & DOG INFO ---
    st.subheader("Client & Dog Info")
    if my_walks.empty:
        st.info("No client or dog information available.")
    else:
        dog_ids = my_walks["dog_id"].unique().tolist()
        client_ids = my_walks["client_id"].unique().tolist()

        dogs = get_table("dogs")
        clients = get_table("clients")

        st.markdown("**Dogs You've Walked**")
        st.dataframe(dogs[dogs["dog_id"].isin(dog_ids)])

        st.markdown("**Clients You Walk For**")
        st.dataframe(clients[clients["client_id"].isin(client_ids)])

    # --- PERFORMANCE SUMMARY ---
    st.subheader("Performance Summary")
    total = len(my_walks)
    completed = len(my_walks[my_walks["status"]=="Completed"])
    cancelled = len(my_walks[my_walks["status"]=="Cancelled"])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Walks", total)
    col2.metric("Completed", completed)
    col3.metric("Cancelled", cancelled)
