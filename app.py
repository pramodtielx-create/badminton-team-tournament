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
# SAFE UI STYLING
# =================================================
st.markdown("""
<style>
html, body {
    font-family: Inter, Segoe UI, Helvetica, Arial, sans-serif;
    background-color: #F8FAFC;
    color: #0F172A;
}
.block-container { max-width: 1200px; padding-top: 1.2rem; }
.card {
    background: white;
    border: 1px solid #E5E7EB;
    border-radius: 14px;
    padding: 18px;
    margin-bottom: 18px;
}
.vs {
    text-align: center;
    font-weight: 700;
    color: #F59E0B;
    margin-top: 18px;
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
    "Smash Titans": ["Omkar","Nishit","Ganesh","Sandeep W","Amit","Jayant"],
    "Quantum Force": ["Rajendra","Aniket","Deepak L","Rahul","Manmohan","Prashant"],
    "Racket Scientists": ["Kiran","Kaustubh","Piyush","Pradyum","Amol S","Amol P"],
    "Net Ninjas": ["Jaswanth","Sandeepk","Ritesh","Vikram","Pramod","Deepak T"]
}

def load_json(path, default):
    try:
        with open(path) as f:
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
# INSIGHTS ENGINE (REAL DATA)
# =================================================
def compute_insights(results, fixtures):
    team_stats = defaultdict(lambda: {"played":0,"wins":0,"ptdiff":0,"results":[]})
    player_forms = defaultdict(list)

    for tid, r in results.items():
        fx = next((f for f in fixtures if f["tie_id"] == tid), None)
        if not fx:
            continue

        ta, tb = fx["team_a"], fx["team_b"]

        for i, m in enumerate(r["matches"]):
            if not m:
                continue

            a_s=b_s=a_p=b_p=0
            for a,b in m["sets"]:
                a_p+=a; b_p+=b
                a_s+=a>b; b_s+=b>a

            team_stats[ta]["played"]+=1
            team_stats[tb]["played"]+=1
            team_stats[ta]["ptdiff"]+=a_p-b_p
            team_stats[tb]["ptdiff"]+=b_p-a_p

            if a_s>b_s:
                team_stats[ta]["wins"]+=1
                team_stats[ta]["results"].append(1)
                team_stats[tb]["results"].append(0)
                win_side = "A"
            else:
                team_stats[tb]["wins"]+=1
                team_stats[tb]["results"].append(1)
                team_stats[ta]["results"].append(0)
                win_side = "B"

            A = [p.strip() for p in fx["matches"][i][0].split("/")]
            B = [p.strip() for p in fx["matches"][i][1].split("/")]

            for p in A:
                player_forms[p].append("W" if win_side=="A" else "L")
            for p in B:
                player_forms[p].append("W" if win_side=="B" else "L")

    insights = []

    if team_stats:
        best = max(team_stats.items(), key=lambda x: x[1]["wins"]/x[1]["played"])
        pct = round(best[1]["wins"]/best[1]["played"]*100,1)
        insights.append(f"Highest win efficiency: **{best[0]} ({pct}%)**")

        worst_pd = min(team_stats.items(), key=lambda x: x[1]["ptdiff"])
        insights.append(f"Lowest point differential: **{worst_pd[0]} ({worst_pd[1]['ptdiff']})**")

        def variance(arr):
            if len(arr)<2: return 999
            m=sum(arr)/len(arr)
            return sum((x-m)**2 for x in arr)/len(arr)

        consistent = min(team_stats.items(), key=lambda x: variance(x[1]["results"]))
        insights.append(f"Most consistent team: **{consistent[0]}**")

    streak = [
        p for p, r in player_forms.items()
        if len(r)>=3 and "".join(r[-3:])=="WWW"
    ]
    if streak:
        insights.append(f"Players on 3‑match winning streak: **{', '.join(streak)}**")

    return insights

# =================================================
# MENU
# =================================================
menu = st.radio(
    "Navigate",
    ["Overview","Fixtures","Results","Team Standings","Player Standings","Insights"],
    horizontal=True
)

# =================================================
# OVERVIEW
# =================================================
if menu == "Overview":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Tournament Operations Dashboard")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Status","LIVE")
    c2.metric("Matches Completed","—")
    c3.metric("Leading Team","—")
    c4.metric("Fixtures Today","—")
    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# FIXTURES
# =================================================
elif menu == "Fixtures":
    results = load_results()
    for f in fixtures:
        done = sum(1 for m in results.get(f["tie_id"],{}).get("matches",[]) if m)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown(f"**{f['team_a']}** <span class='vs'>VS</span> **{f['team_b']}**", unsafe_allow_html=True)
        st.progress(done/3)
        for i,(a,b) in enumerate(f["matches"],1):
            st.write(f"M{i}: {a} vs {b}")
        st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# RESULTS
# =================================================
elif menu == "Results":
    results = load_results()
    for tid, r in results.items():
        fx = next(f for f in fixtures if f["tie_id"]==tid)
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.write(f"**{fx['team_a']} vs {fx['team_b']}**")
        for i,m in enumerate(r["matches"],1):
            if not m:
                st.write(f"M{i}: Pending")
            else:
                score=" | ".join(f"{a}-{b}" for a,b in m["sets"])
                st.write(f"M{i}: {score}")
        st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# TEAM STANDINGS (INTERNATIONAL)
# =================================================
elif menu == "Team Standings":
    results = load_results()
    table = defaultdict(lambda:{"Pts":0,"W":0,"SetΔ":0,"PtΔ":0})

    for tid,r in results.items():
        fx = next(f for f in fixtures if f["tie_id"]==tid)
        ta,tb = fx["team_a"], fx["team_b"]

        for m in r["matches"]:
            if not m: continue
            a_s=b_s=a_p=b_p=0
            for a,b in m["sets"]:
                a_p+=a; b_p+=b
                a_s+=a>b; b_s+=b>a

            if a_s>b_s:
                table[ta]["Pts"]+=2; table[ta]["W"]+=1
            else:
                table[tb]["Pts"]+=2; table[tb]["W"]+=1

            table[ta]["SetΔ"]+=a_s-b_s
            table[tb]["SetΔ"]+=b_s-a_s
            table[ta]["PtΔ"]+=a_p-b_p
            table[tb]["PtΔ"]+=b_p-a_p

    df=pd.DataFrame.from_dict(table,orient="index").sort_values(
        ["Pts","W","SetΔ","PtΔ"],ascending=False)
    st.dataframe(df,width="stretch")

# =================================================
# PLAYER STANDINGS
# =================================================
elif menu == "Player Standings":
    results = load_results()
    stats = defaultdict(lambda:{"Team":"","W":0,"SetΔ":0,"PtΔ":0,"P":0})

    for t,ps in teams_data.items():
        for p in ps:
            stats[p]["Team"]=t

    for tid,r in results.items():
        fx = next(f for f in fixtures if f["tie_id"]==tid)
        for i,m in enumerate(r["matches"]):
            if not m: continue
            A=[x.strip() for x in fx["matches"][i][0].split("/")]
            B=[x.strip() for x in fx["matches"][i][1].split("/")]

            a_s=b_s=a_p=b_p=0
            for a,b in m["sets"]:
                a_p+=a; b_p+=b
                a_s+=a>b; b_s+=b>a

            for p in A:
                stats[p]["P"]+=1
                stats[p]["SetΔ"]+=a_s-b_s
                stats[p]["PtΔ"]+=a_p-b_p
                stats[p]["W"]+=a_s>b_s

            for p in B:
                stats[p]["P"]+=1
                stats[p]["SetΔ"]+=b_s-a_s
                stats[p]["PtΔ"]+=b_p-a_p
                stats[p]["W"]+=b_s>a_s

    df=pd.DataFrame.from_dict(stats,orient="index").sort_values(
        ["W","SetΔ","PtΔ","P"],ascending=[False,False,False,True])
    df.insert(0,"Rank",range(1,len(df)+1))
    st.dataframe(df.reset_index().rename(columns={"index":"Player"}),width="stretch")

# =================================================
# INSIGHTS (REAL DATA ONLY)
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
