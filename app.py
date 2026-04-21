import streamlit as st
import json
import os
import pandas as pd
from collections import defaultdict, deque
RULES_HTML = """
<div style="background-color:#f8f9fa;padding:25px;border-radius:14px;
border-left:6px solid #1f77b4;max-height:80vh;overflow-y:auto;">
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
<li>Top 2 teams qualify for Finals.</li>
<li>Bottom 2 play for 3rd place.</li>
</ul>

<h4>5. Conduct</h4>
<ul>
<li>No equipment abuse.</li>
<li>No arguing with officials.</li>
<li>No coaching during rallies.</li>
</ul>

<p style="font-size:13px;color:#555;">
✅ Rules aligned with international badminton standards.
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
elif menu == "Results":
    st.subheader("📊 Match Results")

    results = load_json("data/results.json", [])

    if not results:
        st.warning("No results entered yet.")
    else:
        for r in results:
            c1, c2, c3 = st.columns([1,4,1])

            with c1:
                show_logo(r["team_a"])

            with c2:
                st.subheader(f"{r['team_a']} VS {r['team_b']}")

            with c3:
                show_logo(r["team_b"])

            for i, m in enumerate(r["matches"], start=1):
                if m.get("sets"):
                    score = " | ".join(
                        f"{s[0]}-{s[1]}" for s in m["sets"]
                    )
                    st.write(f"Match {i}: {score}")
                else:
                    st.write(f"Match {i}: —")

            st.divider()
#================================================================
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
            tie_result = next(
                (
                    r for r in results
                    if r["tie_id"] == tie["tie_id"]
                ),
                {
                    "tie_id": tie["tie_id"],
                    "team_a": tie["team_a"],
                    "team_b": tie["team_b"],
                    "matches": [{}, {}, {}]
                }
            )

            for idx, match in enumerate(match_results):
                if match["sets"]:
                    tie_result["matches"][idx] = match

            updated_results = [
                r for r in results
                if r["tie_id"] != tie["tie_id"]
            ]
            updated_results.append(tie_result)

            save_json("data/results.json", updated_results)

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
            "Won": 0,
            "Points": 0
        })

        for r in results:
            ta, tb = r["team_a"], r["team_b"]
            table[ta]["Played"] += 1
            table[tb]["Played"] += 1

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

                if a_sets > b_sets:
                    a_match_wins += 1
                else:
                    b_match_wins += 1

            if a_match_wins >= 2:
                table[ta]["Won"] += 1
                table[ta]["Points"] += 2
            elif b_match_wins >= 2:
                table[tb]["Won"] += 1
                table[tb]["Points"] += 2

        df = pd.DataFrame.from_dict(table, orient="index")
        df = df.sort_values(by=["Points", "Won"], ascending=False)

        st.dataframe(df, width="stretch")
#=================================================================================
elif menu == "Player Standings":
    st.subheader("👤 Individual Player Standings")

    results = load_json("data/results.json", [])

    stats = defaultdict(lambda: {
        "Team": "",
        "Played": 0,
        "Won": 0,
        "Points": 0,
        "Form": deque(maxlen=5)
    })

    # Initialize all players with 0
    for team, players in teams_data.items():
        for p in players:
            stats[p]["Team"] = team

    # Apply results
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

            a_sets = 0
            b_sets = 0

            for a, b in m["sets"]:
                if a > b:
                    a_sets += 1
                else:
                    b_sets += 1

            a_win = a_sets > b_sets

            for p in pair_a:
                p = p.strip()
                stats[p]["Played"] += 1
                stats[p]["Form"].append("✅" if a_win else "❌")
                if a_win:
                    stats[p]["Won"] += 1
                    stats[p]["Points"] += 2

            for p in pair_b:
                p = p.strip()
                stats[p]["Played"] += 1
                stats[p]["Form"].append("✅" if not a_win else "❌")
                if not a_win:
                    stats[p]["Won"] += 1
                    stats[p]["Points"] += 2

    dfp = pd.DataFrame.from_dict(stats, orient="index")
    dfp["Recent Form"] = dfp["Form"].apply(lambda x: " ".join(list(x)))

    dfp = dfp.sort_values(
        by=["Points", "Won", "Played"],
        ascending=[False, False, True]
    )

    st.dataframe(
        dfp[["Team", "Played", "Won", "Points", "Recent Form"]],
        width="stretch"
    )

    if dfp["Points"].max() > 0:
        pot = dfp.index[0]
        st.success(f"🥇 Player of the Tournament: **{pot}** ({dfp.loc[pot,'Team']})")
    else:
        st.info("Player of the Tournament will be decided after matches are played.")
