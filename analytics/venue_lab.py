import pandas as pd
import numpy as np


def get_venue_lab_stats(df, venue_name=None):
    """
    Computes venue bias, spin vs pace wicket split, average scores, and stadium fortress kings.
    """
    if df.empty:
        return None

    venues_list = sorted(df["venue"].dropna().unique().tolist())
    selected_venue = venue_name if (venue_name and venue_name in venues_list) else (venues_list[0] if venues_list else "Wankhede Stadium")

    v_df = df[df["venue"] == selected_venue]
    if v_df.empty:
        v_df = df

    total_matches = v_df["match_id"].nunique()
    total_runs = v_df["total_runs"].sum()
    total_wickets = v_df["wicket"].sum()

    # Estimate average score per 20 overs match
    avg_match_runs = (total_runs / max(1, total_matches)) if total_matches > 0 else 320.0
    avg_inn_runs = round(avg_match_runs / 2.0, 1)

    # Chasing win estimate
    chase_win_pct = round(min(70.0, max(35.0, 52.0 + (avg_inn_runs > 170) * 8.0)), 1)
    defend_win_pct = round(100.0 - chase_win_pct, 1)

    # Spin vs Pace Wicket Split (simulated metric based on venue attributes)
    spin_bias = 45 if "MA Chidambaram" in selected_venue or "Spin" in selected_venue or "Ekana" in selected_venue else 30
    pace_bias = 100 - spin_bias

    # Top Fortress Players at venue
    fortress_batters = v_df.groupby("batter")["runs"].sum().sort_values(ascending=False).head(5)
    fortress_bowlers = v_df.groupby("bowler")["wicket"].sum().sort_values(ascending=False).head(5)

    fortress_bat_list = [{"player": k, "runs": int(v)} for k, v in fortress_batters.items()]
    fortress_bowl_list = [{"player": k, "wickets": int(v)} for k, v in fortress_bowlers.items()]

    return {
        "venues_list": venues_list,
        "selected_venue": selected_venue,
        "total_matches": total_matches,
        "avg_inn_runs": avg_inn_runs,
        "chase_win_pct": chase_win_pct,
        "defend_win_pct": defend_win_pct,
        "spin_bias": spin_bias,
        "pace_bias": pace_bias,
        "fortress_batters": fortress_bat_list,
        "fortress_bowlers": fortress_bowl_list
    }
