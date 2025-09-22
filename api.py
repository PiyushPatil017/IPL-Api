# here Api  is developed which will be sent to app.py in json format

import numpy as np
import pandas as pd
import json
import re

df = pd.read_csv('Dataset/ipl_matches_cleaned.csv')

# replace Player name which are doubles
def replace_player(data):
  replacement = {'Arshad Khan (2)':'Arshad Khan' , 'Virat Kohli': 'V Kohli', 'Anureet Singh':'A Singh', 'Kuldeep Yadav': 'K Yadav' ,'Navdeep Saini':'N Saini'}
  for old_word,new_word in replacement.items():
    data = re.sub(r'{}'.format(old_word),'{}'.format(new_word),data)
  return data
df['team1'] = df['team1'].apply(replace_player)
df['team2'] = df['team2'].apply(replace_player)

# conver team1 and team2 column to list dtype
df['team1'] = df['team1'].apply(lambda x: x.split(','))
df['team2'] = df['team2'].apply(lambda x: x.split(','))
df['season'] = df['season'].astype('string')
df['date'] = pd.to_datetime(df['date'])

# hometown ground of teams
ipl_teams_hometowns = {
    "Chennai Super Kings": "Chennai",
    "Mumbai Indians": "Mumbai",
    "Kolkata Knight Riders": "Kolkata",
    "Royal Challengers Bengaluru": "Bengaluru",
    "Rajasthan Royals": "Jaipur",
    "Sunrisers Hyderabad": "Hyderabad",
    "Delhi Capitals": "Delhi",
    "Punjab Kings": "Mohali",
    "Lucknow Super Giants": "Lucknow",
    "Gujarat Titans": "Ahmedabad",

    # Former Teams
    "Deccan Chargers": "Hyderabad",
    "Pune Warriors India": "Pune",
    "Rising Pune Supergiant": "Pune",
    "Kochi Tuskers Kerala": "Kochi",
    "Gujarat Lions": "Rajkot, Gujarat"
}


# convert obj from np type to normal type
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super(NpEncoder, self).default(obj)


# returns seasons
def season_name_api():
    seasons = sorted(df['season'].unique())
    return json.dumps(seasons, cls = NpEncoder, indent = 4)

#returns team name
def team_name_api():
    teams = sorted(df['batting_team'].unique())
    return json.dumps(teams, cls = NpEncoder, indent =4)

# returns player names
def player_name_api():
    with open('players_names.json','r') as rf:
        response = json.load(rf)
        response = sorted(response.keys())
    return json.dumps(response, cls = NpEncoder, indent = 4)

# returns team record
def team_api(team):
    temp_df = df[(df['bowling_team'] == team) | (df['batting_team'] == team)].groupby('match_id').tail(1)

    # Overall record of team
    total_match = temp_df.shape[0]
    total_win = temp_df[(temp_df['winning_team'] == team) | (temp_df['superover_winner'] == team)]['winning_team'].count()
    total_draw = temp_df[temp_df['result_type'] == 'no result']['result_type'].count()
    total_loss = total_match - total_win - total_draw
    trophy = temp_df[(temp_df['stage'] == 'Final') & (temp_df['winning_team'] == team)]['winning_team'].count()
    trophy_year = temp_df[(temp_df['stage'] == 'Final') & (temp_df['winning_team'] == team)]['season'].values.tolist()
    trophy_year = ",".join(trophy_year)

    team_overall_dict = {'Overall': {'Total Match': total_match,
                                     'Total Win': total_win,
                                     'Total Loss': total_loss,
                                     'Total Draw': total_draw,
                                     'Trophys': trophy,
                                     'trophy_years':trophy_year}
                         }
    # Season wise record of team
    team_season_dict = {season: {} for season in temp_df['season'].unique()}
    for season in team_season_dict:
        team_season_dict[season]['Matches'] = temp_df[temp_df['season'] == season]['batting_team'].count()
        team_season_dict[season]['Won'] = temp_df[(temp_df['season'] == season) & ((temp_df['winning_team'] == team) | (temp_df['superover_winner'] == team))]['winning_team'].count()
        team_season_dict[season]['Draw'] = temp_df[(temp_df['season'] == season) & (temp_df['result_type'] == 'no result')]['result_type'].count()
        team_season_dict[season]['Loss'] = team_season_dict[season]['Matches'] - team_season_dict[season]['Won'] - team_season_dict[season]['Draw']

    team_overall_dict['Season'] = team_season_dict

    return json.dumps(team_overall_dict, cls=NpEncoder, indent=4)

