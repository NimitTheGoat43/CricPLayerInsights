import pandas as pd

# ==========================
# LOAD DATA
# ==========================

df = pd.read_csv(
    "data/processed/ball_by_ball_clean.csv",
    low_memory=False
)

# ==========================
# INPUTS
# ==========================

batter = "V Kohli"
bowler = "PJ Cummins"

# ==========================
# FILTER MATCHUP
# ==========================

matchup = df[
    (df["batter"] == batter)
    &
    (df["bowler"] == bowler)
]

# ==========================
# BASIC STATS
# ==========================

runs = int(
    matchup["runs"].sum()
)

balls = len(matchup)

strike_rate = round(
    (runs / balls) * 100,
    2
) if balls > 0 else 0

dismissals = int(
    matchup["wicket"].sum()
)

# ==========================
# DOT BALLS
# ==========================

dots = len(
    matchup[
        matchup["runs"] == 0
    ]
)

dot_percentage = round(
    (dots / balls) * 100,
    2
) if balls > 0 else 0

# ==========================
# BOUNDARIES
# ==========================

fours = len(
    matchup[
        matchup["runs"] == 4
    ]
)

sixes = len(
    matchup[
        matchup["runs"] == 6
    ]
)

boundaries = fours + sixes

boundary_percentage = round(
    (boundaries / balls) * 100,
    2
) if balls > 0 else 0

boundary_runs = (
    fours * 4
    +
    sixes * 6
)

boundary_run_percentage = round(
    (boundary_runs / runs) * 100,
    2
) if runs > 0 else 0

# ==========================
# DISMISSAL RATE
# ==========================

dismissal_rate = round(
    (dismissals / balls) * 100,
    2
) if balls > 0 else 0

# ==========================
# RUNS PER BALL
# ==========================

runs_per_ball = round(
    runs / balls,
    2
) if balls > 0 else 0

# ==========================
# OUTPUT
# ==========================

print("\n==========================")
print("MATCHUP INTELLIGENCE")
print("==========================\n")

print("BATTER :", batter)

print("BOWLER :", bowler)

print("\nRUNS :", runs)

print("BALLS :", balls)

print("STRIKE RATE :", strike_rate)

print("RUNS PER BALL :", runs_per_ball)

print("DISMISSALS :", dismissals)

print("DISMISSAL RATE :", dismissal_rate)

print("\nDOT BALL % :", dot_percentage)

print("FOURS :", fours)

print("SIXES :", sixes)

print("BOUNDARY % :", boundary_percentage)

print(
    "BOUNDARY RUN % :",
    boundary_run_percentage
)

# ==========================
# ANALYST REPORT
# ==========================

print("\n==========================")
print("ANALYST REPORT")
print("==========================\n")

if dismissals >= 5:
    print(
        f"{bowler} has consistently troubled {batter}."
    )

if dot_percentage >= 50:
    print(
        f"{bowler} maintains strong pressure through dot balls."
    )

if boundary_percentage >= 20:
    print(
        f"{batter} finds boundaries regularly against {bowler}."
    )

if strike_rate >= 140:
    print(
        f"{batter} attacks aggressively in this matchup."
    )

else:
    print(
        f"This matchup is fairly balanced."
    )

print("\n==========================")