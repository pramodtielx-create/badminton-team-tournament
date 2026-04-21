import streamlit as st
import json
import pandas as pd
import os

st.set_page_config(
    page_title="🏸 Team Badminton Tournament",
    layout="wide"
)

FIXTURE_FILE = "data/fixtures.json"
RESULTS_FILE = "data/results.json"

# Load fixtures
with open(FIXTURE_FILE, "r") as f:
    fixtures = json.load(f)

# Ensure results file exists
if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "w") as f:
        json.dump([], f)

with open(RESULTS_FILE, "r") as f:
    results = json.load(f)

# Team list
teams = sorted(
    set(
        [f["team_a"] for f in fixtures] +
        [f["team_b"] for f in fixtures]
    )
)

st.title("🏸 Team Badminton Tournament")
st.caption("Format: 3 matches per tie • Team wins if it wins 2 out of 3")

tab_results, tab_standings = st.tabs(["📝 Enter Results", "📊 Standings"])

# -------------------- ENTER RESULTS --------------------
with tab_results:
    tie = st.selectbox(
        "Select Tie",
        fixtures,
        format_func=lambda x: f'Tie {x["tie_id"]}: {x["team_a"]} vs {x["team_b"]}'
    )

    st.markdown(
        f"**Toss:** {tie['toss']}  \n"
        f"**Service:** {tie['service']}"
    )

    winners = []

    for i, match in enumerate(tie["matches"]):
        winner = st.radio(
            f"Match {i + 1}: {match[0]} vs {match[1]}",
            options=[tie["team_a"], tie["team_b"]],
            horizontal=True,
            key=f"tie_{tie['tie_id']}_match_{i}"
        )
        winners.append(winner)

    if st.button("✅ Save Tie Result"):
        tie_winner = (
            tie["team_a"]
            if winners.count(tie["team_a"]) >= 2
            else tie["team_b"]
        )

        # Prevent duplicate tie entry
        results = [r for r in results if r["tie_id"] != tie["tie_id"]]

        results.append({
            "tie_id": tie["tie_id"],
            "team_a": tie["team_a"],
            "team_b": tie["team_b"],
            "winner": tie_winner
        })

        with open(RESULTS_FILE, "w") as f:
            json.dump(results, f, indent=2)

        st.success(f"🏆 {tie_winner} wins the tie!")

# -------------------- STANDINGS --------------------
with tab_standings:
    standings = {t: {"Played": 0, "Won": 0, "Lost": 0} for t in teams}

    for r in results:
        standings[r["team_a"]]["Played"] += 1
        standings[r["team_b"]]["Played"] += 1
        standings[r["winner"]]["Won"] += 1

        loser = r["team_b"] if r["winner"] == r["team_a"] else r["team_a"]
        standings[loser]["Lost"] += 1

    df = pd.DataFrame.from_dict(standings, orient="index")

    if not df.empty:
        df = df.sort_values(by="Won", ascending=False)

    st.dataframe(df, use_container_width=True)

    st.subheader("✅ Qualified Teams (Top 2)")

    if df["Won"].max() == 0:
        st.info("No teams have qualified yet. Enter results to determine qualifiers.")
    else:
        qualified = df[df["Won"] > 0].head(2)
        for team in qualified.index:
            st.success(team)
