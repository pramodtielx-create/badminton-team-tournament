import streamlit as st
import json
import pandas as pd
from calculations import analyze_results

st.set_page_config("🏸 Badminton Tournament", layout="wide")

fixtures = json.load(open("data/fixtures.json"))
results = json.load(open("data/results.json"))

teams = sorted(set([f["team_a"] for f in fixtures] + [f["team_b"] for f in fixtures]))

st.title("🏸 Badminton Tournament Dashboard")
st.caption("International Standard • Live Statistics")

menu = st.radio(
    "Choose Section",
    ["Fixtures", "Enter Results", "Team Standings", "Player Standings", "Knockout"],
    horizontal=True
)

team_stats, player_stats = analyze_results(results, fixtures)

# ---------------- FIXTURES ----------------
if menu == "Fixtures":
    for f in fixtures:
        st.markdown(f"**{f['team_a']} vs {f['team_b']}**")

# ---------------- TEAM STANDINGS ----------------
elif menu == "Team Standings":
    df = pd.DataFrame.from_dict(team_stats, orient="index")
    df["Set Diff"] = df["Sets Won"] - df["Sets Lost"]
    df["Point Diff"] = df["Points Won"] - df["Points Lost"]
    df = df.sort_values(by=["Points", "Set Diff", "Point Diff"], ascending=False)
    st.dataframe(df, use_container_width=True)

# ---------------- PLAYER STANDINGS ----------------
elif menu == "Player Standings":
    dfp = pd.DataFrame.from_dict(player_stats, orient="index")
    dfp["Recent Form"] = dfp["Form"].apply(lambda x: "".join(x))
    dfp = dfp.sort_values(by=["Points", "Won"], ascending=False)
    st.dataframe(dfp[["Team", "Points", "Played", "Recent Form"]], use_container_width=True)

# ---------------- KNOCKOUT ----------------
elif menu == "Knockout":
    st.info("Semi‑finals & Finals generated automatically once league completes.")
