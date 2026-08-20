import pandas as pd
import base64
from datetime import datetime

def generate_report(df: pd.DataFrame, player: str, start_date: str = None, end_date: str = None, fmt: str = 'csv'):
    """Generate a simple player report filtered by optional date range.

    Args:
        df: Full ball‑by‑ball DataFrame.
        player: Player name (batter or bowler).
        start_date: ISO date string (inclusive) or None.
        end_date: ISO date string (inclusive) or None.
        fmt: Output format – currently only 'csv' is supported.

    Returns:
        dict with keys:
            - filename: suggested download name
            - content: base64‑encoded file bytes
            - mime: MIME type
    """
    filtered = df.copy()
    if start_date:
        filtered = filtered[filtered['date'] >= start_date]
    if end_date:
        filtered = filtered[filtered['date'] <= end_date]

    if player in filtered['batter'].values:
        player_df = filtered[filtered['batter'] == player]
    elif player in filtered['bowler'].values:
        player_df = filtered[filtered['bowler'] == player]
    else:
        player_df = pd.DataFrame()

    if fmt == 'csv':
        csv_bytes = player_df.to_csv(index=False).encode('utf-8')
        b64 = base64.b64encode(csv_bytes).decode('utf-8')
        filename = f"{player}_report_{datetime.now().strftime('%Y%m%d')}.csv"
        return {'filename': filename, 'content': b64, 'mime': 'text/csv'}
    raise ValueError('Unsupported format')
