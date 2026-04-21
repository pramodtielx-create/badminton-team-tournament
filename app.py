import streamlit as st
import json
import pandas as pd

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(
    page_title="🏸 Badminton Tournament",
    layout="wide"
)

st.title("🏸 Badminton Tournament")

# -------------------------------------------------
# TEAM DATA + LOGOS (JPEG)
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
    "Smash Titans": "assets/logos/smash_titans.jpeg",
    "Quantum Force": "assets/logos/quantum_force.jpeg",
    "Racket Scientists": "assets/logos/racket_scientists.jpeg",
    "Net Ninjas": "assets/logos/net_ninjas.jpeg"
}

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
    st.success("✅ Tournament system is running correctly")
    st.write("Use the menu above to navigate through the tournament.")

# -------------------------------------------------
# TEAMS (WITH LOGOS)
# -------------------------------------------------
elif menu == "Teams":
    st.subheader("👥 Team Combinations")

    cols = st.columns(2)
    for idx, (team, players) in enumerate(teams_data.items()):
        with cols[idx % 2]:
            col_logo, col_name = st.columns([1, 4])

            with col_logo:
                st.image(team_logos[team], width=80)

            with col_name:
                st.markdown(f"### {team}")

            for p in players:
                st.write(f"• {p}")

# -------------------------------------------------
# FIXTURES (WITH LOGOS)
# -------------------------------------------------
elif menu == "Fixtures":
    st.subheader("📅 Fixtures")

    for tie in fixtures:
        col1, col2, col3 = st.columns([1, 3, 3])

        with col1:
            st.image(team_logos[tie["team_a"]], width=60)
            st.image(team_logos[tie["team_b"]], width=60)

        with col2:
            st.markdown(f"### {tie['team_a']}")

        with col3:
            st.markdown(f"### {tie['team_b']}")

        for i, match in enumerate(tie["matches"], start=1):
            st.write(f"Match {i}: {match[0]}  vs  {match[1]}")

        st.divider()

# -------------------------------------------------
# ENTER RESULTS
# -------------------------------------------------
elif menu == "Enter Results":
    st.subheader("📝 Enter Match Results (Best of 3 Sets)")

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
                    min_value=0,
                    max_value=30,
                    key=f"a_{tie['tie_id']}_{m}_{s}"
                )

            with col2:
                b = st.number_input(
                    f"Set {s + 1} – {tie['team_b']}",
                    min_value=0,
                    max_value=30,
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
        st.success("✅ Results saved successfully")

# -------------------------------------------------
# STANDINGS (WITH LOGOS)
# -------------------------------------------------
elif menu == "Standings":
    st.subheader("📊 Team Standings")

    if len(results) == 0:
        st.warning("⚠️ No results entered yet. Enter results to see standings.")
    else:
        teams = set()
        for t in fixtures:
            teams.add(t["team_a"])
            teams.add(t["team_b"])

        standings = {
            team: {
                "Played": 0,
                "Won": 0,
                "Lost": 0,
                "Points": 0,
                "Sets Won": 0,
                "Sets Lost": 0,
                "Points Won": 0,
                "Points Lost": 0
            }
            for team in teams
        }

        for r in results:
            team_a = r["team_a"]
            team_b = r["team_b"]

            standings[team_a]["Played"] += 1
            standings[team_b]["Played"] += 1

            team_a_match_wins = 0
            team_b_match_wins = 0

            for match in r["matches"]:
                a_sets = 0
                b_sets = 0

                for s in match["sets"]:
                    a_pts, b_pts = s

                    standings[team_a]["Points Won"] += a_pts
                    standings[team_a]["Points Lost"] += b_pts
                    standings[team_b]["Points Won"] += b_pts
                    standings[team_b]["Points Lost"] += a_pts

                    if a_pts > b_pts:
                        a_sets += 1
                        standings[team_a]["Sets Won"] += 1
                        standings[team_b]["Sets Lost"] += 1
                    else:
                        b_sets += 1
                        standings[team_b]["Sets Won"] += 1
                        standings[team_a]["Sets Lost"] += 1

                if a_sets > b_sets:
                    team_a_match_wins += 1
                else:
                    team_b_match_wins += 1

            if team_a_match_wins >= 2:
                standings[team_a]["Won"] += 1
                standings[team_a]["Points"] += 2
                standings[team_b]["Lost"] += 1
            else:
                standings[team_b]["Won"] += 1
                standings[team_b]["Points"] += 2
                standings[team_a]["Lost"] += 1

        df = pd.DataFrame.from_dict(standings, orient="index")
        df["Set Diff"] = df["Sets Won"] - df["Sets Lost"]
        df["Point Diff"] = df["Points Won"] - df["Points Lost"]

        df = df.sort_values(
            by=["Points", "Set Diff", "Point Diff"],
            ascending=False
        )

        for team in df.index:
            col1, col2 = st.columns([1, 8])

            with col1:
                st.image(team_logos[team], width=50)

            with col2:
                row = df.loc[team]
                st.markdown(
                    f"""
                    **{team}**  
                    Played: {row['Played']} | Won: {row['Won']} | Points: {row['Points']}  
                    Set Diff: {row['Set Diff']} | Point Diff: {row['Point Diff']}
                    """
                )

            st.divider()
