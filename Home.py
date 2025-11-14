# ===============================================
# Streamlit Admin Dashboard – Fully Functional CRUD
# Live MySQL Database Integration
# ===============================================

# Install dependencies:
# pip install streamlit sqlalchemy pymysql pandas

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

# Inline registration
components.html("""
<script>
const swCode = `
self.addEventListener('install', e => e.waitUntil(
  caches.open('sw-cache').then(cache => cache.addAll(['/']))
));
self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(r => r || fetch(e.request)));
});
`;
const blob = new Blob([swCode], { type: 'application/javascript' });
const swUrl = URL.createObjectURL(blob);

if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register(swUrl)
    .then(() => console.log('Service Worker registered'))
    .catch(err => console.error(err));
}
</script>
""", height=0)

# --- DATABASE CONNECTION ---
DB_USER = "root"
DB_PASSWORD = "Tsu9tail$13"
DB_HOST = "localhost"
DB_PORT = 3306
DB_NAME = "dog_walking_company"

engine = create_engine(f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# --- UTILITY FUNCTIONS ---
@st.cache_data(ttl=30)
def get_table(table_name: str) -> pd.DataFrame:
    with engine.connect() as conn:
        return pd.read_sql(f"SELECT * FROM {table_name}", conn)

def insert_client(name, phone, email, address):
    if not name:
        st.error("Client name is required")
        return
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO clients (name, phone, email, address)
            VALUES (:name, :phone, :email, :address)
        """), {"name": name, "phone": phone, "email": email, "address": address})
    st.success(f"Client '{name}' added successfully!")

def insert_dog(name, breed, age, owner_id):
    if not name or owner_id is None:
        st.error("Dog name and owner are required")
        return
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO dogs (name, breed, age, owner_id)
            VALUES (:name, :breed, :age, :owner_id)
        """), {"name": name, "breed": breed, "age": age, "owner_id": owner_id})
    st.success(f"Dog '{name}' added successfully!")

def insert_walker(name, phone, availability):
    if not name:
        st.error("Walker name is required")
        return
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO walkers (name, phone, availability)
            VALUES (:name, :phone, :availability)
        """), {"name": name, "phone": phone, "availability": ",".join(availability)})
    st.success(f"Walker '{name}' added successfully!")

def insert_walk(dog_id, walker_id, client_id, date, time, status, notes):
    if dog_id is None or client_id is None or date is None or time is None:
        st.error("Dog, client, date, and time are required")
        return
    with engine.begin() as conn:
        conn.execute(text("""
            INSERT INTO walks (dog_id, walker_id, client_id, date, time, status, notes)
            VALUES (:dog_id, :walker_id, :client_id, :date, :time, :status, :notes)
        """), {"dog_id": dog_id, "walker_id": walker_id, "client_id": client_id, 
               "date": date, "time": time, "status": status, "notes": notes})
    st.success("Walk scheduled successfully!")

# --- ADMIN DASHBOARD ---
st.title("🛠 Admin Dashboard - Dog Walking Company")

# ------------------------
# CLIENTS
# ------------------------
st.header("👥 Clients")
clients = get_table("clients")
st.dataframe(clients)

st.subheader("Add New Client")
with st.form("add_client_form"):
    name = st.text_input("Name")
    phone = st.text_input("Phone")
    email = st.text_input("Email")
    address = st.text_input("Address")
    submitted = st.form_submit_button("Add Client")
    if submitted:
        insert_client(name, phone, email, address)
        st.experimental_rerun()

# ------------------------
# DOGS
# ------------------------
st.header("🐕 Dogs")
dogs = get_table("dogs")
st.dataframe(dogs)

st.subheader("Add New Dog")
with st.form("add_dog_form"):
    dog_name = st.text_input("Dog Name")
    breed = st.text_input("Breed")
    age = st.number_input("Age", 0, 30)
    owner = st.selectbox("Owner", clients["name"].tolist() if not clients.empty else [])
    submitted = st.form_submit_button("Add Dog")
    if submitted:
        if owner:
            owner_id = clients.loc[clients["name"]==owner, "client_id"].values[0]
            insert_dog(dog_name, breed, age, owner_id)
            st.experimental_rerun()
        else:
            st.error("Select a valid owner")

# ------------------------
# WALKERS
# ------------------------
st.header("🚶 Walkers")
walkers = get_table("walkers")
st.dataframe(walkers)

st.subheader("Add New Walker")
with st.form("add_walker_form"):
    walker_name = st.text_input("Walker Name")
    walker_phone = st.text_input("Phone")
    availability = st.multiselect("Availability", ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"])
    submitted = st.form_submit_button("Add Walker")
    if submitted:
        insert_walker(walker_name, walker_phone, availability)
        st.experimental_rerun()

# ------------------------
# WALKS
# ------------------------
st.header("📅 Walks")
walks = get_table("walks")
st.dataframe(walks)

st.subheader("Schedule a Walk")
with st.form("add_walk_form"):
    dog_options = dogs["name"].tolist() if not dogs.empty else []
    walker_options = walkers["name"].tolist() if not walkers.empty else []
    client_options = clients["name"].tolist() if not clients.empty else []

    dog_name = st.selectbox("Select Dog", dog_options)
    walker_name = st.selectbox("Select Walker", ["None"] + walker_options)
    client_name = st.selectbox("Select Client", client_options)
    date = st.date_input("Date", datetime.now())
    time = st.time_input("Time", datetime.now().time())
    status = st.selectbox("Status", ["Requested", "Scheduled", "Completed", "Cancelled"])
    notes = st.text_area("Notes")
    submitted = st.form_submit_button("Schedule Walk")
    if submitted:
        dog_id = dogs.loc[dogs["name"]==dog_name, "dog_id"].values[0] if dog_name else None
        walker_id = walkers.loc[walkers["name"]==walker_name, "walker_id"].values[0] if walker_name != "None" else None
        client_id = clients.loc[clients["name"]==client_name, "client_id"].values[0] if client_name else None
        insert_walk(dog_id, walker_id, client_id, date, time, status, notes)
        st.experimental_rerun()
