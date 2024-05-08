import os
import cfbd
import psycopg2
from cfbd.rest import ApiException

# Configure API key authorization
configuration = cfbd.Configuration()
configuration.api_key['Authorization'] = os.environ['CFBD_API_KEY']
configuration.api_key_prefix['Authorization'] = 'Bearer'

def write_team_to_postgres(conn,team):
    cur = conn.cursor()
    logo0 = ""
    logo1 = ""
    if team.logos:
        logo0 = team.logos[0]
        if len(team.logos) > 1:
            logo1 = team.logos[1]
    cur.execute('INSERT INTO cfbd.teams(id, school, mascot, abbreviation, alt_name1, alt_name2, alt_name3, conference, classification, color, alt_color, logo_1, logo_2, twitter, location_venue_id, location_name, location_city, location_state, location_zip, location_country_code, location_timezone, location_latitude, location_longitude, location_elevation, location_capacity, location_year_constructed, location_grass, location_dome) '
                'VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)',
                [team.id,team.school, team.mascot, team.abbreviation,team.alt_name_1, team.alt_name_2, team.alt_name_3, team.conference, team.classification, team.color, team.alt_color, logo0, logo1, team.twitter, team.location.venue_id, team.location.name, team.location.city,team.location.state,team.location.zip,team.location.country_code, team.location.timezone, team.location.latitude, team.location.longitude, team.location.elevation, team.location.capacity, team.location.year_constructed, team.location.grass, team.location.dome ])
    conn.commit()


# create an instance of the API class
teams_api_instance = cfbd.TeamsApi(cfbd.ApiClient(configuration))

season_type = {'regular': 'regular', 'post': 'postseason', 'both': 'both'}
api_response = []
try:
    api_response = teams_api_instance.get_teams()
except ApiException as e:
    print("Exception when calling TeamsApi->get_teams: %s\n" % e)

conn = psycopg2.connect("dbname='{postgres_db}' user='{postgres_user}' host='{postgres_host}' password='{postgres_pw}'"
                        .format(postgres_db=os.environ['POSTGRES_DB'],
                                postgres_host=os.environ['POSTGRES_HOST'],
                                postgres_user=os.environ['POSTGRES_USER'],
                                postgres_pw=os.environ['POSTGRES_PW']
                                )
                        )
for team in api_response:
    write_team_to_postgres(conn,team)
conn.close()
