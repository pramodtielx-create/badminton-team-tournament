import streamlit as st
import json
import pandas as pd
import os

st.set_page_config(page_title="🏸 Team Badminton Tournament", layout="wide")

FIXTURE_FILE = "data/fixtures.json"
RESULTS_FILE = "data/results.json"

# Load fixtures
with open(FIXTURE_FILE) as f:
    fixtures = json.load(f)

# Initialize results
if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "w") as f:
        json.dump([], f)

with open(RESULTS_FILE) as f:
    results = json.load(f)

teams = sorted(
    set([f["team_a"] for f in fixtures] + [f["team_b"] for f in fixtures])
)

st.title("🏸 Team Badminton Tournament")
st.caption("Format: 3 matches per tie • Team wins if it wins 2 out of 3")

tabs = st.tabs(["📝 Enter Results", "📊 Standings"])

# ---------------------------
# ENTER RESULTS
# ---------------------------
with tabs[0]:
    tie = st.selectbox(
        "Select Tie",
        fixtures,
        format_func=lambda x: f'Tie {x["tie_id"]}: {x["team_a"]} vs {x["team_b"]}'
    )

    st.markdown(
        f"""
        **Toss:** {tie['toss']}  
        **Service:** {tie['service']}
        """
    )

    winners = []

    for i, match in enumerate(tie["matches"]):
        winner = st.radio(
            f"Match {i+1}: {match[0]}  vs  {match[1]}",
            options=[tie["team_a"], tie["team_b"]],
            horizontal=True,
            key=f"{tie['tie_id']}_m{i}"
        )
        winners.append(winner)

    if st.button("✅ Save Tie Result"):
        team_a_wins = winners.count(tie["team_a"])
        team_b_wins = winners.count(tie["team_b"])
        tie_winner = tie["team_a"] if team_a_wins >= 2 else tie["team_b"]

        results.append({
            "tie_id": tie["tie_id"],
            "team_a": tie["team_a"],
            "team_b": tie["team_b"],
            "match_winners": winners,
            "winner": tie_winner
        })

        with open(RESULTS_FILE, "w") as f:
            json.dump(results, f, indent=2)

        st.success(f"🏆 {tie_winner} wins the tie!")

# ---------------------------
# STANDINGS
# ---------------------------
with tabs[1]:
    standings = {t: {"Played": 0, "Won": 0, "Lost": 0} for t in teams}

    for r in results:
        standings[r["team_a"]]["Played"] += 1
        standings[r["team_b"]]["Played"] += 1
        standings[r["winner"]]["Won"] += 1

        loser = r["team_b"] if r["winner"] == r["team_a"] else r["team_a"]
        standings[loser]["Lost"] += 1

    df = pd.DataFrame.from_dict(standings, orient="index")
    df = df.sort_values(by="Won", ascending=False)

    st.dataframe(df, use_container_width=True)

  st.subheader("✅ Qualified Teams (Top 2)")

if df["Won"].max() == 0:
    st.info("No teams have qualified yet. Enter match results to determine qualifiers.")
else:
    qualified = df[df["Won"] > 0].head(2)
    for team in qualified.index:
        st.success(team)

