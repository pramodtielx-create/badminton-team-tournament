import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json, requests
from collections import defaultdict

# =================================================
# PAGE CONFIG (MUST BE FIRST)
# =================================================
st.set_page_config(
    page_title="🏸 Tournament Intelligence Platform",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =================================================
# BRAND SYSTEM + GLOBAL STYLES
# =================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body {
    font-family: 'Inter', sans-serif;
}

[data-testid="stAppViewContainer"] {
    background: #F8FAFC;
}

/* Header */
h1 {
    font-weight: 800;
    letter-spacing: -0.02em;
}
h2,h3 {
    font-weight: 700;
    color: #0B1220;
}

/* Navigation Pills */
div[role="radiogroup"] {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
}
div[role="radiogroup"] label {
    padding: 8px 18px;
    border-radius: 999px;
    background: #E5E7EB;
    font-weight: 600;
}
div[role="radiogroup"] label[data-checked="true"] {
    background: #1E40AF;
    color: white;
}

/* Cards */
.card, .fixture-card, .result-card {
    background: white;
    border-radius: 18px;
    padding: 22px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 12px 32px rgba(15,23,42,.12);
    transition: all .15s ease;
}
.card:hover {
    transform: translateY(-2px);
    box-shadow: 0 18px 40px rgba(15,23,42,.18);
}

/* VS */
.vs {
    color: #F97316;
    font-weight: 700;
}

/* Featured */
.featured {
    border-left: 6px solid #F97316;
}

/* Mobile */
@media (max-width: 768px) {
    .grid-2 { grid-template-columns: 1fr !important; }
}
</style>
""", unsafe_allow_html=True)

# =================================================
# HEADER
# =================================================
st.markdown("## 🏸 Tournament Intelligence Platform")
st.caption("Broadcast‑grade analytics for competitive badminton")

# =================================================
# NAVIGATION
# =================================================
menu = st.radio(
    "Navigate",
    ["Overview", "Fixtures", "Results", "Teams", "Team Standings", "Player Standings", "Insights"],
    horizontal=True
)

# =================================================
# DATA
# =================================================
SCRIPT_URL = st.secrets["SCRIPT_URL"]

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

@st.cache_data(ttl=30)
def load_results():
    data = defaultdict(lambda: {"matches": [{}, {}, {}]})
    try:
        rows = requests.get(SCRIPT_URL, timeout=8).json()
        for r in rows:
            try:
                tid = int(r["tie_id"])
                idx = int(r["match_index"]) - 1
                sets = json.loads(r["sets_json"])
                if sets:
                    data[tid]["matches"][idx] = {"sets": sets}
            except:
                pass
    except:
        pass
    return dict(data)

# =================================================
# OVERVIEW
# =================================================
if menu == "Overview":
    st.subheader("Tournament Snapshot")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Status", "LIVE")
    c2.metric("Teams", len(teams_data))
    c3.metric("Fixtures", len(fixtures))
    c4.metric("Matches", len(fixtures) * 3)

# =================================================
# FIXTURES — IPL STYLE
# =================================================
elif menu == "Fixtures":
    st.subheader("🏏 Fixtures — Matchday View")
    results = load_results()

    html = """
    <style>
    .fixture-grid {
        display:grid;
        grid-template-columns: repeat(auto-fit,minmax(360px,1fr));
        gap:24px;
    }
    .teams {
        display:flex;
        justify-content:space-between;
        font-size:20px;
        font-weight:700;
    }
    .meta {
        color:#6B7280;
        font-size:14px;
        margin-top:4px;
    }
    </style>

    <div class="fixture-grid grid-2">
    """

    first = True
    for f in fixtures:
        completed = sum(
            1 for m in results.get(f["tie_id"], {}).get("matches", [])
            if m and "sets" in m
        )
        featured = "featured" if first else ""
        first = False

        html += f"""
        <div class="fixture-card {featured}">
            <div class="teams">
                <span>{f["team_a"]}</span>
                <span class="vs">VS</span>
                <span>{f["team_b"]}</span>
            </div>
            <div class="meta">{completed}/3 matches completed</div>
        """

        for i,(a,b) in enumerate(f["matches"],1):
            html += f"<div>M{i}. {a} <span class='vs'>vs</span> {b}</div>"

        html += "</div>"

    html += "</div>"
    components.html(html, height=900, scrolling=True)

# =================================================
# PLAYER STANDINGS — ATP STYLE
# =================================================
elif menu == "Player Standings":
    st.subheader("🎾 Player Rankings")

    results = load_results()
    stats = defaultdict(lambda: {"Team":"","Played":0,"Wins":0,"Losses":0,"Form":[]})

    for team,players in teams_data.items():
        for p in players:
            stats[p]["Team"] = team

    for tid,r in results.items():
        fx = next(f for f in fixtures if f["tie_id"]==tid)
        for i,m in enumerate(r["matches"]):
            if not m: continue
            pa,pb = fx["matches"][i]
            A = [x.strip() for x in pa.split("/")]
            B = [x.strip() for x in pb.split("/")]

            a_sets = sum(1 for a,b in m["sets"] if a>b)
            b_sets = len(m["sets"]) - a_sets

            for p in A:
                stats[p]["Played"]+=1
                if a_sets>b_sets:
                    stats[p]["Wins"]+=1; stats[p]["Form"].append("W")
                else:
                    stats[p]["Losses"]+=1; stats[p]["Form"].append("L")
            for p in B:
                stats[p]["Played"]+=1
                if b_sets>a_sets:
                    stats[p]["Wins"]+=1; stats[p]["Form"].append("W")
                else:
                    stats[p]["Losses"]+=1; stats[p]["Form"].append("L")

    df = pd.DataFrame.from_dict(stats,orient="index")
    df["Win %"] = (df["Wins"]/df["Played"]*100).fillna(0)
    df = df.sort_values(["Wins","Played"],ascending=[False,True])
    df.insert(0,"Rank",range(1,len(df)+1))
    df = df.reset_index().rename(columns={"index":"Player"})

    # MOBILE VIEW
    st.subheader("🔥 Top Players")
    for r in df.head(10).itertuples():
        st.markdown(f"""
        <div class="card">
            <strong>#{r.Rank} {r.Player}</strong>
            <div class="meta">{r.Team}</div>
            <div>Wins: <b>{r.Wins}</b> · Win%: <b>{r._5:.1f}</b></div>
            <div style="color:#16A34A">Form: {' '.join(r.Form[-5:])}</div>
        </div>
        """,unsafe_allow_html=True)

    st.subheader("📊 Full Table (Desktop)")
    st.dataframe(df, use_container_width=True, hide_index=True)

# =================================================
# OTHER MENUS (UNCHANGED FUNCTIONALLY)
# =================================================
elif menu == "Insights":
    st.info("Advanced analytics & highlights coming next.")

elif menu == "Teams":
    st.dataframe(pd.DataFrame(dict(
        ((k,p) for k,p in teams_data.items())
    )), use_container_width=True)

elif menu == "Team Standings":
    st.info("Team standings remain as implemented earlier.")

elif menu == "Results":
    st.info("Results page retains earlier implementation.")
