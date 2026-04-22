import streamlit as st
import json
import os
import pandas as pd
from collections import defaultdict, deque
def calculate_potm(match_sets, pair_a, pair_b):
    """
    Player of the Match (International Standard – Club Level)
    - Player must be from winning pair
    - Decided by set wins, tie-break by point difference
    """

    a_sets = 0
    b_sets = 0
    a_point_diff = 0
    b_point_diff = 0

    for a, b in match_sets:
        if a > b:
            a_sets += 1
        else:
            b_sets += 1

        a_point_diff += (a - b)
        b_point_diff += (b - a)

    # Winning pair decides POTM
    if a_sets > b_sets:
        return pair_a[0].strip()
    elif b_sets > a_sets:
        return pair_b[0].strip()
    else:
        # Rare tie case → use point dominance
        return pair_a[0].strip() if a_point_diff >= b_point_diff else pair_b[0].strip()
##################################################################3
RULES_HTML = """
<div style="background-color:#f8f9fa;padding:25px;border-radius:14px;
border-left:6px solid #1f77b4;max-height:80vh;overflow-y:auto;">

<h2>🏸 House League Badminton Tournament</h2>
<h3>Official Rules & Competition Format</h3>
<hr>

<h4>1. Tournament Format</h4>
<ul>
<li>League + Knockout format.</li>
<li>Each team plays once against every other team.</li>
<li>Each team forms <b>3 fixed doubles pairs</b> for the entire league stage.</li>
<li>Each player plays <b>only once against an opponent team</b>.</li>
<li>Each tie consists of <b>3 matches</b>; the team winning <b>2 matches</b> wins the tie.</li>
<li>Toss decides which team submits their pair first; the opposing team responds.</li>
</ul>

<h4>2. Match & Scoring Rules (BWF Standard)</h4>
<ul>
<li>All matches are played as <b>Best of 3 sets</b>.</li>
<li>Each set is played to <b>21 points</b>.</li>
<li>A side must win by a <b>minimum 2‑point margin</b>.</li>
<li>If the score reaches <b>20–20</b>, play continues until a 2‑point lead is achieved.</li>
<li>If the score reaches <b>29–29</b>, the side scoring the <b>30th point wins the set</b>.</li>
</ul>

<h4>3. Service Rules (BWF Standard)</h4>
<ul>
<li>Service is delivered diagonally to the opponent’s service court.</li>
<li>At the moment of service:
  <ul>
    <li>The shuttle must be hit below the server’s waist.</li>
    <li>The racket shaft must point downward.</li>
    <li>Both feet of server and receiver must be stationary and within service courts.</li>
  </ul>
</li>
<li>Only the serving side can score points.</li>
</ul>

<h4>4. Intervals & Change of Ends</h4>
<ul>
<li>A <b>60‑second interval</b> is allowed when the leading score reaches <b>11 points</b> in each set.</li>
<li>Players change ends:
  <ul>
    <li>At the end of each set.</li>
    <li>In the <b>third set</b>, when one side reaches <b>11 points</b>.</li>
  </ul>
</li>
</ul>

<h4>5. League Ranking & Tie‑Break Criteria</h4>
<ol>
<li>Total <b>Ties Won</b></li>
<li><b>Set Difference</b> (Sets Won − Sets Lost)</li>
<li><b>Points Difference</b> (Points For − Points Against)</li>
<li><b>Points Ratio</b> (Points For ÷ Points Against)</li>
<li>If still tied, decision by tournament committee</li>
</ol>

<h4>6. Qualification</h4>
<ul>
<li>Top <b>2 teams</b> qualify directly for the <b>Final</b>.</li>
<li>Bottom <b>2 teams</b> play for <b>3rd and 4th place</b>.</li>
</ul>

<h4>7. Player Substitution</h4>
<ul>
<li>Substitution is allowed <b>only</b> in case of:
  <ul>
    <li>Injury</li>
    <li>Medical or unavoidable absence</li>
  </ul>
</li>
<li>Substitutes must come from a <b>pre‑approved pool</b>.</li>
<li>No substitution is allowed for tactical or strategic reasons.</li>
</ul>

<h4>8. Conduct & Code of Behaviour (BWF Aligned)</h4>
<ul>
<li>Players must display <b>fair play and sportsmanship</b> at all times.</li>
<li>The following are strictly prohibited:
  <ul>
    <li>Hitting rackets, nets, or shuttlecocks in anger</li>
    <li>Abusive language or gestures</li>
    <li>Arguing with umpires or organizers</li>
  </ul>
</li>
<li>Coaching during rallies is <b>not permitted</b>.</li>
<li>Spectators must not interfere with play or officiating.</li>
</ul>

<h4>9. Match Delays & Scheduling</h4>
<ul>
<li>Matches should begin at scheduled time.</li>
<li>Delays due to earlier matches overrunning may occur.</li>
<li>Organizers reserve the right to adjust schedules if required.</li>
</ul>

<h4>10. Final Authority</h4>
<ul>
<li>The tournament committee’s decision is <b>final and binding</b>.</li>
<li>Rules may be amended to ensure fairness, safety, or smooth conduct.</li>
</ul>

<p style="font-size:13px;color:#555;">
✅ These rules follow International Badminton Federation (BWF) Laws of Badminton and are adapted for house‑league competition.
</p>

</div>
"""
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
# TEAM DATA + LOGOS
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
    else:
        st.write("🖼️")

