# app.py

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px  # Optional: for richer charts
import os

# ----------------------------
# Utility: Database setup
# ----------------------------
DB_PATH = "club_dashboard.db"

def init_db():
    """Initialize SQLite DB with tables if they don't exist."""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # Announcements table
    c.execute("""
    CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        date_created TEXT NOT NULL
    )
    """)
    # Events table
    c.execute("""
    CREATE TABLE IF NOT EXISTS events (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        date DATE NOT NULL,
        time TEXT,
        location TEXT,
        created_at TEXT NOT NULL
    )
    """)
    # Members table
    c.execute("""
    CREATE TABLE IF NOT EXISTS members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT,
        joined_date TEXT
    )
    """)
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    return conn

# ----------------------------
# Data Access Functions
# ----------------------------
def fetch_announcements():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM announcements ORDER BY date_created DESC", conn)
    conn.close()
    return df

def add_announcement(title, content):
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute(
        "INSERT INTO announcements (title, content, date_created) VALUES (?, ?, ?)",
        (title, content, now)
    )
    conn.commit()
    conn.close()

def fetch_events():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM events ORDER BY date ASC", conn)
    conn.close()
    # Convert date column to datetime if needed:
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
    return df

def add_event(name, description, date, time, location):
    conn = get_db_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute(
        "INSERT INTO events (name, description, date, time, location, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        (name, description, date.isoformat(), time, location, now)
    )
    conn.commit()
    conn.close()

def fetch_members():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM members ORDER BY joined_date DESC", conn)
    conn.close()
    if not df.empty:
        df['joined_date'] = pd.to_datetime(df['joined_date'])
    return df

def add_member(name, role, joined_date):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute(
        "INSERT INTO members (name, role, joined_date) VALUES (?, ?, ?)",
        (name, role, joined_date.isoformat() if hasattr(joined_date, "isoformat") else joined_date)
    )
    conn.commit()
    conn.close()

