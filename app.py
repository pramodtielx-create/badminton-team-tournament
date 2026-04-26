import streamlit as st
import json
import os
import requests
import pandas as pd
from collections import defaultdict

# =================================================
# CONFIG
# =================================================
st.set_page_config(page_title="🏸 Badminton Tournament", layout="wide")
st.title("🏸 Badminton Tournament")

GOOGLE_SCRIPT_URL = st.secrets["SCRIPT_URL"]

# =================================================
# JSON HELPERS (FIXTURES ONLY)
# =================================================
def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

# =================================================
# GOOGLE SHEETS HELPERS (RESULTS)
# =================================================
def save_result_to_sheet(round_no, tie_id, team_a, team_b, match_index, sets):
    payload = {
        "round_no": round_no,
        "tie_id": tie_id,
        "team_a": team_a,
        "team_b": team_b,
        "match_index": match_index,
        "sets": sets
    }
    requests.post(GOOGLE_SCRIPT_URL, json=payload)

def load_results_from_sheet():
    r = requests.get(GOOGLE_SCRIPT_URL, timeout=10)
    rows = r.json()

    results = defaultdict(lambda: {
        "round": None,
        "tie_id": None,
        "team_a": "",
        "team_b": "",
        "matches": [{}, {}, {}]
    })

    for row in rows:
        # ✅ Hard safety against bad rows
        try:
            sets = json.loads(row["sets_json"])
            if not sets:
                continue
        except Exception:
            continue

        tie_id = int(row["tie_id"])

        results[tie_id]["round"] = int(row["round_no"])
        results[tie_id]["tie_id"] = tie_id
        results[tie_id]["team_a"] = row["team_a"]
        results[tie_id]["team_b"] = row["team_b"]

        results[tie_id]["matches"][int(row["match_index"]) - 1] = {
            "sets": sets
        }

    return list(results.values())
# =================================================
# PLAYER OF MATCH LOGIC
# =================================================
def calculate_potm(match_sets, pair_a, pair_b):
    a_sets = b_sets = 0
    a_pd = b_pd = 0

    for a, b in match_sets:
        if a > b:
            a_sets += 1
        else:
            b_sets += 1
        a_pd += (a - b)
        b_pd += (b - a)

    if a_sets > b_sets:
        return pair_a[0].strip()
    elif b_sets > a_sets:
        return pair_b[0].strip()
    else:
        return pair_a[0].strip() if a_pd >= b_pd else pair_b[0].strip()

# =================================================
# DATA
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

# =================================================
# FIXTURES
# =================================================
fixtures = load_json("data/fixtures.json", [])

# =================================================
# ADMIN SESSION
# =================================================
if "is_admin" not in st.session_state:
    st.session_state.is_admin = False


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
        "Enter Results",
        "Admin Login"
    ],
    horizontal=True
)

# =================================================
# HOME
# =================================================
if menu == "Home":
    st.info("Welcome to the House League Badminton Tournament")

# =================================================
# TEAMS
# =================================================
elif menu == "Teams":
    st.subheader("🏸 Teams")

    team_items = list(teams_data.items())

    # ✅ Create 4 columns (one per team)
    cols = st.columns(4)

    for idx, (team, players) in enumerate(team_items):
        with cols[idx]:
            # ✅ Team logo
            show_logo(team, width=100)

            # ✅ Team name
            st.markdown(f"### {team}")

            st.divider()

            # ✅ Player list
            for p in players:
                st.write(f"• {p}")

