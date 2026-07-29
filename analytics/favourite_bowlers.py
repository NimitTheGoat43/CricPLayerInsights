import pandas as pd

def get_favourite_bowlers(df, player):

    player_df = df[
        df["batter"] == player
    ]

    stats = (
        player_df
        .groupby("bowler")
        .agg(
            runs=("runs", "sum"),
            balls=("runs", "count")
        )
        .reset_index()
    )

    stats["strike_rate"] = round(
        (
            stats["runs"]
            /
            stats["balls"]
        ) * 100,
        2
    )

    # Minimum sample size
    stats = stats[
        stats["balls"] >= 20
    ]

    stats = stats.sort_values(
        by="strike_rate",
        ascending=False
    )

    stats = stats.reset_index(
        drop=True
    )

    return stats.head(10)