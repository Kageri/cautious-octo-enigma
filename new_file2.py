
# app.py
"""
Language Learner — Streamlit web app
A single-file app that helps you pick a study plan, track sessions,
manage simple spaced-repetition vocab items, and visualize progress.

Run:
    streamlit run app.py
"""

from datetime import datetime, timedelta, date
import time
import uuid
import io

import streamlit as st
import pandas as pd
import altair as alt

# ---------------------------
# Helpers / Simple SRS Model
# ---------------------------
def now():
    return datetime.utcnow()

def make_vocab_df():
    # Minimal columns for SRS: id, word, meaning, box (1..5), last_review, next_review
    return pd.DataFrame(
        columns=[
            "id",
            "word",
            "meaning",
            "box",
            "last_review",
            "next_review",
            "times_reviewed",
        ]
    )

def schedule_next_review(box, from_dt):
    # Simple Leitner box schedule (days until next review)
    spacing = {1: 1, 2: 2, 3: 5, 4: 14, 5: 60}
    days = spacing.get(int(box), 1)
    return (from_dt + timedelta(days=days)).date()

def add_vocab_item(df, word, meaning):
    uid = str(uuid.uuid4())[:8]
    row = {
        "id": uid,
        "word": word.strip(),
        "meaning": meaning.strip(),
        "box": 1,
        "last_review": pd.NaT,
        "next_review": (date.today() + timedelta(days=1)),
        "times_reviewed": 0,
    }
    return pd.concat([df, pd.DataFrame([row])], ignore_index=True)

def review_item(row, succeeded: bool):
    # move up if succeeded else move down
    box = int(row["box"])
    if succeeded:
        box = min(5, box + 1)
    else:
        box = max(1, box - 1)
    row["box"] = box
    row["last_review"] = date.today()
    row["next_review"] = schedule_next_review(box, datetime.utcnow())
    row["times_reviewed"] = int(row.get("times_reviewed", 0)) + 1
    return row

# ---------------------------
# Streamlit UI
# ---------------------------
st.set_page_config(page_title="Language Learner", layout="wide")
st.title("🌍 Language Learner — smart study planner & tracker")

# Sidebar: user settings
with st.sidebar:
    st.header("Study Settings")
    language = st.text_input("Target language", value="Spanish")
    goal = st.selectbox("Goal / Focus", ["Conversational fluency", "Travel basics", "Reading & Writing", "Grammar mastery"], index=0)
    target_level = st.selectbox("Target level (CEFR-ish)", ["A1 (Beginner)", "A2", "B1", "B2", "C1", "C2"], index=2)
    daily_minutes = st.slider("Daily study time (minutes)", 5, 180, 30)
    start_date = st.date_input("Plan start date", value=date.today())
    st.markdown("---")
    st.subheader("Methods to include")
    methods = {
        "Daily Practice (short sessions)": st.checkbox("Daily short sessions", True),
        "Immersion (media & listening)": st.checkbox("Immersion — movies/music", True),
        "SRS Vocabulary": st.checkbox("Spaced repetition (vocab)", True),
        "Conversation practice": st.checkbox("Speaking with natives / tutors", True),
        "Grammar & exercises": st.checkbox("Structured grammar study", True),
        "Writing practice": st.checkbox("Writing & journaling", False),
        "Language app / flashcards": st.checkbox("Language apps", True),
    }
    st.markdown("---")
    if st.button("Generate study plan"):
        st.session_state["plan_generated_at"] = datetime.utcnow().isoformat()

# Initialize session state objects
if "vocab_df" not in st.session_state:
    st.session_state["vocab_df"] = make_vocab_df()

if "sessions" not in st.session_state:
    # list of practice sessions: dicts with start, end, minutes, type
    st.session_state["sessions"] = []

if "plan_generated_at" not in st.session_state:
    st.session_state["plan_generated_at"] = None

