import pandas as pd


REQUIRED_GRADING_COLUMNS = ["Format", "Section", "Team_Name", "Club_Name"]
REQUIRED_COURT_COLUMNS = ["Club_Name", "Total_Courts_Available"]
REQUIRED_RULE_COLUMNS = ["Format", "Courts_Required"]


TEMPLATE_8 = {
    1: [(1, 8), (3, 6), (5, 4), (7, 2)],
    2: [(2, 5), (4, 3), (6, 1), (8, 7)],
    3: [(1, 4), (3, 2), (5, 7), (8, 6)],
    4: [(2, 1), (5, 8), (4, 6), (7, 3)],
    5: [(1, 7), (3, 5), (6, 2), (8, 4)],
    6: [(2, 4), (3, 8), (5, 1), (7, 6)],
    7: [(1, 3), (4, 7), (6, 5), (8, 2)],
}

TEMPLATE_6 = {
    1: [(1, 6), (2, 5), (3, 4)],
    2: [(6, 4), (5, 3), (1, 2)],
    3: [(2, 6), (3, 1), (4, 5)],
    4: [(6, 5), (1, 4), (2, 3)],
    5: [(3, 6), (4, 2), (5, 1)],
}


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


def validate_inputs(grading_df, court_df, rules_df):
    results = [
        check_required_columns(grading_df, REQUIRED_GRADING_COLUMNS, "grading_report"),
        check_required_columns(court_df, REQUIRED_COURT_COLUMNS, "court_availability"),
        check_required_columns(rules_df, REQUIRED_RULE_COLUMNS, "court_usage_rules"),
    ]

    validation_df = pd.DataFrame(results)

    if (validation_df["Status"] == "FAIL").any():
        return validation_df

    duplicate_teams = (
        grading_df
        .groupby(["Format", "Section", "Team_Name"])
        .size()
        .reset_index(name="Count")
    )

    duplicate_teams = duplicate_teams[duplicate_teams["Count"] > 1]

    if not duplicate_teams.empty:
        duplicate_teams.insert(0, "File", "grading_report")
        duplicate_teams.insert(1, "Status", "FAIL")
        duplicate_teams["Issue"] = "Duplicate Team_Name within Format + Section"
        return duplicate_teams

    return validation_df


def get_template(team_count):
    if team_count <= 6:
        return TEMPLATE_6, 6

    if team_count <= 8:
        return TEMPLATE_8, 8

    raise ValueError(
        f"Unsupported team count: {team_count}. "
        "Only 6 or 8 team sections are currently supported."
    )


def build_position_map(section_df, template_size):
    section_df = section_df.copy().reset_index(drop=True)

    teams = []

    for _, row in section_df.iterrows():
        teams.append({
            "Team_Name": row["Team_Name"],
            "Club_Name": row["Club_Name"],
        })

    while len(teams) < template_size:
        teams.append({
            "Team_Name": "BYE",
            "Club_Name": "BYE",
        })

    position_map = {}

    for idx, team in enumerate(teams, start=1):
        position_map[idx] = team

    return position_map


def generate_section_fixtures(format_name, section_name, section_df):
    team_count = len(section_df)
    template, template_size = get_template(team_count)
    position_map = build_position_map(section_df, template_size)

    fixtures = []

    for round_number, matches in template.items():
        for home_pos, away_pos in matches:
            home_team = position_map[home_pos]
            away_team = position_map[away_pos]

            fixtures.append({
                "Format": format_name,
                "Section": section_name,
                "Round": round_number,
                "Home_Position": home_pos,
                "Away_Position": away_pos,
                "Home_Team": home_team["Team_Name"],
                "Away_Team": away_team["Team_Name"],
                "Home_Club": home_team["Club_Name"],
                "Away_Club": away_team["Club_Name"],
            })

    mirrored_fixtures = []
    max_round = max(template.keys())

    for fixture in fixtures:
        mirrored = fixture.copy()
        mirrored["Round"] = fixture["Round"] + max_round
        mirrored["Home_Position"] = fixture["Away_Position"]
        mirrored["Away_Position"] = fixture["Home_Position"]
        mirrored["Home_Team"] = fixture["Away_Team"]
        mirrored["Away_Team"] = fixture["Home_Team"]
        mirrored["Home_Club"] = fixture["Away_Club"]
        mirrored["Away_Club"] = fixture["Home_Club"]
        mirrored_fixtures.append(mirrored)

    return fixtures + mirrored_fixtures


def generate_draw(grading_df, court_df, rules_df):
    validation_df = validate_inputs(grading_df, court_df, rules_df)

    if (validation_df["Status"] == "FAIL").any():
        return {
            "Validation": validation_df,
            "Fixtures": pd.DataFrame(),
            "Team_Position_Map": pd.DataFrame(),
        }

    all_fixtures = []
    all_position_maps = []

    grouped = grading_df.groupby(["Format", "Section"], sort=True)

    for (format_name, section_name), section_df in grouped:
        team_count = len(section_df)
        template, template_size = get_template(team_count)
        position_map = build_position_map(section_df, template_size)

        for position, team in position_map.items():
            all_position_maps.append({
                "Format": format_name,
                "Section": section_name,
                "Position": position,
                "Team_Name": team["Team_Name"],
                "Club_Name": team["Club_Name"],
            })

        section_fixtures = generate_section_fixtures(
            format_name=format_name,
            section_name=section_name,
            section_df=section_df,
        )

        all_fixtures.extend(section_fixtures)

    fixtures_df = pd.DataFrame(all_fixtures)

    fixtures_df = fixtures_df[
        (fixtures_df["Home_Team"] != "BYE") &
        (fixtures_df["Away_Team"] != "BYE")
    ]

    fixtures_df = fixtures_df.sort_values(
        ["Format", "Section", "Round", "Home_Team"]
    ).reset_index(drop=True)

    position_map_df = pd.DataFrame(all_position_maps)

    return {
        "Validation": validation_df,
        "Fixtures": fixtures_df,
        "Team_Position_Map": position_map_df,
    }
