from flask import Flask, render_template, request
import pandas as pd
import json
import os
print("Current Working Directory:", os.getcwd())
print("File Exists:", os.path.exists("data/processed/ball_by_ball_clean.csv"))
from analytics.player_report import generate_player_report
from analytics.predictor import predict_player_performance
from analytics.simulator import simulate_match_impact
from analytics.clutch import get_player_clutch_index, get_top_clutch_players, get_clutch_legends
from analytics.super_over import simulate_super_over
from analytics.moneyball import get_moneyball_analytics, evaluate_player_roi
from analytics.kryptonite import get_player_kryptonite
from analytics.venue_lab import get_venue_lab_stats
from analytics.squad_optimizer import evaluate_squad
from analytics.bowler_intelligence import get_bowler_intelligence
from analytics.advanced_intelligence import get_advanced_player_intelligence
from analytics.player_comparison import compare_players
from analytics.opponent_intelligence import get_opponent_intelligence
from analytics.head_to_head import (
    get_head_to_head,
    get_batter_vs_team,
    get_bowler_vs_team,
)
from analytics.player_form import (
    get_recent_form,
    get_consistency_score,
    get_innings_breakdown,
    get_bowler_recent_form,
    get_bowler_consistency_score,
    get_bowler_milestones,
)
from analytics.leaderboards import (
    get_top_batters,
    get_top_bowlers,
    get_highest_strike_rates,
    get_best_economies,
    get_most_dismissals,
)
from analytics.team_stats import (
    get_team_stats,
    get_team_bowling_stats,
    get_team_performance_by_season,
)
from analytics.season_comparison import (
    get_player_season_stats,
    get_bowler_season_stats,
)
from analytics.dismissal_analysis import (
    get_dismissal_breakdown,
    get_most_common_dismissals,
    get_wicket_takers_by_dismissal,
)
from analytics.charts import runs_by_season_chart
from analytics.statistics import (
    get_overall_statistics,
    get_highest_scoring_matches,
    get_lowest_scoring_matches,
    get_highest_wicket_matches,
    get_stats_by_season,
    get_stats_by_venue,
)
from analytics.report_generator import generate_report

app = Flask(__name__)

# =====================================
# LOAD DATA
# =====================================

# =====================================================
# Load Dataset
# =====================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CSV_PATH = os.path.join(
    BASE_DIR,
    "data",
    "processed",
    "ball_by_ball_clean.csv"
)

if not os.path.isfile(CSV_PATH):
    raise FileNotFoundError(
        f"\nDataset not found!\nExpected location:\n{CSV_PATH}"
    )

df = pd.read_csv(
    CSV_PATH,
    low_memory=False
)

# =====================================
# PLAYER LIST
# =====================================

players = sorted(

    set(
        df["batter"].dropna().unique()
    )

    |

    set(
        df["bowler"].dropna().unique()
    )

)

seasons = [
    "All Seasons"
] + sorted(
    df["season"].dropna().unique().tolist()
)


def get_role_eligibility(filtered_df, player):

    batting_df = filtered_df[filtered_df["batter"] == player]
    bowling_df = filtered_df[filtered_df["bowler"] == player]

    batting_runs = int(batting_df["runs"].sum()) if not batting_df.empty else 0
    batting_balls = len(batting_df)
    bowling_balls = len(bowling_df)
    bowling_wickets = int(bowling_df["wicket"].sum()) if not bowling_df.empty else 0

    has_meaningful_batting = (
        batting_runs >= 100
        or batting_balls >= 100
    )
    has_meaningful_bowling = (
        bowling_balls >= 600
        and bowling_wickets >= 25
    )

    return {
        "batting": has_meaningful_batting,
        "bowling": has_meaningful_bowling,
        "all_rounder": has_meaningful_batting and has_meaningful_bowling,
    }


def build_all_rounder_summary(filtered_df, batter_report, bowler_report):

    if not batter_report or not bowler_report:
        return None

    player = batter_report["player"]
    eligibility = get_role_eligibility(
        filtered_df,
        player
    )

    if not eligibility["all_rounder"]:
        return None

    batting_matches = set(
        filtered_df[filtered_df["batter"] == player]["match_id"].unique()
    )

    bowling_matches = set(
        filtered_df[filtered_df["bowler"] == player]["match_id"].unique()
    )

    matches = len(
        batting_matches | bowling_matches
    )

    impact_index = round(
        (batter_report["runs"] / 100)
        + (batter_report["strike_rate"] / 25)
        + (bowler_report["wickets"] * 2)
        + max(0, 12 - bowler_report["economy"]),
        2
    )

    return {
        "player": player,
        "matches": matches,
        "runs": batter_report["runs"],
        "wickets": bowler_report["wickets"],
        "batting_strike_rate": batter_report["strike_rate"],
        "economy": bowler_report["economy"],
        "impact_index": impact_index
    }


