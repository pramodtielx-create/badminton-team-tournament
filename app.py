import streamlit as st
import json
import pandas as pd
import os

# -------------------------------------------------
# PAGE CONFIG
# -------------------------------------------------
st.set_page_config(page_title="🏸 Badminton Tournament", layout="wide")
st.title("🏸 Badminton Tournament")

# -------------------------------------------------
# RULES (SAFE VARIABLE – NO SYNTAX ERRORS)
# -------------------------------------------------
RULES_HTML = """
<div style="
background-color:#f8f9fa;
padding:25px;
border-radius:14px;
border-left:6px solid #1f77b4;
max-height:80vh;
overflow-y:auto;
">

<h2>🏸 Mathi Gang Badminton Tournament</h2>
<h3>Official Rules & Competition Format</h3>

<hr>

<h4>1. Tournament Format</h4>
<ul>
<li>League + Knockout format.</li>
<li>Every team plays once against every other team.</li>
<li>Each team fields three fixed doubles pairs.</li>
<li>Each player plays only once against an opponent team.</li>
<li>Each tie consists of 3 matches; winning 2 wins the tie.</li>
<li>Toss decides which team submits their pair first.</li>
</ul>

<hr>

<h4>2. Match & Scoring Rules</h4>
<ul>
<li>Best of 3 sets.</li>
<li>Each set to 21 points.</li>
<li>Win by 2 points.</li>
<li>At 29–29, first to 30 wins.</li>
</ul>

<hr>

<h4>3. League Ranking Criteria</h4>
<ol>
<li>Ties Won</li>
<li>Set Difference (Won − Lost)</li>
<li>Points Difference (For − Against)</li>
<li>Better points ratio</li>
</ol>

<hr>

<h4>4. Qualification</h4>
<ul>
<li>Top 2 teams qualify for Finals.</li>
<li>Bottom 2 Teams will play for 3rd and 4th/li>
</ul>

<hr>

<h4>5. Knockout Rules</h4>
<ul>
<li>Best of 3 sets.</li>
<li>Same scoring rules apply.</li>
</ul>

<hr>

<h4>6. On‑Court Rules</h4>
<ul>
<li>1‑minute warm‑up.</li>
<li>60‑second interval at 11 points.</li>
<li>Switch sides after every set.</li>
<li>In 3rd set, side change at 11 points.</li>
</ul>

<hr>

<h4>7. Substitution</h4>
<ul>
<li>Allowed only for injury or unavailability.</li>
<li>From approved substitute pool.</li>
</ul>

<hr>

<h4>8. Conduct</h4>
<ul>
<li>No equipment abuse.</li>
<li>No arguing with officials.</li>
<li>No coaching during rallies.</li>
</ul>

<hr>

<h4>9. Final Authority</h4>
<ul>
<li>Organizers’ decisions are final.</li>
</ul>

<p style="font-size:13px;color:#555;">
✅ Rules aligned with international badminton standards.
</p>
</div>
"""

# -------------------------------------------------
# TEAM DATA + LOGOS
# -------------------------------------------------
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
        st.markdown("🖼️")

# -------------------------------------------------
# DATA LOADERS
# -------------------------------------------------
@st.cache_data
def load_fixtures():
    with open("data/fixtures.json","r") as f:
        return json.load(f)

def load_results():
    try:
        with open("data/results.json","r") as f:
            return json.load(f)
    except:
        return []

def save_results(data):
    with open("data/results.json","w") as f:
        json.dump(data,f,indent=2)

fixtures = load_fixtures()
results = load_results()

# -------------------------------------------------
# MENU
# -------------------------------------------------
menu = st.radio("Navigate",["Home","Teams","Fixtures","Enter Results","Standings"],horizontal=True)

# -------------------------------------------------
# HOME
# -------------------------------------------------
if menu == "Home":
    st.markdown(RULES_HTML, unsafe_allow_html=True)

# -------------------------------------------------
# TEAMS
# -------------------------------------------------
elif menu == "Teams":
    st.subheader("👥 Team Combinations")
    cols = st.columns(2)
    for i,(team,players) in enumerate(teams_data.items()):
        with cols[i%2]:
            c1,c2 = st.columns([1,4])
            with c1: show_logo(team,70)
            with c2: st.markdown(f"### {team}")
