import random
import pandas as pd
import numpy as np


def simulate_super_over(df, batter_name, bowler_name):
    """
    Simulates a 6-ball Super Over between a batter and bowler based on death over stats.
    Returns ball-by-ball commentary, runs, wickets, and outcome summary.
    """
    if not batter_name or not bowler_name or df.empty:
        return None

    bat_df = df[(df["batter"] == batter_name) & (df["over"] >= 15)]
    bowl_df = df[(df["bowler"] == bowler_name) & (df["over"] >= 15)]

    # Fallback to overall stats if death over sample is small
    if bat_df.empty:
        bat_df = df[df["batter"] == batter_name]
    if bowl_df.empty:
        bowl_df = df[df["bowler"] == bowler_name]

    if bat_df.empty or bowl_df.empty:
        return None

    # Calculate probabilities
    bat_runs = bat_df["runs"].tolist()
    bowl_runs = bowl_df["total_runs"].tolist()
    bowl_wkts = bowl_df["wicket"].tolist()

    bat_sr = (bat_df["runs"].sum() / max(1, len(bat_df))) * 100
    bowl_econ = (bowl_df["total_runs"].sum() / (max(1, len(bowl_df)) / 6.0))
    wkt_rate = (bowl_df["wicket"].sum() / max(1, len(bowl_df)))

    # Determine probability weights for outcomes: [0, 1, 2, 4, 6, 'W']
    # Higher strike rate -> higher 4 & 6 weights; Higher wicket rate -> higher W weight
    prob_6 = min(0.35, max(0.08, (bat_sr - 100) / 400.0))
    prob_4 = min(0.30, max(0.12, (bat_sr - 80) / 500.0))
    prob_w = min(0.25, max(0.05, wkt_rate * 2.5 + (bowl_econ < 8.0) * 0.05))
    prob_0 = min(0.35, max(0.10, (bowl_econ / 20.0)))
    prob_1_2 = max(0.10, 1.0 - (prob_6 + prob_4 + prob_w + prob_0))

    outcomes = [6, 4, 0, 1, 2, "W"]
    weights = [prob_6, prob_4, prob_0, prob_1_2 * 0.6, prob_1_2 * 0.4, prob_w]
    weights = [w / sum(weights) for w in weights]  # Normalize

    balls_log = []
    total_runs = 0
    wickets = 0

    commentary_templates = {
        6: [
            "MONSTROUS SIX! Sent straight out of the stadium!",
            "CLEARED THE BOUNDARY! Huge hit into the top tier!",
            "BOOM! Launched over long-on for a massive 6!"
        ],
        4: [
            "CRACKING SHOT! Pierces the gap for 4 runs!",
            "SMACKED! Driven forcefully through extra cover!",
            "Edged and fine! Races away to the third-man fence for FOUR!"
        ],
        2: [
            "Driven into the deep, crisp running for 2 runs.",
            "Pushed softly into the gap, quick two taken."
        ],
        1: [
            "Tapped towards mid-off, quick single taken.",
            "Tucked off the pads for a single."
        ],
        0: [
            "DOT BALL! Brilliant Yorker outside off, completely beaten!",
            "Slower ball tricks the batter! No run.",
            "Fired into the blockhole, solid defense."
        ],
        "W": [
            "OUT! CLEAN BOWLED! Perfect lethal yorker smashes the stumps!",
            "OUT! TAKEN IN THE DEEP! High in the air and caught at long-off!",
            "OUT! LBW! Trapped right in front of middle stump!"
        ]
    }

    # Simulate 6 balls (Super Over stops if 2 wickets fall)
    for ball_num in range(1, 7):
        if wickets >= 2:
            break

        raw_res = np.random.choice(outcomes, p=weights)
        res_str = str(raw_res)

        if res_str == "W":
            wickets += 1
            comment = random.choice(commentary_templates["W"])
            balls_log.append({
                "ball": ball_num,
                "event": "W",
                "runs": 0,
                "is_wicket": True,
                "commentary": comment
            })
        else:
            runs_hit = int(res_str)
            total_runs += runs_hit
            comment = random.choice(commentary_templates[runs_hit])
            balls_log.append({
                "ball": ball_num,
                "event": f"{runs_hit}" if runs_hit > 0 else "0",
                "runs": runs_hit,
                "is_wicket": False,
                "commentary": comment
            })

    # Verdict
    if total_runs >= 16:
        verdict = "Dominant Super Over Win for Batter!"
        rating = "🔥 UNSTOPPABLE BATTING DEMOLITION"
    elif total_runs >= 10:
        verdict = "Competitive Super Over Finish!"
        rating = "⚡ HIGH VOLTAGE SHOWDOWN"
    else:
        verdict = "Masterclass Death Bowling Win for Bowler!"
        rating = "🎯 CLUTCH BOWLING LOCKDOWN"

    return {
        "batter": batter_name,
        "bowler": bowler_name,
        "total_runs": total_runs,
        "wickets": wickets,
        "balls": balls_log,
        "verdict": verdict,
        "rating": rating,
        "bat_sr": round(bat_sr, 1),
        "bowl_econ": round(bowl_econ, 2)
    }
