import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.cluster import KMeans
import pydeck as pdk

st.set_page_config(layout="wide")
st.title("Dog Walking Routing System (No External Packages Required)")

# ======================================================
# HAVERSINE DISTANCE (NO GEOPY NEEDED)
# ======================================================
def haversine(coord1, coord2):
    lat1, lon1 = np.radians(coord1)
    lat2, lon2 = np.radians(coord2)

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = np.sin(dlat/2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return 6371000 * c   # meters


# ======================================================
# DATA INPUT
# ======================================================
st.sidebar.header("Data Input")

uploaded = st.sidebar.file_uploader("Upload CSV (client, lat, lon, walk_time)", type=["csv"])
sample = st.sidebar.checkbox("Use sample data")

if sample:
    df = pd.DataFrame({
        "client": ["A","B","C","D","E","F"],
        "lat": [39.7392,39.7420,39.7350,39.7550,39.7501,39.7484],
        "lon": [-104.9903,-104.9982,-104.9820,-104.9700,-105.0020,-104.9912],
        "walk_time": ["09:00","10:00","09:30","11:00","10:15","09:45"]
    })
elif uploaded:
    df = pd.read_csv(uploaded)
else:
    st.stop()

df["walk_dt"] = pd.to_datetime(df["walk_time"], format="%H:%M")

# ======================================================
# CLUSTERING INTO ROUTES
# ======================================================
st.sidebar.header("Routing Settings")
walkers = st.sidebar.number_input("Number of walkers", min_value=1, max_value=20, value=2)

coords = df[["lat", "lon"]].values
kmeans = KMeans(n_clusters=walkers, n_init="auto")
df["route"] = kmeans.fit_predict(coords)


# ======================================================
# ORDER STOPS INSIDE EACH ROUTE
# ======================================================
def ordered_route(group):
    points = group[["lat","lon"]].values
    times = group["walk_dt"].values

    start_idx = np.argmin([abs((t - group["walk_dt"].min()).seconds) for t in times])
    remaining = list(range(len(points)))
    route = [start_idx]
    remaining.remove(start_idx)

    while remaining:
        last = points[route[-1]]
        next_i = min(remaining, key=lambda x: haversine(last, points[x]))
        route.append(next_i)
        remaining.remove(next_i)

    return group.iloc[route]

ordered_df = df.groupby("route", group_keys=False).apply(ordered_route)

st.subheader("Generated Route Order")
st.dataframe(ordered_df)


# ======================================================
# MAP VISUALIZATION
# ======================================================
st.subheader("Map View")

color_list = [
    [255, 0, 0],
    [0, 255, 0],
    [0, 100, 255],
    [255, 255, 0],
    [255, 0, 255],
    [0, 255, 255],
]

layers = []

for r in ordered_df["route"].unique():
    sub = ordered_df[ordered_df["route"] == r].copy()
    sub["color"] = [color_list[r % len(color_list)]] * len(sub)

    layers.append(
        pdk.Layer(
            "ScatterplotLayer",
            data=sub,
            get_position=["lon","lat"],
            get_color="color",
            get_radius=45,
        )
    )

    path = sub[["lon","lat"]].values.tolist()

    layers.append(
        pdk.Layer(
            "PathLayer",
            data=[{"path": path}],
            get_color=color_list[r % len(color_list)],
            width_scale=10,
            width_min_pixels=3,
        )
    )

view = pdk.ViewState(
    latitude=ordered_df["lat"].mean(),
    longitude=ordered_df["lon"].mean(),
    zoom=12
)

st.pydeck_chart(pdk.Deck(layers=layers, initial_view_state=view))


# ======================================================
# EXPORT
# ======================================================
st.subheader("Download Route Plan")
csv = ordered_df.to_csv(index=False)
st.download_button("Download Routes CSV", csv, "routes.csv")
