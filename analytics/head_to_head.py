import pandas as pd


def get_head_to_head(df, batter, bowler):
    """Get head-to-head stats between a specific batter and bowler."""

    matchup_df = df[
        (df["batter"] == batter) & (df["bowler"] == bowler)
    ]

    if len(matchup_df) == 0:
        return None

    runs = int(matchup_df["runs"].sum())
    balls = len(matchup_df)
    sr = round((runs / balls) * 100, 2) if balls > 0 else 0
    wickets = int(matchup_df["wicket"].sum())
    dismissals = int(
        matchup_df[
            matchup_df["player_dismissed"].fillna("") == batter
        ].shape[0]
    )

    winner = None
    if balls > 0:
        runs_per_out = runs / max(1, dismissals)
        if dismissals == 0:
            if sr >= 120 or runs >= 15:
                winner = batter
            else:
                winner = "Even Battle"
        else:
            if sr >= 135 and runs_per_out >= 25:
                winner = batter
            elif dismissals >= 2 and sr < 135:
                winner = bowler
            elif runs_per_out < 20 and sr < 125:
                winner = bowler
            else:
                winner = batter if sr >= 125 else bowler

    return {
        "batter": batter,
        "bowler": bowler,
        "runs": runs,
        "balls": balls,
        "sr": sr,
        "wickets": wickets,
        "dismissals": dismissals,
        "matchups": balls // 6 if balls > 0 else 0,
        "winner": winner,
    }


def get_batter_vs_team(df, player, team):
    """Get batter performance against a specific team."""

    matchup_df = df[
        (df["batter"] == player) & (df["bowling_team"] == team)
    ]

    if len(matchup_df) == 0:
        return None

    runs = int(matchup_df["runs"].sum())
    balls = len(matchup_df)
    sr = round((runs / balls) * 100, 2) if balls > 0 else 0
    matches = matchup_df["match_id"].nunique()
    outs = int(
        matchup_df[
            matchup_df["player_dismissed"].fillna("") == player
        ].shape[0]
    )

    return {
        "player": player,
        "team": team,
        "runs": runs,
        "balls": balls,
        "sr": sr,
        "matches": matches,
        "outs": outs,
    }


def get_bowler_vs_team(df, player, team):
    """Get bowler performance against a specific team."""

    matchup_df = df[
        (df["bowler"] == player) & (df["batting_team"] == team)
    ]

    if len(matchup_df) == 0:
        return None

    wickets = int(matchup_df["wicket"].sum())
    runs = int(matchup_df["total_runs"].sum())
    overs = round(len(matchup_df) / 6, 1)
    economy = round(runs / overs, 2) if overs > 0 else 0
    matches = matchup_df["match_id"].nunique()

    return {
        "player": player,
        "team": team,
        "wickets": wickets,
        "runs": runs,
        "overs": overs,
        "economy": economy,
        "matches": matches,
    }