# =====================================
# HOME
# =====================================

@app.route("/", methods=["GET", "POST"])
def home():

    batter_report = None
    bowler_report = None
    all_rounder_summary = None
    advanced_report = None
    season_chart = None
    selected_season = "All Seasons"

    if request.method == "POST":

        player = request.form["player"]
        selected_season = request.form.get(
            "season",
            "All Seasons"
        )

        filtered_df = (
            df
            if selected_season == "All Seasons"
            else df[df["season"] == selected_season]
        )
        eligibility = get_role_eligibility(
            filtered_df,
            player
        )

        # -------------------------
        # Batter
        # -------------------------

        if eligibility["batting"]:

            try:

                batter_report = generate_player_report(
                    filtered_df,
                    player
                )

                if batter_report:
                    season_chart = runs_by_season_chart(
                        filtered_df,
                        player
                    )

            except Exception as e:

                print(
                    "BATTER REPORT ERROR:",
                    e
                )

        # -------------------------
        # Bowler
        # -------------------------

        if eligibility["bowling"]:

            try:

                bowler_report = get_bowler_intelligence(
                    filtered_df,
                    player
                )

            except Exception as e:

                print(
                    "BOWLER REPORT ERROR:",
                    e
                )

        all_rounder_summary = build_all_rounder_summary(
            filtered_df,
            batter_report,
            bowler_report
        )

        try:

            advanced_report = get_advanced_player_intelligence(
                filtered_df,
                player
            )

        except Exception as e:

            print(
                "ADVANCED REPORT ERROR:",
                e
            )

    return render_template(

        "index.html",

        players=players,

        seasons=seasons,

        selected_season=selected_season,

        batter_report=batter_report,

        bowler_report=bowler_report,

        all_rounder_summary=all_rounder_summary,

        advanced_report=advanced_report,

        season_chart=season_chart

    )

# =====================================
# COMPARE PLAYERS
# =====================================

@app.route("/compare", methods=["GET", "POST"])
def compare():
    comparison = None
    player1 = None
    player2 = None

    if request.method == "POST":
        player1 = request.form.get("player1")
        player2 = request.form.get("player2")

        if player1 and player2 and player1 != player2:
            try:
                comparison = compare_players(
                    df,
                    player1,
                    player2
                )
            except Exception as e:
                print("COMPARISON ERROR:", e)

    return render_template(
        "compare.html",
        players=players,
        comparison=comparison,
        player1=player1,
        player2=player2
    )

@app.route("/download-player-csv/<player_name>")
def download_player_csv(player_name):
    from flask import Response
    import base64
    if not player_name or player_name not in players:
        return "Player not found", 404
    rep = generate_report(df, player_name, fmt='csv')
    csv_bytes = base64.b64decode(rep['content'])
    return Response(
        csv_bytes,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={rep['filename']}"}
    )

@app.route("/download-comparison-csv/<player1>/<player2>")
def download_comparison_csv(player1, player2):
    from flask import Response
    if not player1 or not player2:
        return "Invalid parameters", 400
    comp = compare_players(df, player1, player2)
    if not comp:
        return "Comparison data unavailable", 404
    
    lines = [f"Player Comparison Report: {player1} vs {player2}"]
    lines.append(f"Overall Winner,{comp.get('overall_winner', 'N/A')}")
    lines.append(f"Metric Scoreboard,{player1}: {comp.get('p1_wins', 0)} wins | {player2}: {comp.get('p2_wins', 0)} wins")
    lines.append("")
    
    if comp.get("batting") is not None and not comp["batting"].empty:
        lines.append("--- BATTING COMPARISON ---")
        lines.append(comp["batting"].to_csv())
        lines.append("")
        
    if comp.get("bowling") is not None and not comp["bowling"].empty:
        lines.append("--- BOWLING COMPARISON ---")
        lines.append(comp["bowling"].to_csv())
        
    csv_text = "\n".join(lines)
    filename = f"{player1}_vs_{player2}_comparison.csv".replace(" ", "_")
    return Response(
        csv_text,
        mimetype="text/csv",
        headers={"Content-disposition": f"attachment; filename={filename}"}
    )

# =====================================
# PLAYER PERFORMANCE PREDICTOR
# =====================================