def render_fixture_card(tie, status):
    badge = "🕒 Scheduled" if status == "UPCOMING" else "✅ Completed"

    st.markdown(
        f"""
        <div style="
            padding:18px;
            border-radius:14px;
            border:1px solid #e0e0e0;
            background-color:#fafafa;
            margin-bottom:18px;
        ">
        <div style="text-align:right;font-size:12px;color:#666;">{badge}</div>
        """,
        unsafe_allow_html=True
    )

    # Header
    h1, h2, h3 = st.columns([1, 4, 1])
    with h1:
        show_logo(tie["team_a"], 48)
    with h2:
        st.markdown(
            f"""
            <div style="text-align:center;font-weight:600;">
                {tie['team_a']}
                <div style="color:#ff7f0e;font-size:14px;">VS</div>
                {tie['team_b']}
            </div>
            """,
            unsafe_allow_html=True
        )
    with h3:
        show_logo(tie["team_b"], 48)

    st.divider()

    # Matches (VERTICAL, READABLE)
    for idx, match in enumerate(tie["matches"], start=1):
        st.markdown(
            f"""
            <div style="
                padding:6px 0;
                font-size:14px;
                line-height:1.6;
            ">
                <b>M{idx}</b><br>
                {match[0]}<br>
                <span style="color:#ff7f0e;">vs</span><br>
                {match[1]}
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# FIXTURES
# =================================================
elif menu == "Fixtures":
    st.subheader("📅 Fixtures")

    results = load_results_from_sheet()
    completed_tie_ids = {r["tie_id"] for r in results}

    upcoming = [f for f in fixtures if f["tie_id"] not in completed_tie_ids]
    completed = [f for f in fixtures if f["tie_id"] in completed_tie_ids]

    # =================================================
    # NEXT SCHEDULED FIXTURES
    # =================================================
    if upcoming:
        st.markdown("## ⏭️ Next Scheduled Fixtures")

        for i in range(0, len(upcoming), 2):
            cols = st.columns(2)

            for col, tie in zip(cols, upcoming[i:i+2]):
                with col:
                    render_fixture_card(tie, status="UPCOMING")

    # =================================================
    # CLOSED FIXTURES
    # =================================================
    if completed:
        st.markdown("## ✅ Closed Fixtures")

        for i in range(0, len(completed), 2):
            cols = st.columns(2)

            for col, tie in zip(cols, completed[i:i+2]):
                with col:
                    render_fixture_card(tie, status="CLOSED")

# =================================================
# RESULTS
# =================================================
elif menu == "Results":
    results = load_results_from_sheet()

    if not results:
        st.warning("No results yet.")
    else:
        for r in results:
            st.subheader(f"{r['team_a']} vs {r['team_b']}")
            fixture = next(f for f in fixtures if f["tie_id"] == r["tie_id"])

            for i, m in enumerate(r["matches"], 1):
                if not m:
                    st.write(f"Match {i}: —")
                    continue
                score = " | ".join(f"{a}-{b}" for a,b in m["sets"])
                st.write(f"Match {i}: {score}")

                pair_a = fixture["matches"][i-1][0].split("/")
                pair_b = fixture["matches"][i-1][1].split("/")
                potm = calculate_potm(m["sets"], pair_a, pair_b)
                st.caption(f"🏅 Player of the Match: {potm}")
            st.divider()

# =================================================
# ENTER RESULTS
# =================================================
elif menu == "Enter Results":
    if not st.session_state.is_admin:
        st.warning("Admin only")
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
                a = st.number_input(
                    f"{tie['team_a']} Set {s+1}",
                    key=f"a{m}{s}",
                    min_value=0,max_value=30
                )
                b = st.number_input(
                    f"{tie['team_b']} Set {s+1}",
                    key=f"b{m}{s}",
                    min_value=0,max_value=30
                )
                if a > 0 or b > 0:
                    sets.append([a,b])
            match_results.append({"sets": sets})

        if st.button("✅ Save Results"):
            for i, match in enumerate(match_results):
                if match["sets"]:
                    save_result_to_sheet(
                        tie["tie_id"],
                        tie["team_a"],
                        tie["team_b"],
                        i+1,
                        match["sets"]
                    )
            st.success("Saved to Google Sheets ✅")
            st.rerun()

# =================================================
# TEAM STANDINGS
# =================================================
elif menu == "Team Standings":
    st.subheader("📊 Team Standings")

    results = load_results_from_sheet()

    table = defaultdict(lambda: {
        "Matches Played": 0,
        "Match Wins": 0,
        "Match Losses": 0,
        "Set Diff": 0,
        "Point Diff": 0,
        "Points": 0,
        "Form": []
    })

    for r in results:
        ta, tb = r["team_a"], r["team_b"]

        for m in r["matches"]:
            if not m or "sets" not in m or not m["sets"]:
                continue

            a_sets = b_sets = 0
            a_pts = b_pts = 0

            for a, b in m["sets"]:
                a_pts += a
                b_pts += b
                if a > b:
                    a_sets += 1
                else:
                    b_sets += 1

            # Matches played
            table[ta]["Matches Played"] += 1
            table[tb]["Matches Played"] += 1

            # Set & point difference
            table[ta]["Set Diff"] += (a_sets - b_sets)
            table[tb]["Set Diff"] += (b_sets - a_sets)
            table[ta]["Point Diff"] += (a_pts - b_pts)
            table[tb]["Point Diff"] += (b_pts - a_pts)

            # Match result
            if a_sets > b_sets:
                table[ta]["Match Wins"] += 1
                table[tb]["Match Losses"] += 1
                table[ta]["Form"].append("W")
                table[tb]["Form"].append("L")
            else:
                table[tb]["Match Wins"] += 1
                table[ta]["Match Losses"] += 1
                table[tb]["Form"].append("W")
                table[ta]["Form"].append("L")

    # Points = Match Wins × 2
    for t in table:
        table[t]["Points"] = table[t]["Match Wins"] * 2
        # Keep last 5 matches only
        table[t]["Form"] = " ".join(table[t]["Form"][-5:])

    df = pd.DataFrame.from_dict(table, orient="index")
    df = df.sort_values(
        by=["Points", "Match Wins", "Set Diff", "Point Diff"],
        ascending=False
    )

    st.dataframe(df, width="stretch")

# =================================================
elif menu == "Player Standings":
    st.subheader("👤 Player Standings")

    results = load_results_from_sheet()

    stats = defaultdict(lambda: {
        "Team": "",
        "Played": 0,
        "Match Wins": 0,
        "Set Diff": 0,
        "Point Diff": 0,
        "Form": []
    })

    # ✅ Initialize all players
    for team, players in teams_data.items():
        for p in players:
            stats[p]["Team"] = team

    # ✅ Accumulate match data
    for r in results:
        fixture = next((f for f in fixtures if f["tie_id"] == r["tie_id"]), None)
        if not fixture:
            continue

        for i, m in enumerate(r["matches"]):
            if not m or "sets" not in m or not m["sets"]:
                continue

            pair_a = fixture["matches"][i][0].split("/")
            pair_b = fixture["matches"][i][1].split("/")

            a_sets = b_sets = 0
            a_pts = b_pts = 0

            for a, b in m["sets"]:
                a_pts += a
                b_pts += b
                if a > b:
                    a_sets += 1
                else:
                    b_sets += 1

            a_win = a_sets > b_sets

            for p in pair_a:
                p = p.strip()
                stats[p]["Played"] += 1
                stats[p]["Set Diff"] += (a_sets - b_sets)
                stats[p]["Point Diff"] += (a_pts - b_pts)
                stats[p]["Form"].append("W" if a_win else "L")
                if a_win:
                    stats[p]["Match Wins"] += 1

            for p in pair_b:
                p = p.strip()
                stats[p]["Played"] += 1
                stats[p]["Set Diff"] += (b_sets - a_sets)
                stats[p]["Point Diff"] += (b_pts - a_pts)
                stats[p]["Form"].append("L" if a_win else "W")
                if not a_win:
                    stats[p]["Match Wins"] += 1

    # ✅ Convert to DataFrame
    dfp = (
        pd.DataFrame.from_dict(stats, orient="index")
        .reset_index()
        .rename(columns={"index": "Player"})
    )

    # ✅ Keep last 5 matches in Form
    dfp["Form"] = dfp["Form"].apply(lambda x: " ".join(x[-5:]))

    # ✅ Sort (International standard)
    dfp = dfp.sort_values(
        by=["Match Wins", "Set Diff", "Point Diff", "Played"],
        ascending=[False, False, False, True]
    ).reset_index(drop=True)

    # ✅ Add explicit Rank column (NO pandas index)
    dfp.insert(0, "Rank", dfp.index + 1)

    # ✅ Display final table
    st.dataframe(
        dfp[
            ["Rank", "Team", "Player", "Played", "Match Wins", "Set Diff", "Point Diff", "Form"]
        ],
        width="stretch",
        hide_index=True
    )

elif menu == "Admin Login":
    st.subheader("🔐 Admin Login")

    # ✅ Safety initialization
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False

    st.write("DEBUG: is_admin =", st.session_state.is_admin)

    if st.session_state.is_admin:
        st.success("✅ Logged in as Admin")

        if st.button("Logout"):
            st.session_state.is_admin = False
            st.rerun()

    else:
        try:
            admin_pwd = st.secrets["ADMIN_PASSWORD"]
        except KeyError:
            st.error("❌ ADMIN_PASSWORD not found in Streamlit Secrets")
            st.stop()

        pwd = st.text_input("Admin Password", type="password")

        if st.button("Login"):
            if pwd == admin_pwd:
                st.session_state.is_admin = True
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
