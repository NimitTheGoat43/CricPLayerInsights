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
# RUNS BY SEASON
# ==========================

season_runs = (
    player_df
    .groupby("season")["runs"]
    .sum()
    .sort_index()
)

print("\nRUNS BY SEASON\n")
print(season_runs)

# ==========================
# BEST SEASON
# ==========================

best_season = season_runs.idxmax()
best_runs = season_runs.max()

print("\nBEST SEASON")
print(
    f"{best_season} -> {best_runs} Runs"
)

# ==========================
# WORST SEASON
# ==========================

worst_season = season_runs.idxmin()
worst_runs = season_runs.min()

print("\nWORST SEASON")
print(
    f"{worst_season} -> {worst_runs} Runs"
)

# ==========================
# MOST RUNS AGAINST TEAMS
# ==========================

team_runs = (
    player_df
    .groupby("team")["runs"]
    .sum()
    .sort_values(
        ascending=False
    )
)

print("\nMOST RUNS AGAINST TEAMS")
print(
    team_runs.head(10)
)

# ==========================
# POWERPLAY
# ==========================

powerplay = player_df[
    player_df["over"] <= 5
]

pp_runs = powerplay["runs"].sum()
pp_balls = len(powerplay)

pp_sr = round(
    (pp_runs / pp_balls) * 100,
    2
)

print("\nPOWERPLAY SR")
print(pp_sr)

# ==========================
# DEATH OVERS
# ==========================

death = player_df[
    player_df["over"] >= 16
]

death_runs = death["runs"].sum()
death_balls = len(death)

death_sr = round(
    (death_runs / death_balls) * 100,
    2
)

print("\nDEATH OVER SR")
print(death_sr)

# ==========================
# ANALYST REPORT
# ==========================

print("\nANALYST REPORT")

if death_sr > pp_sr:
    print(
        f"{player} is stronger in death overs."
    )
else:
    print(
        f"{player} is stronger in powerplay."
    )

print(
    f"Best season was {best_season}."
)