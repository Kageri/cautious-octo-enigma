import streamlit as st
import pandas as pd
import altair as alt
import json, os, shutil

# =========================
# 📁 AUTO-CONFIGURE STATIC FILES
# =========================
STATIC_DIR = os.path.join(os.path.dirname(__file__), ".streamlit", "static")
os.makedirs(STATIC_DIR, exist_ok=True)

# --- manifest.json ---
manifest = {
    "name": "Language Learning Strategies",
    "short_name": "LangLearn",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#000000",
    "theme_color": "#0a84ff",
    "scope": "/",
    "icons": [
        {"src": "app-icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "app-icon-512.png", "sizes": "512x512", "type": "image/png"},
    ],
}
with open(os.path.join(STATIC_DIR, "manifest.json"), "w") as f:
    json.dump(manifest, f, indent=2)

# --- service-worker.js ---
service_worker = """
self.addEventListener('install', e => {
  e.waitUntil(
    caches.open('langlearn-v1').then(cache => cache.addAll(['/']))
  );
});

self.addEventListener('fetch', e => {
  e.respondWith(caches.match(e.request).then(resp => resp || fetch(e.request)));
});
"""
with open(os.path.join(STATIC_DIR, "service-worker.js"), "w") as f:
    f.write(service_worker)

# --- placeholder icons ---
for size in [192, 512]:
    icon_path = os.path.join(STATIC_DIR, f"app-icon-{size}.png")
    if not os.path.exists(icon_path):
        import PIL.Image as Image, PIL.ImageDraw as ImageDraw

        img = Image.new("RGBA", (size, size), (10, 132, 255, 255))
        d = ImageDraw.Draw(img)
        d.text((size // 4, size // 3), "LL", fill=(255, 255, 255, 255))
        img.save(icon_path)

# =========================
# 🌐 INJECT PWA COMPONENTS
# =========================
st.set_page_config(page_title="Language Learning Strategies", layout="centered")

st.markdown(
    """
<script>
document.addEventListener("DOMContentLoaded", function() {
  // attach manifest dynamically so Chrome detects it
  const m = document.createElement('link');
  m.rel = 'manifest';
  m.href = '/static/manifest.json';
  document.head.appendChild(m);

  // register service worker
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('/static/service-worker.js', { scope: '/' })
      .then(r => console.log("✅ Service Worker registered:", r.scope))
      .catch(e => console.error("Service Worker registration failed:", e));
  }

  console.log("📦 Manifest linked:", m.href);
});
</script>
""",
    unsafe_allow_html=True,
)

# =========================
# 📊 MAIN APP CONTENT
# =========================
st.title("🧠 Effective Ways to Learn a New Language")

st.write(
    """
Explore the chart below to see how different language learning strategies are rated for effectiveness.
"""
)

data = pd.DataFrame(
    {
        "Strategy": [
            "Daily Practice",
            "Immersion (Media/Conversation)",
            "Vocabulary Spaced Repetition",
            "Speaking with Natives",
            "Grammar Study",
            "Writing Exercises",
            "Language Apps",
        ],
        "Effectiveness (1-10)": [9, 8, 9, 10, 7, 8, 7],
    }
)

chart = (
    alt.Chart(data)
    .mark_bar(color="#0a84ff")
    .encode(
        x=alt.X("Strategy", sort="-y"),
        y="Effectiveness (1-10)",
        tooltip=["Strategy", "Effectiveness (1-10)"],
    )
    .properties(height=400)
)

st.altair_chart(chart, use_container_width=True)

st.subheader("General Guidance")
st.write(
    """
- Consistency beats intensity — short daily sessions win over long irregular ones.  
- Speak early, even if it feels awkward.  
- Mix passive exposure (movies, music) with active practice (writing, conversation).  
- Use spaced-repetition systems for vocabulary retention.  
- Track your progress so you don't lose momentum.
"""
)
