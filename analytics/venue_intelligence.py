def get_best_venues(df, player):

    player_df = df[
        df["batter"] == player
    ]

    venues = (
        player_df
        .groupby("venue")
        .agg(
            runs=("runs", "sum"),
            balls=("runs", "count"),
            matches=("match_id", "nunique")
        )
    )

    venues["strike_rate"] = (
        venues["runs"]
        /
        venues["balls"]
    ) * 100

    venues = venues[
        venues["balls"] >= 50
    ]

    venues = venues.sort_values(
        ["runs", "strike_rate"],
        ascending=False
    ).reset_index()

    return venues.head(10)