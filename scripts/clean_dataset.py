import pandas as pd

df = pd.read_csv(
    "data/processed/ball_by_ball.csv",
    low_memory=False
)

# Venue Cleaning

df["venue"] = (
    df["venue"]
    .astype(str)
    .str.split(",")
    .str[0]
    .str.strip()
)

venue_map = {

    "M.Chinnaswamy Stadium":
    "M Chinnaswamy Stadium",

    "Feroz Shah Kotla":
    "Arun Jaitley Stadium"

}

df["venue"] = df["venue"].replace(
    venue_map
)

# Team Cleaning

team_map = {

    "Royal Challengers Bengaluru":
    "Royal Challengers Bangalore",

    "Punjab Kings":
    "Kings XI Punjab",

    "Rising Pune Supergiants":
    "Rising Pune Supergiant"

}

df["batting_team"] = df[
    "batting_team"
].replace(team_map)

df["bowling_team"] = df[
    "bowling_team"
].replace(team_map)

df.to_csv(
    "data/processed/ball_by_ball_clean.csv",
    index=False
)

print("\nCLEAN DATASET CREATED")
print("\nROWS:", len(df))
print(
    "\nUNIQUE TEAMS:",
    df["batting_team"].nunique()
)
print(
    "UNIQUE VENUES:",
    df["venue"].nunique()
)