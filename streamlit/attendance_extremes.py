import json
import streamlit as st
import pandas as pd

st.set_page_config(page_title="MLB Attendance Extremes", layout="wide")

TEAM_DIVISIONS = {
    'NL West': ['LAD', 'SFG', 'SDP', 'ARI', 'COL'],
    'NL Central': ['CHC', 'CIN', 'STL', 'MIL', 'PIT'],
    'NL East': ['NYM', 'PHI', 'MIA', 'ATL', 'WSN'],
    'AL West': ['SEA', 'OAK', 'HOU', 'LAA', 'TEX'],
    'AL Central': ['CHW', 'CLE', 'DET', 'MIN', 'KCR'],
    'AL East': ['BOS', 'TBR', 'NYY', 'TOR', 'BAL']
}


@st.cache_data
def load_attendance_data() -> dict:
    """Load attendance data from JSON file."""
    with open('attendance_data.json', 'r') as f:
        return json.load(f)


def get_extremes_df(data: dict, year: str, extreme_type: str) -> pd.DataFrame:
    """Get dataframe of min or max attendance per team for a year."""
    rows = []
    year_data = data.get(year, {})
    
    for team, team_data in year_data.items():
        extreme = team_data.get(f'{extreme_type}_attendance', {})
        if extreme:
            rows.append({
                'Tm': team,
                'Date': extreme.get('date', ''),
                'Opp': extreme.get('opponent', ''),
                'Attendance': extreme.get('attendance', 0),
                'W/L': extreme.get('result', '')
            })
    
    df = pd.DataFrame(rows)
    if not df.empty:
        ascending = extreme_type == 'min'
        df = df.sort_values('Attendance', ascending=ascending)
    return df


st.title("MLB Attendance Extremes by Team")

try:
    data = load_attendance_data()
except FileNotFoundError:
    st.error("attendance_data.json not found. Run `python fetch_attendance_data.py` first.")
    st.stop()

available_years = sorted(data.keys(), reverse=True)
year = st.selectbox("Select Year", options=available_years, index=0)

lowest = get_extremes_df(data, year, 'min')
highest = get_extremes_df(data, year, 'max')

if lowest.empty or highest.empty:
    st.error("No data available for the selected year.")
    st.stop()

col1, col2 = st.columns(2)

with col1:
    st.subheader("Lowest Attendance Game per Team")
    
    chart_data_low = lowest[['Tm', 'Attendance']].copy()
    st.bar_chart(
        chart_data_low.set_index('Tm')['Attendance'],
        color='#d62728',
        horizontal=True
    )
    
    st.dataframe(
        lowest[['Tm', 'Date', 'Opp', 'Attendance', 'W/L']].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

with col2:
    st.subheader("Highest Attendance Game per Team")
    
    chart_data_high = highest[['Tm', 'Attendance']].copy()
    st.bar_chart(
        chart_data_high.set_index('Tm')['Attendance'],
        color='#2ca02c',
        horizontal=True
    )
    
    st.dataframe(
        highest[['Tm', 'Date', 'Opp', 'Attendance', 'W/L']].reset_index(drop=True),
        use_container_width=True,
        hide_index=True
    )

st.divider()

st.subheader("Attendance Range by Team")
range_df = pd.merge(
    lowest[['Tm', 'Attendance']].rename(columns={'Attendance': 'Min Attendance'}),
    highest[['Tm', 'Attendance']].rename(columns={'Attendance': 'Max Attendance'}),
    on='Tm'
)
range_df['Range'] = range_df['Max Attendance'] - range_df['Min Attendance']
range_df = range_df.sort_values('Range', ascending=False)

st.bar_chart(
    range_df.set_index('Tm')[['Min Attendance', 'Max Attendance']],
    horizontal=True
)

st.dataframe(
    range_df.reset_index(drop=True),
    use_container_width=True,
    hide_index=True
)

st.divider()

st.subheader("Average Attendance by Team")
avg_rows = []
for team, team_data in data.get(year, {}).items():
    avg_rows.append({
        'Tm': team,
        'Avg Attendance': team_data.get('avg_attendance', 0),
        'Total Games': team_data.get('total_games', 0)
    })
avg_df = pd.DataFrame(avg_rows).sort_values('Avg Attendance', ascending=False)

st.bar_chart(
    avg_df.set_index('Tm')['Avg Attendance'],
    color='#1f77b4',
    horizontal=True
)

st.dataframe(avg_df.reset_index(drop=True), use_container_width=True, hide_index=True)
