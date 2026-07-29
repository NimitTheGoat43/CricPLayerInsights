import pandas as pd

def get_bowler_intelligence(df, player):

    bowler_df = df[
        df["bowler"] == player
    ]

    if len(bowler_df) == 0:

        return None

    # ==========================
    # BASIC STATS
    # ==========================

    wickets = int(
        bowler_df["wicket"].sum()
    )

    balls = len(bowler_df)

    overs = round(
        balls / 6,
        1
    )

    runs_conceded = int(
        bowler_df["total_runs"].sum()
    )

    economy = round(
        runs_conceded / overs,
        2
    ) if overs > 0 else 0

    bowling_sr = round(
        balls / wickets,
        2
    ) if wickets > 0 else 0

    boundary_balls = int(
        (bowler_df["runs"] >= 4).sum()
    )

    dot_balls = int(
        (bowler_df["runs"] == 0).sum()
    )

    boundary_percentage = round(
        (boundary_balls / balls) * 100,
        2
    ) if balls > 0 else 0

    dot_ball_percentage = round(
        (dot_balls / balls) * 100,
        2
    ) if balls > 0 else 0

    # ==========================
    # BEST VENUES
    # ==========================

    venue_stats = (
        bowler_df
        .groupby("venue")
        .agg(
            wickets=("wicket", "sum"),
            runs=("total_runs", "sum")
        )
        .sort_values(
            "wickets",
            ascending=False
        )
        .reset_index()
    )

    # ==========================
    # FAVOURITE BATTERS
    # (Most wickets against)
    # ==========================

    fav_batters = (

        bowler_df[
            bowler_df["player_dismissed"].fillna("") != ""
        ]

        .groupby("player_dismissed")

        .agg(
            wickets=("wicket", "sum")
        )

        .sort_values(
            "wickets",
            ascending=False
        )

        .reset_index()
    )

    dismissal_kinds = (
        bowler_df[
            bowler_df["player_dismissed"].fillna("") != ""
        ]
        .groupby("dismissal_kind")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .reset_index(drop=True)
    )

    top_teams = (
        bowler_df
        .groupby("batting_team")
        .agg(
            wickets=("wicket", "sum"),
            runs=("total_runs", "sum"),
            balls=("runs", "count")
        )
        .reset_index()
    )

    top_teams = top_teams.sort_values(
        ["wickets", "runs"],
        ascending=[False, True]
    ).reset_index(drop=True)

    # ==========================
    # DANGEROUS BATTERS
    # (Highest SR against bowler)
    # ==========================

    batter_stats = (

        bowler_df

        .groupby("batter")

        .agg(
            runs=("runs", "sum"),
            balls=("runs", "count")
        )

        .reset_index()
    )

    batter_stats = batter_stats[
        batter_stats["balls"] >= 20
    ]

    batter_stats["strike_rate"] = round(
        (
            batter_stats["runs"]
            /
            batter_stats["balls"]
        ) * 100,
        2
    )

    dangerous_batters = (
        batter_stats
        .sort_values(
            "strike_rate",
            ascending=False
        )
        .reset_index(drop=True)
    )

    # ==========================
    # PHASE ANALYSIS
    # ==========================

    powerplay = bowler_df[
        bowler_df["over"] <= 5
    ]

    middle = bowler_df[
        (bowler_df["over"] >= 6)
        &
        (bowler_df["over"] <= 15)
    ]

    death = bowler_df[
        bowler_df["over"] >= 16
    ]

    def phase_economy(data):

        balls = len(data)

        overs = balls / 6

        runs = data["total_runs"].sum()

        if overs == 0:
            return 0

        return round(
            runs / overs,
            2
        )

    phases = {

        "powerplay":
        phase_economy(powerplay),

        "middle":
        phase_economy(middle),

        "death":
        phase_economy(death)

    }

    return {

        "player": player,

        "wickets": wickets,

        "overs": overs,

        "economy": economy,

        "bowling_sr": bowling_sr,

        "boundary_percentage": boundary_percentage,

        "dot_ball_percentage": dot_ball_percentage,

        "venues":
        venue_stats.head(10),

        "fav_batters":
        fav_batters.head(10),

        "dismissal_kinds":
        dismissal_kinds.head(10),

        "top_teams":
        top_teams.head(10),

        "dangerous_batters":
        dangerous_batters.head(10),

        "phases":
        phases

    }