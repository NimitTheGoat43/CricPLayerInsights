import pandas as pd


def get_team_stats(df):
    """Get overall stats for each team as batting team."""
    team_batting = (
        df
        .groupby("batting_team")
        .agg(
            matches=("match_id", "nunique"),
            runs=("runs", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )
    
    team_batting["avg_runs_per_match"] = (team_batting["runs"] / team_batting["matches"]).round(2)
    team_batting["sr"] = ((team_batting["runs"] / team_batting["balls"]) * 100).round(2)
    team_batting = team_batting.sort_values("avg_runs_per_match", ascending=False)
    
    return team_batting[["batting_team", "matches", "avg_runs_per_match", "sr"]]


def get_team_bowling_stats(df):
    """Get overall stats for each team as bowling team."""
    team_bowling = (
        df
        .groupby("bowling_team")
        .agg(
            matches=("match_id", "nunique"),
            wickets=("wicket", "sum"),
            runs_conceded=("total_runs", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )
    
    team_bowling["overs"] = (team_bowling["balls"] / 6).round(1)
    team_bowling["economy"] = (team_bowling["runs_conceded"] / team_bowling["overs"]).round(2)
    team_bowling = team_bowling.sort_values("economy", ascending=True)
    
    return team_bowling[["bowling_team", "matches", "wickets", "economy", "overs"]]


def get_team_performance_by_season(df, team):
    """Get performance of a team across different seasons."""
    team_data = df[df["batting_team"] == team]
    
    if len(team_data) == 0:
        return None
    
    season_performance = (
        team_data
        .groupby("season")
        .agg(
            matches=("match_id", "nunique"),
            runs=("runs", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )
    
    season_performance["avg_runs"] = (season_performance["runs"] / season_performance["matches"]).round(2)
    season_performance["sr"] = ((season_performance["runs"] / season_performance["balls"]) * 100).round(2)
    season_performance = season_performance.sort_values("season")
    
    return season_performance[["season", "matches", "avg_runs", "sr"]]
