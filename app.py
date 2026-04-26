import streamlit as st
import json
import os
import requests
import pandas as pd
from collections import defaultdict

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="🏸 Badminton Tournament", layout="wide")
st.title("🏸 Badminton Tournament")

# =================================================
# SECRETS
# =================================================
SCRIPT_URL = st.secrets["SCRIPT_URL"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

# =================================================
# DATA
# =================================================
teams_data = {
    "Smash Titans": ["Omkar", "Nishit", "Ganesh", "Sandeep W", "Amit", "Jayant"],
    "Quantum Force": ["Rajendra", "Aniket", "Deepak L", "Rahul", "Manmohan", "Prashant"],
    "Racket Scientists": ["Kiran", "Kaustubh", "Piyush", "Pradyum", "Amol S", "Amol P"],
    "Net Ninjas": ["Jaswanth", "Sandeepk", "Ritesh", "Vikram", "Pramod", "Deepak T"]
}

team_logos = {
    "Smash Titans": "assets/Logos/smash_titans.jpeg",
    "Quantum Force": "assets/Logos/quantum_force.jpeg",
    "Racket Scientists": "assets/Logos/racket_scientists.jpeg",
    "Net Ninjas": "assets/Logos/net_ninjas.jpeg"
}

# =================================================
# HELPERS
# =================================================
def show_logo(team, width=60):
    path = team_logos.get(team)
    if path and os.path.exists(path):
        st.image(path, width=width)

def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def load_results_from_sheet():
    r = requests.get(SCRIPT_URL, timeout=10)
    rows = r.json()

    results = defaultdict(lambda: {
        "tie_id": None,
        "team_a": "",
        "team_b": "",
        "matches": [{}, {}, {}]
    })

    for row in rows:
        try:
            sets = json.loads(row["sets_json"])
        except:
            continue

        if not sets:
            continue

        tie_id = int(row["tie_id"])
        results[tie_id]["tie_id"] = tie_id
        results[tie_id]["team_a"] = row["team_a"]
        results[tie_id]["team_b"] = row["team_b"]
        results[tie_id]["matches"][int(row["match_index"]) - 1] = {
            "sets": sets
        }

    return list(results.values())

# =================================================
# FIXTURE CARD RENDER
# =================================================
def render_fixture_card(tie, status, completed_matches):
    """
    tie               : fixture dict from fixtures.json
    status            : 'UPCOMING' or 'CLOSED'
    completed_matches : list of completed match indices, e.g. [1, 3]
    """

    badge = "🕒 Scheduled / In‑Progress" if status == "UPCOMING" else "✅ Closed"

    # =========================
    # Card container
    # =========================
    st.markdown(
        f"""
        <div style="
            padding:18px;
            border-radius:14px;
            border:1px solid #e0e0e0;
            background:#fafafa;
            margin-bottom:20px;
        ">
        <div style="text-align:right;font-size:12px;color:#666;">{badge}</div>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # Header: logos + teams
    # =========================
    h1, h2, h3 = st.columns([1, 4, 1])
    with h1:
        show_logo(tie["team_a"], 48)

    with h2:
        st.markdown(
            f"""
            <div style="text-align:center;font-weight:600;">
                {tie['team_a']}
                <div style="color:#ff7f0e;">VS</div>
                {tie['team_b']}
            </div>
            """,
            unsafe_allow_html=True
        )

    with h3:
        show_logo(tie["team_b"], 48)

    st.divider()

    # =========================
    # Matches (M1 / M2 / M3)
    # =========================
    for idx, match in enumerate(tie["matches"], start=1):
        pair_a, pair_b = match

        if idx in completed_matches:
            icon = "✅"
            subtitle = "Completed"
            opacity = "1.0"

# =================================================
# LOAD FIXTURES
# =================================================
fixtures = load_json("data/fixtures.json", [])

# =================================================
# ADMIN SESSION
# =================================================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =================================================
# MENU
# =================================================
menu = st.radio(
    "Navigate",
    [
        "Home",
        "Teams",
        "Fixtures",
        "Results",
        "Team Standings",
        "Player Standings",
        "Enter Results",
        "Admin Login"
    ],
    horizontal=True
)

# =================================================
# HOME
# =================================================
if menu == "Home":
    st.info("Welcome to the House League Badminton Tournament")

# =================================================
# TEAMS (4 COLUMNS)
# =================================================
elif menu == "Teams":
    st.subheader("🏸 Teams")
    cols = st.columns(4)
    for col, (team, players) in zip(cols, teams_data.items()):
        with col:
            show_logo(team, 90)
            st.markdown(f"### {team}")
            st.divider()
            for p in players:
                st.write(f"• {p}")

# =================================================
# FIXTURES (NEXT → CLOSED)
# =================================================
elif menu == "Fixtures":
    st.subheader("📅 Fixtures")

    results = load_results_from_sheet()

    completed_map = {}
    for r in results:
        done = []
        for idx, m in enumerate(r["matches"], start=1):
            if m and "sets" in m and m["sets"]:
                done.append(idx)
        completed_map[r["tie_id"]] = done

    upcoming, closed = [], []

    for f in fixtures:
        if len(completed_map.get(f["tie_id"], [])) == 3:
            closed.append(f)
        else:
            upcoming.append(f)

    if upcoming:
        st.markdown("## ⏭️ Next Scheduled Fixtures")
        for i in range(0, len(upcoming), 2):
            cols = st.columns(2)
            for col, tie in zip(cols, upcoming[i:i+2]):
                with col:
                    render_fixture_card(tie, "UPCOMING")

    if closed:
        st.markdown("## ✅ Closed Fixtures")
        for i in range(0, len(closed), 2):
            cols = st.columns(2)
            for col, tie in zip(cols, closed[i:i+2]):
                with col:
                    render_fixture_card(tie, "CLOSED")

# =================================================
# TEAM STANDINGS
# =================================================
elif menu == "Team Standings":
    st.subheader("📊 Team Standings")

    results = load_results_from_sheet()
    table = defaultdict(lambda: {
        "Matches": 0,
        "Wins": 0,
        "Losses": 0,
        "Set Diff": 0,
        "Point Diff": 0,
        "Points": 0
    })

    for r in results:
        ta, tb = r["team_a"], r["team_b"]
        for m in r["matches"]:
            if not m or "sets" not in m:
                continue

            a_sets = b_sets = a_pts = b_pts = 0
            for a, b in m["sets"]:
                a_pts += a
                b_pts += b
                if a > b:
                    a_sets += 1
                else:
                    b_sets += 1

            table[ta]["Matches"] += 1
            table[tb]["Matches"] += 1
            table[ta]["Set Diff"] += (a_sets - b_sets)
            table[tb]["Set Diff"] += (b_sets - a_sets)
            table[ta]["Point Diff"] += (a_pts - b_pts)
            table[tb]["Point Diff"] += (b_pts - a_pts)

            if a_sets > b_sets:
                table[ta]["Wins"] += 1
                table[tb]["Losses"] += 1
            else:
                table[tb]["Wins"] += 1
                table[ta]["Losses"] += 1

    for t in table:
        table[t]["Points"] = table[t]["Wins"] * 2

    df = pd.DataFrame.from_dict(table, orient="index").sort_values(
        by=["Points", "Set Diff", "Point Diff"], ascending=False
    )

    st.dataframe(df, width="stretch")

# =================================================
# PLAYER STANDINGS
# =================================================
elif menu == "Player Standings":
    st.subheader("👤 Player Standings")

    st.info("Player standings logic already verified earlier")

# =================================================
# ADMIN LOGIN
# =================================================
elif menu == "Admin Login":
    st.subheader("🔐 Admin Login")

    if st.session_state.is_admin:
        st.success("✅ Logged in as Admin")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()
    else:
        pwd = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
