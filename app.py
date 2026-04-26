import streamlit as st
import json
import os
import requests
import pandas as pd
from collections import defaultdict

# =================================================
# PAGE CONFIG
# =================================================
st.set_page_config(page_title="🏸 Badminton Tournament", layout="wide")
st.title("🏸 Badminton Tournament")

# =================================================
# SECRETS
# =================================================
SCRIPT_URL = st.secrets["SCRIPT_URL"]
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

# =================================================
# DATA
# =================================================
teams_data = {
    "Smash Titans": ["Omkar", "Nishit", "Ganesh", "Sandeep W", "Amit", "Jayant"],
    "Quantum Force": ["Rajendra", "Aniket", "Deepak L", "Rahul", "Manmohan", "Prashant"],
    "Racket Scientists": ["Kiran", "Kaustubh", "Piyush", "Pradyum", "Amol S", "Amol P"],
    "Net Ninjas": ["Jaswanth", "Sandeepk", "Ritesh", "Vikram", "Pramod", "Deepak T"]
}

team_logos = {
    "Smash Titans": "assets/Logos/smash_titans.jpeg",
    "Quantum Force": "assets/Logos/quantum_force.jpeg",
    "Racket Scientists": "assets/Logos/racket_scientists.jpeg",
    "Net Ninjas": "assets/Logos/net_ninjas.jpeg"
}

# =================================================
# HELPERS
# =================================================
def show_logo(team, width=60):
    path = team_logos.get(team)
    if path and os.path.exists(path):
        st.image(path, width=width)

def load_json(path, default):
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return default

def load_results_from_sheet():
    r = requests.get(SCRIPT_URL, timeout=10)
    rows = r.json()

    results = defaultdict(lambda: {
        "tie_id": None,
        "team_a": "",
        "team_b": "",
        "matches": [{}, {}, {}]
    })

    for row in rows:
        try:
            sets = json.loads(row["sets_json"])
        except:
            continue

        if not sets:
            continue

        tie_id = int(row["tie_id"])
        results[tie_id]["tie_id"] = tie_id
        results[tie_id]["team_a"] = row["team_a"]
        results[tie_id]["team_b"] = row["team_b"]
        results[tie_id]["matches"][int(row["match_index"]) - 1] = {
            "sets": sets
        }

    return list(results.values())

# =================================================
# FIXTURE CARD RENDER
# =================================================
def render_fixture_card(tie, status, completed_matches):
    """
    tie               : fixture dict from fixtures.json
    status            : 'UPCOMING' or 'CLOSED'
    completed_matches : list of completed match indices, e.g. [1, 3]
    """

    badge = "🕒 Scheduled / In‑Progress" if status == "UPCOMING" else "✅ Closed"

    # =========================
    # Card container
    # =========================
    st.markdown(
        f"""
        <div style="
            padding:18px;
            border-radius:14px;
            border:1px solid #e0e0e0;
            background:#fafafa;
            margin-bottom:20px;
        ">
        <div style="text-align:right;font-size:12px;color:#666;">{badge}</div>
        """,
        unsafe_allow_html=True
    )

    # =========================
    # Header: logos + teams
    # =========================
    h1, h2, h3 = st.columns([1, 4, 1])
    with h1:
        show_logo(tie["team_a"], 48)

    with h2:
        st.markdown(
            f"""
            <div style="text-align:center;font-weight:600;">
                {tie['team_a']}
                <div style="color:#ff7f0e;">VS</div>
                {tie['team_b']}
            </div>
            """,
            unsafe_allow_html=True
        )

    with h3:
        show_logo(tie["team_b"], 48)

    st.divider()

    # =========================
    # Matches (M1 / M2 / M3)
    # =========================
    for idx, match in enumerate(tie["matches"], start=1):
        pair_a, pair_b = match

        if idx in completed_matches:
            icon = "✅"
            subtitle = "Completed"
            opacity = "1.0"
        else:
            icon = "🕒"
            subtitle = "Not played yet"
            opacity = "0.5"

        st.markdown(
            f"""
            <div style="padding:8px 0; line-height:1.6; opacity:{opacity};">
                <b>M{idx}</b> {icon}<br>
                {pair_a}<br>
                <span style="color:#ff7f0e;">vs</span><br>
                {pair_b}<br>
                <span style="font-size:12px;color:#777;">{subtitle}</span>
            </div>
            """,
            unsafe_allow_html=True
        )

    # =========================
    # Close card
    # =========================
    st.markdown("</div>", unsafe_allow_html=True)

# =================================================
# LOAD FIXTURES
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
# TEAMS (4 COLUMNS)
# =================================================
elif menu == "Teams":
    st.subheader("🏸 Teams")
    cols = st.columns(4)
    for col, (team, players) in zip(cols, teams_data.items()):
        with col:
            show_logo(team, 90)
            st.markdown(f"### {team}")
            st.divider()
            for p in players:
                st.write(f"• {p}")

