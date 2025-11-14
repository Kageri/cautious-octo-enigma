# app.py
import os
from datetime import datetime, timedelta
from dateutil import parser

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine


from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    create_engine,
    Text,
    Boolean,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session

# Calendar import (FullCalendar wrapper)
from streamlit_calendar import calendar

# ---------- CONFIG ----------
st.set_page_config(page_title="Dog Walk Manager", page_icon="🐕", layout="wide")

DB_USER = os.getenv("DB_USER", "streamlit_user")
DB_PASS = os.getenv("DB_PASS", "mypassword")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "pet_care")


# If running locally without env vars, fallback to sqlite for dev convenience:
USE_SQLITE_FALLBACK = False
if not (DB_USER and DB_PASS and DB_HOST and DB_NAME):
    # Try fallback to sqlite if explicitly set; otherwise require DB config.
    if os.getenv("FALLBACK_TO_SQLITE", "0") == "1":
        USE_SQLITE_FALLBACK = True
        DB_URL = "sqlite:///dogwalk.db"
    else:
        # If not set, we'll still build a connection string but it'll fail if unreachable.
        DB_URL = None
else:
    DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

if USE_SQLITE_FALLBACK:
    st.info("Using local SQLite fallback database (FALLBACK_TO_SQLITE=1).")
elif DB_URL is None:
    st.warning(
        "No DB configuration found. For local dev you can set FALLBACK_TO_SQLITE=1 or set DB_* env vars."
    )

# ---------- DATABASE SETUP ----------
Base = declarative_base()
engine = create_engine("mysql+pymysql://streamlit_user:mypassword@localhost:3306/pet_care")
Base.metadata.create_all(engine, checkfirst=True)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    name = Column(String(128))
    password_hash = Column(String(256))
    role = Column(String(32))  # 'client' or 'walker'
    active = Column(Boolean, default=True)

class Owner(Base):
    __tablename__ = "owners"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    phone = Column(String(64))
    email = Column(String(128))
    address = Column(String(256))
    notes = Column(Text)

    dogs = relationship("Dog", back_populates="owner", cascade="all, delete-orphan")

class Dog(Base):
    __tablename__ = "dogs"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    breed = Column(String(128))
    age = Column(String(64))
    notes = Column(Text)
    owner_id = Column(Integer, ForeignKey("owners.id"))

    owner = relationship("Owner", back_populates="dogs")

class Walker(Base):
    __tablename__ = "walkers"
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    phone = Column(String(64))
    email = Column(String(128))
    notes = Column(Text)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Link to auth user

class Assignment(Base):
    __tablename__ = "assignments"
    id = Column(Integer, primary_key=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"))
    walker_id = Column(Integer, ForeignKey("walkers.id"))

    dog = relationship("Dog")
    walker = relationship("Walker")

class Schedule(Base):
    __tablename__ = "schedules"
    id = Column(Integer, primary_key=True)
    dog_id = Column(Integer, ForeignKey("dogs.id"))
    walker_id = Column(Integer, ForeignKey("walkers.id"))
    start_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, default=30)
    notes = Column(Text, default="")

    dog = relationship("Dog")
    walker = relationship("Walker")

