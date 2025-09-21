# here our api development will be done
from flask import Flask,request
import api

app = Flask(__name__)

@app.route('/')
def home():
    return 'Home'

# Returns IPL Seasons till 2025
@app.route('/seasons')
def season_name():
    response = api.season_name_api()
    return response

# Returns IPL team names till IPL 2025
@app.route('/ipl_teams')
def team_name():
    response = api.team_name_api()
    return response

# Returns Player overall and season wise Record
@app.route('/player_record')
def player_record():
    player = request.args.get('player')
    response = api.player_record_api(player)
    return response

# Returns player record against teams
@app.route('/player-vs-team')
def player_vs_team():
    player = request.args.get('player')
    response = api.player_vs_team_api(player)
    return response

# Returns rivalry record of teams
@app.route('/team_vs_team')
def team_vs_team():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    response = api.team_vs_team_api(team1,team2)
    return response

# Returns overall record of team
@app.route('/team')
def team():
    team = request.args.get('team')
    response = api.team_api(team)
    print(response)
    return response




app.run(debug=True)