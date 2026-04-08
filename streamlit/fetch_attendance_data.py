import json
import warnings
import pandas as pd
from pybaseball import schedule_and_record
from tqdm import tqdm

# Disable Copy-on-Write to work around pybaseball compatibility issue with pandas 2.0+
pd.options.mode.copy_on_write = False
warnings.filterwarnings('ignore', category=FutureWarning)

MIN_YEAR = 2011
MAX_YEAR = 2024


def load_team_data() -> dict:
    """Load team data from JSON file."""
    with open('team_data.json', 'r') as f:
        return json.load(f)


def get_teams_with_start_years(team_data: dict) -> dict:
    """Extract team abbreviations and start years from team data."""
    teams = {}
    for division, division_teams in team_data.items():
        for team_abbr, team_info in division_teams.items():
            teams[team_abbr] = team_info.get('start_year', MIN_YEAR)
    return teams


def fetch_team_year_attendance(team: str, year: int) -> list[dict]:
    """Fetch home game attendance for a team in a given year."""
    try:
        df = schedule_and_record(year, team)
        df = df[df['Home_Away'] == 'Home']
        df['Attendance'] = pd.to_numeric(df['Attendance'], errors='coerce')
        df = df[df['Attendance'].notna()]
        
        records = []
        for _, row in df.iterrows():
            records.append({
                'date': str(row.get('Date', '')),
                'opponent': row.get('Opp', ''),
                'attendance': int(row['Attendance']),
                'result': row.get('W/L', '')
            })
        return records
    except Exception as e:
        print(f"  Error fetching {team} {year}: {e}")
        return []


def fetch_all_attendance_data(teams_with_start_years: dict) -> dict:
    """Fetch attendance data for all teams and years."""
    data = {}
    teams = list(teams_with_start_years.keys())
    
    for year in range(MIN_YEAR, MAX_YEAR + 1):
        print(f"\nFetching {year}...")
        data[year] = {}
        
        for team in tqdm(teams, desc=f"  {year}"):
            start_year = teams_with_start_years[team]
            if year < start_year:
                continue
                
            records = fetch_team_year_attendance(team, year)
            if records:
                attendances = [r['attendance'] for r in records]
                min_idx = attendances.index(min(attendances))
                max_idx = attendances.index(max(attendances))
                
                data[year][team] = {
                    'games': records,
                    'min_attendance': records[min_idx],
                    'max_attendance': records[max_idx],
                    'avg_attendance': int(sum(attendances) / len(attendances)),
                    'total_games': len(records)
                }
    
    return data


def main():
    print("Loading team data from team_data.json...")
    team_data = load_team_data()
    teams_with_start_years = get_teams_with_start_years(team_data)
    
    print(f"Found {len(teams_with_start_years)} teams:")
    for team, start_year in sorted(teams_with_start_years.items()):
        print(f"  {team}: started {start_year}")
    
    print("\nFetching MLB attendance data...")
    data = fetch_all_attendance_data(teams_with_start_years)
    
    output_file = 'attendance_data.json'
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\nData saved to {output_file}")
    
    total_teams = sum(len(teams) for teams in data.values())
    print(f"Total team-years fetched: {total_teams}")


if __name__ == '__main__':
    main()
