import streamlit as st
import json
import os
import requests
import pandas as pd
from collections import defaultdict

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="🏸 Tournament Intelligence Platform", layout="wide")
st.title("🏸 Tournament Intelligence Platform")

# =================================================
# UI STYLING (SAFE, EXECUTIVE)
# =================================================
st.markdown("""
<style>
html, body {
    font-family: Inter, Segoe UI, Helvetica, Arial, sans-serif;
    background-color: #F8FAFC;
    color: #0F172A;
}
.block-container {
    max-width: 1200px;
    padding-top: 1.2rem;
}
.card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 24px;
}
.vs {
    text-align: center;
    font-weight: 700;
    color: #F59E0B;
    margin-top: 18px;
}
.match-row {
    padding: 6px 0;
    font-size: 14px;
}
.match-done {
    color: #16A34A;
    font-weight: 600;
}
.match-pending {
    color: #6B7280;
}
</style>
""", unsafe_allow_html=True)

# =================================================
# SECRETS
# =================================================
SCRIPT_URL = st.secrets["SCRIPT_URL"]

# =================================================
# DATA
# =================================================
teams_data = {
    "Smash Titans": ["Omkar", "Nishit", "Ganesh", "Sandeep W", "Amit", "Jayant"],
    "Quantum Force": ["Rajendra", "Aniket", "Deepak L", "Rahul", "Manmohan", "Prashant"],
    "Racket Scientists": ["Kiran", "Kaustubh", "Piyush", "Pradyum", "Amol S", "Amol P"],
    "Net Ninjas": ["Jaswanth", "Sandeepk", "Ritesh", "Vikram", "Pramod", "Deepak T"]
}

# =================================================
# HELPERS
# =================================================
def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def load_results():
    rows = requests.get(SCRIPT_URL, timeout=10).json()
    data = defaultdict(lambda: {"matches": [{}, {}, {}]})

    for row in rows:
        try:
            tid = int(row["tie_id"])
            sets = json.loads(row["sets_json"])
            idx = int(row["match_index"]) - 1
            if sets:
                data[tid]["matches"][idx] = {"sets": sets}
        except:
            pass
    return dict(data)

fixtures = load_json("data/fixtures.json", [])

# =================================================
# INSIGHTS (REAL DATA)
# =================================================
def compute_insights(results, fixtures):
    team = defaultdict(lambda: {"played": 0, "wins": 0, "pt": 0, "res": []})
    player_form = defaultdict(list)

    for tid, r in results.items():
        f = next((x for x in fixtures if x["tie_id"] == tid), None)
        if not f:
            continue

        ta, tb = f["team_a"], f["team_b"]

        for i, m in enumerate(r["matches"]):
            if not m:
                continue

            a_s=b_s=a_p=b_p=0
            for a,b in m["sets"]:
                a_p+=a; b_p+=b
                a_s+=a>b; b_s+=b>a

            team[ta]["played"]+=1
            team[tb]["played"]+=1
            team[ta]["pt"]+=a_p-b_p
            team[tb]["pt"]+=b_p-a_p

            if a_s>b_s:
                team[ta]["wins"]+=1
                team[ta]["res"].append(1)
                team[tb]["res"].append(0)
                win_side="A"
            else:
                team[tb]["wins"]+=1
                team[tb]["res"].append(1)
                team[ta]["res"].append(0)
                win_side="B"

            A = [p.strip() for p in f["matches"][i][0].split("/")]
            B = [p.strip() for p in f["matches"][i][1].split("/")]

            for p in A:
                player_form[p].append("W" if win_side=="A" else "L")
            for p in B:
                player_form[p].append("W" if win_side=="B" else "L")

    insights=[]
    if team:
        best = max(team.items(), key=lambda x: x[1]["wins"] / x[1]["played"])
        pct = round(best[1]["wins"] / best[1]["played"] * 100, 1)
        insights.append(f"Highest win efficiency: **{best[0]} ({pct}%)**")

        worst = min(team.items(), key=lambda x: x[1]["pt"])
        insights.append(f"Lowest point differential: **{worst[0]} ({worst[1]['pt']})**")

    streak = [p for p,r in player_form.items() if len(r)>=3 and "".join(r[-3:])=="WWW"]
    if streak:
        insights.append(f"Players on 3‑match win streak: **{', '.join(streak)}**")

    return insights

# =================================================
# MENU
# =================================================
menu = st.radio(
    "Navigate",
    ["Overview", "Fixtures", "Results", "Team Standings", "Player Standings", "Insights"],
    horizontal=True
)

# =================================================
# OVERVIEW
# =================================================
if menu == "Overview":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Tournament Operations Dashboard")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", "LIVE")
    c2.metric("Matches Completed", "—")
    c3.metric("Leading Team", "—")
    c4.metric("Fixtures Today", "—")
    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# FIXTURES (2 CARDS PER ROW)
