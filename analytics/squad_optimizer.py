import pandas as pd
import numpy as np


def evaluate_squad(df, selected_players):
    """
    Evaluates a custom 11-player squad balance, death-overs rating, batting depth,
    bowling variety, and recommended Captain / Vice-Captain picks.
    """
    if not selected_players or len(selected_players) == 0 or df.empty:
        return None

    squad_data = []
    total_runs = 0
    total_wickets = 0
    death_sr_sum = 0
    death_econ_sum = 0
    bat_count = 0
    bowl_count = 0

    for p in selected_players:
        bat_df = df[df["batter"] == p]
        bowl_df = df[df["bowler"] == p]

        p_runs = int(bat_df["runs"].sum()) if not bat_df.empty else 0
        p_wkts = int(bowl_df["wicket"].sum()) if not bowl_df.empty else 0

        d_bat = bat_df[bat_df["over"] >= 15]
        d_sr = (d_bat["runs"].sum() / max(1, len(d_bat))) * 100 if len(d_bat) > 0 else 120.0

        d_bowl = bowl_df[bowl_df["over"] >= 15]
        d_econ = (d_bowl["total_runs"].sum() / (max(1, len(d_bowl)) / 6.0)) if len(d_bowl) > 0 else 9.5

        if p_runs >= 100:
            bat_count += 1
            death_sr_sum += d_sr
        if p_wkts >= 10:
            bowl_count += 1
            death_econ_sum += d_econ

        squad_data.append({
            "player": p,
            "runs": p_runs,
            "wickets": p_wkts,
            "death_sr": round(d_sr, 1),
            "death_econ": round(d_econ, 2)
        })

    # Squad Balance Ratings (0-100)
    batting_depth = min(99, max(30, int(bat_count * 12 + len(selected_players) * 2)))
    bowling_variety = min(99, max(30, int(bowl_count * 18 + 10)))
    death_power = min(99, max(30, int((death_sr_sum / max(1, bat_count)) * 0.45 + (12 - death_econ_sum / max(1, bowl_count)) * 3.5)))

    overall_balance_score = min(99, max(35, int((batting_depth + bowling_variety + death_power) / 3.0)))

    # Sort players for C and VC recommendations
    squad_data_sorted = sorted(squad_data, key=lambda x: (x["runs"] + x["wickets"] * 25), reverse=True)
    captain = squad_data_sorted[0]["player"] if len(squad_data_sorted) > 0 else selected_players[0]
    vice_captain = squad_data_sorted[1]["player"] if len(squad_data_sorted) > 1 else captain

    return {
        "squad_size": len(selected_players),
        "selected_players": squad_data,
        "overall_balance_score": overall_balance_score,
        "batting_depth": batting_depth,
        "bowling_variety": bowling_variety,
        "death_power": death_power,
        "captain": captain,
        "vice_captain": vice_captain
    }