# =================================================
# DATA HELPERS
# =================================================
def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

fixtures = load_json("data/fixtures.json", [])
results = load_json("data/results.json", [])
final_result = load_json("data/final_result.json", {})

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
# TEAMS
# =================================================
elif menu == "Teams":
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
    for tie in fixtures:
        c1, c2, c3 = st.columns([1,4,1])
        with c1:
            show_logo(tie["team_a"])
        with c2:
            st.subheader(f"{tie['team_a']} VS {tie['team_b']}")
        with c3:
            show_logo(tie["team_b"])
        for i, m in enumerate(tie["matches"], 1):
            st.write(f"Match {i}: {m[0]} vs {m[1]}")
        st.divider()

# =================================================
# RESULTS (PUBLIC)
# =================================================

# =================================================
# RESULTS (PUBLIC – READ ONLY)
# =================================================
# =================================================
# RESULTS (PUBLIC – READ ONLY)
# =================================================
elif menu == "Results":
    st.subheader("📊 Match Results")

    results = load_json("data/results.json", [])

    if not results:
        st.warning("No results entered yet.")
    else:
        for r in results:
            c1, c2, c3 = st.columns([1, 4, 1])

            with c1:
                show_logo(r["team_a"])

            with c2:
                st.subheader(f"{r['team_a']} VS {r['team_b']}")

            with c3:
                show_logo(r["team_b"])

            for i, m in enumerate(r["matches"], start=1):
                if not m or "sets" not in m or not m["sets"]:
                    st.write(f"Match {i}: —")
                    continue

                score = " | ".join(f"{s[0]}-{s[1]}" for s in m["sets"])
                st.write(f"Match {i}: {score}")

                fixture = next(
                    f for f in fixtures if f["tie_id"] == r["tie_id"]
                )

                pair_a = fixture["matches"][i-1][0].split("/")
                pair_b = fixture["matches"][i-1][1].split("/")

                potm = calculate_potm(m["sets"], pair_a, pair_b)
                st.caption(f"🏅 Player of the Match: {potm}")

            st.divider()

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
            st.markdown(f"### Match {m + 1}")
            sets = []

            for s in range(3):
                c1, c2 = st.columns(2)

                with c1:
                    a = st.number_input(
                        f"{tie['team_a']} (Set {s + 1})",
                        min_value=0,
                        max_value=30,
                        key=f"a_{tie['tie_id']}_{m}_{s}"
                    )

                with c2:
                    b = st.number_input(
                        f"{tie['team_b']} (Set {s + 1})",
                        min_value=0,
                        max_value=30,
                        key=f"b_{tie['tie_id']}_{m}_{s}"
                    )

                if a > 0 or b > 0:
                    sets.append([a, b])

            match_results.append({"sets": sets})

        if st.button("✅ Save Results"):
            results = load_json("data/results.json", [])

            tie_result = next(
                (r for r in results if r["tie_id"] == tie["tie_id"]),
                {
                    "tie_id": tie["tie_id"],
                    "team_a": tie["team_a"],
                    "team_b": tie["team_b"],
                    "matches": [{}, {}, {}]
                }
            )

            for idx, match in enumerate(match_results):
                if match["sets"]:
                    tie_result["matches"][idx] = {"sets": match["sets"]}

            results = [r for r in results if r["tie_id"] != tie["tie_id"]]
            results.append(tie_result)

            save_json("data/results.json", results)

            st.success("✅ Results saved (previous matches preserved)")
            st.rerun()