# =================================================
elif menu == "Fixtures":
    st.subheader("Fixtures")

    results = load_results()

    for i in range(0, len(fixtures), 2):
        cols = st.columns(2)

        for col, f in zip(cols, fixtures[i:i+2]):
            with col:
                completed = sum(
                    1 for m in results.get(f["tie_id"], {}).get("matches", []) if m
                )

                # Card container
                st.markdown("<div class='card'>", unsafe_allow_html=True)

                # Fixture header
                st.markdown(
                    f"""
                    <div style="font-size:16px;font-weight:600;margin-bottom:6px;">
                        {f["team_a"]}
                        <span style="color:#F59E0B;"> vs </span>
                        {f["team_b"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                # Completion text
                st.caption(f"{completed} / 3 matches completed")

                # Progress bar (supporting, not dominant)
                st.progress(completed / 3)

                # Divider
                st.markdown("<hr>", unsafe_allow_html=True)

                # Match rows
                for idx, (pair_a, pair_b) in enumerate(f["matches"], start=1):
                    status_icon = "✅" if idx <= completed else "⏳"

                    st.markdown(
                        f"""
                        <div style="padding:6px 0;font-size:14px;">
                            <strong>M{idx}</strong> {status_icon}
                            <span style="color:#374151;">
                                {pair_a}
                                <span style="color:#9CA3AF;">vs</span>
                                {pair_b}
                            </span>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                # Close card
                st.markdown("</div>", unsafe_allow_html=True)
``

# =================================================
# RESULTS
# =================================================
elif menu == "Results":
    st.subheader("Results")

    results = load_results()

    if not results:
        st.info("No results available yet.")
    else:
        for tid, r in results.items():
            fixture = next((f for f in fixtures if f["tie_id"] == tid), None)
            if not fixture:
                continue

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.write(f"**{fixture['team_a']} vs {fixture['team_b']}**")

            for i, m in enumerate(r["matches"], start=1):
                if not m:
                    st.write(f"M{i}: Pending")
                else:
                    score = " | ".join(f"{a}-{b}" for a, b in m["sets"])
                    st.write(f"M{i}: {score}")

            st.markdown("</div>", unsafe_allow_html=True)
# =================================================
# TEAM STANDINGS (INTERNATIONAL)
# =================================================
elif menu == "Team Standings":
    results = load_results()
    table = defaultdict(lambda: {"Points":0,"Wins":0,"SetDiff":0,"PointDiff":0})

    for tid,r in results.items():
        f = next(x for x in fixtures if x["tie_id"]==tid)

        for m in r["matches"]:
            if not m: continue

            a_s=b_s=a_p=b_p=0
            for a,b in m["sets"]:
                a_p+=a; b_p+=b
                a_s+=a>b; b_s+=b>a

            if a_s>b_s:
                table[f["team_a"]]["Points"]+=2
                table[f["team_a"]]["Wins"]+=1
            else:
                table[f["team_b"]]["Points"]+=2
                table[f["team_b"]]["Wins"]+=1

            table[f["team_a"]]["SetDiff"]+=a_s-b_s
            table[f["team_b"]]["SetDiff"]+=b_s-a_s
            table[f["team_a"]]["PointDiff"]+=a_p-b_p
            table[f["team_b"]]["PointDiff"]+=b_p-a_p

    df = pd.DataFrame.from_dict(table, orient="index")
    df = df.sort_values(by=["Points","Wins","SetDiff","PointDiff"], ascending=False)
    st.dataframe(df, width="stretch")

# =================================================
# PLAYER STANDINGS
# =================================================
elif menu == "Player Standings":
    results = load_results()
    stats = defaultdict(lambda: {"Team":"","Wins":0,"SetDiff":0,"PointDiff":0,"Played":0})

    for t, players in teams_data.items():
        for p in players:
            stats[p]["Team"] = t

    for tid,r in results.items():
        f = next(x for x in fixtures if x["tie_id"]==tid)
        for i,m in enumerate(r["matches"]):
            if not m: continue

            A = [x.strip() for x in f["matches"][i][0].split("/")]
            B = [x.strip() for x in f["matches"][i][1].split("/")]

            a_s=b_s=a_p=b_p=0
            for a,b in m["sets"]:
                a_p+=a; b_p+=b
                a_s+=a>b; b_s+=b>a

            for p in A:
                stats[p]["Played"]+=1
                stats[p]["SetDiff"]+=a_s-b_s
                stats[p]["PointDiff"]+=a_p-b_p
                if a_s>b_s: stats[p]["Wins"]+=1
            for p in B:
                stats[p]["Played"]+=1
                stats[p]["SetDiff"]+=b_s-a_s
                stats[p]["PointDiff"]+=b_p-a_p
                if b_s>a_s: stats[p]["Wins"]+=1

    df = pd.DataFrame.from_dict(stats, orient="index")
    df = df.sort_values(by=["Wins","SetDiff","PointDiff","Played"], ascending=[False,False,False,True])
    df.insert(0,"Rank",range(1,len(df)+1))
    st.dataframe(df.reset_index().rename(columns={"index":"Player"}), width="stretch")

# =================================================
# INSIGHTS (REAL)
# =================================================
elif menu == "Insights":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Automated Tournament Insights")

    insights = compute_insights(load_results(), fixtures)

    if not insights:
        st.write("Not enough completed matches to generate insights.")
    else:
        for i in insights:
            st.write("•", i)

    st.markdown("</div>", unsafe_allow_html=True)