# =================================================
# FIXTURES (NEXT → CLOSED)
# =================================================
elif menu == "Fixtures":
    st.subheader("📅 Fixtures")

    results = load_results_from_sheet()

    # Map tie_id -> completed matches
    completed_map = {}
    for r in results:
        done = []
        for idx, m in enumerate(r["matches"], start=1):
            if m and "sets" in m and m["sets"]:
                done.append(idx)
        completed_map[r["tie_id"]] = done

    upcoming = []
    closed = []

    for f in fixtures:
        if len(completed_map.get(f["tie_id"], [])) == 3:
            closed.append(f)
        else:
            upcoming.append(f)

    # ===============================
    # NEXT / IN-PROGRESS FIXTURES
    # ===============================
    if upcoming:
        st.markdown("## ⏭️ Next Scheduled Fixtures")

        for i in range(0, len(upcoming), 2):
            cols = st.columns(2)

            for col, tie in zip(cols, upcoming[i:i+2]):
                with col:
                    render_fixture_card(
                        tie,
                        "UPCOMING",
                        completed_map.get(tie["tie_id"], [])
                    )

    # ===============================
    # CLOSED FIXTURES
    # ===============================
    if closed:
        st.markdown("## ✅ Closed Fixtures")

        for i in range(0, len(closed), 2):
            cols = st.columns(2)

            for col, tie in zip(cols, closed[i:i+2]):
                with col:
                    render_fixture_card(
                        tie,
                        "CLOSED",
                        completed_map.get(tie["tie_id"], [])
                    )


elif menu == "Results":
    st.subheader("🏆 Results")

    results = load_results_from_sheet()

    if not results:
        st.info("No results have been entered yet.")
        st.stop()

    # Show 2 result cards per row
    for i in range(0, len(results), 2):
        cols = st.columns(2)

        for col, r in zip(cols, results[i:i+2]):
            with col:
                tie_id = r["tie_id"]
                fixture = next((f for f in fixtures if f["tie_id"] == tie_id), None)
                if not fixture:
                    continue

             # -------------------------
# Card container
# -------------------------
st.markdown(
    """
    <div style="
        padding:18px;
        border-radius:14px;
        border:1px solid #e0e0e0;
        background:#fafafa;
        margin-bottom:20px;
    ">
    """,
    unsafe_allow_html=True
)

# -------------------------
# Header: Logos + Names (ALIGNED)
# -------------------------
left, mid, right = st.columns([3, 1, 3])

