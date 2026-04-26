import streamlit as st
import json
import os
import requests
import pandas as pd
from collections import defaultdict

# =================================================
# CONFIG
# =================================================
st.set_page_config(page_title="🏸 Badminton Tournament", layout="wide")
st.title("🏸 Badminton Tournament")

GOOGLE_SCRIPT_URL = st.secrets["SCRIPT_URL"]

# =================================================
# JSON HELPERS (FIXTURES ONLY)
# =================================================
def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

# =================================================
# GOOGLE SHEETS HELPERS (RESULTS)
# =================================================
def save_result_to_sheet(tie_id, team_a, team_b, match_index, sets):
    payload = {
        "tie_id": tie_id,
        "team_a": team_a,
        "team_b": team_b,
        "match_index": match_index,
        "sets": sets
    }
    requests.post(GOOGLE_SCRIPT_URL, json=payload)

def load_results_from_sheet():
    r = requests.get(GOOGLE_SCRIPT_URL)
    rows = r.json()

    results = defaultdict(lambda: {
        "tie_id": None,
        "team_a": "",
        "team_b": "",
        "matches": [{}, {}, {}]
    })

    for row in rows:
        tie_id = int(row["tie_id"])
        results[tie_id]["tie_id"] = tie_id
        results[tie_id]["team_a"] = row["team_a"]
        results[tie_id]["team_b"] = row["team_b"]
        results[tie_id]["matches"][int(row["match_index"]) - 1] = {
            "sets": json.loads(row["sets_json"])
        }

    return list(results.values())

# =================================================
# PLAYER OF MATCH LOGIC
# =================================================
def calculate_potm(match_sets, pair_a, pair_b):
    a_sets = b_sets = 0
    a_pd = b_pd = 0

    for a, b in match_sets:
        if a > b:
            a_sets += 1
        else:
            b_sets += 1
        a_pd += (a - b)
        b_pd += (b - a)

    if a_sets > b_sets:
        return pair_a[0].strip()
    elif b_sets > a_sets:
        return pair_b[0].strip()
    else:
        return pair_a[0].strip() if a_pd >= b_pd else pair_b[0].strip()

# =================================================
# DATA
# =================================================
teams_data = {
    "Smash Titans": ["Omkar","Nishit","Ganesh","Sandeep W","Amit","Jayant"],
    "Quantum Force": ["Rajendra","Aniket","Deepak L","Rahul","Manmohan","Prashant"],
    "Racket Scientists": ["Kiran","Kaustubh","Piyush","Pradyum","Amol S","Amol P"],
    "Net Ninjas": ["Jaswanth","Sandeepk","Ritesh","Vikram","Pramod","Deepak T"]
}

team_logos = {
    "Smash Titans": "assets/Logos/smash_titans.jpeg",
    "Quantum Force": "assets/Logos/quantum_force.jpeg",
    "Racket Scientists": "assets/Logos/racket_scientists.jpeg",
    "Net Ninjas": "assets/Logos/net_ninjas.jpeg"
}

def show_logo(team, width=60):
    path = team_logos.get(team)
    if path and os.path.exists(path):
        st.image(path, width=width)

# =================================================
# FIXTURES
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
# TEAMS
# =================================================
elif menu == "Teams":
    for t, players in teams_data.items():
        show_logo(t, 80)
        st.subheader(t)
        for p in players:
            st.write("•", p)
        st.divider()

# =================================================
# FIXTURES
# =================================================
elif menu == "Fixtures":
    for tie in fixtures:
        st.subheader(f"Tie {tie['tie_id']} — {tie['team_a']} vs {tie['team_b']}")
        for i, m in enumerate(tie["matches"], 1):
            st.write(f"Match {i}: {m[0]} vs {m[1]}")
        st.divider()

# =================================================
# RESULTS
# =================================================
elif menu == "Results":
    results = load_results_from_sheet()

    if not results:
        st.warning("No results yet.")
    else:
        for r in results:
            st.subheader(f"{r['team_a']} vs {r['team_b']}")
            fixture = next(f for f in fixtures if f["tie_id"] == r["tie_id"])

            for i, m in enumerate(r["matches"], 1):
                if not m:
                    st.write(f"Match {i}: —")
                    continue
                score = " | ".join(f"{a}-{b}" for a,b in m["sets"])
                st.write(f"Match {i}: {score}")

                pair_a = fixture["matches"][i-1][0].split("/")
                pair_b = fixture["matches"][i-1][1].split("/")
                potm = calculate_potm(m["sets"], pair_a, pair_b)
                st.caption(f"🏅 Player of the Match: {potm}")
            st.divider()

# =================================================
# ENTER RESULTS
# =================================================
elif menu == "Enter Results":
    if not st.session_state.is_admin:
        st.warning("Admin only")
    else:
        tie = st.selectbox(
            "Select Tie",
            fixtures,
            format_func=lambda x: f"Tie {x['tie_id']} — {x['team_a']} vs {x['team_b']}"
        )

        match_results = []

        for m in range(3):
            st.markdown(f"### Match {m+1}")
            sets = []
            for s in range(3):
                a = st.number_input(
                    f"{tie['team_a']} Set {s+1}",
                    key=f"a{m}{s}",
                    min_value=0,max_value=30
                )
                b = st.number_input(
                    f"{tie['team_b']} Set {s+1}",
                    key=f"b{m}{s}",
                    min_value=0,max_value=30
                )
                if a > 0 or b > 0:
                    sets.append([a,b])
            match_results.append({"sets": sets})

        if st.button("✅ Save Results"):
            for i, match in enumerate(match_results):
                if match["sets"]:
                    save_result_to_sheet(
                        tie["tie_id"],
                        tie["team_a"],
                        tie["team_b"],
                        i+1,
                        match["sets"]
                    )
            st.success("Saved to Google Sheets ✅")
            st.rerun()

# =================================================
# TEAM STANDINGS
# =================================================
elif menu == "Team Standings":
    results = load_results_from_sheet()
    table = defaultdict(lambda: {"Match Wins":0,"Points":0})

    for r in results:
        for m in r["matches"]:
            if m:
                a_sets = sum(1 for a,b in m["sets"] if a>b)
                b_sets = sum(1 for a,b in m["sets"] if b>a)
                if a_sets>b_sets:
                    table[r["team_a"]]["Match Wins"]+=1
                else:
                    table[r["team_b"]]["Match Wins"]+=1

    for t in table:
        table[t]["Points"] = table[t]["Match Wins"]*2

    df = pd.DataFrame.from_dict(table, orient="index")
    st.dataframe(df.sort_values("Points",ascending=False))

# =================================================
