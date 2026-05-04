import streamlit as st
import pandas as pd
import json
import requests
from collections import defaultdict

# =================================================
# PAGE CONFIG (MUST BE FIRST)
# =================================================
st.set_page_config(
    page_title="🏸 Tournament Intelligence Platform",
    layout="wide"
)

# =================================================
# GLOBAL STYLE – STREAMLIT SAFE & VISIBLE
# =================================================
st.markdown("""
<style>
/* Background */
[data-testid="stAppViewContainer"] {
    background-color: #F1F5F9;
}

/* Titles */
h1 { color: #0F172A; font-weight: 800; }
h2, h3 { color: #1E293B; font-weight: 700; }

/* Navigation pills */
div[role="radiogroup"] label {
    background: #E5E7EB;
    padding: 10px 18px;
    border-radius: 999px;
    margin-right: 8px;
    font-weight: 600;
}
div[role="radiogroup"] label[data-checked="true"] {
    background: #2563EB;
    color: white;
}

/* Cards */
.card {
    background: white;
    border-left: 6px solid #2563EB;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 18px;
    border: 1px solid #E5E7EB;
}

/* Badges */
.badge-green {
    background: #DCFCE7;
    color: #166534;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}
.badge-yellow {
    background: #FEF3C7;
    color: #92400E;
    padding: 4px 10px;
    border-radius: 999px;
    font-size: 12px;
    font-weight: 600;
}

/* Accent VS */
.vs {
    color: #F97316;
    font-weight: 700;
}
</style>
""", unsafe_allow_html=True)

# =================================================
# HEADER
# =================================================
st.title("🏸 Tournament Intelligence Platform")
st.caption("Professional badminton tournament dashboard")

# =================================================
# NAVIGATION
# =================================================
menu = st.radio(
    "Navigate",
    [
        "Overview",
        "Fixtures",
        "Results",
        "Teams",
        "Team Standings",
        "Player Standings"
    ],
    horizontal=True
)

# =================================================
# DATA
# =================================================
SCRIPT_URL = st.secrets["SCRIPT_URL"]

teams_data = {
    "Smash Titans": ["Omkar", "Nishit", "Ganesh", "Sandeep W", "Amit", "Jayant"],
    "Quantum Force": ["Rajendra", "Aniket", "Deepak L", "Rahul", "Manmohan", "Prashant"],
    "Racket Scientists": ["Kiran", "Kaustubh", "Piyush", "Pradyum", "Amol S", "Amol P"],
    "Net Ninjas": ["Jaswanth", "Sandeepk", "Ritesh", "Vikram", "Pramod", "Deepak T"],
}

def load_json(path):
    with open(path) as f:
        return json.load(f)

fixtures = load_json("data/fixtures.json")

@st.cache_data(ttl=30)
def load_results():
    data = defaultdict(lambda: {"matches": [{}, {}, {}]})
    try:
        rows = requests.get(SCRIPT_URL, timeout=8).json()
        for r in rows:
            tid = int(r["tie_id"])
            idx = int(r["match_index"]) - 1
            sets = json.loads(r["sets_json"])
            if sets:
                data[tid]["matches"][idx] = {"sets": sets}
    except:
        pass
    return dict(data)

# =================================================
# OVERVIEW
# =================================================
if menu == "Overview":
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", "LIVE")
    c2.metric("Teams", len(teams_data))
    c3.metric("Fixtures", len(fixtures))
    c4.metric("Matches", len(fixtures) * 3)

# =================================================
# FIXTURES
# =================================================
elif menu == "Fixtures":
    st.subheader("Fixtures")
    results = load_results()

    for f in fixtures:
        completed = sum(
            1 for m in results.get(f["tie_id"], {}).get("matches", [])
            if m and "sets" in m
        )

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.markdown(
            f"### {f['team_a']} <span class='vs'>VS</span> {f['team_b']}",
            unsafe_allow_html=True
        )

        if completed == 3:
            st.markdown("<span class='badge-green'>COMPLETED</span>", unsafe_allow_html=True)
        else:
            st.markdown("<span class='badge-yellow'>IN PROGRESS</span>", unsafe_allow_html=True)

        st.write(f"{completed} / 3 matches completed")

        for i, (a, b) in enumerate(f["matches"], start=1):
            st.write(f"**M{i}**: {a} vs {b}")

        st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# RESULTS
# =================================================
elif menu == "Results":
    st.subheader("Results")
    results = load_results()

    if not results:
        st.warning("No results available yet.")
        st.stop()

    for tid, r in results.items():
        fx = next((f for f in fixtures if f["tie_id"] == tid), None)
        if not fx:
            continue

        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"### {fx['team_a']} vs {fx['team_b']}")

        for i, m in enumerate(r["matches"], start=1):
            if not m or "sets" not in m:
                st.write(f"**M{i}**: Pending")
            else:
                score = " | ".join(f"{a}-{b}" for a, b in m["sets"])
                st.write(f"**M{i}**: {fx['matches'][i-1][0]} vs {fx['matches'][i-1][1]} — {score}")

        st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# TEAM STANDINGS
# =================================================
elif menu == "Team Standings":
    st.subheader("Team Standings")
    results = load_results()

    table = defaultdict(lambda: {"Played":0, "Wins":0, "Losses":0})

    for tid, r in results.items():
        fx = next((f for f in fixtures if f["tie_id"] == tid), None)
        if not fx:
            continue

        for m in r["matches"]:
            if not m or "sets" not in m:
                continue

            a_sets = sum(1 for a,b in m["sets"] if a>b)
            b_sets = len(m["sets"]) - a_sets

            table[fx["team_a"]]["Played"] += 1
            table[fx["team_b"]]["Played"] += 1

            if a_sets > b_sets:
                table[fx["team_a"]]["Wins"] += 1
                table[fx["team_b"]]["Losses"] += 1
            else:
                table[fx["team_b"]]["Wins"] += 1
                table[fx["team_a"]]["Losses"] += 1

    df = pd.DataFrame.from_dict(table, orient="index").fillna(0)
    df = df.sort_values(["Wins","Played"], ascending=[False, True])
    df.insert(0, "Rank", range(1, len(df)+1))
    st.dataframe(df, use_container_width=True)

# =================================================
# PLAYER STANDINGS
# =================================================
elif menu == "Player Standings":
    st.subheader("Player Standings")
    results = load_results()

    stats = defaultdict(lambda: {"Team":"", "Played":0, "Wins":0})

    for team, players in teams_data.items():
        for p in players:
            stats[p]["Team"] = team

    for tid, r in results.items():
        fx = next((f for f in fixtures if f["tie_id"] == tid), None)
        if not fx:
            continue

        for i, m in enumerate(r["matches"]):
            if not m or "sets" not in m:
                continue

            pa, pb = fx["matches"][i]
            A = pa.split("/")
            B = pb.split("/")

            a_sets = sum(1 for a,b in m["sets"] if a>b)
            b_sets = len(m["sets"]) - a_sets

            for p in A:
                stats[p.strip()]["Played"] += 1
                if a_sets > b_sets:
                    stats[p.strip()]["Wins"] += 1

            for p in B:
                stats[p.strip()]["Played"] += 1
                if b_sets > a_sets:
                    stats[p.strip()]["Wins"] += 1

    df = pd.DataFrame.from_dict(stats, orient="index").fillna(0)
    df = df.sort_values(["Wins","Played"], ascending=[False, True])
    df.insert(0, "Rank", range(1, len(df)+1))
    df = df.reset_index().rename(columns={"index":"Player"})

    st.dataframe(df.head(10), use_container_width=True, hide_index=True)
