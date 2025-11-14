import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Life Streamlining Dashboard", layout="wide")

st.title("🌿 Life Streamlining Dashboard")
st.caption("Reflect, track, and visualize what truly matters to you while minimizing distractions.")

with st.sidebar:
    st.header("🧭 Define Your Core Intentions")
    core_values = st.text_area("What are your top 3 core values?", placeholder="e.g. Creativity, Freedom, Service")
    life_mission = st.text_area("What is your central life mission?", placeholder="e.g. To create meaningful systems that help others live intentionally")
    st.divider()
    st.header("⚙️ Categories to Streamline")
    categories = st.multiselect(
        "Select areas you want to simplify:",
        ["Work", "Social", "Digital", "Health", "Environment", "Habits", "Finances", "Other"],
        default=["Digital", "Habits", "Environment"]
    )

st.subheader("🧹 Distraction Log & Simplification Plan")

if "log" not in st.session_state:
    st.session_state.log = pd.DataFrame(columns=["Category", "Distraction", "Impact", "Keep/Remove", "Notes"])

with st.expander("Add a New Distraction"):
    col1, col2, col3 = st.columns(3)
    with col1:
        cat = st.selectbox("Category", categories)
    with col2:
        distraction = st.text_input("Distraction or Activity")
    with col3:
        impact = st.slider("Impact on Focus (1=low, 5=high)", 1, 5, 3)
    keep_remove = st.radio("Decision", ["Keep", "Remove"], horizontal=True)
    notes = st.text_area("Notes or plan to minimize it")
    if st.button("➕ Add Entry"):
        new_entry = pd.DataFrame(
            [[cat, distraction, impact, keep_remove, notes]],
            columns=["Category", "Distraction", "Impact", "Keep/Remove", "Notes"]
        )
        st.session_state.log = pd.concat([st.session_state.log, new_entry], ignore_index=True)
        st.success("Entry added!")

if len(st.session_state.log) > 0:
    st.dataframe(st.session_state.log, use_container_width=True)

    st.subheader("📊 Distraction Impact Overview")
    fig = px.bar(
        st.session_state.log,
        x="Distraction",
        y="Impact",
        color="Keep/Remove",
        title="Impact of Distractions on Focus",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("🪶 Simplification Progress")
    removal_ratio = (st.session_state.log["Keep/Remove"].value_counts().get("Remove", 0) / len(st.session_state.log)) * 100
    st.metric("Percentage of Distractions Marked for Removal", f"{removal_ratio:.1f}%")

st.divider()
st.header("🧘 Guidance Section")
st.write("""
**Streamlining Steps:**
1. Clarify purpose — Write your mission somewhere visible.  
2. Identify leaks — Notice time and energy drains daily.  
3. Replace, not remove — Swap low-value tasks for aligned actions.  
4. Schedule space — Build daily quiet or reflection blocks.  
5. Reassess weekly — Track progress in this dashboard.  
""")

if core_values or life_mission:
    st.markdown("### 🪷 Your Intent Summary")
    st.write(f"**Core Values:** {core_values}")
    st.write(f"**Mission:** {life_mission}")
