import pandas as pd

df = pd.read_csv(
    "data/processed/ball_by_ball_clean.csv",
    low_memory=False
)

team_map = {

    # RCB rename
    "Royal Challengers Bengaluru":
    "Royal Challengers Bangalore",

    # Delhi rename
    "Delhi Capitals":
    "Delhi Daredevils",

    # Punjab rename
    "Punjab Kings":
    "Kings XI Punjab",

    # Pune duplicate
    "Rising Pune Supergiants":
    "Rising Pune Supergiant"

}

df["team"] = df["team"].replace(
    team_map
)

df.to_csv(
    "data/processed/ball_by_ball_clean.csv",
    index=False
)

print("\nUNIQUE TEAMS\n")

for team in sorted(df["team"].unique()):
    print(team)