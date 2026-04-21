import streamlit as st
import json
import pandas as pd
from collections import defaultdict, deque

st.set_page_config(page_title="🏸 Badminton Tournament", layout="wide")

# ---------------- LOAD DATA ----------------
fixtures = json.load(open("data/fixtures.json"))
results = json.load(open("data/results.json"))
players_master = json.load(open("data/players.json"))

teams = sorted(set(
    [f["team_a"] for f in fixtures] +
    [f["team_b"] for f in fixtures]
))

# ---------------- ADMIN AUTH ----------------
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

def admin_login():
    with st.form("login"):
        pwd = st.text_input("Admin Password", type="password")
        if st.form_submit_button("Login"):
            if pwd == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.is_admin = True
                st.success("Logged in as admin")
                st.rerun()
            else:
                st.error("Wrong password")

# ---------------- CALCULATION ENGINE ----------------
def calculate_stats(results):
    team_stats = defaultdict(lambda: {
        "Played": 0, "Won": 0, "Lost": 0, "Points": 0,
        "Sets Won": 0, "Sets Lost": 0,
        "Points Won": 0, "Points Lost": 0
    })

    player_stats = defaultdict(lambda: {
        "Team": "", "Played": 0, "Won": 0, "Points": 0,
        "Sets Won": 0, "Sets Lost": 0,
        "Points Won": 0, "Points Lost": 0,
        "Form": deque(maxlen=5)
    })

    for tie in results:
        team_a, team_b = tie["team_a"], tie["team_b"]
        fixture = next(f for f in fixtures if f["tie_id"] == tie["tie_id"])

        a_match_wins = b_match_wins = 0

        for i, match in enumerate(tie["matches"]):
            pair_a = [p.strip() for p in fixture["matches"][i][0].split("/")]
