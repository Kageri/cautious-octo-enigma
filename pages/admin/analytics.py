import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# --- PAGE CONFIG ---
st.set_page_config(page_title="Dog Walking Company Growth Dashboard", layout="wide")

st.title("🐾 Dog Walking Company Growth Analytics Dashboard")

# --- SAMPLE DATA ---
# In real usage, replace this with data from your SQL DB or API
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

# --- CHARTS ---
st.subheader("📈 Growth Over Time")
tab1, tab2, tab3 = st.tabs(["Dogs Walked", "Revenue", "Clients"])

with tab1:
    fig1 = px.line(df, x="Date", y="Dogs Walked", title="Dogs Walked Over Time")
    st.plotly_chart(fig1, use_container_width=True)

with tab2:
    fig2 = px.line(df, x="Date", y="Revenue", title="Revenue Over Time ($)")
    st.plotly_chart(fig2, use_container_width=True)

with tab3:
    fig3 = px.line(df, x="Date", y="New Clients", title="New Clients Over Time")
    st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# --- PERFORMANCE INSIGHTS ---
st.subheader("📊 Operational Insights")

col1, col2 = st.columns(2)

with col1:
    fig4 = px.bar(df.tail(30), x="Date", y=["Dogs Walked", "Cancellations"], barmode="group",
                  title="Recent Dog Walks vs Cancellations")
    st.plotly_chart(fig4, use_container_width=True)

with col2:
    df["Revenue per Walker"] = df["Revenue"] / df["Active Walkers"]
    fig5 = px.line(df, x="Date", y="Revenue per Walker", title="Revenue Efficiency per Walker")
    st.plotly_chart(fig5, use_container_width=True)

st.markdown("---")

# --- FUTURE METRICS SUGGESTION ---
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
