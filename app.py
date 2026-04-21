import streamlit as st
import json
import os
import pandas as pd
from collections import defaultdict, deque
RULES_HTML = """
<div style="background-color:#f8f9fa;padding:25px;border-radius:14px;
border-left:6px solid #1f77b4;max-height:80vh;overflow-y:auto;">
<h2>🏸 Mathi Gang Badminton Tournament</h2>
<h3>Official Rules & Competition Format</h3>
<hr>

<h4>1. Tournament Format</h4>
<ul>
<li>League + Knockout format.</li>
<li>Each team plays once against every other team.</li>
<li>Each team forms 3 fixed doubles pairs.</li>
<li>Each player plays only once against an opponent team.</li>
<li>3 matches per tie; winning 2 wins the tie.</li>
<li>Toss decides which team submits their pair first.</li>
</ul>

<h4>2. Match & Scoring Rules</h4>
<ul>
<li>Best of 3 sets.</li>
<li>Each set to 21 points.</li>
<li>Win by 2 points.</li>
<li>At 29–29, first to 30 wins.</li>
</ul>

<h4>3. League Ranking</h4>
<ol>
<li>Ties Won</li>
<li>Set Difference</li>
<li>Points Difference</li>
<li>Points Ratio</li>
</ol>

<h4>4. Qualification</h4>
<ul>
<li>Top 2 teams qualify for Finals.</li>
<li>Bottom 2 play for 3rd place.</li>
</ul>

<h4>5. Conduct</h4>
<ul>
<li>No equipment abuse.</li>
<li>No arguing with officials.</li>
<li>No coaching during rallies.</li>
</ul>

<p style="font-size:13px;color:#555;">
✅ Rules aligned with international badminton standards.
</p>
</div>
"""
# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="🏸 Badminton Tournament", layout="wide")
st.title("🏸 Badminton Tournament")


# =================================================
# ADMIN SESSION
# =================================================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False

# =================================================
# TEAM DATA + LOGOS
# =================================================
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
        st.write("🖼️")

# =================================================
# DATA HELPERS
# =================================================
def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

fixtures = load_json("data/fixtures.json", [])
results = load_json("data/results.json", [])
final_result = load_json("data/final_result.json", {})

# =================================================
# MENU
# =================================================
menu = st.radio(
    "Navigate",
    [
        "Home",
        "Teams",
        "Fixtures",
        "Results",
        "Team Standings",
        "Player Standings",
        "Final",
        "Enter Results",
        "Admin Login"
    ],
    horizontal=True
)

# =================================================
# HOME
# =================================================
if menu == "Home":
    st.markdown(RULES_HTML, unsafe_allow_html=True)
# =================================================
# ADMIN LOGIN
# =================================================
elif menu == "Admin Login":
    st.subheader("🔐 Admin Login")
    if st.session_state.is_admin:
        st.success("✅ Logged in as Admin")
        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()
    else:
        pwd = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if pwd == st.secrets["ADMIN_PASSWORD"]:
                st.session_state.is_admin = True
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Incorrect password")

# =================================================
# TEAMS
# =================================================
elif menu == "Teams":
    for team, players in teams_data.items():
        c1, c2 = st.columns([1,5])
        with c1:
            show_logo(team, 80)
        with c2:
            st.subheader(team)
            for p in players:
                st.write(f"• {p}")
        st.divider()

# =================================================
# FIXTURES
# =================================================
elif menu == "Fixtures":
    for tie in fixtures:
        c1, c2, c3 = st.columns([1,4,1])
        with c1:
            show_logo(tie["team_a"])
        with c2:
            st.subheader(f"{tie['team_a']} VS {tie['team_b']}")
        with c3:
            show_logo(tie["team_b"])
        for i, m in enumerate(tie["matches"], 1):
            st.write(f"Match {i}: {m[0]} vs {m[1]}")
        st.divider()

# =================================================
# RESULTS (PUBLIC)
# =================================================
elif menu == "Results":
    st.subheader("📊 Match Results")
    if not results:
        st.warning("No results entered yet.")
    else:
        for r in results:
            c1, c2, c3 = st.columns([1,4,1])
            with c1:
                show_logo(r["team_a"])
            with c2:
                st.subheader(f"{r['team_a']} VS {r['team_b']}")
            with c3:
                show_logo(r["team_b"])

            for i, m in enumerate(r["matches"], 1):
                score = " | ".join([f"{s[0]}-{s[1]}" for s in m["sets"]])
                st.write(f"Match {i}: {score}")
            st.divider()

# =================================================
# ENTER RESULTS (ADMIN ONLY)
# =================================================
elif menu == "Enter Results":elif            "Select Tie",
            fixtures,
            format_func=lambda x: f"Tie {x['tie_id']} — {x['team_a']} vs {x['team_b']}"
        )

        match_results = []

        for m in range(3):
            st.markdown(f"### Match {m + 1}")
            sets = []

            for s in range(3):
                c1, c2 = st.columns(2)

                with c1:
                    a = st.number_input(
                        f"{tie['team_a']} (Set {s + 1})",
                        0, 30,
                        key=f"a_{tie['tie_id']}_{m}_{s}"
                    )

                with c2:
                    b = st.number_input(
                        f"{tie['team_b']} (Set {s + 1})",
                        0, 30,
                        key=f"b_{tie['tie_id']}_{m}_{s}"
                    )

                if a > 0 or b > 0:
                    sets.append([a, b])

            match_results.append({"sets": sets})

        # ✅ SAVE BUTTON (THIS WAS MISSING)
        if st.button("✅ Save Results"):
            updated_results = [
                r for r in results if r["tie_id"] != tie["tie_id"]
            ]

            updated_results.append({
                "tie_id": tie["tie_id"],
                "team_a": tie["team_a"],
                "team_b": tie["team_b"],
                "matches": match_results
            })

            save_json("data/results.json", updated_results)

            st.success("✅ Results saved successfully")
            st.rerun()   # 🔥 forces reload so Results/Standings update
    st.subheader("📝 Enter Match Results")

    if not st.session_state.is_admin:
        st.warning("🔒 Admin access required")
    else:
        tie = st.selectbox(

                if a or b:
                    sets.append([a, b])
