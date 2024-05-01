import os
import cfbd
import psycopg2
from cfbd.rest import ApiException

# Configure API key authorization
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = os.environ['CFBD_API_KEY']
configuration.api_key_prefix['Authorization'] = 'Bearer'

postgres_user = os.environ['POSTGRES_USER']
postgres_pw = os.environ['POSTGRES_PW']
postgres_host = os.environ['POSTGRES_HOST']
postgres_db = os.environ['POSTGRES_DB']

# create an instance of the API class
drives_api_instance = cfbd.DrivesApi(cfbd.ApiClient(configuration))
api_response = []
years = [2021,2022,2023]
team = 'Iowa'

def write_drive_to_postgres(conn,year,drive):
    cur = conn.cursor()
    cur.execute('INSERT INTO cfbd.drives(year, offense, offense_conference, defense, defense_conference, game_id, drive_id, drive_number,scoring, start_period, start_yardline, start_ytg, start_time_min, start_time_sec, end_period, end_yardline, end_ytg, end_time_min, end_time_sec, plays, yards, drive_result, is_home_offense, start_o_score, start_d_score, end_o_score, end_d_score) '
                'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                [year, drive.offense,drive.offense_conference,drive.defense,drive.defense_conference,drive.game_id, drive.id,drive.drive_number,drive.scoring,drive.start_period, drive.start_yardline,drive.start_yards_to_goal,drive.start_time.minutes, drive.start_time.seconds, drive.end_period, drive.end_yardline, drive.end_yards_to_goal, drive.end_time.minutes, drive.end_time.seconds, drive.plays,drive.yards, drive.drive_result, drive.is_home_offense, drive.start_offense_score, drive.start_defense_score, drive.end_offense_score, drive.end_defense_score])
    conn.commit()

for year in years:

    try:
        api_response = drives_api_instance.get_drives(year=year, season_type="both", team=team)
    except ApiException as e:
        print("Exception when calling DrivesApi->get_drives: %s\n" % e)

    for drive in api_response:
        conn = psycopg2.connect("dbname='{postgres_db}' user='{postgres_user}' host='{postgres_host}' password='{postgres_pw}'"
                                .format(postgres_db=postgres_db,
                                        postgres_host=postgres_host,
                                        postgres_user=postgres_user,
                                        postgres_pw=postgres_pw
                                        )
                                )
        write_drive_to_postgres(conn, year, drive)
        conn.close()
