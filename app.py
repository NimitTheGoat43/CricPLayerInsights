from flask import Flask, render_template, request
import pandas as pd

from analytics.player_report import generate_player_report
from analytics.bowler_intelligence import get_bowler_intelligence
from analytics.advanced_intelligence import get_advanced_player_intelligence
from analytics.player_comparison import compare_players
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


app = Flask(__name__)

# =====================================
# LOAD DATA
# =====================================

df = pd.read_csv(
    "data/processed/ball_by_ball_clean.csv",
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

# =====================================
# HEAD-TO-HEAD
# =====================================

@app.route("/matchup", methods=["GET", "POST"])
def matchup():

    h2h_data = None
    batter = None
    bowler = None
    teams_list = sorted(df["bowling_team"].unique().tolist())

    if request.method == "POST":

        batter = request.form.get("batter")
        bowler = request.form.get("bowler")

        if batter and bowler:

            try:

                h2h_data = get_head_to_head(
                    df,
                    batter,
                    bowler
                )

            except Exception as e:

                print("MATCHUP ERROR:", e)

    return render_template(

        "matchup.html",

        players=players,

        teams=teams_list,

        h2h_data=h2h_data,

        batter=batter,

        bowler=bowler

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
# RUN
# =====================================

if __name__ == "__main__":
    app.run(debug=True)
