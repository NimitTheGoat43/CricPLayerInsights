import pandas as pd


def get_player_season_stats(df, player):
    """Get batter's performance across different seasons."""
    player_data = df[df["batter"] == player]
    
    if len(player_data) == 0:
        return None
    
    season_stats = (
        player_data
        .groupby("season")
        .agg(
            matches=("match_id", "nunique"),
            runs=("runs", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )
    
    season_stats["avg"] = (season_stats["runs"] / season_stats["matches"]).round(2)
    season_stats["sr"] = ((season_stats["runs"] / season_stats["balls"]) * 100).round(2)
    season_stats = season_stats.sort_values("season")
    
    return season_stats[["season", "matches", "runs", "avg", "sr"]]


def get_bowler_season_stats(df, player):
    """Get bowler's performance across different seasons."""
    player_data = df[df["bowler"] == player]
    
    if len(player_data) == 0:
        return None
    
    season_stats = (
        player_data
        .groupby("season")
        .agg(
            matches=("match_id", "nunique"),
            wickets=("wicket", "sum"),
            runs=("total_runs", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )
    
    season_stats["overs"] = (season_stats["balls"] / 6).round(1)
    season_stats["economy"] = (season_stats["runs"] / season_stats["overs"]).round(2)
    season_stats = season_stats.sort_values("season")
    
    return season_stats[["season", "matches", "wickets", "economy", "overs"]]


def get_season_trend(df, player, is_bowler=False):
    """Get trend data showing improvement/decline over seasons."""
    if is_bowler:
        player_data = df[df["bowler"] == player]
    else:
        player_data = df[df["batter"] == player]
    
    if len(player_data) == 0:
        return None
    
    if is_bowler:
        season_stats = (
            player_data
            .groupby("season")
            .agg(
                economy=("total_runs", "sum") / (player_data.groupby("season")["runs"].count() / 6),
                wickets=("wicket", "sum"),
            )
            .reset_index()
        )
    else:
        season_stats = (
            player_data
            .groupby("season")
            .agg(
                runs=("runs", "sum"),
                matches=("match_id", "nunique"),
            )
            .reset_index()
        )
        season_stats["avg"] = (season_stats["runs"] / season_stats["matches"]).round(2)
    
    return season_stats.sort_values("season")
