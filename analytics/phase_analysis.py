def get_phase_analysis(df, player):

    player_df = df[
        df["batter"] == player
    ]

    powerplay = player_df[
        player_df["over"] <= 5
    ]

    middle = player_df[
        (player_df["over"] >= 6)
        &
        (player_df["over"] <= 15)
    ]

    death = player_df[
        player_df["over"] >= 16
    ]

    def sr(data):

        if len(data) == 0:
            return 0

        return round(
            (
                data["runs"].sum()
                /
                len(data)
            ) * 100,
            2
        )

    return {
        "powerplay_sr": sr(powerplay),
        "middle_sr": sr(middle),
        "death_sr": sr(death) }