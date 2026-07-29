import pandas as pd

df = pd.read_csv(
    "data/processed/ball_by_ball_clean.csv",
    low_memory=False
)

print("\nSEASONS:")
print(
    sorted(
        df["season"].unique()
    )
)

print("\nTOTAL MATCHES:")
print(
    df["match_id"].nunique()
)

print("\nTOTAL BATTERS:")
print(
    df["batter"].nunique()
)

print("\nTOTAL BOWLERS:")
print(
    df["bowler"].nunique()
)