@app.route("/predict", methods=["GET", "POST"])
def predict():
    prediction = None
    form_values = {
        "batter": "",
        "bowler": "",
        "venue": "All Venues",
        "batting_team": "All Teams",
        "bowling_team": "All Teams",
        "season": "All Seasons"
    }

    venues_list = ["All Venues"] + sorted(df["venue"].dropna().unique().tolist())
    teams_list = ["All Teams"] + sorted(df["batting_team"].dropna().unique().tolist())

    if request.method == "POST":
        batter = request.form.get("batter", "").strip()
        bowler = request.form.get("bowler", "").strip()
        venue = request.form.get("venue", "All Venues")
        bowling_team = request.form.get("bowling_team", "All Teams")
        batting_team = request.form.get("batting_team", "All Teams")
        season = request.form.get("season", "All Seasons")

        player = batter or bowler
        form_values.update({
            "batter": batter,
            "bowler": bowler,
            "venue": venue,
            "batting_team": batting_team,
            "bowling_team": bowling_team,
            "season": season
        })

        if player:
            try:
                prediction = predict_player_performance(
                    df,
                    player=player,
                    opponent_team=bowling_team,
                    venue=venue,
                    season=season
                )
            except Exception as e:
                print("PREDICTION ERROR:", e)

    return render_template(
        "predict.html",
        players=players,
        venues=venues_list,
        teams=teams_list,
        seasons=seasons,
        form_values=form_values,
        prediction=prediction
    )

# =====================================
# MATCH IMPACT SIMULATOR
# =====================================

@app.route("/simulator", methods=["GET", "POST"])
def simulator():
    simulation = None
    player = None
    target_runs = 40.0
    overs_remaining = 4.0
    req_rr = 10.0
    pitch_condition = "Balanced Pitch"
    dew_factor = "No Dew"

    if request.method == "POST":
        player = request.form.get("player", "").strip()
        target_runs = float(request.form.get("target_runs", 40.0))
        overs_remaining = float(request.form.get("overs_remaining", 4.0))
        req_rr = round(target_runs / max(0.1, overs_remaining), 2)
        pitch_condition = request.form.get("pitch_condition", "Balanced Pitch")
        dew_factor = request.form.get("dew_factor", "No Dew")

        if player:
            try:
                simulation = simulate_match_impact(
                    df,
                    player=player,
                    target_runs=target_runs,
                    overs_remaining=overs_remaining,
                    req_rr=req_rr,
                    pitch_condition=pitch_condition,
                    dew_factor=dew_factor
                )
            except Exception as e:
                print("SIMULATOR ERROR:", e)

    return render_template(
        "simulator.html",
        players=players,
        player=player,
        target_runs=target_runs,
        overs_remaining=overs_remaining,
        req_rr=req_rr,
        pitch_condition=pitch_condition,
        dew_factor=dew_factor,
        simulation=simulation
    )

# =====================================
# CLUTCH & PRESSURE INDEX
# =====================================

@app.route("/clutch", methods=["GET", "POST"])
def clutch():
    player = None
    clutch_data = None
    top_clutch = get_top_clutch_players(df, limit=10)
    clutch_legends = get_clutch_legends(df)

    if request.method == "POST":
        player = request.form.get("player", "").strip()
        if player:
            try:
                clutch_data = get_player_clutch_index(df, player)
            except Exception as e:
                print("CLUTCH ERROR:", e)

    return render_template(
        "clutch.html",
        players=players,
        player=player,
        clutch_data=clutch_data,
        top_clutch=top_clutch,
        clutch_legends=clutch_legends
    )

# =====================================
# HEAD-TO-HEAD
# =====================================

@app.route("/matchup", methods=["GET", "POST"])
def matchup():
    h2h_data = None
    matchup_type = "player_vs_player"
    batter = None
    bowler = None
    team = None
    teams_list = sorted(df["bowling_team"].unique().tolist())

    if request.method == "POST":
        matchup_type = request.form.get("matchup_type", "player_vs_player")
        if matchup_type == "player_vs_player":
            batter = request.form.get("batter")
            bowler = request.form.get("bowler")
            if batter and bowler:
                try:
                    h2h_data = get_head_to_head(df, batter, bowler)
                except Exception as e:
                    print("MATCHUP ERROR (PVP):", e)
        elif matchup_type == "batter_vs_team":
            batter = request.form.get("batter")
            team = request.form.get("team")
            if batter and team:
                try:
                    h2h_data = get_batter_vs_team(df, batter, team)
                except Exception as e:
                    print("MATCHUP ERROR (BVT):", e)
        elif matchup_type == "bowler_vs_team":
            bowler = request.form.get("bowler")
            team = request.form.get("team")
            if bowler and team:
                try:
                    h2h_data = get_bowler_vs_team(df, bowler, team)
                except Exception as e:
                    print("MATCHUP ERROR (WVT):", e)

    return render_template(
        "matchup.html",
        players=players,
        teams=teams_list,
        h2h_data=h2h_data,
        matchup_type=matchup_type,
        batter=batter,
        bowler=bowler,
        team=team
    )

