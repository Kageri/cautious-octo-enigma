import streamlit as st
import pandas as pd

st.set_page_config(page_title="Client Dashboard", layout="wide")

st.title("Client Dashboard — Manage Dogs")

# -------------------------
# DEMO DOG DATA
# -------------------------
if "dogs" not in st.session_state:
    st.session_state.dogs = [
        {"name": "Buddy", "breed": "Labrador", "age": 4},
        {"name": "Luna", "breed": "Husky", "age": 2},
    ]

# -------------------------
# ADD NEW DOG
# -------------------------
st.subheader("Add a New Dog")
with st.form("add_dog_form"):
    name = st.text_input("Dog Name")
    breed = st.text_input("Breed")
    age = st.number_input("Age", min_value=0, max_value=25, step=1)
    submitted = st.form_submit_button("Add Dog")
    if submitted:
        st.session_state.dogs.append({"name": name, "breed": breed, "age": age})
        st.success(f"Added {name}!")

# -------------------------
# VIEW + EDIT EXISTING DOGS
# -------------------------
st.subheader("Your Dogs")
for idx, dog in enumerate(st.session_state.dogs):
    st.markdown(f"**{dog['name']}**")
    with st.expander("Edit Dog Info"):
        new_name = st.text_input("Name", value=dog["name"], key=f"name_{idx}")
        new_breed = st.text_input("Breed", value=dog["breed"], key=f"breed_{idx}")
        new_age = st.number_input("Age", min_value=0, max_value=25, value=dog["age"], step=1, key=f"age_{idx}")
        if st.button("Update", key=f"update_{idx}"):
            st.session_state.dogs[idx] = {"name": new_name, "breed": new_breed, "age": new_age}
            st.success(f"{new_name}'s info updated!")

# -------------------------
# DISPLAY DOGS IN TABLE
# -------------------------
st.subheader("All Dogs")
st.table(pd.DataFrame(st.session_state.dogs))
