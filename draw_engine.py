import pandas as pd


def generate_draw(grading_df, court_df, rules_df):
    """
    Temporary engine test.
    This confirms Streamlit can pass uploaded Excel data into the draw engine.
    """

    summary = pd.DataFrame({
        "Input_File": [
            "grading_report",
            "court_availability",
            "court_usage_rules"
        ],
        "Rows_Loaded": [
            len(grading_df),
            len(court_df),
            len(rules_df)
        ],
        "Columns_Loaded": [
            len(grading_df.columns),
            len(court_df.columns),
            len(rules_df.columns)
        ]
    })

    return summary
