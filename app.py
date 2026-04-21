import streamlit as st
import json
import pandas as pd
import os
from collections import defaultdict, deque

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="🏸 Badminton Tournament", layout="wide")
st.title("🏸 Badminton Tournament")

# =================================================
# ADMIN SESSION
# =================================================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =================================================
# RULES (SAFE STRING)
# =================================================
RULES_HTML = """
<div style="background-color:#f8f9fa;padding:25px;border-radius:14px;border-left:6px solid #1f77b4;max-height:80vh;overflow-y:auto;">
<h2>🏸 Mathi Gang Badminton Tournament</h2>
<h3>Official Rules & Competition Format</h3>
<hr>
<ul>
<li><b>Format:</b> League + Knockout</li>
<li>Each team plays once against every other team</li>
<li>3 fixed doubles pairs per team</li>
<li>3 matches per tie – win 2 to win tie</li>
<li>Best of 3 sets, 21 points, win by 2</li>
<li>At 29–29, first to 30 wins</li>
<li>Top 2 teams qualify for Final</li>
<li>No coaching during rallies</li>
<li>No equipment abuse or arguing</li>
</ul>
<p style="font-size:13px;color:#555;">✅ Aligned with international badminton standards</p>
</div>
"""

# =================================================
# TEAM DATA + LOGOS
# =================================================
teams_data = {
    "Smash Titans": ["Omkar","Nishit","Ganesh","Sandeep W","Amit","Jayant"],
    "Quantum Force": ["Rajendra","Aniket","Deepak L","Rahul","Manmohan","Prashant"],
    "Racket Scientists": ["Kiran","Kaustubh","Piyush","Pradyum","Amol S","Amol P"],
    "Net Ninjas": ["Jaswanth","Sandeepk","Ritesh","Vikram","Pramod","Deepak T"]
}

team_logos = {
    "Smash Titans": "Logo/smash_titans.jpeg",
    "Quantum Force": "Logo/quantum_force.jpeg",
    "Racket Scientists": "Logo/racket_scientists.jpeg",
    "Net Ninjas": "Logo/net_ninjas.jpeg"
}

def show_logo(team, width=60):
    path = team_logos.get(team)
    if path and os.path.exists(path):
        st.image(path, width=width)
    else:
        st.write("🖼️")

# =================================================
# DATA LOADERS
# =================================================
@st.cache_data
def load_fixtures():
    with open("data/fixtures.json", "r") as f:
        return json.load(f)

