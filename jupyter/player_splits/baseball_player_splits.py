import pybaseball
import pandas as pd
from pybaseball import batting_stats_bref, get_splits, playerid_lookup, chadwick_register
pd.options.mode.chained_assignment = None  # default='warn'

players = chadwick_register()
players = players[players['mlb_played_last'] >= 1997]

data = pd.DataFrame()

for x in players['key_bbref']:
    try:
        df = get_splits(x).loc['Opponent'].iloc[1:-2]
        df = df[(df['AB'] >= 100) & (df['tOPS+'] > 100)]
        df['player_id'] = x
        if len(df) > 0:
            df['player_id'] = x
            data = pd.concat([data,df])
    except:
        continue

data.to_csv('baseball_team_killers2.csv')
# Saving a fresh copy

data2 = data
data2 = pd.merge(left=data2.reset_index()
                 ,right=players[['name_last','name_first','key_bbref','mlb_played_first','mlb_played_last']]
                 ,how='left'
                 ,left_on='player_id'
                 ,right_on='key_bbref')
data2['Player Name'] = data2['name_first'] + ' ' + data2['name_last']

data2.to_csv('baseball_team_killers_clean2.csv')