import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import numpy as np

# --- PAGE CONFIG ---
st.set_page_config(page_title="Dog Walking Company Management Dashboard", layout="wide")

st.title("🐕 Dog Walking Company Management Dashboard")

# --- SIDEBAR CONTROLS ---
st.sidebar.header("🔧 Dashboard Filters")

start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=30))
end_date = st.sidebar.date_input("End Date", datetime.now())
selected_view = st.sidebar.selectbox("View Mode", ["Overview", "Operations", "Finance", "Clients", "Walkers"])

# --- MOCK DATA ---
days = (end_date - start_date).days + 1
dates = pd.date_range(start_date, end_date, freq="D")

data = {
    "Date": dates,
    "Dogs Walked": np.random.randint(10, 40, size=days),
    "Revenue": np.random.randint(300, 1200, size=days),
    "New Clients": np.random.randint(0, 6, size=days),
    "Active Walkers": np.random.randint(3, 10, size=days),
    "Cancellations": np.random.randint(0, 4, size=days),
    "Distance (km)": np.random.uniform(2, 8, size=days),
    "Avg Walk Time (min)": np.random.uniform(25, 60, size=days)
}

df = pd.DataFrame(data)

# --- KPI SECTION ---
total_dogs = df["Dogs Walked"].sum()
total_revenue = df["Revenue"].sum()
avg_distance = round(df["Distance (km)"].mean(), 2)
avg_walk_time = round(df["Avg Walk Time (min)"].mean(), 1)
new_clients = df["New Clients"].sum()

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🐶 Dogs Walked", f"{total_dogs:,}")
col2.metric("💰 Total Revenue", f"${total_revenue:,}")
col3.metric("📍 Avg. Distance", f"{avg_distance} km")
col4.metric("⏱️ Avg. Walk Time", f"{avg_walk_time} min")
col5.metric("🧍 New Clients", f"{new_clients:,}")

st.markdown("---")

# --- MAIN VIEWS ---
if selected_view == "Overview":
    st.subheader("📈 Company Overview")

    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Revenue"], label="Revenue", color="green")
    ax.plot(df["Date"], df["Dogs Walked"], label="Dogs Walked", color="steelblue")
    ax.set_title("Daily Revenue & Dogs Walked")
    ax.legend()
    st.pyplot(fig)

    st.subheader("🔍 Insights Summary")
    st.write(f"""
    - **Growth Trend:** {(df['Revenue'].iloc[-1] - df['Revenue'].iloc[0]) / df['Revenue'].iloc[0] * 100:.1f}% increase in revenue since period start.
    - **Best Performing Day:** {df.loc[df['Revenue'].idxmax(), 'Date'].strftime('%b %d, %Y')} (${df['Revenue'].max():,.0f})
    - **Client Acquisition Rate:** {new_clients / days:.2f} new clients per day on average.
    """)

elif selected_view == "Operations":
    st.subheader("🚶 Operational Performance")

    col1, col2 = st.columns(2)
    with col1:
        fig, ax = plt.subplots()
        ax.plot(df["Date"], df["Dogs Walked"], color="steelblue")
        ax.set_title("Dogs Walked Per Day")
        st.pyplot(fig)
    with col2:
        fig, ax = plt.subplots()
        ax.bar(df["Date"], df["Cancellations"], color="tomato")
        ax.set_title("Daily Cancellations")
        st.pyplot(fig)

    st.subheader("📍 Walk Efficiency")
    fig, ax = plt.subplots()
    ax.scatter(df["Distance (km)"], df["Avg Walk Time (min)"], c=df["Dogs Walked"], cmap="viridis")
    ax.set_xlabel("Distance (km)")
    ax.set_ylabel("Walk Time (min)")
    ax.set_title("Distance vs Walk Duration")
    st.pyplot(fig)

elif selected_view == "Finance":
    st.subheader("💵 Financial Overview")

    df["Cumulative Revenue"] = df["Revenue"].cumsum()
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Cumulative Revenue"], color="green")
    ax.set_title("Cumulative Revenue Over Time")
    ax.set_ylabel("Revenue ($)")
    st.pyplot(fig)

    avg_rev_per_dog = total_revenue / total_dogs
    avg_rev_per_client = total_revenue / max(new_clients, 1)

    st.write(f"""
    **Key Financial Indicators:**
    - Average revenue per walk: **${avg_rev_per_dog:.2f}**
    - Average revenue per client: **${avg_rev_per_client:.2f}**
    - Revenue growth rate (period): **{(df['Revenue'].iloc[-1] - df['Revenue'].iloc[0]) / df['Revenue'].iloc[0] * 100:.2f}%**
    """)

elif selected_view == "Clients":
    st.subheader("👥 Client Management")

    st.write("""
    **Metrics to Track:**
    - New client acquisition
    - Repeat customer rate
    - Client satisfaction / reviews
    - Subscription or package usage
    """)

    fig, ax = plt.subplots()
    ax.bar(df["Date"], df["New Clients"], color="orange")
    ax.set_title("New Clients per Day")
    st.pyplot(fig)

elif selected_view == "Walkers":
    st.subheader("🧍 Walker Performance")

    avg_walks_per_walker = (df["Dogs Walked"] / df["Active Walkers"]).mean()
    st.write(f"Average walks per walker per day: **{avg_walks_per_walker:.2f}**")

    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Active Walkers"], color="purple")
    ax.set_title("Active Walkers Over Time")
    ax.set_ylabel("Walkers")
    st.pyplot(fig)

st.markdown("---")

# --- MANAGEMENT NOTES ---
st.subheader("🗂️ Key Areas to Manage in a Dog Walking Company")
management_areas = [
    "Client relationships & retention",
    "Walker scheduling and route optimization",
    "Payroll and walker performance tracking",
    "Customer service and feedback handling",
    "Insurance, licensing, and compliance",
    "Marketing & advertising (social, referrals, partnerships)",
    "Expense tracking and profitability analysis",
    "Safety protocols and incident logging",
    "Time tracking & punctuality monitoring",
    "App or website performance (if digital scheduling is used)"
]
for area in management_areas:
    st.markdown(f"- {area}")