def load_results():
    try:
        with open("data/results.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_results(data):
    with open("data/results.json", "w") as f:
        json.dump(data, f, indent=2)

fixtures = load_fixtures()
results = load_results()

# =================================================
# MENU
# =================================================
menu = st.radio(
    "Navigate",
    [
        "Home",
        "Teams",
        "Fixtures",
        "Team Standings",
        "Player Standings",
        "Final",
        "Enter Results",
        "Admin Login"
    ],
    horizontal=True
)

# =================================================
# HOME
# =================================================
if menu == "Home":
    st.markdown(RULES_HTML, unsafe_allow_html=True)

# =================================================
# TEAMS
# =================================================
elif menu == "Teams":
    st.subheader("👥 Team Combinations")
    for team, players in teams_data.items():
        c1, c2 = st.columns([1,5])
        with c1:
            show_logo(team, 80)
        with c2:
            st.subheader(team)
            for p in players:
                st.write(f"• {p}")
        st.divider()

# =================================================
# FIXTURES
# =================================================
elif menu == "Fixtures":
    st.subheader("📅 Fixtures")
    for tie in fixtures:
        c1, c2, c3 = st.columns([1,4,1])
        with c1:
            show_logo(tie["team_a"])
        with c2:
            st.subheader(f"{tie['team_a']}  VS  {tie['team_b']}")
        with c3:
            show_logo(tie["team_b"])
        for i, m in enumerate(tie["matches"], 1):
            st.write(f"Match {i}: {m[0]} vs {m[1]}")
        st.divider()

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
            if pwd == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.is_admin = True
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Incorrect password")

# =================================================
# ENTER RESULTS (ADMIN ONLY)
# =================================================
elif menu == "Enter Results":
    st.subheader("📝 Enter Match Results")

    if not st.session_state.is_admin:
        st.warning("🔒 Admin access required")
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
                c1, c2 = st.columns(2)
                with c1:
                    a = st.number_input(f"Set {s+1} – {tie['team_a']}", 0, 30, key=f"a{m}{s}")
                with c2:
                    b = st.number_input(f"Set {s+1} – {tie['team_b']}", 0, 30, key=f"b{m}{s}")
                if a or b:
                    sets.append([a, b])

            match_results.append({"sets": sets})

        if st.button("✅ Save Results"):
            results = [r for r in results if r["tie_id"] != tie["tie_id"]]
            results.append({
                "tie_id": tie["tie_id"],
                "team_a": tie["team_a"],
                "team_b": tie["team_b"],
                "matches": match_results
            })
            save_results(results)
            st.success("✅ Results saved")

# =================================================
# TEAM STANDINGS
# =================================================
elif menu == "Team Standings":
    st.subheader("📊 Team Standings")

    if not results:
        st.warning("No results entered yet.")
    else:
        teams = {t["team_a"] for t in fixtures} | {t["team_b"] for t in fixtures}
        S = {t: {"Played":0,"Won":0,"Points":0,"Sets Won":0,"Sets Lost":0} for t in teams}

        for r in results:
            ta, tb = r["team_a"], r["team_b"]
            S[ta]["Played"] += 1
            S[tb]["Played"] += 1
            aw = bw = 0

            for match in r["matches"]:
                a_sets = b_sets = 0
                for a, b in match["sets"]:
                    if a > b:
                        a_sets += 1
                        S[ta]["Sets Won"] += 1
                        S[tb]["Sets Lost"] += 1
                    else:
                        b_sets += 1
                        S[tb]["Sets Won"] += 1
                        S[ta]["Sets Lost"] += 1
                if a_sets > b_sets:
                    aw += 1
                else:
                    bw += 1

            if aw >= 2:
                S[ta]["Won"] += 1
                S[ta]["Points"] += 2
            else:
                S[tb]["Won"] += 1
                S[tb]["Points"] += 2

        df = pd.DataFrame.from_dict(S, orient="index")
        df["Set Diff"] = df["Sets Won"] - df["Sets Lost"]
        df = df.sort_values(by=["Points","Set Diff"], ascending=False)
        st.dataframe(df, width="stretch")

# =================================================
# INDIVIDUAL PLAYER STANDINGS
# =================================================
elif menu == "Player Standings":
    st.subheader("👤 Individual Player Standings")

    stats = defaultdict(lambda: {"Team":"","Played":0,"Won":0,"Points":0,"Form":deque(maxlen=5)})

    for r in results:
        fixture = next(f for f in fixtures if f["tie_id"] == r["tie_id"])
        for i, match in enumerate(r["matches"]):
            pair_a = fixture["matches"][i][0].split("/")
            pair_b = fixture["matches"][i][1].split("/")

            a_sets = b_sets = 0
            for a, b in match["sets"]:
                if a > b:
                    a_sets += 1
                else:
                    b_sets += 1

            a_win = a_sets > b_sets

            for p in pair_a:
                p = p.strip()
                stats[p]["Team"] = r["team_a"]
                stats[p]["Played"] += 1
                stats[p]["Form"].append("✅" if a_win else "❌")
                if a_win:
                    stats[p]["Won"] += 1
                    stats[p]["Points"] += 2

            for p in pair_b:
                p = p.strip()
                stats[p]["Team"] = r["team_b"]
                stats[p]["Played"] += 1
                stats[p]["Form"].append("✅" if not a_win else "❌")
                if not a_win:
                    stats[p]["Won"] += 1
                    stats[p]["Points"] += 2

    dfp = pd.DataFrame.from_dict(stats, orient="index")
    dfp["Recent Form"] = dfp["Form"].apply(lambda x: " ".join(x))
    dfp = dfp.sort_values(by=["Points","Won"], ascending=False)
    st.dataframe(dfp[["Team","Played","Won","Points","Recent Form"]], width="stretch")

# =================================================
# FINAL (TOP 2 TEAMS)
# =================================================
elif menu == "Final":
    st.subheader("🏆 Final")

    if not results:
        st.warning("Final will be available after league matches.")
    else:
        df = pd.read_json("data/results.json")
        standings = {}
        for r in results:
            standings[r["team_a"]] = standings.get(r["team_a"],0) + 2
            standings[r["team_b"]] = standings.get(r["team_b"],0)

        finalists = sorted(standings, key=standings.get, reverse=True)[:2]

        c1, c2, c3 = st.columns([1,4,1])
        with c1:
            show_logo(finalists[0],80)
        with c2:
            st.subheader(f"{finalists[0]}  VS  {finalists[1]}")
        with c3:
            show_logo(finalists[1],80)

        st.info("🏸 Best of 3 sets — Championship Final")