# =====================================
# OPPONENT INTELLIGENCE
# =====================================

@app.route("/opponents", methods=["GET", "POST"])
def opponents():
    opponent_data = None
    player = None

    if request.method == "POST":
        player = request.form.get("player")
        if player:
            try:
                opponent_data = get_opponent_intelligence(df, player)
            except Exception as e:
                print("OPPONENTS ERROR:", e)

    return render_template(
        "opponents.html",
        players=players,
        player=player,
        opponent_data=opponent_data
    )

# =====================================
# RECENT FORM & INSIGHTS
# =====================================

@app.route("/insights", methods=["GET", "POST"])
def insights():

    player = None
    form_data = None
    consistency = None
    milestones = None
    bowler_form = None
    bowler_consistency = None
    bowler_milestones = None

    if request.method == "POST":

        player = request.form.get("player")

        if player:

            try:

                if player in df["batter"].values:

                    form_data = get_recent_form(df, player, limit=5)
                    consistency = get_consistency_score(df, player)
                    milestones = get_innings_breakdown(df, player)

                if player in df["bowler"].values:

                    bowler_form = get_bowler_recent_form(
                        df,
                        player,
                        limit=5
                    )
                    bowler_consistency = get_bowler_consistency_score(df, player)
                    bowler_milestones = get_bowler_milestones(df, player)

            except Exception as e:

                print("INSIGHTS ERROR:", e)

    return render_template(

        "insights.html",

        players=players,

        player=player,

        form_data=form_data,

        consistency=consistency,

        milestones=milestones,

        bowler_form=bowler_form,

        bowler_consistency=bowler_consistency,

        bowler_milestones=bowler_milestones

    )

# =====================================
# LEADERBOARDS
# =====================================

@app.route("/leaderboards")
def leaderboards():
    top_batters = get_top_batters(df, limit=10)
    top_bowlers = get_top_bowlers(df, limit=10)
    highest_sr = get_highest_strike_rates(df, limit=10)
    best_economy = get_best_economies(df, limit=10)
    most_dismissals = get_most_dismissals(df, limit=10)
    
    return render_template(
        "leaderboards.html",
        top_batters=top_batters,
        top_bowlers=top_bowlers,
        highest_sr=highest_sr,
        best_economy=best_economy,
        most_dismissals=most_dismissals
    )

# =====================================
# TEAM STATS
# =====================================

@app.route("/teams")
def teams():
    team_batting = get_team_stats(df)
    team_bowling = get_team_bowling_stats(df)
    teams_list = sorted(df["batting_team"].unique().tolist())
    
    return render_template(
        "teams.html",
        team_batting=team_batting,
        team_bowling=team_bowling,
        teams_list=teams_list
    )

# =====================================
# SEASON COMPARISON
# =====================================

@app.route("/season-comparison", methods=["GET", "POST"])
def season_comparison():
    player = None
    season_stats = None
    is_bowler = False
    
    if request.method == "POST":
        player = request.form.get("player")
        player_type = request.form.get("player_type", "batter")
        is_bowler = (player_type == "bowler")
        
        if player:
            try:
                if is_bowler:
                    season_stats = get_bowler_season_stats(df, player)
                else:
                    season_stats = get_player_season_stats(df, player)
            except Exception as e:
                print("SEASON COMPARISON ERROR:", e)
    
    return render_template(
        "season_comparison.html",
        players=players,
        player=player,
        season_stats=season_stats,
        is_bowler=is_bowler
    )

# =====================================
# DISMISSAL ANALYSIS
# =====================================

@app.route("/dismissals")
def dismissals():
    common_dismissals = get_most_common_dismissals(df, limit=10)
    bowled_bowlers = get_wicket_takers_by_dismissal(df, "bowled", limit=10) if common_dismissals is not None else None
    lbw_bowlers = get_wicket_takers_by_dismissal(df, "lbw", limit=10) if common_dismissals is not None else None
    
    return render_template(
        "dismissals.html",
        common_dismissals=common_dismissals,
        bowled_bowlers=bowled_bowlers,
        lbw_bowlers=lbw_bowlers
    )

# =====================================
# STATISTICS
# =====================================

