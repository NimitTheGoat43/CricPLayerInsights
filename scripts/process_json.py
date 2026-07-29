import json
import pandas as pd
import os

rows = []

folder = "data/raw_json"

for file in os.listdir(folder):

    if not file.endswith(".json"):
        continue

    with open(
        os.path.join(folder, file),
        encoding="utf-8"
    ) as f:

        match = json.load(f)

    match_id = file.replace(".json", "")

    season = match["info"].get(
        "season",
        "Unknown"
    )

    venue = match["info"].get(
        "venue",
        "Unknown"
    )

    innings = match["innings"]

    for inning in innings:

        batting_team = inning["team"]

        teams = match["info"]["teams"]

        bowling_team = [
            t for t in teams
            if t != batting_team
        ][0]

        for over_data in inning["overs"]:

            over_num = over_data["over"]

            for delivery in over_data["deliveries"]:

                batter = delivery["batter"]

                bowler = delivery["bowler"]

                runs = delivery["runs"]["batter"]

                total_runs = delivery["runs"]["total"]

                wicket = 0

                player_dismissed = ""

                dismissal_kind = ""

                if "wickets" in delivery:

                    wicket = len(
                        delivery["wickets"]
                    )

                    player_dismissed = (
                        delivery["wickets"][0]
                        .get(
                            "player_out",
                            ""
                        )
                    )

                    dismissal_kind = (
                        delivery["wickets"][0]
                        .get(
                            "kind",
                            ""
                        )
                    )

                rows.append({

                    "match_id":
                    match_id,

                    "season":
                    season,

                    "venue":
                    venue,

                    "batting_team":
                    batting_team,

                    "bowling_team":
                    bowling_team,

                    "over":
                    over_num,

                    "batter":
                    batter,

                    "bowler":
                    bowler,

                    "runs":
                    runs,

                    "total_runs":
                    total_runs,

                    "wicket":
                    wicket,

                    "player_dismissed":
                    player_dismissed,

                    "dismissal_kind":
                    dismissal_kind

                })

df = pd.DataFrame(rows)

os.makedirs(
    "data/processed",
    exist_ok=True
)

df.to_csv(
    "data/processed/ball_by_ball.csv",
    index=False
)

print("\nDATASET CREATED SUCCESSFULLY")

print("\nROWS:")
print(len(df))

print("\nCOLUMNS:")
print(df.columns.tolist())

print("\nSAMPLE:")
print(df.head())