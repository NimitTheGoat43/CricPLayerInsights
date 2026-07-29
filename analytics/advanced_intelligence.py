import pandas as pd


def _score(value, low, high, reverse=False):
    if high == low:
        return 50

    scaled = ((value - low) / (high - low)) * 100
    scaled = max(0, min(100, scaled))

    if reverse:
        scaled = 100 - scaled

    return round(scaled, 2)


def _level(score):
    if score >= 75:
        return "Elite"
    if score >= 55:
        return "Strong"
    if score >= 35:
        return "Developing"
    return "Needs Attention"


def _empty_frame(columns):
    return pd.DataFrame(columns=columns)


def _has_meaningful_batting(batting_summary):
    return (
        batting_summary is not None
        and (
            batting_summary["runs"] >= 100
            or batting_summary["balls"] >= 100
        )
    )


def _has_meaningful_bowling(bowling_summary):
    return (
        bowling_summary is not None
        and bowling_summary["overs"] >= 100
        and bowling_summary["wickets"] >= 25
    )


def get_advanced_player_intelligence(df, player):
    batting_df = df[df["batter"] == player]
    bowling_df = df[df["bowler"] == player]

    if batting_df.empty and bowling_df.empty:
        return None

    batting_summary = _get_batting_summary(df, batting_df, player)
    bowling_summary = _get_bowling_summary(df, bowling_df, player)
    has_meaningful_batting = _has_meaningful_batting(batting_summary)
    has_meaningful_bowling = _has_meaningful_bowling(bowling_summary)

    if not has_meaningful_batting:
        batting_summary = None
        batting_df = batting_df.iloc[0:0]

    if not has_meaningful_bowling:
        bowling_summary = None
        bowling_df = bowling_df.iloc[0:0]

    role = _classify_role(batting_summary, bowling_summary)
    phase_edge = _get_phase_edge(batting_df, bowling_df)
    strengths = _get_strengths(batting_summary, bowling_summary, phase_edge)
    risks = _get_risks(batting_summary, bowling_summary, phase_edge)
    recommendations = _get_recommendations(role, strengths, risks, phase_edge)

    batting_score = batting_summary["score"] if batting_summary else 0
    bowling_score = bowling_summary["score"] if bowling_summary else 0

    if batting_summary and bowling_summary:
        overall_score = round((batting_score * 0.55) + (bowling_score * 0.45), 2)
    else:
        overall_score = max(batting_score, bowling_score)

    return {
        "player": player,
        "role": role,
        "overall_score": overall_score,
        "overall_level": _level(overall_score),
        "batting": batting_summary,
        "bowling": bowling_summary,
        "phase_edge": phase_edge,
        "strengths": strengths,
        "risks": risks,
        "recommendations": recommendations,
        "explanation": (
            "Scores are normalized within the currently selected dataset. "
            "Batting rewards runs, strike rate, average, boundary rate, and consistency. "
            "Bowling rewards wickets, economy control, dot-ball rate, and bowling strike rate."
        ),
    }


def _get_batting_summary(df, batting_df, player):
    if batting_df.empty:
        return None

    player_outs = batting_df["player_dismissed"].fillna("").eq(player).sum()
    runs = int(batting_df["runs"].sum())
    balls = int(len(batting_df))
    matches = int(batting_df["match_id"].nunique())
    strike_rate = round((runs / balls) * 100, 2) if balls else 0
    average = round(runs / player_outs, 2) if player_outs else runs
    boundary_rate = round((batting_df["runs"].ge(4).sum() / balls) * 100, 2) if balls else 0
    dot_rate = round((batting_df["runs"].eq(0).sum() / balls) * 100, 2) if balls else 0

    batter_pool = (
        df.groupby("batter")
        .agg(
            runs=("runs", "sum"),
            balls=("runs", "count"),
            matches=("match_id", "nunique"),
        )
        .reset_index()
    )
    batter_pool = batter_pool[batter_pool["balls"] >= 50].copy()
    batter_pool["strike_rate"] = (batter_pool["runs"] / batter_pool["balls"]) * 100

    dismissals = (
        df[df["player_dismissed"].fillna("") != ""]
        .groupby("player_dismissed")
        .size()
        .reset_index(name="outs")
        .rename(columns={"player_dismissed": "batter"})
    )
    batter_pool = batter_pool.merge(dismissals, on="batter", how="left")
    batter_pool["outs"] = batter_pool["outs"].fillna(0)
    batter_pool["average"] = batter_pool.apply(
        lambda row: row["runs"] / row["outs"] if row["outs"] else row["runs"],
        axis=1,
    )

    run_score = _score(runs, batter_pool["runs"].min(), batter_pool["runs"].max())
    sr_score = _score(
        strike_rate,
        batter_pool["strike_rate"].min(),
        batter_pool["strike_rate"].max(),
    )
    avg_score = _score(
        average,
        batter_pool["average"].min(),
        batter_pool["average"].max(),
    )
    boundary_score = _score(boundary_rate, 5, 25)
    dot_score = _score(dot_rate, 25, 60, reverse=True)

    match_runs = (
        batting_df.groupby("match_id")
        .agg(runs=("runs", "sum"))
        .reset_index()
    )
    consistency = _consistency_from_series(match_runs["runs"])

    score = round(
        (run_score * 0.25)
        + (sr_score * 0.25)
        + (avg_score * 0.2)
        + (boundary_score * 0.15)
        + (dot_score * 0.15),
        2,
    )

    return {
        "runs": runs,
        "balls": balls,
        "matches": matches,
        "strike_rate": strike_rate,
        "average": average,
        "boundary_rate": boundary_rate,
        "dot_rate": dot_rate,
        "consistency": consistency,
        "score": score,
        "level": _level(score),
    }


