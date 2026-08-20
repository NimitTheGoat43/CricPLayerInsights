import pandas as pd
import numpy as np


def get_player_clutch_index(df, player):
    """
    Calculates Clutch & Pressure Index for a player based on performance in high-pressure situations:
      - Death overs (Overs 16-20)
      - High required run rate situations
      - Close match finishes
    """
    if not player or df.empty:
        return None

    batting_df = df[df["batter"] == player].copy()
    bowling_df = df[df["bowler"] == player].copy()

    has_batting = not batting_df.empty and len(batting_df) >= 15
    has_bowling = not bowling_df.empty and len(bowling_df) >= 15

    if not has_batting and not has_bowling:
        return None

    clutch_batting = None
    phase_batting = {}
    if has_batting:
        overall_runs = batting_df["runs"].sum()
        overall_balls = len(batting_df)
        overall_sr = (overall_runs / max(1, overall_balls)) * 100

        # Phase breakdown for batters
        pp_df = batting_df[batting_df["over"] < 6]
        mid_df = batting_df[(batting_df["over"] >= 6) & (batting_df["over"] < 15)]
        death_df = batting_df[batting_df["over"] >= 15]

        pp_sr = (pp_df["runs"].sum() / max(1, len(pp_df))) * 100 if len(pp_df) > 0 else overall_sr
        mid_sr = (mid_df["runs"].sum() / max(1, len(mid_df))) * 100 if len(mid_df) > 0 else overall_sr
        death_runs = death_df["runs"].sum()
        death_balls = len(death_df)
        death_sr = (death_runs / max(1, death_balls)) * 100 if death_balls > 0 else overall_sr

        fours = (death_df["runs"] == 4).sum()
        sixes = (death_df["runs"] == 6).sum()
        boundary_pct = ((fours + sixes) / max(1, death_balls)) * 100 if death_balls > 0 else 0.0
        dot_pct = ((death_df["runs"] == 0).sum() / max(1, death_balls)) * 100 if death_balls > 0 else 0.0

        clutch_batting = {
            "overall_sr": round(overall_sr, 1),
            "death_sr": round(death_sr, 1),
            "death_runs": int(death_runs),
            "death_balls": int(death_balls),
            "boundary_pct": round(boundary_pct, 1),
            "dot_pct": round(dot_pct, 1),
            "sr_boost": round(death_sr - overall_sr, 1)
        }

        phase_batting = {
            "powerplay_sr": round(pp_sr, 1),
            "middle_sr": round(mid_sr, 1),
            "death_sr": round(death_sr, 1)
        }

    clutch_bowling = None
    phase_bowling = {}
    if has_bowling:
        overall_runs_conceded = bowling_df["total_runs"].sum()
        overall_balls_bowled = len(bowling_df)
        overall_econ = (overall_runs_conceded / (max(1, overall_balls_bowled) / 6.0)) if overall_balls_bowled > 0 else 8.5

        b_pp_df = bowling_df[bowling_df["over"] < 6]
        b_mid_df = bowling_df[(bowling_df["over"] >= 6) & (bowling_df["over"] < 15)]
        b_death_df = bowling_df[bowling_df["over"] >= 15]

        b_pp_econ = (b_pp_df["total_runs"].sum() / (max(1, len(b_pp_df)) / 6.0)) if len(b_pp_df) > 0 else overall_econ
        b_mid_econ = (b_mid_df["total_runs"].sum() / (max(1, len(b_mid_df)) / 6.0)) if len(b_mid_df) > 0 else overall_econ

        b_death_runs = b_death_df["total_runs"].sum()
        b_death_balls = len(b_death_df)
        b_death_wkts = b_death_df["wicket"].sum()
        b_death_econ = (b_death_runs / (max(1, b_death_balls) / 6.0)) if b_death_balls > 0 else overall_econ

        clutch_bowling = {
            "overall_econ": round(overall_econ, 2),
            "death_econ": round(b_death_econ, 2),
            "death_wickets": int(b_death_wkts),
            "death_balls": int(b_death_balls),
            "econ_diff": round(b_death_econ - overall_econ, 2)
        }

        phase_bowling = {
            "powerplay_econ": round(b_pp_econ, 2),
            "middle_econ": round(b_mid_econ, 2),
            "death_econ": round(b_death_econ, 2)
        }

    # Calculate 0-100 Clutch Rating
    clutch_score = 50
    if clutch_batting:
        # High death SR and low dot % boost score
        sr_diff = clutch_batting["death_sr"] - 130
        clutch_score += min(30, max(-20, int(sr_diff * 0.4)))
        if clutch_batting["boundary_pct"] >= 20:
            clutch_score += 10

    if clutch_bowling:
        # Low death economy & wickets boost score
        if clutch_bowling["death_econ"] <= 9.0:
            clutch_score += 15
        elif clutch_bowling["death_econ"] >= 11.5:
            clutch_score -= 10
        if clutch_bowling["death_wickets"] >= 15:
            clutch_score += 10

    clutch_score = min(99, max(25, clutch_score))

    if clutch_score >= 82:
        tier = "Elite Clutch Finisher"
    elif clutch_score >= 68:
        tier = "Pressure Specialist"
    elif clutch_score >= 52:
        tier = "Reliable Under Pressure"
    else:
        tier = "Developing Pressure Record"

    # Calculate 4 Key Pressure Attributes (0-100 scales)
    boundary_power = min(99, max(25, int(clutch_batting["boundary_pct"] * 3.2))) if clutch_batting else 50
    ice_rating = min(99, max(25, int((100 - clutch_batting["dot_pct"]) * 1.15))) if clutch_batting else 60
    acceleration = min(99, max(25, int(50 + (clutch_batting["sr_boost"] if clutch_batting else 0) * 0.8)))
    lethality = min(99, max(25, int(clutch_score)))

    attributes = {
        "boundary_power": boundary_power,
        "ice_rating": ice_rating,
        "acceleration": acceleration,
        "lethality": lethality
    }

    return {
        "player": player,
        "clutch_score": clutch_score,
        "tier": tier,
        "batting": clutch_batting,
        "bowling": clutch_bowling,
        "phase_batting": phase_batting,
        "phase_bowling": phase_bowling,
        "attributes": attributes
    }


