import streamlit as st

st.set_page_config(page_title="Streamlit → PWA Mobile App Guide", layout="wide")

st.title("📱 Streamlit → Progressive Web App (PWA) Converter Dashboard")

st.markdown("""
Turn any **Streamlit app** into a mobile-friendly **installable web app (PWA)** using a few simple steps.
""")

st.sidebar.header("Choose a Setup Step")
step = st.sidebar.radio(
    "PWA Setup Process",
    ["Overview", "Add manifest.json", "Add service worker", "Deploy", "Install on Mobile"]
)

if step == "Overview":
    st.subheader("🔍 Overview: What You’ll Get")
    st.markdown("""
    With Streamlit + PWA setup:
    - Your app can be **installed** on Android, iOS, or desktop.
    - Works **offline (partially)** if configured right.
    - Uses your **custom icon, splash screen, and name.**

    🧠 PWAs are just web apps with:
    - A `manifest.json` file describing your app’s name, theme, and icons.
    - A `service worker` script for caching/offline capability.
    - HTTPS hosting.

    ⚡ *Perfect for turning Streamlit dashboards into lightweight mobile tools!*
    """)

elif step == "Add manifest.json":
    st.subheader("🧾 Step 1: Add manifest.json")
    st.code("""
    # In your Streamlit app directory, create a file named 'manifest.json'

    {
      "name": "My Streamlit App",
      "short_name": "StreamlitApp",
      "start_url": ".",
      "display": "standalone",
      "background_color": "#000000",
      "theme_color": "#0a84ff",
      "icons": [
        {
          "src": "/app-icon-192.png",
          "sizes": "192x192",
          "type": "image/png"
        },
        {
          "src": "/app-icon-512.png",
          "sizes": "512x512",
          "type": "image/png"
        }
      ]
    }
    """, language="json")
    st.markdown("Place this file in your Streamlit app folder, then serve it using a small custom route if needed (e.g., via `st.markdown()` with a `<link>` tag).")

elif step == "Add service worker":
    st.subheader("⚙️ Step 2: Add a Service Worker")
    st.code("""
    // service-worker.js

    self.addEventListener('install', event => {
      event.waitUntil(
        caches.open('streamlit-cache').then(cache => {
          return cache.addAll([
            '/',
            '/index.html',
            '/manifest.json'
          ]);
        })
      );
    });

    self.addEventListener('fetch', event => {
      event.respondWith(
        caches.match(event.request).then(response => {
          return response || fetch(event.request);
        })
      );
    });
    """, language="javascript")
    st.markdown("Place this in your root directory and register it in your Streamlit HTML (we’ll inject it below).")

elif step == "Deploy":
    st.subheader("🚀 Step 3: Deploy on HTTPS Hosting")
    st.markdown("""
    **Recommended hosts:**
    - **Streamlit Cloud** (default HTTPS)
    - **Vercel** (`streamlit run app.py --server.enableCORS false`)
    - **Render / Netlify** (add your manifest + service worker manually)

    **Then**, inject this snippet into your Streamlit app:
    """)
    st.code("""
    st.markdown('''
    <link rel="manifest" href="/manifest.json">
    <script>
      if ('serviceWorker' in navigator) {
        window.addEventListener('load', function() {
          navigator.serviceWorker.register('/service-worker.js');
        });
      }
    </script>
    ''', unsafe_allow_html=True)
    """, language="python")

elif step == "Install on Mobile":
    st.subheader("📲 Step 4: Installing the PWA")
    st.markdown("""
    Once deployed:
    1. Visit your app on a mobile browser (Chrome, Safari, or Edge).
    2. Tap the **menu (⋮)** or **Share** button.
    3. Choose **"Add to Home Screen"**.
    4. It installs like a native app — with your icon and splash screen.

    ✅ *You’ve now turned your Streamlit app into a mobile-ready PWA!*
    """)

st.divider()
st.success("💡 Tip: For fast prototyping, test PWAs locally using `python -m http.server` and visit http://localhost:8000 on mobile.")
