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
# UI STYLING (SAFE)
# =================================================
st.markdown("""
<style>
html, body {
    font-family: Inter, Segoe UI, Helvetica, Arial, sans-serif;
    background-color: #F8FAFC;
    color: #0F172A;
}
.block-container { max-width: 1200px; padding-top: 1.5rem; }

.card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 18px;
}

.rank1 {
    background-color: #FFF7ED;
    border: 1px solid #F59E0B;
}

.vs {
    text-align: center;
    font-weight: 700;
    color: #F59E0B;
    margin-top: 20px;
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
    if team in team_logos and os.path.exists(team_logos[team]):
        st.image(team_logos[team], width=width)

def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def load_results_from_sheet():
    r = requests.get(SCRIPT_URL, timeout=10)
    rows = r.json()

    data = defaultdict(lambda: {
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

        tid = int(row["tie_id"])
        data[tid]["tie_id"] = tid
        data[tid]["matches"][int(row["match_index"]) - 1] = {"sets": sets}

    return list(data.values())

fixtures = load_json("data/fixtures.json", [])

# =================================================
# SESSION
# =================================================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =================================================
# MENU
# =================================================
menu = st.radio(
    "Navigate",
    [
        "Overview",
        "Teams",
        "Fixtures",
        "Results",
        "Team Standings",
        "Player Standings",
        "Admin"
    ],
    horizontal=True
)

# =================================================
# OVERVIEW
# =================================================
if menu == "Overview":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Tournament Operations Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", "LIVE")
    c2.metric("Matches Played", "18 / 24")
    c3.metric("Leading Team", "Smash Titans")
    c4.metric("Fixtures Today", "3")
    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# TEAMS
# =================================================
elif menu == "Teams":
    cols = st.columns(4)
    for col, (team, players) in zip(cols, teams_data.items()):
        with col:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            show_logo(team, 80)
            st.markdown(f"#### {team}")
            for p in players:
                st.write("•", p)
            st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# FIXTURES (with progress bar)
# =================================================
elif menu == "Fixtures":
    results = load_results_from_sheet()
    completed = {
        r["tie_id"]: sum(1 for m in r["matches"] if m)
        for r in results
    }

    for i in range(0, len(fixtures), 2):
        cols = st.columns(2)
        for col, f in zip(cols, fixtures[i:i+2]):
            with col:
                done = completed.get(f["tie_id"], 0)
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                l, m, r = st.columns([3, 1, 3])
                with l:
                    show_logo(f["team_a"])
                    st.write(f["team_a"])
                with m:
                    st.markdown("<div class='vs'>VS</div>", unsafe_allow_html=True)
                with r:
                    show_logo(f["team_b"])
                    st.write(f["team_b"])

                st.progress(done / 3)
                st.caption(f"{done} / 3 matches completed")

                for idx, (pa, pb) in enumerate(f["matches"], start=1):
                    st.write(f"M{idx}: {pa} vs {pb}")

                st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# RESULTS (winner emphasis)
# =================================================
elif menu == "Results":
    results = load_results_from_sheet()

    for i in range(0, len(results), 2):
        cols = st.columns(2)
        for col, rdata in zip(cols, results[i:i+2]):
            with col:
                fixture = next(f for f in fixtures if f["tie_id"] == rdata["tie_id"])
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                l, m, r = st.columns([3, 1, 3])
                l.markdown(f"**{fixture['team_a']}**")
                m.markdown("<div class='vs'>VS</div>", unsafe_allow_html=True)
                r.markdown(f"**{fixture['team_b']}**")

                for idx, mset in enumerate(rdata["matches"], start=1):
                    if not mset:
                        st.write(f"M{idx}: Not played")
                    else:
                        score = " | ".join(f"{a}-{b}" for a, b in mset["sets"])
                        st.write(f"M{idx}: {score}")

                st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# TEAM STANDINGS (gold highlight)
# =================================================
elif menu == "Team Standings":
    results = load_results_from_sheet()
    table = defaultdict(lambda: {
        "Played": 0, "Wins": 0, "Losses": 0,
        "Set Diff": 0, "Point Diff": 0, "Points": 0
    })

    for r in results:
        f = next(fx for fx in fixtures if fx["tie_id"] == r["tie_id"])
        ta, tb = f["team_a"], f["team_b"]

        for m in r["matches"]:
            if not m:
                continue
            a_s = b_s = a_p = b_p = 0
            for a, b in m["sets"]:
                a_p += a; b_p += b
                if a > b: a_s += 1
                else: b_s += 1

            table[ta]["Played"] += 1
            table[tb]["Played"] += 1
            table[ta]["Set Diff"] += a_s - b_s
            table[tb]["Set Diff"] += b_s - a_s
            table[ta]["Point Diff"] += a_p - b_p
            table[tb]["Point Diff"] += b_p - a_p

            if a_s > b_s:
                table[ta]["Wins"] += 1
                table[ta]["Points"] += 2
                table[tb]["Losses"] += 1
            else:
                table[tb]["Wins"] += 1
                table[tb]["Points"] += 2
                table[ta]["Losses"] += 1

    df = pd.DataFrame.from_dict(table, orient="index")
    df = df.sort_values(by=["Points", "Wins", "Set Diff", "Point Diff"], ascending=False)

    for i, row in df.iterrows():
        cls = "card rank1" if row.name == df.index[0] else "card"
        st.markdown(f"<div class='{cls}'>", unsafe_allow_html=True)
        st.write(i, dict(row))
        st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# PLAYER STANDINGS
# =================================================
elif menu == "Player Standings":
    results = load_results_from_sheet()
    stats = defaultdict(lambda: {
        "Team": "", "Played": 0, "Wins": 0,
        "Set Diff": 0, "Point Diff": 0, "Form": []
    })

    for t, players in teams_data.items():
        for p in players:
            stats[p]["Team"] = t

    for r in results:
        f = next(fx for fx in fixtures if fx["tie_id"] == r["tie_id"])
        for i, m in enumerate(r["matches"]):
            if not m:
                continue

            a_pair, b_pair = f["matches"][i]
            A = [p.strip() for p in a_pair.split("/")]
            B = [p.strip() for p in b_pair.split("/")]

            a_s = b_s = a_p = b_p = 0
            for a, b in m["sets"]:
                a_p += a; b_p += b
                if a > b: a_s += 1
                else: b_s += 1

            for p in A:
                stats[p]["Played"] += 1
                stats[p]["Set Diff"] += a_s - b_s
                stats[p]["Point Diff"] += a_p - b_p
                stats[p]["Form"].append("W" if a_s > b_s else "L")
                if a_s > b_s: stats[p]["Wins"] += 1

            for p in B:
                stats[p]["Played"] += 1
                stats[p]["Set Diff"] += b_s - a_s
                stats[p]["Point Diff"] += b_p - a_p
                stats[p]["Form"].append("W" if b_s > a_s else "L")
                if b_s > a_s: stats[p]["Wins"] += 1

    df = pd.DataFrame.from_dict(stats, orient="index")
    df["Form"] = df["Form"].apply(lambda x: " ".join(x[-5:]))
    df = df.sort_values(by=["Wins", "Set Diff", "Point Diff", "Played"], ascending=[False, False, False, True])
    df.insert(0, "Rank", range(1, len(df) + 1))
    st.dataframe(df.reset_index().rename(columns={"index": "Player"}), width="stretch")

# =================================================
# ADMIN
# =================================================
elif menu == "Admin":
    pwd = st.text_input("Admin Password", type="password")
    if st.button("Login"):
        if pwd == ADMIN_PASSWORD:
            st.session_state.is_admin = True
            st.success("Admin Mode Active")
        else:
            st.error("Incorrect password")
