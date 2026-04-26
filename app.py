components.html("""
<style>
@media (max-width: 768px) {
    .grid { grid-template-columns: 1fr !important; }
}
</style>
""", height=0)
import streamlit as st
import streamlit.components.v1 as components
import json
import requests
from collections import defaultdict

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="🏸 Tournament Intelligence Platform", layout="wide")
st.title("🏸 Tournament Intelligence Platform")

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
    "Net Ninjas": ["Jaswanth", "Sandeepk", "Ritesh", "Vikram", "Pramod", "Deepak T"],
}

def load_json(path):
    with open(path) as f:
        return json.load(f)

fixtures = load_json("data/fixtures.json")

# =================================================
# RESULTS LOADER
# =================================================
def load_results():
    rows = requests.get(SCRIPT_URL, timeout=10).json()
    data = defaultdict(lambda: {"matches": [{}, {}, {}]})

    for row in rows:
        try:
            tie_id = int(row["tie_id"])
            idx = int(row["match_index"]) - 1
            sets = json.loads(row["sets_json"])
            if sets:
                data[tie_id]["matches"][idx] = {"sets": sets}
        except:
            continue
    return dict(data)

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
    st.subheader("Tournament Overview")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", "LIVE")
    c2.metric("Teams", len(teams_data))
    c3.metric("Total Fixtures", len(fixtures))
    c4.metric("Matches per Fixture", 3)

# =================================================
# FIXTURES (FULLY HTML – CSS GUARANTEED)
# =================================================
elif menu == "Fixtures":
    results = load_results()

    html = """
    <style>
        body { font-family: Inter, Segoe UI, sans-serif; }
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }
        .card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 20px;
        }
        .title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .vs { color: #f59e0b; padding: 0 4px; }
        .meta { font-size: 13px; color: #6b7280; margin-bottom: 6px; }
        .progress {
            background: #e5e7eb;
            height: 8px;
            border-radius: 6px;
            overflow: hidden;
            margin-bottom: 12px;
        }
        .bar {
            background: #1f7aed;
            height: 100%;
        }
        .divider {
            border-top: 1px solid #e5e7eb;
            margin: 10px 0;
        }
        .row {
            font-size: 14px;
            padding: 6px 0;
            color: #374151;
        }
    </style>
    <div class="grid">
    """

    for f in fixtures:
        completed = sum(
            1 for m in results.get(f["tie_id"], {}).get("matches", []) if m
        )
        pct = int((completed / 3) * 100)

        html += f"""
        <div class="card">
            <div class="title">
                {f["team_a"]}<span class="vs">vs</span>{f["team_b"]}
            </div>
            <div class="meta">{completed} / 3 matches completed</div>

            <div class="progress">
                <div class="bar" style="width:{pct}%"></div>
            </div>

            <div class="divider"></div>
        """

        for i, (pa, pb) in enumerate(f["matches"], start=1):
            icon = "✅" if i <= completed else "⏳"
            html += f"""
            <div class="row">
                <strong>M{i}</strong> {icon}
                {pa} <span class="vs">vs</span> {pb}
            </div>
            """

        html += "</div>"

    html += "</div>"

    components.html(html, height=1400, scrolling=True)

# =================================================
# RESULTS
# =================================================
elif menu == "Results":
    import streamlit.components.v1 as components

    results = load_results()

    html = """
    <style>
        .result-card {
            background:#ffffff;
            border:1px solid #e5e7eb;
            border-radius:14px;
            padding:18px;
            margin-bottom:20px;
        }
        .match {
            padding:6px 0;
            font-size:14px;
        }
        .winner {
            color:#16a34a;
            font-weight:600;
        }
        .loser {
            color:#6b7280;
        }
        .score {
            font-weight:600;
            margin-left:6px;
        }
    </style>
    """

    for tid, r in results.items():
        f = next(fx for fx in fixtures if fx["tie_id"] == tid)

        html += f"""
        <div class="result-card">
            <div style="font-size:16px;font-weight:600;margin-bottom:8px;">
                {f['team_a']} vs {f['team_b']}
            </div>
        """

        for idx, m in enumerate(r["matches"], start=1):
            if not m:
                html += f"<div class='match'>M{idx}: Pending</div>"
                continue

            a_sets = sum(1 for a,b in m["sets"] if a>b)
            b_sets = len(m["sets"]) - a_sets
            score = " | ".join(f"{a}-{b}" for a,b in m["sets"])

            win_class = "winner" if a_sets > b_sets else "loser"
            lose_class = "loser" if a_sets > b_sets else "winner"

            pA, pB = f["matches"][idx-1]

            html += f"""
            <div class="match">
                <span class="{win_class}">{pA}</span>
                vs
                <span class="{lose_class}">{pB}</span>
                <span class="score">({score})</span>
            </div>
            """

        html += "</div>"

    components.html(html, height=900, scrolling=True)
