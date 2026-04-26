import streamlit as st
import json
import os
import requests
import pandas as pd
from collections import defaultdict

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="🏸 Tournament Intelligence Platform", layout="wide")

# =================================================
# GLOBAL THEME / CSS
# =================================================
st.markdown("""
<style>
html, body {
    font-family: Inter, Segoe UI, Helvetica, Arial, sans-serif;
    background-color: #F8FAFC;
    color: #0F172A;
}
.stApp { background-color: #F8FAFC; }
.block-container { max-width: 1200px; padding-top: 1.5rem; }

.card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 20px;
}

h1 { font-size: 28px; font-weight: 600; }
h2 { font-size: 20px; font-weight: 600; }
h3 { font-size: 16px; font-weight: 600; }

.vs {
    color: #F59E0B;
    font-weight: 700;
    text-align: center;
    margin-top: 22px;
}
</style>
""", unsafe_allow_html=True)

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
def show_logo(team, width=50):
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
        results[tie_id]["matches"][int(row["match_index"]) - 1] = {
            "sets": sets
        }

    return list(results.values())

# =================================================
# LOAD FIXTURES
# =================================================
fixtures = load_json("data/fixtures.json", [])

# =================================================
# MENU
# =================================================
menu = st.radio(
    "Navigate",
    ["Overview", "Teams", "Fixtures", "Results", "Team Standings", "Player Standings"],
    horizontal=True
)

# =================================================
# OVERVIEW
# =================================================
if menu == "Overview":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<h2>Tournament Operations Dashboard</h2>", unsafe_allow_html=True)
    st.markdown(
        "Real‑time overview of match operations, competitive status, and performance indicators."
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tournament Status", "LIVE")
    c2.metric("Matches Played", "18 / 24")
    c3.metric("Leading Team", "Smash Titans")
    c4.metric("Fixtures Today", "3")
    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# TEAMS
# =================================================
elif menu == "Teams":
    st.subheader("Participating Teams")
    cols = st.columns(4)
    for col, (team, players) in zip(cols, teams_data.items()):
        with col:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            show_logo(team, 80)
            st.markdown(f"<h3>{team}</h3>", unsafe_allow_html=True)
            for p in players:
                st.write("•", p)
            st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# FIXTURES
# =================================================
elif menu == "Fixtures":
    st.subheader("Fixtures & Match Operations")
    results = load_results_from_sheet()

    completed_map = {}
    for r in results:
        done = []
        for i, m in enumerate(r["matches"], start=1):
            if m and "sets" in m:
                done.append(i)
        completed_map[r["tie_id"]] = done

    for i in range(0, len(fixtures), 2):
        cols = st.columns(2)
        for col, f in zip(cols, fixtures[i:i+2]):
            with col:
                st.markdown("<div class='card'>", unsafe_allow_html=True)
                left, mid, right = st.columns([3, 1, 3])

                with left:
                    show_logo(f["team_a"])
                    st.markdown(f"<b>{f['team_a']}</b>", unsafe_allow_html=True)
                with mid:
                    st.markdown("<div class='vs'>VS</div>", unsafe_allow_html=True)
                with right:
                    show_logo(f["team_b"])
                    st.markdown(f"<b>{f['team_b']}</b>", unsafe_allow_html=True)

                st.divider()
                for idx, (pa, pb) in enumerate(f["matches"], start=1):
                    status = "Completed" if idx in completed_map.get(f["tie_id"], []) else "Scheduled"
                    st.write(f"M{idx}: {pa} vs {pb} — {status}")
                st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# RESULTS
# =================================================
elif menu == "Results":
    st.subheader("Match Results")
    results = load_results_from_sheet()

    for i in range(0, len(results), 2):
        cols = st.columns(2)
        for col, r in zip(cols, results[i:i+2]):
            with col:
                fixture = next((f for f in fixtures if f["tie_id"] == r["tie_id"]), None)
                if not fixture:
                    continue

                st.markdown("<div class='card'>", unsafe_allow_html=True)
                left, mid, right = st.columns([3, 1, 3])

                with left:
                    show_logo(fixture["team_a"])
                    st.markdown(f"<b>{fixture['team_a']}</b>", unsafe_allow_html=True)
                with mid:
                    st.markdown("<div class='vs'>VS</div>", unsafe_allow_html=True)
                with right:
                    show_logo(fixture["team_b"])
                    st.markdown(f"<b>{fixture['team_b']}</b>", unsafe_allow_html=True)

                st.divider()
                for idx, m in enumerate(r["matches"], start=1):
                    if not m or "sets" not in m:
                        st.write(f"M{idx}: Not played yet")
                    else:
                        score = " | ".join(f"{a}-{b}" for a, b in m["sets"])
                        st.write(f"M{idx}: {score}")
                st.markdown("</div>", unsafe_allow_html=True)

# =================================================
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

    results = load_results_from_sheet()

    if not results:
        st.warning("No match results available yet.")
        st.stop()

    # ----------------------------
    # Initialize players
    # ----------------------------
    stats = defaultdict(lambda: {
        "Team": "",
        "Played": 0,
        "Match Wins": 0,
        "Set Diff": 0,
        "Point Diff": 0,
        "Form": []
    })

    for team, players in teams_data.items():
        for p in players:
            stats[p]["Team"] = team

    # ----------------------------
    # Process results
    # ----------------------------
    processed_matches = 0

    for r in results:
        tie_id = r["tie_id"]

        fixture = next((f for f in fixtures if f["tie_id"] == tie_id), None)
        if fixture is None:
            continue

        for i, m in enumerate(r["matches"]):
            if not m or "sets" not in m or not m["sets"]:
                continue

            processed_matches += 1
            sets = m["sets"]

            pair_a, pair_b = fixture["matches"][i]
            team_a_players = [p.strip() for p in pair_a.split("/")]
            team_b_players = [p.strip() for p in pair_b.split("/")]

            a_sets = b_sets = a_pts = b_pts = 0
            for a, b in sets:
                a_pts += a
                b_pts += b
                if a > b:
                    a_sets += 1
                else:
                    b_sets += 1

            a_win = a_sets > b_sets

            for p in team_a_players:
                stats[p]["Played"] += 1
                stats[p]["Set Diff"] += (a_sets - b_sets)
                stats[p]["Point Diff"] += (a_pts - b_pts)
                stats[p]["Form"].append("W" if a_win else "L")
                if a_win:
                    stats[p]["Match Wins"] += 1

            for p in team_b_players:
                stats[p]["Played"] += 1
                stats[p]["Set Diff"] += (b_sets - a_sets)
                stats[p]["Point Diff"] += (b_pts - a_pts)
                stats[p]["Form"].append("L" if a_win else "W")
                if not a_win:
                    stats[p]["Match Wins"] += 1

    if processed_matches == 0:
        st.warning("Results exist but no completed matches were found.")
        st.stop()

    # ----------------------------
    # Build table
    # ----------------------------
    df = (
        pd.DataFrame.from_dict(stats, orient="index")
        .reset_index()
        .rename(columns={"index": "Player"})
    )

    df["Form"] = df["Form"].apply(lambda x: " ".join(x[-5:]))

    df = df.sort_values(
        by=["Match Wins", "Set Diff", "Point Diff", "Played"],
        ascending=[False, False, False, True]
    ).reset_index(drop=True)

    df.insert(0, "Rank", df.index + 1)

    st.dataframe(
        df[
            [
                "Rank",
                "Team",
                "Player",
                "Played",
                "Match Wins",
                "Set Diff",
                "Point Diff",
                "Form",
            ]
        ],
        hide_index=True,
        width="stretch"
    )


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
