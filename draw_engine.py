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
