import pandas as pd

df = pd.read_csv(
    "data/processed/ball_by_ball.csv"
)

player = "V Kohli"

batting = df[
    df["batter"] == player
]

runs = batting["runs"].sum()

balls = len(batting)

strike_rate = round(
    runs / balls * 100,
    2
)

fours = len(
    batting[
        batting["runs"] == 4
    ]
)

sixes = len(
    batting[
        batting["runs"] == 6
    ]
)

print()

print("PLAYER:", player)

print("Runs:", runs)

print("Balls:", balls)

print("SR:", strike_rate)

print("4s:", fours)

print("6s:", sixes)