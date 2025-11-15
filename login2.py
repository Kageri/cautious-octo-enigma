import streamlit as st
import importlib
import os
import sys


# Add the folder containing 'pages' to sys.path
sys.path.append(os.path.dirname(__file__))

st.set_page_config(page_title="Routing", layout="wide")

# ------------------------------------
# AUTH STATE
# ------------------------------------
if "role" not in st.session_state:
    st.session_state.role = None

# ------------------------------------
# ROLE-BASED PAGE MAPS
# (Points to folders in /pages/)
# ------------------------------------
ROLE_PAGES = {
    "admin": {
        "Admin Dashboard": "pages.admin.adminv2",
        #"Manage Admins": "pages.admin.analytics2",
        "Control Pannel": "pages.admin.control_panel2"
 
    },
    "client": {
        "Client Dashboard": "pages.client.dashboard2",
        "Schedule": "pages.client.calendar",
    },
    "walker": {
        "My Schedule": "pages.walker.dashboard3",
    },
}

# ------------------------------------
# LOGIN FORM (DEMO)
# ------------------------------------
USERS = {
    "admin@example.com": {"password": "123", "role": "admin"},
    "client@example.com": {"password": "123", "role": "client"},
    "walker@example.com": {"password": "123", "role": "walker"},
}

def login_screen():
    st.title("Sign In")

    email = st.text_input("Email")
    pw = st.text_input("Password", type="password")

    if st.button("Login"):
        user = USERS.get(email)
        if user and user["password"] == pw:
            st.session_state.role = user["role"]
            st.rerun()
        else:
            st.error("Invalid credentials")


# ------------------------------------
# ROLE LOCK + PAGE LOADER
# ------------------------------------
def load_page(module_path):
    module = importlib.import_module(module_path)
    module.app()   # each page file contains:  def app(): ...


# ------------------------------------
# MAIN ROUTER
# ------------------------------------
if st.session_state.role is None:
    login_screen()

else:
    role = st.session_state.role
    pages = ROLE_PAGES[role]

    st.sidebar.title(f"{role.capitalize()} Menu")
    selection = st.sidebar.radio("Go to:", list(pages.keys()))

    if st.sidebar.button("Logout"):
        st.session_state.role = None
        st.rerun()

    # Load the selected page
    load_page(pages[selection])
