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
