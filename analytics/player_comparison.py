import pandas as pd

def get_player_batting_stats(df, player):
    player_df = df[df["batter"] == player]
    if len(player_df) == 0:
        return None

    runs = int(player_df["runs"].sum())
    balls = len(player_df)
    matches = player_df["match_id"].nunique()
    strike_rate = round((runs / balls) * 100, 2) if balls > 0 else 0
    dismissals = int(df[df["player_dismissed"] == player].shape[0])
    average = round(runs / dismissals, 2) if dismissals > 0 else runs

    innings_scores = player_df.groupby("match_id")["runs"].sum()
    highest_score = int(innings_scores.max()) if not innings_scores.empty else 0
    fifties = int(((innings_scores >= 50) & (innings_scores < 100)).sum())
    hundreds = int((innings_scores >= 100).sum())

    fours = int((player_df["runs"] == 4).sum())
    sixes = int((player_df["runs"] == 6).sum())
    boundary_runs = fours * 4 + sixes * 6
    boundary_percentage = round((boundary_runs / runs) * 100, 2) if runs > 0 else 0
    dot_ball_percentage = round(((player_df["runs"] == 0).sum() / balls) * 100, 2) if balls > 0 else 0

    return {
        "Matches": matches,
        "Runs": runs,
        "Average": average,
        "Strike Rate": strike_rate,
        "Highest Score": highest_score,
        "50s": fifties,
        "100s": hundreds,
        "Boundary %": boundary_percentage,
        "Dot Ball %": dot_ball_percentage
    }

def get_player_bowling_stats(df, player):
    player_df = df[df["bowler"] == player]
    if len(player_df) == 0:
        return None

    wickets = int(player_df["wicket"].sum())
    balls = len(player_df)
    overs = round(balls / 6, 1)
    runs_conceded = int(player_df["total_runs"].sum())
    economy = round(runs_conceded / (balls / 6), 2) if balls > 0 else 0
    bowling_sr = round(balls / wickets, 2) if wickets > 0 else 0
    bowling_avg = round(runs_conceded / wickets, 2) if wickets > 0 else 0

    boundary_balls = int((player_df["runs"] >= 4).sum())
    dot_balls = int((player_df["runs"] == 0).sum())
    boundary_percentage = round((boundary_balls / balls) * 100, 2) if balls > 0 else 0
    dot_ball_percentage = round((dot_balls / balls) * 100, 2) if balls > 0 else 0
    matches = player_df["match_id"].nunique()

    return {
        "Matches": matches,
        "Wickets": wickets,
        "Overs": overs,
        "Economy": economy,
        "Bowling Avg": bowling_avg,
        "Bowling SR": bowling_sr,
        "Boundary Conceded %": boundary_percentage,
        "Dot Ball %": dot_ball_percentage
    }

def compare_players(df, player1, player2):
    """Compare two players across career batting and bowling statistics."""
    p1_wins = 0
    p2_wins = 0

    # Batting
    p1_bat = get_player_batting_stats(df, player1)
    p2_bat = get_player_batting_stats(df, player2)
    batting_comparison = None
    if p1_bat is not None and p2_bat is not None:
        batting_comparison = pd.DataFrame(
            {
                player1: list(p1_bat.values()),
                player2: list(p2_bat.values())
            },
            index=list(p1_bat.keys())
        )
        for metric, row in batting_comparison.iterrows():
            try:
                left = float(row[player1])
                right = float(row[player2])
            except (ValueError, TypeError):
                continue

            lower_better = metric in ["Dot Ball %"]
            if lower_better:
                if left < right:
                    p1_wins += 1
                elif right > left:
                    p2_wins += 1
            else:
                if left > right:
                    p1_wins += 1
                elif right > left:
                    p2_wins += 1

    # Bowling
    p1_bowl = get_player_bowling_stats(df, player1)
    p2_bowl = get_player_bowling_stats(df, player2)
    bowling_comparison = None
    if p1_bowl is not None and p2_bowl is not None:
        bowling_comparison = pd.DataFrame(
            {
                player1: list(p1_bowl.values()),
                player2: list(p2_bowl.values())
            },
            index=list(p1_bowl.keys())
        )
        for metric, row in bowling_comparison.iterrows():
            try:
                left = float(row[player1])
                right = float(row[player2])
            except (ValueError, TypeError):
                continue

            lower_better = metric in ["Economy", "Bowling Avg", "Bowling SR", "Boundary Conceded %"]
            if lower_better:
                if left < right:
                    p1_wins += 1
                elif right > left:
                    p2_wins += 1
            else:
                if left > right:
                    p1_wins += 1
                elif right > left:
                    p2_wins += 1
    elif p1_bowl is not None and p2_bowl is None:
        # Player 1 has active bowling contributions while Player 2 has none
        if p1_bowl.get("Wickets", 0) > 0:
            p1_wins += 2
    elif p2_bowl is not None and p1_bowl is None:
        # Player 2 has active bowling contributions while Player 1 has none
        if p2_bowl.get("Wickets", 0) > 0:
            p2_wins += 2

    overall_winner = None
    if p1_wins > p2_wins:
        overall_winner = player1
    elif p2_wins > p1_wins:
        overall_winner = player2
    elif p1_wins > 0 or p2_wins > 0:
        overall_winner = "Tie"

    return {
        "batting": batting_comparison,
        "bowling": bowling_comparison,
        "p1_wins": p1_wins,
        "p2_wins": p2_wins,
        "overall_winner": overall_winner
    }