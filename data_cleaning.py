# import modules
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
pd.options.display.max_columns = None

matches = pd.read_csv('Dataset/IPL 2008-2025 Matches.csv')
matches.head(2)
matches.duplicated().sum()

# Check for unique values among this column and drop columns that you find are not needed
check_unique = ['match_type','event_name','ball','ball_no','over','valid_ball','runs_not_boundary','extra_type','wicket_kind',
                'umpires_call','match_number','gender','team_type','balls_per_over','overs','stage','result_type','superover_winner','method',
                ]

for i in check_unique:
  print(i,'=>\t',matches[i].unique(),end = '\n\n')

matches.drop(columns = ['Unnamed: 0','match_type','event_name','ball_no','gender','team_type','balls_per_over','overs','day',
                        'month','year','match_number','non_striker_pos','review_batter','umpires_call','umpire','new_batter',
                        'next_batter','striker_out' ],inplace = True)

df = matches.copy()
df.head()

# Rename Columns
df.rename(columns = {'batter':'striker',
                     'match_won_by': 'winning_team',
                     }, inplace = True)

# Rename Team names
rename_teams = {'Delhi Daredevils': 'Delhi Capitals',
                'Royal Challengers Bangalore':'Royal Challengers Bengaluru',
                'Rising Pune Supergiants': 'Rising Pune Supergiant',
                'Kings XI Punjab': 'Punjab Kings'
                }

df['batting_team'] = df['batting_team'].replace(rename_teams)
df['bowling_team'] = df['bowling_team'].replace(rename_teams)
df['winning_team'] = df['winning_team'].replace(rename_teams)
df['superover_winner'] = df['superover_winner'].replace(rename_teams)
df['toss_winner'] = df['toss_winner'].replace(rename_teams)


# Replace values of stage and season
df['stage'] = df['stage'].replace({'Unknown': 'League Stage',
                     'Elimination Final': 'Eliminator',
                     })

df['season'] = df['season'].replace({'2007/08' : 2008,
                      '2009/10': 2010,
                      '2020/21': 2020,
                      })
df['season'] = df['season'].astype(np.int32)

# this dataset was missing team players name so downloaded zip file from cricksheet and extracted the desired data and merged with existing dataframe
import zipfile
import json
data = {}

with zipfile.ZipFile('Dataset/ipl_male_json.zip','r') as zip_ref:
  zip_ref.extractall('Dataset/ipl')
  filenames = zip_ref.namelist()


a = {'team1':{},
      'team2':{}}
for name in filenames:
  with open('Dataset/ipl/{}'.format(name),'r') as rf:
    data = json.load(rf)
    team1 = data['info']['teams'][0]
    team2 = data['info']['teams'][1]

    match_id = int(name.split('.')[0])

    a['team1'][match_id] = data['info']['players'][team1]
    a['team2'][match_id] = data['info']['players'][team2]

team_players_df = pd.DataFrame(a)
team_players_df = team_players_df.reset_index().rename(columns = {'index':'match_id'})

# merge both dataframe
df = df.merge(team_players_df, how = 'outer',on = 'match_id')

# convert list to str
df['team1'] = df['team1'].apply(lambda x: ",".join(x))
df['team2'] = df['team2'].apply(lambda x: ",".join(x))

# convert to csv format and dump
df.to_csv('Dataset/ipl_matches_cleaned.csv',index = False)

