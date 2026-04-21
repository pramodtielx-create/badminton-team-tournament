import streamlit as st

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

if menu == "Home":
    st.success("✅ App is running correctly.")
    st.write("Use the menu above to navigate.")

elif menu == "Fixtures":
    st.info("Fixtures page – coming next")

elif menu == "Standings":
    st.info("Standings page – coming next")

elif menu == "Admin":
    st.info("Admin login – coming next")
``
