import streamlit as st

st.set_page_config(page_title="Smart Agriculture Dashboard", layout="wide")

st.title("🌾 Smart Agriculture Dashboard")

st.sidebar.header("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Analytics", "Reports"])

if page == "Home":
    st.header("Welcome to Smart Agriculture")
    st.write("This dashboard provides insights into agricultural data.")
elif page == "Analytics":
    st.header("Analytics")
    st.write("Analytics content will be displayed here.")
elif page == "Reports":
    st.header("Reports")
    st.write("Reports content will be displayed here.")