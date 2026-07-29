import pandas as pd

# ==========================
# LOAD DATA
# ==========================

df = pd.read_csv(
    "data/processed/ball_by_ball_clean.csv",
    low_memory=False
)

# ==========================
# PLAYER
# ==========================

player = "V Kohli"

player_df = df[
    df["batter"] == player
]

# ==========================
# POWERPLAY (0-5)
# ==========================

powerplay = player_df[
    player_df["over"] <= 5
]

pp_runs = powerplay["runs"].sum()
pp_balls = len(powerplay)

pp_sr = round(
    (pp_runs / pp_balls) * 100,
    2
) if pp_balls > 0 else 0

# ==========================
# MIDDLE OVERS (6-15)
# ==========================

middle = player_df[
    (player_df["over"] >= 6)
    &
    (player_df["over"] <= 15)
]

mid_runs = middle["runs"].sum()
mid_balls = len(middle)

mid_sr = round(
    (mid_runs / mid_balls) * 100,
    2
) if mid_balls > 0 else 0

# ==========================
# DEATH OVERS (16-19)
# ==========================

death = player_df[
    player_df["over"] >= 16
]

death_runs = death["runs"].sum()
death_balls = len(death)

death_sr = round(
    (death_runs / death_balls) * 100,
    2
) if death_balls > 0 else 0

# ==========================
# OUTPUT
# ==========================

print("\n==============================")
print("PHASE ANALYSIS")
print("==============================\n")

print("PLAYER :", player)

print("\nPOWERPLAY")
print("Runs :", pp_runs)
print("Balls :", pp_balls)
print("SR :", pp_sr)

print("\nMIDDLE OVERS")
print("Runs :", mid_runs)
print("Balls :", mid_balls)
print("SR :", mid_sr)

print("\nDEATH OVERS")
print("Runs :", death_runs)
print("Balls :", death_balls)
print("SR :", death_sr)

# ==========================
# AI REPORT
# ==========================

print("\n==============================")
print("AI REPORT")
print("==============================\n")

highest_sr = max(
    pp_sr,
    mid_sr,
    death_sr
)

if highest_sr == death_sr:
    print(
        f"{player} is most aggressive in death overs."
    )

elif highest_sr == mid_sr:
    print(
        f"{player} performs best during middle overs."
    )

else:
    print(
        f"{player} starts aggressively in the powerplay."
    )

print(
    f"Highest SR : {highest_sr}"
)