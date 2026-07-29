import pandas as pd


def get_recent_form(df, player, limit=5):
    """Get recent form for a batter (last N matches)."""

    player_df = df[df["batter"] == player]

    if len(player_df) == 0:
        return None

    recent = (
        player_df
        .groupby("match_id")
        .agg(
            runs=("runs", "sum"),
            balls=("runs", "count"),
            venue=("venue", "first"),
            season=("season", "first"),
        )
        .reset_index()
    )

    recent["sr"] = round(
        (recent["runs"] / recent["balls"]) * 100, 2
    )

    recent = recent.sort_values(
        "match_id", ascending=False
    ).head(limit)

    result = recent[["match_id", "runs", "balls", "sr", "venue", "season"]]
    
    if len(result) == 0:
        return None
    
    return result


def get_consistency_score(df, player):
    """Calculate a consistency score (0-100) for a player."""

    player_df = df[df["batter"] == player]

    if len(player_df) < 10:
        return 0

    match_performance = (
        player_df
        .groupby("match_id")
        .agg(runs=("runs", "sum"))
        .reset_index()
    )

    mean_runs = match_performance["runs"].mean()
    std_runs = match_performance["runs"].std()

    # Coefficient of variation (lower = more consistent)
    cv = std_runs / mean_runs if mean_runs > 0 else 0

    # Convert to 0-100 score (lower CV = higher score)
    consistency_score = max(0, min(100, 100 - (cv * 50)))

    return round(consistency_score, 2)


def get_innings_breakdown(df, player):
    """Get breakdown of player's match performances (50s, 100s, etc)."""

    player_df = df[df["batter"] == player]

    if len(player_df) == 0:
        return None

    match_runs = (
        player_df
        .groupby("match_id")
        .agg(runs=("runs", "sum"))
        .reset_index()
    )

    centuries = len(match_runs[match_runs["runs"] >= 100])
    fifties = len(match_runs[(match_runs["runs"] >= 50) & (match_runs["runs"] < 100)])
    high_scores = len(match_runs[match_runs["runs"] >= 30])
    ducks = len(match_runs[match_runs["runs"] == 0])

    return {
        "centuries": centuries,
        "fifties": fifties,
        "high_scores": high_scores,
        "ducks": ducks,
    }


def get_bowler_recent_form(df, player, limit=5):
    """Get recent form for a bowler (last N matches)."""

    player_df = df[df["bowler"] == player]

    if len(player_df) == 0:
        return None

    recent = (
        player_df
        .groupby("match_id")
        .agg(
            wickets=("wicket", "sum"),
            runs=("total_runs", "sum"),
            balls=("runs", "count"),
            venue=("venue", "first"),
            season=("season", "first"),
        )
        .reset_index()
    )

    recent["overs"] = round(recent["balls"] / 6, 1)
    recent["economy"] = round(
        recent["runs"] / recent["overs"], 2
    )

    recent = recent.sort_values(
        "match_id", ascending=False
    ).head(limit)

    result = recent[["match_id", "wickets", "overs", "economy", "venue", "season"]]
    
    if len(result) == 0:
        return None
    
    return result


def get_bowler_consistency_score(df, player):
    """Calculate a consistency score (0-100) for a bowler based on economy rate."""

    player_df = df[df["bowler"] == player]

    if len(player_df) < 10:
        return 0

    match_performance = (
        player_df
        .groupby("match_id")
        .agg(
            runs=("total_runs", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )

    # Calculate economy for each match
    match_performance["overs"] = match_performance["balls"] / 6
    match_performance["economy"] = match_performance["runs"] / match_performance["overs"]

    # Consistency based on economy variation (lower variation = higher consistency)
    mean_economy = match_performance["economy"].mean()
    std_economy = match_performance["economy"].std()

    # Coefficient of variation
    cv = std_economy / mean_economy if mean_economy > 0 else 0

    # Convert to 0-100 score (lower variation = higher score)
    consistency_score = max(0, min(100, 100 - (cv * 50)))

    return round(consistency_score, 2)


def get_bowler_milestones(df, player):
    """Get breakdown of bowler's career milestones."""

    player_df = df[df["bowler"] == player]

    if len(player_df) == 0:
        return None

    # Total wickets
    total_wickets = player_df["wicket"].sum()

    # Best figures (max wickets in a match)
    match_wickets = (
        player_df
        .groupby("match_id")
        .agg(
            wickets=("wicket", "sum"),
            runs=("total_runs", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )

    best_wickets = match_wickets["wickets"].max() if len(match_wickets) > 0 else 0
    
    # 5-wicket hauls (matches with 5+ wickets)
    five_wicket_hauls = len(match_wickets[match_wickets["wickets"] >= 5])
    
    # 3-wicket hauls (matches with 3+ wickets)
    three_wicket_hauls = len(match_wickets[match_wickets["wickets"] >= 3])

    # Best economy (lowest economy in any match with at least 1 over)
    match_wickets["overs"] = match_wickets["balls"] / 6
    match_wickets["economy"] = match_wickets["runs"] / match_wickets["overs"]
    best_economy = match_wickets["economy"].min() if len(match_wickets) > 0 else 0

    return {
        "total_wickets": int(total_wickets),
        "best_wickets_in_match": int(best_wickets),
        "five_wicket_hauls": int(five_wicket_hauls),
        "three_wicket_hauls": int(three_wicket_hauls),
        "best_economy": round(best_economy, 2),
    }
