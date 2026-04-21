import streamlit as st
import json
import pandas as pd
import os

st.set_page_config(page_title="🏸 Team Badminton Tournament", layout="wide")

FIXTURE_FILE = "data/fixtures.json"
RESULTS_FILE = "data/results.json"

# ---------- LOAD DATA ----------
with open(FIXTURE_FILE, "r") as f:
    fixtures = json.load(f)

if not os.path.exists(RESULTS_FILE):
    with open(RESULTS_FILE, "w") as f:
        json.dump([], f)

with open(RESULTS_FILE, "r") as f:
    results = json.load(f)

teams = sorted(
    set([f["team_a"] for f in fixtures] + [f["team_b"] for f in fixtures])
)

# ---------- MENU STATE ----------
if "page" not in st.session_state:
    st.session_state.page = "Menu"

def menu_button(label):
    if st.button(label, use_container_width=True):
        st.session_state.page = label

# ---------- HEADER ----------
st.title("🏸 Team Badminton Tournament")

# ---------- MAIN MENU ----------
if st.session_state.page == "Menu":
    st.subheader("Choose a section")

    menu_button("Fixtures")
    menu_button("Results")
    menu_button("Teams")
    menu_button("Standings")
    menu_button("Leaderboard")

# ---------- FIXTURES ----------
elif st.session_state.page == "Fixtures":
    st.subheader("📅 Fixtures")

    for f in fixtures:
        st.markdown(
            f"""
            **Tie {f['tie_id']}**  
            {f['team_a']} vs {f['team_b']}  
            Toss: {f['toss']} | Service: {f['service']}
            """
        )

    st.button("⬅ Back to Menu", on_click=lambda: st.session_state.update(page="Menu"))

# ---------- RESULTS ENTRY ----------
elif st.session_state.page == "Results":
    st.subheader("📝 Enter Results")

    tie = st.selectbox(
        "Select Tie",
        fixtures,
        format_func=lambda x: f'Tie {x["tie_id"]}: {x["team_a"]} vs {x["team_b"]}'
    )

    winners = []
    for i, match in enumerate(tie["matches"]):
        winner = st.radio(
            f"Match {i+1}: {match[0]} vs {match[1]}",
            options=[tie["team_a"], tie["team_b"]],
            horizontal=True,
            key=f"result_{tie['tie_id']}_{i}"
        )
        winners.append(winner)

    if st.button("✅ Save Result"):
        winner = tie["team_a"] if winners.count(tie["team_a"]) >= 2 else tie["team_b"]

        results = [r for r in results if r["tie_id"] != tie["tie_id"]]
        results.append({
            "tie_id": tie["tie_id"],
            "team_a": tie["team_a"],
            "team_b": tie["team_b"],
            "winner": winner
        })

        with open(RESULTS_FILE, "w") as f:
            json.dump(results, f, indent=2)

        st.success(f"🏆 {winner} wins the tie!")

    st.button("⬅ Back to Menu", on_click=lambda: st.session_state.update(page="Menu"))

# ---------- TEAMS ----------
elif st.session_state.page == "Teams":
    st.subheader("👥 Teams")

    for team in teams:
        st.markdown(f"- **{team}**")

    st.button("⬅ Back to Menu", on_click=lambda: st.session_state.update(page="Menu"))

# ---------- STANDINGS ----------
elif st.session_state.page == "Standings":
    st.subheader("📊 Standings")

    standings = {t: {"Played": 0, "Won": 0, "Lost": 0} for t in teams}

    for r in results:
        standings[r["team_a"]]["Played"] += 1
        standings[r["team_b"]]["Played"] += 1
        standings[r["winner"]]["Won"] += 1

        loser = r["team_b"] if r["winner"] == r["team_a"] else r["team_a"]
        standings[loser]["Lost"] += 1

    df = pd.DataFrame.from_dict(standings, orient="index").sort_values(
        by="Won", ascending=False
    )

    st.dataframe(df, use_container_width=True)

    st.button("⬅ Back to Menu", on_click=lambda: st.session_state.update(page="Menu"))

# ---------- LEADERBOARD ----------
elif st.session_state.page == "Leaderboard":
    st.subheader("🏆 Leaderboard")

    df = pd.DataFrame.from_dict(
        {t: {"Wins": 0} for t in teams}, orient="index"
    )

    for r in results:
        df.loc[r["winner"], "Wins"] += 1

    df = df.sort_values(by="Wins", ascending=False)

    if df["Wins"].max() == 0:
        st.info("No leaderboard yet. Enter results.")
    else:
        for team in df.index:
            st.success(f"{team} — {df.loc[team, 'Wins']} wins")

    st.button("⬅ Back to Menu", on_click=lambda: st.session_state.update(page="Menu"))
