import streamlit as st
import json

st.set_page_config(
    page_title="🏸 Badminton Tournament",
    layout="wide"
)

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_fixtures():
    with open("data/fixtures.json", "r") as f:
        return json.load(f)

def load_results():
    try:
        with open("data/results.json", "r") as f:
            return json.load(f)
    except:
        return []

def save_results(data):
    with open("data/results.json", "w") as f:
        json.dump(data, f, indent=2)

fixtures = load_fixtures()
results = load_results()

# ---------------- UI ----------------
st.title("🏸 Badminton Tournament")

menu = st.radio(
    "Navigate",
    ["Home", "Fixtures", "Enter Results", "Standings"],
    horizontal=True
)

# ---------------- HOME ----------------
if menu == "Home":
    st.success("✅ Tournament system is running")
    st.write("Use the menu to view fixtures or enter match results.")

# ---------------- FIXTURES ----------------
elif menu == "Fixtures":
    st.subheader("📅 Fixtures")

    for tie in fixtures:
        st.markdown(
            f"""
            ### Tie {tie['tie_id']}
            **{tie['team_a']} vs {tie['team_b']}**
            """
        )
        for i, match in enumerate(tie["matches"], start=1):
            st.write(f"Match {i}: {match[0]}  vs  {match[1]}")

# ---------------- ENTER RESULTS ----------------
elif menu == "Enter Results":
    st.subheader("📝 Enter Match Results")

    tie = st.selectbox(
        "Select Tie",
        fixtures,
        format_func=lambda x: f" Tie {x['tie_id']} — {x['team_a']} vs {x['team_b']}"
    )

    match_results = []

    for m in range(3):
        st.markdown(f"### Match {m+1}")
        sets = []

        for s in range(3):
            col1, col2 = st.columns(2)
            with col1:
                a = st.number_input(
                    f"Set {s+1} – {tie['team_a']}",
                    min_value=0, max_value=30,
                    key=f"a_{tie['tie_id']}_{m}_{s}"
                )
            with col2:
                b = st.number_input(
                    f"Set {s+1} – {tie['team_b']}",
                    min_value=0, max_value=30,
                    key=f"b_{tie['tie_id']}_{m}_{s}"
                )

            if a > 0 or b > 0:
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
        save_results(results)
        st.success("✅ Results saved successfully")

# ---------------- STANDINGS (NEXT) ----------------
elif menu == "Standings":
    st.info("Standings will be calculated next")
