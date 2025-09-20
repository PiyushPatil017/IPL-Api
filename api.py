# here Api  is developed which will be sent to app.py in json format

import numpy as np
import pandas as pd
import json

df = pd.read_csv('Dataset/ipl_matches_cleaned.csv')
df['team1'] = df['team1'].apply(lambda x: x.split(','))
df['team2'] = df['team2'].apply(lambda x: x.split(','))
df['season'] = df['season'].astype('category')
df['date'] = pd.to_datetime(df['date'])

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


def team_api(team):
    pass

def team_vs_team_api(team1,team2):
    pass

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

