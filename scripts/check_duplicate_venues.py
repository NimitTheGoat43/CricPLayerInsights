import pandas as pd

# ==========================
# LOAD DATASET
# ==========================

df = pd.read_csv(
    "data/processed/ball_by_ball.csv"
)

# ==========================
# CLEAN VENUE NAMES
# ==========================

df["venue"] = (
    df["venue"]
    .astype(str)
    .str.split(",")
    .str[0]
    .str.strip()
)

# ==========================
# SAVE CLEAN DATASET
# ==========================

df.to_csv(
    "data/processed/ball_by_ball_clean.csv",
    index=False
)

print("\nDATASET CLEANED SUCCESSFULLY")

print("\nROWS:", len(df))

print("\nUNIQUE VENUES:")
print(df["venue"].nunique())

print("\nSAMPLE VENUES:")
print(
    sorted(
        df["venue"].unique()
    )[:20]
)