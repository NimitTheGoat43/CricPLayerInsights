import pandas as pd

def get_opponent_intelligence(df, player):
    """Analyze player performance against specific opposition teams."""
    # -----------------------------
    # Batting stats by opposing team
    # -----------------------------
    batting_df = df[df["batter"] == player]
    batting_stats = None
    if not batting_df.empty:
        batting_stats = (
            batting_df
            .groupby("bowling_team")
            .agg(
                matches=("match_id", "nunique"),
                runs=("runs", "sum"),
                balls=("runs", "count"),
                outs=("player_dismissed", lambda x: x.fillna("").eq(player).sum())
            )
            .reset_index()
            .rename(columns={"bowling_team": "opponent"})
        )
        batting_stats["average"] = batting_stats.apply(
            lambda r: round(r["runs"] / r["outs"], 2) if r["outs"] > 0 else r["runs"],
            axis=1
        )
        batting_stats["strike_rate"] = round(
            (batting_stats["runs"] / batting_stats["balls"]) * 100,
            2
        )
        batting_stats = batting_stats.sort_values("runs", ascending=False).reset_index(drop=True)

    # -----------------------------
    # Bowling stats by opposing team
    # -----------------------------
    bowling_df = df[df["bowler"] == player]
    bowling_stats = None
    if not bowling_df.empty:
        bowling_stats = (
            bowling_df
            .groupby("batting_team")
            .agg(
                matches=("match_id", "nunique"),
                wickets=("wicket", "sum"),
                runs_conceded=("total_runs", "sum"),
                balls=("runs", "count")
            )
            .reset_index()
            .rename(columns={"batting_team": "opponent"})
        )
        bowling_stats["overs"] = round(bowling_stats["balls"] / 6, 1)
        bowling_stats["economy"] = round(
            bowling_stats["runs_conceded"] / (bowling_stats["balls"] / 6),
            2
        )
        bowling_stats["bowling_sr"] = bowling_stats.apply(
            lambda r: round(r["balls"] / r["wickets"], 2) if r["wickets"] > 0 else 0,
            axis=1
        )
        bowling_stats = bowling_stats.sort_values("wickets", ascending=False).reset_index(drop=True)

    return {
        "player": player,
        "batting": batting_stats,
        "bowling": bowling_stats
    }
