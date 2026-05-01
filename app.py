import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import requests
from collections import defaultdict


# After imports, before menu
components.html("""
<style>
@media (max-width: 768px) {
    .grid { grid-template-columns: 1fr !important; }
}
</style>
""", height=0)
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
#def load_results():
 #   rows = requests.get(SCRIPT_URL, timeout=10).json()
  #  data = defaultdict(lambda: {"matches": [{}, {}, {}]})

   # for row in rows:
    #    try:
     #       tie_id = int(row["tie_id"])
      #      idx = int(row["match_index"]) - 1
       #     sets = json.loads(row["sets_json"])
        #    if sets:
         #       data[tie_id]["matches"][idx] = {"sets": sets}
        #except:
         #   continue
    #return dict(data)

@st.cache_data(ttl=30, show_spinner=False)
def load_results():
    """
    Safely load match results from Google Sheets / Apps Script.
    Never crashes the app.
    Cached for 30 seconds to avoid rate limits.
    """
    data = defaultdict(lambda: {"matches": [{}, {}, {}]})

    try:
        response = requests.get(SCRIPT_URL, timeout=8)
        response.raise_for_status()
        rows = response.json()

        for row in rows:
            try:
                tie_id = int(row["tie_id"])
                idx = int(row["match_index"]) - 1
                sets = json.loads(row["sets_json"])
                if sets:
                    data[tie_id]["matches"][idx] = {"sets": sets}
            except Exception:
                continue

    except requests.exceptions.Timeout:
        st.warning("⚠️ Results service is slow. Showing cached / empty results.")
    except requests.exceptions.RequestException:
        st.warning("⚠️ Results service unavailable. Please retry later.")
    except Exception:
        st.warning("⚠️ Unexpected error loading results.")

    return dict(data)


# =================================================
# MENU
# =================================================

menu = st.radio(
    "Navigate",
    ["Overview", "Fixtures", "Results", "Teams", "Team Standings","Player Standings","Insights"],
    horizontal=True
)

# =================================================
# OVERVIEW
# =================================================
if menu == "Overview":
    st.subheader("Tournament Overview")

    # Derived metrics
    total_rounds = len(set(f["round_no"] for f in fixtures))
    total_fixtures = len(fixtures)
    total_matches = total_fixtures * 3

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Status", "LIVE")
    c2.metric("Teams", len(teams_data))
    c3.metric("Rounds", total_rounds)
    c4.metric("Fixtures", total_fixtures)
    c5.metric("Total Matches", total_matches)

