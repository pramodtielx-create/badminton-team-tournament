import streamlit as st
import json
import os
import pandas as pd
from collections import defaultdict, deque

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
    st.success("✅ Tournament system running")
    st.info("League → Top 2 → Final | Results visible to everyone")

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
elif menu == "Enter Results":
    if not st.session_state.is_admin:
        st.warning("🔒 Admin access required")
    else:
        tie = st.selectbox(
            "Select Tie",
            fixtures,
            format_func=lambda x: f"Tie {x['tie_id']} — {x['team_a']} vs {x['team_b']}"
        )

        match_results = []
        for m in range(3):
            st.markdown(f"### Match {m+1}")
            sets = []
            for s in range(3):
                c1, c2 = st.columns(2)
                with c1:
                    a = st.number_input(
                        f"{tie['team_a']}",
                        0, 30,
                        key=f"a_{tie['tie_id']}_{m}_{s}"
                    )
                with c2:
                    b = st.number_input(
                        f"{tie['team_b']}",
                        0, 30,
                        key=f"b_{tie['tie_id']}_{m}_{s}"
                    )
                if a or b:
                    sets.append([a, b])
            match_results.append({"sets": sets})

        if st.button("✅ Save Results"):
            results = [r for r in results if r["tie_id"] != tie["tie_id"]]
            results.append({
                "tie_id": tie["tie_id"],
                "team_a": tie["team_a"],
                "team_b": tie["team_b"],
                "matches": match_results
            })
            save_json("data/results.json", results)
            st.success("✅ Results saved")

# =================================================
# TEAM STANDINGS
# =================================================
elif menu == "Team Standings":
    table = defaultdict(int)
    for r in results:
        table[r["team_a"]] += 2
    df = pd.DataFrame.from_dict(table, orient="index", columns=["Points"])
    st.dataframe(df.sort_values("Points", ascending=False), width="stretch")

# =================================================
# PLAYER STANDINGS + PLAYER OF TOURNAMENT
# =================================================
elif menu == "Player Standings":
    stats = defaultdict(lambda: {
        "Team": "",
        "Played": 0,
        "Won": 0,
        "Points": 0,
        "Form": deque(maxlen=5)
    })

    for r in results:
        fixture = next(f for f in fixtures if f["tie_id"] == r["tie_id"])
        for i, m in enumerate(r["matches"]):
            pair_a = fixture["matches"][i][0].split("/")
            pair_b = fixture["matches"][i][1].split("/")
            a_sets = b_sets = 0
            for a,b in m["sets"]:
                if a > b: a_sets += 1
                else: b_sets += 1
            a_win = a_sets > b_sets

            for p in pair_a:
                p = p.strip()
                stats[p]["Team"] = r["team_a"]
                stats[p]["Played"] += 1
                stats[p]["Form"].append("✅" if a_win else "❌")
                if a_win:
                    stats[p]["Won"] += 1
                    stats[p]["Points"] += 2

            for p in pair_b:
                p = p.strip()
                stats[p]["Team"] = r["team_b"]
                stats[p]["Played"] += 1
                stats[p]["Form"].append("✅" if not a_win else "❌")
                if not a_win:
                    stats[p]["Won"] += 1
                    stats[p]["Points"] += 2

    dfp = pd.DataFrame.from_dict(stats, orient="index")
    dfp["Recent Form"] = dfp["Form"].apply(lambda x: " ".join(list(x)))
    dfp = dfp.sort_values(by=["Points","Won"], ascending=False)

    st.dataframe(
        dfp[["Team","Played","Won","Points","Recent Form"]],
        width="stretch"
    )

    if not dfp.empty:
        pot = dfp.index[0]
        st.success(f"🥇 Player of the Tournament: **{pot}** ({dfp.loc[pot,'Team']})")

# =================================================
# FINAL (TOP 2)
# =================================================
elif menu == "Final":
    if not results:
        st.warning("Final available after league results.")
    else:
        standings = defaultdict(int)
        for r in results:
            standings[r["team_a"]] += 2

        finalists = sorted(standings, key=standings.get, reverse=True)[:2]

        c1, c2, c3 = st.columns([1,4,1])
        with c1:
            show_logo(finalists[0], 90)
        with c2:
            st.subheader(f"{finalists[0]} VS {finalists[1]}")
        with c3:
            show_logo(finalists[1], 90)

        if final_result.get("sets"):
            a = b = 0
            for s in final_result["sets"]:
                if s[0] > s[1]: a += 1
                else: b += 1
            winner = finalists[0] if a > b else finalists[1]
            st.success(f"🏆 Champion: **{winner}**")
