from analytics.dangerous_bowlers import get_dangerous_bowlers
from analytics.favourite_bowlers import get_favourite_bowlers
from analytics.venue_intelligence import get_best_venues
from analytics.phase_analysis import get_phase_analysis


def _get_batting_profile(player_df, player):

    runs = int(player_df["runs"].sum())
    balls = len(player_df)

    dismissals = int(
        player_df["player_dismissed"]
        .fillna("")
        .eq(player)
        .sum()
    )

    innings = player_df["match_id"].nunique()

    not_outs = innings - dismissals

    average = round(
        runs / dismissals,
        2
    ) if dismissals > 0 else runs

    strike_rate = round(
        (runs / balls) * 100,
        2
    ) if balls > 0 else 0

    # -------------------------
    # Ball Outcome Statistics
    # -------------------------

    dots = int((player_df["runs"] == 0).sum())
    singles = int((player_df["runs"] == 1).sum())
    doubles = int((player_df["runs"] == 2).sum())
    triples = int((player_df["runs"] == 3).sum())
    fours = int((player_df["runs"] == 4).sum())
    sixes = int((player_df["runs"] == 6).sum())

    boundary_runs = fours * 4 + sixes * 6

    boundary_percentage = round(
        (boundary_runs / runs) * 100,
        2
    ) if runs > 0 else 0

    dot_ball_percentage = round(
        (dots / balls) * 100,
        2
    ) if balls > 0 else 0

    # -------------------------
    # Highest Score / 50 / 100
    # -------------------------

    innings_runs = (
        player_df
        .groupby("match_id")["runs"]
        .sum()
    )

    highest_score = int(
        innings_runs.max()
    ) if len(innings_runs) else 0

    fifties = int(
        (
            (innings_runs >= 50)
            &
            (innings_runs < 100)
        ).sum()
    )

    hundreds = int(
        (innings_runs >= 100).sum()
    )

    # -------------------------
    # Dismissal Breakdown
    # -------------------------

    dismissal_breakdown = (

        player_df[
            player_df["player_dismissed"]
            .fillna("")
            .eq(player)
        ]

        .groupby("dismissal_kind")

        .size()

        .reset_index(name="count")

        .sort_values(
            "count",
            ascending=False
        )

        .reset_index(drop=True)

    )

    # -------------------------
    # Best Opposition Teams
    # -------------------------

    top_teams = (

        player_df

        .groupby("bowling_team")

        .agg(

            runs=("runs", "sum"),

            balls=("runs", "count"),

            matches=("match_id", "nunique")

        )

        .reset_index()

    )

    top_teams["strike_rate"] = round(

        (top_teams["runs"] /
         top_teams["balls"]) * 100,

        2

    )

    top_teams = (

        top_teams[
            top_teams["balls"] >= 50
        ]

        .sort_values(

            ["runs", "strike_rate"],

            ascending=[False, False]

        )

        .reset_index(drop=True)

    )

    return {

        "average": average,

        "strike_rate": strike_rate,

        "innings": innings,

        "not_outs": not_outs,

        "highest_score": highest_score,

        "fifties": fifties,

        "hundreds": hundreds,

        "dots": dots,

        "singles": singles,

        "doubles": doubles,

        "triples": triples,

        "fours": fours,

        "sixes": sixes,

        "boundary_percentage": boundary_percentage,

        "dot_ball_percentage": dot_ball_percentage,

        "dismissal_breakdown": dismissal_breakdown,

        "top_teams": top_teams

    }


def generate_player_report(df, player):

    player_df = df[
        df["batter"] == player
    ]

    if player_df.empty:
        return None

    runs = int(
        player_df["runs"].sum()
    )

    balls = len(player_df)

    matches = player_df[
        "match_id"
    ].nunique()

    profile = _get_batting_profile(
        player_df,
        player
    )

    dangerous = get_dangerous_bowlers(
        df,
        player
    )

    favourite = get_favourite_bowlers(
        df,
        player
    )

    venues = get_best_venues(
        df,
        player
    )

    phases = get_phase_analysis(
        df,
        player
    )

    summary = (

        f"{player} has scored "

        f"{runs} IPL runs "

        f"in {matches} matches "

        f"at an average of "

        f"{profile['average']} "

        f"and strike rate of "

        f"{profile['strike_rate']}. "

        f"He has "

        f"{profile['fifties']} fifties "

        f"and "

        f"{profile['hundreds']} hundreds. "

        f"{profile['boundary_percentage']}% "

        f"of his runs have come "

        f"through boundaries."

    )

    return {

        "player": player,

        "runs": runs,

        "matches": matches,

        "innings": profile["innings"],

        "balls": balls,

        "average": profile["average"],

        "strike_rate": profile["strike_rate"],

        "highest_score": profile["highest_score"],

        "fifties": profile["fifties"],

        "hundreds": profile["hundreds"],

        "not_outs": profile["not_outs"],

        "dots": profile["dots"],

        "singles": profile["singles"],

        "doubles": profile["doubles"],

        "triples": profile["triples"],

        "fours": profile["fours"],

        "sixes": profile["sixes"],

        "boundary_percentage": profile["boundary_percentage"],

        "dot_ball_percentage": profile["dot_ball_percentage"],

        "dismissal_breakdown": profile["dismissal_breakdown"],

        "top_teams": profile["top_teams"],

        "dangerous": dangerous,

        "favourite": favourite,

        "venues": venues,

        "phases": phases,

        "summary": summary

    }
