import streamlit as st
import json
import pandas as pd
import os

RULES_HTML = """
<div style="
    background-color:#f8f9fa;
    padding:25px;
    border-radius:14px;
    border-left:6px solid #1f77b4;
    max-height:80vh;
    overflow-y:auto;
">

<h2>🏸 Mathi Gang Badminton Tournament</h2>
<h3>Official Rules & Competition Format</h3>

<hr>

<h4>1. Tournament Format</h4>
<ul>
<li>The tournament will be conducted in a <b>League + Knockout</b> format.</li>
<li><b>League Stage:</b>
<ul>
<li>Every team plays <b>once against every other team</b>.</li>
<li>Each team forms <b>three (3) fixed doubles pairs</b>.</li>
<li>Each player may play <b>only once against a given opponent team</b>.</li>
<li>Equal match participation unless injured or unavailable.</li>
</ul>
</li>
<li><b>Team Tie:</b>
<ul>
<li>Each tie consists of <b>3 matches</b>.</li>
<li>Winning <b>2 of 3</b> wins the tie.</li>
</ul>
</li>
<li><b>Toss:</b> Toss winner submits pair first.</li>
</ul>

<hr>

<h4>2. Match & Scoring Rules</h4>
<ul>
<li>Best of <b>3 sets</b>.</li>
<li>Each set to <b>21 points</b>.</li>
<li>Must win by <b>2 clear points</b>.</li>
<li>At <b>29–29</b>, first to <b>30</b> wins.</li>
</ul>

<hr>

<h4>3. League Ranking Criteria</h4>
<ol>
<li>Ties Won</li>
<li>Set Difference (Won − Lost)</li>
<li>Points Difference (For − Against)</li>
<li>Better points ratio</li>
</ol>

<hr>

<h4>4. Qualification</h4>
<ul>
<li><b>Top 4 teams</b> qualify for semifinals.</li>
<li>SF1: Rank 1 vs Rank 4</li>
<li>SF2: Rank 2 vs Rank 3</li>
</ul>

<hr>

<h4>5. Knockout Rules</h4>
<ul>
<li>Best of 3 sets</li>
<li>Same scoring rules apply</li>
</ul>

<hr>

<h4>6. On‑Court Rules (International Standard)</h4>
<ul>
<li>1‑minute warm‑up</li>
<li>60‑second interval at 11 points</li>
<li>Switch sides after each set</li>
<li>In 3rd set, side change at 11 points on request</li>
</ul>

<hr>

<h4>7. Substitution</h4>
<ul>
<li>Allowed only for injury or unavailability</li>
<li>From approved substitute pool</li>
</ul>

<hr>

<h4>8. Conduct</h4>
<ul>
<li>No equipment abuse</li>
<li>No arguing with officials</li>
<li>No coaching during rallies</li>
</ul>

<hr>

<h4>9. Final Authority</h4>
<ul>
<li>Organizers’ decisions are final</li>
</ul>

<p style="font-size:13px;color:#555;">
✅ Rules aligned with international badminton standards.
</p>

</div>
"""

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
            padding:25px;
            border-radius:14px;
            border-left:6px solid #1f77b4;
            max-height:80vh;
            overflow-y:auto;
        ">

        <h2>🏸 Mathi Gang Badminton Tournament</h2>
        <h3>Official Rules & Competition Format</h3>

        <hr>

        <h4>1. Tournament Format</h4>
        <ul>
            <li>The tournament will be conducted in a <b>League + Knockout</b> format.</li>
            <li><b>League Stage:</b>
                <ul>
                    <li>Every team will play <b>once against every other team</b>.</li>
                    <li>Each team must form <b>three (3) fixed and unique doubles pairs</b>.</li>
                    <li>Each player may play <b>only once against a given opponent team</b>.</li>
                    <li>All players are expected to play an <b>equal number of matches</b>, unless injured or officially unavailable.</li>
                </ul>
            </li>
            <li><b>Team Tie Structure:</b>
                <ul>
                    <li>Each team tie consists of <b>three doubles matches</b>.</li>
                    <li>The team winning <b>at least two (2) out of three (3) matches</b> wins the tie.</li>
                </ul>
            </li>
            <li><b>Toss Rule:</b>
                <ul>
                    <li>The toss winner decides which team submits their pair first.</li>
                    <li>The opposing team then submits their pair in response.</li>
                </ul>
            </li>
        </ul>

        <hr>

        <h4>2. Match & Scoring Rules</h4>
        <ul>
            <li>All matches are played as <b>Best of Three (3) sets</b>.</li>
            <li>Each set is played to <b>21 points</b>.</li>
            <li>A side must win by a <b>minimum margin of two (2) points</b>.</li>
            <li>If the score reaches <b>20–20</b>, play continues until a two‑point lead is achieved.</li>
            <li><b>Maximum cap (international standard):</b>
                <ul>
                    <li>If the score reaches <b>29–29</b>, the side scoring the <b>30th point</b> wins the set.</li>
                </ul>
            </li>
        </ul>

        <hr>

        <h4>3. League Points & Ranking Criteria</h4>
        <ul>
            <li><b>Match Win (Pair Level):</b> 2 points</li>
            <li><b>Team Tie Win:</b> Counts as one tie win in league standings</li>
            <li>League standings are ranked using the following criteria (in order):
                <ol>
                    <li>Total number of <b>ties won</b></li>
                    <li><b>Set Difference</b> = Sets Won − Sets Lost</li>
                    <li><b>Points Difference</b> = Points For − Points Against</li>
                    <li><b>Better points ratio</b> (Points For ÷ Points Against)</li>
                </ol>
            </li>
        </ul>

        <hr>

        <h4>4. Qualification Rules</h4>
        <ul>
            <li>The <b>Top Four (4) teams</b> from the league stage qualify for the <b>Knockout Stage</b>.</li>
            <li>Knockout seeding is as follows:
                <ul>
                    <li><b>Semi‑Final 1:</b> Rank 1 vs Rank 4</li>
                    <li><b>Semi‑Final 2:</b> Rank 2 vs Rank 3</li>
                </ul>
            </li>
        </ul>

        <hr>

        <h4>5. Knockout Stage Rules</h4>
        <ul>
            <li>All knockout matches are played as <b>Best of Three (3) sets</b>.</li>
            <li>Scoring rules remain identical to league matches.</li>
            <li>No league points apply during knockout matches.</li>
            <li>The winning team advances; the losing team is eliminated.</li>
        </ul>

        <hr>

        <h4>6. On‑Court Match Rules (International Standard)</h4>
        <ul>
            <li><b>Warm‑up:</b> Maximum of <b>1 minute</b> before match commencement.</li>
            <li><b>Service Rule:</b> The winner of a set serves first in the next set.</li>
            <li><b>Mid‑Game Interval:</b>
                <ul>
                    <li>A <b>60‑second interval</b> is allowed when a side reaches <b>11 points</b> in any set.</li>
                </ul>
            </li>
            <li><b>Change of Ends:</b>
                <ul>
                    <li>Sides are changed after every completed set.</li>
                    <li>In the <b>third set</b>, when any side reaches <b>11 points</b>, either team may request a side change.</li>
                </ul>
            </li>
            <li><b>Scheduling:</b> Match schedules may be adjusted if earlier matches overrun.</li>
        </ul>

        <hr>

        <h4>7. Player Substitution</h4>
        <ul>
            <li>Substitution is allowed <b>only</b> in the case of:
                <ul>
                    <li>Injury</li>
                    <li>Medical or unavoidable unavailability</li>
                </ul>
            </li>
            <li>Replacement players must be selected from a <b>pre‑approved substitute pool</b>.</li>
            <li>No substitution is permitted for tactical or strategic advantage.</li>
        </ul>

        <hr>

        <h4>8. Conduct & Sportsmanship</h4>
        <ul>
            <li>All players must maintain <b>fair play, discipline, and respect</b> at all times.</li>
            <li><b>Strictly prohibited actions include:</b>
                <ul>
                    <li>Hitting rackets, nets, or equipment in anger</li>
                    <li>Arguing with umpires or tournament officials</li>
                </ul>
            </li>
            <li><b>Supporters and spectators:</b>
                <ul>
                    <li>Must not coach players during rallies</li>
                    <li>Must not interfere with officiating decisions</li>
                </ul>
            </li>
            <li>Repeated misconduct may result in:
                <ul>
                    <li>Point penalties</li>
                    <li>Match forfeiture</li>
                    <li>Tournament disqualification (at organizer’s discretion)</li>
                </ul>
            </li>
        </ul>

        <hr>

        <h4>9. Final Authority</h4>
        <ul>
            <li>The tournament organizers’ decisions are <b>final and binding</b>.</li>
            <li>Rules may be refined if required to ensure fairness, safety, or smooth conduct of the tournament.</li>
        </ul>


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

