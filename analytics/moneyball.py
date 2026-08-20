import pandas as pd
import numpy as np


def get_moneyball_analytics(df):
    """
    Computes Moneyball Value Ratings & Bargain Buys Leaderboard based on performance impact.
    """
    if df.empty:
        return None

    # Batting Value Score (Impact per ball faced)
    bat_stats = df.groupby("batter").agg(
        runs=("runs", "sum"),
        balls=("runs", "count"),
        sixes=("runs", lambda s: (s == 6).sum())
    ).reset_index()
    bat_stats = bat_stats[bat_stats["balls"] >= 150]
    bat_stats["sr"] = (bat_stats["runs"] / bat_stats["balls"]) * 100
    bat_stats["impact_score"] = (bat_stats["runs"] * 0.5) + (bat_stats["sr"] * 1.5) + (bat_stats["sixes"] * 3.0)
    top_bargain_batters = bat_stats.sort_values(by="impact_score", ascending=False).head(8)

    # Bowling Value Score
    bowl_stats = df.groupby("bowler").agg(
        total_runs=("total_runs", "sum"),
        balls=("total_runs", "count"),
        wickets=("wicket", "sum")
    ).reset_index()
    bowl_stats = bowl_stats[bowl_stats["balls"] >= 300]
    bowl_stats["econ"] = (bowl_stats["total_runs"] / (bowl_stats["balls"] / 6.0))
    bowl_stats["impact_score"] = (bowl_stats["wickets"] * 25) + ((10 - bowl_stats["econ"]).clip(lower=0) * 30)
    top_bargain_bowlers = bowl_stats.sort_values(by="impact_score", ascending=False).head(8)

    bargain_batters_list = []
    for _, r in top_bargain_batters.iterrows():
        bargain_batters_list.append({
            "player": r["batter"],
            "runs": int(r["runs"]),
            "sr": round(r["sr"], 1),
            "sixes": int(r["sixes"]),
            "value_score": round(r["impact_score"], 1)
        })

    bargain_bowlers_list = []
    for _, r in top_bargain_bowlers.iterrows():
        bargain_bowlers_list.append({
            "player": r["bowler"],
            "wickets": int(r["wickets"]),
            "econ": round(r["econ"], 2),
            "value_score": round(r["impact_score"], 1)
        })

    return {
        "bargain_batters": bargain_batters_list,
        "bargain_bowlers": bargain_bowlers_list
    }


def evaluate_player_roi(df, player, price_crores=5.0):
    """
    Evaluates player ROI based on auction price in Crores and delivered performance impact.
    """
    if not player or df.empty:
        return None

    bat_df = df[df["batter"] == player]
    bowl_df = df[df["bowler"] == player]

    runs = int(bat_df["runs"].sum()) if not bat_df.empty else 0
    balls_faced = len(bat_df)
    sr = (runs / max(1, balls_faced)) * 100 if balls_faced > 0 else 0.0

    wkts = int(bowl_df["wicket"].sum()) if not bowl_df.empty else 0
    balls_bowled = len(bowl_df)
    econ = (bowl_df["total_runs"].sum() / (max(1, balls_bowled) / 6.0)) if balls_bowled > 0 else 9.0

    # Calculate Value Produced Points
    impact_points = (runs * 1.0) + (sr * 2.0) + (wkts * 30.0) + (max(0, 10.0 - econ) * 20.0)
    cost_per_point = round((price_crores * 100) / max(1, impact_points), 2)
    roi_score = min(99, max(15, int((impact_points / max(0.5, price_crores)) * 0.25)))

    if roi_score >= 80:
        verdict = "💎 MEGA BARGAIN BUY"
        recommendation = "Exceptional return on investment! High performance per Cr spent."
    elif roi_score >= 50:
        verdict = "✅ SOLID FAIR PRICE"
        recommendation = "Balanced contract value. Delivers steady output proportional to salary."
    else:
        verdict = "⚠️ HIGH COST / OVERPRICED"
        recommendation = "High price tag relative to delivered stats. Requires higher impact to justify contract."

    return {
        "player": player,
        "price_crores": price_crores,
        "runs": runs,
        "wickets": wkts,
        "sr": round(sr, 1),
        "econ": round(econ, 2),
        "impact_points": round(impact_points, 1),
        "cost_per_point": cost_per_point,
        "roi_score": roi_score,
        "verdict": verdict,
        "recommendation": recommendation
    }
