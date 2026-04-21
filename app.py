import streamlit as st
import json
import pandas as pd
import os

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="🏸 Badminton Tournament", layout="wide")
st.title("🏸 Badminton Tournament")

# -------------------------------------------------
# FULL RULES (SAFE VARIABLE)
# -------------------------------------------------
RULES_HTML = """
<div style="background-color:#f8f9fa;padding:25px;border-radius:14px;border-left:6px solid #1f77b4;max-height:80vh;overflow-y:auto;">
<h2>🏸 Mathi Gang Badminton Tournament</h2>
<h3>Official Rules & Competition Format</h3>
<hr>

<h4>1. Tournament Format</h4>
<ul>
<li>League + Knockout format.</li>
<li>Each team plays once against every other team.</li>
<li>Each team forms 3 fixed doubles pairs.</li>
<li>Each player plays only once against an opponent team.</li>
<li>3 matches per tie; winning 2 wins the tie.</li>
<li>Toss decides which team submits their pair first.</li>
</ul>

<h4>2. Match & Scoring Rules</h4>
<ul>
<li>Best of 3 sets.</li>
<li>Each set to 21 points.</li>
<li>Win by 2 points.</li>
<li>At 29–29, first to 30 wins.</li>
</ul>

<h4>3. League Ranking</h4>
<ol>
<li>Ties Won</li>
<li>Set Difference</li>
<li>Points Difference</li>
<li>Points Ratio</li>
</ol>

<h4>4. Qualification</h4>
<ul>
<li>Top 4 teams qualify for semifinals.</li>
<li>SF1: Rank 1 vs Rank 4</li>
<li>SF2: Rank 2 vs Rank 3</li>
</ul>

<h4>5. Conduct</h4>
<ul>
<li>No equipment abuse.</li>
<li>No arguing with officials.</li>
<li>No coaching during rallies.</li>
</ul>

<p style="font-size:13px;color:#555;">✅ Rules aligned with international badminton standards.</p>
</div>
"""

# -------------------------------------------------
# TEAM DATA + LOGOS
# -------------------------------------------------
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

def show_logo(team, width=60):
    path = team_logos.get(team)
    if path and os.path.exists(path):
        st.image(path, width=width)
    else:
        st.write("🖼️")

# -------------------------------------------------
# DATA LOADERS
# -------------------------------------------------
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

# -------------------------------------------------
# MENU
# -------------------------------------------------
menu = st.radio(
    "Navigate",
    ["Home", "Teams", "Fixtures", "Enter Results", "Standings"],
    horizontal=True
)

# -------------------------------------------------
# HOME
# -------------------------------------------------
if menu == "Home":
    st.markdown(RULES_HTML, unsafe_allow_html=True)

# -------------------------------------------------
# TEAMS (SAFE RENDERING)
# -------------------------------------------------
elif menu == "Teams":
    st.subheader("👥 Team Combinations")

    for team, players in teams_data.items():
        col1, col2 = st.columns([1, 5])

        with col1:
            show_logo(team, 80)

        with col2:
            st.subheader(team)
            for p in players:
                st.write(f"• {p}")

        st.divider()

# -------------------------------------------------
# FIXTURES (VISIBLE + ALIGNED)
# -------------------------------------------------
elif menu == "Fixtures":
    st.subheader("📅 Fixtures")

    for tie in fixtures:
        col1, col2, col3 = st.columns([1, 4, 1])

        with col1:
            show_logo(tie["team_a"], 60)

        with col2:
            st.subheader(f"{tie['team_a']}  VS  {tie['team_b']}")

        with col3:
            show_logo(tie["team_b"], 60)

        for i, match in enumerate(tie["matches"], start=1):
            st.write(f"Match {i}: {match[0]} vs {match[1]}")

        st.divider()

# -------------------------------------------------
# ENTER RESULTS
# -------------------------------------------------
elif menu == "Enter Results":
    st.subheader("📝 Enter Results")

    tie = st.selectbox(
        "Select Tie",
        fixtures,
        format_func=lambda x: f"Tie {x['tie_id']} — {x['team_a']} vs {x['team_b']}"
    )

    match_results = []

    for m in range(3):
        st.markdown(f"### Match {m + 1}")
        sets = []

        for s in range(3):
            col1, col2 = st.columns(2)

            with col1:
                a = st.number_input(f"Set {s+1} – {tie['team_a']}", 0, 30, key=f"a{m}{s}")
            with col2:
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

# -------------------------------------------------
# STANDINGS
# -------------------------------------------------
elif menu == "Standings":
    st.subheader("📊 Team Standings")

    if not results:
        st.warning("No results entered yet.")
    else:
        teams = {t["team_a"] for t in fixtures} | {t["team_b"] for t in fixtures}
        S = {t: {"Played":0,"Won":0,"Lost":0,"Points":0,"Sets Won":0,"Sets Lost":0,"Points Won":0,"Points Lost":0} for t in teams}

        for r in results:
            ta, tb = r["team_a"], r["team_b"]
            S[ta]["Played"] += 1
            S[tb]["Played"] += 1

            aw = bw = 0
            for match in r["matches"]:
                asw = bsw = 0
                for a, b in match["sets"]:
                    S[ta]["Points Won"] += a
                    S[ta]["Points Lost"] += b
                    S[tb]["Points Won"] += b
                    S[tb]["Points Lost"] += a

                    if a > b:
                        asw += 1
                        S[ta]["Sets Won"] += 1
                        S[tb]["Sets Lost"] += 1
                    else:
                        bsw += 1
                        S[tb]["Sets Won"] += 1
                        S[ta]["Sets Lost"] += 1

                if asw > bsw:
                    aw += 1
                else:
                    bw += 1

            if aw >= 2:
                S[ta]["Won"] += 1
                S[ta]["Points"] += 2
                S[tb]["Lost"] += 1
            else:
                S[tb]["Won"] += 1
