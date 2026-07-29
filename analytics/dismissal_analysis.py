import pandas as pd


def get_dismissal_breakdown(df, player=None):
    """Get dismissal breakdown by type."""
    if player:
        dismissals = df[
            (df["wicket"] == 1) & (df["player_dismissed"] == player)
        ].copy()
    else:
        dismissals = df[df["wicket"] == 1].copy()
    
    if len(dismissals) == 0:
        return None
    
    dismissal_types = (
        dismissals
        .groupby("dismissal_kind")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    
    return dismissal_types


def get_dismissal_by_bowler(df, player):
    """Get breakdown of how a batter was dismissed by different bowlers."""
    dismissals = df[
        (df["wicket"] == 1) & 
        (df["player_dismissed"] == player)
    ].copy()
    
    if len(dismissals) == 0:
        return None
    
    dismissal_breakdown = (
        dismissals
        .groupby(["bowler", "dismissal_kind"])
        .size()
        .reset_index(name="dismissals")
        .sort_values("dismissals", ascending=False)
    )
    
    return dismissal_breakdown


def get_bowler_dismissal_types(df, player):
    """Get types of dismissals a bowler typically achieves."""
    bowler_dismissals = df[
        (df["wicket"] == 1) & (df["bowler"] == player)
    ].copy()
    
    if len(bowler_dismissals) == 0:
        return None
    
    dismissal_types = (
        bowler_dismissals
        .groupby("dismissal_kind")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
    )
    
    return dismissal_types


def get_most_common_dismissals(df, limit=10):
    """Get most common dismissal types overall."""
    dismissals = df[df["wicket"] == 1].copy()
    
    if len(dismissals) == 0:
        return None
    
    common_dismissals = (
        dismissals
        .groupby("dismissal_kind")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(limit)
    )
    
    return common_dismissals


def get_wicket_takers_by_dismissal(df, dismissal_type, limit=10):
    """Get bowlers who most frequently achieve a specific dismissal type."""
    specific_dismissals = df[
        (df["wicket"] == 1) & 
        (df["dismissal_kind"] == dismissal_type)
    ].copy()
    
    if len(specific_dismissals) == 0:
        return None
    
    bowler_stats = (
        specific_dismissals
        .groupby("bowler")
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(limit)
    )
    
    return bowler_stats
