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
# BASIC STATS
# ==========================

runs = player_df["runs"].sum()

balls = len(player_df)

matches = player_df["match_id"].nunique()

strike_rate = round(
    (runs / balls) * 100,
    2
)

# ==========================
# BEST SEASON
# ==========================

season_stats = (
    player_df
    .groupby("season")["runs"]
    .sum()
)

best_season = season_stats.idxmax()
best_season_runs = season_stats.max()

worst_season = season_stats.idxmin()
worst_season_runs = season_stats.min()

# ==========================
# DANGEROUS BOWLER
# ==========================

dismissals = (

    df[
        df["player_dismissed"] == player
    ]

    .groupby("bowler")

    .size()

)

dangerous_bowler = dismissals.idxmax()
dangerous_bowler_outs = dismissals.max()

# ==========================
# FAVOURITE BOWLER
# ==========================

bowler_stats = (

    player_df

    .groupby("bowler")

    .agg(
        runs=("runs","sum"),
        balls=("runs","count")
    )

)

bowler_stats = bowler_stats[
    bowler_stats["balls"] >= 20
]

bowler_stats["sr"] = round(
    (
        bowler_stats["runs"]
        /
        bowler_stats["balls"]
    ) * 100,
    2
)

fav_bowler = (
    bowler_stats["sr"]
    .idxmax()
)

fav_bowler_sr = (
    bowler_stats["sr"]
    .max()
)

# ==========================
# BEST VENUE
# ==========================

venue_stats = (
    player_df
    .groupby("venue")["runs"]
    .sum()
)

best_venue = venue_stats.idxmax()
best_venue_runs = venue_stats.max()

# ==========================
# PHASE ANALYSIS
# ==========================

powerplay = player_df[
    player_df["over"] <= 5
]

middle = player_df[
    (player_df["over"] >= 6)
    &
    (player_df["over"] <= 15)
]

death = player_df[
    player_df["over"] >= 16
]

pp_sr = round(
    (
        powerplay["runs"].sum()
        /
        len(powerplay)
    ) * 100,
    2
)

mid_sr = round(
    (
        middle["runs"].sum()
        /
        len(middle)
    ) * 100,
    2
)

death_sr = round(
    (
        death["runs"].sum()
        /
        len(death)
    ) * 100,
    2
)

# ==========================
# REPORT
# ==========================

print("\n===================================")
print("PLAYER INTELLIGENCE REPORT")
print("===================================\n")

print("PLAYER :", player)

print("MATCHES :", matches)

print("RUNS :", runs)

print("BALLS :", balls)

print("CAREER SR :", strike_rate)

print("\nBEST SEASON")
print(best_season, "-", best_season_runs)

print("\nWORST SEASON")
print(worst_season, "-", worst_season_runs)

print("\nDANGEROUS BOWLER")
print(
    dangerous_bowler,
    "-",
    dangerous_bowler_outs,
    "dismissals"
)

print("\nFAVOURITE BOWLER")
print(
    fav_bowler,
    "- SR",
    fav_bowler_sr
)

print("\nBEST VENUE")
print(
    best_venue,
    "-",
    best_venue_runs,
    "runs"
)

print("\nPHASE ANALYSIS")

print(
    "Powerplay SR:",
    pp_sr
)

print(
    "Middle Overs SR:",
    mid_sr
)

print(
    "Death Overs SR:",
    death_sr
)

print("\n===================================")
print("AI SUMMARY")
print("===================================\n")

print(
    f"{player} has scored {runs} IPL runs."
)

print(
    f"His best season was {best_season}."
)

print(
    f"{dangerous_bowler} has dismissed him "
    f"the most."
)

print(
    f"He scores most freely against "
    f"{fav_bowler}."
)

print(
    f"{best_venue} has been his strongest venue."
)

if death_sr > pp_sr and death_sr > mid_sr:
    print(
        f"He is most aggressive during death overs."
    )

elif mid_sr > pp_sr:
    print(
        f"He performs best in middle overs."
    )

else:
    print(
        f"He starts aggressively in powerplay."
    )