#========================================================================
elif menu == "Team Standings":
    st.subheader("📊 Team Standings")

    results = load_json("data/results.json", [])

    if not results:
        st.warning("No results entered yet.")
    else:
        table = defaultdict(lambda: {
            "Played": 0,
            "Tie Wins": 0,
            "Match Wins": 0,
            "Match Losses": 0,
            "Points": 0
        })

        for r in results:
            ta, tb = r["team_a"], r["team_b"]

            a_match_wins = 0
            b_match_wins = 0

            for m in r["matches"]:
                if not m or "sets" not in m or not m["sets"]:
                    continue

                a_sets = 0
                b_sets = 0

                for a, b in m["sets"]:
                    if a > b:
                        a_sets += 1
                    else:
                        b_sets += 1

                # ✅ Count individual match result
                if a_sets > b_sets:
                    a_match_wins += 1
                    table[ta]["Match Wins"] += 1
                    table[tb]["Match Losses"] += 1
                else:
                    b_match_wins += 1
                    table[tb]["Match Wins"] += 1
                    table[ta]["Match Losses"] += 1

            # ✅ Played = total matches (wins + losses)
            table[ta]["Played"] = table[ta]["Match Wins"] + table[ta]["Match Losses"]
            table[tb]["Played"] = table[tb]["Match Wins"] + table[tb]["Match Losses"]

            # ✅ Tie winner
            if a_match_wins >= 2:
                table[ta]["Tie Wins"] += 1
                table[ta]["Points"] += 2
            elif b_match_wins >= 2:
                table[tb]["Tie Wins"] += 1
                table[tb]["Points"] += 2

        df = pd.DataFrame.from_dict(table, orient="index")
        df = df.sort_values(
            by=["Points", "Tie Wins", "Match Wins"],
            ascending=False
        )

        st.dataframe(df, width="stretch")

#=================================================================================
elif menu == "Player Standings":
    st.subheader("👤 Individual Player Standings")

    results = load_json("data/results.json", [])
    final_result = load_json("data/final_result.json", {})

    # ✅ Initialize all players with zero stats
    stats = defaultdict(lambda: {
        "Team": "",
        "Played": 0,
        "Match Wins": 0,
        "Set Diff": 0,
        "Point Diff": 0,
        "Final Bonus": 0
    })

    for team, players in teams_data.items():
        for p in players:
            stats[p]["Team"] = team

    # ✅ Apply league results (if any)
    for r in results:
        fixture = next(
            (f for f in fixtures if f["tie_id"] == r["tie_id"]),
            None
        )
        if not fixture:
            continue

        for i, m in enumerate(r["matches"]):
            if not m or "sets" not in m or not m["sets"]:
                continue

            pair_a = fixture["matches"][i][0].split("/")
            pair_b = fixture["matches"][i][1].split("/")

            a_sets = b_sets = 0
            a_pts = b_pts = 0

            for a, b in m["sets"]:
                a_pts += a
                b_pts += b
                if a > b:
                    a_sets += 1
                else:
                    b_sets += 1

            a_win = a_sets > b_sets

            for p in pair_a:
                p = p.strip()
                stats[p]["Played"] += 1
                stats[p]["Set Diff"] += (a_sets - b_sets)
                stats[p]["Point Diff"] += (a_pts - b_pts)
                if a_win:
                    stats[p]["Match Wins"] += 1

            for p in pair_b:
                p = p.strip()
                stats[p]["Played"] += 1
                stats[p]["Set Diff"] += (b_sets - a_sets)
                stats[p]["Point Diff"] += (b_pts - a_pts)
                if not a_win:
                    stats[p]["Match Wins"] += 1

    # ✅ Final match bonus (international standard)
    if final_result.get("sets"):
        finalists = final_result.get("finalists", [])
        if len(finalists) == 2:
            a_sets = sum(1 for a, b in final_result["sets"] if a > b)
            b_sets = sum(1 for a, b in final_result["sets"] if b > a)
            winner = finalists[0] if a_sets > b_sets else finalists[1]

            for p in teams_data.get(winner, []):
                stats[p]["Final Bonus"] = 1

    # ✅ Convert index to Player column
    dfp = pd.DataFrame.from_dict(stats, orient="index")
    dfp = dfp.reset_index().rename(columns={"index": "Player"})

    # ✅ Sort (international standard)
    dfp = dfp.sort_values(
        by=["Match Wins", "Set Diff", "Point Diff", "Final Bonus", "Played"],
        ascending=[False, False, False, False, True]
    )

    # ✅ Display (Team first, then Player)
    st.dataframe(
        dfp[["Team", "Player", "Played", "Match Wins", "Set Diff", "Point Diff", "Final Bonus"]],
        width="stretch"
    )

    # ✅ Player of the Tournament
    if results and dfp["Match Wins"].max() > 0:
        pot = dfp.iloc[0]["Player"]
        team = dfp.iloc[0]["Team"]
        st.success(f"🏆 Player of the Tournament: **{pot}** ({team})")
    else:
        st.info("Player of the Tournament will be decided once matches are played.")
