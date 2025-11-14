# app.py
import streamlit as st
import requests
import json
import pandas as pd
from datetime import datetime, date, time

st.set_page_config(page_title="Dog Walking Admin Panel", layout="wide")

WEBHOOK_URL = "https://your-webhook-url.com/webhook/dogwalking"  # 🔗 Replace with your actual webhook endpoint

# -------------------------------
# Helper: Send data to webhook
# -------------------------------
def send_to_webhook(payload: dict):
    try:
        response = requests.post(WEBHOOK_URL, json=payload, timeout=5)
        if response.status_code == 200:
            st.success("✅ Data sent successfully!")
        else:
            st.warning(f"⚠️ Webhook returned {response.status_code}: {response.text}")
    except Exception as e:
        st.error(f"❌ Failed to send data: {e}")

# -------------------------------
# Page Header
# -------------------------------
st.title("🐾 Dog Walking Company Admin Panel")
st.write("Add owners, walkers, dogs, and schedule walks. Each submission automatically sends data to your webhook.")

# -------------------------------
# Tabs for Owners, Walkers, Dogs, Walks
# -------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["Add Owner", "Add Walker", "Add Dog", "Schedule Walk", "📅 Calendar View"])

# -------------------------------
# Add Owner
# -------------------------------
with tab1:
    st.subheader("Add Dog Owner")

    owner_name = st.text_input("Owner Name")
    owner_email = st.text_input("Owner Email")
    owner_phone = st.text_input("Owner Phone")
    owner_address = st.text_input("Owner Address")

    if st.button("Submit Owner"):
        payload = {
            "type": "owner",
            "data": {
                "name": owner_name,
                "email": owner_email,
                "phone": owner_phone,
                "address": owner_address,
            },
        }
        send_to_webhook(payload)

# -------------------------------
# Add Walker
# -------------------------------
with tab2:
    st.subheader("Add Walker")

    walker_name = st.text_input("Walker Name")
    walker_email = st.text_input("Walker Email")
    walker_phone = st.text_input("Walker Phone")

    if st.button("Submit Walker"):
        payload = {
            "type": "walker",
            "data": {
                "name": walker_name,
                "email": walker_email,
                "phone": walker_phone,
            },
        }
        send_to_webhook(payload)

# -------------------------------
# Add Dog
# -------------------------------
with tab3:
    st.subheader("Add Dog")

    dog_name = st.text_input("Dog Name")
    dog_breed = st.text_input("Breed")
    dog_age = st.number_input("Age", min_value=0, max_value=30, step=1)
    dog_owner_id = st.text_input("Owner ID (link dog to owner)")
    dog_notes = st.text_area("Notes")

    if st.button("Submit Dog"):
        payload = {
            "type": "dog",
            "data": {
                "name": dog_name,
                "breed": dog_breed,
                "age": dog_age,
                "owner_id": dog_owner_id,
                "notes": dog_notes,
            },
        }
        send_to_webhook(payload)

# -------------------------------
# Schedule a Walk
# -------------------------------
with tab4:
    st.subheader("Schedule a Walk")

    walker_id = st.text_input("Walker ID")
    dog_id = st.text_input("Dog ID")
    walk_date = st.date_input("Walk Date", value=date.today())
    walk_time = st.time_input("Walk Time", value=datetime.now().time())
    notes = st.text_area("Walk Notes")

    if st.button("Schedule Walk"):
        # Combine date and time
        walk_datetime = datetime.combine(walk_date, walk_time)
        payload = {
            "type": "walk",
            "data": {
                "walker_id": walker_id,
                "dog_id": dog_id,
                "scheduled_time": walk_datetime.isoformat(),
                "notes": notes,
            },
        }
        send_to_webhook(payload)
        # Save locally for calendar view
        if "walks" not in st.session_state:
            st.session_state["walks"] = []
        st.session_state["walks"].append(payload["data"])

# -------------------------------
# Calendar View
# -------------------------------
with tab5:
    st.subheader("📅 Scheduled Walks Calendar")

    if "walks" not in st.session_state or len(st.session_state["walks"]) == 0:
        st.info("No walks scheduled yet.")
    else:
        walks_df = pd.DataFrame(st.session_state["walks"])
        walks_df["scheduled_time"] = pd.to_datetime(walks_df["scheduled_time"])
        walks_df["Date"] = walks_df["scheduled_time"].dt.date
        walks_df["Time"] = walks_df["scheduled_time"].dt.time

        st.dataframe(
            walks_df[["dog_id", "walker_id", "Date", "Time", "notes"]]
            .sort_values(by="scheduled_time")
            .reset_index(drop=True),
            use_container_width=True,
            height=400
        )

        # Optional: Simple daily visual summary
        st.bar_chart(walks_df.groupby("Date").size())
