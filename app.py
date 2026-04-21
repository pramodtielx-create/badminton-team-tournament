import streamlit as st
import json
import pandas as pd
import os

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="🏸 Badminton Tournament",
    layout="wide"
)

st.title("🏸 Badminton Tournament")

# -------------------------------------------------
# TEAM DATA
# -------------------------------------------------
teams_data = {
    "Smash Titans": [
        "Omkar", "Nishit", "Ganesh",
        "Sandeep W", "Amit", "Jayant"
    ],
    "Quantum Force": [
        "Rajendra", "Aniket", "Deepak L",
        "Rahul", "Manmohan", "Prashant"
    ],
    "Racket Scientists": [
        "Kiran", "Kaustubh", "Piyush",
        "Pradyum", "Amol S", "Amol P"
    ],
    "Net Ninjas": [
        "Jaswanth", "Sandeepk", "Ritesh",
        "Vikram", "Pramod", "Deepak T"
    ]
}

team_logos = {
    "Smash Titans": "assets/Logos/smash_titans.jpeg",
    "Quantum Force": "assets/Logos/quantum_force.jpeg",
    "Racket Scientists": "assets/Logos/racket_scientists.jpeg",
    "Net Ninjas": "assets/Logos/net_ninjas.jpeg"
}

def show_logo(team, width=80):
    logo_path = team_logos.get(team)
    if logo_path and os.path.exists(logo_path):
        st.image(logo_path, width=width)
    else:
        st.markdown("🖼️ *(logo missing)*")

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
    st.markdown(
        """
        <div style="
            background-color:#f8f9fa;
            padding:20px;
            border-radius:12px;
            border-left:6px solid #1f77b4;
        ">
        <h2>🏸 Mathi Gang Badminton Tournament</h2>
        <h4>Official Rules & Format</h4>
        <ul>
            <li><b>Format:</b> League + Knockout</li>
            <li><b>League:</b> Every team plays all others</li>
            <li><b>Team Tie:</b> 3 matches per tie, win 2 to win tie</li>
            <li><b>Scoring:</b> Best of 3 sets, 21 points, 2‑point lead</li>
            <li><b>Qualification:</b> Top 4 teams to semifinals</li>
            <li><b>Knockouts:</b> Rank 1 vs 4, Rank 2 vs 3</li>
            <li><b>Player Rule:</b> Each player plays once per opponent team</li>
            <li><b>Conduct:</b> Fair play & sportsmanship mandatory</li>
        </ul>
        <p style="font-size:13px;color:#555;">
        📘 Full detailed rules are applied as per international badminton standards.
        </p>
        </div>
        """,
        unsafe_allow_html=True
    )

# -------------------------------------------------
# TEAMS
# -------------------------------------------------
elif menu == "Teams":
    st.subheader("👥 Team Combinations")

    cols = st.columns(2)
    for idx, (team, players) in enumerate(teams_data.items()):
        with cols[idx % 2]:
            col_logo, col_name = st.columns([1, 4])

            with col_logo:
                show_logo(team)

            with col_name:
                st.markdown(f"### {team}")

            for p in players:
                st.write(f"• {p}")

# -------------------------------------------------
# FIXTURES
# -------------------------------------------------
elif menu == "Fixtures":
  
    st.subheader("📅 Fixtures")

    for tie in fixtures:
        # Header row: Logo - Team A - VS - Team B - Logo
        col_logo_a, col_team_a, col_vs, col_team_b, col_logo_b = st.columns(
            [1, 3, 1, 3, 1]
        )

        with col_logo_a:
            show_logo(tie["team_a"], width=60)

        with col_team_a:
            st.markdown(
                f"<h3 style='text-align: right;'>{tie['team_a']}</h3>",
                unsafe_allow_html=True
            )

        with col_vs:
            st.markdown(
                "<h3 style='text-align: center;'>VS</h3>",
                unsafe_allow_html=True
            )

        with col_team_b:
            st.markdown(
                f"<h3 style='text-align: left;'>{tie['team_b']}</h3>",
                unsafe_allow_html=True
            )

        with col_logo_b:
            show_logo(tie["team_b"], width=60)

        # Matches
        st.markdown("---")
        for i, match in enumerate(tie["matches"], start=1):
            st.markdown(
                f"**Match {i}:** {match[0]}  vs  {match[1]}"
            )

        st.divider()


# -------------------------------------------------
# ENTER RESULTS
# -------------------------------------------------
elif menu == "Enter Results":
    st.subheader("📝 Enter Match Results")

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
                a = st.number_input(
                    f"Set {s + 1} – {tie['team_a']}",
                    min_value=0, max_value=30,
                    key=f"a_{tie['tie_id']}_{m}_{s}"
                )

            with col2:
                b = st.number_input(
                    f"Set {s + 1} – {tie['team_b']}",
                    min_value=0, max_value=30,
                    key=f"b_{tie['tie_id']}_{m}_{s}"
                )

            if a > 0 or b > 0:
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
        st.warning("⚠️ No results entered yet.")
    else:
        teams = {t["team_a"] for t in fixtures} | {t["team_b"] for t in fixtures}

        standings = {
            team: {
                "Played": 0, "Won": 0, "Lost": 0, "Points": 0,
                "Sets Won": 0, "Sets Lost": 0,
                "Points Won": 0, "Points Lost": 0
            }
            for team in teams
        }

        for r in results:
            ta, tb = r["team_a"], r["team_b"]
            standings[ta]["Played"] += 1
            standings[tb]["Played"] += 1