@app.route("/statistics")
def statistics():
    overall_stats = get_overall_statistics(df)
    highest_scoring = get_highest_scoring_matches(df, limit=10)
    lowest_scoring = get_lowest_scoring_matches(df, limit=10)
    highest_wickets = get_highest_wicket_matches(df, limit=10)
    season_stats = get_stats_by_season(df)
    venue_stats = get_stats_by_venue(df, limit=15)
    
    return render_template(
        "statistics.html",
        overall_stats=overall_stats,
        highest_scoring=highest_scoring,
        lowest_scoring=lowest_scoring,
        highest_wickets=highest_wickets,
        season_stats=season_stats,
        venue_stats=venue_stats
    )

# =====================================
# REPORTS
# =====================================

@app.route("/reports", methods=["GET", "POST"])
def reports():
    report_result = None
    player = None
    error = None

    if request.method == "POST":
        player = request.form.get("player")
        if player:
            try:
                report_result = generate_report(df, player)
            except Exception as e:
                error = str(e)
                print("REPORTS ERROR:", e)

    return render_template(
        "reports.html",
        players=players,
        player=player,
        report_result=report_result,
        error=error
    )

# =====================================
# SEARCH
# =====================================

@app.route("/search")
def search():
    query = request.args.get("q", "").strip().lower()
    results = []

    if query:
        results = [p for p in players if query in p.lower()]

    return render_template(
        "search.html",
        query=query,
        results=results,
        players=players
    )

# =====================================
# SUPER OVER SHOWDOWN
# =====================================
@app.route("/super-over", methods=["GET", "POST"])
def super_over():
    simulation = None
    batter = None
    bowler = None
    if request.method == "POST":
        batter = request.form.get("batter", "").strip()
        bowler = request.form.get("bowler", "").strip()
        if batter and bowler:
            try:
                simulation = simulate_super_over(df, batter, bowler)
            except Exception as e:
                print("SUPER OVER ERROR:", e)
    return render_template(
        "super_over.html",
        players=players,
        batter=batter,
        bowler=bowler,
        simulation=simulation
    )

# =====================================
# MONEYBALL ROI ENGINE
# =====================================
@app.route("/moneyball", methods=["GET", "POST"])
def moneyball():
    roi_data = None
    player = None
    price = 7.5
    moneyball_data = get_moneyball_analytics(df)
    if request.method == "POST":
        player = request.form.get("player", "").strip()
        try:
            price = float(request.form.get("price", 7.5))
        except ValueError:
            price = 7.5
        if player:
            try:
                roi_data = evaluate_player_roi(df, player, price)
            except Exception as e:
                print("MONEYBALL ERROR:", e)
    return render_template(
        "moneyball.html",
        players=players,
        player=player,
        price=price,
        roi_data=roi_data,
        moneyball_data=moneyball_data
    )

# =====================================
# KRYPTONITE RADAR
# =====================================
@app.route("/kryptonite", methods=["GET", "POST"])
def kryptonite():
    kryptonite_data = None
    player = None
    if request.method == "POST":
        player = request.form.get("player", "").strip()
        if player:
            try:
                kryptonite_data = get_player_kryptonite(df, player)
            except Exception as e:
                print("KRYPTONITE ERROR:", e)
    return render_template(
        "kryptonite.html",
        players=players,
        player=player,
        kryptonite=kryptonite_data
    )

# =====================================
# STADIUM PITCH LAB
# =====================================
@app.route("/venue-lab", methods=["GET", "POST"])
def venue_lab():
    selected_venue = None
    if request.method == "POST":
        selected_venue = request.form.get("venue", "").strip()
    venue_data = get_venue_lab_stats(df, selected_venue)
    return render_template(
        "venue_lab.html",
        venue_data=venue_data
    )

# =====================================
# DREAM XI SQUAD OPTIMIZER
# =====================================
@app.route("/squad-builder", methods=["GET", "POST"])
def squad_builder():
    squad_result = None
    selected_inputs = []
    if request.method == "POST":
        selected_inputs = [request.form.get(f"player_{i}", "").strip() for i in range(1, 12)]
        valid_players = [p for p in selected_inputs if p]
        if valid_players:
            try:
                squad_result = evaluate_squad(df, valid_players)
            except Exception as e:
                print("SQUAD OPTIMIZER ERROR:", e)
    return render_template(
        "squad_builder.html",
        players=players,
        selected_inputs=selected_inputs,
        squad_result=squad_result
    )

# =====================================
# RUN
# =====================================

if __name__ == "__main__":
    app.run(debug=True)
