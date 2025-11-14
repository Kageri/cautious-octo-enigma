import streamlit as st

st.set_page_config(page_title="Test Streamlit PWAs Locally", layout="wide")

st.title("🧪 Local Testing Dashboard for Streamlit PWAs")

st.markdown("""
Here’s a full guide to testing your **Streamlit Progressive Web App (PWA)** locally — verifying installation, caching, and offline behavior before deployment.
""")

st.sidebar.header("Choose Testing Stage")
stage = st.sidebar.radio(
    "Testing Stages",
    ["1️⃣ Setup Local Server", "2️⃣ Add HTTPS (Optional)", "3️⃣ Test Installation", "4️⃣ Test Offline Mode", "5️⃣ Debugging Tips"]
)

if stage == "1️⃣ Setup Local Server":
    st.subheader("🧰 Step 1: Run a Local Web Server")
    st.markdown("""
    PWAs require being served over HTTP(S), not opened from local file paths.  
    You can simulate hosting easily with a Python server.
    """)

    st.code("""
    # From your app directory (where manifest.json and service-worker.js are)
    python -m http.server 8000
    """, language="bash")

    st.markdown("""
    Then open your browser at:
    ```
    http://localhost:8000
    ```
    Your `manifest.json` and `service-worker.js` should load without errors.
    """)

    st.info("If you’re testing a Streamlit app, run it on another port (e.g., 8501) and ensure the manifest and service worker paths match the app’s structure.")

elif stage == "2️⃣ Add HTTPS (Optional)":
    st.subheader("🔐 Step 2: Add HTTPS Locally (Optional)")
    st.markdown("""
    While `localhost` is allowed for PWA testing even without HTTPS,  
    you can add a **secure local server** for more realistic testing using:
    """)

    st.code("""
    # Install local HTTPS dev server
    npm install -g local-web-server
    ws --https
    """, language="bash")

    st.markdown("""
    This creates a self-signed HTTPS server so you can test PWA install prompts and push notifications.
    Visit:
    ```
    https://localhost:8000
    ```
    """)

elif stage == "3️⃣ Test Installation":
    st.subheader("📲 Step 3: Install the App Locally")
    st.markdown("""
    Once your app runs on `localhost`:
    1. Open **Chrome** or **Edge**.
    2. Go to **http://localhost:8501** (your Streamlit app).
    3. Check the **address bar** → a small **‘Install App’ icon** should appear.
    4. Click it → choose **Install**.

    ✅ This installs the app like a native mobile or desktop app.
    """)

    st.image("https://developers.google.com/web/updates/images/2018/06/a2hs-icon.png", caption="Install prompt example")

elif stage == "4️⃣ Test Offline Mode":
    st.subheader("📴 Step 4: Simulate Offline Behavior")
    st.markdown("""
    1. Open **Chrome DevTools → Application → Service Workers**.
    2. Check **'Offline'** mode under the Network tab.
    3. Reload your app.

    If your service worker was set up correctly:
    - Cached pages load from local storage.
    - Your app still opens without network.
    - Dynamic API calls will fail (expected).

    🧠 **Tip:** Make sure your service worker’s `cache.addAll()` includes your Streamlit pages and assets.
    """)

elif stage == "5️⃣ Debugging Tips":
    st.subheader("🪲 Step 5: Debug Common Issues")
    st.markdown("""
    **Manifest not loading?**
    - Check your browser console → it must be served under the same domain as your app.
    - Use:  
      ```html
      <link rel="manifest" href="/manifest.json">
      ```

    **Service Worker not registering?**
    - Ensure you have HTTPS or localhost.
    - Verify this script runs inside your Streamlit template:
      ```python
      st.markdown('''
      <script>
        if ('serviceWorker' in navigator) {
          navigator.serviceWorker.register('/service-worker.js');
        }
      </script>
      ''', unsafe_allow_html=True)
      ```

    **Cache not updating?**
    - Change the service worker cache name (e.g., `streamlit-cache-v2`).
    - Unregister old workers via Chrome DevTools → Application → Service Workers.

    🧩 Use Chrome DevTools → *Application → Manifest* to validate icon sizes, colors, and metadata.
    """)

st.divider()
st.success("💡 Quick Recap: localhost testing works fine for PWAs — HTTPS is optional there, but required for live deployment.")
