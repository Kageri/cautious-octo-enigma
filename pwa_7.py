import streamlit as st

st.set_page_config(page_title="Local PWA Testing Guide", layout="wide")

st.title("🧪 How to Test Your Streamlit PWA Locally")

st.markdown("""
Here’s exactly how to test your **Streamlit Progressive Web App (PWA)** on your own computer or mobile device before you deploy it.
""")

st.sidebar.header("Choose Platform")
platform = st.sidebar.radio(
    "Testing Environment:",
    ["Desktop (Localhost)", "Mobile (Same Wi-Fi Network)", "Docker Sandbox"]
)

if platform == "Desktop (Localhost)":
    st.subheader("💻 Testing on Your Desktop")
    st.markdown("""
    Follow these steps to simulate hosting your PWA:

    1. **Make sure your folder looks like this:**
       ```
       /my_app/
       ├── app.py
       ├── manifest.json
       ├── service-worker.js
       ├── app-icon-192.png
       ├── app-icon-512.png
       ```

    2. **Run Streamlit locally:**
       ```bash
       streamlit run app.py
       ```

       This usually launches your app on:
       ```
       http://localhost:8501
       ```

    3. **Add your PWA files to the Streamlit HTML:**
       ```python
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
       ```

    4. **Open DevTools → Application → Manifest**  
       Confirm that your `manifest.json` and icons load without 404 errors.

    5. **Test Installation**
       - Open the site in **Chrome or Edge**.
       - Click the **install icon (📲)** in the address bar.
       - Your Streamlit app now behaves like a native desktop app.
    """)

elif platform == "Mobile (Same Wi-Fi Network)":
    st.subheader("📱 Testing on Your Phone")
    st.markdown("""
    You can access your local Streamlit app from your phone on the same network.

    1. **Find your local IP address:**
       ```bash
       ipconfig   # Windows
       ifconfig   # macOS/Linux
       ```
       Example: `192.168.1.22`

    2. **Run Streamlit binding to all interfaces:**
       ```bash
       streamlit run app.py --server.address 0.0.0.0
       ```

    3. **On your phone’s browser**, visit:
       ```
       http://192.168.1.22:8501
       ```

    4. If the manifest and service worker load correctly, your phone browser will prompt:
       > “Add to Home Screen”

       Once installed, it appears like a native mobile app!
    """)

elif platform == "Docker Sandbox":
    st.subheader("🐳 Testing Inside Docker")
    st.markdown("""
    1. **Create a Dockerfile**
       ```dockerfile
       FROM python:3.10
       WORKDIR /app
       COPY . .
       RUN pip install streamlit
       EXPOSE 8501
       CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
       ```

    2. **Build and run**
       ```bash
       docker build -t streamlit-pwa .
       docker run -p 8501:8501 streamlit-pwa
       ```

    3. **Access locally**
       ```
       http://localhost:8501
       ```

    4. **Test PWA install and cache behavior** the same as normal.
    """)

st.divider()
st.info("""
✅ **Summary:**
- You can fully test PWA behavior (install prompt, manifest loading, offline cache) on `localhost` or local IP.  
- HTTPS is not required for `localhost`.  
- Use Chrome → DevTools → *Application → Service Workers* to inspect and refresh cached files.
""")