# returns team vs team record
def team_vs_team_api(team1,team2):

    temp_df = df[df['batting_team'].isin([team1, team2]) & (df['bowling_team'].isin([team1, team2]))].groupby('match_id').tail(1)

    # overall win
    win_team1 = temp_df[(temp_df['winning_team'] == team1) | (temp_df['superover_winner'] == team1)]['winning_team'].count()
    win_team2 = temp_df[(temp_df['winning_team'] == team2) | (temp_df['superover_winner'] == team2)]['winning_team'].count()

    # Win in hometown of team1
    city1 = ipl_teams_hometowns[team1]
    city1_team1 = temp_df[(temp_df['city'] == city1) &((temp_df['winning_team'] == team1) | (temp_df['superover_winner'] == team1))]['winning_team'].count()
    city1_team2 = temp_df[(temp_df['city'] == city1) &((temp_df['winning_team'] == team2) | (temp_df['superover_winner'] == team2))]['winning_team'].count()

    # win in homwtown of team2
    city2 = ipl_teams_hometowns[team2]
    city2_team1 = temp_df[(temp_df['city'] == city2) &((temp_df['winning_team'] == team1) | (temp_df['superover_winner'] == team1))]['winning_team'].count()
    city2_team2 = temp_df[(temp_df['city'] == city2) &((temp_df['winning_team'] == team2) | (temp_df['superover_winner'] == team2))]['winning_team'].count()

    # win in neutral venue
    neutral_team1 = temp_df[(~temp_df['city'].isin([city1,city2])) &((temp_df['winning_team'] == team1) | (temp_df['superover_winner'] == team1))]['winning_team'].count()
    neutral_team2 = temp_df[(~temp_df['city'].isin([city1,city2])) &((temp_df['winning_team'] == team2) | (temp_df['superover_winner'] == team2))]['winning_team'].count()

    team_vs_team_dict = {team1:{'Won':win_team1,
                              'In {}'.format(city1):city1_team1,
                              'In {}'.format(city2): city2_team1,
                              'In Neutral':neutral_team1},
                      team2:{'Won':win_team2,
                              'In {}'.format(city1):city1_team2,
                              'In {}'.format(city2): city2_team2,
                              'In Neutral':neutral_team2}
                      }
    return json.dumps(team_vs_team_dict, cls = NpEncoder, indent = 4)

# returns player vs team record
def player_vs_team_api(player):
    pass

