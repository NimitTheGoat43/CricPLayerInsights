import sys
sys.path.insert(0, '/c/Users/YUG MEHTA/Desktop/CricPlayerInsights')

import pandas as pd
from analytics.leaderboards import get_top_batters, get_top_bowlers, get_highest_strike_rates, get_best_economies, get_most_dismissals

df = pd.read_csv('data/processed/ball_by_ball_clean.csv', low_memory=False)

print("Testing leaderboards data shapes...")
top_batters = get_top_batters(df, limit=10)
top_bowlers = get_top_bowlers(df, limit=10)
highest_sr = get_highest_strike_rates(df, limit=10)
best_economy = get_best_economies(df, limit=10)
most_dismissals = get_most_dismissals(df, limit=10)

print(f"top_batters shape: {top_batters.shape}")
print(f"top_bowlers shape: {top_bowlers.shape}")
print(f"highest_sr shape: {highest_sr.shape}")
print(f"best_economy shape: {best_economy.shape}")
print(f"most_dismissals shape: {most_dismissals.shape}")

# Test rendering
print("\nTesting template render...")
print(f"top_batters columns: {list(top_batters.columns)}")
print(f"top_bowlers columns: {list(top_bowlers.columns)}")
print("\nAll looks good!")
