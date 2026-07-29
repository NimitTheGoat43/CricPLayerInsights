import pandas as pd
from analytics.leaderboards import get_top_batters
from analytics.statistics import get_overall_statistics

df = pd.read_csv("data/processed/ball_by_ball_clean.csv", low_memory=False)
print("Testing leaderboards...")
top_batters = get_top_batters(df, limit=5)
print(top_batters)
print("\nTesting overall statistics...")
stats = get_overall_statistics(df)
print(f"Total matches: {stats['total_matches']}")
print(f"Total players: {stats['total_players']}")
print("✓ Analytics functions working!")
