import streamlit as st
import pandas as pd
import altair as alt
import os

# ✅ Inject PWA support (manifest + service worker)
st.markdown("""
<script>
window.addEventListener('DOMContentLoaded', function() {
  let link = document.createElement('link');
  link.rel = 'manifest';
  link.href = '/static/manifest.json';
  document.head.appendChild(link);

  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/service-worker.js')
      .then(() => console.log('✅ Service worker registered'))
      .catch(err => console.error('SW registration failed', err));
  }
});
</script>
""", unsafe_allow_html=True)



st.set_page_config(page_title="Language Learning Strategies", layout="centered")

st.title("🧠 Effective Ways to Learn a New Language")

st.write("""
Explore the chart below to see how different language learning strategies are rated for effectiveness.  
Use these insights to build a study plan that fits your preferences and schedule.
""")

# ✅ Data setup
data = pd.DataFrame({
    "Strategy": [
        "Daily Practice",
        "Immersion (Media/Conversation)",
        "Vocabulary Spaced Repetition",
        "Speaking with Natives",
        "Grammar Study",
        "Writing Exercises",
        "Language Apps"
    ],
    "Effectiveness (1-10)": [9, 8, 9, 10, 7, 8, 7]
})

# ✅ Visualization
chart = (
    alt.Chart(data)
    .mark_bar(color="#0a84ff")
    .encode(
        x=alt.X("Strategy", sort="-y"),
        y="Effectiveness (1-10)",
        tooltip=["Strategy", "Effectiveness (1-10)"]
    )
    .properties(height=400)
)

st.altair_chart(chart, use_container_width=True)

# ✅ Learning advice
st.subheader("💡 General Guidance")
st.markdown("""
- **Consistency beats intensity** — short daily sessions are better than occasional long ones.  
- **Speak early**, even if it’s uncomfortable — it accelerates fluency.  
- **Mix passive input** (TV, podcasts) with **active output** (conversation, writing).  
- Use **spaced-repetition tools** (like Anki or Quizlet) for vocabulary.  
- Track your progress — even small wins build long-term motivation.
""")

# ✅ Developer note / testing guidance
with st.expander("🧩 How to Test as a PWA"):
    st.markdown("""
    1. Save `manifest.json` and `service-worker.js` in the same directory as this file.
    2. Run locally:
       ```bash
       streamlit run app.py
       ```
       Then visit **http://localhost:8501**
    3. In Chrome → DevTools → *Application* tab:
       - Check that the **manifest** loads.
       - Verify the **service worker** registers.
    4. Click the install icon in your browser → *Add to Home Screen*.
    5. You can now launch your Streamlit dashboard like a mobile app!
    """)

# ✅ Optional: auto-create basic manifest/service worker (for convenience)
if not os.path.exists("manifest.json"):
    with open("manifest.json", "w") as f:
        f.write('''
{
  "name": "Language Learning Strategies",
  "short_name": "LangLearn",
  "start_url": ".",
  "display": "standalone",
  "background_color": "#000000",
  "theme_color": "#0a84ff",
  "icons": [
    { "src": "app-icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "app-icon-512.png", "sizes": "512x512", "type": "image/png" }
  ]
}
''')

if not os.path.exists("service-worker.js"):
    with open("service-worker.js", "w") as f:
        f.write('''
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open('streamlit-cache-v1').then(cache => {
      return cache.addAll(['/', '/manifest.json']);
    })
  );
});
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request).then(response => response || fetch(event.request))
  );
});
''')