class WalkNote(Base):
    __tablename__ = "walk_notes"
    id = Column(Integer, primary_key=True)
    schedule_id = Column(Integer, ForeignKey("schedules.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    content = Column(Text)
    author = Column(String(128))  # username or display name

    schedule = relationship("Schedule")

def get_engine():
    if USE_SQLITE_FALLBACK:
        return create_engine("sqlite:///dogwalk.db", connect_args={"check_same_thread": False})
    if DB_URL:
        return create_engine(DB_URL, pool_pre_ping=True)
    raise RuntimeError("Database URL not configured. Set DB_* environment variables or set FALLBACK_TO_SQLITE=1")



Session = scoped_session(sessionmaker(bind=engine))
Base.metadata.create_all(engine)


# ---------- HELPERS ----------
def create_user(username, password, name, role="walker"):
    session = Session()
    if session.query(User).filter_by(username=username).first():
        session.close()
        return False
    user = User(username=username, name=name, password_hash=generate_password_hash(password), role=role)
    session.add(user)
    session.commit()
    session.close()
    return True

def authenticate(username, password):
    session = Session()
    u = session.query(User).filter_by(username=username).first()
    session.close()
    if not u:
        return None
    if check_password_hash(u.password_hash, password):
        return {"username": u.username, "name": u.name, "role": u.role, "id": u.id}
    return None

def get_user_by_username(username):
    session = Session()
    u = session.query(User).filter_by(username=username).first()
    session.close()
    return u

# ---------- BOOTSTRAP: create an initial client user if none ----------
def bootstrap_client():
    session = Session()
    c = session.query(User).filter_by(role="client").first()
    if not c:
        # default admin account
        username = os.getenv("BOOTSTRAP_CLIENT_USER", "client")
        password = os.getenv("BOOTSTRAP_CLIENT_PASS", "client123")
        create_user(username, password, "Client Admin", role="client")
        st.info(f"Created bootstrap client user: {username} (change password after).")
    session.close()

bootstrap_client()

# ---------- AUTH UI ----------
st.sidebar.title("Login")
if "auth" not in st.session_state:
    st.session_state.auth = None
if "user" not in st.session_state:
    st.session_state.user = None

def do_login():
    username = st.session_state.login_username.strip()
    password = st.session_state.login_password
    user = authenticate(username, password)
    if user:
        st.session_state.auth = True
        st.session_state.user = user
        st.experimental_rerun()
    else:
        st.session_state.auth = False
        st.sidebar.error("Invalid username or password.")

with st.sidebar.form("login_form"):
    st.text_input("Username", key="login_username")
    st.text_input("Password", type="password", key="login_password")
    submitted = st.form_submit_button("Login", on_click=None)
    if submitted:
        do_login()

if not st.session_state.user:
    st.sidebar.info("If you don't have an account, please ask the client admin to create one.")
    st.stop()

# ---------- MAIN APP (role-based) ----------
user = st.session_state.user
st.sidebar.markdown(f"**Logged in as:** {user['name']} ({user['username']}) — {user['role']}")
st.sidebar.button("Logout", on_click=lambda: st.session_state.clear())

# ---- Shared DB session for the request ----
db = Session()

# ---------- CLIENT (ADMIN) DASHBOARD ----------
def client_dashboard():
    st.title("Client Admin Dashboard")
    tabs = st.tabs(["Owners", "Dogs", "Walkers", "Assignments", "Schedules", "Users"])
    # --- Owners tab ---
    with tabs[0]:
        st.header("Owners (Clients)")
        owners = pd.read_sql(db.query(Owner).statement, db.bind)
        st.dataframe(owners)
        with st.expander("Add / Edit Owner"):
            with st.form("owner_form"):
                owner_id = st.number_input("Owner ID (leave 0 for new)", min_value=0, value=0)
                name = st.text_input("Name")
                phone = st.text_input("Phone")
                email = st.text_input("Email")
                address = st.text_input("Address")
                notes = st.text_area("Notes")
                save = st.form_submit_button("Save Owner")
                if save:
                    if owner_id == 0:
                        o = Owner(name=name, phone=phone, email=email, address=address, notes=notes)
                        db.add(o)
                    else:
                        o = db.query(Owner).get(owner_id)
                        if o:
                            o.name = name
                            o.phone = phone
                            o.email = email
                            o.address = address
                            o.notes = notes
                    db.commit()
                    st.success("Owner saved.")
                    st.experimental_rerun()

    # --- Dogs tab ---
    with tabs[1]:
        st.header("Dogs")
        dogs = pd.read_sql(db.query(Dog).statement, db.bind)
        st.dataframe(dogs)
        with st.expander("Add / Edit Dog"):
            with st.form("dog_form"):
                dog_id = st.number_input("Dog ID (0 to create)", min_value=0, value=0)
                name = st.text_input("Name", key="dog_name")
                breed = st.text_input("Breed")
                age = st.text_input("Age")
                owner_options = {o.id: o.name for o in db.query(Owner).all()}
                owner_id = st.selectbox("Owner", options=[0] + list(owner_options.keys()), format_func=lambda x: "None" if x==0 else owner_options.get(x))
                notes = st.text_area("Notes")
                save = st.form_submit_button("Save Dog")
                if save:
                    if dog_id == 0:
                        d = Dog(name=name, breed=breed, age=age, owner_id=(owner_id if owner_id != 0 else None), notes=notes)
                        db.add(d)
                    else:
                        d = db.query(Dog).get(dog_id)
                        if d:
                            d.name = name
                            d.breed = breed
                            d.age = age
                            d.owner_id = (owner_id if owner_id != 0 else None)
                            d.notes = notes
                    db.commit()
                    st.success("Dog saved.")
                    st.experimental_rerun()

    # --- Walkers tab ---
    with tabs[2]:
        st.header("Walkers")
        walkers = pd.read_sql(db.query(Walker).statement, db.bind)
        st.dataframe(walkers)
        with st.expander("Add / Edit Walker"):
            with st.form("walker_form"):
                walker_id = st.number_input("Walker ID (0 to create)", min_value=0, value=0)
                name = st.text_input("Name", key="walker_name")
                phone = st.text_input("Phone")
                email = st.text_input("Email")
                notes = st.text_area("Notes")
                link_user = st.selectbox("Link to user account (optional)", options=[0] + [u.id for u in db.query(User).all()])
                save = st.form_submit_button("Save Walker")
                if save:
                    if walker_id == 0:
                        w = Walker(name=name, phone=phone, email=email, notes=notes, user_id=(link_user if link_user != 0 else None))
                        db.add(w)
                    else:
                        w = db.query(Walker).get(walker_id)
                        if w:
                            w.name = name
                            w.phone = phone
                            w.email = email
                            w.notes = notes
                            w.user_id = (link_user if link_user != 0 else None)
                    db.commit()
                    st.success("Walker saved.")
                    st.experimental_rerun()

    # --- Assignments tab ---
    with tabs[3]:
        st.header("Assign Dogs to Walkers")
        dogs_list = db.query(Dog).all()
        walkers_list = db.query(Walker).all()
        dog_map = {d.id: f"{d.name} (owner: {d.owner.name if d.owner else '—'})" for d in dogs_list}
        walker_map = {w.id: w.name for w in walkers_list}
        st.write("Current assignments:")
        assign_df = pd.read_sql(db.query(Assignment).join(Dog).join(Walker).statement, db.bind)
        if not assign_df.empty:
            st.dataframe(assign_df)
        else:
            st.write("No assignments yet.")
        with st.form("assign_form"):
            dog_choice = st.selectbox("Dog", options=[0]+list(dog_map.keys()), format_func=lambda x: "Select..." if x==0 else dog_map.get(x))
            walker_choice = st.selectbox("Walker", options=[0]+list(walker_map.keys()), format_func=lambda x: "Select..." if x==0 else walker_map.get(x))
            add_assign = st.form_submit_button("Assign")
            if add_assign:
                if dog_choice == 0 or walker_choice == 0:
                    st.error("Choose both a dog and a walker.")
                else:
                    # avoid duplicate
                    existing = db.query(Assignment).filter_by(dog_id=dog_choice, walker_id=walker_choice).first()
                    if existing:
                        st.warning("This assignment already exists.")
                    else:
                        a = Assignment(dog_id=dog_choice, walker_id=walker_choice)
                        db.add(a)
                        db.commit()
                        st.success("Assigned.")
                        st.experimental_rerun()
        # option to delete assignment
        with st.expander("Remove an assignment"):
            assignment_options = {a.id: f"{a.dog.name} → {a.walker.name}" for a in db.query(Assignment).all()}
            if assignment_options:
                to_remove = st.selectbox("Assignment", options=list(assignment_options.keys()), format_func=lambda x: assignment_options[x])
                if st.button("Remove selected assignment"):
                    db.query(Assignment).filter_by(id=to_remove).delete()
                    db.commit()
                    st.success("Removed.")
                    st.experimental_rerun()
            else:
                st.write("No assignments to remove.")

    # --- Schedules tab ---
    with tabs[4]:
        st.header("Schedules")
        schedules_df = pd.read_sql(db.query(Schedule).statement, db.bind)
        # join dog/walker names
        if not schedules_df.empty:
            # display times nicely
            st.dataframe(schedules_df)
        else:
            st.write("No scheduled walks yet.")
        with st.expander("Create a schedule entry"):
            with st.form("schedule_form"):
                dog_opts = {d.id: d.name for d in db.query(Dog).all()}
                walker_opts = {w.id: w.name for w in db.query(Walker).all()}
                dog_sel = st.selectbox("Dog", options=list(dog_opts.keys()), format_func=lambda x: dog_opts[x])
                walker_sel = st.selectbox("Walker", options=list(walker_opts.keys()), format_func=lambda x: walker_opts[x])
                start = st.text_input("Start (YYYY-MM-DD HH:MM) e.g. 2025-11-06 15:30")
                duration = st.number_input("Duration (minutes)", min_value=5, value=30)
                ssave = st.form_submit_button("Create schedule")
                if ssave:
                    try:
                        start_dt = parser.parse(start)
                        sch = Schedule(dog_id=dog_sel, walker_id=walker_sel, start_time=start_dt, duration_minutes=duration)
                        db.add(sch)
                        db.commit()
                        st.success("Schedule created.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Invalid start time: {e}")

    # --- Users tab (create simple users) ---
    with tabs[5]:
        st.header("User Accounts")
        users = pd.read_sql(db.query(User).statement, db.bind)
        st.dataframe(users[["id", "username", "name", "role", "active"]])
        with st.expander("Create user"):
            with st.form("create_user_form"):
                uname = st.text_input("Username")
                pname = st.text_input("Display name")
                pw = st.text_input("Password", type="password")
                role = st.selectbox("Role", options=["walker", "client"])
                create = st.form_submit_button("Create user")
                if create:
                    if not uname or not pw:
                        st.error("Provide username and password.")
                    else:
                        created = create_user(uname, pw, pname, role=role)
                        if created:
                            st.success("User created.")
                            st.experimental_rerun()
                        else:
                            st.error("Username already exists.")

# ---------- WALKER (USER) DASHBOARD ----------
def walker_dashboard(user):
    st.title("Walker Dashboard")
    st.subheader(f"Welcome, {user['name']}")

    # get walker linked to this auth user if any
    walker = db.query(Walker).filter_by(user_id=user["id"]).first()
    if not walker:
        st.warning("Your account is not linked to a Walker profile. Contact admin to link.")
        st.stop()

    # show assigned dogs (via assignments)
    assignments = db.query(Assignment).filter_by(walker_id=walker.id).all()
    dog_rows = []
    for a in assignments:
        dog = db.query(Dog).get(a.dog_id)
        dog_rows.append({"id": dog.id, "name": dog.name, "breed": dog.breed, "owner": dog.owner.name if dog.owner else ""})
    if dog_rows:
        st.subheader("Assigned Dogs")
        st.table(pd.DataFrame(dog_rows))
    else:
        st.info("No dogs assigned yet.")

    # show upcoming schedule for this walker
    st.subheader("My Schedule (upcoming 30 days)")
    now = datetime.utcnow()
    upcoming = db.query(Schedule).filter(Schedule.walker_id==walker.id, Schedule.start_time >= now).order_by(Schedule.start_time).all()
    schedule_rows = []
    events = []
    for s in upcoming:
        dog = db.query(Dog).get(s.dog_id)
        schedule_rows.append({
            "id": s.id,
            "dog": dog.name if dog else "—",
            "start_time": s.start_time,
            "duration_minutes": s.duration_minutes,
            "notes": s.notes
        })
        events.append({
            "id": s.id,
            "title": f"{dog.name if dog else 'Dog'}",
            "start": s.start_time.isoformat(),
            "end": (s.start_time + timedelta(minutes=s.duration_minutes)).isoformat(),
        })
    if schedule_rows:
        st.dataframe(pd.DataFrame(schedule_rows))
    else:
        st.write("No upcoming walks scheduled.")

    # calendar visualization
    st.subheader("Calendar")
    # calendar takes events: list of {id, title, start, end}
    calendar(events=events, initial_view="dayGridMonth", height=600)

    # ability to add post-walk note for a past or scheduled walk
    st.subheader("Add Post-walk Note")
    with st.form("note_form"):
        sch_options = {s.id: f"{db.query(Dog).get(s.dog_id).name if db.query(Dog).get(s.dog_id) else 'Dog'} @ {s.start_time}" for s in db.query(Schedule).filter_by(walker_id=walker.id).all()}
        if not sch_options:
            st.info("No schedules found to attach a note to.")
        else:
            sch_choice = st.selectbox("Schedule", options=list(sch_options.keys()), format_func=lambda x: sch_options[x])
            content = st.text_area("Note content")
            save = st.form_submit_button("Save note")
            if save:
                note = WalkNote(schedule_id=sch_choice, content=content, author=user["username"])
                db.add(note)
                db.commit()
                st.success("Note saved.")

    # view notes authored by this walker
    st.subheader("My Notes")
    notes = db.query(WalkNote).filter_by(author=user["username"]).order_by(WalkNote.created_at.desc()).all()
    if notes:
        for n in notes:
            st.markdown(f"**{n.created_at.strftime('%Y-%m-%d %H:%M')}** — {n.content}")
    else:
        st.write("No notes yet.")

# ---------- ROUTING ----------
if user["role"] == "client":
    client_dashboard()
elif user["role"] == "walker":
    walker_dashboard(user)
else:
    st.error("Unknown role — contact admin.")

# close db session at end
db.close()
