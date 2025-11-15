import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def app():
    st.title("Analytics")
    st.write("Admin analytics page content here.")
# --- PAGE CONFIG ---
st.set_page_config(page_title="Dog Walking Company Growth Dashboard", layout="wide")

st.title("🐾 Dog Walking Company Growth Analytics Dashboard")

# --- SAMPLE DATA ---
# Replace with live SQL or API data
data = {
    "Date": pd.date_range(datetime.now() - timedelta(days=180), periods=180),
    "Dogs Walked": (pd.Series(range(180)) * 2 + 20).apply(lambda x: x + (x * 0.05)),
    "Revenue": (pd.Series(range(180)) * 15 + 500),
    "New Clients": (pd.Series(range(180)) % 10 + 2),
    "Active Walkers": (pd.Series(range(180)) % 7 + 3),
    "Cancellations": (pd.Series(range(180)) % 5)
}
df = pd.DataFrame(data)

# --- KPI METRICS ---
total_dogs = int(df["Dogs Walked"].sum())
total_revenue = int(df["Revenue"].sum())
new_clients = int(df["New Clients"].sum())
avg_revenue_per_walk = round(total_revenue / total_dogs, 2)

col1, col2, col3, col4 = st.columns(4)
col1.metric("🐶 Total Dogs Walked", f"{total_dogs:,}")
col2.metric("💰 Total Revenue", f"${total_revenue:,}")
col3.metric("👥 New Clients Acquired", f"{new_clients:,}")
col4.metric("📊 Avg. Revenue / Walk", f"${avg_revenue_per_walk}")

st.markdown("---")

# --- GROWTH VISUALS ---
st.subheader("📈 Growth Over Time")
tab1, tab2, tab3 = st.tabs(["Dogs Walked", "Revenue", "Clients"])

with tab1:
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Dogs Walked"], color="steelblue")
    ax.set_title("Dogs Walked Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("Dogs Walked")
    st.pyplot(fig)

with tab2:
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Revenue"], color="green")
    ax.set_title("Revenue Over Time ($)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue")
    st.pyplot(fig)

with tab3:
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["New Clients"], color="orange")
    ax.set_title("New Clients Over Time")
    ax.set_xlabel("Date")
    ax.set_ylabel("New Clients")
    st.pyplot(fig)

st.markdown("---")

# --- OPERATIONAL INSIGHTS ---
st.subheader("📊 Operational Insights")

col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots()
    recent = df.tail(30)
    ax.bar(recent["Date"], recent["Dogs Walked"], label="Dogs Walked", alpha=0.7)
    ax.bar(recent["Date"], recent["Cancellations"], label="Cancellations", alpha=0.7)
    ax.set_title("Recent Dog Walks vs Cancellations (30 Days)")
    ax.legend()
    st.pyplot(fig)

with col2:
    df["Revenue per Walker"] = df["Revenue"] / df["Active Walkers"]
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Revenue per Walker"], color="purple")
    ax.set_title("Revenue Efficiency per Walker")
    ax.set_xlabel("Date")
    ax.set_ylabel("Revenue / Walker")
    st.pyplot(fig)

st.markdown("---")

# --- RECOMMENDED METRICS ---
st.subheader("📋 Recommended Metrics to Track for Growth")

metrics = [
    "Total number of dog walks (daily, weekly, monthly)",
    "Average revenue per walk and per client",
    "Client retention rate (repeat customers vs new)",
    "Walker utilization rate (walks per walker per day)",
    "Cancellations and no-shows percentage",
    "Average distance/time per walk",
    "Customer satisfaction (ratings, reviews)",
    "Marketing ROI (spend vs new client acquisition)",
    "Revenue by neighborhood or region",
    "Subscription or package plan uptake rate",
    "Lifetime value per client",
    "Peak time analysis (best days/hours for walks)"
]

for m in metrics:
    st.markdown(f"- {m}")

st.info("💡 Connect this dashboard to your live database or CRM to visualize real-time growth trends.")
