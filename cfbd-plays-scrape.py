import os
import cfbd
import psycopg2
from cfbd.rest import ApiException
from pprint import pprint

# Configure API key authorization
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = os.environ['CFBD_API_KEY']
configuration.api_key_prefix['Authorization'] = 'Bearer'

# create an instance of the API class
plays_api_instance = cfbd.PlaysApi(cfbd.ApiClient(configuration))

# toggling between regular & post
season_type = {'regular': 'regular', 'post': 'postseason', 'both': 'both'}

def write_play_to_postgres(conn,play: cfbd.Play):
    cur = conn.cursor()
    cur.execute('INSERT INTO cfbd.plays(id, offense, offense_conference, defense, defense_conference, home, away, offense_score, defense_score, game_id, drive_id, drive_number, play_number, period, clock_minutes, clock_seconds, offense_timeouts, defense_timeouts, yard_line, yards_to_goal, down, distance, scoring, yards_gained, play_type, play_text, ppa, wall_clock) '
                'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                [play.id,play.offense,play.offense_conference,play.defense, play.defense_conference, play.home, play.away, play.offense_score, play.defense_score, play.game_id, play.drive_id, play.drive_number, play.play_number, play.period, play.clock.minutes, play.clock.seconds, play.offense_timeouts, play.defense_timeouts, play.yard_line, play.yards_to_goal, play.down, play.distance,play.scoring, play.yards_gained, play.play_type,play.play_text, play.ppa, play.wallclock])
    conn.commit()

api_response = []

# 'postseason' resets the week counter, bowl games & playoffs are only post season games
# weeks = [1,2,3,4,5,6,7,8,9,10,11,12,13,14]
weeks = [1]

conn = psycopg2.connect("dbname='{postgres_db}' user='{postgres_user}' host='{postgres_host}' password='{postgres_pw}'"
                        .format(postgres_db=os.environ['POSTGRES_DB'],
                                postgres_host=os.environ['POSTGRES_HOST'],
                                postgres_user=os.environ['POSTGRES_USER'],
                                postgres_pw=os.environ['POSTGRES_PW']
                                )
                        )

for week in weeks:
    try:
        api_response = plays_api_instance.get_plays(year=2023,season_type=season_type['post'], week=week, team="Iowa")
    except ApiException as e:
        print("Exception when calling PlaysApi->get_plays: %s\n" % e)


    for play in api_response:
        write_play_to_postgres(conn, play)
conn.close()
