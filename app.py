import streamlit as st
import json

st.set_page_config(
    page_title="🏸 Badminton Tournament",
    layout="wide"
)

st.title("🏸 Badminton Tournament")

menu = st.radio(
    "Navigate",
    ["Home", "Fixtures", "Standings", "Admin"],
    horizontal=True
)

# -------- LOAD FIXTURES SAFELY --------
@st.cache_data
def load_fixtures():
    with open("data/fixtures.json", "r") as f:
        return json.load(f)

fixtures = load_fixtures()

# -------- PAGES --------
if menu == "Home":
    st.success("✅ App is running correctly.")
    st.write("Use the menu above to navigate.")

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
            st.write(
                f"Match {i}: {match[0]}  vs  {match[1]}"
            )

elif menu == "Standings":
    st.info("Standings page – coming next")

elif menu == "Admin":
    st.info("Admin login – coming next")