# Main columns
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("1) Weekly Plan & Quick Actions")
    # Create a simple plan for 7 days based on daily_minutes and methods
    def make_week_plan(start, daily_minutes, methods):
        days = []
        for i in range(7):
            d = start + timedelta(days=i)
            items = []
            # allocate minutes proportionally by method weight
            base = daily_minutes
            if methods["Daily Practice (short sessions)"]:
                items.append(("Practice session", int(base * 0.35)))
            if methods["Immersion (media & listening)"]:
                items.append(("Immersion", int(base * 0.25)))
            if methods["SRS Vocabulary"]:
                items.append(("SRS vocab", int(base * 0.15)))
            if methods["Conversation practice"]:
                items.append(("Speaking", int(base * 0.10)))
            if methods["Grammar & exercises"]:
                items.append(("Grammar", int(base * 0.10)))
            if not items:
                items.append(("Free study", base))
            days.append({"date": d, "tasks": items})
        return days

    week_plan = make_week_plan(start_date, daily_minutes, methods)
    # Flatten for display/chart
    plan_rows = []
    for day in week_plan:
        for task, mins in day["tasks"]:
            plan_rows.append({"date": day["date"], "task": task, "minutes": mins})
    plan_df = pd.DataFrame(plan_rows)

    st.markdown("**Weekly schedule**")
    st.dataframe(plan_df.sort_values(["date", "minutes"], ascending=[True, False]).reset_index(drop=True), height=220)

    st.markdown("**Visual: time allocation this week**")
    chart = (
        alt.Chart(plan_df)
        .mark_bar()
        .encode(
            x=alt.X("date:T", title="Date"),
            y=alt.Y("sum(minutes):Q", title="Minutes"),
            color="task:N",
            tooltip=["date", "task", "minutes"],
        )
        .properties(height=250)
    )
    st.altair_chart(chart, use_container_width=True)

    # Quick session recorder
    st.markdown("**Start/Stop a practice session**")
    session_type = st.selectbox("Session type", ["Practice session", "SRS vocab", "Immersion", "Speaking", "Grammar", "Writing"])
    if "current_session" not in st.session_state:
        st.session_state.current_session = None

    start_btn, stop_btn = st.columns([1, 1])
    with start_btn:
        if st.button("Start session ⏱️"):
            if st.session_state.current_session is None:
                st.session_state.current_session = {"start": now(), "type": session_type}
                st.success(f"Session started: {session_type} — {st.session_state.current_session['start'].strftime('%H:%M:%S UTC')}")
            else:
                st.warning("A session is already running. Stop it first.")
    with stop_btn:
        if st.button("Stop session ⏹️"):
            if st.session_state.current_session is not None:
                cur = st.session_state.current_session
                cur["end"] = now()
                elapsed = (cur["end"] - cur["start"]).total_seconds() / 60.0
                cur["minutes"] = round(elapsed, 1)
                cur["date"] = cur["start"].date().isoformat()
                st.session_state.sessions.append(cur)
                st.session_state.current_session = None
                st.success(f"Stopped — {cur['minutes']} minutes recorded.")
            else:
                st.warning("No running session to stop.")

    # Show recent sessions
    st.markdown("**Recent sessions**")
    sess_df = pd.DataFrame(st.session_state.sessions)
    if not sess_df.empty:
        st.dataframe(sess_df.sort_values("start", ascending=False).head(10))
    else:
        st.info("No practice sessions recorded yet — start one above.")

with col2:
    st.subheader("2) Spaced-Repetition Vocab (SRS)")
    st.markdown("Add vocabulary items, review items due today, export/import your deck.")
    vocab_df = st.session_state.vocab_df.copy()

    # Upload / Import
    uploaded = st.file_uploader("Upload CSV to import vocab (columns: word,meaning,box,last_review,next_review)", type=["csv"])
    if uploaded is not None:
        try:
            incoming = pd.read_csv(uploaded)
            # Normalize
            if "word" in incoming.columns and "meaning" in incoming.columns:
                # Fill missing optional columns
                for c in ["box", "last_review", "next_review", "times_reviewed"]:
                    if c not in incoming.columns:
                        incoming[c] = None
                # convert dates where possible
                if incoming.get("next_review") is not None:
                    try:
                        incoming["next_review"] = pd.to_datetime(incoming["next_review"]).dt.date
                    except Exception:
                        pass
                incoming["id"] = incoming.get("id", [str(uuid.uuid4())[:8] for _ in range(len(incoming))])
                st.session_state.vocab_df = pd.concat([st.session_state.vocab_df, incoming[list(vocab_df.columns)]], ignore_index=True)
                st.success(f"Imported {len(incoming)} items.")
            else:
                st.error("CSV must contain 'word' and 'meaning' columns.")
        except Exception as e:
            st.error(f"Couldn't import: {e}")

    # Manual add
    with st.form("add_vocab"):
        w = st.text_input("Word / phrase", "")
        m = st.text_input("Meaning / translation", "")
        submitted = st.form_submit_button("Add to deck")
        if submitted:
            if w.strip() == "":
                st.error("Enter a word or phrase.")
            else:
                st.session_state.vocab_df = add_vocab_item(st.session_state.vocab_df, w, m)
                st.success(f"Added: {w}")

    st.markdown("**Deck overview**")
    if st.session_state.vocab_df.empty:
        st.info("No vocab yet — add some words or upload a CSV.")
    else:
        df_show = st.session_state.vocab_df.copy()
        df_show["next_review"] = pd.to_datetime(df_show["next_review"]).dt.date
        st.dataframe(df_show.sort_values(["next_review", "box"]).reset_index(drop=True).head(250), height=220)

    # Items due for review today
    st.markdown("**Review items due today**")
    if not st.session_state.vocab_df.empty and methods["SRS Vocabulary"]:
        today = date.today()
        due_mask = pd.to_datetime(st.session_state.vocab_df["next_review"]).dt.date <= today
        due = st.session_state.vocab_df.loc[due_mask].copy()
        if due.empty:
            st.success("No items due today. Nice!")
        else:
            st.write(f"{len(due)} item(s) due for review")
            # Show interactive one-by-one review
            idxs = list(due.index)
            if "review_index" not in st.session_state:
                st.session_state.review_index = 0
            if st.session_state.review_index >= len(idxs):
                st.session_state.review_index = 0

            if idxs:
                i = idxs[st.session_state.review_index]
                item = st.session_state.vocab_df.loc[i]
                st.markdown(f"**{item['word']}** — *{item.get('meaning','')}*")
                col_yes, col_no, col_skip = st.columns([1, 1, 1])
                with col_yes:
                    if st.button("I remembered ✅"):
                        st.session_state.vocab_df.loc[i] = review_item(st.session_state.vocab_df.loc[i], True)
                        st.session_state.review_index = min(st.session_state.review_index + 1, len(idxs)-1)
                with col_no:
                    if st.button("I forgot ❌"):
                        st.session_state.vocab_df.loc[i] = review_item(st.session_state.vocab_df.loc[i], False)
                        st.session_state.review_index = min(st.session_state.review_index + 1, len(idxs)-1)
                with col_skip:
                    if st.button("Skip / Later"):
                        st.session_state.review_index = min(st.session_state.review_index + 1, len(idxs)-1)
            else:
                st.write("No due items to review.")

    # Export deck
    st.markdown("---")
    st.write("Export your deck:")
    if not st.session_state.vocab_df.empty:
        csv = st.session_state.vocab_df.to_csv(index=False)
        st.download_button("Download CSV", csv, file_name=f"{language}_vocab_deck.csv", mime="text/csv")
    else:
        st.info("Add vocab to enable export.")