def _get_bowling_summary(df, bowling_df, player):
    if bowling_df.empty:
        return None

    wickets = int(bowling_df["wicket"].sum())
    balls = int(len(bowling_df))
    overs = round(balls / 6, 1)
    runs = int(bowling_df["total_runs"].sum())
    economy = round(runs / (balls / 6), 2) if balls else 0
    bowling_sr = round(balls / wickets, 2) if wickets else 0
    dot_rate = round((bowling_df["runs"].eq(0).sum() / balls) * 100, 2) if balls else 0
    boundary_rate = round((bowling_df["runs"].ge(4).sum() / balls) * 100, 2) if balls else 0
    matches = int(bowling_df["match_id"].nunique())

    bowler_pool = (
        df.groupby("bowler")
        .agg(
            wickets=("wicket", "sum"),
            runs=("total_runs", "sum"),
            balls=("runs", "count"),
        )
        .reset_index()
    )
    bowler_pool["overs"] = bowler_pool["balls"] / 6
    bowler_pool = bowler_pool[bowler_pool["overs"] >= 10].copy()
    bowler_pool["economy"] = bowler_pool["runs"] / bowler_pool["overs"]
    bowler_pool["bowling_sr"] = bowler_pool.apply(
        lambda row: row["balls"] / row["wickets"] if row["wickets"] else row["balls"],
        axis=1,
    )

    wicket_score = _score(wickets, bowler_pool["wickets"].min(), bowler_pool["wickets"].max())
    economy_score = _score(
        economy,
        bowler_pool["economy"].min(),
        bowler_pool["economy"].max(),
        reverse=True,
    )
    sr_score = _score(
        bowling_sr,
        bowler_pool["bowling_sr"].min(),
        bowler_pool["bowling_sr"].max(),
        reverse=True,
    )
    dot_score = _score(dot_rate, 25, 60)
    boundary_control = _score(boundary_rate, 5, 25, reverse=True)

    match_economy = (
        bowling_df.groupby("match_id")
        .agg(runs=("total_runs", "sum"), balls=("runs", "count"))
        .reset_index()
    )
    match_economy["economy"] = match_economy["runs"] / (match_economy["balls"] / 6)
    consistency = _consistency_from_series(match_economy["economy"], reverse=True)

    score = round(
        (wicket_score * 0.3)
        + (economy_score * 0.25)
        + (sr_score * 0.2)
        + (dot_score * 0.15)
        + (boundary_control * 0.1),
        2,
    )

    return {
        "wickets": wickets,
        "overs": overs,
        "matches": matches,
        "economy": economy,
        "bowling_sr": bowling_sr,
        "dot_rate": dot_rate,
        "boundary_rate": boundary_rate,
        "consistency": consistency,
        "score": score,
        "level": _level(score),
    }


def _consistency_from_series(series, reverse=False):
    if len(series) < 2 or series.mean() == 0:
        return 0

    cv = series.std() / series.mean()
    score = max(0, min(100, 100 - (cv * 50)))

    if reverse:
        score = max(0, min(100, score))

    return round(score, 2)


def _classify_role(batting, bowling):
    if batting and bowling:
        diff = batting["score"] - bowling["score"]

        if (
            batting["score"] >= 45
            and bowling["score"] >= 45
        ):
            if abs(diff) <= 12:
                return "Balanced All-Rounder"
            if diff > 12:
                return "Batting All-Rounder"
            return "Bowling All-Rounder"

        if batting["score"] >= bowling["score"]:
            return "Batting All-Rounder"
        return "Bowling All-Rounder"

    if batting:
        if batting["strike_rate"] >= 140:
            return "Aggressive Batter"
        if batting["average"] >= 30:
            return "Anchor Batter"
        return "Specialist Batter"

    if bowling:
        if bowling["economy"] <= 7.5:
            return "Control Bowler"
        if bowling["bowling_sr"] <= 18:
            return "Wicket-Taking Bowler"
        return "Specialist Bowler"

    return "Unknown"


def _get_phase_edge(batting_df, bowling_df):
    rows = []

    if not batting_df.empty:
        rows.extend(_phase_rows(batting_df, "Batting"))

    if not bowling_df.empty:
        rows.extend(_phase_rows(bowling_df, "Bowling"))

    if not rows:
        return _empty_frame(["skill", "phase", "balls", "runs", "metric"])

    return pd.DataFrame(rows)


