import streamlit as st
import mariadb

# Database connection
def get_connection():
    try:
        conn = mariadb.connect(
            user="root",
            password="yourpassword",
            host="localhost",
            port=3306,
            database="pet_care"
        )
        return conn
    except mariadb.Error as e:
        st.error(f"Error connecting to MariaDB: {e}")
        return None

# Insert data functions
def add_owner(name, email, phone):
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO owner (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
        conn.commit()
        conn.close()
        st.success("Owner added successfully!")

def add_client(name, email, phone):
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO client (name, email, phone) VALUES (?, ?, ?)", (name, email, phone))
        conn.commit()
        conn.close()
        st.success("Client added successfully!")

def add_dog(name, breed, age, owner_id):
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        cur.execute("INSERT INTO dogs (name, breed, age, owner_id) VALUES (?, ?, ?, ?)", (name, breed, age, owner_id))
        conn.commit()
        conn.close()
        st.success("Dog added successfully!")

# Streamlit UI
st.title("🐶 Pet Care Database App")

menu = st.sidebar.selectbox("Select Table", ["Owner", "Client", "Dogs"])

if menu == "Owner":
    st.header("Add Owner")
    name = st.text_input("Owner Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    if st.button("Add Owner"):
        add_owner(name, email, phone)

elif menu == "Client":
    st.header("Add Client")
    name = st.text_input("Client Name")
    email = st.text_input("Email")
    phone = st.text_input("Phone")
    if st.button("Add Client"):
        add_client(name, email, phone)

elif menu == "Dogs":
    st.header("Add Dog")
    name = st.text_input("Dog Name")
    breed = st.text_input("Breed")
    age = st.number_input("Age", min_value=0, step=1)
    owner_id = st.number_input("Owner ID", min_value=1, step=1)
    if st.button("Add Dog"):
        add_dog(name, breed, age, owner_id)

# Display data
if st.checkbox("Show Tables"):
    conn = get_connection()
    if conn:
        cur = conn.cursor()
        for table in ["owner", "client", "dogs"]:
            st.subheader(f"{table.title()} Table")
            cur.execute(f"SELECT * FROM {table}")
            rows = cur.fetchall()
            st.dataframe(rows)
        conn.close()
