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
from analytics.opponent_intelligence import get_opponent_intelligence
from analytics.player_comparison import compare_players

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

print("Testing new opponent intelligence...")
opp_stats = get_opponent_intelligence(df, "MS Dhoni")
assert opp_stats is not None
assert isinstance(opp_stats, dict)
assert "batting" in opp_stats
assert "bowling" in opp_stats

print("Testing player comparison...")
# Compare two batters / all-rounders
comp_batters = compare_players(df, "MS Dhoni", "RG Sharma")
assert comp_batters is not None
assert isinstance(comp_batters, dict)
assert comp_batters["batting"] is not None

# Compare two pure bowlers
comp_bowlers = compare_players(df, "JJ Bumrah", "Rashid Khan")
assert comp_bowlers is not None
assert isinstance(comp_bowlers, dict)
assert comp_bowlers["bowling"] is not None

print("Testing predictor...")
from analytics.predictor import predict_player_performance
pred = predict_player_performance(df, "MS Dhoni")
assert pred is not None
assert isinstance(pred, dict)

print("Testing simulator...")
from analytics.simulator import simulate_match_impact
sim = simulate_match_impact(df, "MS Dhoni")
assert sim is not None
assert isinstance(sim, dict)

print("Testing clutch index...")
from analytics.clutch import get_player_clutch_index, get_top_clutch_players
clutch_p = get_player_clutch_index(df, "MS Dhoni")
assert clutch_p is not None
top_clutch = get_top_clutch_players(df)
assert top_clutch is not None

print("Testing Super Over Showdown...")
from analytics.super_over import simulate_super_over
so = simulate_super_over(df, "MS Dhoni", "JJ Bumrah")
assert so is not None
assert isinstance(so, dict)

print("Testing Moneyball ROI Engine...")
from analytics.moneyball import get_moneyball_analytics, evaluate_player_roi
mb = get_moneyball_analytics(df)
assert mb is not None
roi = evaluate_player_roi(df, "MS Dhoni", 12.0)
assert roi is not None

print("Testing Kryptonite Radar...")
from analytics.kryptonite import get_player_kryptonite
kry = get_player_kryptonite(df, "V Kohli")
assert kry is not None

print("Testing Stadium Pitch Lab...")
from analytics.venue_lab import get_venue_lab_stats
vl = get_venue_lab_stats(df)
assert vl is not None

print("Testing Dream XI Squad Optimizer...")
from analytics.squad_optimizer import evaluate_squad
sq = evaluate_squad(df, ["MS Dhoni", "V Kohli", "JJ Bumrah", "AB de Villiers"])
assert sq is not None

print("\nAll active features tested successfully!")
