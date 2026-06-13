import streamlit as st
import pandas as pd
from io import BytesIO

from draw_engine import generate_draw


st.set_page_config(
    page_title="Tennis Draw Generator",
    layout="wide"
)

st.title("🎾 Tennis Draw Generator")

st.write("Upload the required Excel files, then generate the draw.")

grading_file = st.file_uploader("Upload grading_report.xlsx", type=["xlsx"])
court_file = st.file_uploader("Upload court_availability.xlsx", type=["xlsx"])
rules_file = st.file_uploader("Upload court_usage_rules.xlsx", type=["xlsx"])


def dataframe_to_excel_bytes(df):
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Output")

    return output.getvalue()


if grading_file and court_file and rules_file:
    grading_df = pd.read_excel(grading_file)
    court_df = pd.read_excel(court_file)
    rules_df = pd.read_excel(rules_file)

    st.success("All files loaded successfully.")

    with st.expander("Preview uploaded files"):
        st.subheader("Grading Report")
        st.dataframe(grading_df.head())

        st.subheader("Court Availability")
        st.dataframe(court_df.head())

        st.subheader("Court Usage Rules")
        st.dataframe(rules_df.head())

    if st.button("Generate Draw"):
        output_df = generate_draw(
            grading_df=grading_df,
            court_df=court_df,
            rules_df=rules_df
        )

        st.subheader("Generated Output")
        st.dataframe(output_df)

        excel_bytes = dataframe_to_excel_bytes(output_df)

        st.download_button(
            label="Download Output Excel",
            data=excel_bytes,
            file_name="tennis_draw_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.warning("Please upload all three Excel files.")
