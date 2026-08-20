import pandas as pd
import numpy as np


def get_player_kryptonite(df, player):
    """
    Analyzes a player's biggest vulnerabilities, nemesis bowlers/batters, weakest overs phase,
    and generates an anti-strategy blueprint.
    """
    if not player or df.empty:
        return None

    bat_df = df[df["batter"] == player].copy()
    bowl_df = df[df["bowler"] == player].copy()

    is_batter = not bat_df.empty and len(bat_df) >= 20
    is_bowler = not bowl_df.empty and len(bowl_df) >= 20

    if not is_batter and not is_bowler:
        return None

    nemesis_name = "N/A"
    nemesis_stat = "N/A"
    weakest_phase = "N/A"
    vulnerability_score = 65

    tactical_tips = []

    if is_batter:
        # Find bowler who dismissed batter the most
        dismissals_df = bat_df[bat_df["wicket"] == 1]
        if not dismissals_df.empty and "bowler" in dismissals_df.columns:
            top_dismissers = dismissals_df["bowler"].value_counts()
            if not top_dismissers.empty:
                nemesis_name = top_dismissers.index[0]
                times = top_dismissers.iloc[0]
                nemesis_stat = f"Dismissed {times} times"

        # Phase breakdown
        pp_sr = (bat_df[bat_df["over"] < 6]["runs"].sum() / max(1, len(bat_df[bat_df["over"] < 6]))) * 100
        mid_sr = (bat_df[(bat_df["over"] >= 6) & (bat_df["over"] < 15)]["runs"].sum() / max(1, len(bat_df[(bat_df["over"] >= 6) & (bat_df["over"] < 15)]))) * 100
        death_sr = (bat_df[bat_df["over"] >= 15]["runs"].sum() / max(1, len(bat_df[bat_df["over"] >= 15]))) * 100

        phase_srs = {"Powerplay (Overs 1-6)": pp_sr, "Middle Overs (7-14)": mid_sr, "Death Overs (15-20)": death_sr}
        weakest_phase = min(phase_srs, key=phase_srs.get)
        min_sr = round(phase_srs[weakest_phase], 1)

        dot_pct = (bat_df["runs"] == 0).sum() / max(1, len(bat_df)) * 100
        vulnerability_score = min(99, max(25, int(dot_pct * 1.6 + (200 - min_sr) * 0.2)))

        tactical_tips = [
            f"Target early in the innings during {weakest_phase} (lowest Strike Rate: {min_sr}).",
            f"Deploy {nemesis_name} as the tactical matchup bowler.",
            "Use wide yorkers outside off stump or hard-length bouncers to force high-risk aerial shots.",
            "Set a tight inner ring in the first 10 balls to build dot-ball pressure."
        ]

    elif is_bowler:
        # Find batter who scored most runs off this bowler
        top_scorers = bowl_df.groupby("batter")["total_runs"].sum().sort_values(ascending=False)
        if not top_scorers.empty:
            nemesis_name = top_scorers.index[0]
            runs_conceded = top_scorers.iloc[0]
            nemesis_stat = f"Conceded {runs_conceded} runs to {nemesis_name}"

        pp_econ = (bowl_df[bowl_df["over"] < 6]["total_runs"].sum() / (max(1, len(bowl_df[bowl_df["over"] < 6])) / 6.0))
        mid_econ = (bowl_df[(bowl_df["over"] >= 6) & (bowl_df["over"] < 15)]["total_runs"].sum() / (max(1, len(bowl_df[(bowl_df["over"] >= 6) & (bowl_df["over"] < 15)])) / 6.0))
        death_econ = (bowl_df[bowl_df["over"] >= 15]["total_runs"].sum() / (max(1, len(bowl_df[bowl_df["over"] >= 15])) / 6.0))

        phase_econs = {"Powerplay (Overs 1-6)": pp_econ, "Middle Overs (7-14)": mid_econ, "Death Overs (15-20)": death_econ}
        weakest_phase = max(phase_econs, key=phase_econs.get)
        max_econ = round(phase_econs[weakest_phase], 2)

        vulnerability_score = min(99, max(25, int(max_econ * 7.5)))

        tactical_tips = [
            f"Attack during {weakest_phase} where economy leaks at {max_econ} rpo.",
            f"Send {nemesis_name} out to exploit bowler's rhythm.",
            "Capitalize on full slot deliveries and force bowler away from good-length areas.",
            "Target boundaries straight over bowler's head in death overs."
        ]

    return {
        "player": player,
        "nemesis_name": nemesis_name,
        "nemesis_stat": nemesis_stat,
        "weakest_phase": weakest_phase,
        "vulnerability_score": vulnerability_score,
        "tactical_tips": tactical_tips
    }