# Footer area with progress visualization
st.markdown("---")
st.subheader("Progress & Analytics")

# Simple analytics: daily minutes last 14 days
if st.session_state.sessions:
    sess_df = pd.DataFrame(st.session_state.sessions)
    sess_df["date"] = pd.to_datetime(sess_df["date"]).dt.date
    summary = sess_df.groupby("date")["minutes"].sum().reset_index()
    # Fill last 14 days
    last_14 = [date.today() - timedelta(days=i) for i in range(13, -1, -1)]
    summary_full = pd.DataFrame({"date": last_14})
    summary_full = summary_full.merge(summary, on="date", how="left").fillna(0)
    chart2 = (
        alt.Chart(summary_full)
        .mark_area(opacity=0.5)
        .encode(x="date:T", y="minutes:Q", tooltip=["date", "minutes"])
        .properties(height=200)
    )
    st.altair_chart(chart2, use_container_width=True)
    avg = summary_full["minutes"].mean()
    st.write(f"Average minutes/day (last 14 days): **{avg:.1f}**")
else:
    st.info("Record practice sessions to see progress charts.")

# Study tips and personalized plan notes
st.markdown("---")
st.subheader("Tips & Next Steps")
st.markdown(
    """
- **Consistency > intensity**: short daily sessions (15–45 min) beat irregular marathon sessions.  
- **Speak early**: use language exchanges or short tutor sessions to build speaking confidence.  
- **Mix passive + active**: listen to media and follow with active tasks (write a summary, repeat aloud).  
- **SRS + Context**: learn vocab with spaced repetition, *and* practice those words in sentences.  
- **Track & iterate**: use the session recorder above and tweak your daily minutes and methods if you miss goals.
"""
)

# Small "save workspace" / snapshot
st.markdown("---")
col_a, col_b = st.columns([1, 1])
with col_a:
    if st.button("Save snapshot (download workspace)"):
        obj = {
            "vocab": st.session_state.vocab_df.to_csv(index=False),
            "sessions": pd.DataFrame(st.session_state.sessions).to_csv(index=False),
            "plan_generated_at": st.session_state.plan_generated_at,
        }
        buf = io.BytesIO()
        # create a simple zip-like text bundle (CSVs separated)
        content = f"---VOCAB.CSV---\n{obj['vocab']}\n---SESSIONS.CSV---\n{obj['sessions']}"
        buf.write(content.encode("utf-8"))
        buf.seek(0)
        st.download_button("Download workspace snapshot", data=buf, file_name=f"language_workspace_{language}.txt", mime="text/plain")

with col_b:
    if st.button("Reset app data (clear sessions & vocab)"):
        st.session_state.vocab_df = make_vocab_df()
        st.session_state.sessions = []
        st.success("Cleared vocab and sessions.")

# Final note
st.markdown(
    """
---

**How to use this app effectively:**  
1. Enter your language and target daily minutes in the sidebar.  
2. Add 20–50 core words/phrases to the SRS and review daily.  
3. Use the Start/Stop session buttons to record study time — watch the progress charts.  
4. Iterate weekly: increase speaking, adjust daily minutes, and import/export your deck.
"""
)