# =================================================
# FIXTURES (FULLY HTML – CSS GUARANTEED)
# =================================================
elif menu == "Fixtures":
    st.subheader("Fixtures")

    results = load_results()

    # ==================================================
    # FILTER CHECKBOXES (REPLACES SELECTBOX)
    # ==================================================
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        show_round_1 = st.checkbox("Round 1", value=False)
    with c2:
        show_round_2 = st.checkbox("Round 2", value=True)   # ✅ default
    with c3:
        show_completed = st.checkbox("Completed", value=False)
    with c4:
        show_pending = st.checkbox("Pending", value=True)  # ✅ default

    # ==================================================
    # HELPER: fixture status
    # ==================================================
    def fixture_completed(f):
        match_results = results.get(f["tie_id"], {}).get("matches", [])
        completed_count = sum(
            1 for m in match_results if m and "sets" in m
        )
        return completed_count == len(f["matches"])

    # ==================================================
    # FILTER FIXTURES BASED ON CHECKBOXES
    # ==================================================
    filtered_fixtures = []
    for f in fixtures:
        # round filter
        round_ok = (
            (f.get("round_no") == 1 and show_round_1) or
            (f.get("round_no") == 2 and show_round_2)
        )

        if not round_ok:
            continue

        completed = fixture_completed(f)

        # status filter
        status_ok = (
            (completed and show_completed) or
            (not completed and show_pending)
        )

        if status_ok:
            filtered_fixtures.append(f)

    if not filtered_fixtures:
        st.info("No fixtures match the selected filters.")
        st.stop()

    # ==================================================
    # SUMMARY (UNCHANGED LOOK & FEEL)
    # ==================================================
    total_ties = len(filtered_fixtures)
    total_matches = total_ties * 3
    completed_matches = sum(
        1
        for f in filtered_fixtures
        for m in results.get(f["tie_id"], {}).get("matches", [])
        if m and "sets" in m
    )

    st.info(
        f"📊 **Fixtures Summary:** "
        f"{completed_matches} / {total_matches} matches completed"
    )

    # ==================================================
    # HTML (UNCHANGED)
    # ==================================================
    html = """
    <style>
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }
        .card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 20px;
            font-family: Inter, Segoe UI, sans-serif;
        }
        .title {
            font-size: 16px;
            font-weight: 600;
            margin-bottom: 4px;
        }
        .vs {
            color: #f59e0b;
            padding: 0 4px;
        }
        .meta {
            font-size: 13px;
            color: #6b7280;
            margin-bottom: 6px;
        }
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

    for f in filtered_fixtures:
        tie_id = f["tie_id"]
        match_results = results.get(tie_id, {}).get("matches", [])

        completed_count = sum(
            1 for m in match_results if m and "sets" in m
        )
        percent = int((completed_count / 3) * 100)

        html += f"""
        <div class="card">
            <div class="title">
                {f["team_a"]}<span class="vs">vs</span>{f["team_b"]}
            </div>
            <div class="meta">{completed_count} / 3 matches completed</div>

            <div class="progress">
                <div class="bar" style="width:{percent}%"></div>
            </div>

            <div class="divider"></div>
        """

        for idx, (pair_a, pair_b) in enumerate(f["matches"]):
            match_data = match_results[idx] if idx < len(match_results) else None
            status = "✅" if match_data and "sets" in match_data else "⏳"

            html += f"""
            <div class="row">
                <strong>M{idx + 1}</strong> {status}
                {pair_a} <span class="vs">vs</span> {pair_b}
            </div>
            """

        html += "</div>"

    html += "</div>"

    components.html(html, height=1200, scrolling=True)
# =================================================
# RESULTS
# =================================================
# =================================================
# RESULTS
# =================================================
elif menu == "Results":
    import streamlit.components.v1 as components

    st.subheader("Results")

    results = load_results()

    # ==================================================
    # FILTER CHECKBOXES (SAME AS FIXTURES)
    # ==================================================
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        show_round_1 = st.checkbox("Round 1", value=False, key="res_r1")
    with c2:
        show_round_2 = st.checkbox("Round 2", value=True, key="res_r2")   # ✅ default
    with c3:
        show_completed = st.checkbox("Completed", value=False, key="res_done")
    with c4:
        show_pending = st.checkbox("Pending", value=True, key="res_pending")  # ✅ default

    # ==================================================
    # HELPER — COMPLETION LOGIC (MATCHES FIXTURES)
    # ==================================================
    def fixture_completed(f):
        match_results = results.get(f["tie_id"], {}).get("matches")

        # ✅ If results not available yet → treat as pending (but still SHOW)
        if not match_results:
            return False

        completed_count = sum(
            1 for m in match_results if m and "sets" in m
        )
        return completed_count == len(f["matches"])

    # ==================================================
    # FILTER FIXTURES (SAME MODEL AS FIXTURES PAGE)
    # ==================================================
    filtered_fixtures = []
    for f in fixtures:
        # round filter
        round_ok = (
            (f.get("round_no") == 1 and show_round_1) or
            (f.get("round_no") == 2 and show_round_2)
        )
        if not round_ok:
            continue

        completed = fixture_completed(f)

        # status filter
        status_ok = (
            (completed and show_completed) or
            (not completed and show_pending)
        )

        if status_ok:
            filtered_fixtures.append(f)

    if not filtered_fixtures:
        st.info(
            "No results match the selected filters.\n\n"
            "Tip:\n"
            "• Select **Pending** to see ongoing ties\n"
            "• A tie appears as **Completed** only when all 3 matches finish"
        )
        st.stop()

    # ==================================================
    # RESULTS UI — TWO CARDS PER ROW ✅
    # ==================================================
  elif menu == "Results":
    import streamlit.components.v1 as components

    st.subheader("Results")

    results = load_results()

    # ================= FILTERS =================
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        show_round_1 = st.checkbox("Round 1", value=False, key="res_r1")
    with c2:
        show_round_2 = st.checkbox("Round 2", value=True, key="res_r2")
    with c3:
        show_completed = st.checkbox("Completed", value=False, key="res_done")
    with c4:
        show_pending = st.checkbox("Pending", value=True, key="res_pending")

    def fixture_completed(f):
        mr = results.get(f["tie_id"], {}).get("matches")
        if not mr:
            return False
        return sum(1 for m in mr if m and "sets" in m) == len(f["matches"])

    filtered_fixtures = []
    for f in fixtures:
        round_ok = (
            (f["round_no"] == 1 and show_round_1) or
            (f["round_no"] == 2 and show_round_2)
        )
        if not round_ok:
            continue

        completed = fixture_completed(f)
        status_ok = (
            (completed and show_completed) or
            (not completed and show_pending)
        )

        if status_ok:
            filtered_fixtures.append(f)

    if not filtered_fixtures:
        st.info("No results match the selected filters.")
        st.stop()

    # ================= UI =================
    html = """
    <style>
        .grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
        }
        .result-card {
            background: #ffffff;
            border: 1px solid #e5e7eb;
            border-radius: 14px;
            padding: 18px;
        }
        .match {
            padding: 6px 0;
            font-size: 14px;
            color: #374151;   /* ✅ CRITICAL FIX */
        }
        .winner {
            color: #16a34a;
            font-weight: 600;
        }
        .loser {
            color: #6b7280;
        }
        .score {
            font-weight: 600;
            margin-left: 6px;
        }
    </style>

    <div class="grid">
    """

    for f in filtered_fixtures:
        tid = f["tie_id"]
        result_matches = results.get(tid, {}).get("matches", [])

        html += f"""
        <div class="result-card">
            <div style="font-size:16px;font-weight:600;margin-bottom:8px;">
                Round {f["round_no"]} · {f["team_a"]} vs {f["team_b"]}
            </div>
        """

        for idx, (pA, pB) in enumerate(f["matches"], start=1):
            match_data = result_matches[idx - 1] if idx - 1 < len(result_matches) else None

            if not match_data or "sets" not in match_data:
                html += f"""
                <div class="match">
                    <strong>M{idx}</strong>: {pA} vs {pB} — Pending
                </div>
                """
                continue

            a_sets = sum(1 for a, b in match_data["sets"] if a > b)
            b_sets = len(match_data["sets"]) - a_sets
            score = " | ".join(f"{a}-{b}" for a, b in match_data["sets"])

            win = "winner" if a_sets > b_sets else "loser"
            lose = "loser" if a_sets > b_sets else "winner"

            html += f"""
            <div class="match">
                <span class="{win}">{pA}</span>
                vs
                <span class="{lose}">{pB}</span>
                <span class="score">({score})</span>
            </div>
            """

        html += "</div>"

    html += "</div>"

    components.html(html, height=900, scrolling=True)

# =================================================
# TEAM STANDINGS (BASIC, STABLE)
# =================================================
elif menu == "Team Standings":
    st.subheader("🏆 Team Standings")

    results = load_results()

    if not results:
        st.info("No completed team matches yet.")
        st.stop()

    table = defaultdict(lambda: {
        "Played": 0,
        "Wins": 0,
        "Losses": 0,
        "Sets Won": 0,
        "Sets Lost": 0,
        "Points Won": 0,
        "Points Lost": 0,
        "Form": []
    })

    for tid, r in results.items():
        # Find matching fixture
        fixture = next((f for f in fixtures if f["tie_id"] == tid), None)
        if not fixture:
            continue

        team_a = fixture["team_a"]
        team_b = fixture["team_b"]

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

            # Played
            table[team_a]["Played"] += 1
            table[team_b]["Played"] += 1

            # Sets
            table[team_a]["Sets Won"] += a_sets
            table[team_a]["Sets Lost"] += b_sets
            table[team_b]["Sets Won"] += b_sets
            table[team_b]["Sets Lost"] += a_sets

            # Points
            table[team_a]["Points Won"] += a_pts
            table[team_a]["Points Lost"] += b_pts
            table[team_b]["Points Won"] += b_pts
            table[team_b]["Points Lost"] += a_pts

            # Result
            if a_sets > b_sets:
                table[team_a]["Wins"] += 1
                table[team_b]["Losses"] += 1
                table[team_a]["Form"].append("W")
                table[team_b]["Form"].append("L")
            else:
                table[team_b]["Wins"] += 1
                table[team_a]["Losses"] += 1
                table[team_b]["Form"].append("W")
                table[team_a]["Form"].append("L")

    # Build DataFrame
    df = pd.DataFrame.from_dict(table, orient="index")

    if df.empty:
        st.warning("Team results exist but no completed matches found.")
        st.stop()

    df["Set Diff"] = df["Sets Won"] - df["Sets Lost"]
    df["Point Diff"] = df["Points Won"] - df["Points Lost"]
    df["League Points"] = df["Wins"] * 2
    df["Recent Form"] = df["Form"].apply(lambda x: " ".join(x[-5:]))

    df = df.drop(columns=["Form"])

    # International sorting
    df = df.sort_values(
        by=["League Points", "Wins", "Set Diff", "Point Diff"],
        ascending=False
    )

    df.insert(0, "Rank", range(1, len(df) + 1))

    st.dataframe(df, use_container_width=True)

#Teams###########################################
elif menu == "Teams":
    st.subheader("🏸 Team Squads")

    import pandas as pd

    # teams_data is already defined in your app
    # Example:
    # teams_data = {
    #   "Smash Titans": [...],
    #   "Quantum Force": [...],
    #   "Racket Scientists": [...],
    #   "Net Ninjas": [...]
    # }

    # Find the max number of players in any team
    max_len = max(len(players) for players in teams_data.values())

    table = {}

    for team, players in teams_data.items():
        # Pad with empty strings so all columns are equal length
        padded_players = players + [""] * (max_len - len(players))
        table[team] = padded_players

    df = pd.DataFrame(table)

    st.dataframe(df, use_container_width=True, hide_index=True)
# =================================================
# PLAYER STANDINGS
# =================================================
elif menu == "Player Standings":
    st.subheader("👤 Player Standings")

    results = load_results()

    from collections import defaultdict
    import pandas as pd

    stats = defaultdict(lambda: {
        "Team": "",
        "Played": 0,
        "Wins": 0,
        "Losses": 0,
        "Sets Won": 0,
        "Sets Lost": 0,
        "Points Won": 0,
        "Points Lost": 0,
        "Form": []
    })

    # Assign teams to players
    for team, players in teams_data.items():
        for p in players:
            stats[p]["Team"] = team

    # Process results
    for tid, r in results.items():
        fixture = next(f for f in fixtures if f["tie_id"] == tid)

        for idx, m in enumerate(r["matches"]):
            if not m:
                continue

            pair_a, pair_b = fixture["matches"][idx]
            team_a_players = [p.strip() for p in pair_a.split("/")]
            team_b_players = [p.strip() for p in pair_b.split("/")]

            a_sets = b_sets = a_pts = b_pts = 0
            for a, b in m["sets"]:
                a_pts += a
                b_pts += b
                if a > b:
                    a_sets += 1
                else:
                    b_sets += 1

            # Team A players
            for p in team_a_players:
                stats[p]["Played"] += 1
                stats[p]["Sets Won"] += a_sets
                stats[p]["Sets Lost"] += b_sets
                stats[p]["Points Won"] += a_pts
                stats[p]["Points Lost"] += b_pts
                if a_sets > b_sets:
                    stats[p]["Wins"] += 1
                    stats[p]["Form"].append("W")
                else:
                    stats[p]["Losses"] += 1
                    stats[p]["Form"].append("L")

            # Team B players
            for p in team_b_players:
                stats[p]["Played"] += 1
                stats[p]["Sets Won"] += b_sets
                stats[p]["Sets Lost"] += a_sets
                stats[p]["Points Won"] += b_pts
                stats[p]["Points Lost"] += a_pts
                if b_sets > a_sets:
                    stats[p]["Wins"] += 1
                    stats[p]["Form"].append("W")
                else:
                    stats[p]["Losses"] += 1
                    stats[p]["Form"].append("L")

    # Build DataFrame
    df = pd.DataFrame.from_dict(stats, orient="index")

    df["Set Diff"] = df["Sets Won"] - df["Sets Lost"]
    df["Point Diff"] = df["Points Won"] - df["Points Lost"]
    df["Recent Form"] = df["Form"].apply(lambda x: " ".join(x[-5:]))

    df = df.drop(columns=["Form"])

    # Sort standings
    df = df.sort_values(
        by=["Wins", "Set Diff", "Point Diff", "Played"],
        ascending=[False, False, False, True]
    )

    # Add Rank column
    df.insert(0, "Rank", range(1, len(df) + 1))

    # Move Player name from index to column
    df = df.reset_index().rename(columns={"index": "Player"})

    # Final column order (as requested)
    column_order = [
        "Team",
        "Rank",
        "Player",
        "Played",
        "Wins",
        "Losses",
        "Sets Won",
        "Sets Lost",
        "Set Diff",
        "Points Won",
        "Points Lost",
        "Point Diff",
        "Recent Form"
    ]

    df = df[column_order]

    # Display without index (removes 0 / duplicate ranking column)
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )

# =================================================
# INSIGHTS
# =================================================
elif menu == "Insights":
    st.subheader("📊 Insights")
    st.info("Match highlights and key moments from completed fixtures.")

    results = load_results()

    if not results:
        st.warning("No match data available yet.")
    else:
        st.markdown("## 🔥 Match Highlights")

        # Create 3 responsive columns
        cols = st.columns(3)
        col_index = 0

        for tid, r in results.items():
            fixture = next(f for f in fixtures if f["tie_id"] == tid)

            for idx, m in enumerate(r["matches"]):
                if not m:
                    continue

                pair_a, pair_b = fixture["matches"][idx]

                a_sets = b_sets = 0
                a_pts = b_pts = 0

                for a, b in m["sets"]:
                    a_pts += a
                    b_pts += b
                    if a > b:
                        a_sets += 1
                    else:
                        b_sets += 1

                winner = pair_a if a_sets > b_sets else pair_b

                # Place card in current column
                with cols[col_index]:
                    st.markdown(
                        f"""
                        ### 🆚 Match {idx + 1}
                        **{pair_a} vs {pair_b}**

                        🏆 **Winner:** {winner}  
                        📊 **Sets:** {a_sets} – {b_sets}  
                        🎯 **Points:** {a_pts} – {b_pts}
                        """
                    )

                    

                # Move to next column (0 → 1 → 2 → 0)
                col_index = (col_index + 1) % 3
