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

# ==========================
# ALL BALLS FACED
# ==========================

player_df = df[
    df["batter"] == player
]

# ==========================
# RUNS & BALLS VS BOWLERS
# ==========================

bowler_stats = (

    player_df

    .groupby("bowler")

    .agg(
        runs=("runs", "sum"),
        balls=("runs", "count")
    )

)

# ==========================
# DISMISSALS
# ==========================

dismissals = (

    df[
        df["player_dismissed"] == player
    ]

    .groupby("bowler")

    .size()

    .reset_index(name="outs")

)

# ==========================
# MERGE
# ==========================

bowler_stats = bowler_stats.reset_index()

final = bowler_stats.merge(
    dismissals,
    on="bowler",
    how="left"
)

final["outs"] = (
    final["outs"]
    .fillna(0)
    .astype(int)
)

# ==========================
# STRIKE RATE
# ==========================

final["strike_rate"] = round(
    (
        final["runs"]
        /
        final["balls"]
    ) * 100,
    2
)

# ==========================
# OUT RATE
# ==========================

final["out_rate"] = round(
    (
        final["outs"]
        /
        final["balls"]
    ) * 100,
    2
)

# ==========================
# MINIMUM SAMPLE SIZE
# ==========================

final = final[
    final["balls"] >= 20
]

# ==========================
# DANGER SCORE
# ==========================

final["danger_score"] = round(

    (
        final["out_rate"] * 5
    )

    -

    (
        final["strike_rate"] / 25
    ),

    2

)

# ==========================
# SORT
# ==========================

dangerous = final.sort_values(
    "danger_score",
    ascending=False
)
# ==========================
# SORT
# ==========================

dangerous = final.sort_values(
    "danger_score",
    ascending=False
)

dangerous = dangerous.reset_index(
    drop=True
)

dangerous.index += 1

# ==========================
# OUTPUT
# ==========================

print("\n==============================")
print("DANGEROUS BOWLERS V2")
print("==============================\n")

print("PLAYER :", player)

print("\nTOP 15 DANGEROUS BOWLERS\n")

print(
    dangerous[
        [
            "bowler",
            "runs",
            "balls",
            "outs",
            "strike_rate",
            "out_rate",
            "danger_score"
        ]
    ]
    .head(15)
)

# ==========================
# AI REPORT
# ==========================

top = dangerous.iloc[0]

print("\n==============================")
print("AI REPORT")
print("==============================\n")

print(
    f"{top['bowler']} appears to be one of "
    f"{player}'s toughest opponents."
)

print(
    f"Runs Scored: {top['runs']}"
)

print(
    f"Balls Faced: {top['balls']}"
)

print(
    f"Dismissals: {top['outs']}"
)

print(
    f"Strike Rate: {top['strike_rate']}"
)

print(
    f"Out Rate: {top['out_rate']}%"
)

print("\nSUMMARY")

if top["outs"] >= 5:
    print(
        f"{top['bowler']} has dismissed "
        f"{player} frequently."
    )

if top["strike_rate"] < 120:
    print(
        f"{player} scores slowly against "
        f"{top['bowler']}."
    )

elif top["strike_rate"] > 140:
    print(
        f"{player} still scores aggressively "
        f"against {top['bowler']} despite "
        f"being dismissed multiple times."
    )