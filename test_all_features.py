import pandas as pd

from analytics.dismissal_analysis import (
    get_most_common_dismissals,
    get_wicket_takers_by_dismissal,
)
from analytics.leaderboards import (
    get_best_economies,
    get_highest_strike_rates,
    get_most_dismissals,
    get_top_batters,
    get_top_bowlers,
)
from analytics.statistics import (
    get_highest_scoring_matches,
    get_highest_wicket_matches,
    get_lowest_scoring_matches,
    get_overall_statistics,
    get_stats_by_season,
    get_stats_by_venue,
)
from analytics.team_stats import get_team_bowling_stats, get_team_stats


df = pd.read_csv("data/processed/ball_by_ball_clean.csv", low_memory=False)

print("Testing leaderboards...")
assert get_top_batters(df) is not None
assert get_top_bowlers(df) is not None
assert get_highest_strike_rates(df) is not None
assert get_best_economies(df) is not None
assert get_most_dismissals(df) is not None

print("Testing teams...")
assert get_team_stats(df) is not None
assert get_team_bowling_stats(df) is not None

print("Testing dismissals...")
assert get_most_common_dismissals(df) is not None
assert get_wicket_takers_by_dismissal(df, "bowled") is not None

print("Testing statistics...")
stats = get_overall_statistics(df)
assert isinstance(stats, dict)
assert get_highest_scoring_matches(df) is not None
assert get_lowest_scoring_matches(df) is not None
assert get_highest_wicket_matches(df) is not None
assert get_stats_by_season(df) is not None
assert get_stats_by_venue(df) is not None

print("\nAll active features tested successfully!")
