import streamlit as st

st.set_page_config(page_title="Admin Control Panel", layout="wide")

# ---------------------------------------------------------
# ADMIN-ONLY CONTROL PANEL (NO LOGIN NEEDED)
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

# ------------------------- VIEW SCHEDULES ------------------------
with tabs[5]:
    st.header("Walking Schedule")
    st.table([
        {"walker": "Walker One", "dog": "Buddy", "time": "10:00 AM"},
        {"walker": "Walker One", "dog": "Luna", "time": "12:00 PM"},
    ])
