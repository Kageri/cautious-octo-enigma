import streamlit as st
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

# --- DB connection ---
conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Tsu9tail$13",
    database="dog_walking_company"
)
cursor = conn.cursor(dictionary=True)

# --- Login Form ---
walker_name = st.text_input("Name")
password = st.text_input("Password", type="password")

if st.button("Login"):
    cursor.execute("SELECT * FROM walkers WHERE name=%s", (walker_name,))
    walker = cursor.fetchone()
    
    if walker and check_password_hash(walker["password_hash"], password):
        st.success(f"Logged in as {walker_name}")
        
        # --- Force password change if first login ---
        if walker["must_change_password"]:
            st.warning("Please set a new password")
            new_password = st.text_input("New Password", type="password")
            if st.button("Update Password"):
                new_hash = generate_password_hash(new_password)
                cursor.execute("""
                    UPDATE walkers SET password_hash=%s, must_change_password=FALSE
                    WHERE walker_id=%s
                """, (new_hash, walker["walker_id"]))
                conn.commit()
                st.success("Password updated successfully! You can now access your dashboard.")
        
        # --- Otherwise, show dashboard ---
        else:
            st.write("Accessing dashboard...")
    else:
        st.error("Invalid credentials")
