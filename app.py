# here our api development will be done
from flask import Flask,request
import api

app = Flask(__name__)

@app.route('/')
def home():
    return 'Home'


@app.route('/player_record')
def player_record():
    player = request.args.get('player')
    response = api.player_record_api(player)
    return response


@app.route('/player-vs-team')
def player_vs_team():
    player = request.args.get('player')
    response = api.player_vs_team_api(player)
    return response


@app.route('/team_vs_team')
def team_vs_team():
    team1 = request.args.get('team1')
    team2 = request.args.get('team2')
    response = api.team_vs_team_api(team1,team2)
    return response


@app.route('/team')
def team():
    team = request.args.get('team')
    response = api.team_api(team)
    print(response)
    return response




app.run(debug=True)