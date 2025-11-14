
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from geopy.distance import geodesic
from sklearn.cluster import KMeans
import pydeck as pdk

import streamlit as st
import os

# If geopy is not installed, install it
try:
    from geopy.distance import geodesic
except ImportError:
    st.text('Installing geopy package...')
    os.system('pip install geopy')

# Example Streamlit app content
st.title("Geopy Distance Calculator")

st.set_page_config(layout="wide")

st.title("Dog Walking Routing & Scheduling System")

# -----------------------
# SAMPLE DATA INPUTS
# -----------------------
st.sidebar.header("Data Input")

uploaded = st.sidebar.file_uploader("Upload client addresses CSV", type=["csv"])

sample = st.sidebar.checkbox("Use sample data")

if sample:
    data = pd.DataFrame({
        "client": ["A","B","C","D","E","F"],
        "lat": [39.7392,39.7420,39.7350,39.7550,39.7501,39.7484],
        "lon": [-104.9903,-104.9982,-104.9820,-104.9700,-105.0020,-104.9912],
        "walk_time": ["09:00","10:00","09:30","11:00","10:15","09:45"]
    })
elif uploaded:
    data = pd.read_csv(uploaded)
else:
    st.stop()

data["walk_dt"] = pd.to_datetime(data["walk_time"], format="%H:%M")

# -----------------------
# CLUSTERING INTO ROUTES
# -----------------------

st.subheader("Generated Routes")

num_walkers = st.sidebar.number_input("Number of walkers", min_value=1, max_value=20, value=2)

coords = data[["lat","lon"]].values
kmeans = KMeans(n_clusters=num_walkers, n_init="auto").fit(coords)
data["route"] = kmeans.labels_

# -----------------------
# ORDER INSIDE EACH ROUTE
# -----------------------

def order_route(df):
    points = df[["lat","lon"]].values
    start = np.argmin([abs((t - df["walk_dt"].min()).seconds) for t in df["walk_dt"]])
    route = [start]
    remaining = list(range(len(points)))
    remaining.remove(start)

    while remaining:
        last = points[route[-1]]
        next_idx = min(remaining, key=lambda i: geodesic(last, points[i]).meters)
        route.append(next_idx)
        remaining.remove(next_idx)
    return df.iloc[route]

ordered = (
    data.groupby("route")
    .apply(order_route)
    .reset_index(drop=True)
)

st.dataframe(ordered)

# -----------------------
# MAP VISUALIZATION
# -----------------------

st.subheader("Route Map")

layers = []
colors = [
    [255,0,0],
    [0,255,0],
    [0,0,255],
    [255,255,0],
    [255,0,255],
    [0,255,255],
]

for r in ordered["route"].unique():
    subset = ordered[ordered["route"] == r].copy()
    subset["color"] = [colors[r % len(colors)]] * len(subset)

    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=subset,
            get_position=["lon","lat"],
            get_color="color",
            get_radius=40,
        )
    )

    path = subset[["lon","lat"]].values.tolist()

    layers.append(
        pdk.Layer(
            "PathLayer",
            data=[{"path": path}],
            get_color=colors[r % len(colors)],
            width_scale=10,
            width_min_pixels=3,
        )
    )

view = pdk.ViewState(
    latitude=ordered["lat"].mean(),
    longitude=ordered["lon"].mean(),
    zoom=12
)

st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view))

# -----------------------
# EXPORT
# -----------------------

st.subheader("Download Route Plan")

csv = ordered.to_csv(index=False)
st.download_button("Download CSV", csv, "routes.csv")