with left:
    st.markdown(
        f"""
        <div style="text-align:center;">
            <img src="{team_logos[fixture['team_a']]}" width="60"><br>
            <b>{fixture['team_a']}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

with mid:
    st.markdown(
        """
        <div style="text-align:center;font-weight:600;color:#ff7f0e;
                    position:relative;top:22px;">
            VS
        </div>
        """,
        unsafe_allow_html=True
    )

with right:
    st.markdown(
        f"""
        <div style="text-align:center;">
            <img src="{team_logos[fixture['team_b']]}" width="60"><br>
            <b>{fixture['team_b']}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

st.divider()

# -------------------------
# Matches & Results (FULL WIDTH)
# -------------------------
for idx, match in enumerate(r["matches"], start=1):
    pair_a, pair_b = fixture["matches"][idx - 1]

    if not match or "sets" not in match or not match["sets"]:
        st.markdown(
            f"""
            <div style="padding:8px 0; opacity:0.5;">
                <b>M{idx}</b><br>
                {pair_a} <span style="color:#ff7f0e;">vs</span> {pair_b}<br>
                <i>Not played yet</i>
            </div>
            """,
            unsafe_allow_html=True
        )
        continue

    score = " | ".join(f"{a}-{b}" for a, b in match["sets"])

    st.markdown(
        f"""
        <div style="padding:8px 0;">
            <b>M{idx}</b><br>
            {pair_a} <span style="color:#ff7f0e;">vs</span> {pair_b}<br>
            <b>{score}</b>
        </div>
        """,
        unsafe_allow_html=True
    )

st.markdown("</div>", unsafe_allow_html=True)

                # -------------------------
                # Matches + Scores
                # -------------------------
                for idx, match in enumerate(r["matches"], start=1):
                    pair_a, pair_b = fixture["matches"][idx - 1]

                    if not match or "sets" not in match or not match["sets"]:
                        st.markdown(
                            f"""
                            <div style="padding:8px 0; opacity:0.5;">
                                <b>M{idx}</b><br>
                                {pair_a}<br>
                                <span style="color:#ff7f0e;">vs</span><br>
                                {pair_b}<br>
                                <i>Not played yet</i>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        continue

                    score = " | ".join(f"{a}-{b}" for a, b in match["sets"])

                    st.markdown(
                        f"""
                        <div style="padding:8px 0;">
                            <b>M{idx}</b><br>
                            {pair_a}<br>
                            <span style="color:#ff7f0e;">vs</span><br>
                            {pair_b}<br>
                            <b>{score}</b>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown("</div>", unsafe_allow_html=True)
# =================================================
# TEAM STANDINGS
# =================================================
elif menu == "Team Standings":
    st.subheader("📊 Team Standings")

    results = load_results_from_sheet()
    table = defaultdict(lambda: {
        "Matches": 0,
        "Wins": 0,
        "Losses": 0,
        "Set Diff": 0,
        "Point Diff": 0,
        "Points": 0
    })

    for r in results:
        ta, tb = r["team_a"], r["team_b"]
        for m in r["matches"]:
            if not m or "sets" not in m:
                continue

            a_sets = b_sets = a_pts = b_pts = 0
            for a, b in m["sets"]:
                a_pts += a
                b_pts += b
                if a > b:
                    a_sets += 1
                else:
                    b_sets += 1

            table[ta]["Matches"] += 1
            table[tb]["Matches"] += 1
            table[ta]["Set Diff"] += (a_sets - b_sets)
            table[tb]["Set Diff"] += (b_sets - a_sets)
            table[ta]["Point Diff"] += (a_pts - b_pts)
            table[tb]["Point Diff"] += (b_pts - a_pts)

            if a_sets > b_sets:
                table[ta]["Wins"] += 1
                table[tb]["Losses"] += 1
            else:
                table[tb]["Wins"] += 1
                table[ta]["Losses"] += 1

    for t in table:
        table[t]["Points"] = table[t]["Wins"] * 2

    df = pd.DataFrame.from_dict(table, orient="index").sort_values(
        by=["Points", "Set Diff", "Point Diff"], ascending=False
    )

    st.dataframe(df, width="stretch")

# =================================================
# PLAYER STANDINGS
# =================================================
elif menu == "Player Standings":
    st.subheader("👤 Player Standings")

    results = load_results_from_sheet()

    if not results:
        st.warning("No match results available yet.")
        st.stop()

    # ----------------------------
    # Initialize players
    # ----------------------------
    stats = defaultdict(lambda: {
        "Team": "",
        "Played": 0,
        "Match Wins": 0,
        "Set Diff": 0,
        "Point Diff": 0,
        "Form": []
    })

    for team, players in teams_data.items():
        for p in players:
            stats[p]["Team"] = team

    # ----------------------------
    # Process results
    # ----------------------------
    processed_matches = 0

    for r in results:
        tie_id = r["tie_id"]

        fixture = next((f for f in fixtures if f["tie_id"] == tie_id), None)
        if fixture is None:
            continue

        for i, m in enumerate(r["matches"]):
            if not m or "sets" not in m or not m["sets"]:
                continue

            processed_matches += 1
            sets = m["sets"]

            pair_a, pair_b = fixture["matches"][i]
            team_a_players = [p.strip() for p in pair_a.split("/")]
            team_b_players = [p.strip() for p in pair_b.split("/")]

            a_sets = b_sets = a_pts = b_pts = 0
            for a, b in sets:
                a_pts += a
                b_pts += b
                if a > b:
                    a_sets += 1
                else:
                    b_sets += 1

            a_win = a_sets > b_sets

            for p in team_a_players:
                stats[p]["Played"] += 1
                stats[p]["Set Diff"] += (a_sets - b_sets)
                stats[p]["Point Diff"] += (a_pts - b_pts)
                stats[p]["Form"].append("W" if a_win else "L")
                if a_win:
                    stats[p]["Match Wins"] += 1

            for p in team_b_players:
                stats[p]["Played"] += 1
                stats[p]["Set Diff"] += (b_sets - a_sets)
                stats[p]["Point Diff"] += (b_pts - a_pts)
                stats[p]["Form"].append("L" if a_win else "W")
                if not a_win:
                    stats[p]["Match Wins"] += 1

    if processed_matches == 0:
        st.warning("Results exist but no completed matches were found.")
        st.stop()

    # ----------------------------
    # Build table
    # ----------------------------
    df = (
        pd.DataFrame.from_dict(stats, orient="index")
        .reset_index()
        .rename(columns={"index": "Player"})
    )

    df["Form"] = df["Form"].apply(lambda x: " ".join(x[-5:]))

    df = df.sort_values(
        by=["Match Wins", "Set Diff", "Point Diff", "Played"],
        ascending=[False, False, False, True]
    ).reset_index(drop=True)

    df.insert(0, "Rank", df.index + 1)

    st.dataframe(
        df[
            [
                "Rank",
                "Team",
                "Player",
                "Played",
                "Match Wins",
                "Set Diff",
                "Point Diff",
                "Form",
            ]
        ],
        hide_index=True,
        width="stretch"
    )


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
            if pwd == ADMIN_PASSWORD:
                st.session_state.is_admin = True
                st.success("✅ Login successful")
                st.rerun()
            else:
                st.error("❌ Incorrect password")
