import pandas as pd


REQUIRED_GRADING_COLUMNS = [
    "Format",
    "Section",
    "Team_Name",
    "Club_Name",
]

REQUIRED_COURT_COLUMNS = [
    "Club_Name",
    "Total_Courts_Available",
]

REQUIRED_RULE_COLUMNS = [
    "Format",
    "Courts_Required",
]


def check_required_columns(df, required_columns, file_name):
    missing = [col for col in required_columns if col not in df.columns]

    if missing:
        return {
            "File": file_name,
            "Status": "FAIL",
            "Issue": f"Missing columns: {', '.join(missing)}",
        }

    return {
        "File": file_name,
        "Status": "PASS",
        "Issue": "",
    }


def generate_draw(grading_df, court_df, rules_df):
    validation_results = []

    validation_results.append(
        check_required_columns(
            grading_df,
            REQUIRED_GRADING_COLUMNS,
            "grading_report",
        )
    )

    validation_results.append(
        check_required_columns(
            court_df,
            REQUIRED_COURT_COLUMNS,
            "court_availability",
        )
    )

    validation_results.append(
        check_required_columns(
            rules_df,
            REQUIRED_RULE_COLUMNS,
            "court_usage_rules",
        )
    )

    validation_df = pd.DataFrame(validation_results)

    if (validation_df["Status"] == "FAIL").any():
        return validation_df

    summary = pd.DataFrame({
        "Check": [
            "Grading rows loaded",
            "Court availability rows loaded",
            "Court usage rule rows loaded",
            "Formats detected",
            "Sections detected",
            "Clubs detected",
        ],
        "Result": [
            len(grading_df),
            len(court_df),
            len(rules_df),
            ", ".join(sorted(grading_df["Format"].dropna().astype(str).unique())),
            grading_df.groupby(["Format", "Section"]).ngroups,
            grading_df["Club_Name"].nunique(),
        ],
    })

    return summary
