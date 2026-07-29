import pandas as pd


def get_top_batters(df, limit=10):
    """Get top batters by runs."""
    batter_stats = (
        df
        .groupby("batter")
        .agg(
            runs=("runs", "sum"),
            matches=("match_id", "nunique"),
            balls=("runs", "count"),
        )
        .reset_index()
    )
    
    batter_stats["avg"] = (batter_stats["runs"] / batter_stats["matches"]).round(2)
    batter_stats["sr"] = ((batter_stats["runs"] / batter_stats["balls"]) * 100).round(2)
    batter_stats = batter_stats.sort_values("runs", ascending=False).head(limit)
    
    return batter_stats[["batter", "runs", "matches", "avg", "sr"]]


def get_top_bowlers(df, limit=10):
    """Get top bowlers by wickets."""
    bowler_stats = (
        df
        .groupby("bowler")
        .agg(
            wickets=("wicket", "sum"),
            matches=("match_id", "nunique"),
            runs=("total_runs", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )
    
    bowler_stats["overs"] = (bowler_stats["balls"] / 6).round(1)
    bowler_stats["economy"] = (bowler_stats["runs"] / bowler_stats["overs"]).round(2)
    bowler_stats = bowler_stats.sort_values("wickets", ascending=False).head(limit)
    
    return bowler_stats[["bowler", "wickets", "matches", "economy", "overs"]]


def get_highest_strike_rates(df, min_balls=100, limit=10):
    """Get players with highest strike rates."""
    batter_stats = (
        df
        .groupby("batter")
        .agg(
            runs=("runs", "sum"),
            balls=("runs", "count"),
            matches=("match_id", "nunique"),
        )
        .reset_index()
    )
    
    batter_stats = batter_stats[batter_stats["balls"] >= min_balls]
    batter_stats["sr"] = ((batter_stats["runs"] / batter_stats["balls"]) * 100).round(2)
    batter_stats = batter_stats.sort_values("sr", ascending=False).head(limit)
    
    return batter_stats[["batter", "sr", "runs", "balls", "matches"]]


def get_best_economies(df, min_overs=30, limit=10):
    """Get bowlers with best (lowest) economies."""
    bowler_stats = (
        df
        .groupby("bowler")
        .agg(
            wickets=("wicket", "sum"),
            runs=("total_runs", "sum"),
            balls=("runs", "count"),
            matches=("match_id", "nunique"),
        )
        .reset_index()
    )
    
    bowler_stats["overs"] = bowler_stats["balls"] / 6
    bowler_stats = bowler_stats[bowler_stats["overs"] >= min_overs]
    bowler_stats["economy"] = (bowler_stats["runs"] / bowler_stats["overs"]).round(2)
    bowler_stats = bowler_stats.sort_values("economy", ascending=True).head(limit)
    
    return bowler_stats[["bowler", "economy", "wickets", "runs", "overs"]]


def get_most_dismissals(df, limit=10):
    """Get bowlers with most dismissals."""
    dismissal_stats = (
        df[df["wicket"] == 1]
        .groupby("bowler")
        .agg(
            dismissals=("wicket", "sum"),
            matches=("match_id", "nunique"),
        )
        .reset_index()
    )
    
    dismissal_stats = dismissal_stats.sort_values("dismissals", ascending=False).head(limit)
    return dismissal_stats[["bowler", "dismissals", "matches"]]
