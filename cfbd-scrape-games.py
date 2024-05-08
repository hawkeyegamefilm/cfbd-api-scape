import os
import cfbd
from cfbd.rest import ApiException
import psycopg2

# Configure API key authorization
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = os.environ['CFBD_API_KEY']
configuration.api_key_prefix['Authorization'] = 'Bearer'

def write_game_result_to_postgres(conn,game: cfbd.Game):
    cur = conn.cursor()

    cur.execute('INSERT INTO cfbd.games(id, year, week, season_type, start_date, completed, neutral_site, conference_game, attendance, venue_id, venue, home_id, home_team, home_conference, home_division, home_points, home_line_score_1, home_line_score_2, home_line_score_3, home_line_score_4, home_post_win_prob, home_pregame_elo, home_postgame_elo, away_id, away_team, away_conference, away_division, away_points, away_line_score_1, away_line_score_2, away_line_score_3, away_line_score_4, away_post_win_prob, away_pregame_elo, away_postgame_elo, exitement_index, highlights, notes) '
                'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                [game.id, game.season, game.week, game.season_type, game.start_date, game.completed, game.neutral_site, game.conference_game, game.attendance, game.venue_id, game.venue, game.home_id, game.home_team, game.home_conference, game.home_division, game.home_points, game.home_line_scores[0], game.home_line_scores[1], game.home_line_scores[2], game.home_line_scores[3], game.home_post_win_prob, game.home_pregame_elo, game.home_postgame_elo, game.away_id, game.away_team, game.away_conference, game.away_division, game.away_points, game.away_line_scores[0], game.away_line_scores[1], game.away_line_scores[2], game.away_line_scores[3], game.away_post_win_prob, game.away_pregame_elo, game.away_postgame_elo, game.excitement_index, game.highlights, game.notes])
    conn.commit()


api_response = []
games_api_instance = cfbd.GamesApi(cfbd.ApiClient(configuration))

season_type = {'regular': 'regular', 'post': 'postseason', 'both': 'both'}

try:
    api_response = games_api_instance.get_games(2023, season_type='both', division='fbs')
except ApiException as e:
    print("Exception when calling GamesApi->get_games: %s\n" % e)

conn = psycopg2.connect("dbname='{postgres_db}' user='{postgres_user}' host='{postgres_host}' password='{postgres_pw}'"
                        .format(postgres_db=os.environ['POSTGRES_DB'],
                                postgres_host=os.environ['POSTGRES_HOST'],
                                postgres_user=os.environ['POSTGRES_USER'],
                                postgres_pw=os.environ['POSTGRES_PW']
                                )
                        )

for game in api_response:
    write_game_result_to_postgres(conn, game)
conn.close()