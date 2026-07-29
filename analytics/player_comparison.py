import pandas as pd


def get_player_stats(df, player):

    player_df = df[
        df["batter"] == player
    ]

    if len(player_df) == 0:
        return None

    runs = int(
        player_df["runs"].sum()
    )

    balls = len(player_df)

    matches = player_df[
        "match_id"
    ].nunique()

    strike_rate = round(
        (runs / balls) * 100,
        2
    ) if balls > 0 else 0

    dismissals = int(
        df[
            df["player_dismissed"] == player
        ].shape[0]
    )

    average = round(
        runs / dismissals,
        2
    ) if dismissals > 0 else runs

    innings_scores = (

        player_df

        .groupby("match_id")["runs"]

        .sum()

    )

    highest_score = int(
        innings_scores.max()
    )

    fifties = int(
        (
            (innings_scores >= 50)
            &
            (innings_scores < 100)
        ).sum()
    )

    hundreds = int(
        (innings_scores >= 100).sum()
    )

    fours = int(
        (player_df["runs"] == 4).sum()
    )

    sixes = int(
        (player_df["runs"] == 6).sum()
    )

    boundary_runs = fours * 4 + sixes * 6

    boundary_percentage = round(
        (boundary_runs / runs) * 100,
        2
    ) if runs else 0

    dot_ball_percentage = round(
        (
            (player_df["runs"] == 0).sum()
            /
            balls
        ) * 100,
        2
    )

    return {

        "Player": player,

        "Matches": matches,

        "Runs": runs,

        "Average": average,

        "Strike Rate": strike_rate,

        "Highest Score": highest_score,

        "50s": fifties,

        "100s": hundreds,

        "Boundary %": boundary_percentage,

        "Dot Ball %": dot_ball_percentage

    }


def compare_players(df, player1, player2):

    p1 = get_player_stats(
        df,
        player1
    )

    p2 = get_player_stats(
        df,
        player2
    )

    comparison = pd.DataFrame(

        {

            player1: list(
                p1.values()
            ),

            player2: list(
                p2.values()
            )

        },

        index=list(
            p1.keys()
        )

    )

    return comparison