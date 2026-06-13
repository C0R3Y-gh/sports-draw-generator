import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="Tennis Draw Generator",
    layout="wide"
)

st.title("🎾 Tennis Draw Generator")

st.markdown(
    """
    Upload the required source files.
    """
)

grading_file = st.file_uploader(
    "Grading Report",
    type=["xlsx"]
)

court_file = st.file_uploader(
    "Court Availability",
    type=["xlsx"]
)

rules_file = st.file_uploader(
    "Court Usage Rules",
    type=["xlsx"]
)

if grading_file:
    grading_df = pd.read_excel(grading_file)

    st.subheader("Grading Report Preview")
    st.dataframe(grading_df.head())

if court_file:
    court_df = pd.read_excel(court_file)

    st.subheader("Court Availability Preview")
    st.dataframe(court_df.head())

if rules_file:
    rules_df = pd.read_excel(rules_file)

    st.subheader("Court Usage Rules Preview")
    st.dataframe(rules_df.head())

if grading_file and court_file and rules_file:
    st.success("All files loaded successfully.")

    if st.button("Generate Draw"):
        st.info("Draw generation logic coming next...")