def _phase_rows(player_df, skill):
    phases = [
        ("Powerplay", player_df[player_df["over"] <= 5]),
        ("Middle Overs", player_df[(player_df["over"] >= 6) & (player_df["over"] <= 15)]),
        ("Death Overs", player_df[player_df["over"] >= 16]),
    ]

    rows = []
    for phase, data in phases:
        balls = len(data)
        runs_column = "runs" if skill == "Batting" else "total_runs"
        runs = int(data[runs_column].sum()) if balls else 0

        if skill == "Batting":
            metric = round((runs / balls) * 100, 2) if balls else 0
        else:
            metric = round(runs / (balls / 6), 2) if balls else 0

        rows.append(
            {
                "skill": skill,
                "phase": phase,
                "balls": balls,
                "runs": runs,
                "metric": metric,
            }
        )

    return rows


def _get_strengths(batting, bowling, phase_edge):
    strengths = []

    if batting and batting["score"] >= 55:
        strengths.append(
            f"Batting output is {_level(batting['score']).lower()} with {batting['runs']} runs at {batting['strike_rate']} strike rate."
        )
    if batting and batting["boundary_rate"] >= 15:
        strengths.append(
            f"Boundary conversion is strong: {batting['boundary_rate']}% of balls faced go for four or more."
        )
    if bowling and bowling["score"] >= 55:
        strengths.append(
            f"Bowling impact is {_level(bowling['score']).lower()} with {bowling['wickets']} wickets and {bowling['economy']} economy."
        )
    if bowling and bowling["dot_rate"] >= 40:
        strengths.append(
            f"Dot-ball pressure is high: {bowling['dot_rate']}% dot balls while bowling."
        )

    if not phase_edge.empty:
        batting_rows = phase_edge[phase_edge["skill"] == "Batting"]
        if not batting_rows.empty:
            best = batting_rows.sort_values("metric", ascending=False).iloc[0]
            strengths.append(
                f"Best batting phase is {best['phase']} with a phase strike rate of {best['metric']}."
            )

        bowling_rows = phase_edge[phase_edge["skill"] == "Bowling"]
        if not bowling_rows.empty:
            best = bowling_rows[bowling_rows["balls"] > 0].sort_values("metric").head(1)
            if not best.empty:
                row = best.iloc[0]
                strengths.append(
                    f"Best bowling phase is {row['phase']} with phase economy of {row['metric']}."
                )

    return strengths[:5]


def _get_risks(batting, bowling, phase_edge):
    risks = []

    if batting and batting["dot_rate"] >= 45:
        risks.append(
            f"High dot-ball percentage while batting ({batting['dot_rate']}%) can slow innings momentum."
        )
    if batting and batting["average"] < 20 and batting["matches"] >= 5:
        risks.append(
            f"Batting average is below 20, so dismissal resistance is an improvement area."
        )
    if bowling and bowling["economy"] >= 9:
        risks.append(
            f"Economy rate of {bowling['economy']} suggests run control can be improved."
        )
    if bowling and bowling["boundary_rate"] >= 18:
        risks.append(
            f"Boundary percentage conceded is {bowling['boundary_rate']}%, which can hurt in pressure overs."
        )

    if not phase_edge.empty:
        bowling_rows = phase_edge[
            (phase_edge["skill"] == "Bowling") & (phase_edge["balls"] >= 12)
        ]
        if not bowling_rows.empty:
            worst = bowling_rows.sort_values("metric", ascending=False).iloc[0]
            if worst["metric"] >= 10:
                risks.append(
                    f"Bowling is most expensive in {worst['phase']} with economy {worst['metric']}."
                )

    if not risks:
        risks.append("No major red flags from the selected data; monitor role-specific consistency.")

    return risks[:5]


def _get_recommendations(role, strengths, risks, phase_edge):
    recommendations = []

    if "All-Rounder" in role:
        recommendations.append(
            "Use this player as a balance option because both batting and bowling have measurable value."
        )
    elif "Batter" in role:
        recommendations.append(
            "Use this player primarily for batting role clarity; bowling value is secondary or unavailable."
        )
    elif "Bowler" in role:
        recommendations.append(
            "Use this player primarily as a bowling specialist; batting value is secondary or unavailable."
        )

    if not phase_edge.empty:
        batting_rows = phase_edge[phase_edge["skill"] == "Batting"]
        if not batting_rows.empty:
            best_batting = batting_rows.sort_values("metric", ascending=False).iloc[0]
            recommendations.append(
                f"Batting deployment: maximize balls in {best_batting['phase']} where the scoring rate is strongest."
            )

        bowling_rows = phase_edge[(phase_edge["skill"] == "Bowling") & (phase_edge["balls"] > 0)]
        if not bowling_rows.empty:
            best_bowling = bowling_rows.sort_values("metric").iloc[0]
            recommendations.append(
                f"Bowling deployment: prefer {best_bowling['phase']} because economy is best there."
            )

    if risks:
        recommendations.append(
            "Training focus: prioritize the listed risk area with the clearest match impact."
        )

    return recommendations[:4]