# Player Season-wise and Overall Record
def player_record_api(player):
    seasons = sorted(df['season'].unique())
    player_season_dict = {"Player":player,
                        'Batting':{'Season':{season:{} for season in seasons}
                                   },
                        'Bowling':{'Season':{season:{} for season in seasons}
                                   },
                        'Overall Record':{'Batting':{},
                                          'Bowling':{}
                                          }
                        }

    # Batting Record
    # Player Batting Record Season Wise
    # match in each season
    match_each_season = df[(df['team1'].apply(lambda player_list: player in player_list)) | (df['team2'].apply(lambda player_list: player in player_list))].groupby('season')['match_id'].nunique()
    # runs in each season
    runs_each_season = df[(df['striker'] == player) & (df['innings'] < 3)].groupby('season')['runs_batter'].sum()
    # 100s each season
    hundreds_each_season = df[(df['striker'] == player) & (df['batter_runs'] >=100)].groupby('season')['date'].nunique()
    # 50s each season
    fifty_each_season = df[(df['striker'] == player) & (df['batter_runs'] >=50)].groupby('season')['date'].nunique() - hundreds_each_season
    # Highest Score in each season
    highest_each_season = df[(df['striker'] == player) & (df['innings'] < 3)].groupby('season')['batter_runs'].max()
    # 4s and 6s in each season
    fours_each_season = df[(df['striker'] == player) & (df['innings'] < 3) & (df['runs_batter'] == 4)].groupby('season')['batter_runs'].count()
    sixs_each_season = df[(df['striker'] == player) & (df['innings'] < 3) & (df['runs_batter'] == 6)].groupby('season')['batter_runs'].count()
    # balls faced in each season
    balls_each_season = df[(df['striker'] == player) & (df['innings'] < 3)].groupby('season')['balls_faced'].sum()
    # out rate in each season
    out_each_season = df[(df['striker'] == player) & (df['innings'] < 3) & (df['player_out'] == player)].groupby('season')['match_id'].count()


    # loop within seasons variable and add details for that season within player_season_dict['Season']
    for season in seasons:
        # Matches played in each season
        player_season_dict['Batting']['Season'][season]['Matches'] = match_each_season[season]
        # Runs scored in each season
        player_season_dict['Batting']['Season'][season]['Runs'] = runs_each_season[season]
        # hundreds Scored
        player_season_dict['Batting']['Season'][season]['100s'] = hundreds_each_season[season]
        # Fiftys Scored
        player_season_dict['Batting']['Season'][season]['50s'] = fifty_each_season[season]
        # highest score
        player_season_dict['Batting']['Season'][season]['Highest Score'] = highest_each_season[season]
        # 4s and 6s
        player_season_dict['Batting']['Season'][season]['4s'] = fours_each_season[season]
        player_season_dict['Batting']['Season'][season]['6s'] = sixs_each_season[season]
        # balls faced
        player_season_dict['Batting']['Season'][season]['Balls Faced'] = balls_each_season[season]
        # Strike Rate
        player_season_dict['Batting']['Season'][season]['Strike Rate'] = round(((runs_each_season[season]/balls_each_season[season]) *100),2)
        # Batting Average
        player_season_dict['Batting']['Season'][season]['Average'] = round((runs_each_season[season]/out_each_season[season]),2)


    # Batting Overall Record
    # Total matches played by player in his entire IPL carrer
    player_season_dict['Overall Record']['Batting']['Matches'] = match_each_season.sum()
    # Total runs scored by player in his entire IPL carrer
    player_season_dict['Overall Record']['Batting']['Runs'] = runs_each_season.sum()
    # Total 100s scored by player in his entire IPL carrer
    player_season_dict['Overall Record']['Batting']['100s'] = hundreds_each_season.sum()
    # Total 50s scored by player in his entire IPL carrer
    player_season_dict['Overall Record']['Batting']['50s'] = fifty_each_season.sum()
    # Highest Score in IPL carrer
    player_season_dict['Overall Record']['Batting']['Highest Score'] = highest_each_season.max()
    # Total 4s and 6s hit by player in his entire IPL carrer
    player_season_dict['Overall Record']['Batting']['4s'] = fours_each_season.sum()
    player_season_dict['Overall Record']['Batting']['6s'] = sixs_each_season.sum()
    # Total balls faced by player in his entire IPL carrer
    player_season_dict['Overall Record']['Batting']['Balls Faced'] = balls_each_season.sum()
    # Strike Rate in IPL carrer
    player_season_dict['Overall Record']['Batting']['Strike Rate'] = round(((runs_each_season.sum()/balls_each_season.sum()) *100),2)
    # Batting Average
    player_season_dict['Overall Record']['Batting']['Average'] = round((runs_each_season.sum()/out_each_season.sum()),2)



    # Bowling Record
    # Player Bowling Record Season Wise
    # match in each season
    match_each_season = df[(df['team1'].apply(lambda player_list: player in player_list)) | (df['team2'].apply(lambda player_list: player in player_list))].groupby('season')['match_id'].nunique()
    # Balls Delivered each season
    balls_delivered_each_season = df[(df['bowler'] == player) & (df['valid_ball'] == 1) & (df['innings'] <3)].groupby('season')['balls_faced'].sum()
    # Runs Conceded each season
    runs_bowler_each_season = df[(df['bowler'] == player) & (df['innings'] <3)].groupby('season')['runs_bowler'].sum()
    # wickets taken each season
    wicket_each_season = df[(df['bowler'] == player) & (df['innings'] < 3)].groupby('season')['bowler_wicket'].sum()


    for season in seasons:
        # Matches played in each season
        player_season_dict['Bowling']['Season'][season]['Matches'] = match_each_season[season]
        # Balls Delivered
        player_season_dict['Bowling']['Season'][season]['Balls'] = balls_delivered_each_season[season]
        # Runs Conceded
        player_season_dict['Bowling']['Season'][season]['Runs'] = runs_bowler_each_season[season]
        # Wickets Taken
        player_season_dict['Bowling']['Season'][season]['Wicket'] = wicket_each_season[season]
        # Bowling Average
        player_season_dict['Bowling']['Season'][season]['Average'] = round((runs_bowler_each_season[season] / wicket_each_season[season]),2)
        # Bowling Economy
        temp_df = df[(df['bowler'] == player) & (df['innings'] <3) & (df['season'] == season)].groupby('match_id')['over'].unique()
        overs_bowled = temp_df.apply(lambda x: len(x)).sum()
        player_season_dict['Bowling']['Season'][season]['Economy'] = runs_bowler_each_season[season] / overs_bowled
        # Bowling Strike Rate
        player_season_dict['Bowling']['Season'][season]['Strike Rate'] = round((balls_delivered_each_season[season] / wicket_each_season[season])*100,2)
        # 4 Wicket Haul each season
        temp_df = df[(df['bowler'] == player) & (df['bowler_wicket'] == 1) & (df['innings'] <3) & (df['season'] == season)].groupby('match_id')['bowler_wicket'].sum()
        player_season_dict['Bowling']['Season'][season]['4W'] = temp_df[temp_df == 4].count()
        # 5 Wicket Haul each season
        temp_df = df[(df['bowler'] == player) & (df['bowler_wicket'] == 1) & (df['innings'] <3) & (df['season'] == season)].groupby('match_id')['bowler_wicket'].sum()
        player_season_dict['Bowling']['Season'][season]['5W'] = temp_df[temp_df >= 5].count()


    # Bowling Overall Record
    # Total matches played by player in his entire IPL carrer
    player_season_dict['Overall Record']['Bowling']['Matches'] = match_each_season.sum()
    # Total Balls Delivered in IPL carrer
    player_season_dict['Overall Record']['Bowling']['Balls'] = balls_delivered_each_season.sum()
    # Total Runs Conceded in IPL carrer
    player_season_dict['Overall Record']['Bowling']['Runs'] = runs_bowler_each_season.sum()
    # Total wicket taken by player in his entire IPL carrer
    player_season_dict['Overall Record']['Bowling']['Wickets'] = wicket_each_season.sum()
    # Bowling Average in IPL carrer
    player_season_dict['Overall Record']['Bowling']['Average'] = round((runs_bowler_each_season.sum() / wicket_each_season.sum()),2)
    # Bowling Economy in IPL carrer
    temp_df = df[(df['bowler'] == player) & (df['innings'] <3)].groupby('match_id')['over'].unique()
    total_overs_bowled = temp_df.apply(lambda x: len(x)).sum()
    player_season_dict['Overall Record']['Bowling']['Economy'] = runs_bowler_each_season.sum()/total_overs_bowled
    # Bowling Strike rate in IPL carrer
    player_season_dict['Overall Record']['Bowling']['Strike Rate'] = round((balls_delivered_each_season.sum() / wicket_each_season.sum()),2)
    # Total 4 Wicket Haul in IPL carrer
    temp_df = df[(df['bowler'] == player) & (df['bowler_wicket'] == 1) & (df['innings'] <3)].groupby('match_id')['bowler_wicket'].sum()
    player_season_dict['Overall Record']['Bowling']['4W'] = temp_df[temp_df == 4].count().sum()
    # Total 5 Wicket Haul in IPL carrer
    player_season_dict['Overall Record']['Bowling']['5W'] = temp_df[temp_df >= 5].count().sum()


    return json.dumps(player_season_dict,cls = NpEncoder, indent = 4)

