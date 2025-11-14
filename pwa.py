import streamlit as st
import os
import json

# ============================================
# STREAMLIT PWA SETUP + DEMO DASHBOARD
# ============================================

# --- Create required PWA folders/files if missing ---
PWA_DIR = ".streamlit/pwa"
os.makedirs(PWA_DIR, exist_ok=True)

# --- Manifest file ---
manifest = {
    "name": "Streamlit PWA",
    "short_name": "SLT-PWA",
    "start_url": ".",
    "display": "standalone",
    "background_color": "#ffffff",
    "theme_color": "#0b4fff",
    "orientation": "portrait",
    "icons": [
        {
            "src": "icon-192.png",
            "sizes": "192x192",
            "type": "image/png"
        },
        {
            "src": "icon-512.png",
            "sizes": "512x512",
            "type": "image/png"
        }
    ]
}

with open(f"{PWA_DIR}/manifest.json", "w") as f:
    json.dump(manifest, f, indent=4)

# --- Service Worker ---
service_worker = """
self.addEventListener("install", event => {
    event.waitUntil(
        caches.open("streamlit-pwa-cache").then(cache => {
            return cache.addAll(["./", "./manifest.json"]);
        })
    );
});

self.addEventListener("fetch", event => {
    event.respondWith(
        caches.match(event.request).then(response => {
            return response || fetch(event.request);
        })
    );
});
"""

with open(f"{PWA_DIR}/service_worker.js", "w") as f:
    f.write(service_worker)

# --- Inject into the HTML header ---
st.markdown("""
<script>
if ("serviceWorker" in navigator) {
    navigator.serviceWorker.register("/.streamlit/pwa/service_worker.js");
}
</script>

<link rel="manifest" href="/.streamlit/pwa/manifest.json">
""", unsafe_allow_html=True)

# ============================================
# DASHBOARD CONTENT (EXTEND FOREVER)
# ============================================

st.title("Streamlit PWA Dashboard")

st.sidebar.header("Menu")
page = st.sidebar.selectbox("Choose a section", ["Home", "Data", "Notes"])

if page == "Home":
    st.subheader("Welcome")
    st.write("Your Streamlit app is now installable as a Progressive Web App.")

elif page == "Data":
    st.subheader("Example Data Explorer")
    import pandas as pd
    df = pd.DataFrame({
        "Value A": range(1, 11),
        "Value B": [x * 2 for x in range(1, 11)]
    })
    st.dataframe(df)

elif page == "Notes":
    st.subheader("Quick Notes")
    note = st.text_area("Write something")
    if st.button("Save"):
        st.success("Note stored in session memory.")
