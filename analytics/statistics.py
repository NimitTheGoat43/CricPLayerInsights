import pandas as pd


def get_overall_statistics(df):
    """Get overall game statistics."""
    total_matches = df["match_id"].nunique()
    total_players = pd.concat([df["batter"], df["bowler"]]).nunique()
    total_teams = pd.concat([df["batting_team"], df["bowling_team"]]).nunique()
    total_runs = df["runs"].sum()
    total_wickets = df["wicket"].sum()
    total_balls = len(df)
    
    return {
        "total_matches": int(total_matches),
        "total_players": int(total_players),
        "total_teams": int(total_teams),
        "total_runs": int(total_runs),
        "total_wickets": int(total_wickets),
        "total_overs": round(total_balls / 6, 1),
        "avg_runs_per_match": round(total_runs / total_matches, 2),
        "avg_wickets_per_match": round(total_wickets / total_matches, 2),
    }


def get_highest_scoring_matches(df, limit=10):
    """Get matches with highest run totals."""
    match_stats = (
        df
        .groupby("match_id")
        .agg(
            runs=("runs", "sum"),
            batting_team=("batting_team", "first"),
            bowling_team=("bowling_team", "first"),
            venue=("venue", "first"),
            season=("season", "first"),
        )
        .reset_index()
    )
    
    match_stats = match_stats.sort_values("runs", ascending=False).head(limit)
    return match_stats[["match_id", "batting_team", "runs", "venue", "season"]]


def get_lowest_scoring_matches(df, limit=10):
    """Get matches with lowest run totals."""
    match_stats = (
        df
        .groupby("match_id")
        .agg(
            runs=("runs", "sum"),
            batting_team=("batting_team", "first"),
            bowling_team=("bowling_team", "first"),
            venue=("venue", "first"),
            season=("season", "first"),
        )
        .reset_index()
    )
    
    match_stats = match_stats.sort_values("runs", ascending=True).head(limit)
    return match_stats[["match_id", "batting_team", "runs", "venue", "season"]]


def get_highest_wicket_matches(df, limit=10):
    """Get matches with highest wickets lost."""
    match_stats = (
        df
        .groupby("match_id")
        .agg(
            wickets=("wicket", "sum"),
            batting_team=("batting_team", "first"),
            bowling_team=("bowling_team", "first"),
            venue=("venue", "first"),
            season=("season", "first"),
        )
        .reset_index()
    )
    
    match_stats = match_stats.sort_values("wickets", ascending=False).head(limit)
    return match_stats[["match_id", "batting_team", "wickets", "venue", "season"]]


def get_stats_by_season(df):
    """Get aggregated statistics for each season."""
    season_stats = (
        df
        .groupby("season")
        .agg(
            matches=("match_id", "nunique"),
            runs=("runs", "sum"),
            wickets=("wicket", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )
    
    season_stats["overs"] = (season_stats["balls"] / 6).round(1)
    season_stats["avg_runs_per_match"] = (season_stats["runs"] / season_stats["matches"]).round(2)
    season_stats = season_stats.sort_values("season")
    
    return season_stats[["season", "matches", "runs", "avg_runs_per_match", "wickets"]]


def get_stats_by_venue(df, limit=15):
    """Get statistics for each venue."""
    venue_stats = (
        df
        .groupby("venue")
        .agg(
            matches=("match_id", "nunique"),
            runs=("runs", "sum"),
            wickets=("wicket", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )
    
    venue_stats["avg_runs_per_match"] = (venue_stats["runs"] / venue_stats["matches"]).round(2)
    venue_stats["overs"] = (venue_stats["balls"] / 6).round(1)
    venue_stats = venue_stats.sort_values("avg_runs_per_match", ascending=False).head(limit)
    
    return venue_stats[["venue", "matches", "avg_runs_per_match", "runs", "wickets"]]
