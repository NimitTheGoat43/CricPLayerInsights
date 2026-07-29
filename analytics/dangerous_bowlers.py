import pandas as pd

def get_dangerous_bowlers(df, player):

    dismissals = (
    df[df["player_dismissed"] == player]
    .groupby("bowler")
    .size()
    .reset_index(name="outs")
    .sort_values("outs", ascending=False)
    .reset_index(drop=True)
)

    return dismissals.head(10)