def get_top_clutch_players(df, limit=10):
    """
    Computes top IPL clutch batters and bowlers based on death overs (16-20) performance.
    """
    death_bat = df[df["over"] >= 15].groupby("batter").filter(lambda g: len(g) >= 100)
    top_batters_list = []

    if not death_bat.empty:
        stats = death_bat.groupby("batter").agg(
            death_runs=("runs", "sum"),
            death_balls=("runs", "count"),
            sixes=("runs", lambda s: (s == 6).sum())
        ).reset_index()

        stats["death_sr"] = (stats["death_runs"] / stats["death_balls"]) * 100
        stats = stats.sort_values(by="death_sr", ascending=False).head(limit)

        for _, r in stats.iterrows():
            top_batters_list.append({
                "player": r["batter"],
                "death_runs": int(r["death_runs"]),
                "death_balls": int(r["death_balls"]),
                "sixes": int(r["sixes"]),
                "death_sr": round(r["death_sr"], 1)
            })

    death_bowl = df[df["over"] >= 15].groupby("bowler").filter(lambda g: len(g) >= 120)
    top_bowlers_list = []

    if not death_bowl.empty:
        b_stats = death_bowl.groupby("bowler").agg(
            death_runs=("total_runs", "sum"),
            death_balls=("total_runs", "count"),
            death_wkts=("wicket", "sum")
        ).reset_index()

        b_stats["death_econ"] = (b_stats["death_runs"] / (b_stats["death_balls"] / 6.0))
        b_stats = b_stats.sort_values(by="death_econ", ascending=True).head(limit)

        for _, r in b_stats.iterrows():
            top_bowlers_list.append({
                "player": r["bowler"],
                "death_wkts": int(r["death_wkts"]),
                "death_balls": int(r["death_balls"]),
                "death_econ": round(r["death_econ"], 2)
            })

    return {
        "batters": top_batters_list,
        "bowlers": top_bowlers_list
    }


def get_clutch_legends(df):
    """
    Returns curated IPL Clutch Legends data with icons, ratings, and stats.
    """
    legends_names = ["MS Dhoni", "AB de Villiers", "Jasprit Bumrah", "AD Russell", "KA Pollard"]
    result = []
    for name in legends_names:
        try:
            data = get_player_clutch_index(df, name)
            if data:
                result.append(data)
        except Exception:
            pass
    return result

