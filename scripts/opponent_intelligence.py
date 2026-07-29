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
# RUNS & BALLS VS TEAMS
# ==========================

team_stats = (

    player_df

    .groupby("bowling_team")

    .agg(
        runs=("runs", "sum"),
        balls=("runs", "count")
    )

    .reset_index()

)

# ==========================
# DISMISSALS VS TEAMS
# ==========================

dismissals = (

    df[
        df["player_dismissed"] == player
    ]

    .groupby("bowling_team")

    .size()

    .reset_index(name="outs")

)

# ==========================
# MERGE
# ==========================

team_stats = team_stats.merge(
    dismissals,
    on="bowling_team",
    how="left"
)

team_stats["outs"] = (
    team_stats["outs"]
    .fillna(0)
    .astype(int)
)

# ==========================
# STRIKE RATE
# ==========================

team_stats["strike_rate"] = round(
    (
        team_stats["runs"]
        /
        team_stats["balls"]
    ) * 100,
    2
)

# ==========================
# AVERAGE
# ==========================

team_stats["average"] = 0.0

team_stats.loc[
    team_stats["outs"] > 0,
    "average"
] = round(
    team_stats["runs"]
    /
    team_stats["outs"],
    2
)

team_stats.loc[
    team_stats["outs"] == 0,
    "average"
] = team_stats["runs"]

# ==========================
# MINIMUM SAMPLE SIZE
# ==========================

team_stats = team_stats[
    team_stats["balls"] >= 50
]

# ==========================
# FAVOURITE OPPONENTS
# ==========================

favourite = team_stats.sort_values(
    ["strike_rate", "runs"],
    ascending=False
)

favourite = favourite.reset_index(
    drop=True
)

favourite.index += 1

# ==========================
# DANGEROUS OPPONENTS
# ==========================

dangerous = team_stats.sort_values(
    ["average", "strike_rate"]
)

dangerous = dangerous.reset_index(
    drop=True
)

dangerous.index += 1

# ==========================
# OUTPUT
# ==========================

print("\n==============================")
print("FAVOURITE OPPONENTS")
print("==============================\n")

print(
    favourite[
        [
            "bowling_team",
            "runs",
            "balls",
            "outs",
            "average",
            "strike_rate"
        ]
    ]
    .head(5)
)

print("\n==============================")
print("DANGEROUS OPPONENTS")
print("==============================\n")

print(
    dangerous[
        [
            "bowling_team",
            "runs",
            "balls",
            "outs",
            "average",
            "strike_rate"
        ]
    ]
    .head(5)
)

# ==========================
# AI REPORT
# ==========================

fav = favourite.iloc[0]

dang = dangerous.iloc[0]

print("\n==============================")
print("AI REPORT")
print("==============================\n")

print(
    f"Favourite Opponent: {fav['bowling_team']}"
)

print(
    f"Dangerous Opponent: {dang['bowling_team']}"
)

print(
    f"{player} scores most freely against "
    f"{fav['bowling_team']}."
)

print(
    f"{dang['bowling_team']} has been one of "
    f"the toughest teams for {player}."
)