# ----------------------------
# Page: Home
# ----------------------------
def page_home():
    st.header("Welcome to the Club Dashboard")
    st.markdown(
        """
        This dashboard follows the classic CRUD approach (Create, Read, Update, Delete) for announcements, events, and members,
        but you can innovate by connecting APIs, adding real-time features, or integrating AI summarization later.
        
        **Tips (from tradition):**
        - Keep data normalized (we’re using SQLite here for simplicity).
        - Display lists in tables, sorted by date.
        - Provide simple forms for creating new entries.
        
        **Forward-looking ideas:**
        - Hook this into a cloud database or REST API.
        - Add authentication (Streamlit-Auth or OAuth) to restrict admin access.
        - Integrate notifications (email/SMS) when new announcements are posted.
        - Use AI (e.g., GPT) to auto-summarize event descriptions.
        """
    )
    st.write("Current date and time:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

# ----------------------------
# Page: Announcements
# ----------------------------
def page_announcements():
    st.header("Announcements")
    df = fetch_announcements()

    # Display existing announcements
    if df.empty:
        st.info("No announcements yet.")
    else:
        for _, row in df.iterrows():
            with st.expander(f"{row['title']}  ({row['date_created'][:10]})"):
                st.markdown(row['content'])

    st.markdown("---")
    st.subheader("Create New Announcement")
    with st.form("announcement_form", clear_on_submit=True):
        title = st.text_input("Title")
        content = st.text_area("Content")
        submitted = st.form_submit_button("Post Announcement")
        if submitted:
            if not title.strip() or not content.strip():
                st.warning("Title and content cannot be empty.")
            else:
                add_announcement(title.strip(), content.strip())
                st.success("Announcement posted!")
                # Rerun to show the new announcement
                st.experimental_rerun()

# ----------------------------
# Page: Events
# ----------------------------
def page_events():
    st.header("Events")
    df = fetch_events()

    # Filter upcoming vs past
    if not df.empty:
        today = pd.to_datetime(datetime.now().date())
        upcoming = df[df['date'] >= today]
        past = df[df['date'] < today]
        st.subheader("Upcoming Events")
        if upcoming.empty:
            st.write("No upcoming events.")
        else:
            # Show as table or cards
            st.dataframe(upcoming[['name', 'date', 'time', 'location']])
        st.subheader("Past Events")
        if past.empty:
            st.write("No past events.")
        else:
            st.dataframe(past[['name', 'date', 'time', 'location']])
    else:
        st.info("No events scheduled yet.")

    st.markdown("---")
    st.subheader("Schedule a New Event")
    with st.form("event_form", clear_on_submit=True):
        name = st.text_input("Event Name")
        description = st.text_area("Description")
        date = st.date_input("Date")
        time = st.time_input("Time")
        location = st.text_input("Location")
        submitted = st.form_submit_button("Add Event")
        if submitted:
            if not name.strip():
                st.warning("Event name is required.")
            else:
                add_event(name.strip(), description.strip(), date, time.strftime("%H:%M") if hasattr(time, "strftime") else str(time), location.strip())
                st.success("Event added!")
                st.experimental_rerun()

# ----------------------------
# Page: Members
# ----------------------------
def page_members():
    st.header("Members")
    df = fetch_members()
    if df.empty:
        st.info("No members in the database yet.")
    else:
        st.dataframe(df[['name', 'role', 'joined_date']])

    st.markdown("---")
    st.subheader("Add New Member")
    with st.form("member_form", clear_on_submit=True):
        name = st.text_input("Name")
        role = st.text_input("Role (e.g., President, Treasurer)")
        joined_date = st.date_input("Joined Date", value=datetime.now().date())
        submitted = st.form_submit_button("Add Member")
        if submitted:
            if not name.strip():
                st.warning("Member name is required.")
            else:
                add_member(name.strip(), role.strip(), joined_date)
                st.success("Member added!")
                st.experimental_rerun()

# ----------------------------
# Page: Analytics
# ----------------------------
def page_analytics():
    st.header("Analytics & Insights")
    st.markdown(
        """
        Traditional dashboards would show counts, trends over time, etc. Here are some examples:
        """
    )
    # Announcements over time
    ann = fetch_announcements()
    if not ann.empty:
        df_ann = ann.copy()
        df_ann['date'] = pd.to_datetime(df_ann['date_created']).dt.date
        count_by_date = df_ann.groupby('date').size().reset_index(name='count')
        st.subheader("Announcements Posted Over Time")
        fig1 = px.bar(count_by_date, x='date', y='count', title="Announcements per Day")
        st.plotly_chart(fig1, use_container_width=True)
    else:
        st.write("No announcements data for analytics.")

    # Events count by month
    ev = fetch_events()
    if not ev.empty:
        df_ev = ev.copy()
        df_ev['month'] = df_ev['date'].dt.to_period("M").astype(str)
        count_ev = df_ev.groupby('month').size().reset_index(name='num_events')
        st.subheader("Events Scheduled by Month")
        fig2 = px.line(count_ev, x='month', y='num_events', title="Events per Month")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.write("No events data for analytics.")

    # Member roles distribution
    mem = fetch_members()
    if not mem.empty:
        st.subheader("Member Roles Distribution")
        role_counts = mem['role'].value_counts().reset_index()
        role_counts.columns = ['role', 'count']
        fig3 = px.pie(role_counts, names='role', values='count', title="Roles Breakdown")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.write("No member data for analytics.")

# ----------------------------
# Main
# ----------------------------
def main():
    # Initialize DB on first run
    if not os.path.exists(DB_PATH):
        init_db()

    st.set_page_config(page_title="Club Dashboard", layout="wide")
    st.sidebar.title("Navigation")
    pages = {
        "Home": page_home,
        "Announcements": page_announcements,
        "Events": page_events,
        "Members": page_members,
        "Analytics": page_analytics
    }
    choice = st.sidebar.radio("Go to", list(pages.keys()))
    # Traditional pattern: call the selected page function
    pages[choice]()

if __name__ == "__main__":
    main()
