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


def output_to_excel_bytes(output):
    excel_file = BytesIO()

    with pd.ExcelWriter(excel_file, engine="openpyxl") as writer:
        for sheet_name, df in output.items():
            safe_sheet_name = sheet_name[:31]
            df.to_excel(writer, index=False, sheet_name=safe_sheet_name)

    return excel_file.getvalue()


def has_failures(df):
    return (
        isinstance(df, pd.DataFrame)
        and "Status" in df.columns
        and (df["Status"] == "FAIL").any()
    )


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
        output = generate_draw(
            grading_df=grading_df,
            court_df=court_df,
            rules_df=rules_df
        )

        if has_failures(output.get("Validation")):
            st.error("Validation failed. Please fix the input files.")
        elif has_failures(output.get("Court_Availability_Check")):
            st.warning("Draw generated, but some clubs exceed court availability.")
        else:
            st.success("Draw generated successfully. No court availability issues detected.")

        for sheet_name, df in output.items():
            st.subheader(sheet_name.replace("_", " "))

            if df.empty:
                st.info("No rows to display.")
            else:
                st.dataframe(df, use_container_width=True)

        excel_bytes = output_to_excel_bytes(output)

        st.download_button(
            label="Download Full Output Excel",
            data=excel_bytes,
            file_name="tennis_draw_output.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:
    st.warning("Please upload all three Excel files.")
