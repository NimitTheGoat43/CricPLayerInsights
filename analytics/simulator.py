import pandas as pd
import numpy as np


def simulate_match_impact(df, player, target_runs=40, overs_remaining=4.0, req_rr=10.0, pitch_condition="Balanced Pitch", dew_factor="No Dew"):
    """
    Simulates match outcome probabilities & player contribution impact under custom pressure scenarios.
    """
    if not player or df.empty:
        return None

    batting_df = df[df["batter"] == player].copy()
    bowling_df = df[df["bowler"] == player].copy()

    has_batting = not batting_df.empty and len(batting_df) >= 15
    has_bowling = not bowling_df.empty and len(bowling_df) >= 15

    if not has_batting and not has_bowling:
        return None

    # Pitch & Dew Multipliers
    pitch_mult = 1.0
    if pitch_condition == "Batting Friendly":
        pitch_mult = 1.15
    elif pitch_condition == "Spin Friendly / Slow":
        pitch_mult = 0.85
    elif pitch_condition == "Pace & Bounce":
        pitch_mult = 0.95

    dew_mult = 1.0
    if dew_factor == "Heavy Dew (Chasing Advantage)":
        dew_mult = 1.12
    elif dew_factor == "Mild Dew":
        dew_mult = 1.05

    total_balls_needed = int(overs_remaining * 6)
    target_sr = (target_runs / max(1, total_balls_needed)) * 100

    # Batting simulation
    batting_sim = None
    if has_batting:
        death_df = batting_df[batting_df["over"] >= 15]
        use_df = death_df if (overs_remaining <= 6 and not death_df.empty) else batting_df

        runs_sum = use_df["runs"].sum()
        balls_count = len(use_df)
        historical_sr = (runs_sum / max(1, balls_count)) * 100
        effective_sr = historical_sr * pitch_mult * dew_mult

        # Probability of player scoring required runs
        proj_balls_faced = min(total_balls_needed, int(round(total_balls_needed * 0.7)))
        proj_runs = int(round((proj_balls_faced * effective_sr / 100.0)))
        
        match_contribution_pct = min(98, max(15, int(round((proj_runs / max(1, target_runs)) * 100))))
        win_probability = min(96, max(10, int(round(50 + (effective_sr - target_sr) * 0.45 + (proj_runs - target_runs * 0.5) * 0.8))))

        dot_pct = round(((use_df["runs"] == 0).sum() / max(1, balls_count)) * 100, 1)
        boundary_pct = round(((use_df["runs"] >= 4).sum() / max(1, balls_count)) * 100, 1)

        batting_sim = {
            "historical_sr": round(historical_sr, 1),
            "effective_sr": round(effective_sr, 1),
            "target_sr": round(target_sr, 1),
            "proj_runs": proj_runs,
            "proj_balls": proj_balls_faced,
            "match_contribution_pct": match_contribution_pct,
            "win_probability": win_probability,
            "dot_pct": dot_pct,
            "boundary_pct": boundary_pct
        }

    # Bowling simulation
    bowling_sim = None
    if has_bowling:
        b_death_df = bowling_df[bowling_df["over"] >= 15]
        b_use_df = b_death_df if (overs_remaining <= 6 and not b_death_df.empty) else bowling_df

        b_runs = b_use_df["total_runs"].sum()
        b_balls = len(b_use_df)
        b_econ = (b_runs / (max(1, b_balls) / 6.0)) if b_balls > 0 else 8.5
        b_wkts = b_use_df["wicket"].sum()
        b_sr = (b_balls / max(1, b_wkts)) if b_wkts > 0 else 18.0

        effective_econ = round(b_econ * (1.1 - 0.1 * pitch_mult) * (1.0 + 0.08 if dew_factor.startswith("Heavy") else 1.0), 2)
        proj_overs = min(overs_remaining, 2.0 if overs_remaining <= 4 else 4.0)
        proj_conceded = int(round(effective_econ * proj_overs))
        proj_wkts = round((proj_overs * 6) / max(1, b_sr), 1)

        containment_score = min(98, max(15, int(round((req_rr / max(1.0, effective_econ)) * 50))))

        bowling_sim = {
            "historical_econ": round(b_econ, 2),
            "effective_econ": effective_econ,
            "proj_overs": proj_overs,
            "proj_conceded": proj_conceded,
            "proj_wkts": proj_wkts,
            "containment_score": containment_score
        }

    # Simulation Narrative
    scenario_desc = f"Chasing {target_runs} runs off {overs_remaining} overs (Req RRR: {req_rr:.1f}) under {pitch_condition} conditions."
    
    if batting_sim and batting_sim["win_probability"] >= 65:
        summary_insight = f"{player} has a high simulation win impact ({batting_sim['win_probability']}%) due to strong historical strike rate ({batting_sim['effective_sr']}) matching target RRR."
    elif bowling_sim and bowling_sim["containment_score"] >= 60:
        summary_insight = f"{player} offers strong containment power ({bowling_sim['effective_econ']} RPO projected) to throttle opposition run chase."
    else:
        summary_insight = f"Balanced high-pressure scenario. Player contribution will depend heavily on early boundary execution."

    return {
        "player": player,
        "scenario": scenario_desc,
        "target_runs": target_runs,
        "overs_remaining": overs_remaining,
        "req_rr": req_rr,
        "pitch_condition": pitch_condition,
        "dew_factor": dew_factor,
        "batting_sim": batting_sim,
        "bowling_sim": bowling_sim,
        "summary_insight": summary_insight
    }
