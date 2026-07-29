import pandas as pd

# ==========================
# LOAD CLEAN DATASET
# ==========================

df = pd.read_csv(
    "data/processed/ball_by_ball_clean.csv"
)

# ==========================
# PLAYER NAME
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

strike_rate = round(
    (runs / balls) * 100,
    2
) if balls > 0 else 0

fours = len(
    player_df[
        player_df["runs"] == 4
    ]
)

sixes = len(
    player_df[
        player_df["runs"] == 6
    ]
)

matches = player_df["match_id"].nunique()

# ==========================
# VENUE ANALYSIS
# ==========================

venue_stats = (
    player_df
    .groupby("venue")
    .agg(
        runs=("runs", "sum"),
        balls=("runs", "count")
    )
)

# Ignore venues where player barely played

venue_stats = venue_stats[
    venue_stats["balls"] >= 50
]

venue_stats["strike_rate"] = round(
    (
        venue_stats["runs"]
        /
        venue_stats["balls"]
    ) * 100,
    2
)

best_venues = (
    venue_stats
    .sort_values(
        "runs",
        ascending=False
    )
    .head(5)
)

worst_venues = (
    venue_stats
    .sort_values(
        "strike_rate",
        ascending=True
    )
    .head(5)
)

# ==========================
# DANGEROUS BOWLERS
# ==========================

dangerous_bowlers = (

    df[
        (df["batter"] == player)
        &
        (df["wicket"] == 1)
    ]

    .groupby("bowler")
    .size()

    .sort_values(
        ascending=False
    )

    .head(5)

)

# ==========================
# FAVORITE BOWLERS
# ==========================

bowler_stats = (

    player_df

    .groupby("bowler")

    .agg({

        "runs":"sum",

        "bowler":"count"

    })

)

bowler_stats.columns = [

    "runs",

    "balls"

]

bowler_stats["sr"] = (

    bowler_stats["runs"]

    /

    bowler_stats["balls"]

) * 100

favorite_bowlers = (

    bowler_stats

    .sort_values(
        "sr",
        ascending=False
    )

    .head(5)

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
) if pp_balls > 0 else 0

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
) if death_balls > 0 else 0

# ==========================
# REPORT
# ==========================

print("\n===================")
print("PLAYER INTELLIGENCE")
print("===================\n")

print("PLAYER :", player)

print("MATCHES :", matches)

print("RUNS :", runs)

print("BALLS :", balls)

print("STRIKE RATE :", strike_rate)

print("FOURS :", fours)

print("SIXES :", sixes)

print("\nBEST VENUES")
print(best_venues)

print("\nWORST VENUES")
print(worst_venues)

print("\nDANGEROUS BOWLERS")
print(dangerous_bowlers)

print("\nFAVORITE BOWLERS")
print(
    favorite_bowlers["sr"]
)

print("\nPOWERPLAY SR")
print(pp_sr)

print("\nDEATH OVER SR")
print(death_sr)

print("\nANALYST REPORT")

if death_sr > strike_rate:
    print(
        f"{player} accelerates strongly in death overs."
    )

if pp_sr > strike_rate:
    print(
        f"{player} is aggressive in powerplay."
    )

if death_sr < strike_rate:
    print(
        f"{player} scores more consistently before death overs."
    )