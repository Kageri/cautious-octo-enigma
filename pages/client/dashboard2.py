import streamlit as st
import pandas as pd

def app():
    st.title("Analytics")
    st.write("Admin analytics page content here.")
    
st.set_page_config(page_title="Client Dashboard", layout="wide")

st.title("Client Dashboard — Manage Account & Dogs")

# -------------------------
# CLIENT INFO
# -------------------------
if "client" not in st.session_state:
    st.session_state.client = {
        "name": "John Doe",
        "email": "john@example.com",
        "phone": "555-1234",
        "address": "123 Main St",
        "notes": "Loves walks in the park",
    }

# -------------------------
# DOGS: KEEP AS LIST, NOT DATAFRAME
# -------------------------
if "dogs" not in st.session_state:
    st.session_state.dogs = [
        {"name": "Buddy", "breed": "Labrador", "age": 4},
        {"name": "Luna", "breed": "Husky", "age": 2},
    ]

# -------------------------
# EDIT CLIENT INFO
# -------------------------
st.subheader("Edit Your Information")
with st.form("client_info_form"):
    name = st.text_input("Name", value=st.session_state.client["name"])
    email = st.text_input("Email", value=st.session_state.client["email"])
    phone = st.text_input("Phone", value=st.session_state.client["phone"])
    address = st.text_input("Address", value=st.session_state.client["address"])
    notes = st.text_area("Additional Notes", value=st.session_state.client["notes"])
    if st.form_submit_button("Update Info"):
        st.session_state.client.update({
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "notes": notes
        })
        st.success("Client information updated!")

# -------------------------
# ADD DOG
# -------------------------
st.subheader("Add a New Dog")
with st.form("add_dog_form"):
    dog_name = st.text_input("Dog Name")
    breed = st.text_input("Breed")
    age = st.number_input("Age", min_value=0, max_value=25, step=1)
    if st.form_submit_button("Add Dog"):
        # append to the list, NOT a DataFrame
        st.session_state.dogs.append({"name": dog_name, "breed": breed, "age": age})
        st.success(f"Added {dog_name}!")

# -------------------------
# EDIT EXISTING DOGS
# -------------------------
st.subheader("Your Dogs")
for idx, dog in enumerate(st.session_state.dogs):
    st.markdown(f"**{dog['name']}**")
    with st.expander("Edit Dog Info"):
        new_name = st.text_input("Name", value=dog["name"], key=f"name_{idx}")
        new_breed = st.text_input("Breed", value=dog["breed"], key=f"breed_{idx}")
        new_age = st.number_input("Age", min_value=0, max_value=25, value=dog["age"], step=1, key=f"age_{idx}")
        if st.button("Update Dog", key=f"update_{idx}"):
            st.session_state.dogs[idx] = {"name": new_name, "breed": new_breed, "age": new_age}
            st.success(f"{new_name}'s info updated!")

# -------------------------
# DISPLAY CLIENT + DOGS
# -------------------------
st.subheader("Client Summary")
st.table(pd.DataFrame([st.session_state.client]))

st.subheader("Dogs Summary")
st.table(pd.DataFrame(st.session_state.dogs))