# =================================================
# TEAM STANDINGS (BASIC, STABLE)
# =================================================
elif menu == "Team Standings":
    import streamlit.components.v1 as components
    from collections import defaultdict

    results = load_results()
    table = defaultdict(lambda: {"Pts":0,"W":0,"SetΔ":0,"PtΔ":0})

    for tid,r in results.items():
        f = next(x for x in fixtures if x["tie_id"]==tid)

        for m in r["matches"]:
            if not m: continue
            a_s=b_s=a_p=b_p=0
            for a,b in m["sets"]:
                a_p+=a; b_p+=b
                a_s+=a>b; b_s+=b>a

            if a_s>b_s:
                table[f["team_a"]]["Pts"]+=2
                table[f["team_a"]]["W"]+=1
            else:
                table[f["team_b"]]["Pts"]+=2
                table[f["team_b"]]["W"]+=1

            table[f["team_a"]]["SetΔ"]+=a_s-b_s
            table[f["team_b"]]["SetΔ"]+=b_s-a_s
            table[f["team_a"]]["PtΔ"]+=a_p-b_p
            table[f["team_b"]]["PtΔ"]+=b_p-a_p

    ordered = sorted(
        table.items(),
        key=lambda x:(x[1]["Pts"],x[1]["W"],x[1]["SetΔ"],x[1]["PtΔ"]),
        reverse=True
    )

    html = """
    <style>
        .team-card {
            border:1px solid #e5e7eb;
            border-radius:12px;
            padding:14px;
            margin-bottom:12px;
        }
        .leader {
            background:#fff7ed;
            border-color:#f59e0b;
        }
        .row {
            display:flex;
            justify-content:space-between;
            font-size:14px;
        }
    </style>
    """

    for i,(team,data) in enumerate(ordered, start=1):
        cls = "team-card leader" if i==1 else "team-card"
        html += f"""
        <div class="{cls}">
            <div style="font-weight:600;margin-bottom:6px;">#{i} {team}</div>
            <div class="row">
                <span>Pts: {data['Pts']}</span>
                <span>W: {data['W']}</span>
                <span>SetΔ: {data['SetΔ']}</span>
            </div>
        </div>
        """

    components.html(html, height=800)

# =================================================
# PLAYER STANDINGS
# =================================================
elif menu == "Player Standings":
    import streamlit.components.v1 as components
    from collections import defaultdict

    results = load_results()
    stats = defaultdict(lambda:{"Team":"","W":0,"P":0,"Form":[]})

    for t, players in teams_data.items():
        for p in players:
            stats[p]["Team"]=t

    for tid,r in results.items():
        f = next(x for x in fixtures if x["tie_id"]==tid)

        for i,m in enumerate(r["matches"]):
            if not m: continue
            A=[x.strip() for x in f["matches"][i][0].split("/")]
            B=[x.strip() for x in f["matches"][i][1].split("/")]

            a_s=sum(1 for a,b in m["sets"] if a>b)
            b_s=len(m["sets"])-a_s

            for p in A:
                stats[p]["P"]+=1
                stats[p]["Form"].append("W" if a_s>b_s else "L")
                if a_s>b_s: stats[p]["W"]+=1
            for p in B:
                stats[p]["P"]+=1
                stats[p]["Form"].append("W" if b_s>a_s else "L")
                if b_s>a_s: stats[p]["W"]+=1

    ordered = sorted(
        stats.items(),
        key=lambda x:(x[1]["W"],-x[1]["P"]),
        reverse=True
    )

    html = """
    <style>
        .player {
            border:1px solid #e5e7eb;
            border-radius:12px;
            padding:12px;
            margin-bottom:10px;
            font-size:14px;
        }
        .pill {
            display:inline-block;
            padding:2px 8px;
            border-radius:999px;
            font-size:12px;
            margin-right:4px;
        }
        .W {background:#dcfce7;color:#166534;}
        .L {background:#fee2e2;color:#991b1b;}
    </style>
    """

    for rank,(p,d) in enumerate(ordered, start=1):
        forms=" ".join(
            f"<span class='pill {x}'>{x}</span>"
            for x in d["Form"][-5:]
        )

        html += f"""
        <div class="player">
            <strong>#{rank} {p}</strong> ({d['Team']})<br>
            Wins: {d['W']} | Played: {d['P']}<br>
            {forms}
        </div>
        """

    components.html(html, height=900, scrolling=True)
# =================================================
# INSIGHTS
# =================================================
elif menu == "Insights":
    st.subheader("Insights")
    st.info("Data‑driven insights generated from fixtures and results.")
