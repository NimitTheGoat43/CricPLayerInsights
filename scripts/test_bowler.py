import pandas as pd

from analytics.bowler_intelligence import get_bowler_intelligence

df = pd.read_csv(
    "data/processed/ball_by_ball_clean.csv",
    low_memory=False
)

report = get_bowler_intelligence(
    df,
    "JJ Bumrah"
)

print(report)