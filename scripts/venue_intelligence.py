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
# VENUE STATS
# ==========================

venue_stats = (

    player_df

    .groupby("venue")

    .agg(
        runs=("runs", "sum"),
        balls=("runs", "count"),
        matches=("match_id", "nunique")
    )

)

venue_stats = venue_stats.reset_index()

# ==========================
# STRIKE RATE
# ==========================

venue_stats["strike_rate"] = round(
    (
        venue_stats["runs"]
        /
        venue_stats["balls"]
    ) * 100,
    2
)

# ==========================
# MINIMUM SAMPLE
# ==========================

venue_stats = venue_stats[
    venue_stats["balls"] >= 50
]

# ==========================
# BEST VENUES
# ==========================

best_venues = venue_stats.sort_values(
    ["runs", "strike_rate"],
    ascending=False
)

best_venues = best_venues.reset_index(
    drop=True
)

best_venues.index += 1

# ==========================
# WORST VENUES
# ==========================

worst_venues = venue_stats.sort_values(
    ["strike_rate", "runs"],
    ascending=True
)

worst_venues = worst_venues.reset_index(
    drop=True
)

worst_venues.index += 1

# ==========================
# OUTPUT
# ==========================

print("\n==============================")
print("BEST VENUES")
print("==============================\n")

print(
    best_venues[
        [
            "venue",
            "runs",
            "balls",
            "matches",
            "strike_rate"
        ]
    ]
    .head(5)
)

print("\n==============================")
print("WORST VENUES")
print("==============================\n")

print(
    worst_venues[
        [
            "venue",
            "runs",
            "balls",
            "matches",
            "strike_rate"
        ]
    ]
    .head(5)
)

# ==========================
# AI REPORT
# ==========================

best = best_venues.iloc[0]

worst = worst_venues.iloc[0]

print("\n==============================")
print("AI REPORT")
print("==============================\n")

print(
    f"Best Venue : {best['venue']}"
)

print(
    f"Worst Venue : {worst['venue']}"
)

print(
    f"{player} has scored "
    f"{best['runs']} runs at "
    f"{best['venue']}."
)

print(
    f"{player} has struggled comparatively "
    f"at {worst['venue']}."
)