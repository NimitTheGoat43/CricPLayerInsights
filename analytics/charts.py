import plotly.express as px


def runs_by_season_chart(df, player):

    player_df = df[df["batter"] == player]

    if player_df.empty:
        return None

    season_runs = (

        player_df

        .groupby("season")["runs"]

        .sum()

        .reset_index()

    )

    fig = px.line(

        season_runs,

        x="season",

        y="runs",

        markers=True,

        title=f"{player} - Runs by Season"

    )

    fig.update_layout(

        template="plotly_white",

        title_x=0.5,

        height=450,

        xaxis_title="Season",

        yaxis_title="Runs"

    )

    return fig.to_html(
        full_html=False
    )