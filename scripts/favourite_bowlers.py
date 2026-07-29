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
# BOWLER STATS
# ==========================

bowler_stats = (

    player_df

    .groupby("bowler")

    .agg(
        runs=("runs", "sum"),
        balls=("runs", "count")
    )

)

bowler_stats = bowler_stats.reset_index()

# ==========================
# STRIKE RATE
# ==========================

bowler_stats["strike_rate"] = round(
    (
        bowler_stats["runs"]
        /
        bowler_stats["balls"]
    ) * 100,
    2
)

# ==========================
# MINIMUM SAMPLE SIZE
# ==========================

bowler_stats = bowler_stats[
    bowler_stats["balls"] >= 20
]

# ==========================
# FAVOURITE SCORE
# ==========================

bowler_stats["favourite_score"] = round(

    (
        bowler_stats["strike_rate"]
    )

    +

    (
        bowler_stats["runs"] / 5
    ),

    2

)

# ==========================
# SORT
# ==========================

favourite = bowler_stats.sort_values(
    "favourite_score",
    ascending=False
)

favourite = favourite.reset_index(
    drop=True
)

favourite.index += 1

# ==========================
# OUTPUT
# ==========================

print("\n==============================")
print("FAVOURITE BOWLERS ENGINE")
print("==============================\n")

print("PLAYER :", player)

print("\nTOP 15 FAVOURITE BOWLERS\n")

print(
    favourite[
        [
            "bowler",
            "runs",
            "balls",
            "strike_rate",
            "favourite_score"
        ]
    ]
    .head(15)
)

# ==========================
# AI REPORT
# ==========================

top = favourite.iloc[0]

print("\n==============================")
print("AI REPORT")
print("==============================\n")

print(
    f"{player} appears to dominate "
    f"{top['bowler']}."
)

print(
    f"Runs Scored: {top['runs']}"
)

print(
    f"Balls Faced: {top['balls']}"
)

print(
    f"Strike Rate: {top['strike_rate']}"
)

print("\nSUMMARY")

if top["strike_rate"] >= 180:
    print(
        f"{player} attacks {top['bowler']} aggressively."
    )

elif top["strike_rate"] >= 150:
    print(
        f"{player} scores comfortably against {top['bowler']}."
    )

else:
    print(
        f"{player} has a positive matchup against {top['bowler']}."
    )