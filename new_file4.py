import streamlit as st

st.set_page_config(page_title="Quick Mobile App Builder Guide", layout="wide")

st.title("📱 Quick Mobile App Creation Dashboard")

st.markdown("""
This dashboard walks you through the fastest and easiest methods to build mobile apps — whether you want **no-code**, **low-code**, or **full-code** approaches.
""")

st.sidebar.header("Choose Your Approach")
choice = st.sidebar.selectbox(
    "Select your skill level / need:",
    ["No-Code", "Low-Code", "Full-Code (Python/JS)", "Deploying & Testing"]
)

if choice == "No-Code":
    st.subheader("🧩 No-Code App Builders")
    st.markdown("""
    **Best Platforms for Building Mobile Apps Fast:**
    - **Glide** → Build data-driven apps using Google Sheets or Airtable.
    - **Adalo** → Visual drag-and-drop editor with native app publishing.
    - **Thunkable** → Cross-platform apps with visual logic blocks.
    - **Bravo Studio** → Turns Figma designs into working apps.
    - **AppSheet (Google)** → Automate apps from Google Workspace data.

    💡 *Use these if you want working apps in hours without coding.*
    """)

elif choice == "Low-Code":
    st.subheader("⚙️ Low-Code Builders")
    st.markdown("""
    **Best for semi-technical users or quick prototypes:**
    - **FlutterFlow** → Google Flutter-based builder with Firebase integration.
    - **Backendless** → Includes UI builder + backend database + API system.
    - **Draftbit** → Build React Native apps visually.
    - **AppGyver (SAP)** → Strong for enterprise-grade low-code apps.

    🧠 *Combine drag-and-drop UI with some light scripting or API integration.*
    """)

elif choice == "Full-Code (Python/JS)":
    st.subheader("💻 Fast Full-Code Frameworks")
    st.markdown("""
    **1️⃣ Python Routes**
    - **BeeWare** → Build native mobile apps in Python.
    - **Kivy** → Cross-platform mobile apps with Python.
    - **Streamlit + PWA wrapper** → Build Streamlit apps and make them installable via Progressive Web App.

    **2️⃣ JavaScript/TypeScript Routes**
    - **React Native** → Build real native apps using React.
    - **Expo** → Managed React Native platform — perfect for fast deployment.
    - **Ionic + Capacitor** → Hybrid apps using web tech (HTML, CSS, JS).

    ⚡ *Developers prefer these for performance, scalability, and control.*
    """)

elif choice == "Deploying & Testing":
    st.subheader("🚀 Deployment & Testing Tools")
    st.markdown("""
    **To test and ship your app quickly:**
    - **Expo Go** → Test React Native apps instantly.
    - **Firebase App Distribution** → Send test builds to users.
    - **TestFlight (iOS)** → Distribute iOS builds before publishing.
    - **Google Play Internal Testing** → Quick beta testing on Android.
    - **PWA (Progressive Web App)** → Convert your web app into installable mobile app.

    🌍 *For instant access, deploying a web app as a PWA is the fastest option.*
    """)

st.divider()
st.info("💬 Tip: For fastest real-world app → design in Figma → import into Bravo Studio → connect APIs → publish to store in hours.")
